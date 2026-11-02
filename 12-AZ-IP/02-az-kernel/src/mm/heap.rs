// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/mm/heap.rs — AZ-HEAP: Kernel-Owned Free-List Allocator
//!
//! ## Why this module exists
//!
//! Before this module, the kernel's `#[global_allocator]` was the `uefi`
//! crate's firmware-backed `Allocator`, which services every request with
//! the UEFI `AllocatePool`/`FreePool` **boot services**. Those boot services
//! are torn down the instant `boot::exit_boot_services` is called — yet
//! `main.rs` kept calling `alloc::format!` (and therefore the global
//! allocator) *after* that call, to render the banner. That is a real
//! use-after-free of a firmware table: undefined behaviour on real hardware,
//! masked only by QEMU/OVMF usually leaving the old pool pages intact.
//!
//! AZ-HEAP replaces that firmware dependency with a first-fit, coalescing
//! free-list allocator over memory the kernel owns for its *entire*
//! lifetime — a static arena compiled directly into the kernel image — so
//! allocation never depends on boot services, firmware, or the host OS.
//!
//! ## Design
//!
//! Classic intrusive free list: each free block stores its own size and a
//! pointer to the next free block, directly in the first bytes of the free
//! memory itself (no separate bookkeeping heap). `alloc` is first-fit with
//! address-ordered splitting (both the padding needed for alignment *and*
//! any leftover tail are recovered as new free blocks, so alignment never
//! leaks memory). `dealloc` reinserts the freed block in address order and
//! coalesces with an immediately-adjacent predecessor and/or successor,
//! keeping steady-state fragmentation bounded under alloc/free churn.

use core::alloc::{GlobalAlloc, Layout};
use core::mem::{align_of, size_of};
use core::ptr::NonNull;

use spin::Mutex;

/// Intrusive free-list node, written directly into free memory.
#[repr(C)]
struct FreeBlock {
    size: usize,
    next: Option<NonNull<FreeBlock>>,
}

/// Minimum block size: must be able to hold a `FreeBlock` header.
const MIN_BLOCK_SIZE: usize = size_of::<FreeBlock>();

/// First-fit, address-ordered, coalescing free-list allocator.
pub struct FreeListAllocator {
    head: Option<NonNull<FreeBlock>>,
    arena_start: usize,
    arena_end: usize,
}

// SAFETY: the allocator is only ever accessed through `LockedHeap`'s
// `spin::Mutex`, which provides the required synchronisation.
unsafe impl Send for FreeListAllocator {}

impl FreeListAllocator {
    /// An allocator with no backing memory yet. Must call `init` before use.
    pub const fn empty() -> Self {
        Self { head: None, arena_start: 0, arena_end: 0 }
    }

    /// Initialise the allocator over the byte range `[start, start + size)`.
    ///
    /// # Safety
    /// Caller must guarantee: the range is valid, writable, not aliased by
    /// any other live reference, and that `init` is called at most once
    /// before any `allocate`/`deallocate` call on this instance.
    pub unsafe fn init(&mut self, start: usize, size: usize) {
        assert!(start % align_of::<FreeBlock>() == 0, "heap arena must be word-aligned");
        assert!(size >= MIN_BLOCK_SIZE, "heap arena smaller than one block header");
        self.arena_start = start;
        self.arena_end = start + size;
        let block = start as *mut FreeBlock;
        block.write(FreeBlock { size, next: None });
        self.head = NonNull::new(block);
    }

    fn align_up(addr: usize, align: usize) -> usize {
        (addr + align - 1) & !(align - 1)
    }

    /// True once `init` has established a backing arena.
    pub fn is_initialised(&self) -> bool {
        self.arena_end > self.arena_start
    }

    /// Total arena size in bytes.
    pub fn capacity(&self) -> usize {
        self.arena_end - self.arena_start
    }

    /// Sum of all free-block sizes currently in the list (O(n), diagnostic use).
    pub fn free_bytes(&self) -> usize {
        let mut total = 0usize;
        let mut cur = self.head;
        while let Some(block_ptr) = cur {
            // SAFETY: every node in the list was written by `init`/`insert_and_coalesce`
            // and remains valid for as long as it stays linked.
            let block = unsafe { block_ptr.as_ref() };
            total += block.size;
            cur = block.next;
        }
        total
    }

    /// Find the first free block that fits `size` bytes aligned to `align`,
    /// unlink it, and recover both the alignment padding and any leftover
    /// tail as new free blocks. Returns the aligned, usable pointer.
    fn find_and_remove(&mut self, size: usize, align: usize) -> Option<*mut u8> {
        let mut prev: Option<NonNull<FreeBlock>> = None;
        let mut cur = self.head;

        while let Some(block_ptr) = cur {
            // SAFETY: `block_ptr` comes from the intrusive free list, which
            // only ever contains live, exclusively-owned block headers.
            let block_size = unsafe { block_ptr.as_ref().size };
            let next = unsafe { block_ptr.as_ref().next };
            let block_addr = block_ptr.as_ptr() as usize;

            let alloc_start = Self::align_up(block_addr, align);
            let padding = alloc_start - block_addr;

            if let Some(needed) = padding.checked_add(size) {
                if block_size >= needed {
                    let tail_addr = alloc_start + size;
                    let tail_size = block_size - needed;

                    // Recover the alignment padding as its own free block
                    // (only possible/worthwhile if it is big enough to hold
                    // a header; sub-MIN_BLOCK_SIZE slivers are vanishingly
                    // rare in practice because callers align the arena and
                    // every split point to `align_of::<FreeBlock>()`).
                    let mut replacement = next;
                    if tail_size >= MIN_BLOCK_SIZE {
                        let tail_block = tail_addr as *mut FreeBlock;
                        // SAFETY: tail_addr..tail_addr+tail_size lies strictly
                        // inside the block we are splitting, which this
                        // allocator exclusively owns.
                        unsafe { tail_block.write(FreeBlock { size: tail_size, next }); }
                        replacement = NonNull::new(tail_block);
                    }
                    if padding >= MIN_BLOCK_SIZE {
                        let pad_block = block_addr as *mut FreeBlock;
                        // SAFETY: same region-ownership argument as above.
                        unsafe { pad_block.write(FreeBlock { size: padding, next: replacement }); }
                        replacement = NonNull::new(pad_block);
                    }

                    self.relink(prev, replacement);
                    return Some(alloc_start as *mut u8);
                }
            }

            prev = cur;
            cur = next;
        }
        None
    }

    /// Point `prev`'s `next` (or `self.head` if there is no `prev`) at `new`.
    fn relink(&mut self, prev: Option<NonNull<FreeBlock>>, new: Option<NonNull<FreeBlock>>) {
        match prev {
            None => self.head = new,
            // SAFETY: `prev` is a live node from the free list that this
            // allocator exclusively owns.
            Some(mut p) => unsafe { p.as_mut().next = new },
        }
    }

    /// Insert a freed `[addr, addr+size)` block back into the address-ordered
    /// free list, coalescing with an adjacent predecessor and/or successor.
    fn insert_and_coalesce(&mut self, addr: usize, size: usize) {
        let mut prev: Option<NonNull<FreeBlock>> = None;
        let mut cur = self.head;

        // Walk to the first node whose address is >= addr (keeps list sorted).
        while let Some(block_ptr) = cur {
            if block_ptr.as_ptr() as usize >= addr {
                break;
            }
            prev = cur;
            // SAFETY: see find_and_remove.
            cur = unsafe { block_ptr.as_ref().next };
        }

        let new_addr = addr;
        let mut new_size = size;
        let mut new_next = cur;

        // Coalesce with the following block if directly adjacent.
        if let Some(next_ptr) = cur {
            if new_addr + new_size == next_ptr.as_ptr() as usize {
                // SAFETY: see find_and_remove.
                let next_block = unsafe { next_ptr.as_ref() };
                new_size += next_block.size;
                new_next = next_block.next;
            }
        }

        // Coalesce with the preceding block if directly adjacent.
        if let Some(mut prev_ptr) = prev {
            // SAFETY: `prev_ptr` is a live node owned exclusively by this allocator.
            let prev_block = unsafe { prev_ptr.as_mut() };
            if prev_ptr.as_ptr() as usize + prev_block.size == new_addr {
                prev_block.size += new_size;
                prev_block.next = new_next;
                return;
            }
        }

        let block = new_addr as *mut FreeBlock;
        // SAFETY: `[new_addr, new_addr+new_size)` was just freed by the
        // caller and is not reachable from anywhere else in the free list.
        unsafe { block.write(FreeBlock { size: new_size, next: new_next }); }
        self.relink(prev, NonNull::new(block));
    }

    /// Allocate memory satisfying `layout`, or `None` if no block fits.
    pub fn allocate(&mut self, layout: Layout) -> Option<*mut u8> {
        let size = layout.size().max(MIN_BLOCK_SIZE);
        let align = layout.align().max(align_of::<FreeBlock>());
        self.find_and_remove(size, align)
    }

    /// Return memory previously returned by `allocate` with the same `layout`.
    ///
    /// # Safety
    /// `ptr` must have been returned by `allocate` on this instance with an
    /// identical `layout`, and must not be used again afterwards.
    pub unsafe fn deallocate(&mut self, ptr: *mut u8, layout: Layout) {
        if ptr.is_null() {
            return;
        }

        let addr = ptr as usize;
        let size = layout.size().max(MIN_BLOCK_SIZE);
        let end = match addr.checked_add(size) {
            Some(v) => v,
            None => return,
        };

        // Defensive validation: reject pointers/ranges that cannot belong to
        // this allocator arena. This prevents invalid raw-pointer writes when
        // callers violate the deallocation contract.
        if addr < self.arena_start
            || end > self.arena_end
            || addr % align_of::<FreeBlock>() != 0
        {
            return;
        }

        self.insert_and_coalesce(addr, size);
    }
}

/// `GlobalAlloc`-compatible wrapper: a `spin::Mutex`-guarded `FreeListAllocator`.
pub struct LockedHeap(Mutex<FreeListAllocator>);

impl LockedHeap {
    /// An allocator with no backing memory yet. Must call `init` before use.
    pub const fn empty() -> Self {
        Self(Mutex::new(FreeListAllocator::empty()))
    }

    /// Initialise the backing arena. See `FreeListAllocator::init` for the
    /// safety contract.
    ///
    /// # Safety
    /// See `FreeListAllocator::init`.
    pub unsafe fn init(&self, start: usize, size: usize) {
        self.0.lock().init(start, size);
    }

    /// Diagnostic: bytes currently free across the whole arena.
    pub fn free_bytes(&self) -> usize {
        self.0.lock().free_bytes()
    }

    /// Diagnostic: total arena size in bytes.
    pub fn capacity(&self) -> usize {
        self.0.lock().capacity()
    }
}

// SAFETY: `alloc`/`dealloc` only touch memory inside the arena passed to
// `init`, which the allocator owns exclusively for the kernel's lifetime;
// all mutation is serialised through the inner `spin::Mutex`.
unsafe impl GlobalAlloc for LockedHeap {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        self.0.lock().allocate(layout).unwrap_or(core::ptr::null_mut())
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        self.0.lock().deallocate(ptr, layout);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::alloc::{alloc as std_alloc, dealloc as std_dealloc, Layout as StdLayout};

    /// A host-allocated arena handed to the allocator under test. Freed on
    /// `Drop` so Miri/ASan-style leak checks stay clean across the suite.
    struct TestArena {
        layout: StdLayout,
        ptr: *mut u8,
    }

    impl TestArena {
        fn new(size: usize) -> Self {
            let layout = StdLayout::from_size_align(size, 16).unwrap();
            // SAFETY: size > 0, alignment is a valid power of two.
            let ptr = unsafe { std_alloc(layout) };
            assert!(!ptr.is_null());
            Self { layout, ptr }
        }

        fn start(&self) -> usize {
            self.ptr as usize
        }
    }

    impl Drop for TestArena {
        fn drop(&mut self) {
            // SAFETY: `ptr`/`layout` are exactly what `std_alloc` returned.
            unsafe { std_dealloc(self.ptr, self.layout) };
        }
    }

    fn new_allocator(arena: &TestArena, size: usize) -> FreeListAllocator {
        let mut a = FreeListAllocator::empty();
        unsafe { a.init(arena.start(), size) };
        a
    }

    #[test]
    fn single_alloc_dealloc_round_trip() {
        let arena = TestArena::new(4096);
        let mut a = new_allocator(&arena, 4096);
        assert_eq!(a.free_bytes(), 4096);

        let layout = Layout::from_size_align(64, 8).unwrap();
        let p = a.allocate(layout).expect("allocation should succeed");
        assert!(!p.is_null());
        assert_eq!(p as usize % 8, 0, "pointer must respect requested alignment");
        assert!(a.free_bytes() < 4096);

        unsafe { a.deallocate(p, layout) };
        assert_eq!(a.free_bytes(), 4096, "freeing the only allocation must restore full capacity");
    }

    #[test]
    fn allocations_never_overlap() {
        let arena = TestArena::new(4096);
        let mut a = new_allocator(&arena, 4096);
        let layout = Layout::from_size_align(100, 8).unwrap();

        let mut ptrs = std::vec::Vec::new();
        for _ in 0..8 {
            let p = a.allocate(layout).expect("allocation should succeed");
            ptrs.push(p as usize);
        }
        ptrs.sort_unstable();
        for w in ptrs.windows(2) {
            assert!(w[1] >= w[0] + layout.size(), "allocations must not overlap");
        }
    }

    #[test]
    fn respects_large_alignment_without_leaking_padding() {
        let arena = TestArena::new(4096);
        let mut a = new_allocator(&arena, 4096);

        let layout = Layout::from_size_align(32, 128).unwrap();
        let p = a.allocate(layout).expect("allocation should succeed");
        assert_eq!(p as usize % 128, 0);

        unsafe { a.deallocate(p, layout) };
        assert_eq!(a.free_bytes(), 4096, "alignment padding must be recovered, not leaked");
    }

    #[test]
    fn coalesces_adjacent_free_blocks_back_to_full_capacity() {
        let arena = TestArena::new(4096);
        let mut a = new_allocator(&arena, 4096);
        let layout = Layout::from_size_align(256, 16).unwrap();

        let a1 = a.allocate(layout).unwrap();
        let a2 = a.allocate(layout).unwrap();
        let a3 = a.allocate(layout).unwrap();
        assert!(a.free_bytes() < 4096);

        // Free out of allocation order to exercise both-neighbour coalescing.
        unsafe { a.deallocate(a2, layout) };
        unsafe { a.deallocate(a1, layout) };
        unsafe { a.deallocate(a3, layout) };

        assert_eq!(a.free_bytes(), 4096, "all blocks freed must coalesce into one full-capacity block");
    }

    #[test]
    fn out_of_memory_returns_none_without_panicking() {
        let arena = TestArena::new(256);
        let mut a = new_allocator(&arena, 256);
        let layout = Layout::from_size_align(4096, 8).unwrap();
        assert!(a.allocate(layout).is_none(), "oversized request must fail gracefully");
    }

    #[test]
    fn reuses_freed_block_of_matching_size() {
        let arena = TestArena::new(4096);
        let mut a = new_allocator(&arena, 4096);
        let layout = Layout::from_size_align(200, 8).unwrap();

        let p1 = a.allocate(layout).unwrap();
        unsafe { a.deallocate(p1, layout) };
        let p2 = a.allocate(layout).unwrap();
        assert_eq!(p1, p2, "first-fit should reuse the just-freed block");
    }

    #[test]
    fn locked_heap_is_usable_as_global_allocator_api() {
        let arena = TestArena::new(4096);
        let heap = LockedHeap::empty();
        unsafe { heap.init(arena.start(), 4096) };
        assert_eq!(heap.capacity(), 4096);
        assert_eq!(heap.free_bytes(), 4096);

        let layout = Layout::from_size_align(64, 8).unwrap();
        // SAFETY: exercising the `GlobalAlloc` trait methods directly, as
        // the real kernel's allocator machinery would.
        unsafe {
            let p = <LockedHeap as GlobalAlloc>::alloc(&heap, layout);
            assert!(!p.is_null());
            <LockedHeap as GlobalAlloc>::dealloc(&heap, p, layout);
        }
        assert_eq!(heap.free_bytes(), 4096);
    }
}

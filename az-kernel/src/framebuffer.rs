// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//! az-kernel/src/framebuffer.rs — GOP Framebuffer Abstraction
//!
//! Sprint 0: Provides the kernel's first output channel.  Wraps the UEFI
//! Graphics Output Protocol (GOP) linear framebuffer into a safe interface
//! with AxiomZero-themed colours and text rendering.
//!
//! The framebuffer is the kernel's "holographic boundary" in the sense of
//! Pillar 4: the 2D projection of the internal 5D state onto a surface that
//! humans can observe.

#![allow(dead_code)]

use uefi::proto::console::gop::{GraphicsOutput, PixelFormat};

// ---------------------------------------------------------------------------
// Colour palette — AxiomZero design language
// ---------------------------------------------------------------------------
#[derive(Clone, Copy)]
pub struct Color {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

impl Color {
    pub const AXIOMZERO_BLACK: Color  = Color { r: 0x08, g: 0x08, b: 0x10 };
    pub const AXIOMZERO_WHITE: Color  = Color { r: 0xF0, g: 0xF0, b: 0xFF };
    pub const AXIOMZERO_GOLD:  Color  = Color { r: 0xFF, g: 0xD7, b: 0x00 };
    pub const AXIOMZERO_CYAN:  Color  = Color { r: 0x00, g: 0xE5, b: 0xFF };
    pub const AXIOMZERO_GREEN: Color  = Color { r: 0x39, g: 0xFF, b: 0x14 };
    pub const AXIOMZERO_GREY:  Color  = Color { r: 0x88, g: 0x88, b: 0x99 };
    pub const AXIOMZERO_RED:   Color  = Color { r: 0xFF, g: 0x33, b: 0x33 };

    pub fn as_u32_bgr(&self) -> u32 {
        ((self.b as u32) << 16) | ((self.g as u32) << 8) | (self.r as u32)
    }

    pub fn as_u32_rgb(&self) -> u32 {
        ((self.r as u32) << 16) | ((self.g as u32) << 8) | (self.b as u32)
    }
}

// ---------------------------------------------------------------------------
// Framebuffer wrapper
// ---------------------------------------------------------------------------

/// The kernel's primary output surface.
///
/// Wraps the UEFI GOP linear framebuffer.  After `exit_boot_services` the
/// framebuffer memory remains mapped and writable for the kernel's lifetime.
pub struct AxiomFramebuffer {
    base: *mut u32,
    width: usize,
    height: usize,
    stride: usize,          // pixels per scanline (may differ from width)
    pixel_format: PixelFormat,
}

// SAFETY: The framebuffer base pointer is static hardware memory; we are the
// only entity writing to it (bare metal, single address space in Sprint 0).
unsafe impl Send for AxiomFramebuffer {}
unsafe impl Sync for AxiomFramebuffer {}

// 8×16 monospace font glyph table (printable ASCII 0x20–0x7E).
// Each glyph is 8 pixels wide × 16 pixels tall, stored as 16 u8 bitmasks.
// Sprint 0 uses a minimal embedded font; Sprint 3 extends with full Unicode.
static FONT_8X16: &[u8] = include_bytes!("../assets/font8x16.bin");
const GLYPH_W: usize = 8;
const GLYPH_H: usize = 16;
const FONT_FIRST: u8 = 0x20; // space
const FONT_LAST:  u8 = 0x7E; // ~

impl AxiomFramebuffer {
    /// Construct from UEFI GOP.  Call before `exit_boot_services`.
    pub fn from_gop(gop: &mut GraphicsOutput) -> Self {
        let mode_info = gop.current_mode_info();
        let (width, height) = mode_info.resolution();
        let stride = mode_info.stride();
        let pixel_format = mode_info.pixel_format();
        let base = gop.frame_buffer().as_mut_ptr() as *mut u32;
        Self { base, width, height, stride, pixel_format }
    }

    /// Fill the entire screen with a single colour.
    pub fn clear(&mut self, c: Color) {
        let px = self.pack(c);
        for y in 0..self.height {
            for x in 0..self.width {
                unsafe { *self.base.add(y * self.stride + x) = px; }
            }
        }
    }

    /// Draw a single pixel.
    pub fn set_pixel(&mut self, x: usize, y: usize, c: Color) {
        if x < self.width && y < self.height {
            unsafe { *self.base.add(y * self.stride + x) = self.pack(c); }
        }
    }

    /// Draw a filled rectangle.
    pub fn fill_rect(&mut self, x0: usize, y0: usize, w: usize, h: usize, c: Color) {
        let px = self.pack(c);
        for y in y0..(y0 + h).min(self.height) {
            for x in x0..(x0 + w).min(self.width) {
                unsafe { *self.base.add(y * self.stride + x) = px; }
            }
        }
    }

    /// Draw text at character-grid position (col, row).
    pub fn draw_text(&mut self, col: usize, row: usize, text: &str, fg: Color) {
        let x0 = col * GLYPH_W;
        let y0 = row * GLYPH_H;
        for (i, ch) in text.chars().enumerate() {
            self.draw_glyph(x0 + i * GLYPH_W, y0, ch, fg);
        }
    }

    /// Draw the AxiomZero boot banner (large ASCII art header).
    pub fn draw_banner(&mut self, major: u32, minor: u32, patch: u32) {
        // Top gold divider
        self.fill_rect(0, 0, self.width, 2, Color::AXIOMZERO_GOLD);
        // Title
        self.draw_text(2, 0, "  AxiomZero OS", Color::AXIOMZERO_BLACK);
        self.fill_rect(0, GLYPH_H * 2, self.width, 2, Color::AXIOMZERO_GOLD);

        extern crate alloc;
        use alloc::format;
        let ver = format!("v{}.{}.{}", major, minor, patch);
        self.draw_text(2, 2, &format!("AxiomZero Unitary Operating System  {}", ver), Color::AXIOMZERO_WHITE);
    }

    /// Draw the single-line status bar at the bottom of the screen.
    pub fn draw_status_line(&mut self, msg: &str) {
        let last_row = self.height / GLYPH_H - 1;
        self.fill_rect(0, last_row * GLYPH_H, self.width, GLYPH_H, Color::AXIOMZERO_GOLD);
        self.draw_text(1, last_row, msg, Color::AXIOMZERO_BLACK);
    }

    // ------------------------------------------------------------------
    // Internal helpers
    // ------------------------------------------------------------------

    fn pack(&self, c: Color) -> u32 {
        match self.pixel_format {
            PixelFormat::Rgb => c.as_u32_rgb(),
            PixelFormat::Bgr => c.as_u32_bgr(),
            _ => c.as_u32_bgr(), // safe default for BltOnly / custom
        }
    }

    fn draw_glyph(&mut self, x0: usize, y0: usize, ch: char, fg: Color) {
        let code = ch as u8;
        if code < FONT_FIRST || code > FONT_LAST {
            return; // non-printable; skip
        }
        let idx = (code - FONT_FIRST) as usize * GLYPH_H;
        if idx + GLYPH_H > FONT_8X16.len() {
            return;
        }
        for row in 0..GLYPH_H {
            let bits = FONT_8X16[idx + row];
            for col in 0..GLYPH_W {
                if bits & (0x80 >> col) != 0 {
                    self.set_pixel(x0 + col, y0 + row, fg);
                }
            }
        }
    }
}

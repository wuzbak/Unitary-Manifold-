.PHONY: build run test test-lib clean qemu
build:
	cargo build --release
test: test-lib
test-lib:
	bash scripts/test_lib.sh
clean:
	cargo clean
qemu:
	cargo run

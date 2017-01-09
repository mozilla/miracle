.PHONY: all clean debug release

ifeq ($(shell uname),Darwin)
    EXT := dylib
else
    EXT := so
endif

LIBNAME = libmiracle_rlib.$(EXT)


all: release

clean:
	rm -rf target

debug: target/debug/$(LIBNAME)

release: target/release/$(LIBNAME)

target/debug/$(LIBNAME): src/lib.rs Cargo.toml
	cargo build

target/release/$(LIBNAME): src/lib.rs Cargo.toml
	cargo build --release

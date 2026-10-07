SHELL := /bin/bash
.DEFAULT_GOAL := wheel
.DELETE_ON_ERROR:

include ../versions/*.env venv.env

JOBS := $(shell sysctl -n hw.ncpu)

.PHONY: x264 x265 de265 aom sharpyuv libpng libjpeg libheif
x264: build/x264-$(X264_BUILD).done
x265: build/x265-$(X265_VERSION).done
de265: build/de265-$(DE265_VERSION).done
aom: build/aom-$(AOM_VERSION).done
sharpyuv: build/sharpyuv-$(WEBP_VERSION).done
libpng: build/libpng-$(LIBPNG_VERSION).done
libjpeg: build/libjpeg-$(LIBJPEG_VERSION).done
libheif: build/libheif-$(LIBHEIF_VERSION).done

sources/x264.tar.gz: URL := $(X264_URL)
sources/x264.tar.gz: SHA256 := $(X264_SHA256)
sources/x265.tar.gz: URL := $(X265_URL)
sources/x265.tar.gz: SHA256 := $(X265_SHA256)
sources/de265.tar.gz: URL := $(DE265_URL)
sources/de265.tar.gz: SHA256 := $(DE265_SHA256)
sources/aom.tar.gz: URL := $(AOM_URL)
sources/aom.tar.gz: SHA256 := $(AOM_SHA256)
sources/sharpyuv.tar.gz: URL := $(WEBP_URL)
sources/sharpyuv.tar.gz: SHA256 := $(WEBP_SHA256)
sources/libpng.tar.gz: URL := $(LIBPNG_URL)
sources/libpng.tar.gz: SHA256 := $(LIBPNG_SHA256)
sources/libjpeg.tar.gz: URL := $(LIBJPEG_URL)
sources/libjpeg.tar.gz: SHA256 := $(LIBJPEG_SHA256)
sources/libheif.tar.gz: URL := $(LIBHEIF_URL)
sources/libheif.tar.gz: SHA256 := $(LIBHEIF_SHA256)

sources/%.tar.gz: ../versions/%.env | sources
	@set -euo pipefail; \
	if ! printf '%s  %s\n' "$(SHA256)" "$@" | sha256sum -c - >/dev/null 2>&1; then \
		curl -fL "$(URL)" -o "$@"; \
		printf '%s  %s\n' "$(SHA256)" "$@" | sha256sum -c -; \
	fi; \
	touch "$@"

sources/nasm.zip: venv.env | sources
	@set -euo pipefail; \
	if ! printf '%s  %s\n' "$(NASM_SHA256)" "$@" | sha256sum -c - >/dev/null 2>&1; then \
		curl -fL "$(NASM_URL)" -o "$@"; \
		printf '%s  %s\n' "$(NASM_SHA256)" "$@" | sha256sum -c -; \
	fi; \
	touch "$@"

sources:
	mkdir -p "$@"

build/venv: sources/nasm.zip venv.env
	set -euo pipefail; \
	trap 'rm -rf "$@"' ERR; \
	python3 -m venv "$@"; \
	source "$@/bin/activate"; \
	unzip -p "$<" "nasm-$(NASM_VERSION)/nasm" > "$@/bin/nasm"; \
	chmod +x "$@/bin/nasm"; \
	pip install cmake==$(CMAKE_VERSION) delocate==$(DELOCATE_VERSION) wheel==$(WHEEL_VERSION); \
	touch "$@"

# Run each build in a fresh temporary directory; install into its versioned prefix.
define prepare
set -euo pipefail; \
source build/venv/bin/activate; \
prefix="$(abspath $(basename $@))"; \
stamp="$(abspath $@)"; \
rm -f "$$stamp"; \
rm -rf "$$prefix"; \
work=$$(mktemp -d); \
trap 'rm -rf "$$work"' EXIT; \
tar xf "$(abspath $<)" --strip-components=1 -C "$$work"; \
cd "$$work";
endef

build/x264-$(X264_BUILD).done: sources/x264.tar.gz ../versions/x264.env | build/venv
	$(prepare) \
	grep -q '^#define X264_BUILD $(X264_BUILD)$$' x264.h; \
	./configure \
		--prefix="$$prefix" \
		--libdir="$$prefix/lib" \
		--enable-shared \
		--enable-pic \
		--disable-cli \
		--disable-opencl; \
	make -j $(JOBS); \
	make install; \
	mkdir -p "$$prefix/share/licenses"; \
	cp COPYING "$$prefix/share/licenses/x264-COPYING"; \
	printf '%s\n' "$(X264_SHA256)" > "$$stamp"

build/x265-$(X265_VERSION).done: sources/x265.tar.gz ../versions/x265.env | build/venv
	$(prepare) \
	cmake -S source -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$prefix" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DENABLE_CLI=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$prefix/share/licenses"; \
	cp COPYING "$$prefix/share/licenses/x265-COPYING"; \
	printf '%s\n' "$(X265_SHA256)" > "$$stamp"

build/de265-$(DE265_VERSION).done: sources/de265.tar.gz ../versions/de265.env | build/venv
	$(prepare) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$prefix" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DENABLE_ENCODER=OFF \
		-DENABLE_DECODER=OFF \
		-DENABLE_SHERLOCK265=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$prefix/share/licenses"; \
	cp COPYING "$$prefix/share/licenses/libde265-COPYING"; \
	printf '%s\n' "$(DE265_SHA256)" > "$$stamp"

build/aom-$(AOM_VERSION).done: sources/aom.tar.gz ../versions/aom.env | build/venv
	$(prepare) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$prefix" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DBUILD_SHARED_LIBS=ON \
		-DENABLE_TESTS=OFF \
		-DENABLE_APPS=OFF \
		-DENABLE_TOOLS=OFF \
		-DENABLE_EXAMPLES=OFF \
		-DENABLE_DOCS=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$prefix/share/licenses"; \
	cp LICENSE "$$prefix/share/licenses/aom-LICENSE"; \
	cp PATENTS "$$prefix/share/licenses/aom-PATENTS"; \
	printf '%s\n' "$(AOM_SHA256)" > "$$stamp"

build/sharpyuv-$(WEBP_VERSION).done: sources/sharpyuv.tar.gz ../versions/sharpyuv.env | build/venv
	$(prepare) \
	./configure \
		--prefix="$$prefix" \
		--libdir="$$prefix/lib" \
		--disable-everything \
		--disable-shared \
		--disable-threading; \
	make -C sharpyuv -j $(JOBS) CFLAGS='-fPIC' install; \
	mkdir -p "$$prefix/share/licenses"; \
	cp COPYING "$$prefix/share/licenses/libwebp-COPYING"; \
	cp PATENTS "$$prefix/share/licenses/libwebp-PATENTS"; \
	printf '%s\n' "$(WEBP_SHA256)" > "$$stamp"

build/libpng-$(LIBPNG_VERSION).done: sources/libpng.tar.gz ../versions/libpng.env | build/venv
	$(prepare) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$prefix" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DPNG_STATIC=OFF \
		-DPNG_FRAMEWORK=OFF \
		-DPNG_TESTS=OFF \
		-DPNG_TOOLS=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$prefix/share/licenses"; \
	cp LICENSE "$$prefix/share/licenses/libpng-LICENSE"; \
	printf '%s\n' "$(LIBPNG_SHA256)" > "$$stamp"

build/libjpeg-$(LIBJPEG_VERSION).done: sources/libjpeg.tar.gz ../versions/libjpeg.env | build/venv
	$(prepare) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$prefix" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DENABLE_STATIC=OFF \
		-DWITH_TURBOJPEG=OFF \
		-DWITH_TOOLS=OFF \
		-DWITH_TESTS=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$prefix/share/licenses"; \
	cp LICENSE.md "$$prefix/share/licenses/libjpeg-LICENSE.md"; \
	cp README.ijg "$$prefix/share/licenses/libjpeg-README.ijg"; \
	printf '%s\n' "$(LIBJPEG_SHA256)" > "$$stamp"

build/libheif-$(LIBHEIF_VERSION).done: sources/libheif.tar.gz ../versions/libheif.env \
        build/x264-$(X264_BUILD).done \
        build/x265-$(X265_VERSION).done \
        build/de265-$(DE265_VERSION).done \
        build/aom-$(AOM_VERSION).done \
        build/sharpyuv-$(WEBP_VERSION).done \
        build/libpng-$(LIBPNG_VERSION).done \
        build/libjpeg-$(LIBJPEG_VERSION).done | build/venv
	build="$(abspath build)"; \
	$(prepare) \
	cmake --preset=release-noplugins -S . -B build \
		-DCMAKE_INSTALL_PREFIX="$$prefix" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DCMAKE_PREFIX_PATH="$$build/x264-$(X264_BUILD);$$build/x265-$(X265_VERSION);$$build/de265-$(DE265_VERSION);$$build/aom-$(AOM_VERSION);$$build/sharpyuv-$(WEBP_VERSION);$$build/libpng-$(LIBPNG_VERSION);$$build/libjpeg-$(LIBJPEG_VERSION)" \
		-DCMAKE_INCLUDE_PATH="$$build/sharpyuv-$(WEBP_VERSION)/include/webp" \
		-DWITH_EXAMPLE_HEIF_THUMB=OFF 2>&1 | tee _configure.log; \
	grep -q 'Found PNG:' _configure.log; \
	grep -q 'Found JPEG:' _configure.log; \
	grep -q 'Found libsharpyuv:' _configure.log; \
	grep -q "'x264' as built-in backend" _configure.log; \
	grep -q "'x265' as built-in backend" _configure.log; \
	grep -q "'libde265' as built-in backend" _configure.log; \
	grep -q "'aomdec' as built-in backend" _configure.log; \
	grep -q "'aomenc' as built-in backend" _configure.log; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$prefix/share/licenses"; \
	cp COPYING "$$prefix/share/licenses/libheif-COPYING"; \
	printf '%s\n' "$(LIBHEIF_SHA256)" > "$$stamp"

.PHONY: wheel
wheel: build/libheif-$(LIBHEIF_VERSION).done | build/venv
	# Prepare package files.
	set -euo pipefail; \
	build=build/libheif-$(LIBHEIF_VERSION); \
	target=build/wheel/libheif_binary; \
	rm -rf build/wheel; \
	mkdir -p build/wheel; \
	cp ../pyproject.toml ../setup.py build/wheel/; \
	cp -r ../libheif_binary build/wheel/; \
	mkdir -p $$target/bin $$target/licenses; \
	sed -n 's/^#define LIBHEIF_VERSION "\([^" ]*\)"/\1/p' \
		$$build/include/libheif/heif_version.h > $$target/LIBVERSION; \
	test -s $$target/LIBVERSION; \
	for prefix in build/x264-$(X264_BUILD) build/x265-$(X265_VERSION) \
		build/de265-$(DE265_VERSION) build/aom-$(AOM_VERSION) \
		build/sharpyuv-$(WEBP_VERSION) build/libpng-$(LIBPNG_VERSION) \
		build/libjpeg-$(LIBJPEG_VERSION) $$build; do \
		cp $$prefix/share/licenses/* $$target/licenses/; \
	done; \
	cp $$build/bin/heif-enc $$build/bin/heif-dec $$build/bin/heif-info $$target/bin/

	# Build the initial wheel and bundle dependencies
	set -euo pipefail; \
	source build/venv/bin/activate; \
	platform=$$(python -c 'import platform, sysconfig; print(sysconfig.get_platform().rsplit("-", 1)[0] + "-" + platform.machine())'); \
	pip wheel ./build/wheel -w build/wheel \
		--config-settings=--build-option=--plat-name="$$platform"; \
	DYLD_LIBRARY_PATH="build/libheif-$(LIBHEIF_VERSION)/lib:build/x264-$(X264_BUILD)/lib:build/x265-$(X265_VERSION)/lib:build/de265-$(DE265_VERSION)/lib:build/aom-$(AOM_VERSION)/lib:build/sharpyuv-$(WEBP_VERSION)/lib:build/libpng-$(LIBPNG_VERSION)/lib:build/libjpeg-$(LIBJPEG_VERSION)/lib" \
		delocate-wheel -L lib build/wheel/*.whl

	# Restore the stable libheif install ID and repack
	set -euo pipefail; \
	source build/venv/bin/activate; \
	wheel unpack build/wheel/*.whl -d build/wheel/unpacked; \
	set -- build/wheel/unpacked/*/libheif_binary/lib/libheif.*.dylib; dylib=$$1; \
	install_name_tool -id '@rpath/libheif.1.dylib' "$$dylib"; \
	codesign --force --sign - "$$dylib"; \
	mkdir -p ../dist; \
	wheel pack build/wheel/unpacked/* -d ../dist

	# Test the installed wheel in a fresh temporary environment.
	set -euo pipefail; \
	smoke_venv=$$(mktemp -d); \
	trap 'rm -rf "$$smoke_venv"' EXIT; \
	python3 -m venv "$$smoke_venv"; \
	source "$$smoke_venv/bin/activate"; \
	pip install "../dist/$$(basename build/wheel/*.whl)"; \
	tar -xOf sources/libheif.tar.gz \
		"libheif-$(LIBHEIF_VERSION)/examples/example.heic" > build/example.heic; \
	python ../tests/smoke.py build/example.heic

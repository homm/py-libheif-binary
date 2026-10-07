SHELL := /bin/bash
.DEFAULT_GOAL := wheel
.DELETE_ON_ERROR:

export MACOSX_DEPLOYMENT_TARGET := 11.0
export CFLAGS := -O3 -g0
export CXXFLAGS := -O3 -g0
include ../versions/*.env venv.env

JOBS := $(shell sysctl -n hw.physicalcpu)

.PHONY: libs x264 x265 de265 aom sharpyuv libpng libjpeg libheif
libs: x265 de265 aom sharpyuv libpng libjpeg
x264: build/x264-$(X264_BUILD).done
x265: build/x265-$(X265_VERSION).done
de265: build/de265-$(DE265_VERSION).done
aom: build/aom-$(AOM_VERSION).done
sharpyuv: build/sharpyuv-$(WEBP_VERSION).done
libpng: build/libpng-$(LIBPNG_VERSION).done
libjpeg: build/libjpeg-$(LIBJPEG_VERSION).done
libheif: build/libheif-$(LIBHEIF_VERSION).done

sources/x264-$(X264_BUILD).tar.gz: ../versions/x264.env
sources/x264-$(X264_BUILD).tar.gz: URL := $(X264_URL)
sources/x264-$(X264_BUILD).tar.gz: SHA256 := $(X264_SHA256)
sources/x265-$(X265_VERSION).tar.gz: ../versions/x265.env
sources/x265-$(X265_VERSION).tar.gz: URL := $(X265_URL)
sources/x265-$(X265_VERSION).tar.gz: SHA256 := $(X265_SHA256)
sources/de265-$(DE265_VERSION).tar.gz: ../versions/de265.env
sources/de265-$(DE265_VERSION).tar.gz: URL := $(DE265_URL)
sources/de265-$(DE265_VERSION).tar.gz: SHA256 := $(DE265_SHA256)
sources/aom-$(AOM_VERSION).tar.gz: ../versions/aom.env
sources/aom-$(AOM_VERSION).tar.gz: URL := $(AOM_URL)
sources/aom-$(AOM_VERSION).tar.gz: SHA256 := $(AOM_SHA256)
sources/sharpyuv-$(WEBP_VERSION).tar.gz: ../versions/sharpyuv.env
sources/sharpyuv-$(WEBP_VERSION).tar.gz: URL := $(WEBP_URL)
sources/sharpyuv-$(WEBP_VERSION).tar.gz: SHA256 := $(WEBP_SHA256)
sources/libpng-$(LIBPNG_VERSION).tar.gz: ../versions/libpng.env
sources/libpng-$(LIBPNG_VERSION).tar.gz: URL := $(LIBPNG_URL)
sources/libpng-$(LIBPNG_VERSION).tar.gz: SHA256 := $(LIBPNG_SHA256)
sources/libjpeg-$(LIBJPEG_VERSION).tar.gz: ../versions/libjpeg.env
sources/libjpeg-$(LIBJPEG_VERSION).tar.gz: URL := $(LIBJPEG_URL)
sources/libjpeg-$(LIBJPEG_VERSION).tar.gz: SHA256 := $(LIBJPEG_SHA256)
sources/libheif-$(LIBHEIF_VERSION).tar.gz: ../versions/libheif.env
sources/libheif-$(LIBHEIF_VERSION).tar.gz: URL := $(LIBHEIF_URL)
sources/libheif-$(LIBHEIF_VERSION).tar.gz: SHA256 := $(LIBHEIF_SHA256)

sources/%.tar.gz: | sources
	@set -euo pipefail; \
	if ! printf '%s  %s\n' "$(SHA256)" "$@" | sha256sum -c - >/dev/null 2>&1; then \
		curl -fL "$(URL)" -o "$@"; \
		printf '%s  %s\n' "$(SHA256)" "$@" | sha256sum -c -; \
	fi; \
	touch "$@"

sources/nasm-$(NASM_VERSION).zip: venv.env | sources
	@set -euo pipefail; \
	if ! printf '%s  %s\n' "$(NASM_SHA256)" "$@" | sha256sum -c - >/dev/null 2>&1; then \
		curl -fL "$(NASM_URL)" -o "$@"; \
		printf '%s  %s\n' "$(NASM_SHA256)" "$@" | sha256sum -c -; \
	fi; \
	touch "$@"

sources:
	mkdir -p "$@"

build/venv: sources/nasm-$(NASM_VERSION).zip venv.env
	set -euo pipefail; \
	trap 'rm -rf "$@"' ERR; \
	python3 -m venv "$@"; \
	source "$@/bin/activate"; \
	unzip -p "$<" "nasm-$(NASM_VERSION)/nasm" > "$@/bin/nasm"; \
	chmod +x "$@/bin/nasm"; \
	pip install cmake==$(CMAKE_VERSION) delocate==$(DELOCATE_VERSION) wheel==$(WHEEL_VERSION); \
	touch "$@"

# Run each build in a fresh temporary directory; install into its versioned output directory.
define prepare
set -euo pipefail; \
source build/venv/bin/activate; \
target="$(abspath $(basename $@))"; \
stamp="$(abspath $@)"; \
if [ -n "$(1)" ] && [ -f "$$stamp" ] && [ "$$(cat "$$stamp")" = "$(1)" ]; then \
	printf '\n%s\n' "Skipping $(notdir $(basename $@)): SHA256 matches the .done file"; \
	exit 0; \
fi; \
printf '\n########################\n%s\n########################\n' \
	"Compiling $(notdir $(basename $@))"; \
rm -f "$$stamp"; \
rm -rf "$$target"; \
work=$$(mktemp -d); \
trap 'rm -rf "$$work"' EXIT; \
tar xf "$(abspath $<)" --strip-components=1 -C "$$work"; \
cd "$$work";
endef

build/x264-$(X264_BUILD).done: sources/x264-$(X264_BUILD).tar.gz ../versions/x264.env | build/venv
	@$(call prepare,$(X264_SHA256)) \
	grep -q '^#define X264_BUILD $(X264_BUILD)$$' x264.h; \
	STRIP= ./configure \
		--prefix="$$target" \
		--libdir="$$target/lib" \
		--enable-shared \
		--enable-pic \
		--disable-cli \
		--disable-opencl; \
	make -j $(JOBS); \
	make install; \
	mkdir -p "$$target/share/licenses"; \
	cp COPYING "$$target/share/licenses/x264-COPYING"; \
	printf '%s\n' "$(X264_SHA256)" > "$$stamp"

build/x265-$(X265_VERSION).done: sources/x265-$(X265_VERSION).tar.gz ../versions/x265.env | build/venv
	@$(call prepare,$(X265_SHA256)) \
	x265_options=( \
		-DCMAKE_BUILD_TYPE=Release \
		-DENABLE_CLI=OFF \
		-DCMAKE_ASM_NASM_FLAGS="--pragma \"macho build_version macos,11,0\""); \
	for depth in 10 12; do \
		cmake -S source -B build-$$depth "$${x265_options[@]}" \
			-DHIGH_BIT_DEPTH=ON -DMAIN12=$$((depth == 12)) \
			-DEXPORT_C_API=OFF -DENABLE_SHARED=OFF \
			-DENABLE_PIC=ON; \
		cmake --build build-$$depth -j $(JOBS); \
	done; \
	cmake -S source -B build "$${x265_options[@]}" \
		-DCMAKE_INSTALL_PREFIX="$$target" \
		-DLIB_INSTALL_DIR=lib \
		-DHIGH_BIT_DEPTH=OFF \
		-DLINKED_10BIT=ON -DLINKED_12BIT=ON \
		-DEXTRA_LIB="$$work/build-10/libx265.a;$$work/build-12/libx265.a" \
		-DENABLE_SHARED=ON; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	rm "$$target/lib/libx265.a"; \
	mkdir -p "$$target/share/licenses"; \
	cp COPYING "$$target/share/licenses/x265-COPYING"; \
	printf '%s\n' "$(X265_SHA256)" > "$$stamp"

build/de265-$(DE265_VERSION).done: sources/de265-$(DE265_VERSION).tar.gz ../versions/de265.env | build/venv
	@$(call prepare,$(DE265_SHA256)) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$target" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DENABLE_ENCODER=OFF \
		-DENABLE_DECODER=OFF \
		-DENABLE_SDL=OFF \
		-DENABLE_SHERLOCK265=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$target/share/licenses"; \
	cp COPYING "$$target/share/licenses/libde265-COPYING"; \
	printf '%s\n' "$(DE265_SHA256)" > "$$stamp"

build/aom-$(AOM_VERSION).done: sources/aom-$(AOM_VERSION).tar.gz ../versions/aom.env | build/venv
	@$(call prepare,$(AOM_SHA256)) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$target" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DBUILD_SHARED_LIBS=ON \
		-DENABLE_TESTS=OFF \
		-DENABLE_APPS=OFF \
		-DENABLE_TOOLS=OFF \
		-DENABLE_EXAMPLES=OFF \
		-DENABLE_DOCS=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	rm "$$target/lib/libaom.a"; \
	rm -rf "$$target/lib/cmake/AOM"; \
	mkdir -p "$$target/share/licenses"; \
	cp LICENSE "$$target/share/licenses/aom-LICENSE"; \
	cp PATENTS "$$target/share/licenses/aom-PATENTS"; \
	printf '%s\n' "$(AOM_SHA256)" > "$$stamp"

build/sharpyuv-$(WEBP_VERSION).done: sources/sharpyuv-$(WEBP_VERSION).tar.gz ../versions/sharpyuv.env | build/venv
	@$(call prepare,$(WEBP_SHA256)) \
	./configure \
		--prefix="$$target" \
		--libdir="$$target/lib" \
		--disable-everything \
		--enable-shared \
		--disable-static \
		--disable-threading; \
	make -C sharpyuv -j $(JOBS) install; \
	mkdir -p "$$target/share/licenses"; \
	cp COPYING "$$target/share/licenses/libwebp-COPYING"; \
	cp PATENTS "$$target/share/licenses/libwebp-PATENTS"; \
	printf '%s\n' "$(WEBP_SHA256)" > "$$stamp"

build/libpng-$(LIBPNG_VERSION).done: sources/libpng-$(LIBPNG_VERSION).tar.gz ../versions/libpng.env | build/venv
	@$(call prepare,$(LIBPNG_SHA256)) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$target" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DPNG_STATIC=OFF \
		-DPNG_FRAMEWORK=OFF \
		-DPNG_TESTS=OFF \
		-DPNG_TOOLS=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$target/share/licenses"; \
	cp LICENSE "$$target/share/licenses/libpng-LICENSE"; \
	printf '%s\n' "$(LIBPNG_SHA256)" > "$$stamp"

build/libjpeg-$(LIBJPEG_VERSION).done: sources/libjpeg-$(LIBJPEG_VERSION).tar.gz ../versions/libjpeg.env | build/venv
	@$(call prepare,$(LIBJPEG_SHA256)) \
	cmake -S . -B build \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX="$$target" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DENABLE_STATIC=OFF \
		-DWITH_TURBOJPEG=OFF \
		-DWITH_TOOLS=OFF \
		-DWITH_TESTS=OFF; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$target/share/licenses"; \
	cp LICENSE.md "$$target/share/licenses/libjpeg-LICENSE.md"; \
	cp README.ijg "$$target/share/licenses/libjpeg-README.ijg"; \
	printf '%s\n' "$(LIBJPEG_SHA256)" > "$$stamp"

DEPENDENCY_PREFIXES := build/x265-$(X265_VERSION) \
    build/de265-$(DE265_VERSION) build/aom-$(AOM_VERSION) \
    build/sharpyuv-$(WEBP_VERSION) build/libpng-$(LIBPNG_VERSION) \
    build/libjpeg-$(LIBJPEG_VERSION)

define prepare_prefix
prefix="$(abspath build/prefix)"; \
rm -rf "$$prefix"; \
mkdir -p "$$prefix"; \
for dependency in $(abspath $(DEPENDENCY_PREFIXES)); do \
	cp -R "$$dependency/." "$$prefix/"; \
done;
endef

build/libheif-$(LIBHEIF_VERSION).done: sources/libheif-$(LIBHEIF_VERSION).tar.gz ../versions/libheif.env \
        $(addsuffix .done,$(DEPENDENCY_PREFIXES)) | build/venv
	@$(prepare) \
	$(prepare_prefix) \
	cmake --preset=release-noplugins -B build \
		-DCMAKE_INSTALL_PREFIX="$$target" \
		-DCMAKE_INSTALL_LIBDIR=lib \
		-DCMAKE_PREFIX_PATH="$$prefix" \
		-DCMAKE_IGNORE_PREFIX_PATH="/opt/homebrew;/usr/local" \
		-DCMAKE_DISABLE_FIND_PACKAGE_TIFF=ON \
		-DCMAKE_INCLUDE_PATH="$$prefix/include/webp" \
		-DWITH_JPEG_ENCODER=ON \
		-DWITH_JPEG_DECODER=ON \
		-DWITH_EXAMPLE_HEIF_VIEW=OFF \
		. 2>&1 | tee _configure.log; \
	grep -q 'Found PNG:' _configure.log; \
	grep -q 'Found JPEG:' _configure.log; \
	grep -q 'Found libsharpyuv:' _configure.log; \
	grep -q "'jpegenc' as built-in backend" _configure.log; \
	grep -q "'jpegdec' as built-in backend" _configure.log; \
	grep -q "'x265' as built-in backend" _configure.log; \
	grep -q "'libde265' as built-in backend" _configure.log; \
	grep -q "'aomdec' as built-in backend" _configure.log; \
	grep -q "'aomenc' as built-in backend" _configure.log; \
	cmake --build build -j $(JOBS); \
	cmake --install build; \
	mkdir -p "$$target/share/licenses"; \
	cp COPYING "$$target/share/licenses/libheif-COPYING"; \
	cp -R "$$target/." "$$prefix/"; \
	printf '%s\n' "$(LIBHEIF_SHA256)" > "$$stamp"

.PHONY: wheel
wheel: build/libheif-$(LIBHEIF_VERSION).done | build/venv
	# Prepare package files.
	@set -euo pipefail; \
	$(prepare_prefix) \
	cp -R "build/libheif-$(LIBHEIF_VERSION)/." "$$prefix/"; \
	wheel_root=build/wheel; \
	rm -rf $$wheel_root; \
	mkdir -p $$wheel_root; \
	cp -r ../libheif_binary ../pyproject.toml ../setup.py ../README.md $$wheel_root; \
	target=$$wheel_root/libheif_binary; \
	mkdir -p $$target/bin $$target/licenses $$target/include; \
	sed -n 's/^#define LIBHEIF_VERSION "\([^" ]*\)"/\1/p' \
		$$prefix/include/libheif/heif_version.h > $$target/LIBVERSION; \
	test -s $$target/LIBVERSION; \
	cp -r $$prefix/include/libheif $$target/include/; \
	sed -i '' 's/^#define LIBHEIF_PLUGIN_DIRECTORY .*/#define LIBHEIF_PLUGIN_DIRECTORY ""/' \
		$$target/include/libheif/heif_version.h; \
	cp $$prefix/share/licenses/* $$target/licenses/; \
	cp $$prefix/bin/heif-enc $$prefix/bin/heif-dec $$prefix/bin/heif-info $$target/bin/

	# Build the initial wheel and bundle dependencies
	@set -euo pipefail; \
	source build/venv/bin/activate; \
	platform=$$(python -c 'import platform, sysconfig; print(sysconfig.get_platform().rsplit("-", 1)[0] + "-" + platform.machine())'); \
	pip wheel ./build/wheel -w build/wheel \
		--config-settings=--build-option=--plat-name="$$platform"; \
	DYLD_LIBRARY_PATH=build/prefix/lib \
		delocate-wheel -L lib build/wheel/*.whl

	# Restore the stable libheif install ID and repack
	@set -euo pipefail; \
	source build/venv/bin/activate; \
	wheel unpack build/wheel/*.whl -d build/wheel/unpacked; \
	set -- build/wheel/unpacked/*/libheif_binary/lib/libheif.*.dylib; dylib=$$1; \
	install_name_tool -id '@rpath/libheif.1.dylib' "$$dylib"; \
	codesign --force --sign - "$$dylib"; \
	mkdir -p ../dist; \
	wheel pack build/wheel/unpacked/* -d ../dist

	# Test the installed wheel in a fresh temporary environment.
	@set -euo pipefail; \
	smoke_venv=$$(mktemp -d); \
	trap 'rm -rf "$$smoke_venv"' EXIT; \
	python3 -m venv "$$smoke_venv"; \
	source "$$smoke_venv/bin/activate"; \
	pip install "../dist/$$(basename build/wheel/*.whl)"; \
	tar -xOf sources/libheif-$(LIBHEIF_VERSION).tar.gz \
		"libheif-$(LIBHEIF_VERSION)/examples/example.heic" > build/example.heic; \
	python ../tests/smoke.py build/example.heic

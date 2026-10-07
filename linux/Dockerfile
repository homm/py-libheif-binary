ARG BASE=manylinux
FROM quay.io/pypa/manylinux_2_28:2026.10.03-1 AS manylinux-image
FROM quay.io/pypa/musllinux_1_2:2026.10.03-1 AS musllinux-image

# -------------------------------- manylinux-base --------------------------------------
FROM manylinux-image AS manylinux-base

ARG TARGETARCH
RUN --mount=type=cache,id=manylinux-2-28-dnf-${TARGETARCH},target=/var/cache/dnf,sharing=locked \
    dnf install -y --setopt=keepcache=True \
        nasm libpng-devel libjpeg-turbo-devel


# -------------------------------- musllinux-base --------------------------------------
FROM musllinux-image AS musllinux-base

RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --cache-dir /var/cache/apk \
        nasm libpng-dev libjpeg-turbo-dev


# -------------------------------- build-base ------------------------------------------
FROM ${BASE}-base AS build-base

ENV PATH="/opt/python/cp314-cp314/bin:${PATH}"
SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]
WORKDIR /build/src


# -------------------------------- build-patchelf --------------------------------------
FROM build-base AS build-patchelf

ENV LIEF_VERSION="1.0.0"

RUN case "$(uname -m)" in \
        x86_64) sha256="4c463a1d3014e32741fe88e4612105d27daef6975cdc3788752c1b3e5bf28e6b" ;; \
        aarch64) sha256="8183f2cddc0e33d88223600617db5ece393dbd430de9a9978b54b6b8875f5848" ;; \
    esac \
    && curl -fL "https://github.com/lief-project/LIEF/releases/download/${LIEF_VERSION}/lief-tools-$(uname -m)-unknown-linux-musl.zip" -o /tmp/lief-tools.zip \
    && echo "${sha256} */tmp/lief-tools.zip" | sha256sum -c - \
    && python -m zipfile -e /tmp/lief-tools.zip /tmp/lief-tools \
    && install /tmp/lief-tools/bin/lief-patchelf /usr/local/bin/ \
    && rm -rf /tmp/lief-tools /tmp/lief-tools.zip



# -------------------------------- build-x264 ------------------------------------------
FROM build-base AS build-x264

COPY versions/x264.env /build/x264.env

RUN . /build/x264.env \
    && curl -fL "${X264_URL}" -o ../x264.tar.gz \
    && echo "${X264_SHA256} *../x264.tar.gz" | sha256sum -c - \
    && tar -xOf ../x264.tar.gz "x264-${X264_COMMIT}/x264.h" \
        | grep "^#define X264_BUILD ${X264_BUILD}$"

RUN --mount=type=cache,id=libheif-build-lock,target=/tmp/libheif-build-lock,sharing=locked \
    tar xf ../x264.tar.gz --strip-components=1 \
    && ./configure \
        --prefix=/usr/local \
        --libdir=/usr/local/lib \
        --enable-shared \
        --enable-pic \
        --disable-cli \
        --disable-opencl \
    && make -j $(nproc) \
    && make install DESTDIR=/opt \
    && install -D COPYING /opt/usr/local/share/licenses/x264-COPYING \
    && rm -rf /build/*


# -------------------------------- build-x265 ------------------------------------------
FROM build-base AS build-x265

COPY versions/x265.env /build/x265.env

RUN . /build/x265.env \
    && curl -fL "${X265_URL}" -o ../x265.tar.gz \
    && echo "${X265_SHA256} *../x265.tar.gz" | sha256sum -c -

RUN --mount=type=cache,id=libheif-build-lock,target=/tmp/libheif-build-lock,sharing=locked \
    tar xf ../x265.tar.gz --strip-components=1 \
    && cmake -S source -B ../build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DENABLE_CLI=OFF \
    && cmake --build ../build -j $(nproc) \
    && DESTDIR=/opt cmake --install ../build \
    && install -D COPYING /opt/usr/local/share/licenses/x265-COPYING \
    && rm -rf /build/*


# -------------------------------- build-de265 -----------------------------------------
FROM build-base AS build-de265

COPY versions/de265.env /build/de265.env

RUN . /build/de265.env \
    && curl -fL "${DE265_URL}" -o ../libde265.tar.gz \
    && echo "${DE265_SHA256} *../libde265.tar.gz" | sha256sum -c -

RUN --mount=type=cache,id=libheif-build-lock,target=/tmp/libheif-build-lock,sharing=locked \
    tar xf ../libde265.tar.gz --strip-components=1 \
    && cmake -B ../build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DENABLE_ENCODER=OFF \
        -DENABLE_DECODER=OFF \
        -DENABLE_SHERLOCK265=OFF \
    && cmake --build ../build -j $(nproc) \
    && DESTDIR=/opt cmake --install ../build \
    && install -D COPYING /opt/usr/local/share/licenses/libde265-COPYING \
    && rm -rf /build/*


# -------------------------------- build-aom -------------------------------------------
FROM build-base AS build-aom

COPY versions/aom.env /build/aom.env

RUN . /build/aom.env \
    && curl -fL "${AOM_URL}" -o ../aom.tar.gz \
    && echo "${AOM_SHA256} *../aom.tar.gz" | sha256sum -c -

RUN --mount=type=cache,id=libheif-build-lock,target=/tmp/libheif-build-lock,sharing=locked \
    tar xf ../aom.tar.gz --strip-components=1 \
    && cmake -B ../build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DBUILD_SHARED_LIBS=ON \
        -DENABLE_TESTS=OFF \
        -DENABLE_APPS=OFF \
        -DENABLE_TOOLS=OFF \
        -DENABLE_EXAMPLES=OFF \
        -DENABLE_DOCS=OFF \
    && cmake --build ../build -j $(nproc) \
    && DESTDIR=/opt cmake --install ../build \
    && install -D LICENSE /opt/usr/local/share/licenses/aom-LICENSE \
    && install -D PATENTS /opt/usr/local/share/licenses/aom-PATENTS \
    && rm -rf /build/*


# -------------------------------- build-sharpyuv --------------------------------------
FROM build-base AS build-sharpyuv

COPY versions/sharpyuv.env /build/sharpyuv.env

RUN . /build/sharpyuv.env \
    && curl -fL "${WEBP_URL}" -o ../libwebp.tar.gz \
    && echo "${WEBP_SHA256} *../libwebp.tar.gz" | sha256sum -c -

RUN --mount=type=cache,id=libheif-build-lock,target=/tmp/libheif-build-lock,sharing=locked \
    tar xf ../libwebp.tar.gz --strip-components=1 \
    && ./autogen.sh \
    && ./configure \
        --prefix=/usr/local \
        --libdir=/usr/local/lib \
        --disable-everything \
        --disable-shared \
        --disable-threading \
    && make -C sharpyuv -j $(nproc) CFLAGS='-fPIC' install DESTDIR=/opt \
    && install -D COPYING /opt/usr/local/share/licenses/libwebp-COPYING \
    && install -D PATENTS /opt/usr/local/share/licenses/libwebp-PATENTS \
    && rm -rf /build/*


# -------------------------------- build-libheif ---------------------------------------
FROM build-base AS build-libheif

COPY versions/libheif.env /build/libheif.env

RUN . /build/libheif.env \
    && curl -fL "${LIBHEIF_URL}" -o ../libheif.tar.gz \
    && echo "${LIBHEIF_SHA256} *../libheif.tar.gz" | sha256sum -c - \
    && mkdir -p /src \
    && tar xf ../libheif.tar.gz --strip-components=1 -C /src \
    && rm -rf /build/*

COPY --from=build-x264 /opt/usr/local/ /usr/local/
COPY --from=build-x265 /opt/usr/local/ /usr/local/
COPY --from=build-de265 /opt/usr/local/ /usr/local/
COPY --from=build-aom /opt/usr/local/ /usr/local/
COPY --from=build-sharpyuv /opt/usr/local/ /usr/local/
RUN ldconfig || true

WORKDIR /src/build

RUN cmake --preset=release-noplugins \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DWITH_EXAMPLE_HEIF_THUMB=OFF \
        .. 2>&1 | tee _configure.log \
    && grep -q 'Found PNG:' _configure.log \
    && grep -q 'Found JPEG:' _configure.log \
    && grep -q 'Found libsharpyuv:' _configure.log \
    && grep -q "'x264' as built-in backend" _configure.log \
    && grep -q "'x265' as built-in backend" _configure.log \
    && grep -q "'libde265' as built-in backend" _configure.log \
    && grep -q "'aomdec' as built-in backend" _configure.log \
    && grep -q "'aomenc' as built-in backend" _configure.log

RUN cmake --build . -j $(nproc) \
    && cmake --install . \
    && install -D ../COPYING /usr/local/share/licenses/libheif-COPYING

COPY --from=build-patchelf /usr/local/bin/lief-patchelf /usr/local/bin/

WORKDIR /package
COPY pyproject.toml setup.py README.md ./
COPY libheif_binary ./libheif_binary

RUN sed -n 's/^#define LIBHEIF_VERSION "\([^"]*\)"/\1/p' \
        /usr/local/include/libheif/heif_version.h > libheif_binary/LIBVERSION \
    && test -s libheif_binary/LIBVERSION \
    && cp -r /usr/local/share/licenses libheif_binary/licenses \
    && mkdir -p libheif_binary/bin libheif_binary/lib \
    && cp -L /usr/local/lib/libheif.so.1 libheif_binary/lib/ \
    && cc -shared -fPIC -x c /dev/null \
        -L/usr/local/lib \
        -Wl,--no-as-needed -lheif -lc -Wl,--as-needed \
        -Wl,-rpath,'$ORIGIN' \
        -o libheif_binary/lib/libheif-loader.so \
    && cp /usr/local/bin/heif-enc /usr/local/bin/heif-dec /usr/local/bin/heif-info libheif_binary/bin/ \
    && for executable in libheif_binary/bin/*; do \
        lief-patchelf --set-rpath '$ORIGIN/../lib' "$executable"; \
    done

RUN pip wheel --no-deps . -w /unrepaired \
    && auditwheel repair --patcher lief-patchelf --lib-sdir /lib --plat "$AUDITWHEEL_PLAT" -w /wheelhouse /unrepaired/*.whl \
    && rm -r /unrepaired


# -------------------------------- tested ----------------------------------------------
FROM ${BASE}-image AS tested

ARG BASE
SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]
WORKDIR /tmp
COPY --from=build-libheif /wheelhouse/ /wheelhouse/
COPY tests/smoke.py /tmp/smoke.py
COPY --from=build-libheif /src/examples/example.heic /tmp/example.heic

RUN interpreters=(/opt/python/cp39-cp39 /opt/python/cp314-cp314 /opt/python/cp314-cp314t) \
    && if [ "$BASE" = manylinux ]; then interpreters+=(/opt/python/pp*); fi \
    && for interpreter in "${interpreters[@]}"; do \
        ( \
            export PATH="$interpreter/bin:$PATH"; \
            pip install /wheelhouse/*.whl; \
            python /tmp/smoke.py /tmp/example.heic; \
        ); \
    done

RUN library_dir=$(/opt/python/cp39-cp39/bin/python -c 'import libheif_binary as l; print(l.__path__[0]+"/lib")') \
    && readelf -d "$library_dir/libheif.so.1" | grep 'SONAME.*\[libheif.so.1\]' \
    && for library in "$library_dir"/*; do \
        ldd "$library" > /tmp/ldd.log; \
        if grep -q 'not found' /tmp/ldd.log; then cat /tmp/ldd.log; exit 1; fi; \
    done


# -------------------------------- wheel export ----------------------------------------
FROM scratch AS wheel
COPY --from=tested /wheelhouse/ /

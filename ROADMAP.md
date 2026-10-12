# Roadmap

## Extended bundle

Provide an optional extended bundle alongside the base HEIC, AVIF and
JPEG-in-HEIF bundle. The extended bundle is not implemented yet.

| Backend | Role | Purpose |
| --- | --- | --- |
| dav1d | AV1 decoder | Faster AVIF decoding |
| SVT-AV1 | AV1 encoder | Alternative encoding speed/quality tradeoffs |
| Kvazaar | HEVC encoder | BSD-licensed alternative to x265 |
| rav1e | AV1 encoder | Candidate only; justify its Rust toolchain with still-image benchmarks or user demand |
| OpenH264 | AVC decoder | Dedicated decoding without FFmpeg |
| x264 | AVC encoder | Pair AVC encoding with OpenH264 decoding |

Retain the existing x264 build recipes for this future work. Exclude FFmpeg,
VVC, JPEG 2000 and HTJ2K from the proposed bundle.

Before release, verify codec capabilities and wheel builds on both Linux libc
variants and macOS, including x86_64 and arm64. Compare AVIF encoders at matched
quality and chroma sampling rather than matching their quality/preset numbers.

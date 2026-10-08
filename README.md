# libheif_binary

Prebuilt libheif and its codec libraries for Python packages that read and write
HEIF and AVIF images. The package bundles native libraries and the `heif-enc`,
`heif-dec` and `heif-info` commands, with a small Python API for loading libheif.
It does not provide Python image objects or bindings to the full libheif API.


## Supported platforms and Python versions

Requires Python **3.6 or newer** and a wheel matching your operating system
and architecture.

| Platform | Minimum system requirement | Architectures | Python |
| --- | --- | --- | --- |
| Linux, glibc (`manylinux_2_28`) | glibc 2.28 | x86_64, aarch64 | 3.6+ |
| Linux, musl (`musllinux_1_2`) | musl 1.2, including compatible Alpine Linux releases | x86_64, aarch64 | 3.6+ |
| macOS | macOS 11 | x86_64, arm64; combined universal2 wheel | 3.6+ |

Windows is not supported.

Compatibility and test coverage are distinct:

| Build | Python versions checked by CI |
| --- | --- |
| Linux, glibc | CPython 3.9, 3.14 and 3.14 free-threaded; PyPy interpreters included in the build image |
| Linux, musl | CPython 3.9, 3.14 and 3.14 free-threaded |
| macOS, including both universal2 architectures | CPython 3.12 |


## Installation

Install the package:

```sh
pip install libheif_binary
```

The native libraries and CLI tools are bundled in the wheel. You do not need
to install libheif or its codecs separately.


## Python API

`get_version_str()` returns the bundled libheif version as a string, such as
`"1.17.6"`. `get_version()` returns it as an integer tuple, such as
`(1, 17, 6)`.

`get_build_config()` returns cffi compiler and linker arguments for the bundled
headers and library:

```python
from cffi import FFI
from libheif_binary import get_build_config

ffi = FFI()
ffi.set_source("_libheif", "#include <libheif/heif.h>", **get_build_config())
```

`get_executable(name)` returns an absolute path to `heif-enc`, `heif-dec` or
`heif-info`.

On Linux and macOS, preload the bundled library before importing a Python
extension linked against libheif:

```python
from libheif_binary import load_library

_libheif_handle = load_library()
from your_package import _libheif_cffi
```

Replace `your_package._libheif_cffi` with your extension module. Keep the returned
`ctypes.CDLL` object alive until the extension has finished importing. The library
is loaded with `RTLD_GLOBAL` so its symbols are available to linked extensions.


## Command-line tools

Installation adds these commands to the Python environment:

| Command | Purpose |
| --- | --- |
| `heif-enc` | Encode images as HEIF or AVIF |
| `heif-dec` | Decode HEIF or AVIF images, including PNG and JPEG output |
| `heif-info` | Inspect image metadata and container information |

Use `--help` for the options supported by the bundled libheif version:

```sh
heif-enc --help
heif-dec --help
heif-info --help
```

By default, these commands start a Python wrapper that executes the native tool.
To run them directly without starting Python, replace the wrappers in the
installed environment with relative symlinks:

```sh
libheif-link-cli
```

This is optional and requires write access to the environment's scripts directory.
Run it again after reinstalling or upgrading the package.


## Building wheels

Run the following commands from the repository root. Wheels are saved in `dist/`.
Dependency versions and source checksums are pinned in `versions/*.env`.
The package version is `<libheif version>.<packaging revision>`.


### Linux

With Docker running, build for glibc or musl:

```sh
make -C linux manylinux
make -C linux musllinux
```

To select an architecture, add `ARCH=amd64` or `ARCH=arm64`:

```sh
make -C linux manylinux ARCH=arm64
```

Each build tests the installed wheel before exporting it.

### macOS

Build with Python (3.12 tested) and the Xcode command-line tools:

```sh
make -C macos
```

The wheel targets the current architecture.


## Testing

Run the unit tests from the repository root:

```sh
pytest tests -v
```

To test an installed wheel, run the smoke test:

```sh
python tests/smoke.py /path/to/example.heic
```

Use `examples/example.heic` from the pinned libheif source release.


## Bundled libraries and licenses

The package includes `libheif`, `x264`, `x265`, `libde265`, `libaom`, `libsharpyuv`,
`libpng` and `libjpeg-turbo`.

License and patent notices for bundled dependencies are included in the
installed package's `libheif_binary/licenses/` directory.

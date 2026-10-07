# libheif_binary

Prebuilt libheif and its codec libraries for Python packages that need to read
and write HEIF and AVIF images. Includes the `heif-enc`, `heif-dec` and
`heif-info` commands.

To build a Linux wheel, run this from the repository directory with Docker running:

```sh
make manylinux
```

For Alpine Linux (musl), use `make musllinux` instead.

The wheel is saved in `dist/`. Install it with:

```sh
python -m pip install dist/*.whl
```

To build for a specific architecture, pass `PLATFORM=linux/amd64` or
`PLATFORM=linux/arm64` to make.

To run the CLI tools without starting Python first, replace their wrappers with
symlinks in the installed environment:

```sh
libheif-link-cli
```

Run it again after reinstalling or upgrading the package.

On Linux, preload the bundled library and keep the returned `CDLL`
object alive until your linked Python extension has finished importing:

```python
from libheif_binary import load_library

_libheif_handle = load_library()
from your_package import _libheif_cffi
```

Preloading on macOS and Windows is not yet implemented.

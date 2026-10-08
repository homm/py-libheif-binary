import os
import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
EXECUTABLES = ("heif-enc", "heif-dec", "heif-info")


def get_version_str():
    """Return the bundled libheif version as a string."""
    return (PACKAGE_DIR / "LIBVERSION").read_text().strip()


def get_version():
    """Return the bundled libheif version as a tuple of integers."""
    return tuple(int(part) for part in get_version_str().split("."))


def get_build_config():
    """Return compiler and linker arguments for cffi.set_source()."""
    if sys.platform == "darwin":
        library = "heif." + get_version_str()
    else:
        library = ":libheif.so.1"
    return {
        "include_dirs": [str(PACKAGE_DIR / "include")],
        "library_dirs": [str(PACKAGE_DIR / "lib")],
        "libraries": [library],
    }


def get_executable(name):
    """Return the absolute path to a bundled HEIF command."""
    if name not in EXECUTABLES:
        raise ValueError(f"Unknown HEIF command: {name}")
    return str(PACKAGE_DIR / "bin" / name)


def load_library():
    """Preload bundled libheif before importing a linked extension."""
    import ctypes

    if sys.platform == "darwin":
        path = PACKAGE_DIR / "lib" / f"libheif.{get_version_str()}.dylib"
    else:
        path = PACKAGE_DIR / "lib" / "libheif-loader.so"
    return ctypes.CDLL(str(path), mode=ctypes.RTLD_GLOBAL)


def _run(name):
    executable = get_executable(name)
    os.execv(executable, [executable, *sys.argv[1:]])


def heif_enc():
    _run("heif-enc")


def heif_dec():
    _run("heif-dec")


def heif_info():
    _run("heif-info")


def link_cli():
    import sysconfig
    import tempfile

    action = "resolve the package and environment paths"
    try:
        scripts = Path(sysconfig.get_path("scripts")).resolve()
        binaries = PACKAGE_DIR / "bin"
        for name in EXECUTABLES:
            executable = binaries / name
            action = f"check binary {executable}"
            if not executable.is_file():
                sys.exit(f"Cannot link CLI: binary missing or not a regular file: {executable}")
        action = f"create temporary links in {scripts}"
        with tempfile.TemporaryDirectory(dir=scripts) as directory:
            for name in EXECUTABLES:
                executable = binaries / name
                link = Path(directory) / name
                action = f"create symlink for {name}"
                link.symlink_to(os.path.relpath(executable, scripts))
                action = f"replace {scripts / name} with a symlink"
                link.replace(scripts / name)
            action = f"remove temporary links from {scripts}"
    except PermissionError as error:
        sys.exit(
            f"Cannot {action}: permission denied ({error.filename}). "
            "Check directory permissions and ownership."
        )
    except OSError as error:
        sys.exit(f"Cannot {action}: {error.strerror or error}.")
    print(f"Linked HEIF commands in {scripts}")

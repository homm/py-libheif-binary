import os
import sys
from pathlib import Path


def load_library():
    """Preload bundled libheif before importing a linked extension."""
    import ctypes

    package = Path(__file__).resolve().parent
    if sys.platform == "darwin":
        version = (package / "LIBVERSION").read_text().strip()
        path = package / "lib" / f"libheif.{version}.dylib"
    else:
        path = package / "lib" / "libheif-loader.so"
    return ctypes.CDLL(str(path), mode=ctypes.RTLD_GLOBAL)


def _run(name):
    executable = str(Path(__file__).parent / "bin" / name)
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
        binaries = Path(__file__).resolve().parent / "bin"
        names = ("heif-enc", "heif-dec", "heif-info")
        for name in names:
            executable = binaries / name
            action = f"check binary {executable}"
            if not executable.is_file():
                sys.exit(f"Cannot link CLI: binary missing or not a regular file: {executable}")
        action = f"create temporary links in {scripts}"
        with tempfile.TemporaryDirectory(dir=scripts) as directory:
            for name in names:
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

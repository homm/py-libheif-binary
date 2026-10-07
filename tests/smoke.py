import ctypes
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

import libheif_binary


package = Path(libheif_binary.__file__).resolve().parent
lib = libheif_binary.load_library()
other = libheif_binary.load_library()
assert other is not lib
assert ctypes.cast(other.heif_get_version, ctypes.c_void_p).value == ctypes.cast(lib.heif_get_version, ctypes.c_void_p).value
resident = ctypes.CDLL("libheif.so.1", mode=os.RTLD_NOLOAD | os.RTLD_NOW)
bundled = ctypes.CDLL(str(package / "lib" / "libheif.so.1"), mode=os.RTLD_NOLOAD | os.RTLD_NOW)
assert ctypes.cast(resident.heif_get_version, ctypes.c_void_p).value == ctypes.cast(bundled.heif_get_version, ctypes.c_void_p).value
lib.heif_get_version.restype = ctypes.c_char_p
assert lib.heif_get_version().decode() == (package / "LIBVERSION").read_text().strip()

for name in ("heif-enc", "heif-dec", "heif-info"):
    executable = shutil.which(name)
    assert executable and Path(executable).parent == Path(sys.executable).parent
    subprocess.run([name, "--help"], check=True)
arguments = ["--invalid-option"]
wrapped = subprocess.run(["heif-enc", *arguments], capture_output=True)
native = subprocess.run([str(package / "bin" / "heif-enc"), *arguments], capture_output=True)
assert wrapped.returncode == native.returncode
assert wrapped.stdout == native.stdout
assert wrapped.stderr == native.stderr, (sys.executable, wrapped.stderr, native.stderr)
subprocess.run(["libheif-link-cli"], check=True)
for name in ("heif-enc", "heif-dec", "heif-info"):
    executable = Path(shutil.which(name))
    assert executable.is_symlink()
    assert executable.resolve() == (package / "bin" / name).resolve()
    subprocess.run([name, "--help"], check=True)
encoders = subprocess.check_output(["heif-enc", "--list-encoders"], text=True)
for encoder in ("x264", "x265", "aom"):
    assert encoder in encoders, encoders


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


with tempfile.TemporaryDirectory() as directory:
    work = Path(directory)
    subprocess.run(["heif-dec", sys.argv[1], str(work / "example.png")], check=True)
    subprocess.run(["heif-dec", sys.argv[1], str(work / "example.jpg")], check=True)
    # The upstream example contains two images; heif-dec numbers its outputs.
    for index in (1, 2):
        assert (work / f"example-{index}.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert (work / f"example-{index}.jpg").read_bytes().startswith(b"\xff\xd8")
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", struct.pack(">IIBBBBB", 16, 16, 8, 2, 0, 0, 0))
    png += png_chunk(b"IDAT", zlib.compress((b"\0" + b"\x80\x40\x20" * 16) * 16))
    png += png_chunk(b"IEND", b"")
    source = work / "input.png"
    source.write_bytes(png)
    for suffix, options in (("heic", ["-e", "x265"]), ("avif", ["-A", "-e", "aom"])):
        encoded = work / ("encoded." + suffix)
        decoded = work / (suffix + ".png")
        subprocess.run(["heif-enc", *options, "-o", str(encoded), str(source)], check=True)
        subprocess.run(["heif-dec", str(encoded), str(decoded)], check=True)
        assert struct.unpack(">II", decoded.read_bytes()[16:24]) == (16, 16)
print("Wheel smoke tests passed:", lib.heif_get_version().decode())

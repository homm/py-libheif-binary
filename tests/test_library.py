import ctypes
import threading
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import call, patch

import libheif_binary


class VersionTest(unittest.TestCase):
    def test_returns_bundled_version_as_string_without_surrounding_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory).resolve()
            (package / "LIBVERSION").write_text(" 1.17.6\n")
            with patch.object(libheif_binary, "PACKAGE_DIR", package):
                self.assertEqual(libheif_binary.get_version_str(), "1.17.6")

    def test_returns_bundled_version_as_integer_tuple(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory).resolve()
            (package / "LIBVERSION").write_text("1.17.6\n")
            with patch.object(libheif_binary, "PACKAGE_DIR", package):
                self.assertEqual(libheif_binary.get_version(), (1, 17, 6))


class BuildConfigTest(unittest.TestCase):
    def test_linux_config_uses_bundled_paths_and_exact_library_filename(self):
        package = Path("relative/libheif_binary").resolve()
        with patch.object(libheif_binary.sys, "platform", "linux"), patch.object(
            libheif_binary, "PACKAGE_DIR", package
        ):
            self.assertEqual(libheif_binary.get_build_config(), {
                "include_dirs": [str(package / "include")],
                "library_dirs": [str(package / "lib")],
                "libraries": [":libheif.so.1"],
            })

    def test_macos_config_uses_recorded_version_for_library_name(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory).resolve()
            for version in ("1.17.6", "1.23.6"):
                with self.subTest(version=version):
                    (package / "LIBVERSION").write_text(version + "\n")
                    with patch.object(libheif_binary.sys, "platform", "darwin"), patch.object(
                        libheif_binary, "PACKAGE_DIR", package
                    ):
                        self.assertEqual(libheif_binary.get_build_config(), {
                            "include_dirs": [str(package / "include")],
                            "library_dirs": [str(package / "lib")],
                            "libraries": ["heif." + version],
                        })


class LoadLibraryTest(unittest.TestCase):
    def setUp(self):
        platform = patch.object(libheif_binary.sys, "platform", "linux")
        platform.start()
        self.addCleanup(platform.stop)

    def test_macos_loads_bundled_library_with_recorded_version(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory).resolve()
            (package / "LIBVERSION").write_text("1.23.6\n")
            with patch.object(libheif_binary.sys, "platform", "darwin"), patch.object(
                libheif_binary, "PACKAGE_DIR", package
            ), patch.object(ctypes, "CDLL") as load:
                self.assertIs(libheif_binary.load_library(), load.return_value)
                load.assert_called_once_with(
                    str(package / "lib/libheif.1.23.6.dylib"), mode=ctypes.RTLD_GLOBAL
                )

    def test_each_call_returns_its_own_library_object(self):
        handles = [object(), object()]
        with patch.object(
            libheif_binary, "PACKAGE_DIR", Path("/different/site-packages/libheif_binary").resolve()
        ), patch.object(ctypes, "CDLL", side_effect=handles) as load:
            first = libheif_binary.load_library()
            second = libheif_binary.load_library()
            self.assertIs(first, handles[0])
            self.assertIs(second, handles[1])
            self.assertIsNot(first, second)
            expected = call(
                str(Path("/different/site-packages/libheif_binary/lib/libheif-loader.so").resolve()),
                mode=ctypes.RTLD_GLOBAL,
            )
            self.assertEqual(load.call_args_list, [expected, expected])

    def test_loading_error_propagates_and_next_call_succeeds(self):
        error = OSError("dependency missing")
        handle = object()
        with patch.object(ctypes, "CDLL", side_effect=[error, handle]) as load:
            with self.assertRaises(OSError) as caught:
                libheif_binary.load_library()
            self.assertIs(caught.exception, error)
            self.assertIs(libheif_binary.load_library(), handle)
            self.assertEqual(load.call_count, 2)

    def test_concurrent_calls_return_independent_library_objects(self):
        barrier = threading.Barrier(8)

        def worker():
            barrier.wait(timeout=5)
            return libheif_binary.load_library()

        with patch.object(
            ctypes, "CDLL", side_effect=lambda *args, **kwargs: object()
        ) as loader, ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(worker) for _ in range(8)]
            handles = [future.result(timeout=5) for future in futures]
            self.assertEqual(len({id(handle) for handle in handles}), 8)
            self.assertEqual(loader.call_count, 8)

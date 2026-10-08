import os
import sysconfig
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import libheif_binary


class ExecutableTest(unittest.TestCase):
    def test_known_commands_return_absolute_paths_without_requiring_files(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory).resolve()
            with patch.object(libheif_binary, "PACKAGE_DIR", package):
                for name in ("heif-enc", "heif-dec", "heif-info"):
                    with self.subTest(name=name):
                        self.assertEqual(
                            libheif_binary.get_executable(name), str(package / "bin" / name)
                        )

    def test_unknown_commands_and_paths_raise_value_error(self):
        for name in ("unknown", "../heif-dec", "/tmp/heif-dec", ""):
            with self.subTest(name=name), self.assertRaises(ValueError):
                libheif_binary.get_executable(name)

    def test_wrappers_execute_resolved_command_with_original_arguments(self):
        for name, wrapper in (
            ("heif-enc", libheif_binary.heif_enc),
            ("heif-dec", libheif_binary.heif_dec),
            ("heif-info", libheif_binary.heif_info),
        ):
            with self.subTest(name=name), patch.object(
                libheif_binary, "get_executable", return_value="/bundled/bin/" + name
            ) as executable, patch.object(libheif_binary.os, "execv") as execute, patch.object(
                libheif_binary.sys, "argv", ["wrapper", "--help", "file with spaces.heic"]
            ):
                wrapper()
                executable.assert_called_once_with(name)
                execute.assert_called_once_with(
                    "/bundled/bin/" + name,
                    ["/bundled/bin/" + name, "--help", "file with spaces.heic"],
                )


class LinkCliTest(unittest.TestCase):
    def test_links_replace_wrappers_and_survive_environment_move(self):
        with tempfile.TemporaryDirectory() as directory:
            environment = Path(directory) / "venv"
            scripts = environment / "bin"
            package = environment / "lib/python3.14/site-packages/libheif_binary"
            binaries = package / "bin"
            scripts.mkdir(parents=True)
            binaries.mkdir(parents=True)
            names = ("heif-enc", "heif-dec", "heif-info")
            for name in names:
                (scripts / name).write_text("wrapper")
                (binaries / name).write_text("binary")
            with patch.object(libheif_binary, "PACKAGE_DIR", package.resolve()), patch.object(
                sysconfig, "get_path", return_value=str(scripts)
            ):
                libheif_binary.link_cli()
                libheif_binary.link_cli()
            moved = Path(directory) / "moved"
            environment.rename(moved)
            for name in names:
                link = moved / "bin" / name
                self.assertTrue(link.is_symlink())
                self.assertFalse(os.path.isabs(os.readlink(link)))
                self.assertEqual(
                    link.resolve(),
                    (moved / "lib/python3.14/site-packages/libheif_binary/bin" / name).resolve(),
                )

    def test_missing_binary_leaves_wrappers_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            scripts = Path(directory) / "bin"
            scripts.mkdir()
            wrapper = scripts / "heif-enc"
            wrapper.write_text("wrapper")
            with patch.object(libheif_binary, "PACKAGE_DIR", Path(directory) / "package"), patch.object(
                sysconfig, "get_path", return_value=str(scripts)
            ):
                with self.assertRaisesRegex(SystemExit, "binary missing.*heif-enc"):
                    libheif_binary.link_cli()
            self.assertEqual(wrapper.read_text(), "wrapper")

    def test_permission_error_explains_directory_access(self):
        with patch.object(Path, "is_file", return_value=True), patch.object(
            tempfile, "TemporaryDirectory",
            side_effect=PermissionError(13, "Permission denied", "/venv/bin"),
        ):
            with self.assertRaisesRegex(SystemExit, "create temporary links.*permission denied.*ownership"):
                libheif_binary.link_cli()

    def test_replacement_error_names_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(sysconfig, "get_path", return_value=directory), patch.object(
                Path, "is_file", return_value=True
            ), patch.object(Path, "replace", side_effect=OSError(30, "Read-only file system")):
                with self.assertRaisesRegex(SystemExit, "replace .*heif-enc.*Read-only file system"):
                    libheif_binary.link_cli()

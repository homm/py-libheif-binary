import os
import sysconfig
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import libheif_binary


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
            with patch.object(libheif_binary, "__file__", str(package / "__init__.py")), patch.object(
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
            with patch.object(libheif_binary, "__file__", str(Path(directory) / "package/__init__.py")), patch.object(
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

import hashlib
import io
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


MAKEFILE = Path(__file__).resolve().parents[1] / "versions/Makefile"


class DependencyUpdatesTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.pin = self.root / "libpng.env"
        self.before = (
            "LIBPNG_VERSION=1.6.9\n"
            "LIBPNG_SHA256=" + "0" * 64 + "\n"
            "LIBPNG_URL=" + self.root.as_uri() + "/libpng-${LIBPNG_VERSION}.tar.gz\n"
        )
        self.pin.write_text(self.before)
        self.archive = self.root / "libpng-1.6.100.tar.gz"
        with tarfile.open(self.archive, "w:gz") as archive:
            content = b"source archive\n"
            info = tarfile.TarInfo("source/README")
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))

    def run_make(self, releases, target="libpng.env"):
        (self.root / "releases.txt").write_text("\n".join(releases) + "\n")
        return subprocess.run(
            ["make", "--no-print-directory", "-f", str(MAKEFILE),
             target, "DISCOVER=cat releases.txt"],
            cwd=self.root, text=True, capture_output=True,
        )

    def test_selects_newest_stable_numerically_and_updates_version_and_checksum(self):
        result = self.run_make(["v1.6.99", "v9.0.0-rc1", "v1.6.100", "v1.6.10"])
        self.assertEqual(result.returncode, 0, result.stderr)
        checksum = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        expected = self.before.replace(
            "LIBPNG_VERSION=1.6.9\n", "LIBPNG_VERSION=1.6.100\n"
        )
        expected = expected.replace("0" * 64, checksum)
        self.assertEqual(self.pin.read_text(), expected)

    def test_older_and_equal_releases_do_not_change_pin(self):
        for releases in (["v1.6.8", "v1.5.99"], ["v1.6.9", "v1.6.8"]):
            with self.subTest(releases=releases):
                result = self.run_make(releases)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.pin.read_text(), self.before)

    def test_x264_updates_commit_checksum_and_build_number(self):
        current = "a" * 40
        latest = "b" * 40
        pin = self.root / "x264.env"
        before = (
            "X264_COMMIT=" + current + "\n"
            "X264_SHA256=" + "0" * 64 + "\n"
            "X264_BUILD=165\n"
            "X264_URL=" + self.root.as_uri() + "/x264-${X264_COMMIT}.tar.gz\n"
        )
        pin.write_text(before)
        source = self.root / ("x264-" + latest + ".tar.gz")
        with tarfile.open(source, "w:gz") as archive:
            content = b"#define X264_BUILD 166\n"
            info = tarfile.TarInfo("x264-" + latest + "/x264.h")
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
        result = self.run_make([latest], "x264.env")
        self.assertEqual(result.returncode, 0, result.stderr)
        checksum = hashlib.sha256(source.read_bytes()).hexdigest()
        expected = (
            before.replace(current, latest).replace("0" * 64, checksum)
            .replace("X264_BUILD=165", "X264_BUILD=166")
        )
        self.assertEqual(pin.read_text(), expected)

    def test_failed_download_or_invalid_archive_leaves_pin_unchanged(self):
        self.archive.unlink()
        for failure in ("download", "invalid archive"):
            with self.subTest(failure=failure):
                if failure == "invalid archive":
                    self.archive.write_text("not an archive")
                result = self.run_make(["v1.6.100"])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Failed to update libpng.env:", result.stderr)
                self.assertIn(
                    "curl -fsSL" if failure == "download" else "tar -tzf", result.stderr
                )
                self.assertEqual(self.pin.read_text(), self.before)

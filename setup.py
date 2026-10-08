from pathlib import Path

from setuptools import Distribution, setup
from wheel.bdist_wheel import bdist_wheel


REVISION = 2
LIBVERSION = Path('libheif_binary/LIBVERSION').read_text().strip()


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


class BinaryWheel(bdist_wheel):
    def get_tag(self):
        return "py3", "none", super().get_tag()[2]


setup(
    version=f"{LIBVERSION}.{REVISION}",
    distclass=BinaryDistribution,
    cmdclass={"bdist_wheel": BinaryWheel},
)

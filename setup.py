import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


def run_post_install():
    """Run optional post-install setup."""
    try:
        import vm.post_install as pi
        pi.run_post_install()
    except Exception as e:
        print(f"  Post-install optionnel ignore: {e}")


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        if "bdist_wheel" not in sys.argv:
            run_post_install()


class PostDevelopCommand(develop):
    def run(self):
        develop.run(self)
        run_post_install()


long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="oktopios",
    version="0.0.21",
    description="Oktopios - un langage de programmation moderne, expressif et bio-inspire",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mouanwiya Ali Soule",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(include=["vm", "vm.*"]),
    install_requires=[
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "psutil>=5.9",
    ],
    entry_points={
        "console_scripts": [
            "okp=vm.main:main",
            "okp-setup=vm.post_install:run_post_install",
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
    include_package_data=True,
    package_data={
        "vm": [
            "modules/*.okp",
            "heart/*.py",
            "assets/icons/*.png",
            "assets/icons/*.ico",
        ],
    },
)

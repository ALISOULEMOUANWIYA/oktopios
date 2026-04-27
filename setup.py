from setuptools import setup, find_packages
import os

long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="oktopios",
    version="0.0.4",
    description="Oktopios — un langage de programmation moderne et expressif",
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
        ],
    },
    include_package_data=True,
    package_data={
        "vm": ["modules/*.okp", "heart/*.py"],
    },
)

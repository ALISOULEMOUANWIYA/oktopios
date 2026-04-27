from setuptools import setup, find_packages

setup(
    name="oktopios",
    version="0.0.1",
    description="Oktopios — un langage de programmation moderne et expressif 🐙",
    author="Mouanwiya Ali Soule",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "okp=vm.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["metadata/*.txt", "metadata/*.md", "vm/modules/*.okp"],
    },
)

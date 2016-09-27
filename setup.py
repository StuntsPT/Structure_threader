#!/usr/bin/python3

import sys
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


def platform_detection(install_binaries=True):
    """
    Detect the platform and adapt the binaries location.
    """
    if install_binaries is True:
        if sys.platform == "linux":
            bin_dir = "bins.linux"
        elif sys.platform == "darwin":
            bin_dir = "bins.osx"
        else:
            return None
    else:
        return None

    return {bin_dir: ["*"]}


DATA_FILES = platform_detection()

print(DATA_FILES)

setup(
    name="structure_threader",
    version="0.1.7",
    packages=["structure_threader",
              "structure_threader.evanno",
              "structure_threader.plotter",
              "structure_threader.sanity_checks"],
    install_requires=[
        "matplotlib",
        "numpy",
    ],
    description=("A program to parallelize runs of 'Structure' and "
                 "'fastStructure'."),
    url="https://github.com/StuntsPT/Structure_threader",
    author="Francisco Pina-Martins",
    author_email="f.pinamartins@gmail.com",
    license="GPL3",
    classifiers=["Intended Audience :: Science/Research",
                 "License :: OSI Approved :: GNU General Public License v3 ("
                 "GPLv3)",
                 "Natural Language :: English",
                 "Operating System:: POSIX:: Linux",
                 "Topic :: Scientific/Engineering :: Bio-Informatics"],
    package_data=DATA_FILES,
    entry_points={
        "console_scripts": [
            "structure_threader = structure_threader.structure_threader:main",
        ]
    },
)

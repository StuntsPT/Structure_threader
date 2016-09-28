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
            bin_dir = "structure_threader/bins/linux"
        elif sys.platform == "darwin":
            bin_dir = "structure_threader/bins/osx"
        else:
            return None
    else:
        return None

    structure_bin = bin_dir + "/structure"
    faststructure_bin = bin_dir + "/fastStructure"

    return [('bin', [faststructure_bin, structure_bin])]


# Set some variables (PKGBUILD inspired)
DATA_FILES = platform_detection()
VERSION = "0.1.8"
URL = "https://github.com/StuntsPT/Structure_threader"


setup(
    name="structure_threader",
    version=VERSION,
    packages=["structure_threader",
              "structure_threader.evanno",
              "structure_threader.plotter",
              "structure_threader.sanity_checks"],
    install_requires=["matplotlib",
                      "numpy",],
    description=("A program to parallelize runs of 'Structure' and "
                 "'fastStructure'."),
    url=URL,
    download_url="{0}/archive/v{1}.tar.gz".format(URL, VERSION),
    author="Francisco Pina-Martins",
    author_email="f.pinamartins@gmail.com",
    license="GPL3",
    classifiers=["Intended Audience :: Science/Research",
                 "License :: OSI Approved :: GNU General Public License v3 ("
                 "GPLv3)",
                 "Natural Language :: English",
                 "Operating System :: POSIX :: Linux",
                 "Topic :: Scientific/Engineering :: Bio-Informatics"],
    data_files=DATA_FILES,
    entry_points={
        "console_scripts": [
            "structure_threader = structure_threader.structure_threader:main",
        ]
    },
)

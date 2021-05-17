#!/usr/bin/python3

# Copyright 2016-2021 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of structure_threader.
# structure_threader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# structure_threader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with structure_threader. If not, see <http://www.gnu.org/licenses/>.


import sys
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


class NotSupportedException(BaseException):
    pass


if sys.version_info.major < 3:
    raise NotSupportedException("Only Python 3.x Supported")


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
    maverick_bin = bin_dir + "/MavericK"

    return [('bin', [faststructure_bin, structure_bin, maverick_bin])]


# Set some variables (PKGBUILD inspired)
DATA_FILES = platform_detection()
try:
    DATA_FILES[0][1].append("structure_threader/wrappers/alstructure_wrapper.R")
except TypeError:
    DATA_FILES = [('bin',
                   ["structure_threader/wrappers/alstructure_wrapper.R"])]
VERSION = "1.3.8"
URL = "https://gitlab.com/StuntsPT/Structure_threader"


setup(
    name="structure_threader",
    version=VERSION,
    packages=["structure_threader",
              "structure_threader.evanno",
              "structure_threader.plotter",
              "structure_threader.sanity_checks",
              "structure_threader.colorer",
              "structure_threader.wrappers",
              "structure_threader.skeletons"],
    install_requires=["plotly>=4.1.1",
                      "colorlover",
                      "numpy>=1.12.1",
                      "matplotlib"],
    description=("A program to parallelize runs of 'Structure', "
                 "'fastStructure' and 'MavericK'."),
    url=URL,
    download_url="{0}/-/archive/{1}/Structure_threader-{1}.tar.gz".format(URL, VERSION),
    author="Francisco Pina-Martins",
    author_email="f.pinamartins@gmail.com",
    license="GPL3",
    classifiers=["Intended Audience :: Science/Research",
                 "License :: OSI Approved :: GNU General Public License v3 ("
                 "GPLv3)",
                 "Natural Language :: English",
                 "Operating System :: POSIX :: Linux",
                 "Topic :: Scientific/Engineering :: Bio-Informatics",
                 "Programming Language :: Python :: 3 :: Only",
                 "Programming Language :: Python :: 3.4",
                 "Programming Language :: Python :: 3.5",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7"],
    data_files=DATA_FILES,
    entry_points={
        "console_scripts": [
            "structure_threader = structure_threader.structure_threader:main",
        ]
    },
)

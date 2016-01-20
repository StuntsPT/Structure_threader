#!/bin/bash

# Copyright 2015 Francisco Pina Martins <f.pinamartins@gmail.com>
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

set -e

# Define and create installation location:
install_dir=~/Software/structure
mkdir -p ${install_dir}

# Define temp dir
tempdir=/tmp/$USER

# Download structure sources into temp dir
wget http://pritchardlab.stanford.edu/structure_software/release_versions/v2.3.4/structure_kernel_source.tar.gz -O ${tempdir}/structure_kernel_source.tar.gz

# Extract tarball, enter src dir, build binary and place it in the install dir
cd ${tempdir}
tar xvfz structure_kernel_source.tar.gz
cd  structure_kernel_src/
make
mv structure ${install_dir}

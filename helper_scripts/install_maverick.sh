#!/bin/bash

# Copyright 2017 Francisco Pina Martins <f.pinamartins@gmail.com>
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

# Define MavericK version and package name:
_version=1.0.4
_name=MavericK

# Define and create installation location:
install_dir=~/Software/${_name}
mkdir -p ${install_dir}

# Define temp dir
tempdir=/tmp/$USER
mkdir -p $tempdir

# Download structure sources into temp dir
wget https://github.com/bobverity/${_name}/archive/v${_version}.tar.gz -O ${tempdir}/${_name}.tar.gz

# Extract tarball, enter src dir, build binary and place it in the install dir
cd ${tempdir}
tar xvfz ${_name}.tar.gz
cd  ${_name}-${_version}/
make
mv ${_name} ${install_dir}

echo ""
echo "Install succesfull. MavericK is now ready to use."
echo ""

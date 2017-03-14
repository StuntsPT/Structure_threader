#!/bin/bash

# Copyright 2016 Francisco Pina Martins <f.pinamartins@gmail.com>
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

LightGreen='\033[1;32m'
NoColor='\033[0m'

echo "Runnig fastStructure 'field test'. This will simulate a full wrapped run on small test data."

git_dir=`pwd`
str_bin=`which fastStructure`

tar xvfJ ${git_dir}/tests/smalldata/BigTestData.str.tar.xz -C ${git_dir}/tests/smalldata/
~/virtualenv/python3.5/bin/structure_threader run -i ${git_dir}/tests/smalldata/BigTestData.str -o ~/results_fs -fs ${str_bin} -K 4 -t 4 --ind ${git_dir}/tests/smalldata/indfile.txt

echo -e "${LightGreen}fastStructure 'Field test' ran successfully. Yay!${NoColor}"

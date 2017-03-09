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

# set -e

LightGreen='\033[1;32m'
NoColor='\033[0m'

echo "Runnig MavericK 'field test'. This will simulate a full wrapped run on small test data."

git_dir=`pwd`
maverick_bin=`which MavericK`

~/virtualenv/python3.5/bin/structure_threader -i ${git_dir}/tests/smalldata/Reduced_dataset.structure -o ~/results -mv ${maverick_bin} -K 3 -t 4 --no-plots 1 --params ${git_dir}/tests/smalldata/parameters.txt

cat /home/travis/results/K1_rep1.stlog

echo -e "${LightGreen}MavericK 'Field test' ran successfully. Yay!${NoColor}"

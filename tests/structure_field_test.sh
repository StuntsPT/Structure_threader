#!/bin/bash

# Copyright 2016-2022 Francisco Pina Martins <f.pinamartins@gmail.com>
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

echo "Runnig STRUCTURE 'field test'. This will simulate a full wrapped run on small test data."

git_dir=$(pwd)
str_bin=$(which structure)
structure_threader_exec=$(which structure_threader)

${structure_threader_exec} run -i "${git_dir}/tests/data/Reduced_dataset.structure" -o ~/results_st -st "${str_bin}" -K 3 -t 4 -R 5 --params "${git_dir}/tests/data/mainparams"

echo -e "${LightGreen}STRUCTURE 'Field test' ran successfully. Yay!${NoColor}"

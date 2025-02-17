#!/bin/bash

# Copyright 2019-2020 Francisco Pina Martins <f.pinamartins@gmail.com>
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

echo "Runnig ALStructure 'field test'. This will simulate a full wrapped run on small test data."

git_dir=$(pwd)
str_bin=$(which alstructure_wrapper.R)
structure_threader_exec=$(which structure_threader)

tar xvfJ "${git_dir}/tests/smalldata/BigTestData.bed.tar.xz" -C "${git_dir}/tests/smalldata/"
${structure_threader_exec} run -i "${git_dir}/tests/smalldata/BigTestData.bed" -o ~/results_als -als "${str_bin}" -K 4 -t 4 --ind "${git_dir}/tests/smalldata/indfile.txt"

echo -e "${LightGreen}ALStructure 'Field test' ran successfully on the \`.bed\` file. Yay!${NoColor}"

tar xvfJ "${git_dir}/tests/smalldata/BigTestData.vcf.tar.xz" -C "${git_dir}/tests/smalldata/"
${structure_threader_exec} run -i "${git_dir}/tests/smalldata/BigTestData.vcf" -o ~/results_als -als "${str_bin}" -K 4 -t 4 --ind "${git_dir}/tests/smalldata/indfile.txt"

echo -e "${LightGreen}ALStructure 'Field test' ran successfully on the \`.vcf\` file. Yay!${NoColor}"

${structure_threader_exec} run -i "${git_dir}/tests/smalldata/BigTestData.vcf.gz" -o ~/results_als -als "${str_bin}" -K 4 -t 4 --ind "${git_dir}/tests/smalldata/indfile.txt"

echo -e "${LightGreen}ALStructure 'Field test' ran successfully on the \`.vcf.gz\` file. Yay!${NoColor}"

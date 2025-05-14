#!/bin/bash

# Copyright 2025 Francisco Pina Martins <f.pinamartins@gmail.com>
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

echo "Runnig Neural ADMIXTURE 'field test'. This will simulate a full wrapped run on small test data."

git_dir=$(pwd)
str_bin=$(which neural-admixture)
structure_threader_exec=$(which structure_threader)

tar xvfJ "${git_dir}/tests/data/BigTestData.bed.tar.xz" -C "${git_dir}/tests/data/"
${structure_threader_exec} run -i "${git_dir}/tests/data/BigTestData.bed" -o ~/results_nad -nad "${str_bin}" -K 4 --exec_mode train --nad_seed 42 -t 1 --ind "${git_dir}/tests/data/indfile.txt"

echo -e "${LightGreen}Neural ADMIXTURE Train 'Field test' ran successfully on the \`.bed\` file. Yay!${NoColor}"

tar xvfJ "${git_dir}/tests/data/BigTestData.pgen.tar.xz" -C "${git_dir}/tests/data/"
${structure_threader_exec} run -i "${git_dir}/tests/data/BigTestData.pgen" -o ~/results_nad -nad "${str_bin}" -K 4 --exec_mode train --nad_seed 42 -t 1 --ind "${git_dir}/tests/data/indfile.txt"

echo -e "${LightGreen}Neural ADMIXTURE Train 'Field test' ran successfully on the \`.pgen\` file. Yay!${NoColor}"

${structure_threader_exec} run -i "${git_dir}/tests/data/BigTestData.bed" -o ~/results_nad -nad "${str_bin}" -K 4 --exec_mode train --supervised True --nad_seed 42 -t 1 --nad_pop "${git_dir}/tests/data/popfile.txt"

echo -e "${LightGreen}Neural ADMIXTURE Supervised Train 'Field test' ran successfully on the \`.bed\` file. Yay!${NoColor}"
#tar xvfJ "${git_dir}/tests/data/BigTestData.vcf.tar.xz" -C "${git_dir}/tests/data/"
#neural-admixture infer --name nad_K4 --data_path /analysis/Structure_threader/tests/data/BigTestData.vcf --out_name K4 --save_dir /analysis/results_nad/nad_K4/ --seed 42
#${structure_threader_exec} run -i "${git_dir}/tests/data/BigTestData.vcf" -o ~/results_nad -nad "${str_bin}" -K 4 --exec_mode infer -t 1 --ind "${git_dir}/tests/data/indfile.txt"

#echo -e "${LightGreen}Neural ADMIXTURE Infer 'Field test' ran successfully. Yay!${NoColor}"

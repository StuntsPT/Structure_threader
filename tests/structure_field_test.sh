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

echo "Runnig STRUCTURE 'field test'. This will simulate a full wrapped run on small test data."

git_dir=`pwd`

~/virtualenv/python3.5/bin/structure_threader -i ${git_dir}/PTS/data/Reduced_dataset.structure -o ~/results -st structure -K 2 -t 2 -R 8

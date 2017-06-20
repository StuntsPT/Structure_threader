#!/usr/bin/python3

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

import os


def str_cli_generator(arg, k_val, rep_num):
    """
    Generates and returns command line for running STRUCTURE.
    """
    output_file = os.path.join(arg.outpath, "str_K" + str(k_val) + "_rep" +
                               str(rep_num))
    cli = [arg.external_prog, "-K", str(k_val), "-i", arg.infile, "-o",
           output_file]
    if arg.params is not None:
        cli += arg.params

    return cli, output_file

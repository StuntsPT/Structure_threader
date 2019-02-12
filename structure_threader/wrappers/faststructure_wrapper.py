#!/usr/bin/python3

# Copyright 2018 Francisco Pina Martins <f.pinamartins@gmail.com>
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


def fs_cli_generator(k_val, arg):
    """
    Generates and returns command line for running fastStructure.
    """
    output_file = os.path.join(arg.outpath, "fS_run_K")
    if arg.infile.endswith((".bed", ".fam", ".bim")):
        file_format = "bed"
        infile = arg.infile[:-4]
    else:
        file_format = "str"  # Assume 'STR' format if plink is not specified
        if arg.infile.endswith(".str") is False:  # Do we need a symlink?
            infile = arg.infile
            try:
                os.symlink(os.path.basename(arg.infile), arg.infile+".str")
            except OSError as err:
                if err.errno != 17:
                    raise
        else:
            infile = arg.infile[:-4]

    cli = ["python2", arg.external_prog, "-K", str(k_val), "--input",
           infile, "--output", output_file, "--format", file_format,
           "--seed", str(arg.seed)] + arg.extra_options.split()

    # Are we using the python script or a binary?
    if arg.external_prog.endswith(".py") is False:
        cli = cli[1:]

    return cli, output_file

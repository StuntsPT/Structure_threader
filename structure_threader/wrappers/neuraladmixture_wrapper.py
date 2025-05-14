#!/usr/bin/python3

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

import os
import logging
import itertools
import random
import gzip


try:
    import colorer.colorer as colorer
    from .alstructure_wrapper import vcfgz_to_vcf
except ImportError:
    import structure_threader.colorer.colorer as colorer
    from structure_threader.wrappers.alstructure_wrapper import vcfgz_to_vcf


def nad_cli_generator(arg, k_val, seed=42):
    """
    Generates and returns command line for running Neural ADMIXTURE.
    """
    run_name = "nad_K" + str(k_val)
    output_dir = os.path.join(arg.outpath, run_name) + os.path.sep

    if arg.infile.endswith(".vcf.gz"):
        arg.infile = vcfgz_to_vcf(arg.infile)

    if arg.exec_mode == "train":
        cli = [arg.external_prog, arg.exec_mode, "--name", run_name, "--k", str(k_val), "--data_path",
               arg.infile, "--save_dir", output_dir, "--seed", str(seed)]
    else:
        cli = [arg.external_prog, arg.exec_mode, "--name", run_name, "--out_name", "nad_infer" + str(k_val),
               "--data_path", arg.infile, "--save_dir", output_dir, "--seed", str(seed)]
    # If no seed is provided, then the default value for Neural ADMIXTURE is 42. See its documentation for more details.

    if arg.init is not None:
        cli += ["--initialization", arg.init]

    if arg.nad_cpus != 0 or arg.nad_gpus != 0:
        if arg.nad_cpus != 0:
            cli += ["--num_cpus", arg.nad_cpus]
        if arg.nad_gpus != 0:
            cli += ["--num_gpus", arg.nad_gpus]

    if arg.exec_mode == "train" and arg.supervised == True and arg.nad_popfile != None:
        pop_list = list()
        pop_count = list()
        with open(arg.nad_popfile, "r") as f:
            for line in f:
                line = line.strip().upper()
                pop_list.append(line)

        for pop in pop_list:
            if not pop in pop_count:
                pop_count.append(pop)

        run_name = "nad_K" + str(len(pop_count)) + "_supervised"
        output_dir = os.path.join(arg.outpath, run_name) + os.path.sep

        cli[3] = run_name
        cli[5] = str(len(pop_count))
        cli[9] = output_dir
        cli += ["--supervised", "--populations_path", arg.nad_popfile]
    elif arg.nad_popfile == None and arg.supervised == True:
        raise IndexError("When running supervised mode with Neural ADMIXTURE, you must include a population file!")

    return cli, run_name, output_dir

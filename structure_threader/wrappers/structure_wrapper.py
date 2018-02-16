#!/usr/bin/python3

# Copyright 2017-2018 Francisco Pina Martins <f.pinamartins@gmail.com>
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


try:
    import colorer.colorer as colorer
except ImportError:
    import structure_threader.colorer.colorer as colorer


def str_cli_generator(arg, k_val, rep_num, seed):
    """
    Generates and returns command line for running STRUCTURE.
    """
    output_file = os.path.join(arg.outpath, "str_K" + str(k_val) + "_rep" +
                               str(rep_num))
    cli = [arg.external_prog, "-K", str(k_val), "-i", arg.infile, "-o",
           output_file]

    if seed is not None:
        cli += ["-D", seed]

    if arg.params is not None:
        cli += arg.params

    return cli, output_file


def str_param_checker(arg):
    """
    Handles the parameter files for STRUCTURE (or lack thereoff)
    """
    os.chdir(os.path.dirname(arg.infile))
    if arg.params is not None:
        mainparams = arg.params
        extraparams = os.path.join(os.path.dirname(arg.params),
                                   "extraparams")
        if os.path.isfile(extraparams) is False:
            logging.warning("No 'extraparams' file was found. An empty one "
                            "was created, but it is highly recommended "
                            "that you fill one out.")
            touch = open(extraparams, 'w')
            touch.close()
        arg.params = ["-m", mainparams, "-e", extraparams]


def seed_generator(extra_options, k_list, replicates):
    """
    Uses a user input seed value to generate *N* seeds, one for each run.
    Takes a seed value and the number of iterations as input and returns a
    job list: [(seed, K, replicate), ...].
    """
    jobs = list(itertools.product(k_list, replicates))[::-1]

    extra_options = extra_options.split()
    if "-D" in extra_options:
        seed = int(extra_options[extra_options.index("-D") + 1])
        random.seed(seed)
        jobs = [(str(random.randrange(10000000)),) + x for x in jobs]

    return jobs

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
import logging
import sys

try:
    import colorer.colorer as colorer
except ImportError:
    import structure_threader.colorer.colorer as colorer


def mav_cli_generator(arg, k_val):
    """
    Generates and returns the command line to run MavericK.
    """
    # MavericK requires a trailing "/" (or "\" if on windows)
    output_dir = os.path.join(arg.outpath, "mav_K" + str(k_val)) + os.path.sep
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    if os.name == "nt":
        root_dir = ""
    else:
        root_dir = "/"
    cli = [arg.external_prog, "-Kmin", str(k_val), "-Kmax", str(k_val), "-data",
           arg.infile, "-outputRoot", output_dir, "-masterRoot",
           root_dir, "-parameters", arg.params]
    if arg.notests is True:
        cli += ["-thermodynamic_on", "f"]
    failsafe = mav_alpha_failsafe(arg.params, arg.Ks)
    for param in failsafe:
        if failsafe[param] is not False:
            cli += ["-" + param, failsafe[param][k_val]]

    return cli, output_dir


def mav_params_parser(parameter_filename):
    """
    Parses MavericK's parameter file and switches some options if necessary.
    """
    param_file = open(parameter_filename, "r")
    use_ti = True
    for lines in param_file:
        if lines.startswith("thermodynamic_on"):
            ti_status = lines.split()[1].lower()
            if ti_status in ("f", "false", "0"):
                use_ti = False
                logging.error("Thermodynamic integration is turned OFF. "
                              "Using STRUCTURE criteria for bestK estimation.")
                break

    param_file.close()

    return use_ti


def mav_alpha_failsafe(parameter_filename, k_list):
    """
    Parses MavericK's parameter file and implements a failsafe for multiple
    alpha values.
    """
    parsed_data = {}
    sorted_data = {"alpha": False, "alphapropsd": False}

    param_file = open(parameter_filename, "r")
    for lines in param_file:
        if lines.lower().startswith("alpha\t"):
            parsed_data["alpha"] = lines.split()[1].split(",")
        elif lines.lower().startswith("alphapropsd\t"):
            parsed_data["alphaPropSD"] = lines.split()[1].split(",")

    param_file.close()

    for param, val in parsed_data.items():
        if len(val) > 1:
            if len(val) != len(k_list):
                logging.fatal("The number of values provided for the %s "
                              "parameter are not the same as the number of "
                              "'Ks' provided. Please correct this.", param)
                sys.exit(0)
            else:
                sorted_data[param] = {}
                for i, j in zip(k_list, val):
                    sorted_data[param][i] = j

    return sorted_data

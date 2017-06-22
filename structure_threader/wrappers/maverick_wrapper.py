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
    failsafe = mav_alpha_failsafe(arg.params, arg.k_list)
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
    Returns the following dict:
    {paramter: {k:param_value}, parameter: {k: param_value}}
    If the paramterer values are a single value, False is returned:
    {paramter: False, parameter: {k: paran_value}}
    """
    parsed_data = {}
    sorted_data = {"alpha": False, "alphaPropSD": False}

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


def maverick_merger(outdir, k_list, params, no_tests):
    """
    Grabs the split outputs from MavericK and merges them in a single directory.
    """
    files_list = ["outputEvidence.csv", "outputEvidenceDetails.csv"]
    mrg_res_dir = os.path.join(outdir, "merged")
    os.makedirs(mrg_res_dir, exist_ok=True)
    log_evidence_mv = {}

    def _mav_output_parser(filename, get_header):
        """
        Parse MavericK output files that need to be merged for TI calculations.
        Returns the contents of the parsed files as a single string, with or
        without a header.
        """
        infile = open(filename, 'r')
        header = infile.readline()
        data = "".join(infile.readlines())
        infile.close()
        if get_header is True:
            data = header + data

        return data

    def _ti_test(outdir, log_evidence_mv):
        """
        Write a bestK result based in TI results.
        """
        bestk_dir = os.path.join(outdir, "bestK")
        os.makedirs(bestk_dir, exist_ok=True)
        bestk = max(log_evidence_mv, key=log_evidence_mv.get).replace("K", "1")
        bestk_file = open(os.path.join(bestk_dir, "TI_integration.txt"), "w")
        output_text = ("MavericK's estimation test revealed "
                       "that the best value of 'K' is: {}\n".format(bestk))
        bestk_file.write(output_text)
        bestk_file.close()
        return [int(bestk)]

    for filename in files_list:
        header = True
        if mav_params_parser(params) is True:
            column_num = -2
        else:
            column_num = -4
        outfile = open(os.path.join(mrg_res_dir, filename), "w")
        for i in k_list:
            data_dir = os.path.join(outdir, "mav_K" + str(i))
            data = _mav_output_parser(os.path.join(data_dir, filename), header)
            header = False
            if filename == "outputEvidence.csv":
                log_evidence_mv[data.split(",")[0]] = float(
                    data.split(",")[column_num])
            outfile.write(data)

        outfile.close()

    if no_tests is False:
        bestk = _ti_test(outdir, log_evidence_mv)
        return bestk


def maverick_normalization(x_mean, x_sd, draws=1e6):
    """
    Performs TI normalization as in the origina implementation from MavericK.
    This is essentially a port from the C++ code written by Bob Verity.
    """
    from math import exp
    from numpy.random import normal as rnorm
    from numpy import array

    # subtract maximum value from x_mean (this has no effect on final outcome
    # but prevents under/overflow)
    new_mean = [x - max(x_mean) for x in x_mean]

    # draw random values of Z (exponentiated and normalised draws)
    x_list = []
    y_list = []
    z_array = array()

    for i in draws:
        y_sum = 0
        for j, k in zip(new_mean, x_sd):
            normalized = rnorm(j, k)
            x_list.append(normalized)
            exponentiated = exp(normalized)
            y_list.append(exponentiated)
            y_sum += exponentiated

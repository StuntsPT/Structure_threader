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

import logging
import sys
import os

from itertools import chain
import numpy as np

from numpy.random import normal as rnorm

try:
    import colorer.colorer as colorer
    from plotter.structplot import plot_normalization
except ImportError:
    import structure_threader.colorer.colorer as colorer
    from structure_threader.plotter.structplot import plot_normalization


def mav_cli_generator(arg, k_val, mav_params):
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
    failsafe = mav_alpha_failsafe(mav_params, arg.k_list)
    for param in failsafe:
        if failsafe[param] is not False:
            cli += ["-" + param, failsafe[param][k_val]]

    return cli, output_dir


def mav_ti_in_use(parameters):
    """
    Checks if TI is in use. Returns True or Flase.
    """
    ti_param = "thermodynamic_on"

    use_ti = True
    try:
        if parameters[ti_param].lower() in ("f", "false", "0"):
            use_ti = False
            logging.info("Thermodynamic integration is turned OFF. "
                         "Using STRUCTURE criteria for bestK estimation.")
    except KeyError:
        logging.error("The parameter setting Thermodynamic integration was not "
                      "found. Assuming the default 'on' value.")

    return use_ti


def mav_params_parser(parameter_filename):
    """
    Parses MavericK's parameter file and returns the results in a dict with
    the following structure:
    {parsed_parameter: param_value, parsed_parameter: param_value ...}
    """
    param_file = open(parameter_filename, "r")
    parameters = {}

    for lines in param_file:
        if not lines.startswith(("#", "\n")):
            lines = lines.split()
            parameters[lines[0]] = "".join(lines[1:])

    param_file.close()

    return parameters


def mav_alpha_failsafe(mav_params, k_list):
    """
    Implements a failsafe for discrepancies with multiple alpha values.
    Returns the following dict:
    {parameter: {k:param_value}, parameter: {k: param_value}}
    If the paramterer values are a single value, False is returned:
    {paramter: False, parameter: {k: param_value}}
    """
    parameters = ("alpha", "alphaPropSD")

    parsed_data = {x: mav_params[x] if x in mav_params else False for x in
                   parameters}
    sorted_data = {x: False for x in parameters}

    for param, val in parsed_data.items():
        if val:
            val = val.split(",")
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


def ti_test(outdir, norm_evidence, ti_in_use):
    """
    Write a bestK result based on TI or STRUCTURE results.
    """
    if ti_in_use:
        # Use TI for bestK estimation
        criteria = norm_evidence[2]
        estimator = "TI"
    else:
        # Use Structure for bestK estimation
        criteria = norm_evidence[1]
        estimator = "STRUCTURE"
    means = {x: y["norm_mean"] for x, y in criteria.items()}

    bestk_dir = os.path.join(outdir, "bestK")
    os.makedirs(bestk_dir, exist_ok=True)
    bestk = max(means, key=means.get)
    bestk_file = open(os.path.join(bestk_dir, "TI_integration.txt"), "w")
    output_text = ("MavericK's estimation test ({}) revealed that the best "
                   "value of 'K' is {}.\nIt is still recommended that you look "
                   "at the generated plot for more accurate "
                   "information.\n".format(estimator, bestk))
    bestk_file.write(output_text)
    bestk_file.close()

    plot_normalization(criteria, outdir)

    return [int(bestk)]


def maverick_merger(outdir, k_list, mav_params, no_tests):
    """
    Grabs the split outputs from MavericK and merges them in a single directory.
    Also uses the data from these files to generate an
    "outputEvidenceNormalized.csv" file.
    """

    def _mav_output_parser(filename):
        """
        Parse MavericK output files that need to be merged for TI calculations.
        Returns the contents of the parsed files as a single string, with or
        without a header.
        """
        infile = open(filename, 'r')
        header = infile.readline()
        data = "".join(infile.readlines())
        infile.close()

        data = header + data

        return data

    def _gen_files_list(output_params, no_tests):
        """
        Defines the output filenames to read based on data from the parameter
        file. Returns a list.
        """
        files_list = []

        parsed_params = {x: mav_params[x] if x in mav_params else False for x in
                         output_params}

        # Generate a list with the files to parse and merge

        if parsed_params["outputEvidence_on"].lower() in ("f", "false", "0"):
            no_tests = True
            logging.error("'outputEvidence' is set to false. Tests will be "
                          "skipped.")
        if parsed_params["outputEvidence"]:
            files_list.append(parsed_params["outputEvidence"])
        else:
            files_list.append("outputEvidence.csv")

        if parsed_params["outputEvidenceDetails"]:
            evidence_filename = parsed_params["outputEvidenceDetails"]
        else:
            evidence_filename = "outputEvidenceDetails.csv"

        if parsed_params["outputEvidenceDetails_on"].lower() in ("f",
                                                                 "false",
                                                                 "0"):
            pass
        else:
            files_list.append(evidence_filename)

        return files_list, no_tests

    def _write_normalized_output(evidence, k_list, ti_in_use):
        """
        Writes the normalized output file.
        """
        param_entry = "outputEvidenceNormalised"

        if param_entry in mav_params:
            filename = mav_params["outputEvidenceNormalised"]
        else:
            filename = "outputEvidenceNormalised.csv"
        filepath = os.path.join(mrg_res_dir, filename)

        categories = ["harmonic_grand", "structure_grand"]
        if ti_in_use:
            categories += ["TI"]

        indep = [["logEvidence_" + x + "Mean" if x != "TI" else "logEvidence_"
                  + x,
                  "logEvidence_" + x + "SE" if x != "TI" else "logEvidence_"
                  + x + "_SE"] for x in categories]

        p_format = "posterior_{}{}"

        posterior = [[[p_format.format(x.replace("_grand", ""), i)]
                      for i in ["_mean", "_LL", "_UL"]]
                     for x in categories]
        flat_posterior = list(chain(*list(chain(*posterior))))

        normalized = []
        normalization = True
        for cat in indep:
            for i in cat:
                evidence[i] = [float(x) if x != "NA"
                               else x for x in evidence[i]]
                if "NA" in evidence[i]:
                    logging.error("Some 'NA' values found in outputEvidence.csv"
                                  ". Normalization can not proceed."
                                  "(Are you using a single "
                                  "'MainRepeats' parameter?).")
                    normalization = False
            if normalization:
                normalized.append(maverick_normalization(evidence[cat[0]],
                                                         evidence[cat[1]],
                                                         k_list))

        dtypes = ("norm_mean", "lower_limit", "upper_limit")

        outfile = open(filepath, 'w')

        outfile.write(",".join(["K", "posterior_exhaustive"] + flat_posterior))
        outfile.write("\n")
        for k in k_list:
            line = str(k) + ",N/A"
            for i in normalized:
                line += "," + ",".join([str(i[k][x]) for x in dtypes])

            outfile.write(line)
            outfile.write("\n")

        if no_tests is False and normalization is True:
            bestk = ti_test(outdir, normalized, ti_in_use)
            return bestk

    output_params = ("outputEvidence", "outputEvidence_on",
                     "outputEvidenceDetails_on", "outputEvidenceDetails")

    files_list, no_tests = _gen_files_list(output_params, no_tests)
    ti_in_use = mav_ti_in_use(mav_params)

    # Handle a new directory for merged data
    mrg_res_dir = os.path.join(outdir, "merged")
    os.makedirs(mrg_res_dir, exist_ok=True)

    for filename in files_list:
        outfile = open(os.path.join(mrg_res_dir, filename), "w")
        first_k = True
        if filename == files_list[0]:
            evidence = {}
        else:
            evidence = None
        for i in k_list:
            data_dir = os.path.join(outdir, "mav_K" + str(i))
            data = _mav_output_parser(os.path.join(data_dir, filename))
            diff = data.split("\n")
            if evidence == {}:
                evidence = {head: [val] for head, val in
                            zip(diff[0].split(","), diff[1].split(","))}
            elif evidence is not None:
                for j, k in zip(diff[0].split(","), diff[1].split(",")):
                    evidence[j].append(k)
            if first_k:
                outfile.write(data)
                first_k = False
            else:
                outfile.write(diff[1])
                outfile.write("\n")
        if evidence is not None:
            bestk = _write_normalized_output(evidence, k_list, ti_in_use)
        outfile.close()

    return bestk


def maverick_normalization(x_mean, x_sd, klist, draws=int(1e6), limit=95):
    """
    Performs TI normalization as in the original implementation from MavericK.
    This is essentially a port from the C++ code written by Bob Verity.
    """
    # subtract maximum value from x_mean (this has no effect on final outcome
    # but prevents under/overflow)
    # Just like in the original implementation
    x_mean = [x - max(x_mean) for x in x_mean]

    z_array = np.zeros([len(x_mean), draws], dtype=np.longdouble)

    # draw random values of Z, exponentiate, and sort them in a bidimensional
    # array
    for i in range(z_array.shape[0]):
        y_array = np.array([np.exp(rnorm(x_mean[i], x_sd[i]),
                                   dtype=np.longdouble)
                            for _ in range(draws)])

        z_array[i] = y_array

    sum_ar = sum(z_array)

    for i in range(draws):

        z_array[:, i] = z_array[:, i] / sum_ar[i]

    # Define limit tails
    l_limit = (100 - limit) / 2
    u_limit = 100 - l_limit

    # Gather mean and CI values and return them as a single dict.
    norm_res = dict(
        (k, {"norm_mean": np.mean(z_array[i]),
             "lower_limit": np.percentile(z_array[i], l_limit),
             "upper_limit": np.percentile(z_array[i], u_limit)})
        for i, k in enumerate(klist))

    return norm_res

#!/usr/bin/python3

# Copyright 2015-2021 Francisco Pina Martins <f.pinamartins@gmail.com>
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
import sys
import signal
import subprocess
import itertools
import shutil
import logging
import pandas as pd

from multiprocessing import Pool
from random import choice
from functools import partial
from clumppling.__main__ import main as clumppling_main

try:
    import plotter.structplot as sp
    import sanity_checks.sanity as sanity
    import colorer.colorer as colorer
    import wrappers.maverick_wrapper as mw
    import wrappers.faststructure_wrapper as fsw
    import wrappers.structure_wrapper as sw
    import wrappers.alstructure_wrapper as alsw
    import wrappers.neuraladmixture_wrapper as nadw
    import argparser

except ImportError:
    import structure_threader.plotter.structplot as sp
    import structure_threader.sanity_checks.sanity as sanity
    import structure_threader.colorer.colorer as colorer
    import structure_threader.wrappers.maverick_wrapper as mw
    import structure_threader.wrappers.faststructure_wrapper as fsw
    import structure_threader.wrappers.structure_wrapper as sw
    import structure_threader.wrappers.alstructure_wrapper as alsw
    import structure_threader.wrappers.neuraladmixture_wrapper as nadw
    import structure_threader.argparser as argparser

# Where are we?
CWD = os.getcwd()

# Set default log level and format
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


def gracious_exit(*args):
    """
    Graciously exit the program.
    """
    logging.critical("\rExiting graciously, murdering child processes and "
                     "cleaning output directory.")
    os.chdir(CWD)
    sys.exit(0)


def runprogram(wrapped_prog, iterations, arg):
    """
    Run each wrapped program job. Return the worker status.
    This attribute will be populated with the worker exit code and output file
    and returned. The first element is the exit code itself (0 if normal exit
    and -1 in case of errors). The second element contains the output file
    that identifies the worker.
    """
    worker_status = (None, None)

    try:
        seed, k_val, rep_num = iterations
    except ValueError:
        k_val, rep_num = iterations
        seed = None

    if wrapped_prog == "structure":  # Run STRUCTURE
        cli, output_file = sw.str_cli_generator(arg, k_val, rep_num, seed)

    elif wrapped_prog == "maverick":  # Run MavericK
        mav_params = mw.mav_params_parser(arg.params)
        cli, output_dir = mw.mav_cli_generator(arg, k_val, mav_params)

    elif wrapped_prog == "alstructure":  # Run ALStructure
        cli, output_file = alsw.alstr_cli_generator(arg, k_val)

    elif wrapped_prog == "neuraladmixture": # Run Neural ADMIXTURE
        cli, run_name, output_file = nadw.nad_cli_generator(arg, k_val, arg.nad_seed)

    else:  # Run fastStructure
        cli, output_file = fsw.fs_cli_generator(k_val, arg)

    logging.info("Running: " + " ".join(cli))
    if wrapped_prog == "alstructure":
        logging.info("If this is the first time running ALStructure it might "
                     "take a while to install all the dependencies. Please "
                     "be patient.")
    program = subprocess.Popen(cli,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    out, err = map(lambda x: x.decode("utf-8"), program.communicate())

    # Check for errors in the program's exit code
    if program.returncode != 0:
        arg.log = True
        try:
            worker_status = (-1, output_file)
        except UnboundLocalError:
            worker_status = (-1, output_dir)
    else:
        worker_status = (0, None)

    # Handle logging for debugging purposes.
    if arg.log is True:

        logfile = open(os.path.join(arg.outpath, "K" + str(k_val) + "_rep" +
                                    str(rep_num) + ".stlog"), "w")
        logging.info("Writing logfile for K" + str(k_val) + ", replicate " +
                     str(rep_num) + ". Please wait...")
        logfile.write(out)
        logfile.write(err)
        logfile.close()

    return worker_status


def structure_threader(wrapped_prog, arg):
    """
    Do the threading book-keeping to spawn jobs at the asked rate.
    """

    if wrapped_prog != "neuraladmixture":
        arg.exec_mode = ""
        arg.supervised = None

    if wrapped_prog != "structure":
        arg.replicates = [1]
        if arg.supervised == True:
            jobs = list(itertools.product([1], arg.replicates))[::-1]
            arg.noplot = True
            arg.noclumpp = True
        else:
            jobs = list(itertools.product(arg.k_list, arg.replicates))[::-1]
    else:
        sw.str_param_checker(arg)
        jobs = sw.seed_generator(arg.seed, arg.k_list, arg.replicates)

    # This allows us to pass partial arguments to a function so we can later
    # use it with multiprocessing map().
    temp = partial(runprogram, wrapped_prog, arg=arg)

    # This will automatically create the Pool object, run the jobs and deadlock
    # the function while the children processed are being executed. This will
    # also allow to iterate over the values returned by all workers and to sort
    # them out to see if there were any errors
    pool = Pool(arg.threads).map(temp, jobs)

    # Check for worker status. This will search the worker outputs and if
    # one or more workers had an error exit status, the error_list will be
    # populated with the cli commands that generated the errors
    error_list = [x[1] for x in pool if x[0] == -1]

    logging.info("\n==============================\n")
    if error_list:
        logging.critical("%s %s runs exited with errors. Check the log files of"
                         " the following output files:",
                         len(error_list), wrapped_prog)
        for out in error_list:
            logging.error(out)
    else:
        logging.info("All %s jobs finished successfully.", len(pool))

    os.chdir(CWD)


def structure_harvester(resultsdir, wrapped_prog):
    """
    Run Structure Harvester or fastChooseK to perform the Evanno test or the
    likelihood testing on the results.
    """
    outdir = os.path.join(resultsdir, "bestK")
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if wrapped_prog == "faststructure":
        try:
            import evanno.fastChooseK as sh
        except ImportError:
            import structure_threader.evanno.fastChooseK as sh

        method = "fastChooseK"
    else:
        try:
            import evanno.structureHarvester as sh
        except ImportError:
            import structure_threader.evanno.structureHarvester as sh

        method = "Structure Harvester"

    logging.info(f"Inferring the optimal K value using {method}...")
    # Retrieve list of best K values
    bestk = sh.main(resultsdir, outdir)
    logging.info("Optimal K value estimation complete!")

    return bestk


def create_plts(wrapped_prog, bestk, arg):
    """
    Create plots from result dir.
    :param resultsdir: path to results directory
    """

    outdir = os.path.join(arg.outpath, "plots")
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if wrapped_prog == "structure":
        # Get only relevant output files, choosen randomly from the replictes.
        # Failsafe in case we only have 1 replicate:
        if arg.replicates == 1:
            file_to_plot = "1"
        else:
            file_to_plot = str(choice(arg.replicates))
        plt_files = [os.path.join(arg.outpath, "str_K") + str(i) + "_rep" +
                     file_to_plot + "_f"
                     for i in arg.k_list]
    elif wrapped_prog == "maverick":
        plt_files = [os.path.join(os.path.join(arg.outpath, "mav_K" + str(i)),
                                  "outputQmatrix_ind_K" + str(i) + ".csv")
                     for i in arg.k_list]
    elif wrapped_prog == "alstructure":
        plt_files = [os.path.join(os.path.join(arg.outpath, "alstr_K" + str(i)))
                     for i in arg.k_list]

    elif wrapped_prog == "faststructure":
        plt_files = [os.path.join(arg.outpath, "fS_run_K.") + str(i) + ".meanQ"
                     for i in arg.k_list]
    else:
        if arg.supervised == True:
            pop_list = list()
            pop_count = list()
            with open(arg.nad_popfile, "r") as f:
                for line in f:
                    line = line.strip().upper()
                    pop_list.append(line)

            for pop in pop_list:
                if not pop in pop_count:
                    pop_count.append(pop)

            pop_count_n = len(pop_count)

            plt_files = [os.path.join(os.path.join(arg.outpath, "nad_K" + str(pop_count_n) + "_supervised"),
                                      "nad_K" + str(pop_count_n) + "_supervised." + str(pop_count_n) + ".Q")]
        else:
            plt_files = [os.path.join(os.path.join(arg.outpath, "nad_K" + str(i)),
                                      "nad_K" + str(i) + "." + str(i) + ".Q")
                         for i in arg.k_list]

    logging.info("Creating plots from the results directory...")
    sp.main(plt_files, wrapped_prog, outdir, bestk=bestk, popfile=arg.popfile,
            indfile=arg.indfile, bw=arg.blacknwhite, use_ind=arg.use_ind)
    logging.info("Plots created!")


def plots_only(arg):
    """
    Handles arguments and wraps things up for drawing the plots without
    running any wrapped programs.
    """
    # Relative to abs path
    prefix_abs_path = os.path.abspath(arg.results_path)
    # Get all files matching the provided prefix
    prefix_dir, prefix_name = os.path.split(prefix_abs_path)

    if prefix_dir == "":
        prefix_dir = "."
    k_vals = arg.bestk

    if arg.program == "faststructure":
        infiles = [os.path.join(prefix_abs_path, "fS_run_K." + x + ".meanQ")
                   for x in k_vals]

    elif arg.program == "structure":
        infiles = [os.path.join(prefix_abs_path, "str_K" + x + "_rep1_f")
                   for x in k_vals]

    elif arg.program == "alstructure":
        infiles = [os.path.join(prefix_abs_path, "alstr_K" + x)
                   for x in k_vals]

    else:
        infiles = [os.path.join(os.path.join(prefix_abs_path, "mav_K" + x),
                                "outputQmatrix_ind_K" + x + ".csv")
                   for x in k_vals]

    for filename in infiles:
        sanity.file_checker(filename, "There was a problem with the deduced "
                                      "filename '{}'. Please check "
                                      "it.".format(filename))

    if not infiles:
        logging.error("No input files that match the expected prefix were "
                      "found in the provided path. Aborting.")
        raise SystemExit

    if not os.path.exists(arg.outpath):
        os.makedirs(arg.outpath)

    bestk = [int(x) for x in arg.bestk]

    sp.main(infiles, arg.program, arg.outpath, bestk, popfile=arg.popfile,
            indfile=arg.indfile, filter_k=bestk, bw=arg.blacknwhite,
            use_ind=arg.use_ind)


def clumppling_run(wrapped_prog, arg):
    """
    Handles arrugments and runs an analysis on the output data using Clumppling.
    Assumes wrapped software output folder as input for Clumppling.
    """
    if wrapped_prog == "structure":
        wrapped_prog_f = wrapped_prog
        input_dir = arg.outpath

    elif wrapped_prog == "faststructure":
        wrapped_prog_f = "fastStructure"
        input_dir = arg.outpath

        for file in os.listdir(arg.outpath):
            if file == "fS_run_K.1.meanQ": # placeholder until Clumppling releases version with fix
                full_file_path = os.path.join(arg.outpath, file)
                os.rename(full_file_path, f"{full_file_path}.bak")
                break

    elif wrapped_prog == "maverick":
        wrapped_prog_f = "generalQ"

        out_dir_list = []
        for file in os.listdir(arg.outpath):
            if file.startswith("mav") and not file == "mav_K1":
                out_dir_list.append(file)

        input_dir = arg.outpath + "/clumpp_temp"
        if not os.path.exists(input_dir):
            os.mkdir(input_dir)

        for dir in out_dir_list:
            K = dir[-1:]
            try:
                full_file_path = os.path.join(arg.outpath, dir + f"/outputQmatrix_pop_K{K}.csv")
                Q_df = pd.read_csv(full_file_path)
            except FileNotFoundError:
                full_file_path = os.path.join(arg.outpath, dir + f"/outputQmatrix_ind_K{K}.csv")
                Q_df = pd.read_csv(full_file_path)

            out_file = f"K{K}.Q"
            deme_columns = [col for col in Q_df.columns if "deme" in col]
            df_deme = Q_df[deme_columns]
            new_file_path = os.path.join(input_dir, out_file)

            df_deme.to_csv(new_file_path, index=False, header=False, sep=" ")

    elif wrapped_prog == "alstructure":
        wrapped_prog_f = "generalQ"

        input_dir = arg.outpath + "/clumpp_temp"
        if not os.path.exists(input_dir):
            os.mkdir(input_dir)

        for file in os.listdir(arg.outpath):
            if file.startswith("alstr"):
                K = file[-1:]
                out_file = f"K{K}.Q"

                full_file_path = os.path.join(arg.outpath, file)
                Q_df = pd.read_csv(full_file_path)

                v_columns = [col for col in Q_df.columns if "V" in col]
                df_v = Q_df[v_columns]
                new_file_path = os.path.join(input_dir, out_file)

                df_v.to_csv(new_file_path, index=False, header=False, sep=" ")

    elif wrapped_prog == "neuraladmixture":
        wrapped_prog_f = "admixture"

        out_dir_list = []
        for file in os.listdir(arg.outpath):
            if file.startswith("nad") and not file == "nad_K1":
                out_dir_list.append(file)

        input_dir = arg.outpath + "/clumpp_temp"
        if not os.path.exists(input_dir):
            os.mkdir(input_dir)

        for dir in out_dir_list:
            K = dir[-1:]
            file = dir + f"/nad_K{K}.{K}.Q"
            out_file = f"K{K}.Q"

            full_file_path = os.path.join(arg.outpath, file)
            new_file_path = os.path.join(input_dir, out_file)
            shutil.copy(full_file_path, new_file_path)

    else:
        return

    args_dict = {
        'input_path': input_dir,
        'output_path': f"{arg.outpath}/clumpp",
        'input_format': wrapped_prog_f,
        'vis': 1,  # Default value for visualization
        'cd_param': 1.0,  # Default value for community detection parameter
        'use_rep': 0,  # Default value for using representative replicate
        'merge_cls': 0,  # Default value for merging clusters
        'cd_default': 1,  # Default value for using default community detection method
        'plot_modes': 1,  # Default value for displaying aligned modes
        'plot_modes_withinK': 0,  # Default value for displaying modes for each K
        'plot_major_modes': 0,  # Default value for displaying major modes
        'plot_all_modes': 0,  # Default value for displaying all aligned modes
        'custom_cmap': ''  # Default value for custom colormap
    }

    args = argparser.argparse.Namespace(**args_dict)

    logging.info("Running Clumppling analysis on the results...")
    try:
        clumppling_main(args)

        if wrapped_prog == "faststructure":
            for file in os.listdir(arg.outpath):
                if file == "fS_run_K.1.meanQ.bak":
                    full_file_path = os.path.join(arg.outpath, file)
                    os.rename(full_file_path, full_file_path[:-4])

        elif wrapped_prog == "maverick" or wrapped_prog == "alstructure":
            for file in os.listdir(arg.outpath):
                if file.endswith(".Q"):
                    os.remove(file)

        for file in os.listdir(arg.outpath):
            if file == "clumpp.zip":
                os.remove(os.path.join(arg.outpath, file))
            if file == "clumpp_temp":
                shutil.rmtree(os.path.join(arg.outpath, file))

    except Exception as e:
        print(f"An error occurred during Clumppling analysis: {e}")


def full_run(arg):
    """
    Make a full Structure_threader run, including program wrapping, and
    eventually bestK tests and plotting.
    """
    # Figure out which program we are wrapping
    if "-fs" in sys.argv:
        wrapped_prog = "faststructure"
    elif "-mv" in sys.argv:
        wrapped_prog = "maverick"
    elif "-st" in sys.argv:
        wrapped_prog = "structure"
    elif "-als" in sys.argv:
        wrapped_prog = "alstructure"
        arg.threads = 1  # Depencency handling forces this
        arg.notests = True  # No way to perform K tests with ALS
        arg.k_list = [x for x in arg.k_list if x != 1]  # ALS can't have K=1
    elif "-nad" in sys.argv:
        wrapped_prog = "neuraladmixture"
        arg.threads = 1 # Neural ADMIXTURE already has multithreading
        arg.notests = True

    structure_threader(wrapped_prog, arg)

    if wrapped_prog == "maverick":
        mav_params = mw.mav_params_parser(arg.params)
        bestk = mw.maverick_merger(arg.outpath, arg.k_list, mav_params,
                                   arg.notests)
        arg.notests = True

    if wrapped_prog == "alstructure" or wrapped_prog == "neuraladmixture":
        try:
            infile = arg.infile[:-4]
            if infile.endswith(".vc"):
                raise ValueError

        except ValueError:
            infile = arg.infile[:-7]
            extracted_vcf = arg.infile[:-3]

            if os.path.exists(extracted_vcf):
                os.remove(extracted_vcf)

        if os.path.exists(infile):
            os.remove(infile)

    if arg.notests is False:
        bestk = structure_harvester(arg.outpath, wrapped_prog)
    else:
        logging.info(f"Inferring the optimal K value...")
        bestk = arg.k_list
        logging.info("Optimal K value estimation complete!")

    if arg.noplot is False:
        create_plts(wrapped_prog, bestk, arg)

    if arg.noclumpp is False:
        clumppling_run(wrapped_prog, arg)


def spooky_scary_skeletons(arg):
    """
    Generates skeleton parameter files for STRUCTURE.
    """
    try:
        import structure_threader.skeletons.stparams as parameters
    except ImportError:
        import skeletons.stparams as parameters

    sanity.file_checker(arg.outpath, is_file=False)
    main_file = os.path.join(arg.outpath, "mainparams")
    with open(main_file, 'w') as fhandle:
        fhandle.write(parameters.MAINPARAMS)
    extra_file = os.path.join(arg.outpath, "extraparams")
    with open(extra_file, 'w') as fhandle:
        fhandle.write(parameters.EXTRAPARAMS)


def main():
    """
    Main function, where variables are set and other functions get called
    from.
    """

    # Make sure we exit graciously on Crtl+c
    signal.signal(signal.SIGINT, gracious_exit)

    # Make sure we provide an help message instead of an error
    if len(sys.argv) == 1:
        sys.argv += ["-h"]
    arg = argparser.argument_parser(sys.argv[1:])

    # Perform full structure_threader run
    if arg.main_op == "run":
        full_run(arg)

    # Perform only plotting operation
    if arg.main_op == "plot":
        plots_only(arg)

    # Write skeleton parameter files
    elif arg.main_op == "params":
        spooky_scary_skeletons(arg)


if __name__ == "__main__":
    main()

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
import logging

from multiprocessing import Pool
from random import choice
from functools import partial

try:
    import plotter.structplot as sp
    import sanity_checks.sanity as sanity
    import colorer.colorer as colorer
    import wrappers.maverick_wrapper as mw
    import wrappers.faststructure_wrapper as fsw
    import wrappers.structure_wrapper as sw
    import wrappers.alstructure_wrapper as alsw
    import argparser

except ImportError:
    import structure_threader.plotter.structplot as sp
    import structure_threader.sanity_checks.sanity as sanity
    import structure_threader.colorer.colorer as colorer
    import structure_threader.wrappers.maverick_wrapper as mw
    import structure_threader.wrappers.faststructure_wrapper as fsw
    import structure_threader.wrappers.structure_wrapper as sw
    import structure_threader.wrappers.alstructure_wrapper as alsw
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

    if wrapped_prog != "structure":
        arg.replicates = [1]
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
    Run structureHarvester or fastChooseK to perform the Evanno test or the
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
    else:
        try:
            import evanno.structureHarvester as sh
        except ImportError:
            import structure_threader.evanno.structureHarvester as sh

    # Retrieve list of best K values
    bestk = sh.main(resultsdir, outdir)

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

    else:
        plt_files = [os.path.join(arg.outpath, "fS_run_K.") + str(i) + ".meanQ"
                     for i in arg.k_list]

    sp.main(plt_files, wrapped_prog, outdir, bestk=bestk, popfile=arg.popfile,
            indfile=arg.indfile, bw=arg.blacknwhite, use_ind=arg.use_ind)


def plots_only(arg):
    """
    Handles arrugments and wraps things up for drawing the plots without
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

    structure_threader(wrapped_prog, arg)

    if wrapped_prog == "maverick":
        mav_params = mw.mav_params_parser(arg.params)
        bestk = mw.maverick_merger(arg.outpath, arg.k_list, mav_params,
                                   arg.notests)
        arg.notests = True

    if arg.notests is False:
        bestk = structure_harvester(arg.outpath, wrapped_prog)
    else:
        bestk = arg.k_list

    if arg.noplot is False:
        create_plts(wrapped_prog, bestk, arg)


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

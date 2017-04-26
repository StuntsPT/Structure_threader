#!/usr/bin/python3

# Copyright 2015-2017 Francisco Pina Martins <f.pinamartins@gmail.com>
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
import argparse
import logging

from multiprocessing import Pool
from random import randrange
from functools import partial

try:
    import plotter.structplot as sp
    import sanity_checks.sanity as sanity
    import colorer.colorer as colorer
except ImportError:
    import structure_threader.plotter.structplot as sp
    import structure_threader.sanity_checks.sanity as sanity
    import structure_threader.colorer.colorer as colorer

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

    K, rep_num = iterations

    if wrapped_prog == "structure":  # Run STRUCTURE
        # Keeps correct directory separator across OS's
        output_file = os.path.join(arg.outpath, "str_K" + str(K) + "_rep" +
                                   str(rep_num))
        cli = [arg.external_prog, "-K", str(K), "-i", arg.infile, "-o",
               output_file]
        if arg.params is not None:
            cli += arg.params

    elif wrapped_prog == "maverick":  # Run MavericK
        # MavericK requires a trailing "/" (or "\" if on windows)
        output_dir = os.path.join(arg.outpath, "mav_K" + str(K)) + os.path.sep
        try:
            os.mkdir(output_dir)
        except FileExistsError:
            pass
        cli = [arg.external_prog, "-Kmin", str(K), "-Kmax", str(K), "-data",
               arg.infile, "-outputRoot", output_dir, "-masterRoot", "/",
               "-parameters", arg.params]
        if arg.notests is True:
            cli += ["-thermodynamic_on", "f"]

    else:  # Run fastStructure
        # Keeps correct directory separator across OS's
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

        cli = ["python2", arg.external_prog, "-K", str(K), "--input",
               infile, "--output", output_file, "--format", file_format,
               arg.extra_options]

        # Are we using the python script or a binary?
        if arg.external_prog.endswith(".py") is False:
            cli = cli[1:]

    logging.info("Running: " + " ".join(cli))
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

        logfile = open(os.path.join(arg.outpath, "K" + str(K) + "_rep" +
                                    str(rep_num) + ".stlog"), "w")
        logging.info("Writing logfile for K" + str(K) + ", replicate " +
                     str(rep_num) + ". Please wait...")
        logfile.write(out)
        logfile.write(err)
        logfile.close()

    return worker_status


def structure_threader(Ks, replicates, threads, wrapped_prog, arg):
    """
    Do the threading book-keeping to spawn jobs at the asked rate.
    """

    if wrapped_prog != "structure":
        replicates = [1]
    else:
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

    jobs = list(itertools.product(Ks, replicates))[::-1]

    # This allows us to pass partial arguments to a function so we can later
    # use it with multiprocessing map().
    temp = partial(runprogram, wrapped_prog, arg=arg)

    # This will automatically create the Pool object, run the jobs and deadlock
    # the function while the children processed are being executed. This will
    # also allow to iterate over the values returned by all workers and to sort
    # them out to see if there were any errors
    pool = Pool(threads).map(temp, jobs)

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

    if wrapped_prog == "fastStructure":
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


def create_plts(resultsdir, wrapped_prog, Ks, bestk, arg):
    """
    Create plots from result dir.
    :param resultsdir: path to results directory
    """

    plt_list = [x for x in Ks if x != 1]  # Don't plot K=1

    outdir = os.path.join(resultsdir, "plots")
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if wrapped_prog == "structure":
        # Get only relevant output files, choosen randomly from the replictes.
        # Failsafe in case we only have 1 replicate:
        if arg.replicates == 1:
            file_to_plot = "1"
        else:
            file_to_plot = str(randrange(1, arg.replicates + 1))
        plt_files = [os.path.join(resultsdir, "str_K") + str(i) + "_rep" +
                     file_to_plot + "_f"
                     for i in plt_list]
    elif wrapped_prog == "maverick":
        plt_files = [os.path.join(os.path.join(resultsdir, "mav_K" + str(i)),
                                  "outputQmatrix_ind_K" + str(i) + ".csv")
                     for i in plt_list]

    else:
        plt_files = [os.path.join(resultsdir, "fS_run_K.") + str(i) + ".meanQ"
                     for i in plt_list]

    sp.main(plt_files, wrapped_prog, outdir, bestk=bestk, popfile=arg.popfile,
            indfile=arg.indfile, bw=arg.blacknwhite)


def maverick_merger(outdir, k_list, no_tests):
    """
    Grabs the split outputs from MavericK and merges them in a single directory.
    """
    files_list = ["outputEvidence.csv", "outputEvidenceDetails.csv"]
    mrg_res_dir = os.path.join(outdir, "merged")
    os.makedirs(mrg_res_dir, exist_ok=True)
    log_evidence_ti = {}

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

    def _ti_test(outdir, log_evidence_ti):
        """
        Write a bestK result based in TI results.
        """
        bestk_dir = os.path.join(outdir, "bestK")
        os.makedirs(bestk_dir, exist_ok=True)
        bestk = max(log_evidence_ti, key=log_evidence_ti.get).replace("K", "1")
        bestk_file = open(os.path.join(bestk_dir, "TI_integration.txt"), "w")
        output_text = ("MavericK's 'Thermodynamic Integration' test revealed "
                       "that the best value of 'K' is: {}\n".format(bestk))
        bestk_file.write(output_text)
        bestk_file.close()
        return [int(bestk)]

    for filename in files_list:
        header = True
        outfile = open(os.path.join(mrg_res_dir, filename), "w")
        for i in k_list:
            data_dir = os.path.join(outdir, "mav_K" + str(i))
            data = _mav_output_parser(os.path.join(data_dir, filename), header)
            header = False
            if filename == "outputEvidence.csv":
                log_evidence_ti[data.split(",")[0]] = float(data.split(",")[-2])
            outfile.write(data)

        outfile.close()

    if no_tests is False:
        bestk = _ti_test(outdir, log_evidence_ti)
        return bestk


def argument_parser(args):
    """
    Parses the list of arguments as implemented in argparse.
    """
    parser = argparse.ArgumentParser(
        description="A software wrapper to paralelize genetic clustering "
                    "programs.",
        prog="Structure_threader",
        formatter_class=argparse.RawTextHelpFormatter)

    # Create subparsers for each main structure_threader  operation
    subparsers = parser.add_subparsers(
        help="Select which structure_threader command you wish to"
             "execute.",
        dest="main_op")

    run_parser = subparsers.add_parser("run", help="Performs a complete"
                                       " run of structure_threader.")
    plot_parser = subparsers.add_parser("plot", help="Performs only the"
                                        " plotting operations.")

    # ####################### RUN ARGUMENTS ###################################
    # Group definition
    io_opts = run_parser.add_argument_group("Input/Output options")
    id_opts = run_parser.add_argument_group(
        "Individual/Population identification options")
    main_exec = run_parser.add_argument_group(
        "Program execution options. Mutually exclusive")
    k_opts = run_parser.add_argument_group("Cluster options")
    run_opts = run_parser.add_argument_group("Structure run options")
    plot_opts = run_parser.add_argument_group("Q-matrix plotting options")
    misc_opts = run_parser.add_argument_group("Miscellaneous options")

    # Group options
    main_exec_ex = main_exec.add_mutually_exclusive_group(required=True)
    k_opts = k_opts.add_mutually_exclusive_group(required=True)
    id_opts = id_opts.add_mutually_exclusive_group(required=False)

    main_exec_ex.add_argument("-st", dest="external_prog", type=str,
                              default=None,
                              metavar="filepath",
                              help="Location of the structure executable "
                              "in  your environment.")
    main_exec_ex.add_argument("-fs", dest="external_prog", type=str,
                              default=None,
                              metavar="filepath",
                              help="Location of the fastStructure "
                              "executable in your environment.")
    main_exec_ex.add_argument("-mv", dest="external_prog", type=str,
                              default=None,
                              metavar="filepath",
                              help="Location of the MavericK executable "
                              "in your environment.")

    k_opts.add_argument("-K", dest="Ks", type=int,
                        help="Number of Ks to calculate.\n", metavar="int")
    k_opts.add_argument("-Klist", dest="Ks", nargs="+", type=int,
                        help="List of Ks to calculate.\n",
                        metavar="'2 4 6'")

    run_opts.add_argument("-R", dest="replicates", type=int, required=False,
                          help="Number of replicate runs for each value "
                          "of K (default:%(default)s).\nIgnored for "
                          "fastStructure and MavericK",
                          metavar="int", default=20)

    io_opts.add_argument("-i", dest="infile", type=str, required=True,
                         help="Input file.\n", metavar="infile")
    io_opts.add_argument("-o", dest="outpath", type=str, required=True,
                         help="Directory where the results will be "
                         "stored in.\n",
                         metavar="output_directory")
    io_opts.add_argument("--params", dest="params", type=str, required=False,
                         help="File with run parameters.",
                         metavar="parameters_file.txt", default=None)

    id_opts.add_argument("--pop", dest="popfile", type=str, required=False,
                         help="File with population information.",
                         metavar="popfile", default=None)
    id_opts.add_argument("--ind", dest="indfile", type=str, required=False,
                         help="File with population information.",
                         metavar="indfile", default=None)

    misc_opts.add_argument("-t", dest="threads", type=int, required=True,
                           help="Number of threads to use "
                                "(default:%(default)s).\n",
                           metavar="int", default=4)
    misc_opts.add_argument("--log", dest="log", type=bool, required=False,
                           help="Choose this option if you want to "
                           "enable logging.",
                           metavar="bool", default=False)
    misc_opts.add_argument("--no_tests", dest="notests", type=bool,
                           required=False,
                           help="Disable best K tests. Implies "
                           "--no_plots",
                           metavar="bool", default=False)
    misc_opts.add_argument("--extra_opts", dest="extra_options", type=str,
                           required=False,
                           help="Add extra arguments to pass to the "
                           "wrapped program here.\nExample: "
                           "prior=logistic seed=123",
                           metavar="string", default="")

    plot_opts.add_argument("--no_plots", dest="noplot", type=bool,
                           required=False, help="Disable plot drawing.",
                           metavar="bool", default=False)
    plot_opts.add_argument("--override_bestk", dest="bestk", type=int,
                           required=False, nargs="+",
                           help="Override 'K' values from the given list"
                           " to be ploteted in the combined figure.",
                           metavar="'2 4 5'", default=None)
    plot_opts.add_argument("-bw", dest="blacknwhite",
                            action="store_const", const=True,
                            help="Set this flag to draw greyscale plots"
                                 " instead of colored ones.")

    # ####################### PLOT ARGUMENTS ##################################
    # Group definitions

    main_opts = plot_parser.add_argument_group("Main plotting options")
    extra_opts = plot_parser.add_argument_group("Extra plotting options")
    sort_opts = plot_parser.add_argument_group("Plot sorting options")

    # Group options
    sort_opts_ex = sort_opts.add_mutually_exclusive_group(required=True)

    main_opts.add_argument("-i", dest="prefix", type=str, required=True,
                           help="The prefix of the output meanQ files."
                                "The current directory will be scanned"
                                " and all files that match the prefix.")
    main_opts.add_argument("-f", dest="format", type=str, required=True,
                           choices=["structure", "fastStructure",
                                    "maverick"],
                           help="The format of the result files.")
    main_opts.add_argument("-K", dest="bestk", nargs="+", required=True,
                           help="Choose the K values to plot. Each K"
                                "value provided will be plotted "
                                "individually and a comparative plot"
                                " will all K's will be generated."
                                "Example: -K 2 3 4.")
    main_opts.add_argument("-o", dest="outpath", type=str, default=".",
                           help="The directory where the plots will be"
                                " generated. If it is not provided,"
                                " the current working directory"
                                " will be used.")

    extra_opts.add_argument("-bw", dest="blacknwhite",
                            action="store_const", const=True,
                            help="Set this flag to draw greyscale plots"
                                 " instead of colored ones.")

    sort_opts_ex.add_argument("--pop", dest="popfile", type=str,
                              required=False,
                              help="File with population information.",
                              metavar="popfile", default=None)
    sort_opts_ex.add_argument("--ind", dest="indfile", type=str,
                              required=False,
                              help="File with individual information.",
                              metavar="indfile", default=None)

    # ##################### Sanity checks ################################
    arguments = parser.parse_args(args)

    if arguments.main_op == "run":
        # Handle argparse limitations with "--" options.
        if arguments.extra_options != "":
            arguments.extra_options = "--{0}".format(arguments.extra_options)
            arguments.extra_options = \
                " --".join(arguments.extra_options.split())

        # fastStructure is really only usefull with either a pop or indfile...
        if "-fs" in sys.argv and\
            arguments.popfile is None and\
                arguments.indfile is None:
            parser.error("-fs requires either --pop or --ind.")

        # Make sure we provide paths for mainparam, extraparams and
        # parameters.txt  depending on the wrapped program.
        if arguments.params is not None:
            arguments.params = os.path.abspath(arguments.params)
        if "-mv" in sys.argv and arguments.params is None:
            parser.error("-mv requires --params.")
    else:
        if arguments.format == "faststructure" and arguments.popfile is None\
                and arguments.indfile is None:
            parser.error("fastStructure plots require either --pop or --ind.")

    return arguments


def main():
    """
    Main function, where variables are set and other functions get called
    from.
    """

    # Make sure we provide an help message instead of an error
    if len(sys.argv) == 1:
        sys.argv += ["-h"]
    arg = argument_parser(sys.argv[1:])

    # Check the existance of several files:
    # Popfile
    if arg.popfile is not None:
        sanity.file_checker(arg.popfile,
                            "The specified popfile '{}' does not "
                            "exist.".format(arg.popfile))
    # Indfile
    if arg.indfile is not None:
        sanity.file_checker(arg.indfile,
                            "The specified indfile '{}' does not "
                            "exist.".format(arg.indfile))

    # Perform usual structure_threader run
    if arg.main_op == "run":

        # Switch relative to absolute paths
        arg.infile = os.path.abspath(arg.infile)
        arg.outpath = os.path.abspath(arg.outpath)

        # Figure out which program we are wrapping
        if "-fs" in sys.argv:
            wrapped_prog = "fastStructure"
        elif "-mv" in sys.argv:
            wrapped_prog = "maverick"
        elif "-st" in sys.argv:
            wrapped_prog = "structure"

        # External program
        sanity.file_checker(arg.external_prog,
                            "Could not find your external program in "
                            "the specified path "
                            "'{}'.".format(arg.external_prog))
        # Input file
        sanity.file_checker(arg.infile, "The specified infile '{}' does "
                                        "not exist.".format(arg.infile))
        # Output dir
        sanity.file_checker(arg.outpath,
                            "Output argument '{}' is pointing to an "
                            "existing file. This argument requires a "
                            "directory.".format(arg.outpath), False)

        # Number of Ks
        if isinstance(arg.Ks, int):
            Ks = range(1, arg.Ks + 1)
        else:
            Ks = arg.Ks

        # Number of replicates
        replicates = range(1, arg.replicates + 1)

        threads = sanity.cpu_checker(arg.threads)

        signal.signal(signal.SIGINT, gracious_exit)

        structure_threader(Ks, replicates, threads, wrapped_prog, arg)

        if wrapped_prog == "maverick":
            bestk = maverick_merger(arg.outpath, Ks, arg.notests)
            arg.notests = True

        if arg.notests is False:
            bestk = structure_harvester(arg.outpath, wrapped_prog)
        else:
            bestk = Ks

        if arg.noplot is False:
            create_plts(arg.outpath, wrapped_prog, Ks, bestk, arg)

    # Perform only plotting operation
    if arg.main_op == "plot":

        # Get all files matching the provided prefix
        if arg.format == "fastStructure":
            infiles = [x for x in os.listdir(".") if x.startswith(arg.prefix)
                       and x.endswith(".meanQ")]
        elif arg.format == "structure":
            infiles = [x for x in os.listdir(".") if x.startswith(arg.prefix)
                       and "rep1_" in x]
        else:
            infiles = [x for x in os.listdir(".") if x.startswith(arg.prefix)
                       and x.endswith(".csv")]

        if not infiles:
            print("ERROR: There are no input files that match the"
                  " provided prefix")
            raise SystemExit

        if not os.path.exists(arg.outpath):
            os.makedirs(arg.outpath)

        bestk = [int(x) for x in arg.bestk]

        sp.main(infiles, arg.format, arg.outpath, bestk, popfile=arg.popfile,
                indfile=arg.indfile, filter_k=bestk, bw=arg.blacknwhite)


if __name__ == "__main__":
    main()

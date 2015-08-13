#!/usr/bin/python3

# Copyright 2015 Francisco Pina Martins <f.pinamartins@gmail.com>
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
import plotter.structplot as sp
import sanity_checks.sanity as sanity
from multiprocessing import Pool
from random import randrange


def gracious_exit(*args):
    """Graciously exit the program."""
    print("\rExiting graciously, murdering child processes and cleaning output"
          " directory", end="")
    os.chdir(cwd)
    sys.exit(0)


def runprogram(iterations):
    """Run each structure job. Return the worker status.
    This attribute will be populated with the worker exit code and output file
    and returned. The first element is the exit code itself (0 if normal exit
    and -1 in case of errors). The second element contains the output file
    that identifies the worker.
    """

    worker_status = (None, None)

    K, rep_num = iterations

    if wrapped_prog == "structure":
        # Keeps correct directory separator across OS's
        output_file = os.path.join(outpath, "K" + str(K) + "_rep" +
                      str(rep_num))
        cli = [arg.structure_bin, "-K", str(K), "-i", infile, "-o", output_file]
    else:
        # Keeps correct directory separator across OS's
        output_file = os.path.join(outpath, "fS_run_K")
        from os import symlink
        try:
            symlink(infile, infile+".str")
        except OSError as err:
            if err.errno != 17:
                raise

        cli = ["python2", arg.faststructure_bin, "-K", str(K), "--input", infile, "--output", output_file, "--format=str"]

    print("Running: " + " ".join(cli))
    program = subprocess.Popen(cli, bufsize=64, shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    out, err = map(lambda x: x.decode("utf-8"), program.communicate())

    # Check for errors in the program's exit code
    if program.returncode != 0:
        arg.log = True
        worker_status = (-1, output_file)
    else:
        worker_status = (0, None)

    # Handle logging for debugging purposes.
    if arg.log is True:

        logfile = open(os.path.join(outpath, "K" + str(K) + "_rep" +
                                    str(rep_num) + ".stlog"), "w")
        print("Writing logfile for K" + str(K) + ", replicate " +
              str(rep_num) + ". Please wait...")
        logfile.write(out)
        logfile.close()

    return worker_status


def structure_threader(Ks, replicates, threads):
    """Do the threading book-keeping to spawn jobs at the asked rate."""

    if wrapped_prog == "fastStructure":
        replicates = [1]
    else:
        os.chdir(os.path.dirname(infile))


    jobs = list(itertools.product(Ks, replicates))[::-1]

    # This will automatically create the Pool object, run the jobs and deadlock
    # the function while the children processed are being executed. This will
    # also allow to iterate over the values returned by all workers and to sort
    # them out to see if there were any errors
    pool = Pool(threads).map(runprogram, jobs)

    # Check for worker status. This will search the worker outputs and if
    # one or more workers had an error exit status, the error_list will be
    # populated with the cli commands that generated the errors
    error_list = [x[1] for x in pool if x[0] == -1]

    print("\n==============================\n")
    if error_list:
        print("%s Structure runs exited with errors. Check the log files of "
              "the following output files:" % len(error_list))
        for out in error_list:
            print(out)
    else:
        print("All %s jobs finished successfully." % len(pool))

    os.chdir(cwd)


def structureHarvester(resultsdir):
    """Run structureHarvester or fastChooseK to perform the Evanno test or the
    likelihood testing on the results."""
    outdir = os.path.join(resultsdir, "bestK")
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    sh.main(resultsdir, outdir)


def create_plts(resultsdir):
    """Create plots from result dir.
    :param resultsdir: path to results directory"""
    # This is only for Structure - it must be changed for fastStructure too.
    outdir = os.path.join(resultsdir, "plots")
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if wrapped_prog == "structure":
        # Get only relevant output files, choosen randomly from the replictes.
        plt_files = [os.path.join(resultsdir, "K") + str(i) + "_rep" +
                     str(randrange(arg.minK, arg.replicates)) + "_f"
                     for i in range(arg.minK, arg.Ks + 1)]
    else:
        plt_files = [os.path.join(resultsdir, "fS_run_K.") + str(i) + ".meanQ"
                     for i in range(max(arg.minK, 2), arg.Ks + 1)]

    sp.main(plt_files, wrapped_prog, outdir)

if __name__ == "__main__":
    import argparse
    # Argument list
    parser = argparse.ArgumentParser(description="A simple program to "
                                                 "paralelize the runs of the "
                                                 "Structure software.",
                                     prog="Structure_threader",
                                formatter_class=argparse.RawTextHelpFormatter)

    io_opts = parser.add_argument_group("Input/Output options")
    main_exec = parser.add_argument_group("Program execution options")
    run_opts = parser.add_argument_group("Structure run options")
    misc_opts = parser.add_argument_group("Miscellaneous options")

    main_exec_ex = main_exec.add_mutually_exclusive_group(required=True)

    main_exec_ex.add_argument("-st", dest="structure_bin", type=str,
                           default=None,
                           metavar="filepath",
                           help="Location of the structure executable in your "
                                "environment.")
    main_exec_ex.add_argument("-fs", dest="faststructure_bin", type=str,
                           default=None,
                           metavar="filepath",
                           help="Location of the fastStructure executable "
                           "(structure.py) in your environment.")

    run_opts.add_argument("-K", dest="Ks", type=int, required=True,
                          help="Number of Ks to run.\n", metavar="int")

    run_opts.add_argument("--min_K", dest="minK", type=int, required=False,
                          help="Minimum value of \"K\" to test "
                               "(default:%(default)s).\n",
                          metavar="int", default=1)

    run_opts.add_argument("-R", dest="replicates", type=int, required=False,
                          help="Number of replicate runs for each value of K "
                               "(default:%(default)s).\n"
                               "Ignored for fastStructure",
                          metavar="int", default=20)

    io_opts.add_argument("-i", dest="infile", type=str, required=True,
                         help="Input file.\n", metavar="infile")

    io_opts.add_argument("-o", dest="outpath", type=str, required=True,
                         help="Directory where the results will be stored "
                              "in.\n",
                         metavar="output_directory")

    misc_opts.add_argument("-t", dest="threads", type=int, required=True,
                           help="Number of threads to use "
                                "(default:%(default)s).\n",
                           metavar="int", default=4)

    misc_opts.add_argument("--log", dest="log", type=bool, required=False,
                           help="Choose this option if you want to enable "
                                "logging.",
                           metavar="bool", default=False)

    misc_opts.add_argument("--no-tests", dest="notests", type=bool,
                           required=False, help="Disable best K tests.",
                           metavar="bool", default=False)

    misc_opts.add_argument("--no-plots", dest="noplot", type=bool,
                           required=False, help="Disable plot drawing.",
                           metavar="bool", default=False)

    arg = parser.parse_args()

    # Where are we?
    cwd = os.getcwd()

    # Figure out which program we are wrapping
    if arg.faststructure_bin != None:
        wrapped_prog = "fastStructure"
        import evanno.fastChooseK as sh
    else:
        wrapped_prog = "structure"
        import evanno.structureHarvester as sh

    # Switch relative to absolute paths
    infile = os.path.abspath(infile)
    outpath = os.path.abspath(outpath)

    # Number of Ks
    Ks = range(arg.minK, arg.Ks + 1)

    # Number of replicates
    replicates = range(1, arg.replicates + 1)

    infile = arg.infile
    outpath = arg.outpath

    threads = sanity.cpu_checker(arg.threads)

    sanity.output_checker(outpath)

    signal.signal(signal.SIGINT, gracious_exit)

    structure_threader(Ks, replicates, threads)

    if arg.notests == False:
        try:
            structureHarvester(arg.outpath)
        except sh.Exception as ex:
            sys.stderr.write(str(ex))

    if arg.noplot == False:
        create_plts(arg.outpath)

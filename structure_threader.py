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

# Usage: python3 structure_threader.py -K Ks -reps replicates -i infile -o outpath -t num_of_threads -p path_to_structure
# Where "-K" is the number of "Ks" to test, "-reps" is the number of replicates,
# "-t"  is the number of threads and "-p" is the path to structure binary in the personal environment.


import os
import sys
import signal
import subprocess
import itertools
from multiprocessing import Pool


def gracious_exit(*args):
    """Graciously exit the program."""
    print("\rExiting graciously, murdering child processes and cleaning output"
          " directory", end="")
    sys.exit(0)


def runprogram(iterations):
    """Run each structure job."""

    # This attribute will be populated with the worker exit code and output file
    #  and  returned. First element is the exit code itself (0 if all normal,
    # -1 if  error), Second element will contain the output file to identify
    # the worker
    worker_status = (None, None)

    K, rep_num = iterations
    # Keeps correct directory separator across OS's
    output_file = os.path.join(outpath, "K" + str(K) + "_rep" + str(rep_num))

    cli = [arg.structure_bin, "-K", str(K), "-i", infile, "-o", output_file]
    print("Running: " + " ".join(cli))
    program = subprocess.Popen(cli, bufsize=64, shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    out, err = map(lambda x: x.decode("utf-8"), program.communicate())

    # Check for errors using STRUCTURE's signature string
    sign = "Exiting the program due to error(s) listed above."
    if sign in out:
        arg.log = True
        worker_status = (-1, output_file)
    else:
        worker_status = (0, None)

    # Handle logging for debugging purposes.
    if arg.log is True:

        logfile = open(os.path.join(outpath, "K" + str(K) + "_rep" +
                                    str(rep_num) + ".log"), "w")
        if not sign in out:
            print("Writing logfile for K" + str(K) + ", replicate " +
                  str(rep_num) + ". Please wait...")
        logfile.write(out)
        logfile.close()

    return worker_status


def structure_threader(Ks, replicates, threads):
    """Do the threading book-keeping to spawn jobs at the asked rate."""

    jobs = list(itertools.product(Ks, replicates))

    # This will automatically create the Pool object, run the jobs and deadlock
    # the function while the children processed are being executed. This will
    # also allow to iterate over the values return by all workers and to sort
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


if __name__ == "__main__":
    import argparse
    # Argument list
    parser = argparse.ArgumentParser(description="A simple program to paralelize the runs of the Structure software.",
                                     prog="Structure_threader",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-K", dest="Ks", type=int, required=True,
                        help="Number of Ks to run\n",
                        metavar="int")

    parser.add_argument("--min_K", dest="minK", type=int, required=False,
                        help="Minimum value of \"K\" to test (default:1)\n",
                        metavar="int", default=1)

    parser.add_argument("-R", dest="replicates", type=int, required=True,
                        help="Number of replicate runs for each value of K (default:20)\n",
                        metavar="int", default=20)

    parser.add_argument("-i", dest="infile", type=str, required=True,
                        help="Input file \n", metavar="infile")

    parser.add_argument("-o", dest="outpath", type=str, required=True,
                        help="Directory where the results will be stored in\n",
                        metavar="output_directory")

    parser.add_argument("-t", dest="threads", type=int, required=True,
                        help="Number of threads to use (default:4)\n",
                        metavar="int", default=4)

    parser.add_argument("-p", dest="structure_bin", type=str, required=False,
                        help="Location of the structure binary in your environment (default:structure - use structure from your $PATH)\n",
                        metavar="structure_bin",
                        default="structure")

    parser.add_argument("--log", dest="log", type=bool, required=False,
                        help="Choose this option if you want to enable logging",
                        metavar="bool", default=False)

    arg = parser.parse_args()

    # Number of K
    Ks = range(arg.minK, arg.Ks + 1)
    # Number of replicates
    replicates = range(1, arg.replicates + 1)
    infile = arg.infile
    outpath = arg.outpath

    # Make cpu usage check to prevent excessive usage of threads
    try:
        if int(arg.threads) > os.cpu_count():
            print("WARNING: Number of specified threads is higher than the"
                  " available ones. Adjusting number of threads to %s" %
                  os.cpu_count())
            threads = os.cpu_count()
        else:
            threads = arg.threads
    except:
        threads = arg.threads

    # Check for output directory, create if it doesn't exist
    if not os.path.exists(outpath) or not os.path.isdir(outpath):
        try:
            os.makedirs(outpath)
        except FileExistsError:
            print("ERROR: Output directory already exists.")
            raise SystemExit

    signal.signal(signal.SIGINT, gracious_exit)

    structure_threader(Ks, replicates, arg.threads)

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


import subprocess
from multiprocessing import Pool


def runprogram(iterations):
    """Run each structure job."""
    K, rep_num = iterations
    cli = [arg.structure_bin, "-K", str(K), "-i", infile, "-o", outpath + "/K"
           + str(K) + "_rep" + str(rep_num)]
    print("Running: " + " ".join(cli))
    program = subprocess.Popen(cli, bufsize=64, shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

    # This loop does nothing, but seems to be required for the program to fully
    # run all the jobs...
    # TODO: Add optional logging here
    for lines in program.stdout:
        pass


def structure_threader(Ks, replicates, threads):
    """Do the threading book-keeping to spawn jobs at the asked rate."""
    pool = Pool(threads)
    jobs = []
    # Ugly, ugly code. But since we are just dealing with counts here, we can
    # just leave it like that...
    for k in Ks:
        for rep in replicates:
            jobs.append((k, rep))

    pool.map(runprogram, jobs)
    pool.close()
    pool.join()
    print("All jobs finished.")


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

    structure_threader(Ks, replicates, arg.threads)

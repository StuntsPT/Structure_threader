#!/usr/bin/python3

# The MIT License (MIT)
#
# Copyright (c) 2014 Anil
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Copyright 2015-2016 Francisco Pina Martins <f.pinamartins@gmail.com>
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


import glob
import numpy as np


insum = lambda x, axes: np.apply_over_axes(np.sum, x, axes)


# class Exception(Exception):
#     pass


def parse_logs(files):
    """
    Parses through log files to extract marginal
    likelihood estimates from executing the
    variational inference algorithm on a dataset.

    Arguments:

        files : list
            list of .log file names
    """
    marginal_likelihood = []
    for file in files:
        handle = open(file, 'r')
        for line in handle:
            if 'Marginal Likelihood' in line:
                m = float(line.strip().split('=')[1])
                marginal_likelihood.append(m)
                break
        handle.close()

    return marginal_likelihood


def parse_varQs(files):
    """
    Parses through multiple .meanQ files to extract the mean
    admixture proportions estimated by executing the
    variational inference algorithm on a dataset. This is then used
    to identify the number of model components used to explain
    structure in the data, for each .meanQ file.

    Arguments:

        files : list
            list of .meanQ file names
    """
    bestKs = []

    for file in files:
        handle = open(file, 'r')
        Q = np.array([list(map(float, line.strip().split())) for line in handle])
        Q = Q/insum(Q, [1])
        handle.close()

        N = Q.shape[0]
        C = np.cumsum(np.sort(Q.sum(0))[::-1])
        bestKs.append(np.sum(C < N - 1) + 1)

    return bestKs

def main(indir, outpath):
    """
    Main function that runs everything in order.
    """
    if indir.endswith("/") is False:
        indir = indir + "/"

    files = glob.glob('%s*.log'%indir)
    Ks = np.array([int(file.split('.')[-2]) for file in files])
    marginal_likelihoods = parse_logs(files)

    files = glob.glob('%s*.meanQ'%indir)
    bestKs = parse_varQs(files)

    outfile = open(outpath + "/chooseK.txt", "w")
    ml = "Model complexity that maximizes marginal likelihood = %d\n"\
          % Ks[np.argmax(marginal_likelihoods)]
    ex_str = "Model components used to explain structure in data = %d\n"\
              % np.argmax(np.bincount(bestKs))

    outfile.write(ml)
    outfile.write(ex_str)
    outfile.close()

    # Retrieve list of bestk
    return [x for x in range(Ks[np.argmax(marginal_likelihoods)],
                             np.argmax(np.bincount(bestKs)) + 1)]


if __name__ == "__main__":
    # Usage: python3 fastChooseK.py /path/to/faststructure_outdir/common_sufix \
    # /path/to/dir/where/results_file/is_written
    from sys import argv

    filesuffix = argv[1]

    outpath = argv[2]

    main(filesuffix, outpath)

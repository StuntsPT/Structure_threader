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

# Usage: python3 structplot.py infile outfile

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter


def dataminer(indfile_name, fmt, popfile=None):
    """Parse the output files of structure and faststructure and return a
    numpy array with the individual clustering values and a list with the
    population names and number of individuals.

    :param indfile_name: path to structure/fastStructure output file
    :param fmt: string, format of the indfile_name. Can be either structure of
    faststructure
    :param popfile: string. path to file with population list
    """

    # Parse popfile if provided
    if popfile:
        # Assuming popfile has 2 columns with pop name in 1st column and number
        # of samples in the 2nd column
        poparray = np.genfromtxt(popfile)
        # Final pop list
        poplist = [(x, y) for x, y in zip(np.cumsum([x[1] for x in poparray]),
                                          [x[0] for x in poparray])]

    else:
        poplist = []

    # Parse structure/faststructure output file
    if fmt == "faststructure":
        qvalues = np.genfromtxt(indfile_name)

    else:
        qvalues = np.array([])

        # Start file parsing
        r = False
        with open(indfile_name) as file_handle:
            for line in file_handle:
                if line.strip().lower().startswith("inferred ancestry of "
                                                   "individuals:"):
                    # Enter parse mode ON
                    r = True
                    # Skip subheader
                    next(file_handle)
                elif line.strip().lower().startswith("estimated allele "
                                                     "frequencies in each "
                                                     "cluster"):
                    # parse mode OFF
                    r = False
                elif r:
                    if line.strip() != "":
                        fields = line.strip().split()
                        # Get cluster values
                        cl = [float(x) for x in fields[5:]]
                        try:
                            qvalues = np.vstack((qvalues, cl))
                        except ValueError:
                            qvalues = np.array(cl)
                        if not popfile:
                            # Get population
                            poplist.append(int(fields[3]))

        if not popfile:
            # Transform poplist in convenient format,in which each element
            # is the boundary of a population in the x-axis
            poplist = Counter(poplist)
            poplist = [(x, None) for x in np.cumsum(list(poplist.values()))]

    return qvalues, poplist


def plotter(qvalues, poplist):
    """
    Plot the qvalues histogram.

    :param qvalues: numpy array with variable shape containing the inferred
    ancestry values for each sample
    :param poplist: list, contains information on the sample's population.
    Must be a list of tuples, in which each element consists of
    (x-axys position int, population label str). Example:
    [(2, "Angola"), (5, "Kenya")...]
    """

    colors = ('#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
              '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928')

    plt.style.use("ggplot")

    numinds = qvalues.shape[0]

    # Update plot width according to the number of samples
    plt.rcParams["figure.figsize"] = (8 * numinds * .05, 6)

    for i in range(qvalues.shape[1]):
        if i == 0:
            plt.bar(range(numinds), qvalues[:, i], facecolor=colors[i],
                    edgecolor="none", width=1)
            formerQ = qvalues[:, i]
        else:
            plt.bar(range(numinds), qvalues[:, i], bottom=formerQ,
                    facecolor=colors[i], edgecolor="none", width=1)
            formerQ = formerQ + qvalues[:, i]

    # Set lines delimiting populations
    for i in poplist:
        plt.axvline(x=i[0], linewidth=1.5, color='black')

    plt.ylim(0, 1)
    plt.xlim(0, numinds)

    plt.yticks([])

    plt.show()

if __name__ == "__main__":
    data, pops = dataminer("/home/diogo/Diogo/Science/Scripts/packages/Structure_threader/TestData/Test/K3_rep1_f", "structure")
    plotter(data, pops)

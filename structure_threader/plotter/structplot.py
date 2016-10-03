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
from collections import Counter, defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def parse_usepopinfo(fhandle, end_string):
    """
    Parses Structure results when using the USEPOPINFO flag.
    """
    qvalues = np.array([])
    poplist = []
    # Skip subheader
    next(fhandle)
    for line in fhandle:
        if line.strip() != "":
            if line.strip().lower().startswith(end_string):
                return qvalues, poplist

            qvalues_dic = defaultdict(float)
            fields = line.strip().split("|")[:-1]
            # Assumed pop
            qvalues_dic[fields[0].split()[3]] = float(fields[0].split()[5])
            # Other pops
            for pop in fields[1:]:
                prob = sum(map(float, pop.split()[-3:]))
                qvalues_dic[pop.split()[1][:-1]] = prob
            clv = []
            for percents in sorted(list(map(int, list(qvalues_dic.keys())))):
                clv.append(qvalues_dic[str(percents)])
            try:
                qvalues = np.vstack((qvalues, clv))
            except ValueError:
                qvalues = np.array(clv)
            poplist.append(int(fields[0].split()[3]))


def parse_nousepopinfo(fhandle, end_string):
    """
    Parses Structure results when **not** using the USEPOPINFO flag.
    """
    qvalues = np.array([])
    poplist = []

    for line in fhandle:
        if line.strip() != "":
            if line.strip().lower().startswith(end_string):
                return qvalues, poplist

            fields = line.strip().split()
            # Get cluster values
            clv = [float(x) for x in fields[5:]]
            try:
                qvalues = np.vstack((qvalues, clv))
            except ValueError:
                qvalues = np.array(clv)
            # Get population
            poplist.append(int(fields[3]))


def dataminer(indfile_name, fmt, popfile=None):
    """Parse the output files of structure and faststructure and return a
    numpy array with the individual clustering values and a list with the
    population names and number of individuals.

    :param indfile_name: path to structure/fastStructure output file
    :param fmt: string, format of the indfile_name. Can be either structure of
    faststructure
    :param popfile: string. path to file with population list
    """

    poplist = []

    # Parse popfile if provided
    if popfile:
        # Assuming popfile has 3 columns with pop name in 1st column, number
        # of samples in the 2nd column and input file order number in the 3rd.
        datatype = np.dtype([("popname", "|U20"), ("num_indiv", int),
                             ("original_order", int)])
        poparray = np.genfromtxt(popfile, dtype=datatype)
        # Final pop list
        poplist = [([x]*y, z) for x, y, z in
                   zip([x[0] for x in poparray],
                       [x[1] for x in poparray],
                       [x[2] for x in poparray])]

    # Parse structure/faststructure output file
    if fmt == "fastStructure":  # fastStructure
        qvalues = np.genfromtxt(indfile_name)

    else:  # STRUCTURE
        parsing_string = "inferred ancestry of individuals:"
        popinfo_string = ("probability of being from assumed population | " +
                          "prob of other pops")
        end_parsing_string = "estimated allele frequencies in each cluster"

        with open(indfile_name) as file_handle:
            for line in file_handle:
                if line.strip().lower().startswith(parsing_string):
                    if next(file_handle).lower().startswith(popinfo_string):
                        qvalues, numlist = parse_usepopinfo(file_handle,
                                                            end_parsing_string)
                        break
                    else:
                        qvalues, numlist = parse_nousepopinfo(file_handle,
                                                              end_parsing_string)
                        break
        #if not popfile:
            #poplist = numlist


        if not popfile:
            # Transform poplist in convenient format, in which each element
            # is the boundary of a population in the x-axis
            poplist = numlist
            poplist = Counter(poplist)
            poplist = [([x]*y, None) for x, y in poplist.items()]


    if popfile:
        # Re-order the qvalues to match what is specified in the popfile.
        qvalues = re_order(qvalues, poplist)

    return qvalues, poplist


def re_order(qvalues, poplist):
    """
    Recieves a list of q-values, re-orders them according to the order
    specified in the popfile and returns that list.
    """
    qvalues = qvalues.tolist()
    locations_dict = {pos:(index, len(loc)) for index, (loc, pos) in
                      enumerate(poplist)}

    offsets = [None] * len(poplist)


    def compute_offset(pos):
        """
        Recursively compute the offset values.
        """
        # compute new offset from offset and length of previous position. End of
        # recursion at position 1: we’re at the beginning of the list
        offset = sum(compute_offset(pos-1)) if pos > 1 else 0
        # get index at where to store current offset + length of current location
        index, length = locations_dict[pos]
        offsets[index] = (offset, length)

        return offsets[index]


    compute_offset(len(poplist))

    qvalues = [value for offset, length in offsets for value in
               qvalues[offset:offset + length]]

    qvalues = np.array(qvalues)

    return qvalues


def plotter(qvalues, poplist, outfile):
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
    plt.rcParams["figure.figsize"] = (8 * numinds * .01, 2.64)

    fig = plt.figure()
    axe = fig.add_subplot(111, xlim=(0, numinds), ylim=(0, 1))

    for i in range(qvalues.shape[1]):
        # Get bar color. If K exceeds the 12 colors, generate random color
        try:
            clr = colors[i]
        except IndexError:
            clr = np.random.rand(3, 1)

        if i == 0:
            axe.bar(range(numinds), qvalues[:, i], facecolor=clr,
                    edgecolor="none", width=1)
            former_q = qvalues[:, i]
        else:
            axe.bar(range(numinds), qvalues[:, i], bottom=former_q,
                    facecolor=clr, edgecolor="none", width=1)
            former_q = former_q + qvalues[:, i]

    # Annotate population info
    if poplist:
        for i in zip(np.cumsum([len(x[0]) for x in poplist]), poplist):
            orderings = [(x, y[0][0]) for x, y in
                         zip(np.cumsum([len(x[0]) for x in poplist]), poplist)]
            count = 1
        for ppl, vals in enumerate(orderings):

            # Add population delimiting lines
            plt.axvline(x=vals[0], linewidth=1.5, color='black')

            # Add population labels
            # Determine x pos
            xpos = vals[0] - ((vals[0] - orderings[ppl - 1][0]) / 2) if ppl > 0 \
                else vals[0] / 2

            # Draw text
            axe.text(xpos, -0.05, vals[1] if vals[1] else "Pop{}".format(count),
                     rotation=45, va="top", ha="right", fontsize=6,
                     weight="bold")
            count += 1

    for axis in ["top", "bottom", "left", "right"]:
        axe.spines[axis].set_linewidth(2)
        axe.spines[axis].set_color("black")

    plt.yticks([])
    plt.xticks([])


    plt.savefig("{}.svg".format(outfile), bbox_inches="tight")


def main(result_files, fmt, outdir, popfile=None):
    """
    Wrapper function that generates one plot for each K value.
    :return:
    """

    for files in result_files:
        data, pops = dataminer(files, fmt, popfile)
        # Get output file name from input file name
        outfile = os.path.join(outdir, files.split(os.sep)[-1])
        # Create plots
        plotter(data, pops, outfile)

if __name__ == "__main__":
    from sys import argv
    # Usage: structplot.py results_file format outdir
    DATAFILES = []
    DATAFILES.append(argv[1])
    main(DATAFILES, argv[2], argv[3])

#!/usr/bin/python3

# Copyright 2015-2017 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of speedup_plotter.
# speedup_plotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# speedup_plotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with speedup_plotter. If not, see <http://www.gnu.org/licenses/>.

import matplotlib.pyplot as plt
import numpy

def data_harverster(datafile_name):
    """
    Gather speedup data from a csv file and return a np array with it.
    """
    timearray = numpy.genfromtxt(datafile_name, delimiter=";", autostrip=True,
                                 dtype=float, skip_header=False, names=True,
                                 filling_values=False)

    return timearray


def draw_plot(timearray):
    """
    Draw a line plot based on speedup data.
    """
    system_cores = max(map(int, timearray["CPUs"]))
    names = [x for x in timearray.dtype.names if x != "CPUs"]
    linetypes = ("k-", "k:", "k--")
    lines = {k: v for k, v in zip(names, linetypes)}
    plt.axis([1, system_cores + 1, 1, system_cores + 1])
    for name in names:
        plt.plot(list(map(int, timearray["CPUs"])), timearray[name],
                 lines[name],
                 fillstyle="full", ms=7, label=name)
    plt.plot(range(1, system_cores + 2), range(1, system_cores + 2), 'k-.',
             label="Linear scaling")

    plt.grid(True)
    plt.xlabel("Number of threads")
    plt.ylabel("Speed increase")
    plt.xticks(list(map(int, timearray["CPUs"])))
    plt.legend(loc=2, fontsize="small")
    plt.savefig(argv[1] + "_plot.svg", format="svg")
    #plt.show()

if __name__ == "__main__":
    from sys import argv
    TIMEARRAY = data_harverster(argv[1])
    draw_plot(TIMEARRAY)

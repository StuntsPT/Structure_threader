#!/usr/bin/python3

# Copyright 2015 Francisco Pina Martins <f.pinamartins@gmail.com>
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
    """Gather speedup data from a csv file and return a np array with it.."""
    timearray = numpy.genfromtxt(datafile_name, delimiter = ";", autostrip=True, 
                                 dtype=float, skip_header=True,
                                 filling_values=False)
    
    return timearray


def draw_plot(timearray):
    """Draw a line plot based on the speedup data."""
    i7 = list(timearray[:, 1][:-4])
    i7.insert(0, 1)
    amd = list(timearray[:, 2][:-4])
    amd.insert(0, 1)
    e5 = list(timearray[:, 3][:-4])
    e5.insert(0, 1)
    oldxeon = list(timearray[:, 4])
    oldxeon.insert(0, 1)

    plt.axis([0, 16, 0, 16])
    plt.plot([1, 2, 4, 6, 8], i7, 'b-s')
    plt.plot([1, 2, 4, 6, 8], amd, 'r-^')
    plt.plot([1, 2, 4, 6, 8, 10, 12, 14, 16], oldxeon, 'y-o')
    plt.plot([1, 2, 4, 6, 8], e5, 'gp-')
    
    plt.grid(True)
    plt.plot(range(16), range(16))
    plt.show()

if __name__ == "__main__":
    timearray = data_harverster("/home/francisco/aa.csv")
    draw_plot(timearray)

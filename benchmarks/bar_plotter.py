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

from speedup_plotter import data_harverster


def draw_bar_plot(dataframes):
    """
    Draws a bar plot with the different times for single vs. multiple
    threads implementations."""

    N = len(dataframes[:, 0])
    single_times = dataframes[:, 1]
    threaded_times = dataframes[:, 2]

    locs = numpy.arange(N)  # the x locations for the groups

    width = 0.35       # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(locs, single_times, width, color='grey')

    rects2 = ax.bar(locs+width, threaded_times, width, color='darkgrey')

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Time (s)')
    ax.set_title('Time to calculate clustering for each value of "K", single, '
                 'vs. multiple threading')
    ax.set_xticks(locs+width)

    ax.set_xticklabels(list(map(int, dataframes[:, 0])))

    ax.legend((rects1[0], rects2[0]), ('Single thread', '8 threads'), loc="upper left")

    ax.grid(True, zorder=0)

    plt.savefig(argv[1] + "_plot.svg", format="svg")

if __name__ == "__main__":
    from sys import argv
    # Usage: python3 bar_plotter.py K_times.csv
    dataframes = data_harverster(argv[1])
    draw_bar_plot(dataframes)

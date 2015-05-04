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

def dataminer(indfile_name):
    """Parses the output files of structure and faststructure and returns a 
    numpy array with the individual clustering values and a list with the
    population names and number of individuals."""
    indfile = indfile_name  # Placeholder code to insert function that identifies structure and faststructure outputs and uses the correct parsing function.
    
    Qvalues = np.genfromtxt(indfile)
    
    return Qvalues

def plotter(Qvalues):
    """Plots the Qvalues histogram"""
    
    colors = ('#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
              '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928')
    
    numinds = Qvalues.shape[0]
    for i in range(Qvalues.shape[1]):
        if i == 0:
            plt.bar(range(numinds), Qvalues[:, i], facecolor=colors[i], edgecolor="none", width=1)
            formerQ = Qvalues[:, i]
        else:
            plt.bar(range(numinds), Qvalues[:, i], bottom=formerQ, facecolor=colors[i], edgecolor="none", width=1)
            formerQ = formerQ + Qvalues[:, i]
    
    plt.show()
    
if __name__ == "__main__":
    data = dataminer("/home/francisco/Dropbox/Science/PhD/GBS/Analyses/clust6/structure/tests/k3.3.meanQ")
    plotter(data)
    
    

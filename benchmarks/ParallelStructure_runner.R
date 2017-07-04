#!/usr/bin/Rscript
# Copyright 2016 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of Structure_threader.
# Structure_threader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Structure_threader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Structure_threader. If not, see <http://www.gnu.org/licenses/>.

# Usage: Rscript ParallelStructure_runer.R "number_of_threads_to_use"

library(ParallelStructure)

## Define variables
# Get number of threads from CLI
args <- commandArgs(trailingOnly = TRUE)

# Joblist location
joblist_location = "/home/francisco/bench/joblist.txt"
# Location of STRUCUTRE binary
structure_bin = "/opt/structure/bin/"
# Infile location
infile_path = "/home/francisco/bench/SmallTestData.structure"
# Outfile location
outfile_path = "Results/" # Yes! This C**p program takes arguments in both full and relative path simultaneously!
# Number of individuals
n_inds = 100
#Number of loci
n_loci = 80

parallel_structure(joblist = joblist_location, n_cpu = args[1],
                   structure_path = structure_bin, infile = infile_path,
                   outpath = outfile_path, numinds = n_inds, numloci = n_loci,
                   plot_output = 0, label = 1, popdata = 1, popflag = 0,
                   locdata = 0, phenotypes = 0, markernames = 1,
                   mapdist = 0, onerowperind = 0, phaseinfo = 0,
                   recessivealleles = 0, phased = 0, extracol = 0, missing = -9,
                   ploidy = 2, noadmix = 0, linkage = 0, usepopinfo = 0,
                   locprior = 0, inferalpha = 1, alpha = 1, popalphas = 0,
                   unifprioralpha = 1, alphamax = 10, alphapropsd = 0.025,
                   freqscorr = 0, onefst = 0, fpriormean = 0.01,
                   fpriorsd = 0.05, inferlambda = 0, lambda = 1,
                   computeprob = 1, pfromflagonly = 0, ancestdist = 0,
                   startatpopinfo = 0, metrofreq = 10, updatefreq = 100,
                   printqhat = 0,revert_convert=0, randomize=1)

#!/usr/bin/Rscript
# Copyright 2019 Francisco Pina Martins <f.pinamartins@gmail.com>
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

ll = Sys.getenv()[ grep("R_LIBS_USER", names(Sys.getenv())) ]
local_lib = gsub("^.*\t", "", ll)

if(!require("alstructure")){
  if(!require("devtools")){
    install.packages("devtools", lib=.libPaths()[1])
  }
  library("devtools")
  install_github("storeylab/alstructure", build_vignettes=FALSE, ref="e355411", lib=.libPaths()[1])
  library(alstructure)
}

if(!require(lfa)){
  if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager", lib=.libPaths()[1])
  
  BiocManager::install("lfa", lib=.libPaths()[1])
  library(lfa)
}

alstructure_wrapper = function(input_prefix, K) {
  #' ALStructure wrapper
  #'
  #' Small wrapper function that wraps ALStructure
  #' Takes an input prefix (file minus the extension) and value of K
  #' as arguments and returns a q-matrix

  K = as.numeric(K)
  input_data = lfa::read.bed(input_prefix)
  fit <- alstructure(X = input_data, d_hat=K)
  q_matrix = t(fit$Q_hat)

  return(q_matrix)
}

args = commandArgs(trailingOnly=TRUE)

if (sys.nframe() == 0){
  Q_matrix = alstructure_wrapper(args[1], args[2])
  write.csv(Q_matrix, args[3])
}

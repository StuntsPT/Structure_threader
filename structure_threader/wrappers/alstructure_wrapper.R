#!/usr/bin/env Rscript
# Copyright 2019-2020 Francisco Pina Martins <f.pinamartins@gmail.com>
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

## Default repo
local({r <- getOption("repos")
r["CRAN"] <- "http://cran.r-project.org" 
options(repos=r)
})

ll = Sys.getenv()[ grep("R_LIBS_USER", names(Sys.getenv())) ]
local_lib = gsub(".*~", path.expand('~'), as.character(ll), perl=T)

if (dir.exists(local_lib) == FALSE) {
  dir.create(local_lib, showWarnings = TRUE, recursive = TRUE)
}

.libPaths(c(local_lib))

if(!require("alstructure")){
  if(!require("devtools")){
    install.packages("devtools")
  }
  library("devtools")
  install_github("storeylab/alstructure", build_vignettes=FALSE, ref="e355411")
  library(alstructure)
}

if(!require(lfa)){
  if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
  
  BiocManager::install("lfa")
  library(lfa)
}

alstructure_wrapper = function(data_matrix, K) {
  #' ALStructure wrapper
  #'
  #' Small wrapper function that wraps ALStructure
  #' Takes a data matrix and value of K
  #' as arguments and returns a q-matrix

  K = as.numeric(K)

  fit <- alstructure(X = data_matrix, d_hat=K)
  q_matrix = t(fit$Q_hat)

  return(q_matrix)
}

data_to_matrix = function (ifile) {
  #' data_to_matrix
  #' Converts the data in an input file into a data matrix that can be read
  #' by alstructure
  #' Takes a tsv or a bed file as input and returns a data matrix

  if (substring(ifile, nchar(ifile)-3) == ".tsv") {
    print(ifile)
    input_data = as.matrix(read.csv(ifile, header=F, sep="\t"))
  } else {
    input_data = lfa::read.bed(ifile)
  }
  
  return(input_data)
}

args = commandArgs(trailingOnly=TRUE)

if (sys.nframe() == 0){
  data_matrix = data_to_matrix(args[1])
  Q_matrix = alstructure_wrapper(data_matrix, args[2])
  write.csv(Q_matrix, args[3])
}

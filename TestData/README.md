#Test Data for  *Structure_threader*

In this directory you will find the data that was used to benchmark *Structure_threader*.

##Contents (in alphabetical order):

* benchmark.sh
* extraparams
* joblist.txt
* mainparams
* TestData.structure

###benchmark.sh

This is a [Zsh](http://www.zsh.org/) script to run STRUCTURE sequentially for 16 jobs, 4 jobs for each value of "K" (from 1 to 4).
It does not log the runs, nor the results (everything is written into the same file).
It was used with the Unix [time](http://linux.die.net/man/1/time) program to log the time it took to run.

###extraparams and mainparams

The STRUCTURE paramater files that were used in the benchmarking process.

###joblist.txt

The joblist used to benchmark *ParallelStructure*. Consists of 16 jobs, 4 values of "K" with 4 replicates each.

###TestData.structure

This is the datafile itself  that was used in the benchmarking process.
It contains 83 individuals, divided in 17 populations, represented for 29 SNP loci.
There is aproximately 13% missing data in the file.

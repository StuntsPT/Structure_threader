# Benchmarking process

You can find some of the scripts used for the benchmarking process inside the [*benchmarks* directory](https://github.com/StuntsPT/Structure_threader/tree/master/benchmarks). Inside this directory you will find the files used for benchmarking the single threaded runs of both STRUCTURE and *fastStructure*, as well as some results.
The scripts to draw the speedup plots and the barplots can be found there as well.
You will also find relevant documentation, which is reproduced here.


## Directory contents:

* benchmark.sh
* benchmark_fast.sh
* speedup_plotter.py
* bar_plotter.py


### benchmark.sh

This is a [Zsh](http://www.zsh.org/) script to run STRUCTURE sequentially for 16 jobs, 4 jobs for each value of "K" (from 1 to 4).
It does not log the runs, nor the results (everything is written into the same file).
It was used with the Unix [time](http://linux.die.net/man/1/time) program to log the time it took to run.


### benchmark_fast.sh

This is a [Zsh](http://www.zsh.org/) script to run fastStructure sequentially for 16 jobs, 4 jobs for each value of "K" (from 1 to 4).
It does not log the runs, nor the results (everything is written into the same file).
It was used with the Unix [time](http://linux.die.net/man/1/time) program to log the time it took to run.


### speedup_plotter.py

This is the python script that was used to create the speedup plots for the generated data.


### bar_plotter.py

This is the python script that was used to create the bar plots for the single threaded vs. multi-threaded run times.

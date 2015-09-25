# Structure_threader

A simple program to parallelize the runs of [Structure](http://pritchardlab.stanford.edu/structure.html) and [fastStructure](https://rajanil.github.io/fastStructure/) software.


## Requirements

Python3. Only uses modules from the standard library. Requires matplotlib to draw the plots and numpy to run "fastChooseK.py".

It *might* also work with python2, however, this is not as tested as the python3 version (actually its hardly tested at all).

Running in python3 also yields ~11% speed gains relatively to python2 (altough this testing was limited).


## Installation

Just clone the repository, and place the contents, respecting the directory
structure in your $PATH.

You can go the the "helper_scripts" directory where you will find some scripts to help you install both *Structure* and *fastStructure*.


## Running

The program takes a few arguments:

* K (-K)
* Replicates (-R)
* Input file (-i)
* Output dir (-o)
* Number of threads (-t)
* Program location - you have to pass one and only of the following arguments:
    * Structure location (if you want to run "Structure"; -st)
    * fastStructure location (if you want to run "fastStructure"; -fs) -
     ~~**WARNING** - This is not yet implemented.~~
* Logging (optional - useful when problems arise; --log)
* Minimum K (optional - use as a start value for "K" - by default the value is 1; --min_K)
* No-tests (optional - use this if you do not want to run the BestK tests; --no-tests)
* No-plots (optional - use this if you do not want to draw plots; --no-plots)

Example:

```
structure_threader.py -K Ks -R replicates -i infile -o outpath -t num_of_threads -st path_to_structure
```

Where -K is the number of "Ks" to run, -R is the number of replicate runs for
each value of "K", -i is the input file for STRUCTURE, -o is the directory where the output results should be stored,
-t is the number of threads to use and -p the path for the STRUCTURE binary.

The program should be run in the same directory as the files "mainparams" and
"extraparams" for your STRUCTURE run are placed.


### fastStrucutre Warning:

If running fastStructure, keep in mind that this program requires your input
file to have each individual represented in two rows (one for each allele), and
six "bogus" columns before the actual data. **No Header is allowed**. Here is a short example:

```
Ind1    col1  col2  col3  col4  col5 1    3   1   4
Ind1    col1  col2  col3  col4  col5 1    3   2   4
Ind2    col1  col2  col3  col4  col5 1    2   1   4
Ind2    col1  col2  col3  col4  col5 1    2   1   3

```


## Output

The program will inform the user of what run is currently being processed by
outputting the command it is running to STDOUT, such as this:

```
Running: /opt/structure/bin/structure -K 1 -i input_file.structure -o results_admix/K1_rep10
```

After each run, the corresponding output file is saved to the location chosen in
the *Output dir* argument.

When all tasks are performed the program will exit with the message:
"All jobs finished."
After these jobs are run, the program will use [Structure Harvester](http://taylor0.biology.ucla.edu/struct_harvest/) to infer the optimal value of "K".
After this, the program will create plots with the inferred clustering, one for each "K".


## Test data

The directory "TestData" in the repository contains some test data that was used in the benchmarking of *Structure_threader*.
You can find documentation about it inside the directory itself.


## Benchmarking processed

You can find some of the scripts used for the benchmarking process inside the *benchmark* directory. Further documentation on this topic can be found inside the directory itself.


## Other works

The script "fastChooseK.py" was taken from [the original fastStructure repository](https://github.com/rajanil/fastStructure), ported to python 3, largely modified to work as a module for the main script and relicensed as GPLv3.

The scripts "harvesterCore.py" and "structureHarvester.py" were taken from [the original structureHarverster repository](https://github.com/dentearl/structureHarvester), ported to python 3, and slightly modified to work as a module for the main script. Please see the "Citation" part of the README to know what to cite, should you use this module.


## Citation

If you use Structure_threader, please cite

* Coming soon (hopefully)!

If you used the evanno test module, please cite:

*  Earl, Dent A. and vonHoldt, Bridgett M. (2012) STRUCTURE HARVESTER: a website
 and program for visualizing STRUCTURE output and implementing the Evanno
 method. Conservation Genetics Resources vol. 4 (2) pp. 359-361. doi: 10.1007/s12686-011-9548-7 http://www.springerlink.com/content/jnn011511h415358/


## License

GPLv3

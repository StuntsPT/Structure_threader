# Structure_threader
A simple program to paralelize the runs of the [Structure](http://pritchardlab.stanford.edu/structure.html) software.


##Requirements
Python3. Only uses modules from the standard library. Requires matplotlib to draw the plots.

It *might* also work with python2, however, this is not as tested as the python3 version (actually its hardly tested at all).

Running in python3 also yelds ~11% speed gains relatively to python2 (altough this testing was limited).


##Installation
Just clone the repository, and place the contents, respecting the directory
structure your $PATH.


##Running
The program takes a few arguments:

* K (-K)
* Replicates (-R)
* Input file (-i)
* Output dir (-o)
* Number of threads (-t)
* Program location - you have to pass one and only of the following arguments:
    * Structure location (if you want to run "Structure"; -st)
    * fastStructure location (if you want to run "fastStructure"; -fs) **WARNING** This is not yet implemented.
* Logging (optional - usefull when problems arise; --log)
* Minnimum K (optional use as a start value for "K" - by default thi value is 1; --min_K)

Example: 

```
structure_threader.py -K Ks -R replicates -i infile -o outpath -t num_of_threads -st path_to_structure
```

Where -K is the number of "Ks" to run, -R is the number of replicate runs for
each value of "K", -i is the input file for STRUCTURE, -o is the directory where the output results should be stored,
-t is the number of threads to use and -p the path for the STRUCTURE binary.

The program should be run in the same directory as the files "mainparams" and
"extraparams" for your STRUCTURE run are placed.

##Output
The program will inform the user of what run is currently being processed by
outputting the command it is running to STDOUT, such as this:

```
Running: /opt/structure/bin/structure -K 1 -i input_file.structure -o results_admix/K1_rep10
```

After each run, the corresponding ouput file is saved to the location choosen in
the *Output dir* argument.

When all tasks are performed the program will exit with the message:
"All jobs finished."
After these jobs are run, the program will use [Structure Harvester](http://taylor0.biology.ucla.edu/struct_harvest/) to infer the optimal value of "K".
After this, the program will create plots with the inferred clustering, one for each "K".

##Downstream

The results directory is ready to be zipped and used in [Structure Harvester](http://taylor0.biology.ucla.edu/struct_harvest/) or [CLUMPAK](http://clumpak.tau.ac.il/).

##Test data

The directory "TestData" in the repository contains some test data that was used in the benchmarking of *Structure_threader*.
You can find documentation about it inside the directory itself.

##Citation

If you use Structure_threader, please cite 

* Comming soon (hopefully)!

If you used the evanno test module, please cite:

*  Earl, Dent A. and vonHoldt, Bridgett M. (2012) STRUCTURE HARVESTER: a website
 and program for visualizing STRUCTURE output and implementing the Evanno 
 method. Conservation Genetics Resources vol. 4 (2) pp. 359-361. doi: 10.1007/s12686-011-9548-7 http://www.springerlink.com/content/jnn011511h415358/

##License
GPLv3

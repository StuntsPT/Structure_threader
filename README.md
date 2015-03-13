# Structure_threader
A simple program to paralelize the runs of the [Structure](http://pritchardlab.stanford.edu/structure.html) software.

##Requirements
Python3. Only uses modules from the standard library.

It also work with python2, however, Ctrl+c will not kill the process graciously.

Running in python3 also yelds ~11% speed gains relatively to python2(altough this testing was limited).


##Installation
Just place the script "structure_threader.py" on any location on your $PATH.


##Running
The program takes a few arguments:

* K
* Replicates
* Input file
* Output dir
* Number of threads
* Structure location
* Logging (usefull for debugging)

Example: 

```
structure_threader.py -K Ks -R replicates -i infile -o outpath -t num_of_threads -p path_to_structure
```

Where -K is the number of "Ks" to run, -R is the number of replicate runs for
each value of "K", -i is the input file for STRUCTURE, -o is the directory where the output results should be stored,
-t is the number of threads to use and -p the path for the STRUCTURE binary.

The program should be run in the same directory as the files "mainparams" and
"extraparams" from STRUCTURE are placed.

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

##Downstream

The results directory is ready to be zipped and used in [Structure Harvester](http://taylor0.biology.ucla.edu/struct_harvest/) or [CLUMPAK](http://clumpak.tau.ac.il/).

##Test data

The directory "TestData" in the repository contains some test data that was used in the benchmarking of *Structure_threader*.
You can find documentation about it inside the directory itself.

##License
GPLv3

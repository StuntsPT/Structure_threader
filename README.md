# Structure_threader
A simple program to paralelize the runs of the [Structure](http://pritchardlab.stanford.edu/structure.html) software.

##Requirements
Python3. Only uses modules from the standard library.
It **might** also work with python2, but it was not tested.

##Installation
Just place the script "structure_threader.py" on any location on your $PATH.

Before the 1st run, don't forget to edit "Where is structure?" in the source
code to provide the location of the structure binary in your environment.

##Running
The program takes a few arguments:

* K
* Replicates
* Input file
* Output dir
* Number of threads

Example: 

```
structure_threader.py 6 20 input_file.structure results_admix/ 4
```

Where 6 is the number of "Ks" to run and 20 is the number of replicate runs for
each value of "K", "input_file.structure" is the input file, 
"results_admix" is the directory where the output results should be stored
and 4 is the number of threads to use.

The program should be run in the same directory as the files "mainparams" and
"extraparams" are stored and configured.

##Output
The program will inform the user of what run is currently being processed by
outputting the command it is running to the STDOUT, such as this:

```
Running: /opt/structure/bin/structure -K 1 -i input_file.structure -o results_admix/K1_rep10
```

After each run, the corresponding ouput file is saved to the location choosen in
the *Output dir* argument.

When all tasks are performed the program will exit with the message:
"All jobs finished."


##License
GPLv3

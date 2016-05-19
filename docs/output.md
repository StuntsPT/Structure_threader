# Output

The program will inform the user of what run is currently being processed by
outputting the command it is running to STDOUT, such as this:

```
Running: /opt/structure/bin/structure -K 1 -i input_file.structure -o results_admix/K1_rep10
```

After each run, the corresponding output file is saved to the location chosen in
the *Output dir* argument.

When all tasks are performed the program will exit with the message:
"All jobs finished."
After these jobs are run, the program will use [Structure Harvester](http://taylor0.biology.ucla.edu/struct_harvest/) (or "fastChooseK.py" if wrapping fastStructure) to infer the optimal value of "K".
Finally, the program will create plots with the inferred clustering, one for each calculated value of "K".

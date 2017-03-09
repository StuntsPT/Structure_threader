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
After these jobs are run, the program will use [Structure Harvester](http://taylor0.biology.ucla.edu/struct_harvest/) (or "fastChooseK.py" if wrapping *fastStructure*) to infer the optimal value of "K".
Finally, the program will create plots with the inferred clustering, one for each calculated value of "K".
A "Thermodynamic Integration" test will be performed to infer the bestK if using *MavericK*.

## Results
After a successful run, inside the directory you selected as "output directory" (let's call it "My_results" for the sake of the example) you will find the following:

* In the root of "My_results" you will find the "results files" outputted by the wrapped program. One file (directory, in the case of *MavericK*) for each replicate of "K".
*  Under "My_results/bestK" you will find either the results of the "Evanno test", the results of "fastChooseK.py", or the results of "Thermodynamic Integration" test, depending on what program was wrapped.
* Under "My_results/plots" you will find one plot for each value of "K" in [SVG format](https://www.w3.org/Graphics/SVG/).
* If logging was turned on, you will also find a detailed log file for each run in the root of "My_results".

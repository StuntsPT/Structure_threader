# Usage
This section describes how to use *Structure_threader*.

*Structure_threader* can be executed via two main modes.

- `run`: The main execution mode that performs the parallel execution of the external structuring program, calculates the best K values and generates the plot files
- `plot`: This execution mode will only generate new plot files from the output files of the structuring program.

### `run` mode

Using the `run` mode, the program currently takes the following arguments:

* I/O arguments:
    * Input file (-i)
    * Output directory (-o)
    * Path to parameters_file (--params)
* Individual/Population identification options:
    * Path to popfile (--pop) [See below for more information]
    * Path to indfile (--ind) [See below for more information]
* Extrnal program location - you have to pass one and only one of the following arguments:
    * *STRUCTURE* location (if you want to run *STRUCTURE*; -st)
    * *fastStructure* location (if you want to run *fastStructure*; -fs)
    * *MavericK* location (if you want to run *MavericK*; -mv)
* Number of K - you have to pass one and only one of the following arguments:
    * K (To test all values of "K" from 1 to "K"; -K)
    * Klist (To test all values of "K" in the provided list; -Klist)
* Replicates (ignored for *fastStructure* and *MavericK*; -R)
* Number of threads to use (-t)
* Q-matrix plotting options:
  * Disable plot drawing (--no_plots)
  * Force plotting the given values together (--override_bestk)
  * Draw the plots only in grayscale (-bw)
* Other options                
    * Enable logging - useful when problems arise (--log)
    * Do not run the BestK tests (--no-tests)
    * Add extra arguments to pass to the wrapped program (--extra_opts) [Example: prior=logistic seed=123]


Example run:

```
structure_threader run -K Ks -R replicates -i infile -o outpath -t num_of_threads -st path_to_structure
```

Where -K is the number of "Ks" to run, -R is the number of replicate runs for
each value of "K", -i is the input file for *STRUCTURE*, -o is the directory where the output results should be stored,
-t is the number of threads to use and -p the path for the *STRUCTURE* binary.

The program should be run in the same directory where the files "mainparams" and
"extraparams" for your *STRUCTURE* run are placed. Please see [Installation](install.md) for information on how to achieve this.

### `plot` mode

Using the `plot` mode, the program currently takes the following arguments:

* Main plotting options:
    * Prefix of the structuring software output files (-i)
    * External program or format of the output files. This can be 'structure', 'fastStructure' or 'maverick'. (-f)
    * The K values that you want to plot. Each individual K value that is provided will be plotted individually and in the end, a comparative plot will all K values will also be generated. (-K; Example: -K 2 3 4)

    * Directory where the plots will be generated. By default they will be generated in the current working directory (-o)

* Individual/Population identification options:
    * Path to popfile (--pop) [See below for more information]
    * Path to indfile (--ind) [See below for more information]
* Extra plotting options:
    * Do not use colors when drawing the plots (-bw)
    * Use individual sample labels even when population labels are available (--use-ind-labels)

Example run:

```
structure_threader plot -i fS_run -f fastStructure -K 2 3 4 -o 2_4_plots --ind indfile.txt
```

Here, *Structure_threader* will search the current directory for all FastStructure output files that start with the "fS_run" string, as specified by the "-i" option. The "-f" option specified the fastStructure format of the output files. The "-K" option specified which K values should be plotted (Note: If any of the provided K values do not exist, they are ignored). Using the "-o" option the plots will be generated into the "2_4_plots" directory. Finally, we also provide an "indfile" using the "--ind" option.

## Using a "popfile"
*Structure_threader* can build your structure plots with labels and in a specified order. For that you have to provide a "popfile" (--pop option). This file consists of the following 3 columns: "Population name", "Number of individuals in the population", "Order of the population in the plot file".
Here is an example:

```
Location_1  20  1
Location_2  21  2
Location_3  11  3
```

This example file contains 3 populations, with 20, 21 and 11 individuals.
 This means that the first 20 individuals are from "Location_1", the next 21 individuals are from "Location_2" and so on.
 The numbers "1", "2" and "3" will be the order of the populations in the plot file.
If you want to draw the plot in a different order than what was provided on the input file, you have to reorder the lines. For the sake of the example, let's say that you wish to plot your data, switching the place of Locations 3 and 2. The input file would look like this:

```
Location_1  20  1
Location_3  11  3
Location_2  21  2
```

You can use any order you like using this scheme. Also note that the "split bars" that split the populations in your plot will correspond to the number provided in column 2.

## Using an "indfile"
The "indfile" works in a similar fashion to the "popfile" but discriminates each individual sample in the output file. This file can be provided with the --ind option and is particularly useful when you have no knowledge of the populations or when individuals from the same population are not clustered together in the input file.

 This file can have between one and up to three columns:

1. Individual sample name
2. Population name
3. Order of the population in the plot

Only the first column is mandatory and if you provide an "indfile" with a single column, the resulting plot will contain the individual samples as the x-axis labels. Such "indfile" could be simply:

```
Ind1
Ind2
Ind3
```

If you provide the second column with the population name, the x-axis labels of the resulting plots will only display the population names. However, the .html plots will also display the name of the individual sample names when hovering the mouse over their respective bars. An example of a two column "indfile":

 ```
Ind1    PopA
Ind2    PopB
Ind3    PopA
```

The third column will simply allow you to change the order of the populations in the generated plots. In this example:

 ```
Ind1    PopA    2
Ind2    PopB    1
Ind3    PopA    2
```

The individuals of "PopB" will appear first, and then the individuals of "PopA".

## fastStrucutre Warning:
Keep in mind that *fastStructure* can take input in two distinct file formats:
[Plink](http://pngu.mgh.harvard.edu/%7Epurcell/plink/data.shtml) and
[structure](http://web.stanford.edu/group/pritchardlab/software/structure-data_v.2.3.1.html).
In order to use the PLINK format, three files are required:

* `file.bed`
* `file.fam`
* `file.bim`

You can enter any of them (but just one oof them) as the input file and
*Structure_threader* will assume the other two exist in the same path.
If the input file specified by the *-i* switch in *Structure_threader* has an
extension different from either of the three mentioned above, *Structure_threader* will assume th input is in the STRUCTURE format, which has some peculiarities:
*fastStructure* requires your input file to have each individual represented in
two rows (one for each allele), and six "bogus" columns before the actual data.
**No Header is allowed**. Here is a short example:

```
Ind1    col1  col2  col3  col4  col5 1    3   1   4
Ind1    col1  col2  col3  col4  col5 1    3   2   4
Ind2    col1  col2  col3  col4  col5 1    2   1   4
Ind2    col1  col2  col3  col4  col5 1    2   1   3

```

Don't forget to look at the [Output section](output.md) for information on how the data is presented after a successful (or not) run.


## Using *MavericK*:
*MavericK* is exhaustively documented. You can find the full manual [here](http://www.bobverity.com/home/maverick/additional-files/), along with other useful material to make the most of the software.

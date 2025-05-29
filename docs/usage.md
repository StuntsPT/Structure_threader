# Usage
This section describes how to use *Structure_threader*.

*Structure_threader* can be executed via two main modes.

- `run`: The main execution mode that performs the parallel execution of the external structuring program, calculates the best K values (ALStructure currently does not support finding the best K) and generates the plot files
- `plot`: This execution mode will only generate new plot files from the output files of the structuring program.

### `run` mode

Using the `run` mode, the program currently takes the following arguments:

* I/O arguments:
    * Input file (-i)
    * Output directory (-o)
    * Path to parameters_file (`mainparams` for STRUCTURE [will assume `extraparams` exists in the same directory] or `parameters.txt` for MavericK; --params)
* Individual/Population identification options:
    * Path to popfile (--pop) [See below for more information]
    * Path to indfile (--ind) [See below for more information]
* External program location - you have to pass one and only one of the following arguments:
    * *STRUCTURE* location (if you want to run *STRUCTURE*; -st)
    * *fastStructure* location (if you want to run *fastStructure*; -fs)
    * *MavericK* location (if you want to run *MavericK*; -mv)
    * *ALStructure_wrapper.R* location (if you want to run *ALStructure*; -als)
    * *Neural ADMIXTURE* location (if you want to run *Neural ADMIXTURE*; -nad)
* Number of K - you have to pass one and only one of the following arguments:
    * K (To test all values of "K" from 1 to "K"; -K)
    * Klist (To test all values of "K" in the provided list; -Klist)
* Replicates (ignored for *fastStructure*, *MavericK*, *ALStructure* and *Neural ADMIXTURE*; -R)
* Number of threads to use (-t)
* Q-matrix plotting options:
  * Disable plot drawing (--no_plots)
  * Force plotting the given values together (--override_bestk)
  * Draw the plots only in grayscale (-bw)
* Other options
    * Enable logging - useful when problems arise (--log)
    * Do not run the BestK tests (--no-tests)
    * Do not run the Clumppling analysis (--no-clumpp)
    * Add extra arguments to pass to the wrapped program (--extra_opts) [Example: prior=logistic seed=123]
    * Define a random seed starting value (--seed) [default:1235813]
    * Neural ADMIXTURE exclusive options:
        * Number of CPUs to use (--nad_cpus)
        * Number of GPUs to use (--nad_gpus)
        * Initialization method (--init)
        * Execution method (--exec_mode) [default: train]
        * Seed (--nad_seed) [default: 42]
        * If the run is supervised (--supervised) [default: False]
        * Single-column population file (--nad_pop)


Example run:

```
structure_threader run -K Ks -R replicates -i infile -o outpath -t num_of_threads -st path_to_structure_binary
```

Where `-K` is the number of "Ks" to run, `-R` is the number of replicate runs for
each value of "K", `-i` is the input file for *STRUCTURE*, `-o` is the directory where the output results should be stored,
`-t` is the number of threads to use, `-st` the path for the *STRUCTURE* binary.

The program should be run in the same directory where the files "mainparams" and
"extraparams" for your *STRUCTURE* run are placed. Please see [Installation](install.md) for information on how to achieve this.
Alternatively, you can specify the path to a `mainparams` (or `parameters.txt if wrapping *MavericK*) file. *Structure_threader* will look for an `extraparams` file in the same location and pass all read parameters to the wrapped program. This can be achieved using the `--params` switch.

### `plot` mode

Using the `plot` mode, the program currently takes the following arguments:

* Main plotting options:
    * Directory where the Qmatrix files you want to plot are located. In the case of MavericK point to where the directories named `mav_KX` are located (-i)
    * External program or format of the output files. This can be 'structure', 'fastStructure' or 'maverick'. (-f)
    * The K values that you want to plot. Each individual K value that is provided will be plotted individually and in the end, a comparative plot will all K values will also be generated. (-K; Example: -K 2 3 4)

    * Directory where the plots will be saved to. By default they will be generated in the current working directory (-o)

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

Here, *Structure_threader* will search the current directory for all FastStructure output files that start with the "fS_run" string, as specified by the "-i" option. The "-f" option specified the fastStructure format of the output files. The "-K" option specified which K values should be plotted (Note: If any of the provided K values do not exist, they are ignored). Using the "-o" option the plots will be generated into the "2_4_plots" directory. Finally, we also provide an `indfile` using the "--ind" option.

### `params` mode

Using the `params` mode, *Structure_threader* generate a skeleton `mainparams` and `extraparams` that you should edit to facilitate *STRUCTURE* runs. Most options have been preset to a commonly used default value, but some of them are set to "CHANGEME" since providing a default value here makes no sense, since it depends on each dataset.
The `params` mode takes only one option:

* Output directory (path to where the skeleton parameter files should be written; -o)

## Using a `popfile`
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

**Please note that this `popfile` is different from the one expected by Neural ADMIXTURE, and so if you wish to use a single-column `popfile` with Neural ADMIXTURE, we provide a separate option (`--nad_pop`).**

## Using an `indfile`
The `indfile` works in a similar fashion to the `popfile` but discriminates each individual sample in the output file. This file can be provided with the --ind option and is particularly useful when you have no knowledge of the populations or when individuals from the same population are not clustered together in the input file.

 This file can have between one and up to three columns:

1. Individual sample name
2. Population name
3. Order of the population in the plot

Only the first column is mandatory and if you provide an `indfile` with a single column, the resulting plot will contain the individual samples as the x-axis labels. Such `indfile` could be simply:

```
Ind1
Ind2
Ind3
```

**NOTE: this WILL NOT RE-ORDER the columns in your plot - this will simply CHANGE THE INDIVIDUAL LABELS! In order to avoid problems, TRIPLE CHECK that the `indfile` order is the same as in your original input file.**

If you provide the second column with the population name, the x-axis labels of the resulting plots will only display the population names. However, the .html plots will also display the name of the individual sample names when hovering the mouse over their respective bars. An example of a two column `indfile`:

```
Ind1    PopA
Ind2    PopB
Ind3    PopA
```

**Like previously, this option will also not reorder the plot columns! It simply changes the labels.**


Adding a third column will allow you to change the order of **the populations** in the generated plots. In this example:

```
Ind1    PopA    2
Ind2    PopB    1
Ind3    PopA    2
```

The individuals of "PopB" will appear first, and then the individuals of "PopA".

**Note:** While `popfiles` and `indfiles` are a simple and convenient way to **change the population order**, they are not meant to change **individual order** (albeit individuals will be moved in the plot when population order changes) in the plot. If you are not happy with the individual order in your plot, the best way to change it is in the input file. I can implement a "plot order changer" routine if there is enough demand for it, though (you can provide feedback by commenting on the issue either on [gitlab](https://gitlab.com/StuntsPT/Structure_threader/-/issues/93) or [github](https://github.com/StuntsPT/Structure_threader/issues/91)). 

## fastStructure Warning
Keep in mind that *fastStructure* can take input in two distinct file formats:
[PLINK](https://www.cog-genomics.org/plink/1.9/input) and
[STRUCTURE](https://web.stanford.edu/group/pritchardlab/software/structure-data_v.2.3.1.html).
In order to use the PLINK format, three files are required:

* `file.bed`
* `file.fam`
* `file.bim`

You can enter any of them (but just one of them) as the input file and
*Structure_threader* will assume the other two exist in the same path.
If the input file specified by the *-i* switch in *Structure_threader* has an
extension different from either of the three mentioned above, *Structure_threader* will assume the input is in the STRUCTURE format, which has some peculiarities:
*fastStructure* requires your input file to have each individual represented in
two rows (one for each allele), and six "bogus" columns before the actual data.
**No Header is allowed**. Here is a short example:

```
Ind1    col1  col2  col3  col4  col5 1    3   1   4
Ind1    col1  col2  col3  col4  col5 1    3   2   4
Ind2    col1  col2  col3  col4  col5 1    2   1   4
Ind2    col1  col2  col3  col4  col5 1    2   1   3

```

## ALStructure Warning
Keep in mind that *ALStructure* can take input in two distinct file formats:
[PLINK](https://www.cog-genomics.org/plink/1.9/input) and
[VCF](https://samtools.github.io/hts-specs/VCFv4.2.pdf).
In order to use the PLINK format, three files are required:

* `file.bed`
* `file.fam`
* `file.bim`

You can enter any of them (but just one of them) as the input file and
*Structure_threader* will assume the other two exist in the same path.

In order to use a `VCF` formatted file, it is only required that you point at it with the `-i` switch. Note that when using this format, *Structure_threader* will create a new file, with the same name and in the same PATH as your `VCF` file, but with a `.tsv` extension, which is ready to be parsed by *ALStructure*.

Don't forget to look at the [Output section](output.md) for information on how the data is presented after a successful (or not) run.


## Neural ADMIXTURE Warning
Keep in mind that *Neural ADMIXTURE* can take input in four distinct file formats:
[PLINK](https://www.cog-genomics.org/plink/1.9/input),
[PLINK 2](https://www.cog-genomics.org/plink/2.0/formats),
[VCF](https://samtools.github.io/hts-specs/VCFv4.2.pdf) and
[HDF5](https://www.hdfgroup.org/solutions/hdf5/).
In order to use the PLINK format, the following three files are required:

* `file.bed`
* `file.fam`
* `file.bim`

In order to use the PLINK 2 format, the following three files are required:

* `file.pgen`
* `file.psam`
* `file.pvar`

It's recommended to use the *\.bed* or the *\.pgen* files as the input
file for Neural ADMIXTURE and *Structure_threader* will assume the
other two exist in the same path.


## Using *MavericK*
*MavericK* is thoroughly documented. Although the original website is no longer accessible, you can find the paper in which it was originally mentioned [here](https://doi.org/10.1534/genetics.115.180992). The documentation is available under "Supplementary data" as "FileS2" (PDF format).

# Usage
This section describes how to use *Structure_threader*.

*Structure_threader* is driven by [Snakemake](https://snakemake.readthedocs.io/) under the hood. All wrapped programs run inside [Apptainer/Singularity](https://apptainer.org/) containers by default, so no manual installation of the external programs is required. Container images are pulled automatically the first time each program is used.

*Structure_threader* can be executed via three main modes.

- `run`: The main execution mode. Orchestrates the parallel execution of the external structuring program, calculates the best K values (where applicable) and generates plot files.
- `plot`: Generates new plot files from existing output files of the structuring program, without re-running the analysis.
- `params`: Generates skeleton `mainparams` and `extraparams` files for use with *Structure*.

### Container mode

By default, *Structure_threader* detects whether Apptainer or Singularity is installed and enables container mode automatically. To opt out and use locally installed binaries instead, pass `--no-container`. You can also pass the path to a specific binary after the wrapper flag when using `--no-container` (e.g. `-st /usr/local/bin/structure --no-container`).

If no container runtime is found and `--no-container` is not set, *Structure_threader* will fall back to using locally installed binaries and print a warning.

### `run` mode

Using the `run` mode, the program currently takes the following arguments:

* I/O arguments:
    * Input file (`-i`)
    * Output directory (`-o`)
    * Path to parameters file (`mainparams` for *Structure* [will assume `extraparams` exists in the same directory] or `parameters.txt` for *MavericK*; `--params`)
* Individual/Population identification options:
    * Path to popfile (`--pop`) [See below for more information]
    * Path to indfile (`--ind`) [See below for more information]
* External program selection — you have to pass one and only one of the following arguments:
    * Run *Structure* (`-st`). Optionally follow with a binary path for `--no-container` mode.
    * Run *fastStructure* (`-fs`). Optionally follow with a binary path for `--no-container` mode.
    * Run *MavericK* (`-mv`). Optionally follow with a binary path for `--no-container` mode.
    * Run *ALStructure* (`-als`). Optionally follow with an Rscript path for `--no-container` mode.
    * Run *Neural ADMIXTURE* (`-nad`). Optionally follow with a binary path for `--no-container` mode.
* Number of K — you have to pass one and only one of the following arguments:
    * `-K` (to test all values of K from 1 to K)
    * `-Klist` (to test all values of K in the provided list; e.g. `-Klist 2 3 5`)
* Replicates (ignored for *fastStructure*, *MavericK*, *ALStructure* and *Neural ADMIXTURE*; `-R`)
* Number of threads / parallel jobs (`-t`)
* Q-matrix plotting options:
    * Disable plot drawing (`--no_plots`)
    * Draw the plots only in greyscale (`-bw`)
    * Use individual sample labels even when population labels are available (`--use-ind-labels`)
* Other options:
    * Do not run the bestK tests (`--no-tests`)
    * Do not run the Clumppling alignment (`--no-clumpp`)
    * Add extra arguments to pass to the wrapped program verbatim (`--extra_opts`)
    * Define a random seed (`--seed`) [default: 1235813]
    * Container and Snakemake options:
        * Disable containers and use local binaries (`--no-container`)
        * Force use of Singularity/Apptainer containers (`--use-singularity`)
        * Pass extra arguments to Snakemake verbatim (`--snakemake-args`)
        * Override the Snakefile path (`--snakefile`)
        * Override container image URIs for individual programs (`--structure-image`, `--faststructure-image`, `--maverick-image`, `--alstructure-image`, `--neuraladmixture-image`, `--clumppling-image`)
    * Clumppling alignment options:
        * Plot type for the alignment graph (`--clumppling_plot_type`) [default: graph]
        * Figure format (`--clumppling_fig_format`) [default: svg]
        * Community detection method (`--clumppling_cd_method`) [default: louvain]
        * Community detection resolution (`--clumppling_cd_res`) [default: 1.0]
    * *Neural ADMIXTURE* exclusive options:
        * Number of GPUs to use (`--nad_gpus`) [default: 0, CPU only]
        * Number of threads for Neural ADMIXTURE (`--nad_threads`) [default: 1]
        * Initialization method (`--init`)
        * Execution mode (`--exec_mode`) [default: train]
        * Seed (`--nad_seed`) [default: 1235813]
        * Run in supervised mode (`--supervised`) [default: False]
        * Single-column population file for supervised mode (`--nad_pop`)


Example run:

```
structure_threader run -K 6 -R 10 -i infile.str -o outpath -t 4 -st
```

Where `-K` is the maximum K to test, `-R` is the number of replicate runs for
each value of K, `-i` is the input file, `-o` is the directory where the output results should be stored,
`-t` is the number of parallel jobs to use, and `-st` selects *Structure* as the wrapped program.

Since container mode is the default, the above command will pull the *Structure* container image automatically if it is not already cached. To use a locally installed *Structure* binary instead:

```
structure_threader run -K 6 -R 10 -i infile.str -o outpath -t 4 -st /usr/local/bin/structure --no-container
```

The program should be run in the same directory where the files "mainparams" and
"extraparams" for your *Structure* run are placed. Please see [Installation](install.md) for information on how to achieve this.
Alternatively, you can specify the path to a `mainparams` (or `parameters.txt` if wrapping *MavericK*) file using the `--params` switch. *Structure_threader* will look for an `extraparams` file in the same location and pass all read parameters to the wrapped program.

### `plot` mode

Using the `plot` mode, the program currently takes the following arguments:

* Main plotting options:
    * Directory where the Q-matrix files you want to plot are located. In the case of *MavericK*, point to where the directories named `mav_KX` are located (`-i`)
    * External program or format of the output files. This can be `structure`, `faststructure`, `maverick`, `alstructure` or `neuraladmixture`. (`-f`)
    * The K values that you want to plot. Each individual K value that is provided will be plotted individually and in the end, a comparative plot with all K values will also be generated. (`-K`; example: `-K 2 3 4`)
    * Directory where the plots will be saved to. By default they will be generated in the current working directory (`-o`)

* Individual/Population identification options:
    * Path to popfile (`--pop`) [See below for more information]
    * Path to indfile (`--ind`) [See below for more information]
* Extra plotting options:
    * Do not use colours when drawing the plots (`-bw`)
    * Use individual sample labels even when population labels are available (`--use-ind-labels`)

Example run:

```
structure_threader plot -i fS_run -f faststructure -K 2 3 4 -o 2_4_plots --ind indfile.txt
```

Here, *Structure_threader* will search the directory specified by `-i` for all fastStructure output files. The `-f` option specifies the fastStructure format. The `-K` option specifies which K values should be plotted (Note: if any of the provided K values do not exist, they are ignored). Using the `-o` option, the plots will be generated into the "2_4_plots" directory. Finally, we also provide an `indfile` using the `--ind` option.

### `params` mode

Using the `params` mode, *Structure_threader* generates a skeleton `mainparams` and `extraparams` that you should edit to facilitate *Structure* runs. Most options have been preset to a commonly used default value, but some of them are set to "CHANGEME" since providing a default value here makes no sense as it depends on each dataset.
The `params` mode takes only one option:

* Output directory (path to where the skeleton parameter files should be written; `-o`)

## Using a `popfile`
*Structure_threader* can build your structure plots with labels and in a specified order. For that you have to provide a "popfile" (`--pop` option). This file consists of the following 3 columns: "Population name", "Number of individuals in the population", "Order of the population in the plot file".
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

**Please note that this `popfile` is different from the one expected by *Neural ADMIXTURE*, and so if you wish to use a single-column `popfile` with *Neural ADMIXTURE*, we provide a separate option (`--nad_pop`).**

## Using an `indfile`
The `indfile` works in a similar fashion to the `popfile` but discriminates each individual sample in the output file. This file can be provided with the `--ind` option and is particularly useful when you have no knowledge of the populations or when individuals from the same population are not clustered together in the input file.

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

**NOTE: this WILL NOT RE-ORDER the columns in your plot — this will simply CHANGE THE INDIVIDUAL LABELS! In order to avoid problems, TRIPLE CHECK that the `indfile` order is the same as in your original input file.**

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

**Note:** While `popfiles` and `indfiles` are a simple and convenient way to **change the population order**, they are not meant to change **individual order** (albeit individuals will be moved in the plot when population order changes) in the plot. If you are not happy with the individual order in your plot, the best way to change it is in the input file.

## fastStructure Warning
Keep in mind that *fastStructure* can take input in two distinct file formats:
[PLINK](https://www.cog-genomics.org/plink/1.9/input) and
[Structure](https://web.stanford.edu/group/pritchardlab/software/structure-data_v.2.3.1.html).
In order to use the PLINK format, three files are required:

* `file.bed`
* `file.fam`
* `file.bim`

You can enter any of them (but just one of them) as the input file and
*Structure_threader* will assume the other two exist in the same path.
If the input file specified by the `-i` switch in *Structure_threader* has an
extension different from either of the three mentioned above, *Structure_threader* will assume the input is in the Structure format, which has some peculiarities:
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

In order to use a `VCF` formatted file, it is only required that you point at it with the `-i` switch. Note that when using this format, *Structure_threader* will create a new file, with the same name and in the same path as your `VCF` file, but with a `.tsv` extension, which is ready to be parsed by *ALStructure*. This temporary file is automatically removed after the run completes.

Don't forget to look at the [Output section](output.md) for information on how the data is presented after a successful (or not) run.


## Neural ADMIXTURE Warning
Keep in mind that *Neural ADMIXTURE* can take input in three distinct file formats:
[PLINK](https://www.cog-genomics.org/plink/1.9/input),
[PLINK 2](https://www.cog-genomics.org/plink/2.0/formats) and
[VCF](https://samtools.github.io/hts-specs/VCFv4.2.pdf).
In order to use the PLINK format, the following three files are required:

* `file.bed`
* `file.fam`
* `file.bim`

In order to use the PLINK 2 format, the following three files are required:

* `file.pgen`
* `file.psam`
* `file.pvar`

It's recommended to use the `*.bed` file as the input for *Neural ADMIXTURE* and *Structure_threader* will assume the other two exist in the same path. Point *Structure_threader* at any one of the three files.

**Note:** `.pgen` support depends on a bug fix that is pending in the upstream *Neural ADMIXTURE* package. Until that fix is released, please use `.bed` input with *Neural ADMIXTURE*.


## Using *MavericK*
*MavericK* is thoroughly documented. Although the original website is no longer accessible, you can find the paper in which it was originally mentioned [here](https://doi.org/10.1534/genetics.115.180992). The documentation is available under "Supplementary data" as "FileS2" (PDF format).

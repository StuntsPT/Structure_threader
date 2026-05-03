# *Structure_threader*

## Description

A program to parallelize and automate the runs of [Structure](http://web.stanford.edu/group/pritchardlab/structure.html), [fastStructure](https://rajanil.github.io/fastStructure/), [MavericK](http://www.bobverity.com/home/maverick/what-is-maverick/), [ALStructure](https://github.com/StoreyLab/alstructure) and [Neural ADMIXTURE](https://github.com/AI-sandbox/neural-admixture) software.

As of version 2.1.0, *Structure_threader* is built on [Snakemake](https://snakemake.readthedocs.io/) and runs all wrapped programs inside [Apptainer/Singularity](https://apptainer.org/) containers by default. This means that no manual installation of the wrapped programs is required: *Structure_threader* will pull the appropriate container image automatically the first time each program is run.


## Requirements

Python 3.11 or later. Python 3.13 is supported.  
[Snakemake](https://snakemake.readthedocs.io/) ≥ 9.14.4 (installed automatically as a dependency).  
[Apptainer](https://apptainer.org/) or [Singularity](https://sylabs.io/) is required to use the default container mode. If neither is available, *Structure_threader* will fall back to using locally installed binaries automatically, or you can pass `--no-container` to opt out of containers explicitly.  
In order to draw the plots, matplotlib ≥ 1.4 is required (installed automatically as a dependency when installed via `conda` and `pip`).  
To run "fastChooseK.py" (fastStructure wrapper only), numpy is also required (installed automatically as a dependency when installed via `conda` and `pip`).  
In order to use *ALStructure*, you need to have [R](https://www.r-project.org/) installed too (installed automatically as a dependency only when installed via `conda`).

Neural ADMIXTURE has to be manually installed using `pip` for the `conda` version.

## Where to get it

* Source code - [Structure_threader on GitLab](https://gitlab.com/StuntsPT/Structure_threader)
* Source code - [Structure_threader on GitHub](https://github.com/StuntsPT/Structure_threader)
* Source distribution with all dependencies (except Neural ADMIXTURE) - [Structure_threader on Bioconda](https://bioconda.github.io/recipes/structure_threader/README.html)
* Source distribution - [Structure_threader on PyPI](https://pypi.org/project/structure_threader/)


## Contents

* [Installation & dependencies](install.md)
* [Usage](usage.md)
* [Output](output.md)
* [Test Data](test_data.md)
* [Benchmarking](benchmark.md)
* [Citation](citation.md)
* [Future Plans](future.md)
* [FAQ](faq.md)


## A word of caution

*Structure_threader* can be quite useful in automating and speeding up your analyses, however, in order to use it effectively you **really** should learn and understand how the wrapped programs work. It is **highly** recommended that you first learn to use the wrapped programs in their default implementations. And by "learning", we don't just mean "I know how to make it run.", but rather "I understand what each of the chosen parameters does, and why I selected each of them."
The paper [An overview of STRUCTURE: applications, parameter settings, and supporting software](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3665925/) is an excellent guide for understanding the parameterization of *Structure*.
We do not know of a good "tutorial" for learning about *fastStructure*, and as such, the [original research paper](http://www.genetics.org/content/197/2/573) (paywalled), albeit a bit dense, is still the best place to learn about it.
The documentation for *MavericK*, for instance, is quite comprehensive and a great resource to learn to use *MavericK* and consequently about the importance of proper MCMC chain mixing. Although the original website is no longer accessible, you can find the paper in which it was originally mentioned [here](https://doi.org/10.1534/genetics.115.180992). The documentation is available under "Supplementary data" as "FileS2" (PDF format).

## Other works

The script "fastChooseK.py" was taken from [the original fastStructure repository](https://github.com/rajanil/fastStructure), ported to Python 3, largely modified to work as a module for the main script and re-licensed as GPLv3.

The scripts "harvesterCore.py" and "structureHarvester.py" were taken from [the original structureHarverster repository](https://github.com/dentearl/structureHarvester), ported to Python 3, and slightly modified to work as a module for the main script. Please see the "Citation" part of the README to know what to cite, should you use this module.


## Bug reporting

Found a bug or would like a feature added? Or maybe drop some feedback?
Just [open a new issue on GitLab](https://gitlab.com/StuntsPT/Structure_threader/issues/new) [or on GitHub](https://github.com/StuntsPT/Structure_threader/issues/new).


## License

This project is licensed under the [GNU General Public License, version 3](https://gitlab.com/StuntsPT/Structure_threader/-/raw/master/LICENSE).

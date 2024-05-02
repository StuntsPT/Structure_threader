# *Structure_threader*

## Description

A program to parallelize and automate the runs of [Structure](http://web.stanford.edu/group/pritchardlab/structure.html), [fastStructure](https://rajanil.github.io/fastStructure/), [MavericK](http://www.bobverity.com/home/maverick/what-is-maverick/) and [ALStructure](https://github.com/StoreyLab/alstructure) software.


## Requirements

Python 3. The main program only uses modules from the standard library.  
In order to draw the plots, matplotlib >= 1.4 is required (installed automatically as a dependency when installed via `pip`).  
To run "fastChooseK.py" (fastStructure wrapper only), numpy is also required (installed automatically as a dependency when installed via `pip`).  
In order to use "ALStructure", you need to have [R](https://www.r-project.org/) installed too (must be installed manually, as `pip` can't handle installing R or dependencies).


## Where to get it

* Source code - [Structure_threader on gitlab](https://gitlab.com/StuntsPT/Structure_threader)
* Source code - [Structure_threader on github](https://github.com/StuntsPT/Structure_threader)
* Source distribution with platform binaries for wrapped programs - [Sturcture_threader on Pypi](https://pypi.python.org/pypi/structure_threader/)
    * You can easily install *Structure_threader* by issuing the command `pip3 install structure_threader`


## Contents

* [Installation & dependencies](install.md)
    * [Binary building](binaries.md)
* [Usage](usage.md)
* [Output](output.md)
* [Test Data](test_data.md)
* [Benchmarking](benchmark.md)
* [Citation](citation.md)
* [Future Plans](future.md)
* [FAQ](faq.md)


## A word of caution

*Structure_threader* can be quite useful in automating and speeding up your analyses, however, in order to use it effectively you **really** should learn and understand how the wrapped programs work. It is **highly** recommended that you first learn to use the wrapped programs in their default implementations. And by "learning", we don't just mean "I know how to make it run.", but rather "I understand what each of the chosen parameters does, and why I selected each of them.".
The paper [An overview of STRUCTURE: applications, parameter settings, and supporting software](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3665925/) is an excellent guide for understanding the parameterization of *STRUCTURE*.
We do not know of a good "tutorial" for learning about *fastStructure*, and as such, the [original research paper](http://www.genetics.org/content/197/2/573) (paywalled), albeit a bit dense, is still the best place to learn about it.
The [documentation for *MavericK*](http://www.bobverity.com/home/maverick/additional-files/), for instance, is quite comprehensive and a great resource to learn to use *MavericK* and consequently about the importance of proper MCMC chain mixing.


## Other works

The script "fastChooseK.py" was taken from [the original fastStructure repository](https://github.com/rajanil/fastStructure), ported to python 3, largely modified to work as a module for the main script and re-licensed as GPLv3.

The scripts "harvesterCore.py" and "structureHarvester.py" were taken from [the original structureHarverster repository](https://github.com/dentearl/structureHarvester), ported to python 3, and slightly modified to work as a module for the main script. Please see the "Citation" part of the README to know what to cite, should you use this module.

Binaries for [fastStructure](https://github.com/rajanil/fastStructure), [STRUCTURE](http://web.stanford.edu/group/pritchardlab/structure.html) and [MavericK](https://github.com/bobverity/MavericK) are distributed in the pypi hosted version.


## Bug reporting

Found a bug or would like a feature added? Or maybe drop some feedback?
Just [open a new issue on gitlab](https://gitlab.com/StuntsPT/Structure_threader/issues/new) [or on github](https://github.com/StuntsPT/Structure_threader/issues/new).


## License

GPLv3

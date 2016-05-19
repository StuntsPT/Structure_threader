# *Structure_threader*

## Description
A program to parallelize and automate the runs of [Structure](http://pritchardlab.stanford.edu/structure.html) and [fastStructure](https://rajanil.github.io/fastStructure/) software.


## Requirements
Python 3. The main program only uses modules from the standard library.
In order to draw the plots, matplotlib >= 1.4 is required.
To run "fastChooseK.py" (fastStructure wrapper only), numpy is also required.

*Structure_threader* **might** also work with python2, however, this is not as tested as the python3 version (actually its hardly tested at all). During our limited testing, running in python3 yields ~11% speed gains relatively to python2 (although this testing was limited).


## Where to get it
* Source code - [Structure_threader on github](https://github.com/StuntsPT/Structure_threader)


## Contents
* [Installation & dependencies](install.md)
* [Usage](usage.md)
* [Output](output.md)
* [Test Data](test_data.md)
* [Benchmarking](benckmark.md)
* [Citation](citation.md)
* [FAQ](faq.md)


## Other works
The script "fastChooseK.py" was taken from [the original fastStructure repository](https://github.com/rajanil/fastStructure), ported to python 3, largely modified to work as a module for the main script and relicensed as GPLv3.

The scripts "harvesterCore.py" and "structureHarvester.py" were taken from [the original structureHarverster repository](https://github.com/dentearl/structureHarvester), ported to python 3, and slightly modified to work as a module for the main script. Please see the "Citation" part of the README to know what to cite, should you use this module.


## Bug reporting
Found a bug or would like a feature added? Or maybe drop some feedback?
Just [open a new issue](https://github.com/StuntsPT/Structure_threader/issues/new).


## License
GPLv3

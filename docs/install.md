# Installation
In order to install *Structure_threader* just clone the repository (or download one of the releases), and place the contents, respecting the directory structure in your $PATH.
Alternatively, you can also place the entire program root directory somewhere, and call it from your current dir using the full path.

You can go the the ["helper_scripts" directory](https://github.com/StuntsPT/Structure_threader/tree/master/helper_scripts) where you will find some scripts to help you install both *Structure* and *fastStructure*.


## Structure_threader helper scripts
The directory "helper_scripts" contains two scripts that will install structure and faststructre, respectively in a *semi* automatic way.

Both scripts default the programs' install locations to ~/Software/<program_name>. You can change this in the scripts themselves should you wish to change this location.


### install_structure.sh
This script will download and install structure.


#### Requirements:
* a C compiler, such as GCC, with fortran support.
* Cmake is required to build LAPACK

In every HPC this should be available.

In Ubuntu, all you should need is the package "build-essential" (if it is not already installed for some reason). In other distros, the package name should be similar. It can be installed like this:

```
sudo apt-get install build-essential
```


### install_faststructure.sh
This script will download and install faststructure and its dependencies.

Faststructure depends on quite a few software packages:
* cython
* numpy
* scipy
* GNU scientific library

If these are already installed in your system, feel free to comment the script section that will install them. Otherwise it will install a new local copy of these programs. Otherwise, you can install them in ubuntu with the following command:

```
sudo apt-get install cython python-numpy python-scipy gsl-bin
```

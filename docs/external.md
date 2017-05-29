# Manually installing external programs

If you wish to compile your own binaries for these programs, you may wish to
rely on our
["helper_scripts"](https://github.com/StuntsPT/Structure_threader/tree/master/helper_scripts)
which contain commands to compile and install *MavericK*, *Structure* **and**
*fastStructure* (along with any required dependencies). For more details check
the next few sections.

## Structure_threader helper scripts
The directory "helper_scripts" contains three scripts that will install *STRUCTURE*, *fastStructre* and *MavericK* respectively in a *semi* automatic way.

All scripts default the programs' install locations to ~/Software/<program_name>. You can change this in the scripts themselves should you wish to change this location.


### install_structure.sh
This script will download and install STRUCTURE.


#### Requirements:
* a C compiler, such as GCC, with fortran support.
* Cmake is required to build LAPACK

This should be available in every HPC environment.

In Ubuntu, all you should need is the package "build-essential" (if it is not
already installed for some reason). It can be installed like this:

```
sudo apt-get install build-essential
```

In other distros, the package name should be similar.

### install_faststructure.sh
This script will download and install fastStructure and its dependencies.

fastStructure depends on quite a few software packages:
* cython
* numpy
* scipy
* GNU scientific library

If these are already installed in your system, feel free to comment the script
section that will install them. Otherwise it will install a new local copy of
these programs. You can install these packages in Ubuntu with the following
command:

```
sudo apt-get install cython python-numpy python-scipy gsl-bin
```

### Important note:
If you are relying on the GNU Scientific Library that was installed using the
`install_faststructure` script, you will need to make your system aware of
where these libraries are.
for that, add the following to your `~/.bashrc`:

```bash
LD_LIBRARY_PATH=$install_dir/lib
export LD_LIBRARY_PATH
```

Where `$install_dir` is the directory defined in `install_faststructure.sh`.


### install_maverick.sh
This script will download, compile and install MavericK.


#### Requirements:
* a recent C compiler, such as GCC 6.1 and above.

This should be available in every HPC environment.

In Ubuntu, all you should need is the package "build-essential" (if it is not
already installed for some reason). It can be installed like this:

```
sudo apt-get install build-essential
```

In other distros, the package name should be similar.

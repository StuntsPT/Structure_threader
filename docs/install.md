# Installation

## Preferred method

Since v0.1.8 *Structure_threader* is available in
[Pypi](https://pypi.python.org/pypi/structure_threader/), which means that
currently, installing *Structure_threader* is as simple as running
`pip3 install structure_threader`. Don't forget the `--user` option if you can't
or don't want to install the program as `root` user.

## Alternative methods

You can also run *Structure_threader* by simply cloning the repository (or
downloading one of the releases), and placing the contents of the directory
"structure_threader", on any location on your `$PATH` env var.

Another alternative, that can be used since version 0.1.6 is the `setup.py`
method. This can be used either by running `python3 setup.py install` (or even
better, `pip3 install .`) from the distribution's root directory (where
`setup.py` is located).

Please note that while dependencies like numpy and matplotlib are handled by
this method, the preferred method for installing via Pypi will also install
binary versions of STRUCTURE, fastStructure and MavericK for your platform.
These binaries are installed in the "standard" `setup.py`
[locations](https://docs.python.org/2/install/), eg. `/usr/bin/` if installed
with `sudo` or `~/.local/bin/` if installed with the option `--user`, etc...

If you wish to compile your own binaries for these programs, you may wish to
rely on our
["helper_scripts"](https://github.com/StuntsPT/Structure_threader/tree/master/helper_scripts)
which contain commands to compile and install *MavericK*, *Structure* **and**
*fastStructure* (along with any required dependencies). For more details check
the next few sections.


## Structure_threader helper scripts

The directory "helper_scripts" contains two scripts that will install STRUCTURE and fastStructre, respectively in a *semi* automatic way.

Both scripts default the programs' install locations to ~/Software/<program_name>. You can change this in the scripts themselves should you wish to change this location.


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

###Important note:

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

This script will download and install MavericK.


#### Requirements:
* a recent C compiler, such as GCC 6.1 and above.

This should be available in every HPC environment.

In Ubuntu, all you should need is the package "build-essential" (if it is not
already installed for some reason). It can be installed like this:

```
sudo apt-get install build-essential
```

In other distros, the package name should be similar.

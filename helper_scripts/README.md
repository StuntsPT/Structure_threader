#Structure_threader helper scripts

This dir contains two scripts that will install structure and faststructre, respectively in a semi automatic way.

Both scripts default the programs' install locations to ~/Software/<program_name>. You can change this in the scripts themselves should you wish to change this location.

##install_structure.sh

This script will download and install structure.

###Requirements:

* a C compiler, such as GCC, with fortran support.
* Cmake is required to build LAPACK

In every HPC this should be available.

In Ubuntu, all you should need is the package "build-essential" (if it is not already installed for some reason). In other distros, the package name should be similar.

##install_faststructure.sh

This script will download and install faststructure and its dependencies.

Faststructure depends on a few software packages:
* cython
* numpy
* scipy
* GNU scientific library

If these are already installed in your system, feel free to comment the script section that will install them. Otherwise it will install a new local copy of these programs.

###Important note:

If you are relying on the GNU Scientific Library that was locally installed, you will need to make your system aware of where these libraries are.
for that, add the following to your `~/.bashrc`:

```bash
LD_LIBRARY_PATH=$install_dir/lib
export LD_LIBRARY_PATH
```

Where `$install_dir` is the directory defined in `install_faststructure`.

##License

GPL V3

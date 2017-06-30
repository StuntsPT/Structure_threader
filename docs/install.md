# Installation
Due to the way different Operating Systems handle dependencies specific instructions for the preferred installation method are provided for each of the most used OS's "GNU/Linux", "MacOS" and "Windows".

## Preferred method, by platform

### GNU/Linux

1. Install python 3. Although python 3 is already installed by default in most modern Linux distributions, sometimes it may not be available (you can type `python3 --version` from a terminal to see if python 3 is installed. If it is, you will have something similar to `Python 3.6.1` printed on your terminal, if it isn't you will either see a "command not found" error, or a helpful message on how to install python 3). In "Debian based" distributions (such as Ubuntu) you can install python 3 by opening a terminal an running the command `sudo apt-get install python3`. In other Linux distributions you can similarly use your package manger to install it. If you do not have administration privileges in your environment, please ask your sysadmin to install python 3 for you. This is the only step that has a hard requirement on administrative privileges.
2. Install `pip`. `pip` is a [package manager for python](https://en.wikipedia.org/wiki/Pip_(package_manager)). If `pip` is not already installed in  your system, you can follow the official instructions on how to get it [here](https://pip.pypa.io/en/stable/installing/). **Make sure you run get-pip.py using python 3 in order to be able to use *structure_threader*.** Like this: `python3 get-pip.py`
3. Install *Structure_threader*. Now that you have python 3 and `pip` installed, installing *Structure_threader* is just one command away: `pip3 install structure_threader --user`. The `--user` option installs the software to a local directory, ensuring you do not need administration privileges to perform the installation.
4. Using *Structure_threader*. Running the command from step 3 will install the program to `~/.local/bin`. You can either run it by calling it directly `~/.local/bin/structure_threader` or by adding the location `~/.local/bin` to your shell `$PATH` ([here is a good guide on how to do it](https://unix.stackexchange.com/questions/26047/how-to-correctly-add-a-path-to-path)) and just calling `structure_threader`. Also note that on GNU/Linux installing *Structure_threader* will also automatically install binaries for *STRUCTURE*, *fastStructure* and *MavericK*, which will also be placed under `~/.local/bin`.

### MacOS

1. Install python 3. MacOS comes with python 2.7 installed by default, (Mac OSX versions before "Sierra" does not have any version of python installed) but in order to run *Structure_threader* you will need python 3.4 or above. You can [follow this comprehensive guide to do it](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install3/osx/).
2. Install `pip`. `pip` is a [package manager for python](https://en.wikipedia.org/wiki/Pip_(package_manager)). You can use the guide from step 1 to install it on your system.
3. Install *Structure_threader*. Now that you have python 3 and `pip` installed, installing *Structure_threader* is just one terminal command away: `pip3 install structure_threader --user`. The `--user` option installs the software to a local directory, ensuring you do not need administration privileges to perform the installation.
4. Using *Structure_threader*. Running the command from step 3 will install the program to `~/.local/bin`. You can either run it by calling it directly `~/.local/bin/structure_threader` or by adding the location `~/.local/bin` to your shell `$PATH` ([here is a good guide on how to do it](https://unix.stackexchange.com/questions/26047/how-to-correctly-add-a-path-to-path))and just calling `structure_threader`. Also note that on MacOS installing *Structure_threader* will also automatically install binaries for *STRUCTURE*, *fastStructure* and *MavericK*, which will also be placed under `~/.local/bin`.

### Windows

1. Install python 3. No version of Windows comes with python installed by default, but you can install it from [here](https://www.python.org/downloads/). If you need help installing python 3 for windows, here is [the official guide](https://docs.python.org/3/using/windows.html).
2. Install `pip`.  `pip` is a [package manager for python](https://en.wikipedia.org/wiki/Pip_(package_manager)). Using the instructions from the guide from step 1 will install `pip` for you.
3. Install *Structure_threader*. Now that you have python 3 and `pip` installed, installing *Structure_threader* is just one terminal command away: `C:\Python3.6\python.exe -m pip install structure_threader`. Don't forget to change the path "python3.6" to whatever version of python 3 you have installed.
4. Using *Structure_threader*. Running the command from step 3 will install the program to `C:\Python3.6\Scripts`. You can run it by calling it directly `C:\Python3.6\Scripts\structure_threader.exe`. Please note that on Windows installing the programs wrapped by *Structure_threader*, *STRUCTURE*, *fastStructure* and *MavericK*, is not done automatically. You will have to do so yourself.


## Alternative methods (AKA 'expert mode')
You can also run *Structure_threader* by simply cloning the repository (or
downloading one of the releases), and placing the contents of the directory
"structure_threader", on any location on your `$PATH` environment variable var.

Another alternative, that can be used since version 0.1.6 is the `setup.py`
method. This can be used either by running `python3 setup.py install` (or even
better, `pip3 install .`) from the distribution's root directory (where
`setup.py` is located).

Please note that while dependencies like numpy and matplotlib are handled by
this method, the preferred method for installing via Pypi will also install
binary versions of *STRUCTURE*, *fastStructure* and *MavericK* for your platform (except on Windows).
These binaries are installed in the "standard" `setup.py`
[locations](https://docs.python.org/2/install/), eg. `/usr/bin/` if installed
with `sudo` or `~/.local/bin/` if installed with the option `--user`, etc...

If you wish to compile your own binaries for these programs, you may wish to
rely on our
["helper_scripts"](https://github.com/StuntsPT/Structure_threader/tree/master/helper_scripts)
which contain commands to compile and install *Structure*, *fastStructure* **and** *MavericK* (along with any required dependencies). For more details check the next few sections.

If you wish to compile your own binaries for the external programs, the manual section [Extrenal programs](external.md) describes how the distributed binaries were built. Instructions and a build script are provided for *Structure*, *fastStructure* and *MavericK*.

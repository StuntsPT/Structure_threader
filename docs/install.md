# Installation
Specific instructions for the preferred installation methods are provided for each of the most used operating systems: GNU/Linux, macOS and Windows. There are also instructions with alternative methods, for example, if you wish to use *Structure_threader* on unsupported platforms (as long as they support Python 3).

## Preferred method, by platform

### GNU/Linux

1. Install Python 3.

   Currently, only versions 3.9-3.11 are supported (>3.12 won't work at all). Although Python 3 is already installed by default in most modern Linux distributions, sometimes it may not be available (you can type `python3 --version` from a terminal to see if Python 3 is installed. If it is, you will have something similar to `Python 3.11.12` printed on your terminal, if it isn't, you will either see a "command not found" error, or a helpful message on how to install Python 3). In Debian-based distributions (such as Ubuntu) you can install Python 3 by opening a terminal an running the command `sudo apt install python3`. In other Linux distributions you can similarly use your package manger to install it. If you do not have administration privileges in your environment, please ask your sysadmin to install Python 3 for you. This is the only step that has a hard requirement on administrative privileges. If your distribution has no official (or even alternative) ways of installing Python 3, we recommend installing a container image containing Python 3.11 (like [Docker's official Python 3.11 slim image](https://hub.docker.com/_/python/tags?name=3.11-slim)). Instructions for setting up Docker can be found [here](https://docs.docker.com/engine/install/).

2. Install `pip`.

   `pip` is a [package manager for Python](https://en.wikipedia.org/wiki/Pip_(package_manager)). If `pip` is not already installed in  your system, you can follow the official instructions on how to get it [here](https://pip.pypa.io/en/stable/installing/). **Make sure you run get-pip.py using Python 3 in order to be able to use *Structure_threader*.** Like this: `python3 get-pip.py`

3. Install *Structure_threader*.

   Now that you have Python 3 and `pip` installed, installing *Structure_threader* is just one command away: `pip install structure-threader --user`. The `--user` option installs the software to a local directory, ensuring you do not need administration privileges to perform the installation.

4. Use *Structure_threader*.

   Running the command from step 3 will install the program to `~/.local/bin`. You can either run it by calling it directly `~/.local/bin/structure_threader` or by adding the location `~/.local/bin` to your shell `$PATH` ([here is a good guide on how to do it](https://unix.stackexchange.com/questions/26047/how-to-correctly-add-a-path-to-path)) and just calling `structure_threader`. Also note that on GNU/Linux installing *Structure_threader* will also automatically install binaries for *STRUCTURE*, *fastStructure* and *MavericK*, which will also be placed under `~/.local/bin`.

### macOS

1. Install Python 3.11.

   You can install it from [here](https://www.python.org/downloads/). If you need further help with the installation on macOS, here is [the official guide](https://docs.python.org/3/using/mac.html).

2. Install `pip`.

   `pip` is a [package manager for Python](https://en.wikipedia.org/wiki/Pip_(package_manager)). You can use the guide from step 1 to install it on your system.

3. Install *Structure_threader*.

   Now that you have Python 3 and `pip` installed, installing *Structure_threader* is just one terminal command away: `pip install structure-threader --user`. The `--user` option installs the software to a local directory, ensuring you do not need administration privileges to perform the installation.

4. Use *Structure_threader*.

   Running the command from step 3 will install the program to `~/.local/bin` (or, under some versions, under `~/Library/Python/3.11/bin`, where `3.11` will change according to the version of `python` you are running). You can either run it by directly calling `~/.local/bin/structure_threader` (or `~/Library/Python/3.11/bin/structure_threader`) or by adding the location `~/.local/bin` (or `~/Library/Python/3.11/bin`) to your shell `$PATH` ([here is a good guide on how to do it](https://unix.stackexchange.com/questions/26047/how-to-correctly-add-a-path-to-path))and just calling `structure_threader`. Also note that on macOS installing *Structure_threader* will also automatically install binaries for *STRUCTURE*, *fastStructure* and *MavericK*, which will also be placed under `~/.local/bin` (or `~/Library/Python/3.11/bin/structure_threader`).

   **WARNING:** If you don't have [Rosetta 2](https://support.apple.com/102527) installed at this point, macOS should show you a prompt asking to install it once you attempt to use *STRUCTURE*, *fastStructure* or *MavericK*. Administrative privileges are required. These binaries will NOT work unless Rosetta 2 is enabled, as they were compiled for x64 macOS and not ARM64.

### Windows

#### Windows Subsystem for Linux (recommended)

If you have Windows 10 build 19041 or above, you can run *Structure_threader* using [Wiundows Subsystem for Linux](https://learn.microsoft.com/windows/wsl/about). We recommend using WSL 2, as this uses a full Linux kernel and is less likely to cause issues, along with improved performance.

1. Enable Windows Subsystem for Linux.

   This step requires administrative privileges. As of July 30th 2021, WSL can be enabled and installed using [only one command](https://devblogs.microsoft.com/commandline/install-wsl-with-a-single-command-now-available-in-windows-10-version-2004-and-higher/). Just run `wsl --install` and everything will be taken care of for you. The default Linux distribution for this method is Ubuntu. You can install other distributions of your choice, as long as they are available on the online store, using `wsl --install -d <Distribution Name>`. Replace `<Distribution Name>` with the name of the distribution you would like to install. To see a list of available Linux distributions available for download through the online store, enter: `wsl --list --online` or `wsl -l -o`.

2. Install Python 3.11.

      Currently, only versions 3.9-3.11 are supported (>3.12 won't work at all). Although Python 3 is already installed by default in most modern Linux distributions, sometimes it may not be available (you can type `python3 --version` from a terminal to see if Python 3 is installed. If it is, you will have something similar to `Python 3.11.12` printed on your terminal, if it isn't, you will either see a "command not found" error, or a helpful message on how to install Python 3). In Debian-based distributions (such as Ubuntu) you can install Python 3 by opening a terminal an running the command `sudo apt install python3`. In other Linux distributions you can similarly use your package manger to install it. If your distribution has no official (or even alternative) ways of installing Python 3, we recommend installing a container image containing Python 3.11 (like [Docker's official Python 3.11 slim image](https://hub.docker.com/_/python/tags?name=3.11-slim)). Instructions for setting up Docker can be found [here](https://docs.docker.com/engine/install/).

3. Install `pip`.

   `pip` is a [package manager for Python](https://en.wikipedia.org/wiki/Pip_(package_manager)). If `pip` is not already installed in  your system, you can follow the official instructions on how to get it [here](https://pip.pypa.io/en/stable/installing/). **Make sure you run get-pip.py using Python 3 in order to be able to use *Structure_threader*.** Like this: `python3 get-pip.py`

4. Install *Structure_threader*.

   Now that you have Python 3 and `pip` installed, installing *Structure_threader* is just one command away: `pip install structure-threader --user`. The `--user` option installs the software to a local directory, ensuring you do not need administration privileges to perform the installation.

5. Use *Structure_threader*.

   Running the command from step 3 will install the program to `~/.local/bin`. You can either run it by calling it directly `~/.local/bin/structure_threader` or by adding the location `~/.local/bin` to your shell `$PATH` ([here is a good guide on how to do it](https://unix.stackexchange.com/questions/26047/how-to-correctly-add-a-path-to-path)) and just calling `structure_threader`. Also note that on GNU/Linux installing *Structure_threader* will also automatically install binaries for *STRUCTURE*, *fastStructure* and *MavericK*, which will also be placed under `~/.local/bin`.

#### Native

1. Install Python 3.11.

   You can install it from [here](https://www.python.org/downloads/). If you need further help with the installation on Windows, here is [the official guide](https://docs.python.org/3/using/windows.html).

2. Install `pip`.

   `pip` is a [package manager for Python](https://en.wikipedia.org/wiki/Pip_(package_manager)). Using the instructions from the guide from step 1 will install `pip` for you.

3. Install *Structure_threader*.

   Now that you have Python 3 and `pip` installed, installing *Structure_threader* is just one terminal command away: `C:\Python3.11\python.exe -m pip install structure-threader`. Don't forget to change the path "Python3.11" to whatever version of Python 3 you have installed.

4. Use *Structure_threader*.

   Running the command from step 3 will install the program to `C:\Python3.11\Scripts`. You can run it by calling it directly `C:\Python3.11\Scripts\structure_threader.exe`. Please note that on Windows the installation of some software wrapped by *Structure_threader* (*STRUCTURE*, *fastStructure* and *MavericK*) is not done automatically. You will have to either install or compile the binaries for them yourself.


## Alternative methods (advanced)
You can also run *Structure_threader* by cloning the repository (or
downloading one of the releases' source code), and placing the contents of the directory
"structure_threader", on any location on your `$PATH` environment variable var.

Another alternative, that can be used since version 0.1.6 is the `setup.py`
method. This can be used either by running `python3 setup.py install` (or even
better, `pip install .`) from the distribution's root directory (where
`setup.py` is located).

Please note that while dependencies like numpy and matplotlib are handled by
this method, the preferred method for installing via PyPI will also install
binary versions of *STRUCTURE*, *fastStructure* and *MavericK* for your platform (except on Windows, if not using WSL).
These binaries are installed in the "standard" `setup.py`
[locations](https://docs.python.org/3/installing/index.html), eg. `/usr/bin/` if installed
as `root`, or `~/.local/bin/` if installed with the option `--user`, etc...

If you wish to compile your own binaries for these programs, you may wish to
rely on our
["helper_scripts"](https://gitlab.com/StuntsPT/Structure_threader/-/tree/master/helper_scripts)
which contain commands to compile and install *Structure*, *fastStructure* **and** *MavericK* (along with any required dependencies). For more details check the next few sections.

If you wish to compile your own binaries for the external programs, the manual section [External programs](external.md) describes how the distributed binaries were built. Instructions and a build script are provided for *Structure*, *fastStructure* and *MavericK*.

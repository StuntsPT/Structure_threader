# Installation
Specific instructions for the preferred installation methods are provided for each of the most used operating systems: GNU/Linux, macOS and Windows. There are also instructions with alternative methods, for example, if you wish to use *Structure_threader* on unsupported platforms (as long as they support Python 3).

## Preferred method, by platform

### GNU/Linux and macOS

1. Install [Conda](https://docs.conda.io/).

    `conda` is a powerful command line tool for dependency, and environment management for any language. You have various distributions for `conda`, and even alternatives like [`mamba`](https://mamba.readthedocs.io/en/latest/index.html). To get started, we recommend using either [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions) or [Micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html). Miniconda bundles `conda` with minimal dependencies, while `micromamba` aims to be a from-scratch reimplementation in C++ (`conda` is written in Python) also with minimal dependencies, making it have considerable speed increases.

2. Add the [Bioconda](https://bioconda.github.io/) channel.

    Bioconda allows you to install software packages related to biomedical research using the `conda` package manager. Following the official instructions should help you add Bioconda to your `conda` channel list. The commands for `micromamba` are a little different.
    For `micromamba`, instead of:

    ```
    $ conda config --add channels <channelname>
    ```

    You should use:

    ```
    $ micromamba config append channels <channelname>
    ```

    Replacing `<channelname>` with the name of the channel you wish to add.

3. Install *Structure_threader*.

    Now that you have Bioconda, installing *Structure_threader* is just one command away:

    `conda install structure_threader` (replace `conda` with `micromamba` if using that)

    It's recommended that you create and activate a fresh environment first:

    `conda create <environmentname>`

    `conda activate <environmentname>`

    Replace `<environmentname>` with any name you'd like to give.

4. Use *Structure_threader*.

    Running the command from step 3 will install the program to your environment's prefix. You can run it after activating that environment just by calling `structure_threader`. All dependencies should be automatically installed for you, including binaries for *STRUCTURE*, *fastStructure* and *MavericK*.

### Windows

#### Windows Subsystem for Linux (recommended)

If you have Windows 10 build 19041 or above, you can run *Structure_threader* using [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl/about). We recommend using WSL 2, as this uses a full Linux kernel and is less likely to cause issues, along with improved performance.

1. Enable Windows Subsystem for Linux.

    This step requires administrative privileges. As of July 30th 2021, WSL can be enabled and installed using [only one command](https://devblogs.microsoft.com/commandline/install-wsl-with-a-single-command-now-available-in-windows-10-version-2004-and-higher/). Just run `wsl --install` and everything will be taken care of for you. The default Linux distribution for this method is Ubuntu. You can install other distributions of your choice, as long as they are available on the online store, using `wsl --install -d <Distribution Name>`. Replace `<Distribution Name>` with the name of the distribution you would like to install. To see a list of available Linux distributions available for download through the online store, enter: `wsl --list --online` or `wsl -l -o`.

2. [Follow the installation steps for GNU/Linux](#gnulinux-and-macos).

#### Docker container

If you don't want to install Python 3, we recommend using a container image. Instructions for setting up Docker can be found [here](https://docs.docker.com/engine/install/). Afterwards you can use *Structure_threader*'s [official image](). Alternatively, you can use [Docker's official Ubuntu image](https://hub.docker.com/_/ubuntu), followed by the [installation steps for GNU/Linux](#gnulinux-and-macos).).

#### Native

1. Install Python 3.11.

    Currently, only versions 3.9-3.11 are supported (>3.12 won't work at all). You can install it from [here](https://www.python.org/downloads/). If you need further help with the installation on Windows, here is [the official guide](https://docs.python.org/3/using/windows.html).

2. Install `pip`.

    `pip` is a [package manager for Python](https://en.wikipedia.org/wiki/Pip_(package_manager)). If `pip` is not already installed in  your system, you can follow the official instructions on how to get it [here](https://pip.pypa.io/en/stable/installation/). **Make sure you run get-pip.py using Python 3 in order to be able to use *Structure_threader*.** Like this: `C:\Python3.11\python.exe get-pip.py`. Change the path "Python3.11" to whatever version of Python 3 you have installed.

3. Install *Structure_threader*.

    Now that you have Python 3 and `pip` installed, installing *Structure_threader* is just one terminal command away: `C:\Python3.11\python.exe -m pip install structure-threader`. Don't forget to change the path "Python3.11" to whatever version of Python 3 you have installed.

4. Use *Structure_threader*.

    Running the command from step 3 will install the program to `C:\Python3.11\Scripts`. You can run it by calling it directly `C:\Python3.11\Scripts\structure_threader.exe`. Please note that on Windows the installation of some software wrapped by *Structure_threader* (*STRUCTURE*, *fastStructure* and *MavericK*) is not done automatically. You will have to either install or compile the binaries for them yourself.


## Alternative methods (advanced)
You can also run *Structure_threader* via `pip`, by running the command:

```
pip install structure-threader
```

Or by cloning the repository (or downloading one of the releases' source code),
and placing the contents of the directory "structure_threader", on any location
on your `$PATH` environment variable var.

Another alternative, that can be used since version 0.1.6 is the `setup.py`
method. This can be used either by running `python3 setup.py install` (or even
better, `pip install .`) from the distribution's root directory (where
`setup.py` is located).

Please note that while dependencies like numpy and matplotlib are handled by
this method, the preferred method for installing via Conda will also install
binary versions of *STRUCTURE*, *fastStructure* and *MavericK* for your platform.
These binaries are installed in the "standard" `setup.py`
[locations](https://docs.python.org/3/installing/index.html), eg. `/usr/bin/` if installed
as `root`, or `~/.local/bin/` if installed with the option `--user`, etc...

If you wish to compile your own binaries for these programs, you may wish to
rely on our
["helper_scripts"](https://gitlab.com/StuntsPT/Structure_threader/-/tree/master/helper_scripts)
which contain commands to compile and install *Structure*, *fastStructure* **and** *MavericK* (along with any required dependencies). For more details check the next few sections.

If you wish to compile your own binaries for the external programs, the manual section [External programs](external.md) describes how the distributed binaries were built. Instructions and a build script are provided for *Structure*, *fastStructure* and *MavericK*.

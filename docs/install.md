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

    Now that you have Bioconda, installing *Structure_threader* is straightforward:

    ```
    $ conda create -n stenv python=3.11
    $ conda activate stenv
    (stenv) $ conda install structure_threader
    ```

    Replace `conda` with `micromamba` if using that. You can also replace `stenv` with any name you'd like to give the environment.

4. Install a container runtime.

    As of version 2.1.0, *Structure_threader* runs the wrapped programs inside [Apptainer/Singularity](https://apptainer.org/) containers by default. If Apptainer or Singularity is already installed on your system, *Structure_threader* will detect and use it automatically.

    If you are on a system where you have administrative access (e.g. your own workstation), you can install Apptainer from your distribution's package manager. On Debian/Ubuntu-based systems:

    ```
    $ sudo add-apt-repository -y ppa:apptainer/ppa
    $ sudo apt update
    $ sudo apt install apptainer-suid
    ```

    The `apptainer-suid` package is recommended over `apptainer` as it works in environments where unprivileged user namespaces are disabled (common on HPC clusters and shared servers).

    If no container runtime is available, *Structure_threader* will fall back to using locally installed binaries and print a warning. You can also explicitly opt out of containers using `--no-container`.

5. Use *Structure_threader*.

    Running the commands from step 3 will install the program to that environment's prefix. You can run it after activating that environment just by calling `structure_threader`. All dependencies should be automatically installed for you, including Snakemake. You can get *Neural ADMIXTURE* by running `pip install neural-admixture` inside the prefix. ALStructure can be run using an included wrapper, as R dependencies are installed.

### Windows

#### Windows Subsystem for Linux (recommended)

If you have Windows 10 build 19041 or above, you can run *Structure_threader* using [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl/about). We recommend using WSL 2, as this uses a full Linux kernel and is less likely to cause issues, along with improved performance.

1. Enable Windows Subsystem for Linux.

    This step requires administrative privileges. As of July 30th 2021, WSL can be enabled and installed using [only one command](https://devblogs.microsoft.com/commandline/install-wsl-with-a-single-command-now-available-in-windows-10-version-2004-and-higher/). Just run `wsl --install` and everything will be taken care of for you. The default Linux distribution for this method is Ubuntu. You can install other distributions of your choice, as long as they are available on the online store, using `wsl --install -d <Distribution Name>`. Replace `<Distribution Name>` with the name of the distribution you would like to install. To see a list of available Linux distributions available for download through the online store, enter: `wsl --list --online` or `wsl -l -o`.

2. [Follow the installation steps for GNU/Linux](#gnulinux-and-macos).

#### Native

1. Install Python 3.11 or later.

    You can install it from [here](https://www.python.org/downloads/). If you need further help with the installation on Windows, here is [the official guide](https://docs.python.org/3/using/windows.html).

2. Install `pip`.

    `pip` is a [package manager for Python](https://en.wikipedia.org/wiki/Pip_(package_manager)). If `pip` is not already installed in your system, you can follow the official instructions on how to get it [here](https://pip.pypa.io/en/stable/installation/).

3. Install *Structure_threader*.

    Now that you have Python 3 and `pip` installed, installing *Structure_threader* is just one terminal command away: `C:\Python311\python.exe -m pip install structure_threader`. Don't forget to change the path "Python311" to whatever version of Python 3 you have installed.

4. Use *Structure_threader*.

    Running the command from step 3 will install the program to `C:\Python311\Scripts`. You can run it by calling it directly: `C:\Python311\Scripts\structure_threader.exe`. Please note that on Windows, container support via Apptainer is not available. You will need to either use `--no-container` with locally installed binaries, or use WSL 2 (recommended).


## Alternative methods (advanced)
You can also install *Structure_threader* via `pip`:

```
pip install structure_threader
```

You can also clone the repository (or download one of the tags' source code) and install from the source directory:

```
pip install .
```

If you wish to compile your own binaries for the external programs, the manual section [External programs](external.md) describes how the distributed legacy binaries were built. Instructions and build scripts are provided for *Structure*, *fastStructure* and *MavericK*, though these are only needed if you intend to use `--no-container` with locally compiled programs.

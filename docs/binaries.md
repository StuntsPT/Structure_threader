# Binary building

For your conveninence, we have pre-built binaries of STRUCTURE,
fastStructure and MavericK. They are provided with the package under
`structure_threader/bins/$platform/`.

Here is how they were built:

## The build system

### GNU/Linux binaries
Binaries were built on a machine with an Intel Xeon E5-2609 0 @ 2.40GHz CPU.
The OS under which the binaries were built is Ubuntu 12.04 64bit. This "old"
OS was used since GNU/Linux systems have backwards, but not forwards compatibility.
This means that binaries built on older systems will run on newer systems, but
the opposite may not be true.

### macOS binaries
Binaries were built on a 2013 MacBook Air with a "Haswell" microarchitecture
based Intel i5 CPU, running Mac OS X 10.10 Yosemite. They should be forward
compatible with later Mac OS X and macOS releases (if using an Apple silicon
Mac, e.g. 2020 Macbook Air with Apple M1, you must have
[Rosetta 2](https://support.apple.com/102527)).

## STRUCTURE

STRUCTURE is relatively simple to build. Source code can be obtained from the
 [STRUCTURE website](http://web.stanford.edu/group/pritchardlab/structure_software/release_versions/v2.3.4/structure_kernel_source.tar.gz). To build the binary, we used our helper
 script "install_structure.sh". The binary version is 2.3.4.


## fastStructure

fastStructure has a more involved process to build, as it requires many
dependencies. It can be obtained from
[its own GitHub repository](https://github.com/rajanil/fastStructure).
Although fastStructure is written in Python 2, it uses compiled code, by making
use of `cython`.
To build the binary, we have installed fastStructure using our helper script
"install_faststructure.sh" and then we used
[pyinstaller](http://www.pyinstaller.org/) to turn it into a binary. The used
"specfile" can be found [here](https://gitlab.com/StuntsPT/Structure_threader/tree/master/helper_scripts/structure.spec) which contains all the required information to reproduce the
build. The binary version is 1.0.

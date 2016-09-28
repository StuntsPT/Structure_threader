# Binary building

For your conveninence, we have pre-build binaries of STRUCTURE and
fastStructure. They are provided with the package under
`structure_threader/bins/$platform/`.
Here is how they were built.

## The build system

### GNU/Linux binaries
Binaries were built on a machine with an Intel Xeon E5-2609 0 @ 2.40GHz CPU.
The OS under which the binaries were built is Ubuntu 12.04 64bit. This "old"
OS was used since linux systems have backwards, but not forwards compatibility.
This means that binaries built on older systems will run on newer systems, but
the opposite may not be true.

### OSX binaries
Binaries were build on Mid 2013 MacBook Air with an "Haswell" based i5 CPU, running OSX 10.10 Yosemite.
They should be forward compatible with later OSX releases.

## STRUCTURE

STRUCTURE is relatively simple to build. Source code can be obtained from the
 [STRUCTURE website](http://pritchardlab.stanford.edu/structure_software/release_versions/v2.3.4/structure_kernel_source.tar.gz). To build the binary, we used our helper
 script "install_structure.sh". The binary version is 2.3.4.


 ## fastStructure

fastStructure requires a more involved process to build as it requires many
dependencies. It can be obtained from
[it's own github repository](https://github.com/rajanil/fastStructure).
Although fastStructure is written in python 2, it uses compiled code, by making
use of `cython`.
To build the binary, we have insatlled fastStructure using our helper script
"install_faststructure.sh" and then we have used
[pyinstaller](http://www.pyinstaller.org/) to turn it into a binary. The used
"specfile" can be found [here](https://github.com/StuntsPT/Structure_threader/tree/master/helper_scripts/structure.spec) which contains all the required information to reproduce the
build. The binary version is 1.0.

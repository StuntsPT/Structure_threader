#!/bin/bash

set -e

# Define test dir
testdir=`pwd`

# Get LDFAGS
_OLD_LDFLAGS=$LDFLAGS

# Create env dir for dependent libraries
mkdir -p ${testdir}/env
envdir=${testdir}/env

# Install dependencies
# LAPACK
tar xvfz lapack-3.5.0.tgz
mkdir -p build-lapack
cd build-lapack
cmake ../lapack-3.5.0
make
#mkdir -p ${envdir}/{bin,lib}
mv bin ${envdir}
mv lib ${envdir}

# cython
cd ${testdir}
unzip Cython-0.22.zip
cd Cython-0.22
PYTHONPATH=$PYTHONPATH:${envdir}
python2 setup.py install --prefix=${envdir}

# python-nose
cd ${testdir}
tar xvfz nose-1.3.6.tar.gz
cd nose-1.3.6
python2 setup.py install --prefix=${envdir}

# numpy
cd ${testdir}
tar xvfz v1.9.2.tar.gz
cd numpy-1.9.2
sed -e "s|#![ ]*/usr/bin/python$|#!/usr/bin/python2|" \
    -e "s|#![ ]*/usr/bin/env python$|#!/usr/bin/env python2|" \
    -e "s|#![ ]*/bin/env python$|#!/usr/bin/env python2|" \
    -i $(find . -name '*.py')
export ATLAS=None
export LDFLAGS="$LDFLAGS -shared"
python2 setup.py install --prefix=${envdir}

# scipy
cd ${testdir}
tar xvfz scipy.tar.gz
cd scipy-0.16.0b2
python2 setup.py install --prefix=${envdir}

# GNU scientific library
cd ${testdir}
tar xvzf gsl-latest.tar.gz
cd gsl-1.16
export LDFLAGS=${_OLD_LDFLAGS}
./configure --prefix=${envdir}
make
make install

# fastStructure
# Extract tarball, enter src dir, build binary and place it in the env dir
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${envdir}/lib
export CFLAGS="-I${envdir}/include"
export LDFLAGS="-L${envdir}/lib"
cd ${testdir}
tar xvfz v1.0.tar.gz
cd  fastStructure-1.0
cd vars
python2 setup.py build_ext --inplace
cd ..
python2 setup.py build_ext --inplace

# Dataset
cd ${testdir}
tar xvfJ BigTestData.str.tar.xz

# Structure_threader
cd ${testdir}
tar xfvz v0.1-rc3.tar.gz

# Create launcher script

echo "#!/bin/bash
workdir=`pwd`
cd Structure_threader-0.1-rc3/
python3 structure_threader.py \$@ -fs \${workdir}/fastStructure-1.0/structure.py > \$LOG_FILE 2>&1
" > structure_threader-faststructure
chmod +x structure_threader-faststructure

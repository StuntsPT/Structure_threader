#!/bin/sh

# Define test dir
testdir=`pwd`

# Create env dir for dependent libraries
mkdir -p ${testdir}/env

# Install dependencies
# Structure
cd ${testdir}
tar -zxvf structure_kernel_source.tar.gz
cd structure_kernel_src
make

# Install Structure_threder
# Structure_threader
cd ${testdir}
tar xfvz v0.1-rc3.tar.gz

# Create launcher script

echo "#!/bin/bash
workdir=`pwd`
cd Structure_threader-0.1-rc3/
python3 structure_threader.py \$@ -st \${workdir}/structure_kernel_src/structure > \$LOG_FILE 2>&1
" > structure_threader-structure_4
chmod +x structure_threader-structure_4

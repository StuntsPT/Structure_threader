#!/bin/sh

tar -zxvf v1.0.tar.gz

cd fastStructure-1.0/vars
python2 setup.py build-ext --inplace
cd ..
python2 setup.py build-ext --inplace

cd ..

echo "#!/bin/bash

for i in {1..4}
  do
      for j in {1..4}
        do
  python2 ./fastStructure-1.0/structure.py --input=BigTestData --output=TestBigData_out_K\${i}_R\${j} -K \${i} --format=str >> \$LOG_FILE 2>&1
        done
  done

" > fastStructure
chmod +x fastStructure

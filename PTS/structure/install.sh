#!/bin/sh

tar -zxvf structure_kernel_source.tar.gz

cd structure_kernel_src
make
echo $? > ~/install-exit-status
cd ..

echo "#!/bin/bash
cd structure_kernel_src/
cp ../mainparams ./
cp ../extraparams ./
for i in {1..4}
  do
      for j in {1..4}
        do
  ./structure -i ../Reduced_dataset.structure -o ../output -K ${i} >> \$LOG_FILE 2>&1
        done
  done

echo \$? > ~/test-exit-status" > structure.sh
chmod +x structure.sh

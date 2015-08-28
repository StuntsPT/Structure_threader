#!/bin/sh

tar -zxvf structure_kernel_source.tar.gz

cd structure_kernel_src
make
echo $? > ~/install-exit-status
cd ..

echo "#!/bin/bash

for i in {1..4}
  do
      for j in {1..4}
        do
  ./structure_kernel_src/structure -i Reduced_dataset.structure -o output_K\${i}_R\${j} -K \${i} >> \$LOG_FILE 2>&1
        done
  done

echo \$? > ~/test-exit-status" > structure
chmod +x structure

#!/bin/sh
# Auto-generated install.sh script for starting/helping the test profile creation process...

tar -xvf v1.0.5.tar.gz

cd MavericK-1.0.5
make
cd ..
mkdir -p results/ results/mav_K{1..4}

echo "#!/bin/bash

for i in {1..4}
  do
    ./MavericK-1.0.5/MavericK -Kmin 1 -Kmax \${i} -data Reduced_dataset.structure -outputRoot results/mav_K\${i}/ -parameters parameters.txt >> \$LOG_FILE 2>&1
  done

" > run-maverick-pts.sh
chmod +x run-maverick-pts.sh


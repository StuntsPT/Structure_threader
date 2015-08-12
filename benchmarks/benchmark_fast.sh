#!/bin/zsh

ks=( 1 2 3 4 5 6 7 8 )

datafile=Chr1
#datafile=Chr22

for i in ${ks}
do
  echo "Currently running K=${i}."
  python2 ~/Software/fastStructure/structure.py -K $i --input=../TestData/${datafile} --output=../TestData/${datafile}_out --format=str
done

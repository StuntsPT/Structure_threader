#!/bin/zsh

ks=( 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 )

datafile=Chr1
#datafile=Chr22

for i in $ks
do
  echo "Currently running K=$i."
  python2 ~/Software/fastStructure/structure.py -K $i --input=../TestData/Chr1 --output=../TestData/Chr1_out --format=str
done

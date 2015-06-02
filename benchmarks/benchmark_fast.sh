#!/bin/zsh

ks=( 1 1 1 1 2 2 2 2 3 3 3 3 4 4 4 4 )

for i in $ks
do
python2 ~/Software/fastStructure/structure.py -K $i --input=../TestData/Chr1 --output=../TestData/Chr1_out --format=str
done

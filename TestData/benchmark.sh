#!/bin/zsh

ks=( 1 1 1 1 2 2 2 2 3 3 3 3 4 4 4 4 )

for i in $ks
do
/opt/structure/bin/structure -K $i -i TestData.structure -o bench.txt
done


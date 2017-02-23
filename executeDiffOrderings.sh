#!/bin/bash

{
    read; # Just a scratch read to get rid of the first line
    while read line; do
	echo $line
	#if echo $line2 | grep "Least"; then
	#python evaluateURLOrderings.py $line
	#fi
	for k in 1 2 3 4; do
	    echo $k
	    line2=`echo $line | sed s/100000/$k/g | sed s/_results/_k${k}_results/g`
	    #if echo $line2 | grep "Least"; then
	    python evaluateURLOrderingsAsNumbers.py $line2
	    #fi
	done	
    done
} < "exectemp2.txt" #"executionParameters.txt"


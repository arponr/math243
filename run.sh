#!/bin/bash

for MEETS in 10 20 50 100
do
    echo MEETS=$MEETS
    python reput.py data$MEETS MEETS=$MEETS STEPS=25000 DUMP=2500 C=1\
    B=2 N=$MEETS PROC=4 SIM=16 
done

python morepics.py data '[10, 20, 50, 100]'

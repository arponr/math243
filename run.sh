#!/bin/bash

for MEETS in 10 20 50 100
do
    python reput.py data$MEETS MEETS=$MEETS STEPS=2500 C=1 B=2 N=100\
    PROC=4 SIM=1
done

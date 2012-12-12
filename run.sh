#!/bin/bash

for MEETS in 10 20 50 10
do
    python reput.py data$MEETS MEETS=$MEETS STEPS=25000 C=1 B=2 N=100\
    PROC=4 SIM=16
done

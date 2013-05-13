#!/bin/bash

for m in 50 200
do
    python reput.py data$m \
    N=100 MEETS=$m ITER=10 \
    STEPS=10000 DUMP=100 PROC=2 SIM=2 \
    C=1 B=5 SEL=.1 
    python pictures.py data$m
done




#!/usr/bin/python
# read ncoarse from a info file

import os
import sys
import numpy
import math
import Image
import fortranfile    # for fortran data import
import initialize as my

# check syntax
i=len(sys.argv)
if i!=2:
    print "Usage: read_ncoarse.py snap"
    exit(1)

snap = int(sys.argv[1])
num5=str(snap).zfill(5)
filename="output_"+num5+"/info_"+num5+".txt"
if(not os.path.exists(filename)): exit(1)
file = open(filename)
i=0; z=100.0
for line in file:
    i=i+1
    if(i==6):
        val = line.split()
        a = int(val[1])
print a

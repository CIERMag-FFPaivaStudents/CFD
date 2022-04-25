#!/usr/bin/bash

foamCleanTutorials #Making sure the directory is clean

blockMesh 

renumberMesh -overwrite

checkMesh

decomposePar

mpirun -np 6 simpleFoam -parallel > log.simple & 
pyFoamPlotWatcher.py log.simple --with-all

reconstructPar -latestTime

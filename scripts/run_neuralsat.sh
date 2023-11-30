#!/bin/bash


. ${SwarmHost}/scripts/init_conda.sh
conda activate neuralsat

which python
export MKL_SERVICE_FORCE_INTEL=1

cmd="python $SwarmHost/lib/neuralsat/src/main.py $@"
echo $cmd
$cmd

conda deactivate

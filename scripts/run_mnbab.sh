#!/bin/bash

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/edward/Apps/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/edward/Apps/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/home/edward/Apps/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/edward/Apps/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda deactivate
conda activate mnbab

MNBAB=$SwarmHost/lib/mnbab
cd $MNBAB
export PYTHONPATH=$PYTHONPATH:$PWD
echo $PYTHONPATH

cmd="python $SwarmHost/swarm_host/verifiers/mnbab/exe.py $@"
echo $cmd
$cmd

cd $OCTOPUS
conda deactivate
#!/bin/bash

conda activate swarmhost

if [ -z ${SwarmHost} ]; then
  export $SwarmHost=`pwd`
fi

export swarmhost="python -m swarm_host"

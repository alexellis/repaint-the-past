#!/bin/bash

docker service create --env-file env.list --network func_functions --name tweetlistener alexellis2/tweetlistener:0.2.1

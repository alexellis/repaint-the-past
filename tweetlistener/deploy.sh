#!/bin/bash

docker service create --env-file env.list --network func_functions --name tweetlistener developius/tweetlistener:latest

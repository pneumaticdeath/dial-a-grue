#!/bin/bash

cmd="screen -D -m -S jasper sudo bash -c 'cd /home/chip/jasper; /home/chip/jasper/jasper.py'"
if [[ "$(whoami)" == "root" ]] ; then 
    exec su - chip -c "${cmd}"
else
    eval ${cmd}
fi

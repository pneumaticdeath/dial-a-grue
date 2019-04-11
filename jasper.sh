#!/bin/bash

source /etc/default/jasper

if [[ "${JASPER_SUDO}" == "yes" ]]; then
    SUDO=sudo
else
    SUDO=""
fi

cmd="screen -D -m -S jasper ${SUDO} bash -c 'cd ${JASPER_DIR}; ${JASPER_DIR}/jasper.py'"
if [[ "$(whoami)" == "root" ]] ; then 
    exec su - ${JASPER_USER} -c "${cmd}"
else
    eval ${cmd}
fi

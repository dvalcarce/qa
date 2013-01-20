#!/bin/bash

# Initialiazing script

info()
{
	echo "Usage:"
	echo "    launch.sh interactive"
	echo "    launch.sh batch <file>"
	echo "    launch.sh debug"
}

cd src

if [ $# -eq 0 ]; then
	info
elif [ $1 = "interactive" ]; then
	python QA.py
elif [ $1 = "batch" ]; then
	if [ $# -eq 1 ]; then
		echo "Syntax: launch.sh batch <file>"
	else
		python QA.py $2
	fi
elif [ $1 = "debug" ]; then
	python QA.py pickle
else
	info
fi

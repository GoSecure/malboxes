#!/bin/bash

for F in `ls malboxes/profiles/*.json`; do
	echo "Processing file $F";
	python3 -m json.tool $F 1>/dev/null
	if [[ $? -ne 0 ]]; then
		echo "Badly formatted JSON file! Failing test...";
		exit 1;
	else
		echo "Properly formatted JSON file";
	fi
done

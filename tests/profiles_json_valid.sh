#!/bin/bash

DIRS="malboxes/profiles/*.json malboxes/profiles/snippets/*.json"

for F in `ls $DIRS`; do
	echo "Processing file $F";
	python3 -m json.tool $F 1>/dev/null
	if [[ $? -ne 0 ]]; then
		echo "Badly formatted JSON file! Failing test...";
		exit 1;
	else
		echo "Properly formatted JSON file";
	fi
done

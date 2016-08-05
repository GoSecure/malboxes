#!/bin/bash

F=config-example.js
echo "Processing file $F";
# minifying first to strip comments
python3 -m jsmin $F | python3 -m json.tool 1>/dev/null
if [[ $? -ne 0 ]]; then
	echo "Badly formatted JSON file! Failing test...";
	exit 1;
else
	echo "Properly formatted JSON file";
fi

#!/bin/bash
#
# Olivier Bilodeau <obilodeau@gosecure.ca>
# Copyright (C) 2018 GoSecure Inc.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

export PATH=$PATH:$HOME/.local/bin

echo "Performing a local install of malboxes in development mode"
pip3 install -e .

echo "Fetching all templates..."
TEMPLATES=$(malboxes list | head -n-1 | tail -n+3; exit ${PIPESTATUS[0]})
if [[ $? != 0 ]]; then
        echo "Malboxes didn't list templates. This is a fatal error. Force failing the build."
	exit 1
fi


# build all templates
declare -A RESULTS
WORST_EXIT_STATUS=0
for _T in $TEMPLATES; do
        echo "Building template $_T"
        malboxes --config tests/smoke/config.js build --force --skip-vagrant-box-add $_T
	EXIT_VAL=$?
	if (( $EXIT_VAL > $WORST_EXIT_STATUS )); then
		WORST_EXIT_STATUS=$EXIT_VAL
	fi
        RESULTS[$_T]=$EXIT_VAL
done

echo Finished building all templates. Results:
for _T in "${!RESULTS[@]}"; do
  echo "$_T: ${RESULTS[$_T]}"
done

# Not necessarily worse but at least non-zero
exit $WORST_EXIT_STATUS

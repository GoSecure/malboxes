#!/usr/bin/env bash

apt-get clean

# Fill drive with zeroes to help compression
dd if=/dev/zero of=/filljunk bs=1M
rm -f /filljunk
sync

rm -f ~/.bash_history

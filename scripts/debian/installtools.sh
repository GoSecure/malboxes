#!/bin/bash

cat << EOF > /etc/apt/sources.list.d/sources.list
deb http://www.inetsim.org/debian/ binary/
EOF

wget -O - http://www.inetsim.org/inetsim.org-archive-signing-key.asc | apt-key add -
apt-get update
apt-get -y install inetsim

#!/usr/bin/env bash

apt-get -y install linux-headers-amd64 dkms build-essential

mkdir /tmp/virtualbox
mount -o loop /home/vagrant/VBoxGuestAdditions.iso /tmp/virtualbox
sh /tmp/virtualbox/VBoxLinuxAdditions.run
umount /tmp/virtualbox
rm -rf /tmp/virtualbox
rm -f /home/vagrant/VBoxGuestAdditions.iso

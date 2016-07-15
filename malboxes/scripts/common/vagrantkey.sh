#!/usr/bin/env bash
mkdir -pm 0700 /home/vagrant/.ssh
wget --no-check-certificate -O authorized_keys  'https://github.com/mitchellh/vagrant/raw/master/keys/vagrant.pub' 
mv authorized_keys /home/vagrant/.ssh
chmod 0600 /home/vagrant/.ssh/authorized_keys
chown -R vagrant:vagrant /home/vagrant/.ssh
echo 'vagrant ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers


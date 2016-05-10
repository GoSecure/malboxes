#!/usr/bin/env python3
#
# Malboxes - Vagrant box builder for malware analysis
# https://github.com/gosecure/malboxes
#
# Olivier Bilodeau <obilodeau@gosecure.ca>
# Copyright (C) 2016 GoSecure Inc.
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
import json
import os
import signal
import subprocess

from jinja2 import Environment, FileSystemLoader
from sh import packer_io

CONFIG_CACHE = 'config_cache/'

def prepare_autounattend(config, os):
    """
    Prepares an Autounattend.xml file according to configuration and writes it
    into a temporary location where packer later expects it.
    
    Uses jinja2 template syntax to generate the resulting XML file.
    """
    env = Environment(loader=FileSystemLoader('installconfig/'))
    template = env.get_template("{}/Autounattend.xml".format(os))
    f = create_configfd('Autounattend.xml')
    f.write(template.render(config))


def load_config():
    """
    Config is in JSON since we can re-use the same in both malboxes and packer
    """
    with open('config.json', 'r') as f:
        return json.load(f)


tempfiles = []
def create_configfd(filename):
    try:
        os.mkdir(CONFIG_CACHE)
    except FileExistsError:
        pass

    tempfiles.append(filename)
    return open(CONFIG_CACHE + filename, 'w')


def cleanup():
    """Removes temporary files"""
    for f in tempfiles:
        os.remove(CONFIG_CACHE + f)


def run_packer(os_config):
    print("Starting packer to generate the VM")
    print("----------------------------------")
    p = subprocess.Popen(['packer-io', 'build', '-var-file=config.json', os_config],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip().decode('utf-8'))

    # send Ctrl-C to packer
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip().decode('utf-8'))
        raise

    print("----------------------------------")
    print("packer completed")


if __name__ == "__main__":
    try:
        print("Generating configuration files...")
        config = load_config()
        prepare_autounattend(config, 'windows_7')
        print("Configuration files are ready")
        run_packer('windows-7-dirty.json')
    finally:
        cleanup()

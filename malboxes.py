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
import argparse
import glob
import json
import os
import re
import signal
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader
from sh import packer_io

CONFIG_CACHE = 'config_cache/'

def prepare_autounattend(config):
    """
    Prepares an Autounattend.xml file according to configuration and writes it
    into a temporary location where packer later expects it.
    
    Uses jinja2 template syntax to generate the resulting XML file.
    """
    # os type is extracted from profile json
    os_type = config['builders'][0]['guest_os_type'].lower()

    env = Environment(loader=FileSystemLoader('installconfig/'))
    template = env.get_template("{}/Autounattend.xml".format(os_type))
    f = create_configfd('Autounattend.xml')
    f.write(template.render(config))


def load_config(profile):
    """
    Config is in JSON since we can re-use the same in both malboxes and packer
    """
    profile_file = 'profiles/{}.json'.format(profile)
    # validate if profile is present
    if not os.path.isfile(profile_file):
        return False, None

    # load general config
    config = {}
    with open('config.json', 'r') as f:
        config = json.load(f)

    # merge/update with profile config
    with open(profile_file, 'r') as f:
        config.update(json.load(f))

    return True, config


tempfiles = []
def create_configfd(filename):
    try:
        os.mkdir(CONFIG_CACHE)
    except FileExistsError:
        pass

    tempfiles.append(filename)
    return open(CONFIG_CACHE + filename, 'w')


def initialize():
    parser = argparse.ArgumentParser(description=
            "Vagrant box builder for malware analysis")
    parser.add_argument('profile', nargs='?', default=None,
            help='Name of the profile to build. '
            'Will list the profiles if no profile is given.')
    args = parser.parse_args()
    return parser, args


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


def list_profiles():
    print("Supported profiles:\n")
    for f in glob.glob('profiles/*.json'):
        m = re.search(r'^profiles\/(.*).json$', f)
        print(m.group(1))
    print()


if __name__ == "__main__":
    try:
        parser, args = initialize()
        if not args.profile:
            list_profiles()
            parser.print_usage()
            sys.exit(1)

        print("Generating configuration files...")
        result, config = load_config(args.profile)
        if not result:
            print("Profile doesn't exist")
            sys.exit(2)

        prepare_autounattend(config)
        print("Configuration files are ready")
        run_packer('profiles/{}.json'.format(args.profile))

    finally:
        cleanup()

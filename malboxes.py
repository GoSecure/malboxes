#!/usr/bin/env python3
#
# Malboxes - Vagrant box builder and config generator for malware analysis
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


def initialize():
    parser = argparse.ArgumentParser(description=
            "Vagrant box builder and config generator for malware analysis")
    subparsers = parser.add_subparsers()

    # list command
    parser_list = subparsers.add_parser('list', help=
            "Lists available profiles")
    parser_list.set_defaults(func=list_profiles)

    # build command
    parser_build = subparsers.add_parser('build',
            help="Builds a Vagrant box based on a given profile")
    parser_build.add_argument('profile', help='Name of the profile to build. '
            'Use list command to view available profiles.')
    parser_build.set_defaults(func=build)

    # spin command
    parser_spin = subparsers.add_parser('spin', help=
            "Creates a Vagrantfile for your profile / Vagrant box")
    parser_spin.add_argument('profile', help='Name of the profile to spin.')
    parser_spin.add_argument('name', help='Name of the target VM. '
            'Must be unique on your system. Ex: Cryptolocker_XYZ')
    parser_spin.set_defaults(func=spin)

    # no command
    parser.set_defaults(func=default)

    args = parser.parse_args()
    return parser, args


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


def cleanup():
    """Removes temporary files"""
    for f in tempfiles:
        os.remove(CONFIG_CACHE + f)


def run_foreground(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    try:
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip().decode('utf-8'))

    # send Ctrl-C to packer
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip().decode('utf-8'))
        raise

    finally:
        p.wait()
        return p.returncode


def run_packer(packer_config):
    print("Starting packer to generate the VM")
    print("----------------------------------")

    cmd = ['packer-io', 'build', '-var-file=config.json', packer_config]
    ret = run_foreground(cmd)

    print("----------------------------------")
    print("packer completed with return code: {}".format(ret))
    return ret


def import_box(config, args):
    print("Importing box into vagrant")
    print("--------------------------")

    box = config['post-processors'][0]['output']
    box = box.replace('{{user `name`}}', args.profile)

    cmd = ['vagrant', 'box', 'add', box, '--name={}'.format(args.profile)]
    ret = run_foreground(cmd)

    print("----------------------------")
    print("vagrant box import completed with return code: {}".format(ret))
    return ret


def default(parser, args):
    parser.print_help()
    print("\n")
    list_profiles(parser, args)
    sys.exit(1)


def list_profiles(parser, args):
    print("supported profiles:\n")
    for f in sorted(glob.glob('profiles/*.json')):
        m = re.search(r'^profiles\/(.*).json$', f)
        print(m.group(1))
    print()


def build(parser, args):
    print("Generating configuration files...")
    result, config = load_config(args.profile)
    if not result:
        print("Profile doesn't exist")
        sys.exit(2)

    prepare_autounattend(config)
    print("Configuration files are ready")
    ret = run_packer('profiles/{}.json'.format(args.profile))
    if ret != 0:
        print("Packer failed. Build failed. Exiting...")
        sys.exit(3)

    ret = import_box(config, args)
    if ret != 0:
        print("'vagrant box add' failed. Build failed. Exiting...")
        sys.exit(4)

    print("A base box was imported into your local Vagrant box repository")
    print("You can re-use this base box several times by using the "
            "following statement in your Vagrantfile:")
    print('config.vm.box = "{}"'.format(args.profile))


def spin(parser, args):
    print("spin called, nothing to see here")
    #create_vagrantfile(config)

if __name__ == "__main__":
    try:
        parser, args = initialize()
        args.func(parser, args)

    finally:
        cleanup()

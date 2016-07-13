# Malboxes - Vagrant box builder and config generator for malware analysis
# https://github.com/gosecure/malboxes
#
# Olivier Bilodeau <obilodeau@gosecure.ca>
# Hugo Genesse <hugo.genesse@polymtl.ca>
# Copyright (C) 2016 GoSecure Inc.
# Copyright (C) 2016 Hugo Genesse
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
from pkg_resources import resource_filename
import re
import signal
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader

CONFIG_CACHE = 'config_cache'
__version__ = "0.1.0"

def initialize():
    parser = argparse.ArgumentParser(
                    description="Vagrant box builder "
                                "and config generator for malware analysis.")
    subparsers = parser.add_subparsers()

    # list command
    parser_list = subparsers.add_parser('list',
                                        help="Lists available profiles.")
    parser_list.set_defaults(func=list_profiles)

    # build command
    parser_build = subparsers.add_parser('build',
                                         help="Builds a Vagrant box based on "
                                              "a given profile.")
    parser_build.add_argument('profile', help='Name of the profile to build. '
                                              'Use list command to view '
                                              'available profiles.')
    parser_build.set_defaults(func=build)

    # spin command
    parser_spin = subparsers.add_parser('spin',
                                        help="Creates a Vagrantfile for "
                                             "your profile / Vagrant box.")
    parser_spin.add_argument('profile', help='Name of the profile to spin.')
    parser_spin.add_argument('name', help='Name of the target VM. '
                                          'Must be unique on your system. '
                                          'Ex: Cryptolocker_XYZ.')
    parser_spin.set_defaults(func=spin)

    # reg command
    parser_reg = subparsers.add_parser('registry',
                                       help='Modifies a registry key.')
    parser_reg.add_argument('profile', help='Name of the profile to modify.')
    parser_reg.add_argument('modtype',
                            help='Modification type (add, delete or modify).')
    parser_reg.add_argument('key', help='Location of the key to modify.')
    parser_reg.add_argument('name', help='Name of the key.')
    parser_reg.add_argument('value', help='Value of the key.')
    parser_reg.add_argument('valuetype',
                            help='Type of the value of the key: '
                                 'DWORD for integer, String for string.')
    parser_reg.set_defaults(func=reg)

    # dir command
    parser_dir = subparsers.add_parser('directory',
                                       help='Modifies a directory.')
    parser_dir.add_argument('profile',
                            help='Name of the profile to modify.')
    parser_dir.add_argument('modtype',
                            help='Modification type (delete or add).')
    parser_dir.add_argument('dirpath',
                            help='Path of the directory to modify.')
    parser_dir.set_defaults(func=directory)

    # wallpaper command

    # package command
    parser_package = subparsers.add_parser('package',
                                           help='Adds package to install.')
    parser_package.add_argument('profile',
                                help='Name of the profile to modify.')
    parser_package.add_argument('package',
                                help='Name of the package to install.')
    parser_package.set_defaults(func=package)

    # document command
    parser_document = subparsers.add_parser('document',
                                            help='Adds a file')
    parser_document.add_argument('profile',
                                 help='Name of the profile to modify.')
    parser_document.add_argument('modtype',
                                 help='Modification type (delete or add).')
    parser_document.add_argument('docpath',
                                 help='Path of the file to add.')
    parser_document.set_defaults(func=document)

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

    # Jinja2 splits on '/' so dont change for os.path.join
    env = Environment(loader=FileSystemLoader('installconfig/'))
    template = env.get_template("{}/Autounattend.xml".format(os_type))
    f = create_configfd('Autounattend.xml')
    f.write(template.render(config)) # pylint: disable=no-member
    f.close()


def load_config(profile):
    """
    Config is in JSON since we can re-use the same in both malboxes and packer
    """
    profile_file = os.path.join('profiles', '{}.json'.format(profile))
    # validate if profile is present
    if not os.path.isfile(profile_file):
        print("Profile doesn't exist")
        sys.exit(2)

    # load general config
    config = {}
    with open('config.json', 'r') as f:
        config = json.load(f)

    # merge/update with profile config
    with open(profile_file, 'r') as f:
        config.update(json.load(f))

    return config


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

    cmd = ['packer', 'build', '-var-file=config.json', packer_config]
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

    filepath = resource_filename(__name__, "profiles/")
    for f in sorted(glob.glob(os.path.join(filepath, '*.json'))):
        m = re.search(r'profiles[\/\\](.*).json$', f)
        print(m.group(1))
    print()


def build(parser, args):
    config = load_config(args.profile)

    print("Generating configuration files...")
    prepare_autounattend(config)
    print("Configuration files are ready")
    ret = run_packer(os.path.join('profiles',
                                  '{}.json'.format(args.profile)))
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
    """
    Creates a Vagrantfile based on a template using the jinja2 engine
    """
    config = load_config(args.profile)

    print("Creating a Vagrantfile")
    env = Environment(loader=FileSystemLoader('vagrantfiles'))
    template = env.get_template("analyst_single.rb")

    if os.path.isfile('Vagrantfile'):
        print("Vagrantfile already exists. Please move away.")
        sys.exit(5)

    config['profile'] = args.profile
    config['name'] = args.name

    with open("Vagrantfile", 'w') as f:
        f.write(template.render(config)) # pylint: disable=no-member
    print("Vagrantfile generated. You can move it in your analysis directory "
          "and issue a `vagrant up` to get started with your VM.")


def append_to_script(filename, line):
    """ Appends a line to a file."""
    with open(filename, 'a') as f:
        f.write(line)


def add_to_user_scripts(profile):
    """ Adds the modified script to the user scripts file."""
    """ File names for the user scripts file and the script to be added."""
    filename = os.path.join("scripts", "windows", "user_scripts.ps1")
    line = "{}.ps1".format(profile)

    """ Check content of the user scripts file."""
    with open(filename, "r") as f:
        content = f.read()

    """ If script isnt present, add it."""
    if content.find(line) == -1:
        with open(filename, "a") as f:
            f.write(line)


def reg(parser, args):
    """
    Adds a registry key modification to a profile with PowerShell commands.
    """
    if args.modtype == "add":
        command = "New-ItemProperty"
        line = "{} -Path {} -Name {} -Value {} -PropertyType {}\r\n".format(
            command, args.key, args.name, args.value, args.valuetype)
        print("Adding: " + line)
    elif args.modtype == "modify":
        command = "Set-ItemProperty"
        line = "{0} -Path {1} -Name {2} -Value {3}\r\n".format(
                command, args.key, args.name, args.value)
        print("Adding: " + line)
    elif args.modtype == "delete":
        command = "Remove-ItemProperty"
        line = "{0} -Path {1} -Name {2}\r\n".format(
                command, args.key, args.name)
        print("Adding: " + line)
    else:
        print("Registry modification type invalid.")
        print("Valid ones are: add, delete and modify.")

    filename = os.path.join("scripts", "user",
                            "windows", "{}.ps1".format(args.profile))
    append_to_script(filename, line)

    """ Adds the modified script to the user scripts."""
    add_to_user_scripts(args.profile)


def directory(parser, args):
    """ Adds the directory manipulation commands to the profile."""
    if args.modtype == "add":
        command = "New-Item"
        line = "{0} -Path {1} -Type directory\r\n".format(command,
                                                          args.dirpath)
        print("Adding directory: {}".format(args.dirpath))
    elif args.modtype == "delete":
        command = "Remove-Item"
        line = "{0} -Path {1}\r\n".format(
                command, args.dirpath)
        print("Removing directory: {}".format(args.dirpath))
    else:
        print("Directory modification type invalid.")
        print("Valid ones are: add, delete.")

    filename = os.path.join("scripts", "user",
                            "windows", "{}.ps1".format(args.profile))
    append_to_script(filename, line)

    """ Adds the modified script to the user scripts."""
    add_to_user_scripts(args.profile)


def package(parser, args):
    """ Adds a package to install with Chocolatey."""
    line = "cinst {} -y\r\n".format(args.package)
    print("Adding Chocolatey package: {}".format(args.package))

    filename = os.path.join("scripts", "user",
                            "windows", "{}.ps1".format(args.profile))
    append_to_script(filename, line)

    """ Adds the modified script to the user scripts."""
    add_to_user_scripts(args.profile)


def document(parser, args):
    """ Adds the file manipulation commands to the profile."""
    if args.modtype == "add":
        command = "New-Item"
        line = "{0} -Path {1}\r\n".format(command, args.docpath)
        print("Adding file: {}".format(args.docpath))
    elif args.modtype == "delete":
        command = "Remove-Item"
        line = "{0} -Path {1}\r\n".format(
                command, args.docpath)
        print("Removing file: {}".format(args.docpath))
    else:
        print("Directory modification type invalid.")
        print("Valid ones are: add, delete.")

    filename = os.path.join(
                    "scripts", "user", "windows",
                    "{}.ps1".format(args.profile))

    append_to_script(filename, line)

    """ Adds the modified script to the user scripts."""
    add_to_user_scripts(args.profile)

def main():
    try:
        parser, args = initialize()
        args.func(parser, args)

    finally:
        cleanup()


if __name__ == "__main__":
    main()

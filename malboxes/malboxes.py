# Malboxes - Vagrant box builder and config generator for malware analysis
# https://github.com/gosecure/malboxes
#
# Olivier Bilodeau <obilodeau@gosecure.ca>
# Hugo Genesse <hugo.genesse@polymtl.ca>
# Copyright (C) 2016, 2017 GoSecure Inc.
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
from io import TextIOWrapper
import json
import os
from pkg_resources import resource_filename, resource_stream
import re
import shutil
import signal
import subprocess
import sys
import textwrap

from appdirs import AppDirs
from jinja2 import Environment, FileSystemLoader
from jsmin import jsmin

from malboxes._version import __version__

DIRS = AppDirs("malboxes")
DEBUG = False

def initialize():
    # create appdata directories if they don't exist
    if not os.path.exists(DIRS.user_config_dir):
        os.makedirs(DIRS.user_config_dir)

    profile_dir = os.path.join(DIRS.user_config_dir, "profiles")

    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

    if not os.path.exists(DIRS.user_cache_dir):
        os.makedirs(DIRS.user_cache_dir)

    cache_scripts_dir = os.path.join(DIRS.user_cache_dir, "scripts", "user")

    if not (os.path.exists(cache_scripts_dir)):
        os.makedirs(cache_scripts_dir)

    return init_parser()

def init_parser():
    parser = argparse.ArgumentParser(
                    description="Vagrant box builder "
                                "and config generator for malware analysis.")
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-d', '--debug', action='store_true',
                        help="Debug mode. Leaves built VMs running on failure!")
    subparsers = parser.add_subparsers()

    # list command
    parser_list = subparsers.add_parser('list',
                                        help="Lists available templates.")
    parser_list.set_defaults(func=list_templates)

    # build command
    parser_build = subparsers.add_parser('build',
                                         help="Builds a Vagrant box based on "
                                              "a given template.")
    parser_build.add_argument('template', help='Name of the template to build. '
                                              'Use list command to view '
                                              'available templates.')
    parser_build.add_argument('--force', action='store_true',
                              help='Force the build to happen. Overwrites '
                                   'pre-existing builds or vagrant boxes.')
    parser_build.add_argument('--skip-packer-build', action='store_true',
                              help='Skip packer build phase. '
                                   'Only useful for debugging.')
    parser_build.add_argument('--skip-vagrant-box-add', action='store_true',
                              help='Skip vagrant box add phase. '
                                   'Only useful for debugging.')
    parser_build.set_defaults(func=build)

    # spin command
    parser_spin = subparsers.add_parser('spin',
                                        help="Creates a Vagrantfile for "
                                             "your template / Vagrant box.")
    parser_spin.add_argument('template', help='Name of the template to spin.')
    parser_spin.add_argument('name', help='Name of the target VM. '
                                          'Must be unique on your system. '
                                          'Ex: Cryptolocker_XYZ.')
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
    os_type = _get_os_type(config)

    filepath = resource_filename(__name__, "installconfig/")
    env = Environment(loader=FileSystemLoader(filepath))
    template = env.get_template("{}/Autounattend.xml".format(os_type))
    f = create_cachefd('Autounattend.xml')
    f.write(template.render(config)) # pylint: disable=no-member
    f.close()


def prepare_packer_template(config, template_name):
    """
    Prepares a packer template JSON file according to configuration and writes
    it into a temporary location where packer later expects it.

    Uses jinja2 template syntax to generate the resulting JSON file.
    Templates are in templates/ and snippets in templates/snippets/.
    """
    try:
        template_fd = resource_stream(__name__,
                                     'templates/{}.json'.format(template_name))
    except FileNotFoundError:
        print("Template doesn't exist: {}".format(template_name))
        sys.exit(2)

    filepath = resource_filename(__name__, 'templates/')
    env = Environment(loader=FileSystemLoader(filepath), autoescape=False,
                      trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("{}.json".format(template_name))

    # write to temporary file
    f = create_cachefd('{}.json'.format(template_name))
    f.write(template.render(config)) # pylint: disable=no-member
    f.close()
    return f.name


def _prepare_vagrantfile(config, source, fd_dest):
    """
    Creates Vagrantfile based on a template using the jinja2 engine. Used for
    spin and also for the packer box Vagrantfile. Based on templates in
    vagrantfiles/.
    """
    filepath = resource_filename(__name__, "vagrantfiles/")
    env = Environment(loader=FileSystemLoader(filepath))
    template = env.get_template(source)

    fd_dest.write(template.render(config)) # pylint: disable=no-member
    fd_dest.close()


def prepare_config(template):
    """
    Prepares Malboxes configuration and merge with Packer template configuration

    Packer uses a configuration in JSON so we decided to go with JSON as well.
    However since we have features that should be easily "toggled" by our users
    I wanted to add an easy way of "commenting out" or "uncommenting" a
    particular feature. JSON doesn't support comments. However JSON's author
    gives a nice suggestion here[1] that I will follow.

    In a nutshell, our configuration is Javascript, which when minified gives
    JSON and then it gets merged with the selected template.

    [1]: https://plus.google.com/+DouglasCrockfordEsq/posts/RK8qyGVaGSr
    """
    # if config does not exist, copy default one
    config_file = os.path.join(DIRS.user_config_dir, 'config.js')
    if not os.path.isfile(config_file):
        print("Default configuration doesn't exist. Populating one: {}"
              .format(config_file))
        shutil.copy(resource_filename(__name__, 'config-example.js'),
                    config_file)

    config = load_config(config_file, template)

    if "profile" in config.keys():
        profile_config = prepare_profile(template, config)

        # profile_config might contain a profile not in the config file
        config.update(profile_config)

    packer_tmpl = prepare_packer_template(config, template)

    # merge/update with template config
    with open(packer_tmpl, 'r') as f:
        config.update(json.loads(f.read()))

    return config, packer_tmpl


def load_config(config_filename, template):
    """Loads the minified JSON config. Returns a dict."""

    config = {}
    with open(config_filename, 'r') as config_file:
        # minify then load as JSON
        config = json.loads(jsmin(config_file.read()))

    # add packer required variables
    # Note: Backslashes are replaced with forward slashes (Packer on Windows)
    config['cache_dir'] = DIRS.user_cache_dir.replace('\\', '/')
    config['dir'] = resource_filename(__name__, "").replace('\\', '/')
    config['template_name'] = template
    config['config_dir'] = DIRS.user_config_dir.replace('\\', '/')

    # add default values
    # for users upgrading from versions where those values weren't defined
    # I don't want default to override the config so I reversed the merge logic
    default = {'hypervisor': 'virtualbox'}
    default.update(config)
    config = default

    return config


def load_profile(profile_name):
    filename = os.path.join(
        DIRS.user_config_dir.replace('\\', '/'),
        "profiles",
        "{}.js".format(profile_name))

    """Loads the profile, minifies it and returns the content."""
    with open(filename, 'r') as profile_file:
        profile = json.loads(jsmin(profile_file.read()))
    return profile


def _get_os_type(config):
    """OS Type is extracted from template json config.
       For older hypervisor compatibility, some values needs to be updated here.
    """
    _os_type = config['builders'][0]['guest_os_type'].lower()
    if config['hypervisor'] == 'vsphere':
        if _os_type == 'windows8':
            _os_type = 'windows10'
        elif _os_type == 'windows8-64':
            _os_type = 'windows10_64'

    return _os_type


tempfiles = []
def create_cachefd(filename):
    tempfiles.append(filename)
    return open(os.path.join(DIRS.user_cache_dir, filename), 'w')


def cleanup():
    """Removes temporary files. Keep them in debug mode."""
    if not DEBUG:
        for f in tempfiles:
            os.remove(os.path.join(DIRS.user_cache_dir, f))


def run_foreground(command, env=None):
    if DEBUG:
        print("DEBUG: Executing {}".format(command))

    cmd_env = os.environ.copy()
    if env is not None:
        cmd_env.update(env)

    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, env=cmd_env)
    try:
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip().decode('utf-8'))

    # send Ctrl-C to subprocess
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip().decode('utf-8'))
        raise

    finally:
        p.wait()
        return p.returncode


def run_packer(packer_tmpl, args):
    print("Starting packer to generate the VM")
    print("----------------------------------")

    prev_cwd = os.getcwd()
    os.chdir(DIRS.user_cache_dir)

    try:
        # packer or packer-io?
        binary = 'packer-io'
        if shutil.which(binary) == None:
            binary = 'packer'
            if shutil.which(binary) == None:
                print("packer not found. Install it: "
                      "https://www.packer.io/docs/install/index.html")
                return 254

        # run packer with relevant config minified
        configfile = os.path.join(DIRS.user_config_dir, 'config.js')
        with open(configfile, 'r') as config:
            f = create_cachefd('packer_var_file.json')
            f.write(jsmin(config.read()))
            f.close()

        flags = ['-var-file={}'.format(f.name)]

        special_env = {'PACKER_CACHE_DIR': DIRS.user_cache_dir}
        special_env['TMPDIR'] = DIRS.user_cache_dir
        if DEBUG:
            special_env['PACKER_LOG']  = '1'
            flags.append('-on-error=abort')

        if args.force:
            flags.append('-force')

        cmd = [binary, 'build']
        cmd.extend(flags)
        cmd.append(packer_tmpl)
        ret = run_foreground(cmd, special_env)

    finally:
        os.chdir(prev_cwd)

    print("----------------------------------")
    print("packer completed with return code: {}".format(ret))
    return ret


def add_box(config, args):
    print("Adding box into vagrant")
    print("--------------------------")

    box = config['post-processors'][0]['output']
    box = os.path.join(DIRS.user_cache_dir, box)
    box = box.replace('{{user `name`}}', args.template)

    flags = ['--name={}'.format(args.template)]
    if args.force:
        flags.append('--force')

    cmd = ['vagrant', 'box', 'add']
    cmd.extend(flags)
    cmd.append(box)
    ret = run_foreground(cmd)

    print("----------------------------")
    print("vagrant box add completed with return code: {}".format(ret))
    return ret


def default(parser, args):
    parser.print_help()
    print("\n")
    list_templates(parser, args)
    sys.exit(1)


def list_templates(parser, args):
    print("supported templates:\n")

    filepath = resource_filename(__name__, "templates/")
    for f in sorted(glob.glob(os.path.join(filepath, '*.json'))):
        m = re.search(r'templates[\/\\](.*).json$', f)
        print(m.group(1))
    print()


def build(parser, args):

    print("Generating configuration files...")
    config, packer_tmpl = prepare_config(args.template)
    prepare_autounattend(config)
    _prepare_vagrantfile(config, "box_win.rb", create_cachefd('box_win.rb'))
    print("Configuration files are ready")

    if not args.skip_packer_build:
        ret = run_packer(packer_tmpl, args)
    else:
        ret = 0

    if ret != 0:
        print("Packer failed. Build failed. Exiting...")
        sys.exit(3)

    if not args.skip_vagrant_box_add:
        ret = add_box(config, args)
    else:
        ret = 0

    if ret != 0:
        print("'vagrant box add' failed. Build failed. Exiting...")
        sys.exit(4)

    if not args.skip_vagrant_box_add:
        print(textwrap.dedent("""
        ===============================================================
        A base box was imported into your local Vagrant box repository.
        You should generate a Vagrantfile configuration in order to
        launch an instance of your box:

        malboxes spin {} <analysis_name>

        You can safely remove the {}/boxes/
        directory if you don't plan on hosting or sharing your base box.

        You can re-use this base box several times by using `malboxes
        spin`. Each VM will be independent of each other.
        ===============================================================""")
        .format(args.template, DIRS.user_cache_dir))


def spin(parser, args):
    """
    Creates a Vagrantfile meant for user-interaction in the current directory.
    """
    if os.path.isfile('Vagrantfile'):
        print("Vagrantfile already exists. Please move it away. Exiting...")
        sys.exit(5)

    config, _ = prepare_config(args.template)

    config['template'] = args.template
    config['name'] = args.name

    print("Creating a Vagrantfile")
    if config['hypervisor'] == 'virtualbox':
        with open("Vagrantfile", 'w') as f:
            _prepare_vagrantfile(config, "analyst_single.rb", f)
    elif config['hypervisor'] == 'vsphere':
        with open("Vagrantfile", 'w') as f:
            _prepare_vagrantfile(config, "analyst_vsphere.rb", f)
    print("Vagrantfile generated. You can move it in your analysis directory "
          "and issue a `vagrant up` to get started with your VM.")


def prepare_profile(template, config):
    """Converts the profile to a powershell script."""

    profile_name = config["profile"]

    profile_filename = os.path.join(DIRS.user_config_dir, "profiles",
                                    '{}.js'.format(profile_name))

    # if profile file doesn't exist, populate it from default
    if not os.path.isfile(profile_filename):
        shutil.copy(resource_filename(__name__, 'profile-example.js'),
                    profile_filename)
        print("WARNING: A profile was specified but was not found on disk. "
              "Copying a default one.")

    profile = load_profile(profile_name)

    fd = create_cachefd('profile-{}.ps1'.format(profile_name))

    if "registry" in profile:
        for reg_mod in profile["registry"]:
            registry(profile_name, reg_mod, fd)

    if "directory" in profile:
        for dir_mod in profile["directory"]:
            directory(profile_name, dir_mod["modtype"], dir_mod["dirpath"], fd)

    if "document" in profile:
        for doc_mod in profile["document"]:
            document(profile_name, doc_mod["modtype"], doc_mod["docpath"], fd)

    if "package" in profile:
        for package_mod in profile["package"]:
            package(profile_name, package_mod["package"], fd)

    if "packer" in profile:
        packer = profile["packer"]
        if "provisioners" in packer:
            config["packer_extra_provisioners"] = packer["provisioners"]

    fd.close()
    return config


def registry(profile_name, reg_mod, fd):
    """
    Adds a registry key modification to a profile with PowerShell commands.
    """
    if reg_mod["modtype"] == "add":
        command = "New-ItemProperty"
        line = '{} -Path "{}" -Name "{}" -Value "{}" -PropertyType "{}"\r\n' \
            .format(command, reg_mod["key"], reg_mod["name"], reg_mod["value"],
                    reg_mod["valuetype"])
    elif reg_mod["modtype"] == "modify":
        command = "Set-ItemProperty"
        line = '{0} -Path "{1}" -Name "{2}" -Value "{3}"\r\n'.format(
            command, reg_mod["key"], reg_mod["name"],
            reg_mod["value"])
    elif reg_mod["modtype"] == "delete":
        command = "Remove-ItemProperty"
        line = '{0} -Path "{1}" -Name "{2}"\r\n'.format(command,
                                                        reg_mod["key"],
                                                        reg_mod["name"])
    else:
        print("Registry modification type invalid.")
        print("Valid ones are: add, delete and modify.")
        return

    print("Adding: " + line, end='')
    fd.write(line)


def directory(profile_name, modtype, dirpath, fd):
    """ Adds the directory manipulation commands to the profile."""
    if modtype == "add":
        command = "New-Item"
        line = '{0} -Path "{1}" -Type directory\r\n'.format(command, dirpath)
        print("Adding directory: {}".format(dirpath))
    elif modtype == "delete":
        command = "Remove-Item"
        line = '{0} -Path "{1}"\r\n'.format(command, dirpath)
        print("Removing directory: {}".format(dirpath))
    else:
        print("Directory modification type invalid.")
        print("Valid ones are: add, delete.")

    fd.write(line)


def package(profile_name, package_name, fd):
    """ Adds a package to install with Chocolatey."""
    line = "choco install {} -y\r\n".format(package_name)
    print("Adding Chocolatey package: {}".format(package_name))

    fd.write(line)


def document(profile_name, modtype, docpath, fd):
    """ Adds the file manipulation commands to the profile."""
    if modtype == "add":
        command = "New-Item"
        line = '{0} -Path "{1}" -ItemType file\r\n'.format(command, docpath)
        print("Adding file: {}".format(docpath))
    elif modtype == "delete":
        command = "Remove-Item"
        line = '{0} -Path "{1}"\r\n'.format(command, docpath)
        print("Removing file: {}".format(docpath))
    else:
        print("Document modification type invalid.")
        print("Valid ones are: add, delete.")

    fd.write(line)


def main():
    global DEBUG
    try:
        parser, args = initialize()
        if args.debug:
            DEBUG = True
        args.func(parser, args)

    finally:
        cleanup()


if __name__ == "__main__":
    main()

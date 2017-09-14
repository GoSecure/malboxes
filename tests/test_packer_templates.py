#!/usr/bin/env python3
#
# This file is part of the Malboxes project.
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
import glob
import json
import os
import re
import sys
import unittest

from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

from malboxes.malboxes import load_config

class PackerTemplateTestCase(unittest.TestCase):

    def setUp(self):
        self.env = Environment(loader=FileSystemLoader('malboxes/templates/'),
                               autoescape=False)

    def test_packer_template_rendering(self):
        for profile in glob.glob("malboxes/templates/*.json"):
            print("Processing file {}".format(profile))

            # process profile
            profile_name = os.path.basename(profile)
            args = SimpleNamespace()
            args.template = re.match('(.*).json$', profile_name).group(1)
            config = load_config('malboxes/config-example.js', args)

            try:
                template = self.env.get_template(os.path.basename(profile_name))
                profile_json = template.render(config) # pylint: disable=no-member
                print("Properly formatted Jinja2 template")
            except:
                print("Badly formatted Jinja2 template! Failing test...")
                raise()

            # test if json is valid
            try:
                json.loads(profile_json)
                print("Properly formatted JSON file")
            except:
                print("Badly formatted JSON file! Failing test...")
                raise()

if __name__ == '__main__':
        unittest.main()

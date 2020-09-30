#!/usr/bin/env python2
# webdriver.py: A webdriver abstraction. -*- coding: utf-8 -*-

# Copyright (C) 2020. Mauro Aranda

# This file is part of Automail-HT.

# Automail-HT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Automail-HT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Automail-HT.  If not, see <https://www.gnu.org/licenses/>.


# Imports to find the installed webdrivers.
import subprocess
from subprocess import CalledProcessError

class Webdriver ():
    "Webdriver abstraction."
    def __init__ (self, webdriver_name, webbrowser_name, args):
        self.name = webdriver_name
        self.webbrowser = webbrowser_name
        self.args = args

    def is_installed_p (self):
        "Find if this webdriver is installed."
        try:
            subprocess.check_output (self.name + " " + self.args["version"],
                                     stderr = subprocess.STDOUT,
                                     shell = True)
        except CalledProcessError:
            return False
        else:
            return True

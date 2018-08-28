#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2018. Mauro Aranda

# This file is part of Automatizador de HT-Mails.

# Automatizador de HT-Mails is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Automatizador de HT-Mails is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Automatizador de HT-Mails.  If not, see <https://www.gnu.org/licenses/>.

# createFirefoxProfile.py: Creates a Firefox Profile, suitable for the
# automation required by HTMails application.  Useful if the Web Extension
# is going to be used.

# Imports for putting the firefox profile where firefox looks for it.
import subprocess
import os
import sys
from shutil import copyfile

import HTMailsGUI

try:
    # Try to create the profile.  The firefox output is sent to stderr.
    err_output = subprocess.check_output("firefox -CreateProfile HTMailsAutomationProfile",
                                        stderr = subprocess.STDOUT,
                                        shell = True)
    # Run firefox profile, so profile gets filled with firefox built files
    subprocess.call(["firefox -P HTMailsAutomationProfile -silent"],
                    shell = True)
except:
    print "El perfil de Firefox necesario no pudo crearse"
    sys.exit()
else:
    # Get profile folder
    err_output = err_output.replace('\n', '')
    profile_path = err_output.rsplit(' ', 1)[-1]
    profile_path = profile_path.rsplit(os.sep, 1)[0]
    # Don't know why, but there's an extra ' present
    profile_path = profile_path.replace('\'', '')

    try:
        # Save where the profile got stored.
        f = open(HTMailsGUI.get_thisfile_directory() + os.pardir + \
                 os.sep + "data" + os.sep + "pathToProfile.txt", "w+")
        f.write(profile_path)
    except:
        print "No pudo guardarse la direccion del perfil de Firefox"
        f.close()
        sys.exit()
    else:
        f.close()

        try:
            # Move the handlers.json (without it, the web extension could
            # not be found.
            # FIXME: Is that so?
            f = open(HTMailsGUI.get_thisfile_directory() + os.pardir + \
                     os.sep + "data" + os.sep + "pathToProfile.txt", "r")
            profile_path = f.read()
            f.close()
            copyfile(HTMailsGUI.get_thisfile_directory() + os.pardir + \
                     os.sep + "build-aux" + os.sep + "handlers.json",
                     profile_path + os.sep + "handlers.json")
        except:
            print "No pudo copiarse handlers.json a la carpeta del perfil"
            sys.exit()

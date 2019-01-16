#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2019. Mauro Aranda

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


# HTMails.py: Main entry for HT-Mails automation application

# Import the GUI:
import HTMailsGUI

# Imports for config file
import os
import json

# Check if config.json file exists.  If not, create it with hard-coded values
try:
    if not (os.path.isfile(HTMailsGUI.get_thisfile_directory() + \
                           os.pardir + os.sep + "config.json")):
        
        default_values = {"Usuario": "", "Directorio Default": "src",
                          "Navegador Default": "Firefox"}
        config_file = open(HTMailsGUI.get_thisfile_directory() + \
                           os.pardir + os.sep + 'config.json', 'w')
        json.dump(default_values, config_file, indent = 4,
                  separators = (",", ": "))
        config_file.close()
except IOError:
    print "El programa se inicializara, pero no se pudo cargar el archivo",
    print "de configuraciones config.json"
finally:
    # Create GUI and start application
    HTMails = HTMailsGUI.GUI()
    HTMails.mainloop()

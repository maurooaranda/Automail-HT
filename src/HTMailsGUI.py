#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2018. Mauro Aranda

# This file is part of Automatizador de HT-Mails.

# This file is part of Automail-HT.

# Automail-HT free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Automail-HT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Automail-HT.  If not, see <https://www.gnu.org/licenses/>.


# HTMailsGUI.py: This is the HTMails Automation GUI

# Imports for GUI
from Tkinter import *
from tkMessageBox import *
import tkFileDialog
import tkSimpleDialog
import ttk

# Import for WebAutomation
import automation

# Imports for manipulating spreadsheet
import spreadsheet
import htmails_ss

# Import for directory manipulations
import os.path

# Import for reading latin-1 file
import io

# For waiting
import time

# Import json, for config.json
import json

# Imports to find the installed webdrivers
import subprocess
from subprocess import CalledProcessError

# TODO: How to do i18n with Python??
# TODO: Does Tk support Unicode??

class GUI(Tk):
    """HTMails Automation GUI"""

    def __init__(self):
        """Creates all GUI Widgets: MenuBar, Labels, TextBoxs, Buttons etc."""
  
        # Overhead code, to initialise Tkinter Frame
        self.root = Tk.__init__(self)
        self.frame = Frame(self.root)
        self.title("Automail-HT")
        self.geometry("650x275")

        # TODO: Add icon
        # self.add-icon()
        
        self.frame.grid(sticky = W+E+N+S)

        # Create MenuBar with items
        self.create_menubar()
        
        # Create widgets
        self.create_widgets()
        
        # configure grid
        self.rowconfigure(4, weight = 1)
        self.columnconfigure(3, weight = 1)

        # Find webdrivers that are installed, to fill combobox
        self.fill_combobox(self.combo_webdriver,
                           get_installed_webdrivers())
        
        # Set default values
        self.set_default_values()
        
        # Events
        self.txt_password.bind("<Return>", self._sendHTMails)
        self.btn_sendHTMails.bind("<Enter>", self.rollover_enter)
        self.btn_sendHTMails.bind("<Leave>", self.rollover_leave)
        self.btn_exit.bind("<Enter>", self.rollover_enter)
        self.btn_exit.bind("<Leave>", self.rollover_leave)
        
    # def add_icon(self):
    #     """Adds an icon.  The use depends on the window manager"""
        
    #     # Create the bitmap
    #     icon = Image('photo',
    #                  file = get_thisfile_directory() + os.pardir + os.sep + \
    #                  'img/the-icon.gif')
    #     self.tk.call('wm', 'iconphoto', self.master._w, icon)
    
    def create_menubar(self):
        """Creates the MenuBar for the application. Menu is:
        # Archivo  -> Enviar Mails | Salir
        # Editar   -> Usuario ||
        #          -> Valores por Defecto
        # Ayuda    -> Manual ||
        #          -> Info ||
        #          -> Licencia"""

        menubar = Menu(self)

        filemenu = Menu(menubar, tearoff = 0)
        filemenu.add_command(label = "Enviar Mails", command = self.sendHTMails)
        filemenu.add_command(label = "Salir", command = self.destroy)
        menubar.add_cascade(label = "Archivo", menu = filemenu)

        editmenu = Menu(menubar, tearoff = 0)
        editmenu.add_command(label = "Usuario", command = self.change_user)
        editmenu.add_command(label = "Valores por defecto",
                             command = self.change_default_fields)
        menubar.add_cascade(label = "Editar", menu = editmenu)

        helpmenu = Menu(menubar, tearoff = 0)
        helpmenu.add_command(label = "Manual", command = self.show_manual)
        helpmenu.add_command(label = "Informacion",
                             command = self.show_information)
        helpmenu.add_command(label = "Licencia", command = self.show_license)
        menubar.add_cascade(label = "Ayuda", menu = helpmenu)

        self.config(menu = menubar)

    def create_widgets(self):
        """Creates all the widgets for the GUI"""
        # static labels:
        self.lbl_user = Label(self, text = "Usuario: ")
        self.lbl_password = Label(self, text = "Clave: ")
        self.lbl_webdriver = Label(self, text = "Navegador: ")
        self.lbl_spreadsheet = Label(self, text = "Planilla: ")

        # textboxs:
        self.user = StringVar()
        self.user.set("")
        self.txt_user = Entry(self, name = "txt_user",
                              textvariable = self.user)
        # Make txtPassword display text as "*"
        self.password = StringVar()
        self.password.set("")
        self.txt_password = Entry(self, name = "txt_password", show = "*",
                                  textvariable = self.password)

        self.spreadsheet_path = StringVar()
        self.spreadsheet_path.set("")
        self.txt_spreadsheet_path = Entry(self, name = "txt_spreadsheet_path",
                                          textvariable = self.spreadsheet_path)
        self.txt_spreadsheet_path.config(state = "readonly")
        
        # Buttons
        self.btn_select_spreadsheet = Button(self, text = "...",
                                             command = self.get_spreadsheet,
                                             height = 1)        
        self.btn_sendHTMails = Button(self, text = "Enviar HTMails",
                                      command = self.sendHTMails,
                                      height = 2,
                                      width = 10)
        self.btn_exit = Button(self, text = "Salir", command = self.destroy,
                               height = 2, width = 10)

        # Webdrivers combo box
        self.combo_webdriver = ttk.Combobox(self)
        self.combo_webdriver.config(state = "readonly")

        # Browser extension checkbutton
        self.use_htmails_extension = IntVar()
        self.chk_use_htmails_extension = \
            Checkbutton(self, text = "Usar extension de HTMails",
                        variable = self.use_htmails_extension)

        # Automation-HT won't ask for login info
        self.no_login_info = IntVar()
        self.chk_no_login_info = \
            Checkbutton(self, text = "Poner información de logueo en HT",
                        variable = self.no_login_info)

        # FIXME: Disable the checkbutton for now, until the web extension
        # is supported
        self.chk_use_htmails_extension.config(state = DISABLED)
        
        # Put widgets on frame
        self.lbl_user.grid(row = 1, column = 0, padx = 10, pady = 0,
                          sticky = E)
        self.lbl_password.grid(row = 2, column = 0, padx = 10, pady = 0,
                              sticky = E)
        self.lbl_webdriver.grid(row = 1, column = 2, padx = 10, pady = 10,
                                sticky = E)
        self.lbl_spreadsheet.grid(row = 3, column = 0, padx = 10, pady = 10,
                                  sticky = E)
        self.txt_user.grid(row = 1, column = 1, padx = 0, pady = 10)
        self.txt_password.grid(row = 2, column = 1, padx = 0, pady = 10)
        self.txt_spreadsheet_path.grid(row = 3, column = 1, padx = 0, pady = 10,
                                  sticky = E)
        self.btn_sendHTMails.grid(row = 4, column = 1, padx = 10, pady = 10,
                                  sticky = W)
        self.btn_exit.grid(row = 4, column = 2, padx = 10, pady = 10,
                           sticky = W)
        self.btn_select_spreadsheet.grid(row = 3, column = 2, sticky = W)
        self.combo_webdriver.grid(row = 1, column = 3, sticky = W)
        self.chk_use_htmails_extension.grid(row = 2, column = 3, sticky = W)
        self.chk_no_login_info.grid(row = 3, column = 3, sticky = W)

    def fill_combobox(self, cbo, values):
        """Fills the combobox CBO, with VALUES"""
        
        cbo["values"] = values
            
    def set_default_values(self):
        """Sets default values of fields"""

        try:
            config_file = open(get_thisfile_directory() + os.pardir + \
                              os.sep + "config.json")
            default_values = json.load(config_file)
            config_file.close()
        except IOError:
            # In case of failing to read config_file, do this to avoid
            # excepcion when calling askopenfilename.  See Issue #1
            self.user.set("")
            self.combo_webdriver.set(self.combo_webdriver["values"][0])
            self.default_directory = os.path.expanduser("~")
            showinfo("Error", "No pudo abrirse el archivo config.json")
        else:
            self.user.set(default_values["Usuario"])

            # Set the default driver.  Default to the first if the default
            # browser has no webdriver installed (or supported).
            if default_values["Navegador Default"] in list(self.combo_webdriver["values"]):
                self.combo_webdriver.set(default_values["Navegador Default"])
            else:
                self.combo_webdriver.set(self.combo_webdriver["values"][0])

            # Maybe expand the default directory, based on '~' or 'src'
            if (default_values["Directorio Default"] == "~"):
                self.default_directory = os.path.expanduser("~")
            elif (default_values["Directorio Default"] == "src"):
                self.default_directory = get_thisfile_directory() + \
                    os.pardir + os.sep
            else:
                self.default_directory = default_values["Directorio Default"]
                
    def get_spreadsheet(self):
        """Prompts the user to find the path to the spreadsheet to be used"""

        self.spreadsheet_path.set(tkFileDialog.askopenfilename(
            initialdir = self.default_directory,
            title = "Selecciona la planilla",
            filetypes = [("Hojas de datos", "*.xls* *.ods"),
                         ("All files", "*.*")]))
        # Show last part of the file selected
        self.txt_spreadsheet_path.xview_moveto(1)
        
    def validate_entry(self):
        """Checks if textboxs are not empty"""

        # Only check spreadsheet_path, if no_login_info is used.
        if self.spreadsheet_path.get() != "":
            if self.no_login_info.get() == 1:
                return True
            else:
                return (self.user.get() != "" and self.password.get() != "")
        else:
            return False
        # return (self.user.get() != "" and \
        #         self.password.get() != "" and \
        #         self.spreadsheet_path.get() != "")

    def get_message_paths(self):
        """Prompts the user for the paths to the messages templates to be 
        used.  The total messages are retrieved from the spreadsheet."""

        message_paths = []
        total_messages = self.htmails_file.get_total_messages()

        for message in range(total_messages):
            file_path = tkFileDialog.askopenfilename(
                initialdir = self.default_directory,
                title = "Selecciona el mensaje " + str(message + 1),
                filetypes = [("Archivos de texto", "*.txt")])

            message_paths.append(file_path)

            # If the user doesn't give one message, break.
            if (file_path == ""):
                break
            
        return message_paths       
        
    def _sendHTMails(self, event):
        """Stub function that calls the real function, sendHTMails.
        Needed because can't call sendHTMails from event <Return> on
        Entry widget"""
        
        self.sendHTMails()

    def sendHTMails(self):
        """Starts the automation of sending HTMails"""

        # If all textboxs contain text, execute
        if self.validate_entry():

            # Try to read the spreadsheet file
            self.htmails_file = \
                htmails_ss.htmails_ss(self.spreadsheet_path.get())

            # Get the paths to the messages.
            message_paths = self.get_message_paths()

            # See if there's no error with the templates.
            if '' in message_paths:
                showinfo("Error",
                         "Error en el numero de mensajes. Revisar")
                return None
            else:
                # Get all the data
                data = self.htmails_file.get_fields()

                # Sort the data by message number.
                # This is to avoid loading all 4 mail templates in memory.
                # Instead, load the one being used, and send all the messages
                # that require that message number.
                data = \
                    sorted(data,
                           key = lambda player: player[self.htmails_file.preferences["Headers"].index("Mensaje")])

                # Start driver
                self.driver = automation.ht_driver(self.combo_webdriver.get())
                self.driver.visit_mainpage()

                if self.no_login_info.get() == 1:
                    login_values = None
                else:
                    login_values = [self.user.get(), self.password.get()]
            
                if self.driver.login(login_values):
                    # `i' holds the template message being used.
                    # Once all those mails are sent, increment it to use
                    # the next template.
                    i = 1

                    # Read the mail_template
                    mail_template = read_textfile(message_paths[i - 1])

                    # Fallidos.txt will be created (or overwrited) the first
                    # time one mail fails.  Then, all failed mails in the
                    # current run will be appended
                    created_failed_file = False

                    # For each row, customize the mail and send it.
                    for field in data:
                        # Change to the next template when needed.
                        if (field[self.htmails_file.preferences["Headers"].index("Mensaje")] != i):
                            i = field[self.htmails_file.preferences["Headers"].index("Mensaje")]
                            mail_template = read_textfile(message_paths[i - 1])

                        mail = self.customize_mail(mail_template,
                                                   self.htmails_file.preferences["Headers"],
                                                   field)
                        subject, content = mail.split("\n", 1)
                        subject = get_subject(subject)
                        content = get_content(content)

                        # Try to send the mail, and if it was not sent
                        # (a.k.a, driver.sendHTMail returns False), append data
                        # to fallidos.txt
                        if not (self.driver.sendHTMail(subject, content, field,
                                                       self.htmails_file.preferences["Headers"].index("ID Jugador"),
                                                       self.htmails_file.preferences["BlackList"], False)):
                            if (not created_failed_file):
                                create_failed_file(get_thisfile_directory() + \
                                                   os.pardir)
                                created_failed_file = True
                                
                            # TODO: Add description of the reason it failed
                            dump_failed_email(field,
                                              get_thisfile_directory() + \
                                              os.pardir)
                        time.sleep(self.htmails_file.preferences["Seconds_wait"])
                else:
                    showinfo("Error",
                             "El login no fue posible. Revisar campos")

                # Exit driver
                self.driver.destroy()

        else:
            showinfo("Error", "Uno o mas campos estan vacios")

    def customize_mail(self, mail, reference, data):
        """Replaces keywords on the template"""

        # Add Apodo, only if it is given.
        try:
            reference.index("Nombre Jugador")
        except ValueError:
            if (mail.find("{0}") != -1):
                mail = replace_keyword(mail, "{0}", "")
                mail = replace_keyword(mail, "{6}", "")
        else:
            try:
                reference.index("Apodo Jugador")
            except ValueError:
                mail = replace_keyword(mail, "{0}",
                                       data[reference.index("Nombre Jugador")])
                mail = replace_keyword(mail, "{6}", "")
            else:
                if data[reference.index("Apodo Jugador")]:
                    # Apodo is added before the surname, between "'" quotes.
                    # If the player has two surnames, then it fails.
                    # FIXME: Add it after the first name?
                    name = data[reference.index("Nombre Jugador")].rsplit(" ", 1)
                    mail = replace_keyword(mail, "{0}", name[0] + " '" + \
                                           data[reference.index("Apodo Jugador")] + \
                                           "' " + name[1])
                else:
                    mail = replace_keyword(mail, "{0}",
                                           data[reference.index("Nombre Jugador")])

        try:
            reference.index("ID Jugador")
        except ValueError:
            if (mail.find("{1}") != -1):
                mail = replace_keyword(mail, "{1}", "")
        else:
            mail = replace_keyword(mail, "{1}",
                                   data[reference.index("ID Jugador")])

        try:
            reference.index("Nombre Usuario")
        except ValueError:
            if (mail.find("{2}") != -1):
                mail = replace_keyword(mail, "{2}", "")
        else:
            mail = replace_keyword(mail, "{2}",
                                   data[reference.index("ID Jugador")])

        try:
            reference.index(u"Fecha de Promoción")
        except ValueError: 
            if (mail.find("{3}") != -1):
                mail = replace_keyword(mail, "{3}", "")
        else:
            mail = replace_keyword(mail, "{3}",
                                   data[reference.index(u"ID Jugador")])
            
        mail = replace_keyword(mail, "{4}", self.htmails_file.get_thread_id())

        try:
            reference.index(u"Condición")
        except ValueError:
            if (mail.find("{5}") != -1):
                mail = replace_keyword(mail, "{5}", "")
        else:
            mail = replace_keyword(mail, "{5}",
                                   data[reference.index(u"Condición")])

        # FIXME: If no thread link is given, then "None" persists.
        # That's why this line is required.
        mail = replace_keyword(mail, "None", "")

        return mail
        
    def rollover_enter(self, event):
        """Set button to GROOVE"""
        
        event.widget.config(relief = GROOVE)
    
    def rollover_leave(self, event):
        """Set button to RAISED"""
        
        event.widget.config(relief = RAISED)

    def change_user(self):
        new_value = tkSimpleDialog.askstring("Usuario", "")

        if new_value:
            self.user.set(new_value)
        
    def change_default_fields(self):
        """Change User default values"""

        try:
            self.change_default_user()
            self.change_default_directory()
            self.change_default_webdriver()
        except IOError:
            # If config.json cannot be opened, then catch the error here.
            showerror("Error", "No pudo abrirse el archivo 'config.json'")

    def change_default_user(self):
        """ Change default user"""
        
        new_value = tkSimpleDialog.askstring("Usuario", "")
        self.change_config_file("Usuario", new_value)

    def change_default_directory(self):
        """Change default destination of folder for the dialogs"""
        
        new_value = tkSimpleDialog.askstring("Directorio", "")
        self.change_config_file("Directorio Default", new_value)

    def change_default_webdriver(self):
        """Change the default webdriver for automation"""

        new_value = tkSimpleDialog.askstring("Navegador", "")
        self.change_config_file("Navegador Default", new_value)
    
    def change_config_file(self, field, value):
        """Modifies config file"""
        
        config_file = open(get_thisfile_directory() + os.pardir + os.sep + \
                           "config.json")
        default_values = json.load(config_file)
        config_file.close()
        
        default_values[field] = value

        config_file = open(get_thisfile_directory() + os.pardir + os.sep + \
                          "config.json", 'w')
        json.dump(default_values, config_file)
        config_file.close()
    
    def show_manual(self):
        manual_frame = Toplevel()
        manual_frame.title("Manual")

        msg = Label(manual_frame, text = "Por favor, lee el archivo etc/TIPS")
        msg.pack()
    
    def show_information(self):
        info_frame = Toplevel()
        info_frame.title("Informacion")

        msg = Label(info_frame, text = \
                    """Este programa fue creado por Mauro Aranda.
Version: 4.0
mail: maurooaranda@gmail.com

Copyright (C) 2018 Mauro Aranda.""")
        msg.pack()

    def show_license(self):
        license_frame = Toplevel()
        license_frame.title("Licencia")

        msg = Label(license_frame, text = """Copyright (C) 2018 Mauro Aranda.
        Automail-HT comes with ABSOLUTELY NO WARRANTY.
        You may redistribute copies of Automail-HT
        under the terms of the GNU General Public License.""")
        msg.pack()

    def destroy(self):
        self.quit()

# TODO: Find a place where to put this functions.        
def get_thisfile_directory():
    """Helper function for obtaining directory of the software"""
    
    return (os.path.dirname(os.path.realpath(__file__)) + os.sep)

def is_webdriver_installed(webdriver):
    """Finds if WEBDRIVER is installed, by calling the semi-standard
    `WEBDRIVER -V'"""

    # If `WEBDRIVER -V' cannot be executed, then we assume it is not installed.
    # (Selenium wouldn't find it anyway).
    # When the call fails, a CalledProcessError exception is raised.
    try:
        subprocess.check_output(webdriver + " -V", stderr = subprocess.STDOUT,
                                shell = True)
    except CalledProcessError:
        return False
    else:
        return True
        
def get_installed_webdrivers():
    """Returns the installed webdrivers on the machine"""
    
    webbrowsers = ["Firefox", "Chrome"]
    webdrivers = ["geckodriver", "chromedriver"]
    
    for webdriver in webdrivers:
        if not is_webdriver_installed(webdriver):
            del webbrowsers[webdrivers.index(webdriver)]

    return webbrowsers
        
def read_textfile(filepath):
    """Reads an entire textfile, with 'latin-1' support"""
    
    try:
        f = io.open(filepath, 'rt', encoding = 'latin-1')
        text = f.read()
        f.close()
    except:
        return ""
    else:
        return text
   
def replace_keyword(text, keyword, replacement):
    """Replace the keyword given, with replacement, in text."""

    # When no replacement is given, simply replace it with ""
    if (replacement or replacement != "None"):
        return text.replace(keyword, replacement)
    else:
        return text.replace(keyword, "")
        
def get_subject(subject):
    """Erases the tags used for the subject"""
    
    subject = subject.replace("[Asunto]", "")
    subject = subject.replace("[/Asunto]", "")

    return subject

def get_content(content):
    """Makes sure the content is well formated"""

    # Delete trailing newline.
    return content.replace("\n", "", 1)

def create_failed_file(folder):
    """Create a textfile or open it in overwrite mode"""
    
    try:
        f = io.open(folder + os.sep + 'fallidos.txt', "w+",
                    encoding = 'latin-1')
        f.write(u"")
        f.close()
    except IOError:
        None
        
def dump_failed_email(failed_email, folder):
    """Function that puts in textfile the HT-Mails that couldn't be sent"""

    try:
        f = io.open(folder + os.sep + 'fallidos.txt', 'a',
                    encoding = 'latin-1')
        f.write(failed_email[0] + '\n')
        f.close()
    except IOError:
        None

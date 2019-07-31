# automation.py: Handles automation of HT web page
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


# Selenium imports.
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

# To know address of src files.
import HTMailsGUI

# Workaround problems with httplib.
from httplib import BadStatusLine

# System related imports.
import os

import json

# TODO: Save the value of time to wait for Explicit Waits,
# so it is easier to adapt.
            
class ht_driver ():
    """Class that performs automation of HT web page."""
    
    def __init__ (self, driver):
        
        # TODO: Don't load profiles if we don't need them.
        # We'll need them if using the extension

        if driver == "Firefox":

            # Comment it for now, to use when using web extension.
            # try:
            #     f = open(HTMailsGUI.get_thisfile_directory() + os.pardir + \
                #              os.sep + "data" + os.sep + "pathToProfile.txt", "r")
            #     profile_path = f.read()
            #     f.close()
            # except:
            #     print "No pudo encontrarse el perfil necesario de Firefox"
            #     print "Por favor, corra de nuevo el archivo create_firefox_profile.py"
            #     sys.exit()
            
            # # Create Firefox Profile
            # fp = webdriver.FirefoxProfile(profile_path)
        
            options = Options ()            

            # Initialize webdriver
            # self.driver = webdriver.Firefox(firefox_profile = fp,
            #                                 firefox_options = options)

            self.driver = webdriver.Firefox (firefox_options = options)

        # FIXME: Maybe more webdrivers will come.
        else:
            self.driver = webdriver.Chrome ()
            
        # Mainpage.
        self.mainpage = "https://hattrick.org/"
        self.server = ""
        self.youthplayer_url = "https://www{0}.hattrick.org/Club/Players/YouthPlayer.aspx?YouthPlayerID={1}"
        self.htmail_url = "https://www{0}.hattrick.org/MyHattrick/Inbox/?actionType=newMail&userId={1}"
        
    def visit_mainpage (self):
        """Get mainpage."""
        
        self.visit_url (self.mainpage, None)

    def visit_url (self, url, replacement):
        """Get URL asked, replacing keywords with the elements in the
        replacement list."""

        if replacement:
            for i in range (len (replacement)):
                url = url.replace ("{" + str(i) + "}", replacement[i])

        # Workaround, to be able to use time.sleep().
        try:    
            self.driver.get (url)
        except BadStatusLine:
            self.driver.get (url)

    def login (self, values):
        """Login user."""

        # TODO: Save in variables the ids, class names, etc,
        # to fix them easily if HT changes them.

        # If no_login_info is used, increase it, so the user has time to type
        # his information on the web page.
        wait_time = 10
        if values:
            # Fill User input.
            elem_user = self.driver.find_element_by_id ("ctl00_CPContent_ucLogin_txtUserName")
            elem_user.send_keys (values[0])
            
            # Fill Password input.
            elem_password = self.driver.find_element_by_id ("ctl00_CPContent_ucLogin_txtPassword")
            elem_password.send_keys (values[1])

            # Click button Login.
            self.driver.find_element_by_id ("ctl00_CPContent_ucLogin_butLogin").click()
        else:
            # 25 seconds should be enough time.
            wait_time = 25
            
        # Check if login was succesful.
        # Check for button Logout, that should be enough.
        try:
            wait = WebDriverWait (self.driver, wait_time)
            elmt = wait.until (EC.presence_of_element_located ((By.ID,
                                                               "ctl00_ctl00_CPHeader_ucMenu_hypLogout")))
        except NoSuchElementException:
            return None
        except TimeoutException:
            return None
        else:
            self.server = self.get_server (self.driver.current_url)
            return True    

    def sendHTMail (self, subject, content, data, where_to_look, blacklist,
                    direct_access):
        """Send HTMails to users, depending on content of spreadsheet file.
        Give the index WHERE_TO_LOOK, to know where to look for an ID in DATA."""

        # TODO: Go right to mail page if direct_access = true, and ID Owner
        # is present.
        # TODO: Add code to handle the web extension.
        if direct_access:
            # HACK ALERT: Make it work now!
            self.visit_url (self.htmail_url,
                            [self.server,
                             self.extract_player_id (data[where_to_look])])
            try:
                wait = WebDriverWait (self.driver, 10)
                elmt = \
                    wait.until (EC.presence_of_element_located ((By.ID,
                                                                "ctl00_ctl00_CPContent_CPMain_tbSubject")))
            except TimeoutException:
                return False
            else:
                elmt.send_keys (subject)
                self.driver.find_element_by_id ("ctl00_ctl00_CPContent_CPMain_ucEditorMain_txtBody").send_keys (content)
                self.driver.find_element_by_id ("ctl00_ctl00_CPContent_CPMain_btnSendNew").click ()
                try:
                    elmt = \
                        wait.until (EC.presence_of_element_located ((By.ID,
                                                                     "ctl00_ctl00_CPContent_ucNotifications_ok_0")))
                    # If that elmt did not appear, then the mail was not sent.
                except TimeoutException:
                    return False
                else:
                    return True
                
        else:
            self.visit_url (self.youthplayer_url,
                            [self.server,
                             self.extract_player_id (data[where_to_look])])
            
            if self.goto_mail_page (blacklist):
                try:
                    wait = WebDriverWait (self.driver, 10)
                    elmt = \
                        wait.until (EC.presence_of_element_located ((By.ID,
                                                                     "ctl00_ctl00_CPContent_CPMain_tbSubject")))
                except TimeoutException:
                    return False
                else:
                    elmt.send_keys (subject)
                    self.driver.find_element_by_id ("ctl00_ctl00_CPContent_CPMain_ucEditorMain_txtBody").send_keys (content)

                    self.driver.find_element_by_id ("ctl00_ctl00_CPContent_CPMain_btnSendNew").click ()

                    try:
                        elmt = \
                            wait.until (EC.presence_of_element_located ((By.ID,
                                                                         "ctl00_ctl00_CPContent_ucNotifications_ok_0")))
                    # If that elmt did not appear, then the mail was not sent.
                    except TimeoutException:
                        return False
                    else:
                        return True
            else:
                return False

    def goto_mail_page (self, blacklist):
        """Attemp to reach the HT-Mail url.  If the manager is in the
        BLACKLIST, then return abort the attempt, returning False."""

        # TODO: There's an easier way if Manager ID is provided,
        # or with the web extension.
        
        # Check if the team is not in the blacklist.
        try:
            wait = WebDriverWait (self.driver, 10)
            elmt_subMenu = \
                wait.until (EC.presence_of_element_located ((By.ID,
                                                             "content")))
            elmt_subMenu.find_element_by_class_name ("subMenu")
            team_id = elmt_subMenu.find_element_by_tag_name ("a").get_attribute ("href")
            team_id = "[teamid=" + team_id[team_id.find("=") + 1:] + "]"

            if team_id in blacklist:
                return False
        
        except TimeoutException:
            return False
        else:
            # Go to manager page.
            elmt_subMenu = self.driver.find_element_by_id ("content")
            elmt_subMenu = elmt_subMenu.find_element_by_class_name ("subMenu")
            elmt_subMenu.find_elements_by_tag_name ("a")[1].click ()

            # And now to the mail page.
            try:
                elmt_mail_img = \
                    wait.until (EC.presence_of_element_located ((By.ID, "ctl00_ctl00_CPContent_CPSidebar_ucVisitorActions_lnkMail")))
                elmt_mail_img.find_element_by_tag_name ("img").click ()
            except TimeoutException:
                return False
            except NoSuchElementException:
                return False
            else:
                return True

    def get_server (self, url):
        """Extract the server of a url, present as: 
        'https://wwwSERVER.RESTOFURL'"""
        
        server_pos = url.find ("www") + 3
        return url[server_pos:url.find (".")]

    def extract_player_id (self, tag):
        """Extracs an id from the tag: [YOUTH?playerid=ID]."""
        pos_equalsign = tag.find ("=")
        return tag[pos_equalsign + 1:-1]
        
    def destroy (self):
        """Logout and destroy driver."""
        
        try:
            self.driver.find_element_by_id ("ctl00_ctl00_CPHeader_ucMenu_hypLogout").click ()
        except BadStatusLine:
            self.driver.find_element_by_id ("ctl00_ctl00_CPHeader_ucMenu_hypLogout").click ()
            
        self.driver.close ()

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 14:04:12 2022

@author: madha
"""

import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class UnexpectedFormatException(Exception):
    pass

def getRecentUsername(username, driver):
    
    def queryRecentUsername(username, driver):
    
        def strip_and_upper(s):
            s = s.strip()
            s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()
            return s

        driver.get("https://en.wikipedia.org/wiki/User:" + username)
        usernameMatch = re.search('User:(.*) - Wikipedia', driver.title)
        if not usernameMatch:
            # look for redirect to talk-page
            usernameMatch = re.search('User talk:(.*) - Wikipedia', driver.title)
            if not usernameMatch:
                return None
            else:
                return strip_and_upper(usernameMatch.group(1))
        elif usernameMatch.group(1) != username:
            # redirected to different user page
            return strip_and_upper(usernameMatch.group(1))
        else:
            try:
                userdoesnotexist_line = driver.find_element(By.CLASS_NAME, "mw-userpage-userdoesnotexist")
            except NoSuchElementException:
                userdoesnotexist_line = None
            try:
                move_line = driver.find_element(By.CLASS_NAME, "mw-logline-move")
            except NoSuchElementException:
                move_line = None
            try:
                rename_line = driver.find_element(By.CLASS_NAME, "mw-logline-renameuser")
            except NoSuchElementException:
                rename_line = None
            if not userdoesnotexist_line and not move_line and not rename_line:
                # should be a valid userpage
                return username
            elif rename_line:
                username_list = rename_line.find_elements(By.TAG_NAME, "a")
                if len(username_list) >= 6:
                    return username_list[5].text
                else:
                    raise UnexpectedFormatException("Unexpected format: rename line")
            elif move_line:
                username_list = move_line.find_elements(By.TAG_NAME, "a")
                if len(username_list) >= 6:
                    new_userpage_title = username_list[5].text
                    if new_userpage_title.startswith("User:"):
                        return new_userpage_title[5:]
                    else:
                        raise UnexpectedFormatException("Unexpected format: move line: new userpage title")
                else:
                    raise UnexpectedFormatException("Unexpected format: move line")
            else:
                return None
            
    recentUsername = queryRecentUsername(username, driver)
    oldUsername = username
    allNames = []
    while recentUsername != None and recentUsername != oldUsername:
        allNames.append(oldUsername)
        oldUsername = recentUsername
        recentUsername = queryRecentUsername(recentUsername, driver)
        if recentUsername in allNames:
            #infinite loop
            break
    return recentUsername
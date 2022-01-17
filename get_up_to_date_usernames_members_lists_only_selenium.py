# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 11:48:19 2022

@author: madha
"""

import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
from collections import OrderedDict
import os
import csv
import sys
import traceback

class UnexpectedFormatException(Exception):
    pass

def getRecentUsername(username, driver):
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

#setup selenium webdriver
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chromeDriverPath = "/home/madhavso/chromedriver"
driver = webdriver.Chrome(executable_path = chromeDriverPath, options = chrome_options)

membersListPath = "/home/madhavso/wikipedia_data/user_lists/complete_user_list.csv"
usernamesMapCsvPath = "/home/madhavso/wikipedia_data/user_lists/usernamesMap.csv"
usernamesInvalidPath = "/home/madhavso/wikipedia_data/user_lists/usernamesInvalid.csv"
failedQueriesPath = "/home/madhavso/wikipedia_data/user_lists/failedQueries.txt"

membersListDf = pd.read_csv(membersListPath, encoding = "utf-8")
usernamesMapPathExists = os.path.exists(usernamesMapCsvPath)
usernamesInvalidPathExists = os.path.exists(usernamesInvalidPath)

#login to Wikipedia
driver.get("https://en.wikipedia.org/w/index.php?title=Special:UserLogin")
usernameBox = driver.find_element(By.NAME, "wpName")
usernameBox.send_keys("Msomanat")
passwordBox = driver.find_element(By.NAME, "wpPassword")
passwordBox.send_keys("p1tm0qpgu" + Keys.ENTER)

usernameToMostRecentUsername = OrderedDict()
usernamesInvalid = OrderedDict()

with open(usernamesMapCsvPath, "a", newline = "", encoding = "utf-8") as usernamesMapCsv:
    writerUsernamesMap = csv.writer(usernamesMapCsv, quoting = csv.QUOTE_MINIMAL)
    if usernamesMapPathExists:
        #read in stored username mappings
        usernamesMapDf = pd.read_csv(usernamesMapCsvPath, encoding = "utf-8")
        for i in usernamesMapDf.index:
            usernameToMostRecentUsername[usernamesMapDf["username"][i]] = usernamesMapDf["mostRecentUsername"][i]
    else:
        #insert header
        writerUsernamesMap.writerow(["username", "mostRecentUsername"])
    
    with open(usernamesInvalidPath, "a", newline = "", encoding = "utf-8") as usernamesInvalidCsv:
        writerUsernamesInvalid = csv.writer(usernamesInvalidCsv, quoting = csv.QUOTE_MINIMAL)
        if usernamesInvalidPathExists:
            #read in stored invalid usernames
            usernamesInvalidDf = pd.read_csv(usernamesInvalidPath, encoding = "utf-8")
            for name in usernamesInvalidDf["username"]:
                usernamesInvalid[name] = None
        else:
            #insert header
            writerUsernamesInvalid.writerow(["username"])
        
        with open(failedQueriesPath, "w", newline = "", encoding = "utf-8") as failedQueriesLog:
            
            #for each member get up-to-date username
            for i in membersListDf.index:
                member = membersListDf["member"][i]
                if pd.isna(member):
                    continue
                if member not in usernameToMostRecentUsername.keys() and member not in usernamesInvalid.keys():
                    try:
                        recentUsername = getRecentUsername(member, driver)
                    except KeyboardInterrupt:
                        print("Stopped execution on user:", member)
                        raise
                    except:
                        failedQueriesLog.write(str(i) + "\n")
                        failedQueriesLog.write(member + "\n")
                        traceback.print_tb(sys.exc_info()[2], file = failedQueriesLog)
                        continue
                    if recentUsername == None:
                        usernamesInvalid[member] = None
                        writerUsernamesInvalid.writerow([member])
                    else:
                        usernameToMostRecentUsername[member] = recentUsername
                        writerUsernamesMap.writerow([member, recentUsername])
                    print(i, member, ":", recentUsername)
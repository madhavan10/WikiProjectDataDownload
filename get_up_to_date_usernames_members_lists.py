# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 17:02:14 2021

@author: madha
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from collections import OrderedDict
import requests
import re
import os
import csv


def userHasContribs(username):
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
            "action": "query",
            "list": "usercontribs",
            "ucuser": username,
            "ucprop": "title|timestamp",
            "uclimit": "1",
            "format": "json"
        }
    R = S.get(url = URL, params = PARAMS)
    if R.json():
        json = R.json()
        if "query" in json.keys() and "usercontribs" in json["query"].keys() and len(json["query"]["usercontribs"]) != 0:
            return True
        else:
            return False
    else:
        raise Exception("Couldn't get json")

def getRecentUsername(username, driver):
    driver.get("https://en.wikipedia.org/wiki/User:" + username)
    usernameMatch = re.search('User:(.*) - Wikipedia', driver.title)
    if not usernameMatch or usernameMatch.group(1) == username:
        usernameMatch = re.search('User talk:(.*) - Wikipedia', driver.title)
        if not usernameMatch:
            rename_line = driver.find_element(By.CLASS_NAME, "mw-logline-renameuser")
            username_list = rename_line.find_elements(By.TAG_NAME, "a")
            if len(username_list) >= 6:
                changedName = username_list[5].text
                return changedName
        else:
            return usernameMatch.group(1)
    else:
        return usernameMatch.group(1)
    
driver = webdriver.Chrome(executable_path = r"C:\Users\madha\chromedriver.exe")
usernamesMapCsvPath = r"C:\users\madha\documents\wikiproject\user_lists\usernamesMap.csv"
membersListPath = r"C:\users\madha\documents\wikiproject\user_lists\complete_user_list.csv"

membersDf = pd.read_csv(membersListPath, encoding = "utf-8")
usernameToMostRecentUsername = OrderedDict()

if os.path.exists(usernamesMapCsvPath):
    usernamesMapCsvExists = True
    usernameToMostRecentUsernameDf = pd.read_csv(usernamesMapCsvPath, encoding = "utf-8")
    for i in usernameToMostRecentUsernameDf.index:
        mrUsername = usernameToMostRecentUsernameDf["mostRecentUsername"][i]
        usernameToMostRecentUsername[usernameToMostRecentUsernameDf["username"][i]]\
            = mrUsername if pd.notna(mrUsername) else None
else:
    usernamesMapCsvExists = False

try:
    usernamesMapCsv = open(usernamesMapCsvPath, "a", newline = "", encoding = "utf-8")
    writerUsernames = csv.writer(usernamesMapCsv, quoting = csv.QUOTE_MINIMAL)
    if not usernamesMapCsvExists:
        #insert header
        writerUsernames.writerow(["username", "mostRecentUsername"])
    
    usernameToProjectMembership = OrderedDict()
    for i in membersDf.index:
        member = membersDf["member"][i]
        print(i, member)
        projectName = membersDf["project"][i]
        if member not in usernameToMostRecentUsername.keys():
            if not userHasContribs(member):
                recentUsername = getRecentUsername(member, driver)
                usernameToMostRecentUsername[member] = recentUsername
            else:
                usernameToMostRecentUsername[member] = member
            writerUsernames.writerow([member, usernameToMostRecentUsername[member]])
        correctUsername = usernameToMostRecentUsername[member]
        if correctUsername != None:
            if correctUsername in usernameToProjectMembership.keys():
                usernameToProjectMembership[correctUsername].append(projectName)
            else:
                usernameToProjectMembership[correctUsername] = [projectName]
                
    dfProjectMembership = pd.DataFrame(columns = ["username", "project"])
    
    i = 0
    for name, projects in usernameToProjectMembership.items():
        for project in projects:
            dfProjectMembership.loc[i] = (name, project)
            i += 1
    
    dfProjectMembership.to_csv(r"C:\users\madha\documents\wikiproject\user_lists\projectMembership.csv", index = False, encoding = "utf-8")

except:    
    usernamesMapCsv.close()
    raise
usernamesMapCsv.close()
# Check if username already seen
# If already seen, get most recent username, and add entry for project
# Else try to get user contribs
# If successful, add to usernames seen, and add entry for project
# Else use selenium to get up-to-date username
# If successful, add to usernames, seen and add entry for project
# Else add to usernames
            

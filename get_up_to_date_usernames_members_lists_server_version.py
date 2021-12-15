# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 17:02:14 2021

@author: madha
"""

import pandas as pd
from collections import OrderedDict
import requests
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
    
usernamesMapCsvPath = "/home/madhavso/wikipedia_data/user_lists/usernamesMap.csv"
changedUsernamesPath = "/home/madhavso/wikipedia_data/user_lists/changedUsernames.csv"
membersListPath = "/home/madhavso/wikipedia_data/user_lists/complete_user_list.csv"

membersDf = pd.read_csv(membersListPath, encoding = "utf-8")
usernameToMostRecentUsername = OrderedDict()
changedUsernames = OrderedDict()

if os.path.exists(usernamesMapCsvPath):
    usernamesMapCsvExists = True
    usernameToMostRecentUsernameDf = pd.read_csv(usernamesMapCsvPath, encoding = "utf-8")
    for i in usernameToMostRecentUsernameDf.index:
        mrUsername = usernameToMostRecentUsernameDf["mostRecentUsername"][i]
        usernameToMostRecentUsername[usernameToMostRecentUsernameDf["username"][i]]\
            = mrUsername if pd.notna(mrUsername) else None
else:
    usernamesMapCsvExists = False

if os.path.exists(changedUsernamesPath):
    changedUsernamesDf = pd.read_csv(changedUsernamesPath, encoding = "utf-8")
    for username in changedUsernamesDf["username"]:
        changedUsernames[username] = None

try:
    usernamesMapCsv = open(usernamesMapCsvPath, "a", newline = "", encoding = "utf-8")
    writerUsernames = csv.writer(usernamesMapCsv, quoting = csv.QUOTE_MINIMAL)
    if not usernamesMapCsvExists:
        #insert header
        writerUsernames.writerow(["username", "mostRecentUsername"])
    
    for i in membersDf.index:
        member = membersDf["member"][i]
        print(i, member)
        if member not in usernameToMostRecentUsername.keys() and member not in changedUsernames.keys():
            if not userHasContribs(member):
                changedUsernames[member] = None
            else:
                usernameToMostRecentUsername[member] = member
                writerUsernames.writerow([member, usernameToMostRecentUsername[member]])

except:    
    usernamesMapCsv.close()
    changedUsernamesDf = pd.DataFrame({"username": changedUsernames.keys()})
    changedUsernamesDf.to_csv(changedUsernamesPath, index = False, encoding = "utf-8")
    raise
usernamesMapCsv.close()
changedUsernamesDf = pd.DataFrame({"username": changedUsernames.keys()})
changedUsernamesDf.to_csv(changedUsernamesPath, index = False, encoding = "utf-8")
            

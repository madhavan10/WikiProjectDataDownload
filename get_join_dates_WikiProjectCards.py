# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 09:36:20 2022

@author: madha
"""

import pandas as pd
import os
import requests
from collections import OrderedDict

def get_members(fname):
    df = pd.read_csv(fname, encoding = "utf-8")
    d = OrderedDict()
    for member in df["member"]:
        d[member] = None
    return d

def get_timestamp(session, pagename):
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
            "action": "query",
            "prop": "revisions",
            "titles": pagename,
            "rvprop": "timestamp",
            "rvslots": "main",
            "rvdir": "newer",
            "rvlimit": "1",
            "format": "json",
            "formatversion": 2
        }
    R = session.get(url = URL, params = PARAMS)
    json = R.json()
    timestamp = json["query"]["pages"][0]["revisions"][0]["timestamp"] if "revisions" in json["query"]["pages"][0].keys() else None
    return timestamp
    
membersListsInputsDf = pd.read_excel("C:/users/madha/dropbox/wikiproject_data_download/retrieve_members_input_vars.xlsx")
projectIdLookupDf = pd.read_csv(r"C:\Users\madha\Documents\WikiProject\projectIdLookup.csv", encoding = "utf-8")
WPCLookupDf = pd.read_csv(r"C:\Users\madha\Documents\WikiProject\WikiProjectCardsLookup.csv", encoding = "utf-8")
statsPath = "C:/users/madha/documents/wikiproject/user_lists/statsWPCards.csv"
listsDir = "C:/users/madha/documents/wikiproject/user_lists/new_way"
os.chdir(listsDir)

lookup = {}
for i in projectIdLookupDf.index:
    lookup[projectIdLookupDf["projectName"][i]] = projectIdLookupDf["projectId"][i]


projectTypeLookup = OrderedDict()
for i in membersListsInputsDf.index:
    projectType = membersListsInputsDf["type"][i]
    projectTypeLookup[membersListsInputsDf["wikiproject"][i]] = projectType if pd.notna(projectType) else "sr"

S = requests.Session()
userList = []
projects = []
timestamps = []
types = []
for projectName in WPCLookupDf["project"]:
    filename = str(lookup[projectName]) + ".csv"
    users = get_members(filename)
    for user in users.keys():
        page = "User:" + user + "/WikiProjectCards/" + projectName
        print(projectName, ":", user)
        timestamp = get_timestamp(S, page)
        userList.append(user)
        projects.append(projectName)
        timestamps.append(timestamp)
        types.append(projectTypeLookup[projectName])
outDf = pd.DataFrame({"member": userList, "project": projects, "joinDate": timestamps, "type": types})
outDf.to_csv(r"C:\users\madha\documents\wikiproject\user_lists\wikiProjectCardsJoinDates.csv", index = False, encoding = "utf-8")
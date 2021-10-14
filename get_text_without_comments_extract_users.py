# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 18:36:56 2021

@author: madha
"""

import requests
import re
import pandas as pd
import os
import sys

def get_properties_from_file(filename):
    properties = dict()
    with open(filename) as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
    return properties

try:
    properties = get_properties_from_file(sys.argv[1])
except IndexError:
    raise Exception("Specify a properties file as an argument to this script.")

inputsPath = os.path.abspath(properties["retrieveMembersInputsPath"])
projectName = properties["projectName"]

inputsDf = pd.read_excel(inputsPath)
inputsDf = inputsDf[inputsDf["wikiproject"] == projectName].reset_index(drop = True)

membersListOutputPath = inputsDf["outputPath"][0]

S = requests.Session()

#outputPath = r"C:\users\madha\documents\wikiproject\user_lists\military_history_members_inactive.txt"

URL = "https://en.wikipedia.org/w/api.php"

#page = "Wikipedia:WikiProject Mathematics/Participants"

users = []
sourcePage = []

for i in inputsDf.index:

    page = inputsDf["page"][i]
    userRegex = inputsDf["regex"][i]
    
    PARAMS = {
            "action": "query",
            "prop": "revisions",
            "titles": page,
            "rvprop": "timestamp|content",
            "rvslots": "main",
            "rvlimit": "1",
            #"rvdir": "newer",
            #"rvend": rvend,
            "format": "xml"        
        }
    
    R = S.get(url = URL, params = PARAMS)
    htmlCommentsRegex = '&lt;!--([^-]|-[^-]|--[^&\s]|--\s*&[^g]|--\s*&g[^t]|--\s*gt[^;])*--\s*&gt;'
    text = re.sub(htmlCommentsRegex, "", R.text)
    foundUsers = re.findall(userRegex, text, flags = re.IGNORECASE)
    for user in foundUsers:
        users.append(user)
        sourcePage.append(page)
        
outputsDf = pd.DataFrame({"member": users, "source": sourcePage})
outputsDf.to_csv(membersListOutputPath, index = False, encoding = "utf-8")
    
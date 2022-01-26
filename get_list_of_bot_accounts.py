# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 11:29:24 2022

@author: madha
"""

import requests
import pandas as pd
import os
import re

outPath = "/home/madhavso/wikipedia_data/user_lists/union_minus_10000_whether_bot.csv"
lookupPath = "/home/madhavso/wikipedia_data/user_lists/1-10000_union_lookup_updated.csv"
lookupDf = pd.read_csv(lookupPath, encoding = "utf-8")
usernameLookup = {}
for i in lookupDf.index:
    usernameLookup[lookupDf["userNumber"][i]] = lookupDf["user"][i]

filenames = []
usernames = []
botTags = []
botTagFound = []
os.chdir("/home/madhavso/wikipedia_data/top_editors/contributions/rest")
for file in os.listdir():
    split = file.rsplit(".", maxsplit = 1)
    if split[-1] != "csv":
        continue
    print(file)
    username = usernameLookup[int(split[0])]
        
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    page = "User:" + username
    PARAMS = {
                "action": "query",
                "prop": "revisions",
                "titles": page,
                "rvprop": "timestamp|content",
                "rvslots": "main",
                "rvlimit": "1",
                "format": "xml"        
            }
    R = S.get(url = URL, params = PARAMS)
    botRegex = "\{\{bot[^\}]*\}\}"
    botMatch = re.search(botRegex, R.text, flags = re.IGNORECASE)
    if botMatch:
        botTags.append(botMatch.group(0))
        botTagFound.append("yes")
    else:
        botTags.append("")
        redirectString = "#REDIRECT"
        if redirectString in R.text:
            botTagFound.append("redirect")
        else:
            botTagFound.append("no")
    filenames.append(file)
    usernames.append(username)
    
df = pd.DataFrame({"filename": filenames, "username": usernames, "botTagFound": botTagFound, "botTagText": botTags})
df.to_csv(outPath, index = False, encoding = "utf-8")
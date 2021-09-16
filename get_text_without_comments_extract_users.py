# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 18:36:56 2021

@author: madha
"""

import requests
import re


S = requests.Session()

outputPath = r"C:\users\madha\documents\wikiproject\user_lists\military_history_members_inactive.txt"

URL = "https://en.wikipedia.org/w/api.php"

#page = "Wikipedia:WikiProject Mathematics/Participants"
page = "Wikipedia:WikiProject Military history/Members/Inactive"

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

users = []

# Mathematics
# userRegex = '\[\[User: *([^\]\|]+)'

# Military history
userRegex = '\{\{#target:User talk: *([^\}\|]+)'
users += re.findall(userRegex, text)
with open(outputPath, "w", newline = "", encoding = "utf-8") as ofile:
    for user in users:
        ofile.write(user)
        ofile.write("\n")
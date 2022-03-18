# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 16:39:34 2021

@author: madha
"""

import requests
import re
import xml.etree.ElementTree as ET

def extract_users_from_str(s):
    lineByLine = s.split("\n")
    if len(lineByLine) != 5009:
        return None
    users = []
    i = 0
    j = 1
    start = False
    for line in lineByLine:
        i += 1
        if i == 9:
            start = True
        if start:
            if line.startswith("|}"):
                break
            if j % 5 == 0:
                j += 1
                continue
            lineStripped = line[2:].rstrip("\n")
            if j % 5 == 2:
                if lineStripped != "[Placeholder]":
                    match = re.match("\[\[User:([^\|\]]+)", lineStripped, flags = re.IGNORECASE)
                    if match:
                        users.append(match.group(1))
                    else:
                        users.append(lineStripped)
            j += 1
    return users

allUsers = set()
ofilename = r"C:\users\madha\documents\wikiproject\top_editors\1-1000_union.txt"

S = requests.Session()
URL = "https://en.wikipedia.org/w/api.php" 
PARAMS = {
            "action": "query",
            "prop": "revisions",
            "titles": "Wikipedia:List of Wikipedians by number of edits/9001–10000",
            "rvprop": "timestamp|user|userid|comment|content",
            "rvslots": "main",
            "rvlimit": "max",
            #"rvend": "2019-06-24T00:00:00Z",
            "rvuser": "BernsteinBot",
            "rvdir": "newer",
            "format": "xml"        
        }
while True: 
    R = S.get(URL, params = PARAMS)
    root = ET.fromstring(R.text)
    for slot in root.iter("slot"):
        users = extract_users_from_str(slot.text)
        if users:
            for user in users:
                allUsers.add(user)
    
    cont = re.search('<continue rvcontinue="([^"]+)"', R.text)
    if not cont:
        break
    PARAMS["rvcontinue"] = cont.group(1)
    print(cont.group(1))
    
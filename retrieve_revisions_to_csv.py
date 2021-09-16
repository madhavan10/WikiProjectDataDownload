# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 11:19:06 2021

@author: madha
"""

import requests
import re
from collections import OrderedDict
import pandas as pd

S = requests.Session()
URL = "https://en.wikipedia.org/w/api.php"

#collect revisions upto
#rvend = "2007-12-01T23:38:59Z"

rvend = ""

page = "Wikipedia:WikiProject Military history/Members/Active"

csvOutputPath = r"C:\users\madha\documents\wikiproject\project_join\military_history_members_active.csv"
revisionsOutputPath = r"C:\users\madha\documents\wikiproject\revisions\military_history_members_active.txt"

PARAMS = {
        "action": "query",
        "prop": "revisions",
        "titles": page,
        "rvprop": "timestamp|user|userid|comment",
        "rvslots": "main",
        "rvlimit": "500",
        "rvdir": "newer",
        "rvend": rvend,
        "format": "xml"        
    }

revisions = []

while True:
    R = S.get(url = URL, params = PARAMS)
    revisions += re.findall('<rev [^>]*>', R.text)
    cont = re.search('<continue rvcontinue="([^"]+)"', R.text)
    if not cont:
        break
    next = cont.group(1)
    PARAMS["rvcontinue"] = next
    print(next)
    
usernamesById = OrderedDict()
joindateByUserId = OrderedDict()
for elt in revisions:
    match = re.search('user="([^"]*)" userid="([^"]*)" timestamp="([^"]*)" [^>]*>', elt)
    if match:
        if re.search('[bB][oO][tT]$', match.group(1)):
            continue
        if match.group(2) not in usernamesById:
            usernamesById[match.group(2)] = match.group(1)
        if match.group(2) not in joindateByUserId:
            joindateByUserId[match.group(2)] = match.group(3)
        
df = pd.DataFrame({"userid": list(usernamesById.keys()), "user": list(usernamesById.values()), "joindate": list(joindateByUserId.values())})
df.to_csv(csvOutputPath, index = False, encoding = "utf-8")
  
with open(revisionsOutputPath, "w", newline="", encoding = "utf-8") as ofile:
    for elt in revisions:
        ofile.write(elt)
        ofile.write("\n")

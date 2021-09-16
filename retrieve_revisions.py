# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
import re

S = requests.Session()
URL = "https://en.wikipedia.org/w/api.php"

PARAMS = {
        "action": "query",
        "prop": "revisions",
        "titles": "Wikipedia:WikiProject Military history/Members",
        "rvprop": "timestamp|user|userid|comment",
        "rvslots": "main",
        "rvlimit": "500",
        "rvdir": "newer",
        "format": "xml"        
    }

revisions = []

i = 1
while True:

    R = S.get(url = URL, params = PARAMS)
    revisions += re.findall('<rev [^>]*>', R.text)
    cont = re.search('<continue rvcontinue="([^"]+)"', R.text)
    if not cont:
        break
    next = cont.group(1)
    PARAMS["rvcontinue"] = next
    print(next)
    i += 1
with open(r"C:\users\madha\documents\wikiproject\test.txt", "w", newline="", encoding = "utf-8") as ofile:
    for elt in revisions:
        ofile.write(elt)
        ofile.write("\n")
print(i)

            


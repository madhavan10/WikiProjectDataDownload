# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 21:45:49 2021

@author: madha
"""

import requests
import csv
import pandas as pd
import os

userNumberLookupDf = pd.read_csv("/home/madhavso/wikipedia_data/user_lists/1-10000_lookup.csv", encoding = "utf-8")
userNumberLookup = {}
for i in userNumberLookupDf.index:
    userNumberLookup[userNumberLookupDf["user"][i]] = userNumberLookupDf["userNumber"][i]

for user in userNumberLookup:
    userCsv = "/home/madhavso/wikipedia_data/top_editors/contributions/" + str(userNumberLookup[user]) + ".csv"
    if os.path.exists(userCsv) and os.path.getsize(userCsv) != 0:
        print(userCsv, " already exists")
        continue
    print(user, userCsv.rsplit(os.sep, maxsplit = 1)[-1])
    with open(userCsv, "w", newline = "", encoding = "utf-8") as userCsvF:
        writer = csv.writer(userCsvF, quoting = csv.QUOTE_MINIMAL)
        writer.writerow(("user", "userid", "timestamp", "ns", "pageid", "title", "comment", "revid", "parentid", "size", "sizediff"))
    
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
            "action": "query",
            "list": "usercontribs",
            "ucuser": user,
            "ucprop": "ids|timestamp|title|comment|size|sizediff",
            "ucdir": "newer",
            "uclimit": "max",
            "format": "json"        
        }
    
    while True:
        contribs = []
        R = S.get(URL, params = PARAMS);
        json = R.json()
        if "query" in json.keys() and "usercontribs" in json["query"].keys():        
            for contrib in json["query"]["usercontribs"]:
                user = contrib["user"] if "user" in contrib.keys() else ""
                userid = contrib["userid"] if "user" in contrib.keys() else -1
                timestamp = contrib["timestamp"] if "timestamp" in contrib.keys() else ""
                ns = contrib["ns"] if "ns" in contrib.keys() else -1
                pageid = contrib["pageid"] if "pageid" in contrib.keys() else -1
                title = contrib["title"] if "title" in contrib.keys() else ""            
                comment = contrib["comment"] if "comment" in contrib.keys() else ""
                revid = contrib["revid"] if "revid" in contrib.keys() else -1
                parentid = contrib["parentid"] if "parentid" in contrib.keys() else -1
                size = contrib["size"] if "size" in contrib.keys() else -1
                sizediff = contrib["sizediff"] if "sizediff" in contrib.keys() else 0
                contribs.append((user, userid, timestamp, ns, pageid, title, comment, revid, parentid, size, sizediff))
            with open(userCsv, "a", newline = "", encoding = "utf-8") as userCsvF:
                writer = csv.writer(userCsvF, quoting = csv.QUOTE_MINIMAL)
                for contrib in contribs:
                    writer.writerow(contrib)
            if "continue" in json.keys() and "uccontinue" in json["continue"].keys():
                cont = json["continue"]["uccontinue"]
                PARAMS["uccontinue"] = cont
                print(cont)
            else:
                break

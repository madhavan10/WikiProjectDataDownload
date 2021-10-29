# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 21:45:49 2021

@author: madha
"""

import requests
import csv
import pandas as pd
import os

userNumberLookupDf = pd.read_csv(r"C:\users\madha\documents\wikiproject\top_editors\1-10000_union_lookup.csv", encoding = "utf-8")
userNumberLookup = {}
for i in userNumberLookupDf.index:
    userNumberLookup[userNumberLookupDf["user"][i]] = userNumberLookupDf["userNumber"][i]

for user in userNumberLookup:
    userCsv = "C:\\users\\madha\\documents\\wikiproject\\top_editors\\debug\\" + str(userNumberLookup[user]) + ".csv"
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
                user = contrib["user"]
                userid = contrib["userid"]
                timestamp = contrib["timestamp"]
                ns = contrib["ns"]
                pageid = contrib["pageid"]
                title = contrib["title"]            
                comment = contrib["comment"] if "comment" in contrib.keys() else ""
                revid = contrib["revid"]
                parentid = contrib["parentid"]
                size = contrib["size"]
                sizediff = contrib["sizediff"]
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
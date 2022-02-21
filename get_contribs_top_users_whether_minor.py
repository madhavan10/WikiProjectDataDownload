# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 22:57:05 2022

@author: madha
"""

import requests
import csv
import pandas as pd
import os

def getUserId(filename):
    contribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
    with open(os.path.join(contribsDir, filename), newline = "", encoding = "utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        row = next(reader)
        userid = row[1]
        return userid

userNumberLookupDf = pd.read_csv("/home/madhavso/wikipedia_data/user_lists/topEditorsLookup.csv", encoding = "utf-8")
userNumberLookup = {}
for i in userNumberLookupDf.index:
    userNumberLookup[userNumberLookupDf["user"][i]] = userNumberLookupDf["userNumber"][i]

contribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
writeDir = os.path.join(contribsDir, "minor")

os.chdir(contribsDir)
for filename in os.listdir():
    split = filename.rsplit(".", maxsplit = 1)
    if split[-1] != ".csv" or filename.startswith("m"):
        continue
    outCsvPath = os.path.join(writeDir, filename)
    if os.path.exists(outCsvPath) and os.path.getsize(outCsvPath) != 0:
        print(outCsvPath,"already exists")
        continue
    userId = getUserId(filename)
    try:
        with open(outCsvPath, "w", newline = "", encoding = "utf-8") as outCsv:
            writer = csv.writer(outCsv, quoting = csv.QUOTE_MINIMAL)
            writer.writerow(("userid", "revid", "minor"))
            
            S = requests.Session()
            URL = "https://en.wikipedia.org/w/api.php"
            PARAMS = {
                "action": "query",
                "list": "usercontribs",
                "ucuserids": userId,
                "ucprop": "ids|flags",
                "ucdir": "newer",
                "uclimit": "max",
                "ucend": "2021-11-11T00:01:00Z",
                "format": "json"        
            }
        
            while True:
                contribs = []
                R = S.get(URL, params = PARAMS);
                json = R.json()
                if "query" in json.keys() and "usercontribs" in json["query"].keys():        
                    for contrib in json["query"]["usercontribs"]:
                        userid = contrib["userid"] if "userid" in contrib.keys() else -1
                        revid = contrib["revid"] if "revid" in contrib.keys() else -1
                        minor = 1 if "minor" in contrib.keys() else 0
                        contribs.append((userid, revid, minor))
                    for contrib in contribs:
                        writer.writerow(contrib)
                    if "continue" in json.keys() and "uccontinue" in json["continue"].keys():
                        cont = json["continue"]["uccontinue"]
                        PARAMS["uccontinue"] = cont
                        print(cont)
                    else:
                        break
    except:
        print("Stopped execution on", filename)
        raise
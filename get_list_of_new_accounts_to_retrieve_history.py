# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 11:41:43 2022

@author: madha
"""
import pandas as pd
import requests
import csv
import os

lookupPath = "/home/madhavso/wikipedia_data/user_lists/1-10000_union_lookup_updated.csv"
lookupDf = pd.read_csv(lookupPath, encoding = "utf-8")
lookup = {}
for i in lookupDf.index:
    lookup[lookupDf["user"][i]] = lookupDf["userNumber"][i]

usersPath = "/home/madhavso/wikipedia_data/user_lists/unfilteredUsersToRetrieve.csv"
usersDf = pd.read_csv(usersPath, encoding = "utf-8")

usersToRetrieve = []
usersNotToRetrieve = []
contribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"

S = requests.Session()
URL = "https://en.wikipedia.org/w/api.php"

for i in usersDf.index:
    oldUsername = usersDf["oldUsername"][i]
    newUsername = usersDf["mostRecentUsername"][i]
    filename = os.path.join(contribsDir, str(lookup[oldUsername]) + ".csv")
    with open(filename, newline = "", encoding = "utf-8") as f:
        reader = csv.reader(f)
        #skip header
        next(reader)
        oldUserId = next(reader)[1]
        
    PARAMS = {
           "action": "query",
           "format": "json",
           "list": "users",
           "usprop": "",
           "ususers": newUsername
        }
    
    R = S.get(url = URL, params = PARAMS)
    json = R.json()
    user = json["query"]["users"][0]
    newUserId = str(user["userid"])
    
    print(oldUserId, ":", newUserId)
    if oldUserId == newUserId:
        usersNotToRetrieve.append(newUsername)
    else:
        usersToRetrieve.append(newUsername)

outDf = pd.DataFrame({"usersToRetrieve":usersToRetrieve})
outDf.to_csv("/home/madhavso/wikipedia_data/user_lists/usersToRetrieve.csv", index = False, encoding = "utf-8")

with open("/home/madhavso/wikipedia_data/user_lists/usersNotToRetrieve.txt", "w", encoding = "utf-8") as oF:
    for u in usersNotToRetrieve:
        oF.write(u + "\n")

        
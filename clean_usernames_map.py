# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 16:29:16 2022

@author: madha
"""

import pandas as pd

#remove all forward-slashes and everything that comes after from right column in usernamesMap
#replace all underscores with spaces and strip white-space
usernameMapDfPath = r"C:\Users\madha\Documents\WikiProject\user_lists\usernamesMap.csv"
usernameMapDf = pd.read_csv(usernameMapDfPath, encoding = "utf-8")
for i in usernameMapDf.index:
    name = usernameMapDf["mostRecentUsername"][i]
    if "/" in name:
        name = name.split("/", maxsplit = 1)[0]
    name = name.replace("_", " ").strip()
    usernameMapDf.loc[i, "mostRecentUsername"] = name


lookupDf = pd.read_csv(r"C:\Users\madha\Documents\WikiProject\top_editors\1-10000_union_lookup_updated.csv", encoding = "utf-8")
lookup = {}
for i in lookupDf.index:
    lookup[lookupDf["user"][i]] = lookupDf["userNumber"][i]

topEditorsMapDf = pd.read_csv(r"C:\Users\madha\Documents\WikiProject\top_editors\usernamesMapTopEditors.csv", encoding = "utf-8")

#remove forward-slashes, replace underscores with spaces, strip white-space
for i in topEditorsMapDf.index:
    name = topEditorsMapDf["mostRecentUsername"][i]
    if "/" in name:
        name = name.split("/", maxsplit = 1)[0]
    name = name.replace("_", " ").strip()
    topEditorsMapDf.loc[i, "mostRecentUsername"] = name

#if recentUsername isn't in lookup, then set recentUsername to oldUsername
for i in topEditorsMapDf.index:
    oldUsername = topEditorsMapDf["username"][i]
    recentUsername = topEditorsMapDf["mostRecentUsername"][i]
    if oldUsername != recentUsername:
        ID = lookup.get(recentUsername, -1)
        if ID == -1:
            topEditorsMapDf.loc[i, "mostRecentUsername"] = oldUsername

topEditorsMap = {}
for i in topEditorsMapDf.index:
    topEditorsMap[topEditorsMapDf["username"][i]] = topEditorsMapDf["mostRecentUsername"][i]

count = 0
for i in usernameMapDf.index:
    oldUsername = usernameMapDf["username"][i]
    if oldUsername in topEditorsMap.keys() and usernameMapDf["mostRecentUsername"][i] != topEditorsMap[oldUsername]:
        usernameMapDf.loc[i, "mostRecentUsername"] = topEditorsMap[oldUsername]
        print(oldUsername, ":", topEditorsMap[oldUsername])
        count += 1

usernameMapDf.to_csv(usernameMapDfPath, index = False, encoding = "utf-8")
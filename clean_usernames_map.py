# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 16:29:16 2022

@author: madha
"""

import pandas as pd

# paths
lookupPath = r"C:\Users\madha\Documents\WikiProject\top_editors\topEditorsLookup.csv"
topEditorsMapPath = r"C:\Users\madha\Documents\WikiProject\top_editors\usernamesMapTopEditors.csv"
usernameMapDfPath = r"C:\Users\madha\Documents\WikiProject\user_lists\usernamesMap.csv"
topEditorsOutPath = r"C:\Users\madha\Documents\WikiProject\top_editors\usernamesMapTopEditors_new.csv"

topEditorsMapDf = pd.read_csv(topEditorsMapPath, encoding = "utf-8")

#remove forward-slashes, replace underscores with spaces, strip white-space
for i in topEditorsMapDf.index:
    name = topEditorsMapDf["mostRecentUsername"][i]
    cleanedName = name
    if "/" in cleanedName:
        cleanedName = cleanedName.split("/", maxsplit = 1)[0]
    cleanedName = cleanedName.replace("_", " ").strip()
    if cleanedName != name:
        topEditorsMapDf.loc[i, "mostRecentUsername"] = cleanedName
        #print(name, ":", cleanedName)

lookupDf = pd.read_csv(r"C:\Users\madha\Documents\WikiProject\top_editors\topEditorsLookup.csv", encoding = "utf-8")
lookup = {}
for i in lookupDf.index:
    lookup[lookupDf["user"][i]] = lookupDf["userNumber"][i]
    
#remove all forward-slashes and everything that comes after from right column in usernamesMap
#replace all underscores with spaces and strip white-space
usernameMapDf = pd.read_csv(usernameMapDfPath, encoding = "utf-8")
count = 1
for i in usernameMapDf.index:
    oldName = usernameMapDf["username"][i]
    name = usernameMapDf["mostRecentUsername"][i]
    cleanedName = name
    if "/" in cleanedName:
        cleanedName = cleanedName.split("/", maxsplit = 1)[0]
    cleanedName = cleanedName.replace("_", " ").strip()
    if cleanedName != name:
        usernameMapDf.loc[i, "mostRecentUsername"] = cleanedName
        print(name, ":", cleanedName)
    
    # if the current username of a user is not in top editors but the old username is, keep the old username
    if oldName in lookup.keys() and cleanedName not in lookup.keys():
        print(count, oldName, ":", cleanedName)
        usernameMapDf.loc[i, "mostRecentUsername"] = oldName

usernameMapDf.to_csv(usernameMapDfPath, index = False, encoding = "utf-8")
topEditorsMapDf.to_csv(topEditorsOutPath, index = False, encoding = "utf-8")
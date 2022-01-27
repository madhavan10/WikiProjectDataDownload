# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 23:24:13 2022

@author: madha
"""

import csv
import pandas as pd
from collections import OrderedDict
import os
import sys # for errors
import traceback # for errors

# TODO:
# 1) How to load saved newLookup table file and avoid repeating 
#    already-completed merges?
# 2) Try-except, save state of newLookup table using DataFrame.to_csv 
        

# input paths
usernameMapPath = "/home/madhavso/wikipedia_data/user_lists/usernamesMapTopEditors.csv"
lookupPath = "/home/madhavso/wikipedia_data/user_lists/1-10000_union_lookup.csv"
newLookupPath = "/home/madhavso/wikipedia_data/user_lists/mergedFilesLookup.csv"

# vars
usernameMapDf = pd.read_csv(usernameMapPath, encoding = "utf-8")
lookupNameToFileNum = {}
newLookup = OrderedDict() # old filename to new (possibly merged) file

# populate dict with old username-to-filename table
lookupDf = pd.read_csv(lookupPath, encoding = "utf-8")
for i in lookupDf.index:
    lookupNameToFileNum[lookupDf["user"][i]] = lookupDf["userNumber"][i]

# populate new lookup dict from saved state (if any)
if os.path.exists(newLookupPath):
    newLookupDf = pd.read_csv(newLookupPath, encoding = "utf-8")
    for i in newLookupDf.index:
        newLookup[newLookupDf["old file number"][i]] = newLookupDf["new filename"][i]

for i in usernameMapDf.index:
    
    oldUsername = usernameMapDf["username"][i] # left
    recentUsername = usernameMapDf["mostRecentUsername"][i] # right
    
    oldUsernameFileNum = lookupNameToFileNum[oldUsername]
    if oldUsernameFileNum not in newLookup.keys():
        if oldUsername == recentUsername:
            newLookup[oldUsernameFileNum] = str(oldUsernameFileNum)
        else:
            recentUsernameFileNum = lookupNameToFileNum[recentUsername]
            if recentUsernameFileNum not in newLookup.keys():
                # TODO: perform merge between [oldUsernameFileNum].csv and [recentUsernameFileNum].csv
                newLookup[recentUsernameFileNum] = "m" + str(recentUsernameFileNum)
            else:
                # TODO: perform merge between [oldUsernameFileNum].csv and newLookup[recentUsernameFileNum].csv
                newLookup[recentUsernameFileNum] = "m" + str(recentUsernameFileNum)
            
        
newLookupDf = pd.DataFrame({"old file number": newLookup.keys(), "new filename": newLookup.values()})
newLookupDf.to_csv(newLookupPath, index = False, encoding = "utf-8")
 
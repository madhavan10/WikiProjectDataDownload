# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 23:24:13 2022

@author: madha
"""

import pandas as pd
from collections import OrderedDict
import os
from utils import merge

# input paths
usernameMapPath = "/home/madhavso/wikipedia_data/user_lists/usernamesMapTopEditors.csv"
lookupPath = "/home/madhavso/wikipedia_data/user_lists/topEditorsLookup.csv"
newLookupPath = "/home/madhavso/wikipedia_data/user_lists/mergedFilesLookup.csv"
currentDir = "/home/madhavso/wikipedia_data/top_editors/contributions"

# vars
usernameMapDf = pd.read_csv(usernameMapPath, encoding = "utf-8")
lookupNameToFileNum = {}
newLookup = OrderedDict() # old filename to new (possibly merged) file

# populate dict with old username-to-filename table
lookupDf = pd.read_csv(lookupPath, encoding = "utf-8")
for i in lookupDf.index:
    lookupNameToFileNum[lookupDf["user"][i]] = lookupDf["userNumber"][i]

# populate new lookup dict from saved state (if any)
# if os.path.exists(newLookupPath):
#     newLookupDf = pd.read_csv(newLookupPath, encoding = "utf-8")
#     for i in newLookupDf.index:
#         newLookup[newLookupDf["old file number"][i]] = newLookupDf["new filename"][i]

os.chdir(currentDir)
for i in usernameMapDf.index:
    
    oldUsername = usernameMapDf["username"][i] # left
    recentUsername = usernameMapDf["mostRecentUsername"][i] # right
    
    oldUsernameFileNum = lookupNameToFileNum[oldUsername]
    if oldUsernameFileNum not in newLookup.keys():
        if oldUsername == recentUsername:
            newLookup[oldUsernameFileNum] = str(oldUsernameFileNum)
        else:
            recentUsernameFileNum = lookupNameToFileNum.get(recentUsername, -1)
            if recentUsernameFileNum == -1:
                # do not have contribs file for recentUsername
                newLookup[oldUsernameFileNum] = str(oldUsernameFileNum)
                continue
            ofileNumStr = "m" + str(recentUsernameFileNum)
            if recentUsernameFileNum not in newLookup.keys():
                # TODO: perform merge between [oldUsernameFileNum].csv and [recentUsernameFileNum].csv
                print("Merging " + str(oldUsernameFileNum) + "(" + oldUsername + ") with "\
                      + str(recentUsernameFileNum) + "(" + recentUsername + ")")
                merge(str(oldUsernameFileNum) + ".csv", str(recentUsernameFileNum) + ".csv", ofileNumStr + ".csv")
            else:
                # TODO: perform merge between [oldUsernameFileNum].csv and newLookup[recentUsernameFileNum].csv
                print("Merging " + str(oldUsernameFileNum) + "(" + oldUsername + ") with "\
                      + newLookup[recentUsernameFileNum] + "(" + recentUsername + ")")
                merge(str(oldUsernameFileNum) + ".csv", newLookup[recentUsernameFileNum] + ".csv", ofileNumStr + ".csv")
            newLookup[recentUsernameFileNum] = ofileNumStr
            
        
newLookupDf = pd.DataFrame({"old file number": newLookup.keys(), "new filename": newLookup.values()})
newLookupDf.to_csv(newLookupPath, index = False, encoding = "utf-8")
 
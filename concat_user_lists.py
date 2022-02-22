# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 12:05:33 2021

@author: madha
"""

import pandas as pd
import os
from collections import OrderedDict

projectNameLookup = OrderedDict()
projectNameLookupDf = pd.read_csv(r"C:\users\madha\documents\wikiproject\projectIdLookup.csv", encoding = "utf-8")

membersListsInputsDf = pd.read_excel("C:/users/madha/dropbox/wikiproject_data_download/retrieve_members_input_vars.xlsx")
projectTypeLookup = OrderedDict()
for i in membersListsInputsDf.index:
    projectType = membersListsInputsDf["type"][i]
    projectTypeLookup[membersListsInputsDf["wikiproject"][i]] = projectType if pd.notna(projectType) else "sr"

for i in projectNameLookupDf.index:
    projectNameLookup[projectNameLookupDf["projectId"][i]] = projectNameLookupDf["projectName"][i]

dfs = []
os.chdir(r"C:\users\madha\documents\wikiproject\user_lists\new_way")
for file in os.listdir():
    df = pd.read_csv(file, encoding = "utf-8")
    df.drop(columns = "source", inplace = True)
    fileNumber = int(file.rsplit(".", maxsplit = 1)[0])
    projectName = projectNameLookup[fileNumber]
    df["project"] = projectName
    df["type"] = projectTypeLookup[projectName]
    df["membership"] = "list"
    dfs.append(df)

outDf = pd.concat(dfs, ignore_index = True)
outDf.to_csv(r"C:\users\madha\documents\wikiproject\user_lists\complete_user_list.csv", index = False, encoding = "utf-8")

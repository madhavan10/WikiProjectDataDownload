# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 14:47:25 2022

@author: madha
"""

import pandas as pd
import os
from collections import OrderedDict

projectNameLookup = OrderedDict()
projectNameLookupDf = pd.read_csv(r"C:\users\madha\documents\wikiproject\userboxProjectLookup.csv", encoding = "utf-8")

for i in projectNameLookupDf.index:
    projectNameLookup[projectNameLookupDf["id"][i]] = projectNameLookupDf["project"][i]
    
userboxInputsDf = pd.read_excel(r"C:\Users\madha\Dropbox\wikiproject_data_download\wikiproject_userboxes.xlsx")
dfs = []
dfs.append(pd.read_csv(r"C:\Users\madha\Documents\WikiProject\user_lists\complete_user_list.csv", encoding = "utf-8"))

os.chdir("C:/users/madha/documents/wikiproject/user_lists/userbox_projects")
for file in os.listdir():
    if file.rsplit(".", maxsplit = 1)[-1] != "csv":
        continue
    print(file)
    df = pd.read_csv(file, encoding = "utf-8")
    renameMap = {"user": "member", "join-date": "joinDate"}
    df.rename(columns = renameMap, inplace = True)
    df.drop(columns = ["matchedText", "matchedPage"], inplace = True)
    df["membership"] = "ubx"
    if df["type"][0] == "s":
        df["type"] = "sr"
    df = df[["member", "project", "type", "membership", "joinDate"]]
    dfs.append(df)
    
outDf = pd.concat(dfs, ignore_index = True)
outDf.to_csv("C:/users/madha/documents/wikiproject/user_lists/complete_user_list_with_ubx_projects.csv", index = False, encoding = "utf-8")
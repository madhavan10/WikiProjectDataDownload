# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 19:16:23 2022

@author: madha
"""

import pandas as pd
import os
import csv


def getUserId(filename):
    contribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
    with open(os.path.join(contribsDir, filename), newline = "", encoding = "utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        row = next(reader)
        userid = row[1]
        return userid

outPath = "/home/madhavso/wikipedia_data/top_editors/projectJoinDatesAllUsers.csv"
userLookupPath = "/home/madhavso/wikipedia_data/user_lists/topEditorsLookup.csv"
joinDatesDir = "/home/madhavso/wikipedia_data/top_editors/projectJoinDates"

userLookupDf = pd.read_csv(userLookupPath, encoding = "utf-8")
userLookup = {}
for i in userLookupDf.index:
    userLookup[userLookupDf["userNumber"][i]] = userLookupDf["user"][i]
    
os.chdir(joinDatesDir)
dfs = []
for file in os.listdir():
    df = pd.read_csv(file, encoding = "utf-8")
    df.drop(columns = "pageTitle", inplace = True)
    df["userid"] = getUserId(file)
    # insert userid column at the front
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[0:-1]
    df = df[cols]
    dfs.append(df)

outDf = pd.concat(dfs, ignore_index = True)
outDf.to_csv(outPath, index = False, encoding = "utf-8")
    
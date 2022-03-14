# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 10:57:39 2022

@author: madha
"""

import csv
import os
import pandas as pd

def getUserId(filename):
    contribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
    with open(os.path.join(contribsDir, filename), newline = "", encoding = "utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        row = next(reader)
        userid = row[1]
        return userid
    
outPath = "/home/madhavso/wikipedia_data/top_editors/unmatchedProjectsAllUsers.csv"
unmatchedProjectsDir = "/home/madhavso/wikipedia_data/top_editors/unmatchedProjects"

os.chdir(unmatchedProjectsDir)
dfs = []

for file in os.listdir():
    df = pd.read_csv(file, encoding = "utf-8")
    df["userid"] = getUserId(file)
    # insert userid column at the front
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[0:-1]
    df = df[cols]
    dfs.append(df)

outDf = pd.concat(dfs, ignore_index = True)
outDf.to_csv(outPath, index = False, encoding = "utf-8")
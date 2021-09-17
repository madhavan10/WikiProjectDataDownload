# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 11:48:32 2021

@author: madha
"""
import pandas as pd

inputPath1 = r"C:\users\madha\documents\wikiproject\project_join\military_history_intermediate.csv"
inputPath2 = r"C:\users\madha\documents\wikiproject\project_join\military_history_members_active.csv"
outputPath = r"C:\users\madha\documents\wikiproject\project_join\military_history_final.csv"

df1 = pd.read_csv(inputPath1, encoding = "utf-8")
df2 = pd.read_csv(inputPath2, encoding = "utf-8")

df = pd.concat([df1, df2], ignore_index = True)

setOfUsers = set()
toDrop = []
for i in df.index:
    if df["userid"][i] not in setOfUsers:
        setOfUsers.add(df["userid"][i])
    else:
        toDrop.append(i)

print(toDrop)

df.drop(index = toDrop, inplace = True)

df.to_csv(outputPath, index = False, encoding = "utf-8")


# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 22:56:59 2021

@author: madha
"""

import pandas as pd

def lower_set(s):
    result = set()
    for elt in s:
        result.add(elt.lower())
    return result

userListPath1 = r"C:\users\madha\documents\wikiproject\user_lists\military_history_members_active.txt"
userListPath2 = r"C:\users\madha\documents\wikiproject\user_lists\military_history_members_inactive.txt"
csvPath = r"C:\users\madha\documents\wikiproject\project_join\military_history_final.csv"
outputCsvPath = r"C:\users\madha\documents\wikiproject\project_join\military_history_checked.csv"

with open(userListPath1, "r", encoding = "utf-8") as usersFile:
    fullText = usersFile.read()
    users = set(fullText.split("\n"))

if userListPath2 != "":        
    with open(userListPath2, "r", encoding = "utf-8") as usersFile:
        fullText = usersFile.read()
        users2 = fullText.split("\n")
        for user in users2:
            users.add(user)

if "" in users:
    users.remove("")
    
df = pd.read_csv(csvPath, encoding = "utf-8")
toDrop = []

lowerSet = lower_set(users)
lowerSetDf = lower_set(list(df["user"]))
for i in df.index:
    if df["user"][i].lower() not in lowerSet:
        toDrop.append(i)
        
unaccounted_for = set()
for user in lowerSet:
    if user not in lowerSetDf:
        unaccounted_for.add(user)

print("Number of editors from edit history:", len(df))
print("Number of participants from participant list(s):", len(users))
print("Number of editors not in participant list(s):", len(toDrop))
print("Number of participants not in edit history:", len(unaccounted_for))

df.drop(index = toDrop, inplace = True)
print("Dropped ", len(toDrop), " users from edit history data")
df.to_csv(outputCsvPath, index = False, encoding = "utf-8")

# def find_duplicates(l):
#     count = dict()
#     for elt in l:
#         if elt in count:
#             count[elt] = count[elt] + 1
#         else:
#             count[elt] = 1
#     result = []
#     for k, v in count.items():
#         if v > 1:
#             result.append((k, v))
#     return result

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 22:56:59 2021

@author: madha
"""

import pandas as pd
import os
import csv
from datetime import date
import sys


def get_properties_from_file(filename):
    properties = dict()
    with open(filename) as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
    return properties

try:
    properties = get_properties_from_file(sys.argv[1])
except IndexError:
    raise Exception("Specify a properties file as an argument to this script.")

retrieveEditorsInputsPath = os.path.abspath(properties["retrieveEditorsInputsPath"])
retrieveMembersInputsPath = os.path.abspath(properties["retrieveMembersInputsPath"])
projectRootDir = os.path.abspath(properties["projectRootDir"])

projectName = properties["projectName"]

def lower_set(s):
    result = set()
    for elt in s:
        result.add(elt.lower())
    return result

editorsInputsDf = pd.read_excel(retrieveEditorsInputsPath)
editorsInputsDf = editorsInputsDf[editorsInputsDf["wikiproject"] == projectName].reset_index(drop = True)
membersInputsDf = pd.read_excel(retrieveMembersInputsPath)
membersInputsDf = membersInputsDf[membersInputsDf["wikiproject"] == projectName].reset_index(drop = True)

editorsPath = os.path.abspath(editorsInputsDf["csvOutputPath"][0])
membersPath = os.path.abspath(membersInputsDf["outputPath"][0])
outputCsvPath = os.path.join(editorsPath.rsplit(os.sep, maxsplit = 1)[0], "final.csv")

membersDf = pd.read_csv(membersPath, encoding = "utf-8")    
editorsDf = pd.read_csv(editorsPath, encoding = "utf-8")

lowerSetMembers = lower_set(set(membersDf["member"]))
toDrop = []

for i in editorsDf.index:
    if editorsDf["user"][i].lower() not in lowerSetMembers:
        toDrop.append(i)

finalDf = editorsDf.drop(index = toDrop)
finalDf.to_csv(outputCsvPath, index = False, encoding = "utf-8")        

statsPath = os.path.join(projectRootDir, "stats.csv")
NumberOfMembersNotInEditHistory = len(lowerSetMembers) - (len(editorsDf) - len(toDrop))
with open(statsPath, "a", newline = "") as statsCsv:
    csvWriter = csv.writer(statsCsv, quoting = csv.QUOTE_MINIMAL)
    csvWriter.writerow([date.today(), projectName, len(editorsDf), len(lowerSetMembers), len(toDrop),\
                        NumberOfMembersNotInEditHistory, NumberOfMembersNotInEditHistory * 100 / len(lowerSetMembers)])
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

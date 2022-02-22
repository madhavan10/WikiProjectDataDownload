# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:53:31 2021

@author: madha
"""

import pandas as pd
from collections import OrderedDict
import os

inputPath = r"C:\users\madha\documents\WikiProject\projectIdLookup.csv"
outputPath = inputPath.rsplit(".", maxsplit = 1)[0] + "_1.csv"

inputsDf = pd.read_excel(r"C:\users\madha\dropbox\wikiproject_data_download\retrieve_members_input_vars.xlsx")
#grouped = inputsDf.groupby("wikiproject")
projectIdLookup = OrderedDict()

if os.path.exists(inputPath):
    projectIdLookupDf = pd.read_csv(inputPath, encoding = "utf-8")
    for i in projectIdLookupDf.index:
        projectIdLookup[projectIdLookupDf["projectName"][i]] = projectIdLookupDf["projectId"][i]

i = max(list(projectIdLookup.values())) + 1
for project in list(inputsDf["wikiproject"]):
    if project not in projectIdLookup.keys():
        projectIdLookup[project] = i
        i += 1

outputDf = pd.DataFrame({"projectId": projectIdLookup.values(), "projectName": projectIdLookup.keys()})
outputDf.to_csv(outputPath, index = False, encoding = "utf-8")
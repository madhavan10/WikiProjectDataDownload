# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 13:03:41 2022

@author: madha
"""

import pandas as pd

userboxInputVarsPath = "C:/users/madha/dropbox/wikiproject_data_download/wikiproject_userboxes.xlsx"
userboxInputsDf = pd.read_excel(userboxInputVarsPath)

outputPath = "C:/users/madha/documents/wikiproject/userboxProjectLookup.csv"

grouped = userboxInputsDf.groupby("Project")

i = 0
names = []
ids = []
for name, group in grouped:
    names.append(name)
    ids.append(i)
    i += 1
    
outDf = pd.DataFrame({"project": names, "id": ids})
outDf.to_csv(outputPath, index = False, encoding = "utf-8")

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 12:24:48 2022

@author: madha
"""

import pandas as pd
from collections import OrderedDict

membersListsInputsDf = pd.read_excel("C:/users/madha/dropbox/wikiproject_data_download/retrieve_members_input_vars.xlsx")
projectTypeLookup = OrderedDict()
for i in membersListsInputsDf.index:
    projectType = membersListsInputsDf["type"][i]
    projectTypeLookup[membersListsInputsDf["wikiproject"][i]] = projectType if pd.notna(projectType) else "sr"

outDf = pd.DataFrame({"project": projectTypeLookup.keys(), "type": projectTypeLookup.values()})
outDf.to_csv(r"C:\users\madha\documents\wikiproject\projectTypeLookup.csv", index = False, encoding = "utf-8")    
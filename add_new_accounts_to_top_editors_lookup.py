# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 14:03:26 2022

@author: madha
"""

import pandas as pd
from collections import OrderedDict

lookupPath = "/home/madhavso/wikipedia_data/user_lists/1-10000_union_lookup_updated.csv"
lookupDf = pd.read_csv(lookupPath, encoding = "utf-8")
lookup = OrderedDict()
for i in lookupDf.index:
    lookup[lookupDf["user"][i]] = lookupDf["userNumber"][i]

usersPath = "/home/madhavso/wikipedia_data/user_lists/usersToRetrieve.csv"
usersDf = pd.read_csv(usersPath, encoding = "utf-8")

i = max(list(lookup.values())) + 1
for username in usersDf["usersToRetrieve"]:
    lookup[username] = i
    i += 1

outDfPath = "/home/madhavso/wikipedia_data/user_lists/topEditorsLookup.csv"
outDf = pd.DataFrame({"user": lookup.keys(), "userNumber": lookup.values()})
outDf.to_csv(outDfPath, index = False, encoding = "utf-8")

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 15:50:08 2022

@author: madha
"""

import pandas as pd
import os

mainContribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
filename = "5029.csv"
mainFilePath = os.path.join(mainContribsDir, filename) 
minorFilePath = os.path.join(mainContribsDir, "minor", filename)

print("reading in main file...")
dfMain = pd.read_csv(mainFilePath, encoding = "utf-8")
print("--done")
userIdMain = dfMain["userid"][0]

print("reading in minor file...")
dfMinor = pd.read_csv(minorFilePath, encoding = "utf-8")
print("--done")
userIdMinor = dfMinor["userid"][0]

if userIdMain != userIdMinor:
    print("User ids don't match")
else:
    print("User ids match")

dfMinor.drop(columns = "userid", inplace = True)

mergedDf = dfMain.merge(dfMinor, how = "inner", on = "revid")

print("Lengths:")
print("Main", len(dfMain))
print("Minor", len(dfMinor))
print("Merged", len(mergedDf))



# TODO change for loop
# mergedDf.to_csv(os.path.join("/home/madhavso/wikipedia_data/top_editors/contributions/big_file_test", filename), index = False, encoding = "utf-8")

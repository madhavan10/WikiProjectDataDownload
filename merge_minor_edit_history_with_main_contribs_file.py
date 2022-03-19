# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 15:50:08 2022

@author: madha
"""

import pandas as pd
import os

mainContribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
mergedContribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions/with_minor_edit_flag"
for filename in os.listdir(mainContribsDir):
    if filename.rsplit(".", maxsplit = 1)[-1] != "csv":
        continue
    if filename.startswith("m"):
        continue
    print(filename)
    mainFilePath = os.path.join(mainContribsDir, filename) 
    minorFilePath = os.path.join(mainContribsDir, "minor", filename)
    
    dfMain = pd.read_csv(mainFilePath, encoding = "utf-8")
    userIdMain = dfMain["userid"][0]
    
    dfMinor = pd.read_csv(minorFilePath, encoding = "utf-8")
    userIdMinor = dfMinor["userid"][0]
    
    if userIdMain != userIdMinor:
        print("User ids don't match")
        break
    
    dfMinor.drop(columns = "userid", inplace = True)
    
    mergedDf = dfMain.merge(dfMinor, how = "inner", on = "revid")

    mergedDf.to_csv(os.path.join(mergedContribsDir, filename), index = False, encoding = "utf-8")

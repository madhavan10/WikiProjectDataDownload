# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 15:34:46 2022

@author: madha
"""

import pandas as pd
import os

contribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
os.chdir(contribsDir)
for file in os.listdir():
    split = file.rsplit(".", maxsplit = 1)
    if split[-1] != "csv":
        continue
    if split[0].startswith("m"):
        continue
    fileNo = int(split[0])
    if fileNo <= 15994:
        continue
    
    df = pd.read_csv(file, encoding = "utf-8")
    df.drop(columns = "minor", inplace = True)
    df.to_csv(file, index = False, encoding = "utf-8")
    
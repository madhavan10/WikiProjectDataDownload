# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 19:08:10 2022

@author: madha
"""

import os
import csv
import pandas as pd
os.chdir("/home/madhavso/wikipedia_data/top_editors/contributions/rest")
output_path = "/home/madhavso/wikipedia_data/user_lists/10000_minus_union.csv"
df = pd.DataFrame(columns = ["filename", "lines", "username"])
filenames = []
lines = []
usernames  = []
for file in os.listdir():
    split = file.rsplit(".", maxsplit = 1)
    if split[-1] != "csv":
        continue
    with open(file, "r", newline = "", encoding = "utf-8") as f:
        count = -1
        reader = csv.reader(f)
        for line in reader:
            count += 1
            if count == 0:
                username = "NO CONTRIBS"
            if count == 1:
                username = line[0]

    filenames.append(file)
    lines.append(count)
    usernames.append(username)

df.to_csv(output_path, index = False, encoding = "utf-8")
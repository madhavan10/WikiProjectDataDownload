# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 14:42:22 2021

@author: madha
"""

import pandas as pd
import sys
import os

def get_properties_from_file(filename):
    properties = dict()
    with open(filename) as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
    return properties

properties = get_properties_from_file(sys.argv[1])
projectRootDir = properties["projectRootDir"]
projectFilename = properties["projectFilename"]

csvPath = os.path.join(os.path.abspath(projectRootDir), "project_join", projectFilename, "way2.csv")
outPath = os.path.join(csvPath.rsplit(os.sep, maxsplit = 1)[0], "years.csv")
df = pd.read_csv(csvPath, encoding = "utf-8")

years = []
for i in df.index:
    years.append("'" + df["Join Date"][i][:4])

df["Join Year"] = years

grouped = df.groupby("Join Year")

years = []
frequencies = []
for name, group in grouped:
    years.append(name)
    frequencies.append(len(group))

new_df = pd.DataFrame({"year": years, "frequency": frequencies})

new_df.to_csv(outPath, index = False, encoding = "utf-8")
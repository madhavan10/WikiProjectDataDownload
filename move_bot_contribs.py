# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 11:27:35 2022

@author: madha
"""

import pandas as pd
import os

path = "/home/madhavso/wikipedia_data/user_lists/union_minus_10000_whether_bot_updated.csv"
df = pd.read_csv(path, encoding = "utf-8")
df_bots = df[df["botTagFound"] == "yes"]
print("Number of bots:", len(df_bots))

root_dir = "/home/madhavso/wikipedia_data/top_editors/contributions/rest"
os.chdir(root_dir)
#for filename in df_bots["filename"]:
#    os.rename(os.path.join(root_dir, filename), os.path.join(root_dir, "bots", filename))
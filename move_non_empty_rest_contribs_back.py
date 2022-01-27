# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 14:33:12 2022

@author: madha
"""

import os

root_dir = "/home/madhavso/wikipedia_data/top_editors/contributions"
rest_dir = os.path.join(root_dir, "rest")
os.chdir(rest_dir)
for file in os.listdir():
    split = file.rsplit(".", maxsplit = 1)
    if split[-1] != "csv":
        continue
    if os.path.getsize(file) >= 77:
        os.rename(os.path.join(rest_dir, file), os.path.join(root_dir, file))

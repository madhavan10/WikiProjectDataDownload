# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 16:51:46 2022

@author: madha
"""

import os

mainContribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions"
minorContribsDir = os.path.join(mainContribsDir, "minor")

count = 0
os.chdir(minorContribsDir)
for filename in os.listdir():
    stream = os.popen("wc -l " + filename)
    output = stream.read()
    lines2 = int(output.split(" ", maxsplit = 1)[0])
    
    stream = os.popen("wc -l " + mainContribsDir + "/" + filename)
    output = stream.read()
    lines1 = int(output.split(" ", maxsplit = 1)[0])
    

    ratio = lines2/lines1
    if ratio < 0.98:
        count += 1
        print(filename, lines2, lines1, ratio)

print("count:", count)
        
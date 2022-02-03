# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 14:08:39 2022

@author: madha
"""

import csv

USERID_INDEX = 1
TIMESTAMP_INDEX = 2
SIZEDIFF_INDEX = 10

ifile = "/home/madhavso/wikipedia_data/top_editors/contributions/test/5888.csv"
ofile = ifile.rsplit(".", maxsplit = 1)[0] + "_copy.csv"
with open(ofile, "w", newline = "", encoding = "utf-8") as oF:
    writer = csv.writer(oF, quoting = csv.QUOTE_MINIMAL)
    with open(ifile, newline = "", encoding = "utf-8") as inF:
        reader = csv.reader(inF)
        rowNumber = 0
        for row in reader:
            newRow = [row[USERID_INDEX], row[TIMESTAMP_INDEX], row[SIZEDIFF_INDEX]]
            writer.writerow(newRow)
            rowNumber += 1
        print("Wrote ", rowNumber, " rows")

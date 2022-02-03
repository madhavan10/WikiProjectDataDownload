# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 11:14:00 2022

@author: madha
"""

import os
import csv
import pandas as pd

resumeFilePath = "/home/madhavso/wikipedia_data/top_editors/contributions/all_users_file/resume.csv"
mergedFilesLookupPath = "/home/madhavso/wikipedia_data/user_lists/mergedFilesLookup.csv"
outPath = "/home/madhavso/wikipedia_data/top_editors/contributions/all_users_file/contributions.csv"
contribsDir = "/home/madhavso/wikipedia_data/top_editors/contributions/test"

# if concat was interrupted, get params about where to resume
if os.path.exists(resumeFilePath) and os.path.getsize(resumeFilePath) > 0:
    with open(resumeFilePath, newline = "") as resumeF:
        rReader = csv.reader(resumeF)
        rRow = next(rReader)
        fileIndex = int(rRow[0]) # current file
        rowNumber = int(rRow[1]) # last line number written
else:
    fileIndex = 0
    rowNumber = 0

mergedFilesLookupDf = pd.read_csv(mergedFilesLookupPath, encoding = "utf-8")
filesToConcat = list(mergedFilesLookupDf["new filename"])
outPathExists = os.path.exists(outPath)

USERID_INDEX = 1
TIMESTAMP_INDEX = 2
SIZEDIFF_INDEX = 10

os.chdir(contribsDir)
with open(outPath, "a", newline = "", encoding = "utf-8") as ofile:
    writer = csv.writer(ofile, quoting = csv.QUOTE_MINIMAL)
    if not outPathExists:
        writer.writerow(["userid", "timestamp", "sizediff"])
    fileIndexCopy = fileIndex
    try:
        for i in range(fileIndexCopy, len(filesToConcat)):
            with open(filesToConcat[i] + ".csv", "r", newline = "", encoding = "utf-8") as iCsv:
                print(i, ":", filesToConcat[i])
                reader = csv.reader(iCsv)
                # skip over already-written rows
                for skipCounter in range(rowNumber):
                    next(reader)
                # remaining rows
                for row in reader:
                    # drop columns except for userid, timestamp, sizediff
                    newRow = [row[USERID_INDEX], row[TIMESTAMP_INDEX], row[SIZEDIFF_INDEX]]
                    writer.writerow(newRow)
                    rowNumber += 1
                print("Wrote ", rowNumber, " rows")
                rowNumber = 0
            fileIndex += 1
    except BaseException:
        with open(resumeFilePath, "w", newline = "") as resumeF:
            rWriter = csv.writer(resumeF)
            rWriter.writerow([str(fileIndex), str(rowNumber)])
        raise
os.remove(resumeFilePath)
    
        
        


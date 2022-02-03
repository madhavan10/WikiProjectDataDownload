# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 14:43:26 2021

@author: madha
"""

import pandas as pd
from collections import OrderedDict
import csv
import os
import re

projectMembershipCsvPath = "/home/madhavso/wikipedia_data/user_lists/projectMembership.csv"
userLookupPath = "/home/madhavso/wikipedia_data/user_lists/1-10000_union_lookup_updated.csv"
mergedFilesListPath = "/home/madhavso/wikipedia_data/user_lists/mergedFilesLookup.csv"
topEditorsRootDir = "/home/madhavso/wikipedia_data/top_editors"
dfProjectMembership = pd.read_csv(projectMembershipCsvPath, encoding = "utf-8")
userLookupDf = pd.read_csv(userLookupPath, encoding = "utf-8")
userLookup = {}
for i in userLookupDf.index:
    userLookup[userLookupDf["userNumber"][i]] = userLookupDf["user"][i]
mergedFilesListDf = pd.read_csv(mergedFilesListPath, encoding = "utf-8")
mergedFilesList = list(mergedFilesListDf["new filename"])

usernameToProjectMembership = OrderedDict()

for i in dfProjectMembership.index:
    user = dfProjectMembership["user"][i]
    project = dfProjectMembership["project"][i]
    if user not in usernameToProjectMembership.keys():
        usernameToProjectMembership[user] = []
    usernameToProjectMembership[user].append(project)

for mFilename in mergedFilesList:
    if mFilename.startswith("m"):
        filename = mFilename[1:]
    else:
        filename = mFilename
    fullFilename = filename + ".csv"
    joinDatesDfPath = os.path.join(topEditorsRootDir, "projectJoinDates", fullFilename)
    unmatchedProjectsDfPath = os.path.join(topEditorsRootDir, "unmatchedProjects", fullFilename)
    if os.path.exists(joinDatesDfPath) and os.path.exists(unmatchedProjectsDfPath):
        continue
    userLookupId = int(filename)
    contribsCsvPath = os.path.join(topEditorsRootDir, "contributions", mFilename + ".csv")
    user = userLookup[userLookupId]
    if user in usernameToProjectMembership.keys():
        print(user, mFilename + ".csv")
        projectList = usernameToProjectMembership[user]
        regexList = []
        ifMatched = []
        joinDates = []
        titles = []
        matchedProjects = []
        for project in projectList:
            projectRegexVersion = project.replace(".", "\\.")
            projectRegexVersion = projectRegexVersion.replace("+", "\\+")
            projectRegexVersion = projectRegexVersion.replace("(", "\\(")
            projectRegexVersion = projectRegexVersion.replace(")", "\\)")
            regex = "Wikipedia:(" + projectRegexVersion + "|" + projectRegexVersion +\
                ".*(members?|participants?|contributors|volunteers|roster).*)"
            regexList.append(regex)
            ifMatched.append(False)
        with open(contribsCsvPath, "r", newline = "", encoding = "utf-8") as contribsCsv:
            reader = csv.reader(contribsCsv)
            for row in reader:
                TIMESTAMP_INDEX = 2
                TITLE_INDEX = 5
                NS_INDEX = 3
                if row[NS_INDEX] != "4":
                    continue
                title = row[TITLE_INDEX]
                for i in range(len(regexList)):
                    if ifMatched[i]:
                        continue
                    match = re.fullmatch(regexList[i], title, flags = re.IGNORECASE)
                    if match:
                        joinDates.append(row[TIMESTAMP_INDEX])
                        titles.append(title)
                        matchedProjects.append(projectList[i])
                        ifMatched[i] = True
        joinDatesDf = pd.DataFrame({"joinDate": joinDates, "WikiProject": matchedProjects, "pageTitle": titles})
        joinDatesDf.to_csv(joinDatesDfPath, index = False, encoding = "utf-8")
        unmatchedProjects = []
        for i in range(len(projectList)):
            if ifMatched[i] == False:
                unmatchedProjects.append(projectList[i])
        unmatchedProjectsDf = pd.DataFrame({"user": user, "unmatchedWikiProject": unmatchedProjects})
        unmatchedProjectsDf.to_csv(unmatchedProjectsDfPath, index = False, encoding = "utf-8")

            
            
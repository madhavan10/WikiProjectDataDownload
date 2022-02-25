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

# paths
projectMembershipCsvPath = "/home/madhavso/wikipedia_data/user_lists/projectMembership.csv"
userLookupPath = "/home/madhavso/wikipedia_data/user_lists/topEditorsLookup.csv"
mergedFilesListPath = "/home/madhavso/wikipedia_data/user_lists/mergedFilesLookup.csv"
wpCardsProjects = set(pd.read_csv("/home/madhavso/wikipedia_data/user_lists/WikiProjectCardsLookup.csv", encoding = "utf-8")["project"])
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
    projectType = dfProjectMembership["type"][i]
    projectMembershipType = dfProjectMembership["membership"][i]
    joinDate = dfProjectMembership["joinDate"][i]
    if user not in usernameToProjectMembership.keys():
        usernameToProjectMembership[user] = []
    usernameToProjectMembership[user].append((project, projectType, projectMembershipType, joinDate))

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
        _NAME_INDEX = 0
        _TYPE_INDEX = 1
        _MBSHIP_INDEX = 2
        _JD_INDEX = 3
        projectDetailsList = usernameToProjectMembership[user]
        regexList = []
        ifMatched = []
        # results
        joinDates = []
        titles = []
        matchedProjects = []
        matchedProjectTypes = []
        matchedProjectMbshipTypes = []
        for projectDetails in projectDetailsList:
            projectRegexVersion = projectDetails[_NAME_INDEX].replace(".", "\\.")
            projectRegexVersion = projectRegexVersion.replace("+", "\\+")
            projectRegexVersion = projectRegexVersion.replace("(", "\\(")
            projectRegexVersion = projectRegexVersion.replace(")", "\\)")
            regex = "Wikipedia:(" + projectRegexVersion + "|" + projectRegexVersion +\
                ".*(members?|participants?|contributors|volunteers|roster|sculptors).*)"
            regexList.append(regex)
            ifMatched.append(False)
        with open(contribsCsvPath, "r", newline = "", encoding = "utf-8") as contribsCsv:
            reader = csv.reader(contribsCsv)
            for row in reader:
                TIMESTAMP_INDEX = 2
                TITLE_INDEX = 5
                NS_INDEX = 3
                if row[NS_INDEX] != "4":
                    # if switch to project-specific regexes, take this out
                    continue
                title = row[TITLE_INDEX]
                for i in range(len(regexList)):
                    if ifMatched[i]:
                        continue
                    if projectDetailsList[i][_MBSHIP_INDEX] == "ubx":
                        continue
                    match = re.fullmatch(regexList[i], title, flags = re.IGNORECASE)
                    if match:
                        joinDates.append(row[TIMESTAMP_INDEX])
                        titles.append(title)
                        matchedProjects.append(projectDetailsList[i][_NAME_INDEX])
                        matchedProjectTypes.append(projectDetailsList[i][_TYPE_INDEX])
                        matchedProjectMbshipTypes.append("list")
                        ifMatched[i] = True
        joinDatesDf = pd.DataFrame({"joinDate": joinDates, "WikiProject": matchedProjects, "type": matchedProjectTypes, "membership": matchedProjectMbshipTypes, "pageTitle": titles})
        unmatchedProjects = []
        for i in range(len(projectDetailsList)):
            if ifMatched[i] == False:
                if projectDetailsList[i][_NAME_INDEX] in wpCardsProjects:
                    # add join-dates for projects using WikiProjectCards
                    if pd.notna(projectDetailsList[i][_JD_INDEX]):
                        wpCardsJoinDatesDf = pd.DataFrame({"joinDate": projectDetailsList[i][_JD_INDEX], "WikiProject": projectDetailsList[i][_NAME_INDEX], "type": projectDetailsList[i][_TYPE_INDEX], "membership": projectDetailsList[i][_MBSHIP_INDEX], "pageTitle": ""}, index = [0])
                        # slow method
                        joinDatesDf = pd.concat([joinDatesDf, wpCardsJoinDatesDf], ignore_index = True) 
                    else:
                        unmatchedProjects.append(projectDetailsList[i][_NAME_INDEX])
                elif projectDetailsList[i][_MBSHIP_INDEX] == "ubx":
                    # add join-dates for userbox projects
                    ubxJoinDatesDf = pd.DataFrame({"joinDate": projectDetailsList[i][_JD_INDEX], "WikiProject": projectDetailsList[i][_NAME_INDEX], "type": projectDetailsList[i][_TYPE_INDEX], "membership": projectDetailsList[i][_MBSHIP_INDEX], "pageTitle": ""}, index = [0])
                    # slow method
                    joinDatesDf = pd.concat([joinDatesDf, ubxJoinDatesDf], ignore_index = True)
                else:
                    unmatchedProjects.append(projectDetailsList[i][_NAME_INDEX])
        # addition of join-dates from wpc and ubx projects messes up ascending order of join-dates so sort
        joinDatesDf.sort_values(by = "joinDate", ignore_index = True, inplace = True)
        joinDatesDf.to_csv(joinDatesDfPath, index = False, encoding = "utf-8")
        unmatchedProjectsDf = pd.DataFrame({"user": user, "unmatchedWikiProject": unmatchedProjects})
        unmatchedProjectsDf.to_csv(unmatchedProjectsDfPath, index = False, encoding = "utf-8")

            
            
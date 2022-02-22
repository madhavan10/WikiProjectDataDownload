# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 10:32:07 2021

@author: madha
"""

import pandas as pd
from collections import OrderedDict

usernamesMapCsvPath = r"C:\users\madha\documents\wikiproject\user_lists\usernamesMap.csv"
membersListPath = r"C:\users\madha\documents\wikiproject\user_lists\complete_user_list.csv"

usernameToMostRecentUsername = OrderedDict()
usernamesMapDf = pd.read_csv(usernamesMapCsvPath, encoding = "utf-8")
for i in usernamesMapDf.index:
    usernameToMostRecentUsername[usernamesMapDf["username"][i]] = usernamesMapDf["mostRecentUsername"][i]

usernameToProjectMembership = OrderedDict()
membersListDf = pd.read_csv(membersListPath, encoding = "utf-8")

for i in membersListDf.index:
    member = membersListDf["member"][i]
    project = membersListDf["project"][i]
    projectType = membersListDf["type"][i]
    membershipType = membersListDf["membership"][i]
    joinDate = membersListDf["joinDate"][i] if pd.notna(membersListDf["joinDate"][i]) else ""
    if membershipType == "list" and member in usernameToMostRecentUsername.keys():
        recentUsername = usernameToMostRecentUsername[member]
        if recentUsername not in usernameToProjectMembership.keys():
            usernameToProjectMembership[recentUsername] = OrderedDict()
        usernameToProjectMembership[recentUsername][project] = (projectType, membershipType, joinDate)
    elif membershipType == "ubx":
        if member not in usernameToProjectMembership.keys():
            usernameToProjectMembership[member] = OrderedDict()
        usernameToProjectMembership[member][project] = (projectType, membershipType, joinDate)

userList = []
projectList = []
typeList = []
membershipTypeList = []
joinDateList = []
for user, projectDict in usernameToProjectMembership.items():
    for project, projectDetails in projectDict.items():
        userList.append(user)
        projectList.append(project)
        typeList.append(projectDetails[0])
        membershipTypeList.append(projectDetails[1])
        joinDateList.append(projectDetails[2])
        
dfProjectMembership = pd.DataFrame({"user":userList, "project":projectList, "type": typeList,\
                                    "membership": membershipTypeList, "joinDate": joinDateList})
dfProjectMembership.to_csv(r"C:\users\madha\documents\WikiProject\user_lists\projectMembership.csv", index = False, encoding = "utf-8")
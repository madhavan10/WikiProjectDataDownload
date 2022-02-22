# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:22:55 2021

@author: madha
"""
import pandas as pd
import requests
import os
import re
from collections import OrderedDict
import csv


def extract_users(inputsDf, rootDir, projectFilename):
    
    def record_stats_for_project(csvWriter, projectName, pageName, numberOfUsers):
        csvWriter.writerow([projectName, pageName, numberOfUsers])
        return
    
    def remove_forward_slash(username):
        if "/" in username:
            usernameWithoutForwardSlash = username.split("/", maxsplit = 1)[0]
            return usernameWithoutForwardSlash
        return username
    
    def replace_special_characters(username):
        if "&amp;" in username:
            username = username.replace("&amp;#39;", "'")
            username = username.replace("&amp;#38;", "&")
            username = username.replace("&amp;#34;", "\"")
            username = username.replace("&amp;", "&")
        while "&amp;" in username:
            username = username.replace("&amp;", "&")
        return username
            
    membersListOutputPath = os.path.join(rootDir, "user_lists", "new_way", projectFilename + ".csv")    
    
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    
    users = OrderedDict()
    numberOfUsersByPage = OrderedDict()
    
    for i in inputsDf.index:
    
        page = inputsDf["page"][i]
        userRegex = inputsDf["regex"][i]
        projectName = inputsDf["wikiproject"][i]
        
        if page not in numberOfUsersByPage.keys():
            numberOfUsersByPage[page] = 0
            print(page)
        
        PARAMS = {
                "action": "query",
                "prop": "revisions",
                "titles": page,
                "rvprop": "timestamp|content",
                "rvslots": "main",
                "rvlimit": "1",
                "format": "xml"        
            }
        
        R = S.get(url = URL, params = PARAMS)
        foundUsers = re.findall(userRegex, R.text, flags = re.IGNORECASE)
        for user in foundUsers:
            #clean-up username
            try:
                user = remove_forward_slash(user)
                user = replace_special_characters(user)
                user = user.replace("_", " ")
                user = user.strip()
                user = user[0].upper() + user[1:] if len(user) > 1 else user.upper()
            except TypeError:
                print(user)
                raise
            if user not in users.keys():
                users[user] = page
                numberOfUsersByPage[page] += 1
                
    for pageName in numberOfUsersByPage.keys():
        record_stats_for_project(writer, projectName, pageName, numberOfUsersByPage[pageName])
    
    outputsDf = pd.DataFrame({"member": users.keys(), "source": users.values()})
    outputsDf.to_csv(membersListOutputPath, index = False, encoding = "utf-8")
    
    return

projectRootDir = r"C:\users\madha\documents\wikiproject"

statsPath = os.path.join(projectRootDir, "user_lists", "stats.csv")
statsCsv = open(statsPath, "a", newline="", encoding = "utf-8")
writer = csv.writer(statsCsv, quoting = csv.QUOTE_MINIMAL)
if os.path.getsize(statsPath) == 0:
    writer.writerow(["wikiproject", "page", "numberOfMembersRetrieved"])

projectIdLookup = OrderedDict()
projectIdLookupDf = pd.read_csv(os.path.join(projectRootDir, "projectIdLookup.csv"), encoding = "utf-8")
for i in projectIdLookupDf.index:
    projectIdLookup[projectIdLookupDf["projectName"][i]] = int(projectIdLookupDf["projectId"][i])

inputsDf = pd.read_excel(r"C:\users\madha\dropbox\wikiproject_data_download\retrieve_members_input_vars.xlsx")
groupedInputs = inputsDf.groupby("wikiproject")

for name, group in groupedInputs:
    projectId = projectIdLookup[name]
    rootDirForUserLists = os.path.join(projectRootDir, "user_lists", "new_way")
    if not os.path.exists(os.path.join(rootDirForUserLists, str(projectId) + ".csv")):
        extract_users(group, projectRootDir, str(projectId))
    else:
        print(name + " already has a members list csv.")
    
statsCsv.close()


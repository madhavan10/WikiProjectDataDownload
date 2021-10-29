# -*- coding: utf-8 -*-
"""
Created on Sat Oct  2 11:05:12 2021

@author: madha
"""

import requests
import re
import os
import csv
import sys
import pandas as pd
from selenium import webdriver
from datetime import date

def get_properties_from_file(filename):
    properties = dict()
    with open(filename) as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
    return properties

def get_contribs_to_file(user, textOutputPath):      
    if os.path.exists(textOutputPath):
        print("File already exists for this User.")
        return
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
            "action": "query",
            "list": "usercontribs",
            "ucuser": user,
            "ucprop": "timestamp|title",
            "ucdir": "newer",
            "uclimit": "max",
            "ucnamespace": "4", 
            "format": "xml"        
        }
    print(user)
    i = 0
    while True:
        revisions = []
        R = S.get(url = URL, params = PARAMS)
        i += 1
        revisions += re.findall('<item [^>]*>', R.text)
        try:
            os.makedirs(textOutputPath.rsplit(os.sep, maxsplit = 1)[0])
            print("Creating necessary directories for user contributions")
        except FileExistsError:
            pass
        with open(textOutputPath, "a", newline="", encoding = "utf-8") as ofile:
            for rev in revisions:
                ofile.write(rev)
                ofile.write("\n")
        cont = re.search('<continue uccontinue="([^"]+)"', R.text)
        if not cont:
            break
        next = cont.group(1)
        PARAMS["uccontinue"] = next
        # print(next)
    print(i)
    return

def find_join_dates(textFile, joinDatesCSV, user, projectName):
    regex = '<item userid="[^"]*" user="[^"]*" ns="4" title="Wikipedia:WikiProject ('\
        + projectName + '|' + projectName + '[^"]*(members?|participants?)[^"]*)"'\
        + ' timestamp="([^"]*)"'
    with open(textFile, "r", encoding = "utf-8") as userContribsF:
        lineNo = 0
        for line in userContribsF:
            lineNo += 1
            match = re.search(regex, line, flags = re.IGNORECASE)
            if match:
                try:
                    os.makedirs(joinDatesCSV.rsplit(os.sep, maxsplit = 1)[0])
                    print("Creating necessary directories (project join)")
                except FileExistsError:
                    pass
                with open(joinDatesCSV, "a", newline = "", encoding = "utf-8") as csvF:
                    csvWriter = csv.writer(csvF, quoting = csv.QUOTE_MINIMAL)
                    csvWriter.writerow([user, projectName, match.group(3), lineNo])
                    return True
        return False

try:
    properties = get_properties_from_file(sys.argv[1])
except IndexError:
    raise Exception("Specify a properties file as an argument to this script.")

projectRootDir = properties["projectRootDir"]
projectFilename = properties["projectFilename"]
chromeDriverPath = properties["chromeDriver"]
joinDatesCSV = os.path.join(projectRootDir, "project_join", projectFilename, "way2.csv")
if os.path.exists(joinDatesCSV):
    os.remove(joinDatesCSV)
with open(joinDatesCSV, "w", newline = "", encoding = "utf-8") as f:
    fWriter = csv.writer(f, quoting = csv.QUOTE_MINIMAL)
    fWriter.writerow(["user", "Project Name", "Join Date", "Line number in contributions file"])

projectName = properties["projectName"]
statsPath = os.path.join(projectRootDir, "stats.csv")

userListDf = pd.read_csv(os.path.join(projectRootDir, "user_lists", projectFilename + ".csv"), encoding = "utf-8")
userIdLookupPath = os.path.join(projectRootDir, "user_contributions", projectFilename, "user_id_lookup.csv")

if not os.path.exists(userIdLookupPath):
    users = []
    user_ids = []
    for i in userListDf.index:
        users.append(userListDf["member"][i])
        user_ids.append(i)
    newLookupDf = pd.DataFrame({"user": users, "lookup_id": user_ids})
    try:
        os.makedirs(userIdLookupPath.rsplit(os.sep, maxsplit = 1)[0])
        print("Creating necessary directories (contributions)")
    except FileExistsError:
        pass
    newLookupDf.to_csv(userIdLookupPath, index = False, encoding = "utf-8")

userIdLookupDf = pd.read_csv(userIdLookupPath, encoding = "utf-8")
userIdLookup = {}
for i in userIdLookupDf.index:
    username = userIdLookupDf["user"][i]
    username = username[0].upper() + username[1:] if len(username) > 1 else username.upper()
    userIdLookup[username] = userIdLookupDf["lookup_id"][i]

count = 0
for user in userIdLookup.keys():
    textOutputPath = os.path.join(projectRootDir, "user_contributions", projectFilename, str(userIdLookup[user]) + ".txt")
    get_contribs_to_file(user, textOutputPath)
    if os.path.getsize(textOutputPath) == 0:
        # check for changed username
        driver = webdriver.Chrome(executable_path = chromeDriverPath)
        driver.get("https://en.wikipedia.org/wiki/User:" + user)
        usernameMatch = re.search('User:(.*) - Wikipedia', driver.title)
        userNormalized = user[0].upper() + user[1:]
        if usernameMatch and usernameMatch.group(1) != userNormalized:
            driver.close()
            os.remove(textOutputPath)
            get_contribs_to_file(usernameMatch.group(1), textOutputPath)
            
    if find_join_dates(textOutputPath, joinDatesCSV, user, projectName):
        count += 1

membersWithNoDOJ = len(userIdLookup) - count
with open(statsPath, "a", newline = "", encoding = "utf-8") as statsCsv:
    writer = csv.writer(statsCsv, quoting = csv.QUOTE_MINIMAL)
    writer.writerow([date.today(), projectName, "", len(userIdLookup), "",\
                    membersWithNoDOJ, round(membersWithNoDOJ * 100 / len(userIdLookup), 2)])


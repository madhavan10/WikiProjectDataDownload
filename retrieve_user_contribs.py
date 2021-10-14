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
                    break
try:
    properties = get_properties_from_file(sys.argv[1])
except IndexError:
    raise Exception("Specify a properties file as an argument to this script.")

projectRootDir = os.path.abspath(properties["projectRootDir"])
projectFilename = properties["projectFilename"]
joinDatesCSV = os.path.join(projectRootDir, "project_join", projectFilename, "way2.csv")
projectName = properties["projectName"]

userListDf = pd.read_csv(os.path.join(projectRootDir, "user_lists", projectFilename + ".csv"), encoding = "utf-8")
userIdLookupPath = os.path.join(projectRootDir, "user_contributions", projectFilename, "user_id_lookup.csv")

if not os.path.exists(userIdLookupPath):
    users = []
    user_ids = []
    for i in userListDf.index:
        users.append(userListDf["member"][i])
        user_ids.append(i)
    newLookupDf = pd.DataFrame({"user": users, "lookup_id": user_ids})
    newLookupDf.to_csv(userIdLookupPath, index = False, encoding = "utf-8")

userIdLookupDf = pd.read_csv(userIdLookupPath, encoding = "utf-8")
userIdLookup = {}
for i in userIdLookupDf.index:
    userIdLookup[userIdLookupDf["user"][i]] = userIdLookupDf["lookup_id"][i]

for user in userIdLookup.keys():
    textOutputPath = os.path.join(projectRootDir, "user_contributions", projectFilename, str(userIdLookup[user]) + ".txt")
    get_contribs_to_file(user, textOutputPath)
    find_join_dates(textOutputPath, joinDatesCSV, user, projectName)

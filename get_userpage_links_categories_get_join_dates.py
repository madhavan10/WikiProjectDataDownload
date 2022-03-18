# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 22:28:52 2022

@author: madha
"""

from selenium.webdriver.common.by import By
from selenium import webdriver
from collections import OrderedDict
import requests
import re
import pandas as pd
import csv
import os

def return_timestamp(a):
    return a[1]

chromeDriverPath = "C:/users/madha/chromedriver.exe"
driver = webdriver.Chrome(executable_path = chromeDriverPath)

lookupDf = pd.read_csv("C:/users/madha/documents/wikiproject/userboxProjectLookup.csv")
lookup = {}
for i in lookupDf.index:
    lookup[lookupDf["project"][i]] = lookupDf["id"][i]

userboxInputVarsPath = "C:/users/madha/dropbox/wikiproject_data_download/wikiproject_userboxes.xlsx"
userboxInputsDf = pd.read_excel(userboxInputVarsPath)
groupedInputs = userboxInputsDf.groupby("Project")

statsPath = "C:/users/madha/documents/wikiproject/user_lists/userbox_joindates_stats.csv"
statsPathExists = os.path.exists(statsPath)
with open(statsPath, "a", newline = "", encoding = "utf-8") as statsCsv:
    statsWriter = csv.writer(statsCsv, quoting = csv.QUOTE_MINIMAL)
    if not statsPathExists:
        statsWriter.writerow(["project", "numberOfUsers", "numberFailed"])
    for project, group in groupedInputs:
        print(project)
        outputPath = "C:/users/madha/documents/wikiproject/user_lists/userbox_projects/" + str(lookup[project]) + ".csv"
        failedPath = "C:/users/madha/documents/wikiproject/user_lists/userbox_projects/failed/" + str(lookup[project]) + ".csv"
        # load saved state from previous iteration
        alreadyDone = set()
        alreadyFailed = set()
        if os.path.exists(outputPath):
            doneDf = pd.read_csv(outputPath, encoding = "utf-8")
            for doneUser in doneDf["user"]:
                alreadyDone.add(doneUser)
        if os.path.exists(failedPath):
            alreadyFailedDf = pd.read_csv(failedPath, encoding = "utf-8")
            for failedUser in alreadyFailedDf["user"]:
                alreadyFailed.add(failedUser)
        with open(outputPath, "a", newline = "", encoding = "utf-8") as outputCsv:
            writer = csv.writer(outputCsv, quoting = csv.QUOTE_MINIMAL)
            if os.path.getsize(outputPath) == 0:
                writer.writerow(["user", "join-date", "project", "matchedText", "matchedPage", "type"])
                    
            group.reset_index(drop = True, inplace = True)
            categoryPage = "https://en.wikipedia.org/wiki/" + group["Page"][0]
            if pd.notna(group["type"][0]):
                projectType = group["type"][0]
            else:
                projectType = "s"
            driver.get(categoryPage)
            users = OrderedDict()
            
            # get names of all pages with userbox
            cont = True
            while(cont):
                links = driver.find_elements(By.TAG_NAME, "a")
                cont = False
                contLink = None
                for link in links:
                    if link.text == "next page":
                        contLink = link
                        cont = True
                    if link.text.startswith("User:"):
                        username = link.text[5:].split("/", maxsplit = 1)[0]
                        if username not in users.keys():
                            users[username] = []
                        users[username].append(link.text)
                if contLink:
                    contLink.click()
                
            S = requests.Session()
            URL = "https://en.wikipedia.org/w/api.php"
            with open(failedPath, "a", newline = "", encoding = "utf-8") as failedCsv:
                failedWriter = csv.writer(failedCsv, quoting = csv.QUOTE_MINIMAL)
                if os.path.getsize(failedPath) == 0:
                    failedWriter.writerow(["user", "project"])
                numberFailed = len(alreadyFailed)
                for user, pages in users.items():
                    if user in alreadyDone or user in alreadyFailed:
                        continue
                    PARAMS = {
                        "action": "query",
                        "prop": "revisions",
                        "rvprop": "content|timestamp",
                        "rvdir": "newer",
                        "rvlimit": "max",
                        "rvslots": "main",
                        "format":"json",
                        "formatversion": "2"
                    }
                    
                    matchFound = False
                    matches = []
                    for page in pages:
                        print(page)
                        PARAMS["titles"] = page
                        PARAMS.pop("rvcontinue", None)
                        # get revision history of page
                        while(True):
                            R = S.get(url = URL, params = PARAMS)
                            json = R.json()
                            revs = json["query"]["pages"][0]["revisions"]
                            # search revisions for appearance of regex
                            for rev in revs:
                                timestamp = rev["timestamp"]
                                # content could be revision-deleted
                                if "content" in rev["slots"]["main"].keys():
                                    content = rev["slots"]["main"]["content"]
                                else:
                                    continue
                                for regex in group["Regex"]:
                                    match = re.search(regex, content, flags = re.IGNORECASE)
                                    if match:
                                        matches.append([user, timestamp, project, match.group(0), page, projectType])
                                        matchFound = True
                                        break
                                if matchFound:
                                    break
                            if matchFound:
                                break
                            if "continue" in json.keys() and "rvcontinue" in json["continue"].keys():
                                PARAMS["rvcontinue"] = json["continue"]["rvcontinue"]
                            else:
                                break
                    if len(matches) > 0:        
                        earliestMatch = min(matches, key = return_timestamp)
                        writer.writerow(earliestMatch)
                    else:
                        failedWriter.writerow([user, project])
                        numberFailed += 1
        statsWriter.writerow([project, len(users), numberFailed])
                    
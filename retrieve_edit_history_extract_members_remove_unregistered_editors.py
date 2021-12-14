# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 21:33:41 2021

@author: madha
"""

import requests
import re
from collections import OrderedDict
import pandas as pd
import os
import sys
import csv
from datetime import date

def get_properties_from_file(filename):
    properties = dict()
    with open(filename) as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
    return properties

def concat_no_duplicates(dfs, outputPath):

    df = pd.concat(dfs, ignore_index = True)
    try:
        os.makedirs(outputPath.rsplit(os.sep, maxsplit = 1)[0])
        print("Creating necessary directories..")
    except:
        pass
    # debug
    df.to_csv(os.path.join(outputPath.rsplit(os.sep, maxsplit = 1)[0], "debug.csv"), index = False, encoding = "utf-8")
    df.sort_values("firstEdit", ignore_index = True, inplace = True)
    setOfUsers = set()
    toDrop = []
    for i in df.index:
        if df["userid"][i] not in setOfUsers:
            setOfUsers.add(df["userid"][i])
        else:
            toDrop.append(i)
    
    df.drop(index = toDrop, inplace = True)
    df.to_csv(outputPath, index = False, encoding = "utf-8")
    return

def retrieve_revisions_build_dfs(inputsPath, projectRootDir, projectName, projectFilename):
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
            "action": "query",
            "prop": "revisions",
            "titles": "",
            "rvprop": "timestamp|user|userid|comment",
            "rvslots": "main",
            "rvlimit": "500",
            #"rvend": "",
            "rvdir": "newer",
            "format": "xml"        
        }
    
    inputsDf = pd.read_excel(inputsPath)
    inputsDf = inputsDf[inputsDf["wikiproject"] == projectName].reset_index(drop = True)

    csvOutputPath = os.path.join(projectRootDir, "project_join", projectFilename, inputsDf["csvOutputPath"][0])
    
    dfs = []
    
    for i in inputsDf.index:
        PARAMS["titles"] = inputsDf["page"][i]
        try:
            del PARAMS["rvcontinue"]
        except KeyError:
            pass      
        
        revisions = []
        # get revisions
        while True:
            R = S.get(url = URL, params = PARAMS)
            revisions += re.findall('<rev [^>]*>', R.text)
            cont = re.search('<continue rvcontinue="([^"]+)"', R.text)
            if not cont:
                break
            next = cont.group(1)
            PARAMS["rvcontinue"] = next
            print(PARAMS["titles"], next)
            
        usernamesById = OrderedDict()
        joindateByUserId = OrderedDict()
        commentByUserId = OrderedDict()
        sourcePage = []
        for elt in revisions:
            match = re.search('user="([^"]*)" userid="([^"]*)" timestamp="([^"]*)" comment="([^"]*)" [^>]*>', elt)
            if match:
                if re.search('[bB][oO][tT]$', match.group(1)):
                    continue
                if match.group(2) not in usernamesById:
                    usernamesById[match.group(2)] = match.group(1)
                if match.group(2) not in joindateByUserId:
                    joindateByUserId[match.group(2)] = match.group(3)
                if match.group(2) not in commentByUserId:
                    commentByUserId[match.group(2)] = match.group(4)
                    sourcePage.append(PARAMS["titles"])
                
        df = pd.DataFrame({"userid": list(usernamesById.keys()), "user": list(usernamesById.values()),\
                           "firstEdit": list(joindateByUserId.values()), "comment": list(commentByUserId.values()),\
                               "page": sourcePage})
        dfs.append(df)
    
    concat_no_duplicates(dfs, csvOutputPath)
    return

def get_text_without_comments_extract_users(inputsPath, projectRootDir, projectName, projectFilename):
    inputsDf = pd.read_excel(inputsPath)
    inputsDf = inputsDf[inputsDf["wikiproject"] == projectName].reset_index(drop = True)
    
    membersListOutputPath = os.path.join(projectRootDir, "user_lists", projectFilename + ".csv")
    
    S = requests.Session()
    
    URL = "https://en.wikipedia.org/w/api.php"
    
    users = OrderedDict()
    
    for i in inputsDf.index:
    
        page = inputsDf["page"][i]
        userRegex = inputsDf["regex"][i]
        
        PARAMS = {
                "action": "query",
                "prop": "revisions",
                "titles": page,
                "rvprop": "timestamp|content",
                "rvslots": "main",
                "rvlimit": "1",
                #"rvdir": "newer",
                #"rvend": rvend,
                "format": "xml"        
            }
        
        R = S.get(url = URL, params = PARAMS)
        htmlCommentsRegex = '&lt;!--([^-]|-[^-]|--[^&\s]|--\s*&[^g]|--\s*&g[^t]|--\s*gt[^;])*--\s*&gt;'
        text = re.sub(htmlCommentsRegex, "", R.text)
        foundUsers = re.findall(userRegex, text, flags = re.IGNORECASE)
        for user in foundUsers:
            user = user[0].upper() + user[1:] if len(user) > 1 else user.upper()
            # strip trailing whitespace from username
            user = user.rstrip()
            users[user] = page
            
    outputsDf = pd.DataFrame({"member": users.keys(), "source": users.values()})
    outputsDf.to_csv(membersListOutputPath, index = False, encoding = "utf-8")
    return

def decapitalize_set(s):
    result = set()
    for elt in s:
        lowered = elt[0].lower() + elt[1:] if len(elt) > 1 else elt.lower()
        if lowered not in result:
            result.add(lowered)
    return result

def remove_unregistered_users(retrieveEditorsInputsPath, retrieveMembersInputsPath, projectRootDir, projectName, projectFilename):
    editorsInputsDf = pd.read_excel(retrieveEditorsInputsPath)
    editorsInputsDf = editorsInputsDf[editorsInputsDf["wikiproject"] == projectName].reset_index(drop = True)
    membersInputsDf = pd.read_excel(retrieveMembersInputsPath)
    membersInputsDf = membersInputsDf[membersInputsDf["wikiproject"] == projectName].reset_index(drop = True)
    
    editorsPath = os.path.join(projectRootDir, "project_join", projectFilename, editorsInputsDf["csvOutputPath"][0])
    membersPath = os.path.join(projectRootDir, "user_lists", projectFilename + ".csv")
    outputCsvPath = os.path.join(editorsPath.rsplit(os.sep, maxsplit = 1)[0], "final.csv")
    
    membersDf = pd.read_csv(membersPath, encoding = "utf-8")    
    editorsDf = pd.read_csv(editorsPath, encoding = "utf-8")
    lowerSetMembers = decapitalize_set(set(membersDf["member"]))
    
    toDrop = []
    for i in editorsDf.index:
        editor = editorsDf["user"][i]
        decapitalized_editor = editor[0].lower() + editor[1:] if len(editor) > 1 else editor.lower()
        if decapitalized_editor not in lowerSetMembers:
            toDrop.append(i)
    
    finalDf = editorsDf.drop(index = toDrop)
    finalDf.to_csv(outputCsvPath, index = False, encoding = "utf-8")        
    
    statsPath = os.path.join(projectRootDir, "stats.csv")
    NumberOfMembersNotInEditHistory = len(lowerSetMembers) - (len(editorsDf) - len(toDrop))
    with open(statsPath, "a", newline = "", encoding = "utf-8") as statsCsv:
        csvWriter = csv.writer(statsCsv, quoting = csv.QUOTE_MINIMAL)
        csvWriter.writerow([date.today(), projectName, len(editorsDf), len(lowerSetMembers), len(toDrop),\
                            NumberOfMembersNotInEditHistory, round(NumberOfMembersNotInEditHistory * 100 / len(lowerSetMembers), 2)])
    
try:
    properties = get_properties_from_file(sys.argv[1])
except IndexError:
    raise Exception("Specify a properties file as an argument to this script.")
    
retrieveEditorsInputsPath = properties["retrieveEditorsInputsPath"]
retrieveMembersInputsPath = properties["retrieveMembersInputsPath"]
projectRootDir = properties["projectRootDir"]
projectName = properties["projectName"]
projectFilename = properties["projectFilename"]

retrieve_revisions_build_dfs(retrieveEditorsInputsPath, projectRootDir, projectName, projectFilename)
get_text_without_comments_extract_users(retrieveMembersInputsPath, projectRootDir, projectName, projectFilename)
remove_unregistered_users(retrieveEditorsInputsPath, retrieveMembersInputsPath, projectRootDir, projectName, projectFilename)

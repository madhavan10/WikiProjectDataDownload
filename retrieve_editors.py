# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 21:58:36 2021

@author: madha
"""

import requests
import re
from collections import OrderedDict
import pandas as pd
import os
import sys

def get_properties_from_file(filename):
    properties = dict()
    with open(filename) as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
    return properties

try:
    properties = get_properties_from_file(sys.argv[1])
except IndexError:
    raise Exception("Specify a properties file as an argument to this script.")

inputsPath = os.path.abspath(properties["retrieveEditorsInputsPath"])
projectRootDir = os.path.abspath(properties["projectRootDir"])
projectName = properties["projectName"]

inputsDf = pd.read_excel(inputsPath)
inputsDf = inputsDf[inputsDf["wikiproject"] == projectName].reset_index(drop = True)

csvOutputPath = os.path.abspath(inputsDf["csvOutputPath"][0])

def retrieve_revisions_build_dfs(inputsPath, projectRootDir, projectName):
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

def concat_no_duplicates(dfs, outputPath):

    df = pd.concat(dfs, ignore_index = True)
    # debug
    df.to_csv(os.path.join(csvOutputPath.rsplit(os.sep, maxsplit = 1)[0], "debug.csv"), index = False, encoding = "utf-8")
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

retrieve_revisions_build_dfs(inputsPath, projectRootDir, projectName)
  

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

inputsPath = "C:/users/madha/documents/wikiproject/retrieve_edit_history_input_vars.xlsx"
projectRootDir = "C:/users/madha/documents/wikiproject"
projectRootDir = os.path.abspath(projectRootDir)
projectName = "Military History"

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
        
    inputsDf = pd.read_excel(inputsPath)
    inputsDf = inputsDf[inputsDf["wikiproject"] == projectName]
    
    csvOutputPath = os.path.abspath(inputsDf["csvOutputPath"][0])
    csvOutputPath = os.path.join(csvOutputPath.rsplit(os.sep, maxsplit = 1)[0], "final.csv") 
    
    dfs = []
    
    for i in inputsDf.index:
        PARAMS["titles"] = inputsDf["page"][i]
        try:
            del PARAMS["rvcontinue"]
        except KeyError:
            pass      
        lastTwoVarsInPath = csvOutputPath.rsplit(os.sep, maxsplit = 2)
        revisionsOutputPath = os.path.join(projectRootDir, "revisions", lastTwoVarsInPath[-2], lastTwoVarsInPath[-1].split(".")[-2] + ".txt")
        
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
        sourcePage = []
        for elt in revisions:
            match = re.search('user="([^"]*)" userid="([^"]*)" timestamp="([^"]*)" [^>]*>', elt)
            if match:
                if re.search('[bB][oO][tT]$', match.group(1)):
                    continue
                if match.group(2) not in usernamesById:
                    usernamesById[match.group(2)] = match.group(1)
                if match.group(2) not in joindateByUserId:
                    joindateByUserId[match.group(2)] = match.group(3)
                    sourcePage.append(PARAMS["titles"])
                
        df = pd.DataFrame({"userid": list(usernamesById.keys()), "user": list(usernamesById.values()),\
                           "firstEdit": list(joindateByUserId.values()), "page": sourcePage})
        dfs.append(df)
        # df.to_csv(csvOutputPath, index = False, encoding = "utf-8")
          
        with open(revisionsOutputPath, "w", newline="", encoding = "utf-8") as ofile:
            for elt in revisions:
                ofile.write(elt)
                ofile.write("\n")
    
    concat_no_duplicates(dfs, csvOutputPath)
    return

def concat_no_duplicates(dfs, outputPath):

    df = pd.concat(dfs, ignore_index = True)
    df.sort_values("firstEdit", ignore_index = True, inplace = True)
    # debug
    df.to_csv("C:/users/madha/documents/wikiproject/mil_hist_df_b4_sort.csv", index = False, encoding = "utf-8")
    setOfUsers = set()
    toDrop = []
    for i in df.index:
        if df["userid"][i] not in setOfUsers:
            setOfUsers.add(df["userid"][i])
        else:
            toDrop.append(i)
    
    print(toDrop)
    
    df.drop(index = toDrop, inplace = True)
    df.to_csv(outputPath, index = False, encoding = "utf-8")
    return

retrieve_revisions_build_dfs(inputsPath, projectRootDir, projectName)
  

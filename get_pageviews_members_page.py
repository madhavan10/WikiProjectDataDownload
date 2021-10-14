# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 18:03:04 2021

@author: madha
"""

import requests
import pandas as pd

wikiProjectsCsv = "C:/users/madha/documents/wikiproject/wikiprojectsViews1.csv"

def get_pageviews(projectName, startDateStr, endDateStr, isTalk):
    
    def get_project_name_url_version(name):
        result = name.replace(" ", "_")
        result = result.replace("/", "%2F")
        result = result.replace("'", "%27")
        result = result.replace("&", "%26")
        result = result.replace("amp;", "")
        return result
        
    S = requests.Session()
    
    if not isTalk:
        projectName = get_project_name_url_version(projectName)
    else:
        projectName = "Wikipedia_talk:WikiProject_" + get_project_name_url_version(projectName)
    
    URL_first_part = "https://wikimedia.org/api/rest_v1/metrics/edits/per-page/en.wikipedia/"
    URL = URL_first_part + projectName + "/user/monthly/" + startDateStr + "/"  + endDateStr
    
    headers = {"user-agent": "madhavansomanathan@gmail.com"}
    
    R = S.get(URL, headers = headers)
    
    if R.json().get("items", -1) == -1:
        return -1
    
    sum = 0
    for item in R.json()["items"]:
        sum += int(item["views"])
        
    print(projectName, sum)
    return sum

    
df = pd.read_csv(wikiProjectsCsv, encoding = "utf-8")
projectsList = list(df["Members page"])

pageviews = []

for project in projectsList:
    if pd.isna(project):
        pageviews.append(-1)
        continue
    views = get_pageviews(project, "20201001", "20211002", isTalk = False)
    pageviews.append(views)

df["Members page views"] = pageviews
df.to_csv(wikiProjectsCsv, index = False, encoding = "utf-8")    
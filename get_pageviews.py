# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 18:51:39 2021

@author: madha
"""

import requests
import pandas as pd

wikiProjectsCsv = "C:/users/madha/documents/wikiproject/wikiprojects_watchers_list.csv"

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
        projectName = "Wikipedia:WikiProject_" + get_project_name_url_version(projectName)
    else:
        projectName = "Wikipedia_talk:WikiProject_" + get_project_name_url_version(projectName)
    
    URL_first_part = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
    URL = URL_first_part + projectName + "/monthly/" + startDateStr + "/"  + endDateStr
    
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
projectsList = list(df["Project Name"])

pageviews = []

for project in projectsList:
    views = get_pageviews(project, "20201001", "20211002", isTalk = False)
    views += get_pageviews(project, "20201001", "20211002", isTalk = True)
    pageviews.append(views)

df["Views of Main page or Talk page"] = pageviews
df.to_csv(wikiProjectsCsv, index = False, encoding = "utf-8")    
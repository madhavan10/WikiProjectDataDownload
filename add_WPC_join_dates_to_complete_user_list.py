# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 19:47:34 2022

@author: madha
"""

import pandas as pd
completeUserListPath = r"C:\Users\madha\Documents\WikiProject\user_lists\complete_user_list_with_ubx_projects.csv"
wikiProjectCardsJoinDatesPath = r"C:\Users\madha\Documents\WikiProject\user_lists\wikiProjectCardsJoinDates.csv"
wikiProjectCardsLookup = r"C:\Users\madha\Documents\WikiProject\WikiProjectCardsLookup.csv"
wikiProjectCardsProjects = set(pd.read_csv(wikiProjectCardsLookup, encoding = "utf-8")["project"])

mainDf = pd.read_csv(completeUserListPath, encoding = "utf-8")
wpcJdDf = pd.read_csv(wikiProjectCardsJoinDatesPath, encoding = "utf-8")
toDrop = []
for i in mainDf.index:
    if mainDf["project"][i] in wikiProjectCardsProjects:
        toDrop.append(i)

mainDf.drop(index = toDrop, inplace = True)

wpcJdDf["membership"] = "list"

mainDf = pd.concat([mainDf, wpcJdDf], ignore_index = True)

mainDf.to_csv(r"C:\users\madha\documents\wikiproject\user_lists\complete_user_list_with_ubx_wpc.csv", index = False, encoding = "utf-8")




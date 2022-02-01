# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 12:53:16 2022

@author: madha
"""

from utils import getRecentUsername
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
from collections import OrderedDict
import csv
import sys
import traceback

chromeDriverPath = "/home/madhavso/chromedriver"
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path = chromeDriverPath, options = chrome_options)

# login to Wikipedia
driver.get("https://en.wikipedia.org/w/index.php?title=Special:UserLogin")
usernameBox = driver.find_element(By.NAME, "wpName")
usernameBox.send_keys("Msomanat")
passwordBox = driver.find_element(By.NAME, "wpPassword")
passwordBox.send_keys("p1tm0qpgu" + Keys.ENTER)

lookupPath = "/home/madhavso/wikipedia_data/user_lists/1-10000_union_lookup.csv"
lookupDf = pd.read_csv(lookupPath, encoding = "utf-8")
lookupIdToName = {}
for i in lookupDf.index:
    lookupIdToName[lookupDf["userNumber"][i]] = lookupDf["user"][i]
        
root_dir = "/home/madhavso/wikipedia_data/top_editors/contributions"
os.chdir(root_dir)

usernamesMap = OrderedDict()
usernamesMapPath = "/home/madhavso/wikipedia_data/user_lists/usernamesMapTopEditors.csv"
usernamesMapPathExists = os.path.exists(usernamesMapPath)
failedQueriesPath = "/home/madhavso/wikipedia_data/user_lists/failedQueriesTopEditors.txt"

with open(usernamesMapPath, "a", newline = "", encoding = "utf-8") as usernamesMapCsv:
    writer = csv.writer(usernamesMapCsv, quoting = csv.QUOTE_MINIMAL)
    if not usernamesMapPathExists:
        writer.writerow(["username", "mostRecentUsername"])
    else:
        usernamesMapDf = pd.read_csv(usernamesMapPath, encoding = "utf-8")
        for i in usernamesMapDf.index:
            usernamesMap[usernamesMapDf["username"][i]] = usernamesMapDf["mostRecentUsername"][i]
    
    with open(failedQueriesPath, "w", newline="", encoding = "utf-8") as failedQueriesLog:        
        i = 0
        for file in os.listdir():
            split = file.rsplit(".", maxsplit = 1)
            if split[-1] != "csv":
                continue
            i += 1
            username = lookupIdToName[int(split[0])]
            if username in usernamesMap.keys():
                continue
            try:
                mostRecentUsername = getRecentUsername(username, driver)
            except KeyboardInterrupt:
                print("Stopped execution on ", file, username)
                raise
            except:
                failedQueriesLog.write(split[0] + "\n")
                failedQueriesLog.write(username + "\n")
                traceback.print_tb(sys.exc_info()[2], file = failedQueriesLog)
                continue
            usernamesMap[username] = mostRecentUsername
            writer.writerow([username, mostRecentUsername])
            print(i, split[0], username, mostRecentUsername, sep = " : ")



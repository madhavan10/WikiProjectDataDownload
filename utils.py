# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 14:04:12 2022

@author: madha
"""

import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import csv
import os

class UnexpectedFormatException(Exception):
    pass

def getRecentUsername(username, driver):
    
    def queryRecentUsername(username, driver):
    
        def strip_and_upper(s):
            s = s.strip()
            s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()
            return s

        driver.get("https://en.wikipedia.org/wiki/User:" + username)
        usernameMatch = re.search('[Uu]ser\s*:\s*(.*) - Wikipedia', driver.title)
        if not usernameMatch:
            # look for redirect to talk-page
            usernameMatch = re.search('[Uu]ser talk\s*:\s*(.*) - Wikipedia', driver.title)
            if not usernameMatch:
                return None
            else:
                return strip_and_upper(usernameMatch.group(1))
        elif usernameMatch.group(1) != username:
            # redirected to different user page
            return strip_and_upper(usernameMatch.group(1))
        else:
            try:
                userdoesnotexist_line = driver.find_element(By.CLASS_NAME, "mw-userpage-userdoesnotexist")
            except NoSuchElementException:
                userdoesnotexist_line = None
            try:
                move_line = driver.find_element(By.CLASS_NAME, "mw-logline-move")
            except NoSuchElementException:
                move_line = None
            try:
                rename_line = driver.find_element(By.CLASS_NAME, "mw-logline-renameuser")
            except NoSuchElementException:
                rename_line = None
            if not userdoesnotexist_line and not move_line and not rename_line:
                # should be a valid userpage
                return username
            elif rename_line:
                username_list = rename_line.find_elements(By.TAG_NAME, "a")
                if len(username_list) >= 6:
                    return username_list[5].text
                else:
                    raise UnexpectedFormatException("Unexpected format: rename line")
            elif move_line:
                username_list = move_line.find_elements(By.TAG_NAME, "a")
                if len(username_list) >= 6:
                    new_userpage_title = username_list[5].text
                    if new_userpage_title.startswith("User:"):
                        return new_userpage_title[5:]
                    else:
                        raise UnexpectedFormatException("Unexpected format: move line: new userpage title")
                else:
                    raise UnexpectedFormatException("Unexpected format: move line")
            else:
                return None
            
    recentUsername = queryRecentUsername(username, driver)
    oldUsername = username
    allNames = []
    while recentUsername != None and recentUsername != oldUsername:
        allNames.append(oldUsername)
        oldUsername = recentUsername
        recentUsername = queryRecentUsername(recentUsername, driver)
        if recentUsername in allNames:
            #infinite loop
            break
    return recentUsername

def merge(ifilename1, ifilename2, ofilename):
    USERNAME_INDEX = 0
    USERID_INDEX = 1
    TIMESTAMP_INDEX = 2
    
    # get username and userid from file 2
    with open(ifilename2, "r", newline = "", encoding = "utf-8") as tempFile2:
        tempReader = csv.reader(tempFile2)
        next(tempReader)
        tempRow = next(tempReader)
        username = tempRow[USERNAME_INDEX]
        userid = tempRow[USERID_INDEX]
        
    secondMerge = (ifilename2 == ofilename) # merging file 1 with the result of a previous merge
    if secondMerge:
        ofilename = ofilename.rsplit(".", maxsplit = 1)[0] + "_tmp.csv"
    with open(ifilename1, "r", newline = "", encoding = "utf-8") as file1:
        reader1 = csv.reader(file1)
        next(reader1) # skip header
        with open(ifilename2, "r", newline = "", encoding = "utf-8") as file2:
            reader2 = csv.reader(file2)
            header = next(reader2) # skip reader
            with open(ofilename, "w", newline = "", encoding = "utf-8") as ofile:
                writer = csv.writer(ofile, quoting = csv.QUOTE_MINIMAL)
                writer.writerow(header)
                eof1 = False
                eof2 = False
                getNext1 = True # determines whether to move to next row of file1
                getNext2 = True # same as above for file2
                while not eof1 and not eof2:
                    if getNext1:
                        try:
                            row1 = next(reader1)
                            # switch content of user, userid columns to match file 2
                            row1[USERNAME_INDEX] = username
                            row1[USERID_INDEX] = userid
                        except StopIteration:
                            eof1 = True
                            row1 = None
                    if getNext2:
                        try:
                            row2 = next(reader2)
                        except StopIteration:
                            eof2 = True
                            row2 = None
                    if row1 == None and row2 == None:
                        # loop will exit
                        continue
                    elif row1 == None:
                        # write one last row before exiting loop
                        writer.writerow(row2)
                    elif row2 == None:
                        # same as above
                        writer.writerow(row1)
                    else:
                        if row1[TIMESTAMP_INDEX] <= row2[TIMESTAMP_INDEX]:
                            writer.writerow(row1)
                            getNext1 = True
                            getNext2 = False
                        else:
                            writer.writerow(row2)
                            getNext2 = True
                            getNext1 = False
                if not eof1:
                    for row in reader1:
                        # switch content of user, userid columns to match file 2
                        row[USERNAME_INDEX] = username
                        row[USERID_INDEX] = userid
                        writer.writerow(row)
                if not eof2:
                    for row in reader2:
                        writer.writerow(row)
    if secondMerge:
        # replace merged file from previous merge with file from this merge
        os.rename(ofilename, ifilename2)
    return
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 21:52:03 2021

@author: madha

AFAIK this script only works when run from the Spyder IDE
"""
propertiesPath = 'C:/users/madha/documents/wikiproject/code/properties.txt'

runfile('C:/users/madha/documents/wikiproject/code/retrieve_editors.py', args=propertiesPath)
runfile('C:/users/madha/documents/wikiproject/code/get_text_without_comments_extract_users.py', args=propertiesPath)
runfile('C:/users/madha/documents/wikiproject/code/remove_unregistered_editors.py', args=propertiesPath)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 19:08:49 2021

@author: blitt
"""

#import sqlite3
import pandas as pd
#from sqlite3 import Error
import sys

#connect = sqlite3.connect('/home/blitt/Academic/Research/practiceDatabase/nrToUniDB.db')

nrToUniDf = pd.read_csv(sys.argv[1], "\t")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 14:01:36 2021

@author: blitt
"""

import sys
import os 
import shutil 
import gc 
import psutil 

#this is the file containing cross references from nr to uniprot
refFile = sys.argv[1]

#this is the directory that our (raw) blast output is stored in 
originalOutputDir = sys.argv[2]

#this is the new directory that will hold the same output but with cross referenced ids instead of nr (if we have them)
newOutputDir = sys.argv[3]

#initialize output dict such that the keys are the filenames in our blast output folder 
outputDict = {}
for fileName in os.listdir(originalOutputDir):
    
    filePath = originalOutputDir.rstrip("/") + "/" + fileName
    file = open(filePath)
    
    #we want all of the lines to be false at first for this file (later to be filled with output values)
    outputDict[fileName] = [False for line in file]

crossRefDict = {}
lineCounter = 0 
for line in open(refFile): 
    lineList = line.split("\t")
    
    #uniprot accession ID 
    uniAcc = lineList[0]

    fromID = lineList[2].strip("\n")
    
    for filename in os.listdir(originalOutputDir): 
        #account for fact that the inDir could have trialing slash or not
        filePath = originalOutputDir.rstrip("/") + "/" + fileName
        file = open(filePath, "r")
        
        i = 0
        for line in file: 
            currOutLine = outputDict[fileName][i]
            
            if currOutLine == False: 
                currNR = line.strip("\n").split("\t")[1]
                
                if currNR in fromID: 
                    outputDict[fileName][i] = line.split("\t")[0] + "\t" + uniAcc + "\t" + "\t".join(line.strip("\n").split("\t")[2:])
            i += 1
    lineCounter += 1
    if lineCounter % 100000 == 0: 
        print(lineCounter)
        
#remove directory if it exists, even if it has files 
if os.path.exists(newOutputDir): 
    shutil.rmtree(newOutputDir)
    
#make the new output directory 
os.mkdir(newOutputDir)

for key, value in outputDict.items(): 
    outfile = open(newOutputDir.rstrip("/") + "/" +  key.split(".")[0] + "UNI.tsv", "w")
    outfile.write("\n".join([str(line) for line in value if line != False]))

"""
outAnalysisStr = ""
for key, value in outputDict.items():
    propLabeled = 0 
    if len(value) > 0: 
        propLabeled = len([item for item in value if item != False])/len(value)
    outAnalysisStr += key + ":\t" + str(propLabeled) + "\n"

analyticsOutfile = open(newOutputDir.rstrip("/") + "/" + "ANALYTICS.txt", "w")
analyticsOutfile.write(outAnalysisStr)
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 13 15:47:24 2021

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

def updateOutputDict(crossRefDict, origDir, outputDict): 
    
    #for each file in inDir
    for fileName in os.listdir(origDir): 
        
        #account for fact that the inDir could have trialing slash or not
        filePath = origDir.rstrip("/") + "/" + fileName
        file = open(filePath, "r")
        
        fileLines = file.readlines()
        currList = outputDict[fileName]
        
        for i in range(1,len(fileLines)):
            
            #line in the original output file
            line = fileLines[i]
            
            #corresponding item in the list for this file in our output dictionary 
            currItem = currList[i]
            
            #the id from the nr database should be the 2nd column 
            currID = line.strip("\n").split("\t")[1]
            
            if currItem == False and currID in crossRefDict: 
                crossRef = crossRefDict[currID]
                crossReferencedLine = line.split("\t")[0] + "\t" + crossRef + "\t" + "\t".join(line.strip("\n").split("\t")[2:])
                currList[i] = crossReferencedLine
            
        file.close()
    return outputDict 
        
        
outputDict = {}
for fileName in os.listdir(originalOutputDir):
    
    filePath = originalOutputDir.rstrip("/") + "/" + fileName
    file = open(filePath)
    
    #we want all of the lines to be false at first for this file (later to be filled with output values)
    outputDict[fileName] = [False for line in file]

crossRefDict = {}
for line in open(refFile): 
    lineList = line.split("\t")
    uniAcc = lineList[0]
    fromID = lineList[2].strip("\n")
    
    """
    #possible exceptions or weird things that could happen with formatting? 
    if "." in fromID: 
        wOutDot = fromID.split(".")[0]
        crossRefDict[wOutDot] = uniAcc
    
    
    if "_" in fromID: 
        wOutUS = fromID.split("_")[1]
        crossRefDict[wOutUS] = uniAcc
    """
    
    #if there is already a uniprot id we want to have that stored to as a key 
    crossRefDict[uniAcc] = uniAcc
    
    crossRefDict[fromID] = uniAcc
    
    #if dict is larger than 5 gb 
    availMem = psutil.virtual_memory()[4]
    if availMem < 20e9:
        print("went!")
        gc.collect()
        outputDict = updateOutputDict(crossRefDict, originalOutputDir, outputDict) 
        crossRefDict = {}
print("went")
outputDict = updateOutputDict(crossRefDict, originalOutputDir, outputDict)

#remove directory if it exists, even if it has files 
if os.path.exists(newOutputDir): 
    shutil.rmtree(newOutputDir)
    
#make the new output directory 
os.mkdir(newOutputDir)

for key, value in outputDict.items(): 
    outfile = open(newOutputDir.rstrip("/") + "/" +  key.split(".")[0] + "UNI.tsv", "w")
    outfile.write("\n".join([str(line) for line in value if line != False]))
    
outAnalysisStr = ""
for key, value in outputDict.items():
    propLabeled = 0 
    if len(value) > 0: 
        propLabeled = len([item for item in value if item != False])/len(value)
    outAnalysisStr += key + ":\t" + str(propLabeled) + "\n"

analyticsOutfile = open(newOutputDir.rstrip("/") + "/" + "ANALYTICS.txt", "w")
analyticsOutfile.write(outAnalysisStr)


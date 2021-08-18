#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 11:11:30 2021

@author: benlitterer

This file is for when we just have two files, one for B62 output and one for MC30 output
"""

import sys
import os 

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
        
        #for testing mostly 
        for i in range(1,len(fileLines)):
            
            #line in the original output file
            line = fileLines[i]
            
            lineList = line.strip("\n").split("\t")
            
            if len(lineList) >= 2: 
                #the id of the query protein is in the first column of the output 
                queryID = lineList[0]
                
                #the uniprot id is in the second column of the blast output 
                outputID = lineList[1]
                
                if outputID in crossRefDict: 
                    goSet = crossRefDict[outputID]
                    
                    #we need to reference both the name of the file and the query that we are looking at 
                    if queryID not in outputDict[fileName]: 
                        outputDict[fileName][queryID] = {}
                        
                    #now that we have added a layer to the dictionary for the query, add a layer for the output protein and assign sets of gos 
                    if outputID not in outputDict[fileName][queryID]: 
                        outputDict[fileName][queryID][outputID] = goSet
                    else: 
                        outputDict[fileName][queryID][outputID] = outputDict[fileName][queryID][outputID].union(goSet)
        file.close()
    return outputDict 

#initialize dict that will hold files as keys and a uniID:goSet dictionary as values   
#should just have one for B62 and one for MC30 (or perhaps there are more of Kejue's matrices too)
outputDict = {filename:{} for filename in os.listdir(originalOutputDir) if "ANALYTICS" not in filename}

crossRefDict = {}
for line in open(refFile): 
    print("updating output dictionary")
    lineList = line.split()
    if len(lineList) == 2: 
        uniAcc = lineList[0]
        goTerm = lineList[1].strip("\n")
        
        #there are some go terms in the two column file that shouldn't be there due to a formatting error 
        if "GO:" in goTerm: 
            #possible exceptions or weird things that could happen with formatting? 
            if "." in uniAcc: 
                wOutDot = uniAcc.split(".")[0]
                if wOutDot not in  crossRefDict: 
                    crossRefDict[wOutDot] = set([goTerm])
                else: 
                    crossRefDict[wOutDot].add(goTerm)
            """
            if "_" in uniAcc: 
                wOutUS = uniAcc.split("_")[1]
                if wOutUS not in  crossRefDict: 
                    crossRefDict[wOutUS] = set([goTerm])
                else: 
                    crossRefDict[wOutUS].add(goTerm)
            """
            
            if uniAcc not in  crossRefDict: 
                crossRefDict[uniAcc] = set([goTerm])
            else: 
                crossRefDict[uniAcc].add(goTerm)
            
    #if dict is larger than 5 gb 
    if sys.getsizeof(crossRefDict) > 1e8:
        #print("refDict: " + str(sys.getsizeof(crossRefDict)))
        #print("outDict: " + str(sys.getsizeof(outputDict)))
        outputDict = updateOutputDict(crossRefDict, originalOutputDir, outputDict) 
        crossRefDict = {}
        
print("finished output dictionary")
#make the new output directory 
os.mkdir(newOutputDir)

totalOutLines = 0
#iterate over each file, and the dictionary corresponding to that file 
for filename, fileNameDict in outputDict.items(): 
    outfile = open(newOutputDir.rstrip("/") + "/" +  filename.split(".")[0] + "UNI.tsv", "w")
    outStr = ""
    
    #iterate over each query id in this file, and each dictionary containing the output prot id and gos for that id
    for queryID, goDict in fileNameDict.items(): 
        
        #iterate through the output ids and goSets for this query id 
        for outputID, goSet in goDict.items(): 
            outStr += queryID + "\t" + outputID + "\t" + ";".join(list(goSet)) + "\n"
            totalOutLines += 1
    outfile.write(outStr)

print("wrote file")
totalInLines = 0
for inFileName in os.listdir(originalOutputDir):
    #account for fact that the inDir could have trialing slash or not
    filePath = originalOutputDir.rstrip("/") + "/" + inFileName
    file = open(filePath, "r")
    
    fileLines = len(set([str(line.split("\t")[0] + " " + line.split("\t")[1]) for line in file]))
    totalInLines += fileLines
    
print(str(float(totalOutLines/totalInLines)))

"""
    #inner dictionary with uniID:{GO1, GO2, GO3} format 
    for innerKey, innerVal in value.items(): 
        outStr += innerKey + "\t" + ";".join(list(innerVal)) + "\n"
    outfile.write(outStr)
"""
    

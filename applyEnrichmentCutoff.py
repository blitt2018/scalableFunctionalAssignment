#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 13 15:13:23 2021

@author: blitt
"""

import sys 
import os 
import glob
import scipy.stats as stats 
from statsmodels.stats.multitest import multipletests 

goAnnotFile = open(sys.argv[1])

#inDir should contain one file for each matrix
inDir = sys.argv[2]

outDir = sys.argv[3]

supportDict = {}
totalCount = 0 

for line in goAnnotFile: 
    lineList = line.split()
    
    if len(lineList) == 2: 
        GO = lineList[1].strip("\n")

        if GO not in supportDict: 
            supportDict[GO] = 1 
        else: 
            supportDict[GO] += 1
        totalCount += 1

for outFileName in glob.glob(inDir.rstrip("/") + "/*"):
    if "ANALYSIS" not in outFileName: 
        outFile = open(outFileName)
        
        thisFileDict = {}
        #we want to store all of the queries in a 
        for line in outFile: 
            lineList = line.rstrip("\n").split("\t")
            queryProt = lineList[0]
            outputProt = lineList[1]
            goList = lineList[2].split(";")
            
            if queryProt not in thisFileDict: 
                thisFileDict[queryProt] = {} 
            
            #we add another layer, so that for each query in this file, we have a count of the occurences for each go annotation 
            for goAnnot in goList: 
                #this updates the amount of "votes" that this go annotaion has for this particular query protein 
                if goAnnot not in thisFileDict[queryProt]: 
                    thisFileDict[queryProt][goAnnot] = 1 
                else: 
                    thisFileDict[queryProt][goAnnot] += 1
                
                #this tracks the total amount of go annotations (not unique) for this query 
                if "totalAnnots" not in thisFileDict[queryProt]: 
                    thisFileDict[queryProt]["totalAnnots"] = 1 
                else: 
                    # we need the total amount of goAnnots for when we do the chi square test 
                    thisFileDict[queryProt]["totalAnnots"] += 1
            
        outputDict = {}
        #we should now have the goAnnot count for each goAnnot in each query. This is in the dictionary thisFileDict
        for queryProt, annotDict in thisFileDict.items(): 
            #how many go annots are assigned to this protein (not unique ones, just total sum)
            queryTotalAnnots= thisFileDict[queryProt]["totalAnnots"]
            
            chiSquareOutput = []
            for goAnnot, thisGOCount in annotDict.items(): 
                if goAnnot != "totalAnnots": 
                    baselineGOCount = supportDict[goAnnot]
                    
                    #apply the chi square test
                    #create a contingency table 
                    contingencyTable = [[thisGOCount, baselineGOCount],[queryTotalAnnots,totalCount]]
                    
                    #proportions of this go in output 
                    testProp = float(thisGOCount/queryTotalAnnots)
                    baselineProp = float(baselineGOCount/totalCount)
                    
                    #this ratio will be over 1 if we have a higher proportion of gos in our output than in the baseline
                    oddsRatio = testProp/baselineProp
                    
                    testStat, pVal, dof, expectedVals = stats.chi2_contingency(contingencyTable)
                    statsLine = [goAnnot, pVal, oddsRatio, thisGOCount, queryTotalAnnots, baselineGOCount , totalCount]
                    
                    chiSquareOutput.append(statsLine)
                
            bfout = multipletests([statsLine[1] for statsLine in chiSquareOutput], method="bonferroni")
            correctedPvals = list(bfout[1])
            
            correctedOutput = []
            for lineIndex in range(0,len(chiSquareOutput)): 
                currLine = chiSquareOutput[lineIndex]
                correctedPval = correctedPvals[lineIndex]
                currLine[1] = correctedPval 
                oddsRatio = currLine[2]
                
                #only want cases where there is at least some enrichment (rather than depletion) in the output (more go annotations than expected in our output)
                if oddsRatio > 1: 
                    correctedOutput.append(currLine)
            outputDict[queryProt] = correctedOutput
        
        #open file of the same name in the output directory 
        outFilePath = outDir.rstrip("/") + "/" + outFileName.split("/")[-1]
        outFile = open(outFilePath, "w")
        outStr = ""
        for queryProt, outputList in outputDict.items(): 
            for infoLine in outputList: 
                infoStr = [str(item) for item in infoLine]
                outLine = queryProt + "\t" + "\t".join(infoStr) + "\n"
                outStr += outLine
                
        #write all of the information from this query to the output file 
        outFile.write(outStr)


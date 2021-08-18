#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 13:00:08 2021

@author: blitt
"""

import sys 

#this should the the "idmapping.dat" mapping file from the uniprot ftp servers 
idMappingPath = sys.argv[1]

idMappingFile = open(idMappingPath)

#the result of running this script is a mapping file that only contains IDs that are in the NR dataset
#reference this post: https://www.biostars.org/p/164641/
outPath = sys.argv[2]
outFile = open(sys.argv[2], "w")

dbIDs = ["geneid", "gi", "embl", "refseq", "pir", "pdb", "uniprotkb-ac", "uniprotkb-id"]

#string containing what to write to the output (filtered) file 
outStr = ""
for line in idMappingFile: 
    lowLine = line.lower()
    toAppend = False 
    for dbID in dbIDs: 
        if dbID in lowLine: 
            toAppend = True 
    
    #append if this line contains a mapping that we need to go from NCBI nr database to uniprot 
    if toAppend: 
        outStr += line
    
outFile.write(outStr)

#!/bin/bash

# Copy/paste this job script into a text file and submit with the command:
#    sbatch thefilename
# job standard output will go to the file slurm-%j.out (where %j is the job ID)

#SBATCH --time=5:00:00   # walltime limit (HH:MM:SS)
#SBATCH --nodes=2   # number of nodes
#SBATCH --ntasks-per-node=16   # 16 processor core(s) per node 
#SBATCH --mem=70G   # maximum memory per node
#SBATCH --job-name="filterIDMapping.dat"
#SBATCH --mail-user=blitt@iastate.edu   # email address
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL

module load python/3.7.7-dwjowwi
basePath=/work/LAS/jernigan-lab/Ben
python3 $basePath/gitScalableFunctionalAssignment/scalableFunctionalAssignment/scripts/filterIDMappingFile.py $basePath/allCOVIDProtsEnrichment/idmapping.dat $basePath/allCOVIDProtsEnrichment/idmappingFiltered.dat 

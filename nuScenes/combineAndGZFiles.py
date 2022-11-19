# Purpose: Combine and GZIP individual Turtle files into a single .ttl.gz file
#          This is the preferred format to import it into a RDF Triple Store
# How to use:
#    python combineAndGZFiles.py -p <path> -f <filter> -t <target-filename-gz> 
# Example:
#    combineAndGZFiles.py -f 'nuscenes_kg_' -t 'nuscenes_kg.ttl.gz'
#    combineAndGZFiles.py -p 'C:\Data\KG\' -f 'nuscenes_kg_' -t 'nuscenes_kg.ttl.gz'
#
# Notes: 
# - The path is optional. Default = current directory 
# - The filter defines the prefix of the RDF Turtle files to be combined in GZIP'ed (e.g. 'nuscenes_kg_')
# - The target filename defines the name of the GZIP file (e.g. 'nuscenes_kg.ttl.gz')
#
# Python version used: 3.8
import os
import time
import gzip
import sys, getopt
from pathlib import Path
import shutil

file_filter = '' 
target_file = ''
path = '.\\'
try:
    opts, args = getopt.getopt(sys.argv[1:],"p:f:t:",["path=", "filter=", "target="])
except getopt.GetoptError:
    print("combineAndGZFiles.py -p <path> -f <filter> -t <target-filename-gz>")
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-f", "--filter"):
        file_filter = arg
    elif opt in ("-p", "--path"):
        path = arg
    elif opt in ("-t", "--target"):
        target_file = arg

if len(file_filter) == 0 or len(target_file) == 0:
    print("combineAndGZFiles.py -p <path> -f <filter> -t <target-filename-gz>")
    sys.exit(2)

target_file = path + target_file

print("write target file: " + target_file)
with gzip.open(target_file,'wb') as f_gz:
    for file in os.listdir(path):
        if file_filter in file:
            # merge intermediate files into target file 
            with open(file,'rb') as f_in:
                shutil.copyfileobj(f_in, f_gz)
            f_in.close()
            # remove file
            # os.remove(file)
f_gz.close()

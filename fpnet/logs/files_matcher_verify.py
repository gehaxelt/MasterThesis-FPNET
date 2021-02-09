#!/usr/bin/env python3
import os 
import sys
import re
import json
import statistics
import tarfile
import networkx
import ssdeep
from multiprocessing import Pool
try:
    import tld 
except:
    print("Install using: pip3 install --user tld")
    sys.exit(1)

from tld import get_fld, get_tld
from tld.utils import update_tld_names
try:
    #update_tld_names()
    pass
except Exception as e:
    print(e)

import csv
import sys
csv.field_size_limit(sys.maxsize)

if len(sys.argv) < 2:
    print("Usage: {} <LOGFOLDER>".format(sys.argv[0]))
    sys.exit(1)

LOGPATH = sys.argv[1]
LIMIT = "unlimited"
THRESHOLD_SCORE = 0

MATCHES = []

with open(LOGPATH + os.sep + "files" + os.sep + "matches.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if(line_count < 1):   # remove table header
            line_count += 1;
            continue;

        line_count += 1

        # script_a,script_b,matchscore,domain_a,filename_a,score_a, hash_a, domain_b,filename_b,score_b, hash_b, same_domain,same_filename
        # script_a = row[0]
        # script_b = row[1]
        # matchscore = int(row[2])
        # domain_a = row[3]
        # source_domain_a = row[4]
        # filename_a = row[5]
        # score_a = row[6]
        # hash_a = row[7]
        # domain_b = row[8]
        # source_domain_b = row[9]
        # filenmae_b = row[10]
        # score_b = row[11]
        # hash_b = row[12]
        # same_domain = row[13]
        # same_filename = row[14]
        # same_score = row[15]

        f1 = row[0]
        f2 = row[1]

        m = row[2]

        h1 = row[7]
        h2 = row[12]

        hn1 = ssdeep.hash(open(LOGPATH + os.sep + "files" + os.sep + "extracted" + os.sep + f1, 'rb').read())
        hn2 = ssdeep.hash(open(LOGPATH + os.sep + "files" + os.sep + "extracted" + os.sep + f2, 'rb').read())

        mn = ssdeep.compare(hn1, hn2)
        if mn != int(m):
            print("Something's wrong!!", m, mn, f1, f2)

        if line_count % 10000 == 0:
            print(line_count)


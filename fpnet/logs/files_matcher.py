#!/usr/bin/env python3
import os 
import sys
import re
import json
import tarfile
import csv
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

import ssdeep

if len(sys.argv) < 2:
    print("Usage: {} <LOGFOLDER>".format(sys.argv[0]))
    sys.exit(1)

LOGPATH = sys.argv[1]
LIMIT = "unlimited"
MATCH_THRESHOLD = 95

FUZZY_HASHES = {}
for f in os.listdir(LOGPATH + os.sep + "files" + os.sep + "extracted"):
    if '.csv' in f:
        continue
    try:
        fdata = open(LOGPATH + os.sep + "files" + os.sep + "extracted" + os.sep + f, encoding="utf8").read()
    except Exception as e:
        pass
    h = ssdeep.hash(fdata)
    FUZZY_HASHES[f] = h

MATCHES = []

with open(LOGPATH + os.sep + "files" + os.sep + "matches" + ".csv", "w") as wfile:
    writer = csv.writer(wfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['script_a', 'script_b', 'matchscore', 'domain_a', 'filename_a', 'score_a', 'domain_b', 'filename_b', 'score_b', 'same_domain', 'same_filename'])
    cntr = 0
    max_cntr = len(FUZZY_HASHES) * len(FUZZY_HASHES)
    for i in FUZZY_HASHES.keys():
        for j in FUZZY_HASHES.keys():
            cntr += 1
            if cntr % (max_cntr // 100) == 0:
                print(round(cntr / max_cntr * 100),)
            if (j,i) in MATCHES:
                continue
            p1 = i.split("_")
            p2 = j.split("_")
            d1 = p1[0]
            d2 = p2[0]
            s1 = p1[1]
            s2 = p2[1]
            f1 = "_".join(p1[2:])
            f2 = "_".join(p2[2:])

            if i == j:
                continue

            m = ssdeep.compare(FUZZY_HASHES[i], FUZZY_HASHES[j])
            if m >= MATCH_THRESHOLD:
                MATCHES.append((i,j))
                writer.writerow([i, j, m, d1, f1, s1, d2, f2, s2, d1 == d2, f1 == f2])

print("Number of matches: ", len(MATCHES))
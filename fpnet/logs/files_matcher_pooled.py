#!/usr/bin/env python3
import os 
import sys
import re
import json
import tarfile
import csv
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
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
        fdata = open(LOGPATH + os.sep + "files" + os.sep + "extracted" + os.sep + f, "rb").read()
    except Exception as e:
        continue
        pass
    h = ssdeep.hash(fdata)
    FUZZY_HASHES[f] = h


FUZZY_HASHES_LEN = len(FUZZY_HASHES)
FUZZY_HASHES_KEYS = list(FUZZY_HASHES.keys())

def create_pairs(offset, chunksize):
    ioffs = offset // FUZZY_HASHES_LEN
    joffs = offset % FUZZY_HASHES_LEN
    cntr = ioffs * FUZZY_HASHES_LEN + joffs
    for i in FUZZY_HASHES_KEYS[ioffs:]:
        for j in FUZZY_HASHES_KEYS[joffs:]:
            if cntr >= (offset+chunksize):
                return
            if cntr < offset:
                cntr += 1
                continue
            cntr += 1
            yield (i, j, FUZZY_HASHES[i], FUZZY_HASHES[j])

def match_ssdeep(pair):
    #p1 = pair[0].split("_")
    #p2 = pair[1].split("_")
    # pair[2] ssdeep hash
    # pair[3] ssdeep hash
    #d1 = p1[0] # page domain
    #d2 = p2[0] # page domain
    #sd1 = p1[1] # script domain
    #sd2 = p2[1] # script domain
    #s1 = p1[2] # score
    #s2 = p2[2] # score
    #f1 = "_".join(p1[3:]) # filename
    #f2 = "_".join(p2[3:]) # filename

    if pair[0] == pair[1]:
        return (pair[0], pair[1], False, 0, "", "")

    m = ssdeep.compare(pair[2], pair[3])
    if m >= MATCH_THRESHOLD:
        return (pair[0], pair[1], True, m, pair[2], pair[3])

    return (pair[0], pair[1], False, 0, "", "")

pairs_len = FUZZY_HASHES_LEN * FUZZY_HASHES_LEN
workers = 40
chunksize = FUZZY_HASHES_LEN * 500


MATCHES = set()
with open(LOGPATH + os.sep + "files" + os.sep + "matches" + ".csv", "w") as wfile:
    writer = csv.writer(wfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['script_a', 'script_b', 'matchscore', 'domain_a', 'sciprt_domain_a', 'filename_a', 'score_a', 'hash_a', 'domain_b', 'script_domain_b', 'filename_b', 'score_b', 'hash_b', 'same_domain', 'same_filename', 'same_score', 'same_script_domain'])

    with Pool(processes=workers) as pool:
        for i in range(0, pairs_len, chunksize):
            print("Creating list")
            data = list(create_pairs(i, chunksize))
            print("List created")
            print("Pool processing")
            results = pool.map(match_ssdeep, data)

            matches = list(filter(lambda x: x[0] != x[1] and x[2], results))
            print(i, i / (pairs_len) * 100, len(MATCHES))

            for match in matches:
                if not match[2] or match[0] == match[1]:
                    continue
                if (match[1], match[0]) in MATCHES:
                    continue

                p1 = match[0].split("_")
                p2 = match[1].split("_")
                d1 = p1[0] # page domain
                d2 = p2[0] # page domain
                sd1 = p1[1] # source domain
                sd2 = p2[1] # source domain
                s1 = p1[2] # score
                s2 = p2[2] # score
                f1 = "_".join(p1[3:]) # filename
                f2 = "_".join(p2[3:]) # filename
                h1 = match[4]
                h2 = match[5]
                MATCHES.add((match[0], match[1]))
                writer.writerow([match[0], match[1], match[3], d1, sd1, f1, s1, h1, d2, sd2, f2, s2, h2, d1 == d2, f1 == f2, s1 == s2, sd1 == sd2])

print("Number of matches: ", len(MATCHES))

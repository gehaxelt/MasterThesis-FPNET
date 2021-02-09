#!/usr/bin/env python3
import os 
import sys
import re
import json
import statistics
import tarfile
import networkx
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

        #if row[11] == "True" or row[12] == "True" or row[13] == "True":
        #    continue

        max_script_score = max(int(row[6]), int(row[11]))
        if max_script_score < THRESHOLD_SCORE:
            continue

        MATCHES.append(row)
        # if line_count >= 500*1000:
        #     break
print("Found matches: ", len(MATCHES))

HASHES = {}
FILE_MATCHES = {}

print("Creating graphs")
g = networkx.Graph(map(lambda x: (x[7], x[12]), MATCHES)) # based on hashes
for group in networkx.connected_components(g):
    group_name = list(group)[0]
    HASHES[group_name] = group
    FILE_MATCHES[group_name] = set()

print("Hash Groups found: ", len(HASHES))

def add_group(x):
    if x[7] in HASHES:
        return (x[7], x)
    elif x[12] in HASHES:
        return (x[12], x)
    else:
        for k in HASHES:
            if x[7] in HASHES[k] or x[12] in HASHES[k]:
                return (k, x)
        raise Exception("Group error")

print("Matching groups")
MATCHES_WITH_GROUP = list(map(add_group,MATCHES))
print("Matching groups done")

print("Adding indices")
for i, mg in enumerate(MATCHES_WITH_GROUP):
    MATCHES_WITH_GROUP[i] = (i,mg[0], mg[1])
print("Adding indices done")

print("Creating FILES_MATCHES")
for i,g,m in MATCHES_WITH_GROUP:
    if not i in FILE_MATCHES[g]:
        FILE_MATCHES[g].add(i)
print("Creating FILES_MATCHES done")

print("File groups: ", len(FILE_MATCHES))

for group in FILE_MATCHES.copy():
    if len(FILE_MATCHES[group]) <= 1:
        del FILE_MATCHES[group]
        continue

print("File groups after filtering: ", len(FILE_MATCHES))

with open(LOGPATH + os.sep + "files" + os.sep + "matches_groups_" + str(THRESHOLD_SCORE) + ".csv", "w") as wfile:
    writer = csv.writer(wfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['scripts', 'size', 'minmatchscore', 'maxmatchscore', 'avgmatchscore', 'unique_minscore', 'unique_maxscore', 'unique_avgscore'])
    for group in FILE_MATCHES:
        tmp_files = []
        tmp_mscores = []
        tmp_scores = []
        for idx in FILE_MATCHES[group]:
            pair = MATCHES[idx]
            file_a = pair[0]
            file_b = pair[1]
            m_score = int(pair[2])
            score_a = int(pair[6])
            score_b = int(pair[11])

            if not file_a in tmp_files:
                tmp_files.append(file_a)
                tmp_scores.append(score_a)
            if not file_b in tmp_files:
                tmp_files.append(file_b)
                tmp_scores.append(score_b)
            tmp_mscores.append(m_score)


        scripts = "|||".join(tmp_files)
        size = len(tmp_files)
        minmatchscore = min(tmp_mscores)
        maxmatchscore = max(tmp_mscores)
        avgmatchscore = statistics.mean(tmp_mscores)

        minscore = min(tmp_scores)
        maxscore = max(tmp_scores)
        avgscore = statistics.mean(tmp_scores)

        writer.writerow([scripts, size, minmatchscore, maxmatchscore, avgmatchscore, minscore, maxscore, avgscore])


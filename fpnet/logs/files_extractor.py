#!/usr/bin/env python3
import os 
import sys
import re
import json
import gzip
import codecs
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

SCRIPTS = {}

with open(LOGPATH + os.sep + "paper_query" + os.sep + "q4_b_" + LIMIT + ".csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if(line_count < 1):   # remove table header
            line_count += 1;
            continue;

        line_count += 1

        # id,domain,script_id,script_score,filename,script_domain,script_signature
        domain = row[1]
        score = row[3]
        filename = row[4]
        filedomain = row[5]

        if not domain in SCRIPTS:
            SCRIPTS[domain] = []
        SCRIPTS[domain].append({'filename': filename, 'score': score, 'filedomain': filedomain})

print("Found domains to process: ", len(SCRIPTS))

if not os.path.exists(LOGPATH + os.sep + "files" + os.sep + "extracted"):
    os.mkdir(LOGPATH + os.sep + "files" + os.sep + "extracted")

EXTRACTED_FILES = {}

for domain in SCRIPTS.copy():
    if not os.path.exists(LOGPATH + os.sep + "files" + os.sep + "{}.json.gz".format(domain)):
        del SCRIPTS[domain]
        continue
    with gzip.open(LOGPATH + os.sep + "files" + os.sep + "{}.json.gz".format(domain), 'rt') as gz:
        try:
            line = gz.read()
            if not line:
                continue
            data = json.loads(line)
        except Exception as e:
            print(line, e)

        for k in SCRIPTS[domain]:
            f = k['filename']
            fdom = k['filedomain']
            score = k['score']

            if not f:
                continue

            for flow_id, http_con in data.items():
                url = http_con['request']['url']
                host = http_con['request']['host']
                url_f = url.split('/')[-1]
                try:
                    domain_res = get_tld("http://{}".format(host),as_object=True)
                    host = domain_res.fld
                except Exception as e:
                    continue

                if url_f == f and host == fdom:
                    has_archive_file = True
                    if not f in EXTRACTED_FILES:
                        EXTRACTED_FILES[f] = []
                    EXTRACTED_FILES[f].append(domain)

                    file_data = codecs.decode(http_con['response']['content'].encode(), 'base64')
                    try:
                        with open(LOGPATH + os.sep + "files" + os.sep + "extracted" + os.sep + "{}_{}_{}_{}".format(domain, fdom, score, f), "wb") as fh:
                            fh.write(file_data)
                    except Exception as e:
                        print(e)
                    break

print("Found archive file matches: ", len(EXTRACTED_FILES), "by domains: ", len(SCRIPTS))

#!/usr/bin/env python3
import os 
import sys
import re
import json
try:
    import tld 
except:
    print("Install using: pip3 install --user tld")
    sys.exit(1)

from tld import get_fld, get_tld
from tld.utils import update_tld_names
try:
    update_tld_names()
except Exception as e:
    print(e)

if len(sys.argv) < 2:
    print("Usage: {} <LOGFOLDER>".format(sys.argv[0]))
    sys.exit(1)

LOGPATH = sys.argv[1]

REDIRECTS = []
REDIRECTS_SAME_DOMAIN = []
REDIRECTS_SAME_TLD = []
REDIRECTS_DIFFERENT = []

URL_IS_NONE = []

with open(LOGPATH + os.sep +  "fpnet_scan.csv") as f:
    for line in f:
        line = json.loads(line)
        if line['origin'] == 'python' and line['action'] == 'finish_trace':
            domain = line['domain']
            url = line['url']

            if not url or url == 'None':
                URL_IS_NONE.append(domain)
                continue
            old_domain = get_fld('http://' + domain + '/')
            new_domain = get_fld(url)
            if old_domain != new_domain:
                REDIRECTS.append((old_domain, url, new_domain))

print("No final URL: ", len(URL_IS_NONE))
print("Total Redirects to other FLDs: ", len(REDIRECTS))

TOP_TARGETS = {}

for r in REDIRECTS:
    old_domain = get_tld('http://' + r[0] + '/', as_object=True)
    new_domain = get_tld('http://' + r[2] + '/', as_object=True)

    if old_domain.domain == new_domain.domain and old_domain.tld != new_domain.tld: 
        REDIRECTS_SAME_DOMAIN.append(r)
    elif old_domain.domain != new_domain.domain and old_domain.tld == new_domain.tld:
        REDIRECTS_SAME_TLD.append(r)
    elif old_domain.domain != new_domain.domain and old_domain.tld != new_domain.tld:
        REDIRECTS_DIFFERENT.append(r)

    if new_domain.fld not in TOP_TARGETS:
        TOP_TARGETS[new_domain.fld] = 1
    else:
        TOP_TARGETS[new_domain.fld] += 1

TOP_TARGETS_TRIMMED = {k: v for k, v in sorted(filter(lambda x: x[1] > 1, TOP_TARGETS.items()), key=lambda item: item[1], reverse=True)}

print("Redirects to same domain, but different TLDs: ", len(REDIRECTS_SAME_DOMAIN))
print("Redirects to same TLD, but different domains: ", len(REDIRECTS_SAME_TLD))
print("Redirects to different TLD + domains: ", len(REDIRECTS_DIFFERENT))
print("Top targets: ", len(TOP_TARGETS_TRIMMED), TOP_TARGETS_TRIMMED)
print("SUM: ", len(REDIRECTS_SAME_DOMAIN) + len(REDIRECTS_SAME_TLD) + len(REDIRECTS_DIFFERENT), len(REDIRECTS_SAME_DOMAIN) + len(REDIRECTS_SAME_TLD) + len(REDIRECTS_DIFFERENT) == len(REDIRECTS))
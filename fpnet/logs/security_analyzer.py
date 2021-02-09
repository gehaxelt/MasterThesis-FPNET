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

EXTRACTED_FILES = {}

INSECURE_SOURCES = {}
SECURE_SOURCES = {}
INSECURE_TO_SECURE_REDIRECTS = {}
TOTAL_NUM = 0
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

                    TOTAL_NUM += 1

                    code = int(http_con['response']['status_code'])
                    if (code == 301 or code == 302) and url.startswith("http://"):
                        if 'Location' in http_con['response']['headers']:
                            #print(http_con['response']['headers']['Location'][0])
                            if http_con['response']['headers']['Location'][0].startswith("https://"):
                                if not url in INSECURE_TO_SECURE_REDIRECTS:
                                    INSECURE_TO_SECURE_REDIRECTS[url] = []
                                INSECURE_TO_SECURE_REDIRECTS[url].append([domain, score, http_con['response']])
                                continue

                    if url.startswith("http://"):
                        is_secure = False
                    elif url.startswith("https://"):
                        is_secure = True
                    else:
                        print("Weird url:", url)
                        continue

                    if not is_secure:
                        if not url in INSECURE_SOURCES:
                            INSECURE_SOURCES[url] = []

                        INSECURE_SOURCES[url].append([domain, score, http_con['response']])
                    else:
                        if not url in SECURE_SOURCES:
                            SECURE_SOURCES[url] = []
                        SECURE_SOURCES[url].append([domain, score, http_con['response']])

def dict2countDomain(d):
    count = 0
    for k in d:
        count += len(d[k])
    return count

def url2domain(u):
    try:
        return get_fld(u)
    except:
        return ''

def dict2domain(d):
    return set(map(url2domain, d)) 

def dict2scores(d):
    s = {}
    for k in d:
        for q in d[k]:
            if not int(q[1]) in s:
                #s[q[1]] = []
                s[int(q[1])] = 0
            #s[q[1]].append(q[0])
            s[int(q[1])] += 1
    return sorted(s.items(), key=lambda x: x[0]) 

def resp2headers(r):
    hsts = False
    csp = False
    cto = False
    refp = False
    for h in r['headers']:
        h = h.lower()
        if h == 'Strict-Transport-Security'.lower():
            hsts = True
        elif h == 'Content-Security-Policy'.lower():
            csp = True
        elif h == 'X-Content-Type-Options'.lower():
            cto = True
        elif h == 'Referrer-Policy'.lower():
            refp = True
    return hsts, csp, cto, refp

def dict2headers(d):
    counts = {
        'hsts': 0,
        'csp': 0,
        'cto': 0,
        'refp': 0,
    }
    for k in d:
        for q in d[k]:
            r = q[2]
            hsts, csp, cto, refp = resp2headers(r)
            if hsts:
                counts['hsts'] += 1
            if csp:
                counts['csp'] += 1
            if cto:
                counts['cto'] += 1
            if refp:
                counts['refp'] += 1
    return counts

print("Total: ", TOTAL_NUM)
print("Redirects: ", len(INSECURE_TO_SECURE_REDIRECTS), dict2countDomain(INSECURE_TO_SECURE_REDIRECTS))
print(sorted(dict2scores(INSECURE_TO_SECURE_REDIRECTS)))
print(dict2headers(INSECURE_TO_SECURE_REDIRECTS))
print("-" * 20)
print("Insecure: ", len(INSECURE_SOURCES), dict2countDomain(INSECURE_SOURCES))
print(sorted(dict2scores(INSECURE_SOURCES)))
print(dict2headers(INSECURE_SOURCES))
print("-" * 20)
print("Secure: ", len(SECURE_SOURCES), dict2countDomain(SECURE_SOURCES))
print(sorted(dict2scores(SECURE_SOURCES)))
print(dict2headers(SECURE_SOURCES))
print("-" * 20)

print('dict vs. set: ', len(INSECURE_SOURCES), len(set(INSECURE_SOURCES)))
print("Insecure & Redirects: ", len(dict2domain(INSECURE_SOURCES) & dict2domain(INSECURE_TO_SECURE_REDIRECTS)))
print(sorted(dict2domain(INSECURE_SOURCES) & dict2domain(INSECURE_TO_SECURE_REDIRECTS)))
print("-" * 20)
print("Insecure & Secure: ", len(dict2domain(INSECURE_SOURCES) & dict2domain(SECURE_SOURCES)))
print(sorted(dict2domain(INSECURE_SOURCES) & dict2domain(SECURE_SOURCES)))
print("-" * 20)
print("Secure & Redirects: ", len(dict2domain(SECURE_SOURCES) & dict2domain(INSECURE_TO_SECURE_REDIRECTS)))
print(sorted(dict2domain(SECURE_SOURCES) & dict2domain(INSECURE_TO_SECURE_REDIRECTS)))
print("-" * 20)

M = {
    'redirects': INSECURE_TO_SECURE_REDIRECTS,
    'insecure': INSECURE_SOURCES,
    'secure': SECURE_SOURCES,
}

if not os.path.exists(LOGPATH + os.sep + "security"):
    os.mkdir(LOGPATH + os.sep + "security")

for d in M:
    csvw = csv.writer(open(LOGPATH + os.sep + "security" + os.sep + d + ".csv", 'w'))
    csvw.writerow(['url', 'domain', 'score', 'hsts', 'csp', 'cto', 'refp'])
    for r in M[d]:
        q = M[d][r]
        for k in q:
            hsts, csp, cto, refp = resp2headers(k[2])
            csvw.writerow([r, k[0], k[1], hsts, csp, cto, refp])

import csv
from urllib.parse import urlparse
from collections import Counter, OrderedDict
# import matplotlib.pyplot as plt
#import numpy as np
#from scipy import stats
#from numpy import mean, absolute
import operator
import collections
import os

import sys
csv.field_size_limit(sys.maxsize)

def topercent(small, big):
    return str( round( (small*100.0)/big, 2) )


stats1 = []
stats2 = []
statsdict = {}
colorstats = []
featurestats = []
featurestats_sample_size = 0

LOGPATH = sys.argv[1]
THRESHOLD = int(sys.argv[2])
LIMIT = "unlimited"


fpscripts = []
# all_script_signatures
with open(LOGPATH + os.sep + "paper_query" + os.sep + "q4_b2_" + LIMIT + ".csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if(line_count < 1):   # remove table header
            line_count += 1;
            continue;

        line_count += 1

        scriptid = row[0]
        score = int(row[1])
        scriptname = row[2]
        scriptdomain = row[3]
        signature = row[4]

        # allscripts.append( [score, scriptname, signature] )
        
        if(score > THRESHOLD):
            fpscripts.append( [score, scriptname, signature, len(signature), scriptdomain] )    


print("we found " +str( len(fpscripts) )+ " scripts with score > {}".format(THRESHOLD))


# Now we search of the same behaviour can be found in larger scripts than the one we know
# webpack, or obfruscated, etc.

fpscripts = sorted(fpscripts, key=lambda x: x[3] ) # sort shortest signature first

sigdict = {}
hitdict = {}
scriptdomainsdict = {}
hasmatch = []
counter = 0
length = len(fpscripts)
for a in fpscripts[:]:
    a_score = a[0]
    a_sig = a[2]
    a_name = "{}_{}_{}".format(a[1], a_score, len(a_sig.split(";")))
    a_domain = a[4]
    counter += 1
    print(round((100.0*counter)/length,1), a_name)

    # if counter > 1000:
    #   continue
    #   
    if a_sig in hasmatch: # don't go over super-set signatures
        continue

    for b in fpscripts:
        b_score = b[0]
        b_sig = b[2]
        b_name = "{}_{}_{}".format(b[1], b_score, len(b_sig.split(";")))
        b_domain = b[4]


        if(a[3] > b[3]):    # some big can not be in a shorter signature
            continue

        if( a_score > b_score): 
            continue

        # if( a_name == b_name):
        #   continue



        if(a_sig in b_sig):
            print(a_name + " signature in " + b_name+" signature")
            if(a_sig in sigdict):
                if not (b_name in sigdict[a_sig]):
                    sigdict[a_sig].append(b_name)
            else:
                sigdict[a_sig] = [a_name]
                if a_name != b_name:
                    sigdict[a_sig].append(b_name)

            if not a_sig in hitdict:
                hitdict[a_sig] = 0
            hitdict[a_sig] += 1

            if not a_sig in scriptdomainsdict:
                scriptdomainsdict[a_sig] = []
            scriptdomainsdict[a_sig].append(b_domain)

            if not b_sig in hasmatch and (a_sig != b_sig or a_name != b_name) : # add matched sig to hasmatch list, so we don't loop it again. Also only if that isn't us.
                print("added " + b_name + " to hasmatch list")
                hasmatch.append(b_sig)

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

FINDINGS = []

for s in  collections.OrderedDict(sorted(list(sigdict.items()), key=lambda x: len(x[1]) )) :
    uniquesig = f7( s.split(";") )
    
    sigscore = len(uniquesig)
    siglen = len(s.split(";"))
    hits = hitdict[s]
    files = len(sigdict[s])
    scriptdomains = scriptdomainsdict[s]

    if hits <= 1:
        print("Removing due to too few hits: ", sigdict[s])
        continue

    FINDINGS.append([sigscore, hits, s, ";".join(sigdict[s]), siglen, files, scriptdomains ])

PAGES = []

# all_page_signatures
with open(LOGPATH + os.sep + "paper_query" + os.sep + "q4_c_" + LIMIT + ".csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if(line_count < 1):   # remove table header
            line_count += 1;
            continue;

        line_count += 1

        p_id = row[0]
        p_domain = row[1]
        p_score = row[2]
        p_sig = row[3]

        PAGES.append([p_domain, p_sig])

print("we found " +str( len(PAGES) )+ " pages")

# 
with open(LOGPATH + os.sep + "paper_query" + os.sep + "found_signatures_{}_".format(THRESHOLD) + LIMIT + ".csv", "w") as wfile:
    writer = csv.writer(wfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["signature score", "hits","affected_domains_cnt", "signature", "scripts", "affected_domains", "siglen", "files", "script_domains_cnt", "script_domains"])

    for finding in FINDINGS:
        f_score = finding[0]
        f_hits = finding[1]
        f_sig = finding[2]
        f_files = finding[3]
        f_siglen = finding[4]
        f_files_cnt = finding[5]
        f_domains = []
        #f_scriptdomains = ";".join(["{}:{}".format(x,y) for x,y in collections.Counter(finding[6]).items()])
        f_scriptdomains = ";".join(["{}:{}".format(x,y) for x,y in collections.Counter(finding[6]).most_common()]) 
        f_scriptdomains_cnt = len(collections.Counter(finding[6]).keys())
        for page in PAGES:
            if not f_sig in page[1]:
                continue
            if page[0] in f_domains:
                continue
            f_domains.append(page[0])

        writer.writerow( [f_score, f_hits, len(f_domains), f_sig, f_files,  ";".join(f_domains), f_siglen, f_files_cnt, f_scriptdomains_cnt, f_scriptdomains ] )




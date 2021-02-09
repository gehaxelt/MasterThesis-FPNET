#!/usr/bin/env python3
import os
import sys 
import re
import json

if len(sys.argv) < 2:
    print("Usage: {} <LOGFOLDER>".format(sys.argv[0]))
    sys.exit(1)

LOGPATH = sys.argv[1]

HUB_REQUEST_COUNT = 0
NEW_SESSION_COUNT = 0
REM_SESSION_COUNT = 0
NODE_DOMAIN_COUNT = 0

MONP_DOMAIN_COUNT = 0 # get trace from python
MONJ_DOMAIN_COUNT = 0 # get trace from javascript
MONL_DOMAIN_COUNT = 0 # log score from javascript
MONF_DOMAIN_COUNT = 0 # finished trace from python

MONFT_DOMAIN_COUNT = 0
MONFE_DOMAIN_COUNT = 0
MONFA_DOMAIN_COUNT = 0
MONFW_DOMAIN_COUNT = 0
MONFJE_DOMAIN_COUNT = 0
MONFJS_DOMAIN_COUNT = 0
MONFLS_DOMAIN_COUNT = 0
MONFJSE_DOMAIN_COUNT = 0

HUB_DOMAINS = []
NODE_DOMAINS = []

MONP_DOMAINS = []
MONJ_DOMAINS = []
MONL_DOMAINS = []
MONF_DOMAINS = []

MONFT_DOMAINS = [] #timeout
MONFE_DOMAINS = [] # no fpmon 
MONFA_DOMAINS = [] # alert text:
MONFW_DOMAINS = [] # no such window
MONFJE_DOMAINS = [] # java.net.ConnectException
MONFJS_DOMAINS = [] #  Message: javascript error
MONFLS_DOMAINS = [] # Message: unknown error: cannot determine loading status
MONFJSE_DOMAINS = [] # Message: java.net.SocketException: Connection rese

with open(LOGPATH + os.sep +  "fpnet_scan.csv") as f:
    for line in f:
        line = json.loads(line)
        if line['origin'] == 'python':
            if line['action'] == 'get_trace':
                MONP_DOMAIN_COUNT += 1
                if not line['domain'] in MONP_DOMAINS:
                    MONP_DOMAINS.append(line['domain'])
            elif line['action'] == 'finish_trace':
                MONF_DOMAIN_COUNT += 1
                if not line['domain'] in MONF_DOMAINS:
                    MONF_DOMAINS.append(line['domain'])
            elif line['action'] == 'fail_trace':
                if 'Message: timeout' in line['reason']: # Reason: Message: timeout: Timed out receiving message from renderer (?)
                    MONFT_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFT_DOMAINS:
                        MONFT_DOMAINS.append(line['domain'])
                elif 'Message: no such element: Unable to locate element:' in line['reason'] or 'fpmon_success not found' in line['reason']:
                    MONFE_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFE_DOMAINS:
                        MONFE_DOMAINS.append(line['domain'])
                elif 'Alert Text:' in line['reason']:
                    MONFA_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFA_DOMAINS:
                        MONFA_DOMAINS.append(line['domain'])
                elif 'Message: no such window:' in line['reason'] or 'Message: chrome not reachable' in line['reason']:
                    MONFW_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFW_DOMAINS:
                        MONFW_DOMAINS.append(line['domain'])
                elif 'java.net.ConnectException' in line['reason']:
                    MONFJE_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFJE_DOMAINS:
                        MONFJE_DOMAINS.append(line['domain'])
                elif 'Message: javascript error' in line['reason']:
                    MONFJS_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFJS_DOMAINS:
                        MONFJS_DOMAINS.append(line['domain'])
                elif 'Message: unknown error: cannot determine loading status' in line['reason']:
                    MONFLS_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFLS_DOMAINS:
                        MONFLS_DOMAINS.append(line['domain'])
                elif 'Message: java.net.SocketException: Connection reset' in line['reason']:
                    MONFJSE_DOMAIN_COUNT += 1
                    if not line['domain'] in MONFJSE_DOMAINS:
                        MONFJSE_DOMAINS.append(line['domain'])
        elif line['origin'] == 'javascript':
            if line['action'] == 'get_trace':
                MONJ_DOMAIN_COUNT +=1
                if not line['domain'] in MONJ_DOMAINS:
                    MONJ_DOMAINS.append(line['domain'])
            elif line['action'] == 'log_score':
                MONL_DOMAIN_COUNT += 1
                if not line['domain'] in MONL_DOMAINS:
                    MONL_DOMAINS.append(line['domain'])


print("Monitor python request count: ", MONP_DOMAIN_COUNT, len(MONP_DOMAINS))
print("Monitor javascript request count: ", MONJ_DOMAIN_COUNT, len(MONJ_DOMAINS))
print("Monitor log score request count: ", MONL_DOMAIN_COUNT, len(MONL_DOMAINS))
print("-"*20)
print("Monitor finished request count: ", MONF_DOMAIN_COUNT, len(MONF_DOMAINS))
print("Monitor timeout request count: ", MONFT_DOMAIN_COUNT, len(MONFT_DOMAINS))
print("Monitor no fpmon request count: ", MONFE_DOMAIN_COUNT, len(MONFE_DOMAINS))
print("Monitor alert text request count: ", MONFA_DOMAIN_COUNT, len(MONFA_DOMAINS))
print("Monitor no such window request count: ", MONFW_DOMAIN_COUNT, len(MONFW_DOMAINS))
print("Monitor Java Exception request count: ", MONFJE_DOMAIN_COUNT, len(MONFJE_DOMAINS))
print("Monitor JavaScript exception request count: ", MONFJS_DOMAIN_COUNT, len(MONFJS_DOMAINS))
print("Monitor Cannot determine loading status: ", MONFLS_DOMAIN_COUNT, len(MONFLS_DOMAINS))
print("Monitor Socket Connection reset: ", MONFJSE_DOMAIN_COUNT, len(MONFJSE_DOMAINS))

FAILED_DOMAINS = set(MONFT_DOMAINS) | set(MONFE_DOMAINS) | set(MONFA_DOMAINS) | set(MONFW_DOMAINS) | set(MONFJE_DOMAINS) | set(MONFJS_DOMAINS) | set(MONFLS_DOMAINS) | set(MONFJSE_DOMAINS)

print("SUM: Finished: {} + Failed: {} => {}".format(len(MONF_DOMAINS), len(FAILED_DOMAINS), len(MONF_DOMAINS)+len(FAILED_DOMAINS)))

UNKNOWN_DOMAINS = (set(FAILED_DOMAINS) | set(MONF_DOMAINS)) ^ set(MONP_DOMAINS)
WITHOUT_SCORE = []
if len(UNKNOWN_DOMAINS) == 0:
    print("GOOD: Sum of finished and failed requests matches")
else:
    print("BAD: Some domains were not properly monitored:")
    print("Missing: ", len(UNKNOWN_DOMAINS), UNKNOWN_DOMAINS)

    for domain in UNKNOWN_DOMAINS:
        if domain not in MONL_DOMAINS:
            WITHOUT_SCORE.append(domain)
    
    if WITHOUT_SCORE:
        print("BAD: Some of those did not send a log score :-( ")
        print("Missing: ", WITHOUT_SCORE)
    else:
        print("GOOD: We got a log score for for all of them!")

print("-"*20)

for file in os.listdir(LOGPATH):
    if not re.match(r'^node\d+', file): 
        continue
    node_id = int(file.replace("node", ""))
    with open(LOGPATH + os.sep + file) as f:
        for line in f:
            if 'Started new session' in line:
                NEW_SESSION_COUNT += 1
                continue
            elif 'Removing session' in line:
                REM_SESSION_COUNT += 1
                continue
            elif '--domain=' in line:
                NODE_DOMAIN_COUNT += 1
                m = re.findall(r'--domain=(.*?)"', line)
                if not m[0] in NODE_DOMAINS:
                    NODE_DOMAINS.append(m[0])

print("Node new sessions: ", NEW_SESSION_COUNT)
print("Node removed sessions: ", REM_SESSION_COUNT)
print("Node domain count: ", NODE_DOMAIN_COUNT, len(NODE_DOMAINS))

#print("-"*20)

if len(NODE_DOMAINS) == len(MONP_DOMAINS):
    print("GOOD: Python and nodes had the same amount of domains!")
else:
    print("BAD: Python and node domain lists do not match :-/")

    # Question: Why doesn't the python request domains and the node domain count match? 
    # Domains that we have a python trace request for, but didn't see them in the node logs.
    monp_vs_node_domains = set(NODE_DOMAINS) ^ set(MONP_DOMAINS)
    print("Monitor python vs. Node domains: ", len(monp_vs_node_domains))
    print("Missing: ", monp_vs_node_domains)

print("-"*20)

# Question: Why doesn't the python request domains and python finished domain match?
# Domains that we've seen in the python trace request, but not in the python finished request.
monp_vs_monf_domains = set(MONF_DOMAINS) ^ set(MONP_DOMAINS)
print("Monitor python vs. Monitor finished domains: ", len(monp_vs_monf_domains))

MISSING = []
for domain in monp_vs_monf_domains:
    if domain in FAILED_DOMAINS:
        continue
    else:
        MISSING.append(domain)

if MISSING:
    print("BAD: Unknown failure for domains: ", len(MISSING), MISSING)
else:
    print("GOOD: We got log scores and no unknown failures")

# Question: Why is the python request count lower than the fpnet_scanners domain count?
# -> works for 1k

print("-"*20)

# Question: Why are the log score request domains vs. finished different? 
# Sometimes we have a log score, but after that a timeout :-/
monl_vs_monf_domains = set(MONL_DOMAINS) ^ set(MONF_DOMAINS)
print("Log score vs. Finished domains: ", len(monl_vs_monf_domains))
MISSING = []
failure_count = 0
logscore_count = 0
for domain in monl_vs_monf_domains:
    if domain in MONL_DOMAINS:
        logscore_count += 1
        continue
    elif domain in FAILED_DOMAINS:
        failure_count += 1
        continue
    else:
        MISSING.append(domain)

print("Scored, but didn't finish:", logscore_count)
print("Known failure, but no log score:", failure_count)
if MISSING:
    print("BAD: Domains finished, but didn't sent a log score: ", len(MISSING), MISSING)
else:
    print("GOOD: We got log scores before the failures")

print("-"*20)


# Question: Why are the log score request domains vs. monitor python different? 
monl_vs_monp_domains = set(MONL_DOMAINS) ^ set(MONP_DOMAINS)
print("Log score vs. Python request domains: ", len(monl_vs_monp_domains))
MISSING = []
failure_count = 0
logscore_count = 0
for domain in monl_vs_monp_domains:
    if domain in MONL_DOMAINS:
        logscore_count += 1
        continue
    elif domain in FAILED_DOMAINS:
        failure_count += 1
        continue
    else:
        MISSING.append(domain)

print("Scored, but didn't finish:", logscore_count)
print("Known failure, but no log score:", failure_count)
if MISSING:
    print("BAD: Domains finished, but didn't sent a log score: ", len(MISSING), MISSING)
else:
    print("GOOD: We got log scores before the failures")

print("-"*20)


print("SUM: ", len(MONL_DOMAINS) + len(FAILED_DOMAINS) - (len(MONL_DOMAINS) - len(MONF_DOMAINS)) + (len(UNKNOWN_DOMAINS) - len(WITHOUT_SCORE)))

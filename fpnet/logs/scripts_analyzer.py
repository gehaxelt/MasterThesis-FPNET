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

DOMAIN_COUNT = 0
SCRIPT_COUNT = 0
CALLS_COUNT = 0
AVG_SCRIPTS = []
AVG_CALLS = []

TOP_SOURCES = {}
TOP_SOURCE_DOMAINS = {}
TOP_FILENAMES = {}

DATA = []

with open(LOGPATH + os.sep +  "fpnet_scan.csv") as f:
    for line in f:
        line = json.loads(line)
        if line['origin'] == 'javascript' and line['action'] == 'log_score':
            DOMAIN_COUNT += 1
            domain = line['domain']
            url = line['url']
            js_scripts = line['script_origins_calls']

            datapoint = {
                'domain': domain,
                'url': url,
                'scripts': js_scripts
            }
            DATA.append(datapoint)

            SCRIPT_COUNT += len(js_scripts)
            AVG_SCRIPTS.append(len(js_scripts))

            for source in js_scripts:
                # if source == 'undefined':
                #     print(domain)
                # elif source == 'null':
                #     print(domain)
                CALLS_COUNT += len(js_scripts[source]['data'])
                AVG_CALLS.append(len(js_scripts[source]['data']))

                if not source in TOP_SOURCES:
                    TOP_SOURCES[source] = 1
                else:
                    TOP_SOURCES[source] += 1

                filename = source.split('/')[-1]
                if '?' in filename:
                    filename = filename.split("?")[0]
                if '.js' in filename:
                    if not filename in TOP_FILENAMES:
                        TOP_FILENAMES[filename] = 0
                    TOP_FILENAMES[filename] += 1


print("Number of domains: ", DOMAIN_COUNT)
print("Number of scripts: ", SCRIPT_COUNT)
print("min amount of scripts per domain: ", min(AVG_SCRIPTS))
print("max amount of scripts per domain: ", max(AVG_SCRIPTS))
print("AVG amount of scripts per domain: ", sum(AVG_SCRIPTS)/len(AVG_SCRIPTS))

print("--" * 20)
print("Number of calls: ", CALLS_COUNT)
print("min amount of calls per script: ", min(AVG_CALLS))
print("max amount of calls per script: ", max(AVG_CALLS))
print("AVG amount of calls per script: ", sum(AVG_CALLS)/len(AVG_CALLS))

print("--" * 20)
print("Top 15 source urls:")
TOP_SOURCES = {k: v for k, v in sorted(TOP_SOURCES.items(), key=lambda item: item[1], reverse=True)}
with open(LOGPATH + os.sep + 'source_urls.csv', 'w') as f:
    f.write("idx|URL|occurences\n")
    for idx, source in enumerate(TOP_SOURCES):
        if idx < 14:
            print(idx, source, TOP_SOURCES[source])
        f.write("{}|{}|{}\n".format(idx, source, TOP_SOURCES[source]))

print("--" * 20)

for source in TOP_SOURCES:
    try:
        domain = get_fld(source)

        if domain not in TOP_SOURCE_DOMAINS:
            TOP_SOURCE_DOMAINS[domain] = {}
            TOP_SOURCE_DOMAINS[domain]['occurrences'] = 0
            TOP_SOURCE_DOMAINS[domain]['scripts'] = 0
        TOP_SOURCE_DOMAINS[domain]['occurrences'] += 1
        TOP_SOURCE_DOMAINS[domain]['scripts'] += TOP_SOURCES[source]
    except:
        pass

print("Top 15 source domains with N source files: ")
TOP_SOURCE_DOMAINS = {k: v for k, v in sorted(TOP_SOURCE_DOMAINS.items(), key=lambda item: item[1]['occurrences'], reverse=True)}
with open(LOGPATH + os.sep + 'source_domains.csv', 'w') as f:
    f.write("idx|Domain|occurences|scripts\n")
    for idx, soure_domain in enumerate(TOP_SOURCE_DOMAINS):
        if idx < 14:
            print(idx, soure_domain, TOP_SOURCE_DOMAINS[soure_domain])
        f.write("{}|{}|{}|{}\n".format(idx, soure_domain, TOP_SOURCE_DOMAINS[soure_domain]['occurrences'], TOP_SOURCE_DOMAINS[soure_domain]['scripts']))

print("--" * 20)

print("Top 15 source filesnames: ")
TOP_FILENAMES = {k: v for k, v in sorted(TOP_FILENAMES.items(), key=lambda item: item[1], reverse=True)}
with open(LOGPATH + os.sep + 'source_filenames.csv', 'w') as f:
    f.write("idx|filename|occurences\n")
    for idx, filename in enumerate(TOP_FILENAMES):
        if idx < 14:
            print(idx, filename, TOP_FILENAMES[filename])
        f.write("{}|{}|{}\n".format(idx, filename, TOP_FILENAMES[filename]))

print("--" * 20)

print("Internal vs. Externally hosted scripts")

for dp in DATA:
    dp['internallyhosted_scripts_count'] = 0
    dp['externallyhosted_scripts_count'] = 0
    final_domain = get_fld(dp['url'])
    dp['final_domain'] = final_domain
    for source in dp['scripts']:
        if source == 'undefined' or source == 'null':
            continue
        try:
            source_domain = get_fld(source)
            if final_domain == source_domain:
                dp['internallyhosted_scripts_count'] += 1
            else:
                dp['externallyhosted_scripts_count'] +=1
        except:
            pass

INTERNALLYHOSTED_COUNT = 0
EXTERNALLYHOSTED_COUNT = 0
INTERNALLYHOSTED_ONLY = 0
EXTERNALLYHOSTED_ONLY = 0
MIXEDHOSTED = 0
with open(LOGPATH + os.sep + "source_internal_vs_external.csv", 'w') as f:
    f.write("final_domain|internallyhosted|externallyhosted\n")
    for dp in DATA:
        f.write("{}|{}|{}\n".format(dp['final_domain'], dp['internallyhosted_scripts_count'], dp['externallyhosted_scripts_count']))
        INTERNALLYHOSTED_COUNT += dp['internallyhosted_scripts_count']
        EXTERNALLYHOSTED_COUNT += dp['externallyhosted_scripts_count']

        if dp['internallyhosted_scripts_count'] > 0 and dp['externallyhosted_scripts_count'] == 0:
            INTERNALLYHOSTED_ONLY += 1
        elif dp['externallyhosted_scripts_count'] > 0 and dp['internallyhosted_scripts_count'] == 0:
            EXTERNALLYHOSTED_ONLY += 1
        elif dp['externallyhosted_scripts_count'] > 0 and dp['internallyhosted_scripts_count'] > 0:
            MIXEDHOSTED += 1

print("-> internally hosted scripts: ", INTERNALLYHOSTED_COUNT)
print("-> externally hosted scripts: ", EXTERNALLYHOSTED_COUNT)
print("-> internally only domains: ", INTERNALLYHOSTED_ONLY)
print("-> externally only domains: ", EXTERNALLYHOSTED_ONLY)
print("-> mixed hosted domains: ", MIXEDHOSTED)

print("--" * 20)

print("Top Function calls:")
CALLED_FUNCTIONS = {}

for dp in DATA:
    domain = dp['domain']
    for script in dp['scripts']:
        for call in dp['scripts'][script]['data']:
            try:
                the_call = "{}_{}".format(call['object'], call['functioncall'])
                if 'window.' in the_call:
                    the_call = the_call.replace("window.", "")
                if not the_call in CALLED_FUNCTIONS:
                    CALLED_FUNCTIONS[the_call] = {}
                    CALLED_FUNCTIONS[the_call]['count'] = 0
                    CALLED_FUNCTIONS[the_call]['domains'] = []
                CALLED_FUNCTIONS[the_call]['count'] += 1

                if domain not in CALLED_FUNCTIONS[the_call]['domains']:
                    CALLED_FUNCTIONS[the_call]['domains'].append(domain)
            except Exception as e:
                pass
                #print(e)
                #print(call, dp['domain'])

CALLED_FUNCTIONS = {k: v for k, v in sorted(CALLED_FUNCTIONS.items(), key=lambda item: item[1]['count'], reverse=True)}

with open(LOGPATH + os.sep + 'source_functioncalls.csv', 'w') as f:
    f.write("idx|functioncall|callcount|domaincount\n")
    for idx, functioncall in enumerate(CALLED_FUNCTIONS):
        if idx < 14:
            print(idx, functioncall, CALLED_FUNCTIONS[functioncall]['count'], len(CALLED_FUNCTIONS[functioncall]['domains']))
        f.write("{}|{}|{}|{}\n".format(idx, functioncall, CALLED_FUNCTIONS[functioncall]['count'], len(CALLED_FUNCTIONS[functioncall]['domains'])))

print("--" * 20)

print("Top objects:")
OBJECTS_USED = {}

for dp in DATA:
    domain = dp['domain']
    for script in dp['scripts']:
        for call in dp['scripts'][script]['data']:
            try:
                if not call['object'] in OBJECTS_USED:
                    OBJECTS_USED[call['object']] = {}
                    OBJECTS_USED[call['object']]['count'] = 0
                    OBJECTS_USED[call['object']]['domains'] = []
                OBJECTS_USED[call['object']]['count'] += 1

                if domain not in OBJECTS_USED[call['object']]['domains']:
                    OBJECTS_USED[call['object']]['domains'].append(domain)
            except Exception as e:
                pass

OBJECTS_USED = {k: v for k, v in sorted(OBJECTS_USED.items(), key=lambda item: item[1]['count'], reverse=True)}

with open(LOGPATH + os.sep + 'source_objects.csv', 'w') as f:
    f.write("idx|object|callcount\n")
    for idx, obj in enumerate(OBJECTS_USED):
        if idx < 14:
            print(idx, obj, OBJECTS_USED[obj]['count'], len(OBJECTS_USED[obj]['domains']))
        f.write("{}|{}|{}|{}\n".format(idx, obj, OBJECTS_USED[obj]['count'], len(OBJECTS_USED[obj]['domains'])))

print("--" * 20)
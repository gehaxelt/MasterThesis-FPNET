#!/usr/bin/env python3
import os 
import sys
import re
import json
from collections import OrderedDict
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

from utils import CATEGORY_MAPPING, AGGRO_CATS

if len(sys.argv) < 2:
    print("Usage: {} <LOGFOLDER>".format(sys.argv[0]))
    sys.exit(1)

LOGPATH = sys.argv[1]

if os.path.exists(LOGPATH + os.sep + 'scores.db'):
    os.unlink(LOGPATH + os.sep + 'scores.db')

from db import *

# Create categories: 
for category in CATEGORY_MAPPING.keys():
    fpcat = FPCategory(name = category, aggro= category in AGGRO_CATS)
    sql_session.add(fpcat)

sql_session.commit()

CATEGORY_CACHE = {}

insert_counter = 0 
with open(LOGPATH + os.sep +  "fpnet_scan.csv") as f:
    for line in f:
        line = json.loads(line)
        if line['origin'] != 'javascript' or line['action'] != 'log_score':
            continue

        # XXX: Focus only on entries with score >= 10
        if line['score'] < 10:
            continue

        try:
            domain_res = get_tld("https://{}".format(line['domain']),as_object=True)
        except Exception as e:
            print(e)
            continue

        fpscore = FPScore(
            trace_id = line['trace_id'],
            subdomain = domain_res.subdomain,
            domain = domain_res.fld,
            domain2 = domain_res.domain,
            tld = domain_res.tld,
            date = line['date'],
            loadtime = line['loadtime'],
            score = line['score'],
            coverage_entities = line['coverage_entities'],
            coverage_categories = line['coverage_categories'],
            aggressive_coverage = line['aggressive_coverage'],
            aggressive_categories = line['aggressive_categories'],
            script_origins_calls_cnt = line['script_origins_calls_cnt']
            )

        for category in line['fingerprint_categories'].split(";"):
            if category == '':
                continue
            if not category in CATEGORY_CACHE:
                CATEGORY_CACHE[category] = sql_session.query(FPCategory).filter(FPCategory.name == category).one()
            fpscore.categories.append(CATEGORY_CACHE[category])

        for script_origin in line['script_origins_calls'].keys():

            # check if we have a js file
            filename = script_origin.split('/')[-1]
            # if '?' in filename:
            #     filename = filename.split("?")[0]
            # if not '.js' in filename[-3:]:
            #     continue

            try:
                domain_res = get_tld(script_origin,as_object=True)
            except Exception as e:
                print(e)
                continue

            fpscriptorigin = FPScriptOrigin(
                idx = line['script_origins_calls'][script_origin]['idx'],
                url = script_origin,
                proto = domain_res.parsed_url.scheme,
                subdomain = domain_res.subdomain,
                domain = domain_res.fld,
                domain2 = domain_res.domain,
                tld = domain_res.tld,
                path = domain_res.parsed_url.path,
                filename = filename,
                score = 0,
                )

            script_origin_score = []
            for functioncall in line['script_origins_calls'][script_origin]['data']:
                if type(functioncall) != type({}):
                    continue
                fpscriptfunctioncall = FPScriptFunctionCall(
                    idx = functioncall['idx'],
                    gidx = functioncall['gidx'],
                    functioncall = functioncall['functioncall'],
                    obj = functioncall['object']
                )
                the_category = None
                for category in CATEGORY_MAPPING.keys():
                    if not functioncall['functioncall'] in CATEGORY_MAPPING[category]:
                        continue

                    if not category in CATEGORY_CACHE:
                        CATEGORY_CACHE[category] = sql_session.query(FPCategory).filter(FPCategory.name == category).one()
                    fpscriptfunctioncall.category = CATEGORY_CACHE[category]
                    the_category = category
                    break

                if the_category and not the_category in script_origin_score:
                    script_origin_score.append(the_category)

                fpscriptorigin.function_calls.append(fpscriptfunctioncall)

            fpscriptorigin.score = len(script_origin_score)

            fpscore.script_origins.append(fpscriptorigin)

        sql_session.add(fpscore)
        insert_counter += 1

        if insert_counter % 1000 == 0:
            print("Committing...")
            sql_session.commit()

sql_session.execute(text("""CREATE INDEX "1" ON "fpcategories" ( "id" )"""))
sql_session.execute(text("""CREATE INDEX "2" ON "fpscores" ( "id" )"""))
sql_session.execute(text("""CREATE INDEX "3" ON "fpscriptfunctioncalls" ( "id" )"""))
sql_session.execute(text("""CREATE INDEX "4" ON "fpscriptfunctioncalls" ( "category_id" )"""))
sql_session.execute(text("""CREATE INDEX "5" ON "fpscriptorigins" ( "id" )"""))
sql_session.execute(text("""CREATE INDEX "6" ON "fpscriptorigins" ( "filename" )"""))
sql_session.execute(text("""CREATE INDEX "20" ON "fpscriptorigins" ( "score" )"""))
sql_session.execute(text("""CREATE INDEX "7" ON "score_cat_association" ( "score_id", "cat_id" )"""))
sql_session.execute(text("""CREATE INDEX "8" ON "score_scriptorigin_association" ( "score_id", "scriptorigin_id" )"""))
sql_session.execute(text("""CREATE INDEX "9" ON "scriptorigin_scriptfunctioncall_association" ( "scriptorigin_id", "scriptfunctioncall_id" )"""))
sql_session.execute(text("""CREATE INDEX "10" ON "scriptorigin_scriptfunctioncall_association" ( "scriptorigin_id" )"""))
sql_session.execute(text("""CREATE INDEX "11" ON "scriptorigin_scriptfunctioncall_association" ( "scriptfunctioncall_id" )"""))
sql_session.execute(text("""CREATE INDEX "12" ON "fpcategories" ( "aggro" )"""))
sql_session.execute(text("""CREATE INDEX "13" ON "fpcategories" ( "name" )"""))
sql_session.execute(text("""CREATE INDEX "14" ON "fpscores" ( "domain" )"""))
sql_session.execute(text("""CREATE INDEX "15" ON "fpscriptorigins" ( "domain" )"""))
sql_session.execute(text("""CREATE INDEX "16" ON "score_cat_association" ( "score_id" )"""))
sql_session.execute(text("""CREATE INDEX "17" ON "score_cat_association" ( "cat_id" )"""))
sql_session.execute(text("""CREATE INDEX "18" ON "score_scriptorigin_association" ( "score_id" )"""))
sql_session.execute(text("""CREATE INDEX "19" ON "score_scriptorigin_association" ( "scriptorigin_id" )"""))

sql_session.commit()

print(sql_session.query(FPScore).count())

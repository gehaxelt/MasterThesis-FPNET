#!/usr/bin/env python3
import os 
import sys
import re
import json
import csv
from collections import OrderedDict
try:
    import tld 
except:
    print("Install using: pip3 install --user tld")
    sys.exit(1)

from tld import get_fld, get_tld
from tld.utils import update_tld_names
try:
    pass
    #update_tld_names()
except Exception as e:
    print(e)

from utils import CATEGORY_MAPPING, AGGRO_CATS

if len(sys.argv) < 2:
    print("Usage: {} <LOGFOLDER>".format(sys.argv[0]))
    sys.exit(1)

stdoutcsv = csv.writer(sys.stdout)
LOGPATH = sys.argv[1]
LIMIT = "LIMIT 25"
LIMIT = "LIMIT 15"
LIMIT = ""


def print_headline(headline):
    print("#" * 50)
    print("#")
    print("# {}".format(headline))
    print("#")
    print("#" * 50)

def query2csv(query, csv_writer=stdoutcsv):
    result  = sql_session.execute(text(query))
    csv_writer.writerow(result.keys())
    csv_writer.writerows(result.fetchall())

def split_limit():
    try:
        the_limit = LIMIT.split(" ")[1]
    except:
        the_limit = "unlimited"
    return the_limit

def name2csvwriter(filename):
    if not os.path.exists(LOGPATH + os.sep + "paper_query"):
        os.mkdir(LOGPATH + os.sep + "paper_query")

    the_limit = split_limit()

    return csv.writer(open(LOGPATH + os.sep + "paper_query" + os.sep + filename + "_" + the_limit + ".csv", "w"))

def peak(filename):
    the_limit = split_limit()
    with open(LOGPATH + os.sep + "paper_query" + os.sep + filename + "_" + the_limit + ".csv") as f:
        try:
            for i in range(11):
                l = f.readline()
                if l != "":
                    print(l, end='')
        except:
            pass

from db import *

# Data pre-processing
# - We ignore all sites that have score < 10
# - We ignore all source files that do not have a '.js' file ending
# - We ignore all source files that do not have a domain, but i.e. are hosted on a IP address
# - We ignore all calls that are not a dictionary.

# ==========================================================
# =================== Q0 questions with aggro = Don't care
# ==========================================================

# Question 0:
# Question 0 is about some general information about the data:
# a) AVG of all script's scores (categories)
# b) STDEV of all script's scores (categories)
# c) AVG+STDEV the scores per script (categories)
# d) Links to all scripts
# e) MAD ( mean(absolute(data - mean(data))) ) for all script scores
# f) (unique) domain count
# g) (unique) script count

q0_a = """
SELECT AVG(score) FROM (
    SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
    JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
    JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
    JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
    GROUP BY fpscriptorigins.filename
    ORDER BY score DESC
    {LIMIT}
)
""".format(LIMIT=LIMIT)

print_headline("Q0: a) AVG of the scores per script")
query2csv(q0_a, name2csvwriter("q0_a"))
peak("q0_a")

q0_b = """
SELECT STDEV(score) FROM (
    SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
    JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
    JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
    JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
    GROUP BY fpscriptorigins.filename
    ORDER BY score DESC
    {LIMIT}
)
""".format(LIMIT=LIMIT)

print_headline("Q0: b) STDEV of the scores per script")
query2csv(q0_b, name2csvwriter("q0_b"))
peak("q0_b")

q0_c = """
SELECT stdev+avg FROM (
    SELECT STDEV(score) as stdev, AVG(score) as avg FROM (
        SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
        JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
        GROUP BY fpscriptorigins.filename
        ORDER BY score DESC
        {LIMIT}
    )
)
""".format(LIMIT=LIMIT)

print_headline("Q0: c) AVG+STDEV the scores per script (categories)")
query2csv(q0_c, name2csvwriter("q0_c"))
peak("q0_c")

q0_d = """
SELECT DISTINCT url, domain, path, filename from fpscriptorigins
JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
ORDER BY filename
{LIMIT}
""".format(LIMIT=LIMIT)

print_headline("Q0: d) Links to all scripts")
query2csv(q0_d, name2csvwriter("q0_d"))
peak("q0_d")

q0_e = """
SELECT avg(d) as MAD FROM (
    SELECT abs(score - avg(score) over ()) as d FROM (
        SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
        JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
        GROUP BY fpscriptorigins.filename
        ORDER BY score DESC
        {LIMIT}
    )
)
""".format(LIMIT=LIMIT)
print_headline("Q0: e) MAD of the scores per script")
query2csv(q0_e, name2csvwriter("q0_e"))
peak("q0_e")

q0_f = """
select count(domain) as all_domain_entries, count(distinct domain) as unique_domains from fpscores;
""".format(LIMIT=LIMIT)
print_headline("Q0: f) (unique) domain count")
query2csv(q0_f, name2csvwriter("q0_f"))
peak("q0_f")


q0_g = """
select count(url) as all_script_entries, count(distinct url) as unique_urls from fpscriptorigins;
""".format(LIMIT=LIMIT)
print_headline("Q0: g) (unique) script count")
query2csv(q0_g, name2csvwriter("q0_g"))
peak("q0_g")

# ==========================================================
# =================== Q0 questions with aggro = True
# ==========================================================


q0_a_aggro = """
SELECT AVG(score) FROM (
    SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
    JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
    JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
    JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
    WHERE fpcategories.aggro = True
    GROUP BY fpscriptorigins.filename
    ORDER BY score DESC
    {LIMIT}
)
""".format(LIMIT=LIMIT)

print_headline("Q0/aggro: a) AVG of the scores per script")
query2csv(q0_a_aggro, name2csvwriter("q0_a_aggro"))
peak("q0_a_aggro")


q0_b_aggro = """
SELECT STDEV(score) FROM (
    SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
    JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
    JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
    JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
    WHERE fpcategories.aggro = True
    GROUP BY fpscriptorigins.filename
    ORDER BY score DESC
    {LIMIT}
)
""".format(LIMIT=LIMIT)

print_headline("Q0/aggro: b) STDEV of the scores per script")
query2csv(q0_b_aggro, name2csvwriter("q0_b_aggro"))
peak("q0_b_aggro")

q0_c_aggro = """
SELECT stdev+avg FROM (
    SELECT STDEV(score) as stdev, AVG(score) as avg FROM (
        SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
        JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
        WHERE fpcategories.aggro = True
        GROUP BY fpscriptorigins.filename
        ORDER BY score DESC
        {LIMIT}
    )
)
""".format(LIMIT=LIMIT)

print_headline("Q0/aggro: c) AVG+STDEV the scores per script (categories)")
query2csv(q0_c_aggro, name2csvwriter("q0_c_aggro"))
peak("q0_c_aggro")

q0_d_aggro = """
SELECT DISTINCT url, domain, path, filename from fpscriptorigins
JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
WHERE fpcategories.aggro = True
ORDER BY filename
{LIMIT}
""".format(LIMIT=LIMIT)

print_headline("Q0/aggro: d) Links to all scripts")
query2csv(q0_d_aggro, name2csvwriter("q0_d_aggro"))
peak("q0_d_aggro")

q0_e_aggro = """
SELECT avg(d) as MAD FROM (
    SELECT abs(score - avg(score) over ()) as d FROM (
        SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as score FROM fpscriptorigins 
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
        JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
        WHERE fpcategories.aggro = True
        GROUP BY fpscriptorigins.filename
        ORDER BY score DESC
        {LIMIT}
    )
)
""".format(LIMIT=LIMIT)
print_headline("Q0/aggro: e) MAD of the scores per script")
query2csv(q0_e_aggro, name2csvwriter("q0_e_aggro"))
peak("q0_e_aggro")

# # ==========================================================
# # =================== Q1 questions with aggro = Don't care
# # ==========================================================

# # Question 1: 
# # For Question 1, we want:
# # - a) a list of scripts that have as many categories as possible, sorted by category count
# # - b) a list of most used scripts (instances)
# # - c) a list of scripts with weighted scores (categories count * instances)
# # - d) a list of scripts sorted by their max categories, but with all their score-varieties and source domains
# # - e) a list of scripts grouped by their category call stack signature

# q1_a = """
# SELECT ROW_NUMBER() OVER (ORDER BY category_count DESC) rank, * FROM (
#     SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as category_count, GROUP_CONCAT(DISTINCT fpcategories.name) FROM fpscriptorigins 
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#     GROUP BY fpscriptorigins.filename
#     ORDER BY category_count DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q1: a) a list of scripts that have as many categories as possible, sorted by category count")
# query2csv(q1_a, name2csvwriter("q1_a"))
# peak("q1_a")


# q1_b = """
# SELECT ROW_NUMBER() OVER (ORDER BY instances DESC, score DESC) rank, * FROM (
#     SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#     GROUP BY fpscriptorigins.filename
#     ORDER BY instances DESC, score DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q1: b) a list of most used scripts (instances) sorted by instances")
# query2csv(q1_b, name2csvwriter("q1_b_sorted_instances"))
# peak("q1_b_sorted_instances")

# q1_b_sorted_score = """
# SELECT ROW_NUMBER() OVER (ORDER BY score DESC, instances DESC) rank, * FROM (
#     SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#     GROUP BY fpscriptorigins.filename
#     ORDER BY score DESC, instances DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q1: b2) a list of most used scripts (instances) sorted by score")
# query2csv(q1_b_sorted_score, name2csvwriter("q1_b_sorted_score"))
# peak("q1_b_sorted_score")


# q1_c = """
# SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#     SELECT filename, power(score,2)*instances as fpscore, instances, score, categories FROM (
#         SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#         JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#         JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#         JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#         GROUP BY fpscriptorigins.filename
#         ORDER BY instances DESC, score DESC
#     )
#     ORDER BY fpscore DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q1: c) a list of scripts with weighted scores (categories count * instances)")
# query2csv(q1_c, name2csvwriter("q1_c"))
# peak("q1_c")

# q1_d = """
# SELECT source_filename, max(sub_cat_cnt) as cat_max, count(source_filename) as variety_cnt, GROUP_CONCAT(sub_cat_cnt), GROUP_CONCAT(source_domains, "|") FROM (
#     SELECT sub_source_filename as source_filename, sub_cat_cnt, sub_categories, GROUP_CONCAT(DISTINCT sub_source_domain) as source_domains, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
#         SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#         JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#         JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#         JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#         GROUP BY fpscriptorigins.id
#         ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
#         )
#     GROUP BY sub_source_filename, sub_cat_cnt
#     ORDER BY sub_source_filename, sub_cat_cnt DESC
#     )
# GROUP BY source_filename
# ORDER BY cat_max DESC, variety_cnt DESC
# {LIMIT}
# """.format(LIMIT=LIMIT)
# print_headline("Q1: d) a list of scripts sorted by their max categories, but with all their score-varieties and source domains")
# query2csv(q1_d, name2csvwriter("q1_d"))
# peak("q1_d")


# q1_e = """
# SELECT score, cat_cnt, COUNT(script_id) as source_includes_cnt, cat_signature, domain as source_domain, filename FROM (
#     SELECT script_id, filename, domain, GROUP_CONCAT(fpc_name) as cat_signature, COUNT(fpc_name) as cat_cnt, COUNT(DISTINCT fpc_name) as score FROM (
#         SELECT fpscriptorigins.id as script_id, filename, domain, fpscriptfunctioncalls.id as scfc_id, fpcategories.name as fpc_name from fpscriptorigins
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#         JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
#         ORDER BY fpscriptorigins.id
#         )
#     GROUP BY script_id
#     )
# GROUP BY cat_signature
# ORDER BY score DESC, source_includes_cnt DESC, cat_cnt DESC
# {LIMIT}
# """.format(LIMIT=LIMIT)
# print_headline("Q1: e) a list of scripts grouped by their category call stack signature")
# query2csv(q1_e, name2csvwriter("q1_e"))
# peak("q1_e")

# # ==========================================================
# # =================== Q1 questions with aggro = True
# # ==========================================================

# q1_a_aggro = """
# SELECT ROW_NUMBER() OVER (ORDER BY category_count DESC) rank, * FROM (
#     SELECT fpscriptorigins.filename AS fpscriptorigin_filename, COUNT(DISTINCT fpcategories.name) as category_count, GROUP_CONCAT(DISTINCT fpcategories.name) FROM fpscriptorigins 
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#     WHERE fpcategories.aggro = True
#     GROUP BY fpscriptorigins.filename
#     ORDER BY category_count DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q1/aggro: a) a list of scripts that have as many categories as possible, sorted by category count")
# query2csv(q1_a_aggro, name2csvwriter("q1_a_aggro"))
# peak("q1_a_aggro")

# q1_b_aggro = """
# SELECT ROW_NUMBER() OVER (ORDER BY instances DESC, score DESC) rank, * FROM (
#     SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#     WHERE fpcategories.aggro = True
#     GROUP BY fpscriptorigins.filename
#     ORDER BY instances DESC, score DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q1/aggro: b) a list of most used scripts (instances)")
# query2csv(q1_b_aggro, name2csvwriter("q1_b_aggro"))
# peak("q1_b_aggro")

# q1_c_aggro = """
# SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#     SELECT filename, power(score,2)*instances as fpscore, instances, score, categories FROM (
#         SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#         JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#         JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#         JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#         WHERE fpcategories.aggro = True
#         GROUP BY fpscriptorigins.filename
#         ORDER BY instances DESC, score DESC
#     )
#     ORDER BY fpscore DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q1/aggro: c) a list of scripts with weighted scores (categories count * instances)")
# query2csv(q1_c_aggro, name2csvwriter("q1_c_aggro"))
# peak("q1_c_aggro")


# q1_d_aggro = """
# SELECT source_filename, max(sub_cat_cnt) as cat_max, count(source_filename) as variety_cnt, GROUP_CONCAT(sub_cat_cnt), GROUP_CONCAT(source_domains, "|") FROM (
#     SELECT sub_source_filename as source_filename, sub_cat_cnt, sub_categories, GROUP_CONCAT(DISTINCT sub_source_domain) as source_domains, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
#         SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#         JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#         JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#         JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#         WHERE fpcategories.aggro = True
#         GROUP BY fpscriptorigins.id
#         ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
#         )
#     GROUP BY sub_source_filename, sub_cat_cnt
#     ORDER BY sub_source_filename, sub_cat_cnt DESC
#     )
# GROUP BY source_filename
# ORDER BY cat_max DESC, variety_cnt DESC
# {LIMIT}
# """.format(LIMIT=LIMIT)
# print_headline("Q1: d) a list of scripts sorted by their max categories, but with all their score-varieties and source domains")
# query2csv(q1_d_aggro, name2csvwriter("q1_d_aggro"))
# peak("q1_d_aggro")


# q1_e_aggro = """
# SELECT score, cat_cnt, COUNT(script_id) as source_includes_cnt, cat_signature, domain as source_domain, filename FROM (
#     SELECT script_id, filename, domain, GROUP_CONCAT(fpc_name) as cat_signature, COUNT(fpc_name) as cat_cnt, COUNT(DISTINCT fpc_name) as score FROM (
#         SELECT fpscriptorigins.id as script_id, filename, domain, fpscriptfunctioncalls.id as scfc_id, fpcategories.name as fpc_name from fpscriptorigins
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#         JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
#         WHERE fpcategories.aggro = True
#         ORDER BY fpscriptorigins.id
#         )
#     GROUP BY script_id
#     )
# GROUP BY cat_signature
# ORDER BY score DESC, source_includes_cnt DESC, cat_cnt DESC
# {LIMIT}
# """.format(LIMIT=LIMIT)
# print_headline("Q1: e) a list of scripts grouped by their category call stack signature")
# query2csv(q1_e_aggro, name2csvwriter("q1_e_aggro"))
# peak("q1_e_aggro")

# # ==========================================================
# # =================== Q2 questions with aggro = Don't care
# # ==========================================================

# # Question 2: Actors
# # For question 2, we have:
# # - a) what are the most common source domains by script includes? 
# # - b) what are the most common source domains by web domains? 
# # - c) what are the most common source domains by score? 
# # - d) What source domains do the "badest" scripts have? 
# # // -f) What are the weighted source domains?  
# # - e) Are there any clusters/groups? 

# q2_a = """
# SELECT ROW_NUMBER() OVER (ORDER BY cnt DESC) rank, * FROM (
#     SELECT fpscriptorigins.domain, count(fpscriptorigins.id) as cnt from fpscriptorigins
#     GROUP BY fpscriptorigins.domain
#     ORDER BY cnt DESC
# )
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q2: a) what are the most common source domains by script includes? ")
# query2csv(q2_a, name2csvwriter("q2_a"))
# peak("q2_a")


# q2_b = """
# SELECT ROW_NUMBER() OVER (ORDER BY site_domains DESC) rank, * FROM (
#     SELECT fpscriptorigins.domain as source_domain, count(DISTINCT fpscores.domain) as site_domains from fpscriptorigins
#     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#     GROUP BY source_domain
#     ORDER BY site_domains DESC
# )
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q2: b) what are the most common source domains by web domains?")
# query2csv(q2_b, name2csvwriter("q2_b"))
# peak("q2_b")


# q2_c = """
# SELECT ROW_NUMBER() OVER (ORDER BY score DESC) rank, * FROM (
#     SELECT fpscriptorigins.domain, count(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#     JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
#     GROUP BY fpscriptorigins.domain
#     ORDER BY score DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q2: c) What are the most common source domains by score?")
# query2csv(q2_c, name2csvwriter("q2_c"))
# peak("q2_c")

# q2_d = """
# SELECT rank, fpscriptorigins.filename, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#     SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#         SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#             SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#             JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#             JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#             JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#             JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#             JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
            
#             GROUP BY fpscriptorigins.filename
#             ORDER BY instances DESC, score DESC
#         )
#         ORDER BY fpscore DESC
#         {LIMIT}
#     )
# ) AS aggregatedTable
# JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
# GROUP BY fpscriptorigins.filename, source_domain
# ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
# """.format(LIMIT=LIMIT)

# print_headline("Q2: d) What source domains do the \"badest\" scripts have? ")
# query2csv(q2_d, name2csvwriter("q2_d"))
# peak("q2_d")


# # ==========================================================
# # =================== Q2 questions with aggro = True
# # ==========================================================

# q2_a_aggro = """
# SELECT ROW_NUMBER() OVER (ORDER BY cnt DESC) rank, * FROM (
#     SELECT fpscriptorigins.domain, count(DISTINCT fpscriptorigins.id) as cnt from fpscriptorigins
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#     JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
#     WHERE fpcategories.aggro = True
#     GROUP BY fpscriptorigins.domain
#     ORDER BY cnt DESC
# )
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q2/aggro: a) what are the most common source domains by script includes? ")
# query2csv(q2_a_aggro, name2csvwriter("q2_a_aggro"))
# peak("q2_a_aggro")


# q2_b_aggro = """
# SELECT ROW_NUMBER() OVER (ORDER BY site_domains DESC) rank, * FROM (
#     SELECT fpscriptorigins.domain as source_domain, count(DISTINCT fpscores.domain) as site_domains from fpscriptorigins
#     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#     JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
#     WHERE fpcategories.aggro = True
#     GROUP BY source_domain
#     ORDER BY site_domains DESC
# )
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q2/aggro: b) what are the most common source domains by web domains?")
# query2csv(q2_b_aggro, name2csvwriter("q2_b_aggro"))
# peak("q2_b_aggro")

# q2_c_aggro = """
# SELECT ROW_NUMBER() OVER (ORDER BY score DESC) rank, * FROM (
#     SELECT fpscriptorigins.domain, count(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins
#     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#     JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
#     WHERE fpcategories.aggro = True
#     GROUP BY fpscriptorigins.domain
#     ORDER BY score DESC)
# {LIMIT};
# """.format(LIMIT=LIMIT)

# print_headline("Q2/aggro: c) What are the most common source domains by score?")
# query2csv(q2_c_aggro, name2csvwriter("q2_c_aggro"))
# peak("q2_c_aggro")


# q2_d_aggro = """
# SELECT rank, fpscriptorigins.filename, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#     SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#         SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#             SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#             JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#             JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#             JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#             JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#             JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#             WHERE fpcategories.aggro = True 
#             GROUP BY fpscriptorigins.filename
#             ORDER BY instances DESC, score DESC
#         )
#         ORDER BY fpscore DESC
#         {LIMIT}
#     )
# ) AS aggregatedTable
# JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
# GROUP BY fpscriptorigins.filename, source_domain
# ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
# """.format(LIMIT=LIMIT)

# print_headline("Q2/aggro: d) What source domains do the \"badest\" scripts have? ")
# query2csv(q2_d_aggro, name2csvwriter("q2_d_aggro"))
# peak("q2_d_aggro")


# # ==========================================================
# # =================== Q3 questions with aggro = Don't care
# # ==========================================================

# # Question 3: Actor's Visibilty / Networks
# # For question 3, we have:
# # - a) Find site domains for which: script source + script filename of the top badest scripts is the same
# # - b) Find site domains for which: script source + script path + script filename of the top badest scripts is the same
# # - c) Find site domains for which: script source + script filename + script score is the same
# # - d) ==> For each question: What kind of site is that? Politics/Journalism/Porn/Banking/etc? 
# # 
# # XXX: Maybe Q2 based on Q1.


# q3_a = """
# SELECT rank, fpscore, source_domain, source_file, count(DISTINCT fpscores.domain) as fped_domains_cnt, GROUP_CONCAT(DISTINCT fpscores.domain) as fped_domains FROM (
#     SELECT rank, fpscriptorigins.id as source_id, fpscriptorigins.filename as source_file, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#         SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#             SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#                 SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#                 JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#                 JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#                 JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#                 JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#                 JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#                 GROUP BY fpscriptorigins.filename
#                 ORDER BY instances DESC, score DESC
#             )
#             ORDER BY fpscore DESC
#             {LIMIT}
#         )
#     ) AS aggregatedTable
#     JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
#     GROUP BY fpscriptorigins.filename, source_domain
#     ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
# ) 
# JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE filename = source_file AND domain = source_domain)
# JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
# JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
# GROUP BY source_domain, source_file
# ORDER BY rank, fped_domains_cnt DESC
# """.format(LIMIT=LIMIT)

# print_headline("Q3  a) Find site domains for which: script source + script filename of the top badest scripts")
# query2csv(q3_a, name2csvwriter("q3_a"))
# peak("q3_a")

# q3_b = """
# SELECT rank, fpscore, source_domain, source_path, source_file, count(DISTINCT fpscores.domain) as fped_domains_cnt, GROUP_CONCAT(DISTINCT fpscores.domain) as fped_domains FROM (
#     SELECT rank, fpscriptorigins.path as source_path, fpscriptorigins.filename as source_file, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#         SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#             SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#                 SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#                 JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#                 JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#                 JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#                 JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#                 JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#                 GROUP BY fpscriptorigins.filename
#                 ORDER BY instances DESC, score DESC
#             )
#             ORDER BY fpscore DESC
#             {LIMIT}
#         )
#     ) AS aggregatedTable
#     JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
#     GROUP BY fpscriptorigins.filename, source_domain
#     ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
# ) 
# JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE domain = source_domain AND path = source_path AND filename = source_file)
# JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
# JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
# GROUP BY source_domain, source_path, source_file
# ORDER BY rank, fped_domains_cnt DESC
# """.format(LIMIT=LIMIT)

# print_headline("Q3  b) Find site domains for which: script source + script path + script filename of the top badest scripts is the same")
# query2csv(q3_b, name2csvwriter("q3_b"))
# peak("q3_b")

# # q3_c = """
# # SELECT source_domain, source_filename, cat_cnt, categories, COUNT(score_domain) as fped_domains_count, GROUP_CONCAT(score_domain) as fped_domains FROM (
# #     SELECT fpscores.domain as score_domain, filename as source_filename, fpscriptorigins.domain as source_domain, count(DISTINCT fpcategories.id) as cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins
# #     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
# #     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
# #     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
# #     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
# #     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
# #     GROUP BY fpscriptorigins.id
# #     ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, cat_cnt DESC
# #     )
# # GROUP BY source_domain, source_filename, cat_cnt
# # ORDER BY source_domain, source_filename, cat_cnt DESC
# # """

# q3_c = """
# SELECT source_domain, source_file, sub_cat_cnt, sub_categories, sub_fped_domains_count, sub_fped_domains FROM (
#     SELECT rank, fpscore, source_domain, source_file, count(DISTINCT fpscores.domain) as fped_domains_cnt, GROUP_CONCAT(DISTINCT fpscores.domain) as fped_domains FROM (
#         SELECT rank, fpscriptorigins.id as source_id, fpscriptorigins.filename as source_file, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#             SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#                 SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#                     SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#                     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#                     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#                     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#                     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#                     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#                     GROUP BY fpscriptorigins.filename
#                     ORDER BY instances DESC, score DESC
#                 )
#                 ORDER BY fpscore DESC
#             )
#         ) AS aggregatedTable
#         JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
#         GROUP BY fpscriptorigins.filename, source_domain
#         ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
#     )
#     JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE filename = source_file AND domain = source_domain)
#     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#     GROUP BY source_domain, source_file
#     ORDER BY rank
# ) 
# JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE filename = source_file AND domain = source_domain)
# JOIN (
#     SELECT sub_source_domain, sub_source_filename, sub_cat_cnt, sub_categories, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
#         SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#         JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#         JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#         JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#         GROUP BY fpscriptorigins.id
#         ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
#         )
#     GROUP BY sub_source_domain, sub_source_filename, sub_cat_cnt
#     ORDER BY sub_source_domain, sub_source_filename, sub_cat_cnt DESC
# ) ON fpscriptorigins.filename = sub_source_filename AND fpscriptorigins.domain = sub_source_domain
# GROUP BY source_domain, sub_cat_cnt
# ORDER BY sub_fped_domains_count DESC
# """.format(LIMIT=LIMIT)

# print_headline("Q3  c) Find site domains for which: script source + script filename + script score per script is the same on the top badest domains")
# query2csv(q3_c, name2csvwriter("q3_c"))
# peak("q3_c")


# # ==========================================================
# # =================== Q3 questions with aggro = True
# # ==========================================================
# # 
# q3_a_aggro = """
# SELECT rank, fpscore, source_domain, source_file, count(DISTINCT fpscores.domain) as fped_domains_cnt, GROUP_CONCAT(DISTINCT fpscores.domain) as fped_domains FROM (
#     SELECT rank, fpscriptorigins.id as source_id, fpscriptorigins.filename as source_file, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#         SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#             SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#                 SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#                 JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#                 JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#                 JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#                 JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#                 JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#                 WHERE fpcategories.aggro = True 
#                 GROUP BY fpscriptorigins.filename
#                 ORDER BY instances DESC, score DESC
#             )
#             ORDER BY fpscore DESC
#             {LIMIT}
#         )
#     ) AS aggregatedTable
#     JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
#     GROUP BY fpscriptorigins.filename, source_domain
#     ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
# ) 
# JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE filename = source_file AND domain = source_domain)
# JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
# JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
# GROUP BY source_domain, source_file
# ORDER BY rank
# """.format(LIMIT=LIMIT)

# print_headline("Q3/aggro  a) Find site domains for which: script source + script filename of the top badest scripts")
# query2csv(q3_a_aggro, name2csvwriter("q3_a_aggro"))
# peak("q3_a_aggro")


# q3_b_aggro = """
# SELECT rank, fpscore, source_domain, source_path, source_file, count(DISTINCT fpscores.domain) as fped_domains_cnt, GROUP_CONCAT(DISTINCT fpscores.domain) as fped_domains FROM (
#     SELECT rank, fpscriptorigins.path as source_path, fpscriptorigins.filename as source_file, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#         SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#             SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#                 SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#                 JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#                 JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#                 JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#                 JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#                 JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#                 WHERE fpcategories.aggro = True 
#                 GROUP BY fpscriptorigins.filename
#                 ORDER BY instances DESC, score DESC
#             )
#             ORDER BY fpscore DESC
#             {LIMIT}
#         )
#     ) AS aggregatedTable
#     JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
#     GROUP BY fpscriptorigins.filename, source_domain
#     ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
# ) 
# JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE domain = source_domain AND path = source_path AND filename = source_file)
# JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
# JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
# GROUP BY source_domain, source_path, source_file
# ORDER BY rank
# """.format(LIMIT=LIMIT)

# print_headline("Q3/aggro  b) Find site domains for which: script source + script path + script filename of the top badest scripts is the same")
# query2csv(q3_b_aggro, name2csvwriter("q3_b_aggro"))
# peak("q3_b_aggro")


# q3_c = """
# SELECT source_domain, source_file, sub_cat_cnt, sub_categories, sub_fped_domains_count, sub_fped_domains FROM (
#     SELECT rank, fpscore, source_domain, source_file, count(DISTINCT fpscores.domain) as fped_domains_cnt, GROUP_CONCAT(DISTINCT fpscores.domain) as fped_domains FROM (
#         SELECT rank, fpscriptorigins.id as source_id, fpscriptorigins.filename as source_file, fpscriptorigins.domain as source_domain, count(DISTINCT fpscriptorigins.id) as source_includes, instances, fpscore FROM (
#             SELECT ROW_NUMBER() OVER (ORDER BY fpscore DESC) rank, * FROM (
#                 SELECT power(score,2)*instances as fpscore, instances, filename FROM (
#                     SELECT fpscriptorigins.filename AS filename, COUNT(DISTINCT fpscores.domain) as instances,  COUNT(DISTINCT fpcategories.name) as score, GROUP_CONCAT(DISTINCT fpcategories.name) as categories FROM fpscriptorigins 
#                     JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id 
#                     JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id 
#                     JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#                     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#                     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id 
#                     WHERE fpcategories.aggro = True 
#                     GROUP BY fpscriptorigins.filename
#                     ORDER BY instances DESC, score DESC
#                 )
#                 ORDER BY fpscore DESC
#             )
#         ) AS aggregatedTable
#         JOIN fpscriptorigins ON fpscriptorigins.filename = aggregatedTable.filename
#         GROUP BY fpscriptorigins.filename, source_domain
#         ORDER BY fpscore DESC, source_includes DESC, source_domain ASC
#     )
#     JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE filename = source_file AND domain = source_domain)
#     JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#     JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#     GROUP BY source_domain, source_file
#     ORDER BY rank
# ) 
# JOIN fpscriptorigins ON fpscriptorigins.id IN (SELECT id from fpscriptorigins WHERE filename = source_file AND domain = source_domain)
# JOIN (
#     SELECT sub_source_domain, sub_source_filename, sub_cat_cnt, sub_categories, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
#         SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
#         JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
#         JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
#         JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
#         JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
#         JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
#         WHERE fpcategories.aggro = True 
#         GROUP BY fpscriptorigins.id
#         ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
#         )
#     GROUP BY sub_source_domain, sub_source_filename, sub_cat_cnt
#     ORDER BY sub_source_domain, sub_source_filename, sub_cat_cnt DESC
# ) ON fpscriptorigins.filename = sub_source_filename AND fpscriptorigins.domain = sub_source_domain
# GROUP BY source_domain, sub_cat_cnt
# ORDER BY sub_fped_domains_count DESC
# """.format(LIMIT=LIMIT)

# print_headline("Q3/aggro  c) Find site domains for which: script source + script filename + script score per script is the same on the top badest domains")
# query2csv(q3_c, name2csvwriter("q3_c"))
# peak("q3_c")


# ==========================================================
# =================== Q4 questions with aggro = Don't care
# ==========================================================

# Question 4: Further analysis/data for the paper
# For question 4, we have:
# - a) script-signature-table -> table with signatures and their script_score,affected_domains_cnt,sources_cnt,sources_domains_cnt,sources_filenames_cnt,cat_signature,affected_domains,sources,source_domains,source_filenames
# - b) all_script_signatures-with-pages -> Signatures for ALL scripts and the pages they are on: id,domain,script_id,script_score,filename,script_domain,script_signature
# - b2) all_script_signatures -> Same as b), but without pages.
# - c) script-based signatures for all pages: id,domain,score,page_signature
# - d) Score list with the amount of source files, affected domains
# - e) Script Origin table with: script_domain, script_domain_cnt, avg_score, stdev_score, script_files_cnt, script_files, affected_websites_cnt, affected_websites for ever script_domain

q4_a = """
SELECT * FROM (
    SELECT script_score , count(DISTINCT fpscores.domain) as affected_domains_cnt, count(distinct script_domain || ":" || filename) as sources_cnt, count(distinct script_domain) as sources_domains_cnt, count(distinct filename) as sources_filenames_cnt, cat_signature, GROUP_CONCAT(DISTINCT fpscores.domain) as affected_domains, group_concat(distinct script_domain || ":" || filename) as sources, group_concat(DISTINCT script_domain) as source_domains, group_concat(DISTINCT filename) as source_filenames FROM (
        SELECT script_id, filename, script_domain, GROUP_CONCAT(fpc_name, ";") as cat_signature, COUNT(fpc_name) as cat_cnt, COUNT(DISTINCT fpc_name) as script_score FROM (
            SELECT fpscriptorigins.id as script_id, filename, domain as script_domain, fpscriptfunctioncalls.id as scfc_id, fpcategories.name as fpc_name from fpscriptorigins
            JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
            JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
            JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
            ORDER BY fpscriptorigins.id
            )
        GROUP BY script_id
        HAVING script_score  > 0
    )
    JOIN score_scriptorigin_association ON score_scriptorigin_association.scriptorigin_id = script_id
    JOIN fpscores ON score_scriptorigin_association.score_id = fpscores.id
    GROUP BY cat_signature
    HAVING affected_domains_cnt > 1
    ORDER BY affected_domains_cnt DESC
)
GROUP BY cat_signature
HAVING sources_cnt > 1
ORDER BY sources_cnt DESC, sources_domains_cnt DESC
"""
print_headline("Q4 a) script-signature-table")
query2csv(q4_a, name2csvwriter("q4_a"))
peak("q4_a")

q4_b = """
WITH script_signatures as (
    SELECT script_id, COUNT(DISTINCT fpc_name) as script_score, filename, script_domain, GROUP_CONCAT(fpc_name, ";") as script_signature FROM (
        SELECT fpscriptorigins.id as script_id, filename, domain as script_domain, fpscriptfunctioncalls.id as scfc_id, fpscriptfunctioncalls.idx as scfc_idx, fpcategories.name as fpc_name from fpscriptorigins
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
        JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
        ORDER BY fpscriptorigins.id, fpscriptfunctioncalls.idx
        )
    GROUP BY script_id
    ORDER BY script_id
)
SELECT id, domain, script_signatures.* from fpscores
JOIN score_scriptorigin_association ON score_scriptorigin_association.score_id = id
JOIN script_signatures ON script_signatures.script_id = score_scriptorigin_association.scriptorigin_id
ORDER BY id 
"""
print_headline("Q4 b) all_script_signatures-with-pages")
query2csv(q4_b, name2csvwriter("q4_b"))
peak("q4_b")

q4_b2 = """
WITH script_signatures as (
    SELECT script_id, COUNT(DISTINCT fpc_name) as script_score, filename, script_domain, GROUP_CONCAT(fpc_name, ";") as script_signature FROM (
        SELECT fpscriptorigins.id as script_id, filename, domain as script_domain, fpscriptfunctioncalls.id as scfc_id, fpscriptfunctioncalls.idx as scfc_idx, fpcategories.name as fpc_name from fpscriptorigins
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
        JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
        ORDER BY fpscriptorigins.id, fpscriptfunctioncalls.idx
        )
    GROUP BY script_id
    ORDER BY script_id
)
SELECT * from script_signatures
ORDER BY script_id 
"""
print_headline("Q4 b2) all_script_signatures")
query2csv(q4_b2, name2csvwriter("q4_b2"))
peak("q4_b2")


q4_c = """
WITH script_signatures as (
    SELECT script_id, COUNT(DISTINCT fpc_name) as script_score, filename, script_domain, GROUP_CONCAT(fpc_name, ";") as script_signature FROM (
        SELECT fpscriptorigins.id as script_id, filename, domain as script_domain, fpscriptfunctioncalls.id as scfc_id, fpscriptfunctioncalls.idx as scfc_idx, fpcategories.name as fpc_name from fpscriptorigins
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
        JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
        ORDER BY fpscriptorigins.id, fpscriptfunctioncalls.idx
        )
    GROUP BY script_id
    ORDER BY script_id
)
SELECT id, domain, score, group_concat(script_signatures.script_signature, ';') as page_signature from fpscores
JOIN score_scriptorigin_association ON score_scriptorigin_association.score_id = id
JOIN script_signatures ON script_signatures.script_id = score_scriptorigin_association.scriptorigin_id
GROUP BY id
ORDER BY id 
"""
print_headline("Q4 c) all_page_signatures")
query2csv(q4_c, name2csvwriter("q4_c"))
peak("q4_c")

q4_d = """
SELECT sub_cat_cnt as score, COUNT(source_filename) as source_files, SUM(sub_fped_domains_count) as affected_domains FROM (
    SELECT sub_source_filename as source_filename, sub_cat_cnt, sub_categories, GROUP_CONCAT(DISTINCT sub_source_domain) as source_domains, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
        SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
        JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
        JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
        JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
        GROUP BY fpscriptorigins.id
        ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
        )
    GROUP BY sub_source_filename, sub_cat_cnt
    ORDER BY sub_cat_cnt DESC
)
GROUP BY score
ORDER BY score DESC
"""
print_headline("Q4 d) Score list with the amount of source files, affected domains")
query2csv(q4_d, name2csvwriter("q4_d"))
peak("q4_d")

q4_e = """
WITH script_signatures as (
    SELECT *, filename || "_" || script_score as score_name, group_concat(fpscores.domain, ";") as affected_websites  FROM (
        SELECT script_id, COUNT(DISTINCT fpc_name) as script_score, filename, script_domain, GROUP_CONCAT(fpc_name, ";") as script_signature FROM (
            SELECT fpscriptorigins.id as script_id, filename, domain as script_domain, fpscriptfunctioncalls.id as scfc_id, fpscriptfunctioncalls.idx as scfc_idx, fpcategories.name as fpc_name from fpscriptorigins
            JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
            JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
            JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
            ORDER BY fpscriptorigins.id, fpscriptfunctioncalls.idx
            )
            GROUP BY script_id
        )
    JOIN score_scriptorigin_association on score_scriptorigin_association.scriptorigin_id = script_id
    JOIN fpscores on score_scriptorigin_association.score_id = fpscores.id
    GROUP BY script_id
    HAVING script_score > 6
    ORDER BY script_id
), std as (
    SELECT STDEV(script_score) as stdev, script_domain FROM script_signatures
    GROUP BY script_domain
)
SELECT script_signatures.script_domain, count(script_signatures.script_domain) as script_domain_cnt, avg(script_score) as avg_score, std.stdev as stdev_score, count(script_signatures.score_name) as script_files_cnt, GROUP_CONCAT(script_signatures.score_name, ";") as script_files, count(script_signatures.affected_websites) as affected_websits_cnt, group_concat(script_signatures.affected_websites, ";") as affected_websites from script_signatures
JOIN std on script_signatures.script_domain = std.script_domain
GROUP BY script_signatures.script_domain
ORDER BY script_domain_cnt DESC
"""
print_headline("Q4 e) Script Origin table with: script_domain, script_domain_cnt, avg_score, stdev_score, script_files_cnt, script_files, affected_websites_cnt, affected_websites for ever script_domain")
query2csv(q4_e, name2csvwriter("q4_e"))
peak("q4_e")


"""
FOR PAPER... needs to be added somewhere...

# Get script_domain, script_domain_cnt, avg_score, mad_score, stdev_score for ever script_domain. SET script_score > X to filter for categories
WITH script_signatures as (
    SELECT script_id, COUNT(DISTINCT fpc_name) as script_score, filename, script_domain, GROUP_CONCAT(fpc_name, ";") as script_signature FROM (
        SELECT fpscriptorigins.id as script_id, filename, domain as script_domain, fpscriptfunctioncalls.id as scfc_id, fpscriptfunctioncalls.idx as scfc_idx, fpcategories.name as fpc_name from fpscriptorigins
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
        JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
        ORDER BY fpscriptorigins.id, fpscriptfunctioncalls.idx
        )
    GROUP BY script_id
    HAVING script_score > 6
    ORDER BY script_id
), mad as (
    SELECT avg(d) as MAD, script_domain FROM ( 
        SELECT abs(script_score - avg(script_score) over ()) as d, script_domain FROM script_signatures 
        GROUP BY script_domain
    ) GROUP BY script_domain
), std as (
    SELECT STDEV(script_score) as stdev, script_domain FROM script_signatures
    GROUP BY script_domain
)
SELECT script_signatures.script_domain, count(script_signatures.script_domain) as script_domain_cnt, avg(script_score) as avg_score, mad.MAD as mad_score, std.stdev as stdev_score from script_signatures
JOIN std on script_signatures.script_domain = std.script_domain
JOIN mad on script_signatures.script_domain = mad.script_domain
GROUP BY script_signatures.script_domain
ORDER BY script_domain_cnt DESC

# Get script_domain, script_domain_cnt, avg_score, stdev_score, script_files_cnt, script_files, affected_websites_cnt, affected_websites for ever script_domain. SET script_score > X to filter for categories
WITH script_signatures as (
    SELECT *, filename || "_" || script_score as score_name, group_concat(fpscores.domain, ";") as affected_websites  FROM (
        SELECT script_id, COUNT(DISTINCT fpc_name) as script_score, filename, script_domain, GROUP_CONCAT(fpc_name, ";") as script_signature FROM (
            SELECT fpscriptorigins.id as script_id, filename, domain as script_domain, fpscriptfunctioncalls.id as scfc_id, fpscriptfunctioncalls.idx as scfc_idx, fpcategories.name as fpc_name from fpscriptorigins
            JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
            JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
            JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
            ORDER BY fpscriptorigins.id, fpscriptfunctioncalls.idx
            )
            GROUP BY script_id
        )
    JOIN score_scriptorigin_association on score_scriptorigin_association.scriptorigin_id = script_id
    JOIN fpscores on score_scriptorigin_association.score_id = fpscores.id
    GROUP BY script_id
    HAVING script_score > 6
    ORDER BY script_id
), std as (
    SELECT STDEV(script_score) as stdev, script_domain FROM script_signatures
    GROUP BY script_domain
)
SELECT script_signatures.script_domain, count(script_signatures.script_domain) as script_domain_cnt, avg(script_score) as avg_score, std.stdev as stdev_score, count(script_signatures.score_name) as script_files_cnt, GROUP_CONCAT(script_signatures.score_name, ";") as script_files, count(script_signatures.affected_websites) as affected_websits_cnt, group_concat(script_signatures.affected_websites, ";") as affected_websites from script_signatures
JOIN std on script_signatures.script_domain = std.script_domain
GROUP BY script_signatures.script_domain
ORDER BY script_domain_cnt DESC


SELECT sub_cat_cnt as score, source_filename, COUNT(source_filename) as files_in_score, SUM(sub_fped_domains_count) as fped_domains_in_score FROM (
    SELECT sub_source_filename as source_filename, sub_cat_cnt, sub_categories, GROUP_CONCAT(DISTINCT sub_source_domain) as source_domains, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
        SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
        JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
        JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
        JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
        GROUP BY fpscriptorigins.id
        ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
        )
    GROUP BY sub_source_filename, sub_cat_cnt
    ORDER BY sub_cat_cnt DESC
)
GROUP BY score, source_filename
HAVING score > 7
ORDER BY score DESC

SELECT sub_cat_cnt as score, source_filename, COUNT(source_filename) as files_in_score, SUM(sub_fped_domains_count) as fped_domains_in_score FROM (
    SELECT sub_source_filename as source_filename, sub_cat_cnt, sub_categories, GROUP_CONCAT(DISTINCT sub_source_domain) as source_domains, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
        SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
        JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
        JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
        JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
        JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
        JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
        GROUP BY fpscriptorigins.id
        ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
        )
    GROUP BY sub_source_filename, sub_cat_cnt
    ORDER BY sub_cat_cnt DESC
)
GROUP BY score, source_filename
HAVING score > 7
ORDER BY fped_domains_in_score DESC, score DESC

SELECT score, source_filename, GROUP_CONCAT(source_domains), COUNT(source_filename) as file_cnt  FROM (
    SELECT sub_cat_cnt as score, source_filename, source_domains, COUNT(source_filename) as files_in_score, SUM(sub_fped_domains_count) as fped_domains_in_score FROM (
        SELECT sub_source_filename as source_filename, sub_cat_cnt, sub_categories, GROUP_CONCAT(DISTINCT sub_source_domain) as source_domains, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
            SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
            JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
            JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
            JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
            JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
            JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
            GROUP BY fpscriptorigins.id
            ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
            )
        GROUP BY sub_source_filename, sub_cat_cnt
        ORDER BY sub_cat_cnt DESC
    )
    GROUP BY score, source_filename
    HAVING score > 7
    ORDER BY score DESC
)
GROUP BY source_filename
ORDER BY file_cnt DESC

SELECT score, source_filename, GROUP_CONCAT(source_domains), COUNT(source_filename) as file_cnt  FROM (
    SELECT sub_cat_cnt as score, source_filename, source_domains, COUNT(source_filename) as files_in_score, SUM(sub_fped_domains_count) as fped_domains_in_score FROM (
        SELECT sub_source_filename as source_filename, sub_cat_cnt, sub_categories, GROUP_CONCAT(DISTINCT sub_source_domain) as source_domains, COUNT(DISTINCT sub_score_domain) as sub_fped_domains_count, GROUP_CONCAT(DISTINCT sub_score_domain) as sub_fped_domains FROM (
            SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
            JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
            JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
            JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
            JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
            JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
            GROUP BY fpscriptorigins.id
            ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
            )
        GROUP BY sub_source_filename, sub_cat_cnt
        ORDER BY sub_cat_cnt DESC
    )
    GROUP BY score, source_filename
    HAVING score > 7
    ORDER BY score DESC
)
GROUP BY source_filename
ORDER BY score DESC

SELECT sub_source_domain, count(sub_source_domain) as cnt, group_concat(DISTINCT sub_source_filename) FROM (
    SELECT fpscores.domain as sub_score_domain, filename as sub_source_filename, fpscriptorigins.domain as sub_source_domain, count(DISTINCT fpcategories.id) as sub_cat_cnt, GROUP_CONCAT(DISTINCT fpcategories.name) as sub_categories FROM fpscriptorigins
    JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
    JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
    JOIN fpcategories ON fpscriptfunctioncalls.category_id = fpcategories.id
    JOIN score_scriptorigin_association ON fpscriptorigins.id = score_scriptorigin_association.scriptorigin_id
    JOIN fpscores ON fpscores.id = score_scriptorigin_association.score_id
    GROUP BY fpscriptorigins.id
    HAVING sub_cat_cnt > 7
    ORDER BY fpscriptorigins.filename, fpscriptorigins.domain, sub_cat_cnt DESC
)
GROUP BY sub_source_domain
HAVING cnt > 4
ORDER BY cnt DESC

SELECT * FROM (
    SELECT score, cat_signature, count(script_id) as source_id_cnt, group_concat(distinct domain || ":" || filename) as sources, count(distinct domain || ":" || filename) as sources_cnt, count(distinct domain) as sources_domains_cnt, count(distinct filename) as sources_filenames_cnt FROM (
        SELECT script_id, filename, domain, GROUP_CONCAT(fpc_name) as cat_signature, COUNT(fpc_name) as cat_cnt, COUNT(DISTINCT fpc_name) as score FROM (
            SELECT fpscriptorigins.id as script_id, filename, domain, fpscriptfunctioncalls.id as scfc_id, fpcategories.name as fpc_name from fpscriptorigins
            JOIN scriptorigin_scriptfunctioncall_association ON fpscriptorigins.id = scriptorigin_scriptfunctioncall_association.scriptorigin_id
            JOIN fpscriptfunctioncalls ON fpscriptfunctioncalls.id = scriptorigin_scriptfunctioncall_association.scriptfunctioncall_id
            JOIN fpcategories ON fpcategories.id = fpscriptfunctioncalls.category_id
            ORDER BY fpscriptorigins.id
            )
        GROUP BY script_id
        HAVING score > 7
    )
    GROUP BY cat_signature
    HAVING source_id_cnt > 1
    ORDER BY source_id_cnt DESC
)
GROUP BY cat_signature
HAVING sources_cnt > 1
ORDER BY sources_cnt DESC, sources_domains_cnt DESC
"""


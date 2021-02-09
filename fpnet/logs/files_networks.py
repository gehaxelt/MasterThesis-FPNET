import os
import sys
import csv
import collections
import shutil
csv.field_size_limit(sys.maxsize)

if len(sys.argv) < 3:
    print("Usage: {} <LOGFOLDER> <THRESHOLD>".format(sys.argv[0]))
    sys.exit(1)

LOGPATH = sys.argv[1]
THRESHOLD_SCORE = sys.argv[2]

NETWORKS = []
with open(LOGPATH + os.sep + "files" + os.sep + "matches_groups_" + str(THRESHOLD_SCORE) + ".csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if(line_count < 1):   # remove table header
            line_count += 1;
            continue;

        line_count += 1

        scripts = row[0].split("|||")
        size = int(row[1])
        minmatchscore = int(row[2])
        maxmatchscore = int(row[3])
        avgmatchscore = float(row[4])
        unique_minscore = int(row[5])
        unique_maxscore = int(row[6])
        unique_avgscore = float(row[7])

        NETWORKS.append([scripts, size, minmatchscore, maxmatchscore, avgmatchscore, unique_minscore, unique_maxscore, unique_avgscore])

print("Networks:", len(NETWORKS))

def same_matchscores(network):
    return network[2] == network[3] == network[4]

def same_scriptscores(network):
    return network[5] == network[6] == network[7]

def sourcedomains(network):
    return collections.Counter(map(lambda x: x.split("_")[1], network[0]))

def filenames(network):
    return collections.Counter(map(lambda x: '_'.join(x.split("_")[3:]), network[0]))

def same_sourcedomains(network):
    return len(sourcedomains(network)) == 1

def same_filenames(network):
    return len(filenames(network)) == 1

def networks2csv(networks, name):

    with open(LOGPATH + os.sep + "files" + os.sep + "network_" + name + "_" + str(THRESHOLD_SCORE) + ".csv", "w") as wfile:
        writer = csv.writer(wfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['scripts', 'size', 'minmatchscore', 'maxmatchscore', 'avgmatchscore', 'unique_minscore', 'unique_maxscore', 'unique_avgscore', 'domain', 'filenames'])

        for network in networks:
            writer.writerow(["|||".join(network[0]), network[1], network[2], network[3], network[4], network[5], network[6], network[7], sourcedomains(network), filenames(network)])

CATS= {
    'sm_ss_sd_sf': [],
    'sm_ss_sd_nsf': [],
    'sm_ss_nsd_sf': [],
    'sm_ss_nsd_nsf': [],
    'sm_nss_sd_sf': [],
    'sm_nss_sd_nsf': [],
    'sm_nss_nsd_sf': [],
    'sm_nss_nsd_nsf': [],
    'nsm_ss_sd_sf': [],
    'nsm_ss_sd_nsf': [],
    'nsm_ss_nsd_sf': [],
    'nsm_ss_nsd_nsf': [],
    'nsm_nss_sd_sf': [],
    'nsm_nss_sd_nsf': [],
    'nsm_nss_nsd_sf': [],
    'nsm_nss_nsd_nsf': [],
}


for network in NETWORKS:
    n_same_matchscores = same_matchscores(network)
    n_same_scriptscores = same_scriptscores(network)
    n_same_sourcedomains = same_sourcedomains(network)
    n_same_filenames = same_filenames(network)

    if n_same_matchscores and n_same_scriptscores and n_same_sourcedomains and n_same_filenames:
        CATS['sm_ss_sd_sf'].append(network)
    elif n_same_matchscores and n_same_scriptscores and n_same_sourcedomains and not n_same_filenames:
        CATS['sm_ss_sd_nsf'].append(network)
    elif n_same_matchscores and n_same_scriptscores and not n_same_sourcedomains and n_same_filenames:
        CATS['sm_ss_nsd_sf'].append(network)
    elif n_same_matchscores and n_same_scriptscores and not n_same_sourcedomains and not n_same_filenames:
        CATS['sm_ss_nsd_nsf'].append(network)
    elif n_same_matchscores and not n_same_scriptscores and n_same_sourcedomains and n_same_filenames:
        CATS['sm_nss_sd_sf'].append(network)
    elif n_same_matchscores and not n_same_scriptscores and n_same_sourcedomains and not n_same_filenames:
        CATS['sm_nss_sd_nsf'].append(network)
    elif n_same_matchscores and not n_same_scriptscores and not n_same_sourcedomains and n_same_filenames:
        CATS['sm_nss_nsd_sf'].append(network)
    elif n_same_matchscores and not n_same_scriptscores and not n_same_sourcedomains and not n_same_filenames:
        CATS['sm_nss_nsd_nsf'].append(network)
    elif not n_same_matchscores and n_same_scriptscores and n_same_sourcedomains and n_same_filenames:
        CATS['nsm_ss_sd_sf'].append(network)
    elif not n_same_matchscores and n_same_scriptscores and n_same_sourcedomains and not n_same_filenames:
        CATS['nsm_ss_sd_nsf'].append(network)
    elif not n_same_matchscores and n_same_scriptscores and not n_same_sourcedomains and n_same_filenames:
        CATS['nsm_ss_nsd_sf'].append(network)
    elif not n_same_matchscores and n_same_scriptscores and not n_same_sourcedomains and not n_same_filenames:
        CATS['nsm_ss_nsd_nsf'].append(network)
    elif not n_same_matchscores and not n_same_scriptscores and n_same_sourcedomains and n_same_filenames:
        CATS['nsm_nss_sd_sf'].append(network)
    elif not n_same_matchscores and not n_same_scriptscores and n_same_sourcedomains and not n_same_filenames:
        CATS['nsm_nss_sd_nsf'].append(network)
    elif not n_same_matchscores and not n_same_scriptscores and not n_same_sourcedomains and n_same_filenames:
        CATS['nsm_nss_nsd_sf'].append(network)
    elif not n_same_matchscores and not n_same_scriptscores and not n_same_sourcedomains and not n_same_filenames:
        CATS['nsm_nss_nsd_nsf'].append(network)
    else:
        print("ERROR!")

def avgscore(network):
    return round(network[7])

for cat in CATS:
    if not CATS[cat]:
        continue
    print(cat, "\tnetworks:",len(CATS[cat]), "\tfiles:",sum(map(lambda x: len(x), CATS[cat])), "\nscores:", sorted(collections.Counter(map(lambda x: avgscore(x), CATS[cat])).items(), key=lambda pair: pair[0], reverse=True)   )
    networks2csv(CATS[cat], cat)

def network2dir(cntr, cat, nw):
    BASEPATH = LOGPATH + os.sep + "files" + os.sep + "networkmatches"
    if not os.path.exists(BASEPATH):
        os.mkdir(BASEPATH)

    if not os.path.exists(BASEPATH + os.sep + "{}_{}".format(cntr, cat)):
        os.mkdir(BASEPATH + os.sep + "{}_{}".format(cntr, cat))
    
    for script in nw[0]:
        shutil.copy2(LOGPATH + os.sep + "files" + os.sep + "extracted" + os.sep + script, BASEPATH + os.sep + "{}_{}".format(cntr, cat) + os.sep)


SCRIPT_NW = []
with open(LOGPATH + os.sep + "paper_query" + os.sep + "q4_a_unlimited.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if(line_count < 1):   # remove table header
            line_count += 1;
            continue;

        line_count += 1

        sscore = int(row[0])
        sscripts = set(row[7].split(","))

        SCRIPT_NW.append([sscore, sscripts])

print("\n\n\t Mode | nw type | snl | fnl | msize | exmsize | example")
EXACT = []
OVERLAP = []
for i, sn in enumerate(list(SCRIPT_NW)):
    snsc = sn[0]

    if snsc <= 15:
        continue


    match_cntr = 0
    to_print = []
    total_nw = []
    for cat in CATS:
        for network in CATS[cat]:
            scripts = set(map(lambda x: "{}:{}".format(x.split("_")[1], "_".join(x.split("_")[3:])), network[0]))
            nscore = network[5]
            mscore = network[6]
            fn = [mscore, scripts, nscore]

            snl = len(sn[1])
            fnl = len(fn[1])
            fnmsc = fn[0]
            fnnsc = fn[2]

            if sn[1] == fn[1] and (fnnsc <= snsc <= fnmsc):
                EXACT.append(fn[1])
                to_print.append("\t{} | Exact | {} | {} | {} | {} | {} | {}".format(match_cntr, cat, len(sn[1]), len(fn[1]), len(fn[1]), 0, list(fn[1])[:2]))
                total_nw.append(fn)
                network2dir("{}_{}".format(i,match_cntr), cat, network)
                match_cntr += 1
                continue
            if len(fn[1] & sn[1]) and (fnnsc <= snsc <= fnmsc):
                OVERLAP.append(fn[1])
                to_print.append("\t{} | Overlap | {} | {} | {} | {} | {} | {}".format(match_cntr, cat, len(sn[1]), len(fn[1]), len(fn[1] & sn[1]), len(fn[1] ^ sn[1]), list(fn[1] & sn[1])[:2]))
                total_nw.append(fn)
                network2dir("{}_{}".format(i,match_cntr), cat, network)
                match_cntr += 1
                continue

    if total_nw:
        combined = set()
        for nw in total_nw:
            combined |= nw[1]

    if to_print:
        print("#### {} Sig-based network:".format(i), sn[0], list(combined | sn[1])[:3])
        for l in to_print:
            print(l)
        print("\t=>sn:{} | fn:{} | intersect:{} | excl:{} | union:{}".format(len(sn[1]), len(combined), len(combined & sn[1]), len(combined ^ sn[1]), len(combined | sn[1])))

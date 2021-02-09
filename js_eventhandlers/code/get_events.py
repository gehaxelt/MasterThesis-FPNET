#!/usr/bin/python3

import os
import json

PATH = "../data/event_counters/"

total_events = 0
total_sites = 0

files = os.scandir(PATH)
for f in files:
    data = json.load(open(f))
    if data["sum"] > 0:
        print(str(f), data["sum"])
        total_events += data["sum"]
        total_sites += 1

print("Total sites: ", total_sites)
print("Total events: ", total_events)
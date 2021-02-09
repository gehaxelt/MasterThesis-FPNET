#!/usr/bin/python3

import os
import json
import sys

def sortDict(d):
    return {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}

PATH = "../data/event_counters.alexaTop10k.fixed/"

DOMAINS = "../data/domains/top10000_alexa.txt"
MISSING_DOMAINS_OFILE = "../data/domains/missing_domains.txt"

missing_sites = []
with open(DOMAINS) as f:
    missing_sites = list(map(lambda x: x.strip(), f.readlines()))

total_sites = 0
total_events = 0
event_sites = 0

events_handler = 0
events_attr = 0
events_jquery = 0

user_events = {
    "ondevicemotion":0,
    "ondeviceorientation":0,
    "onabsolutedeviceorientation":0,
    "ondeviceproximity":0,
    "onuserproximity":0,
    "ondevicelight":0,
    "onabort":0,
    "onblur":0,
    "onfocus":0,
    "onauxclick":0,
    "oncanplay":0,
    "oncanplaythrough":0,
    "onchange":0,
    "onclick":0,
    "onclose":0,
    "oncontextmenu":0,
    "oncuechange":0,
    "ondblclick":0,
    "ondrag":0,
    "ondragend":0,
    "ondragenter":0,
    "ondragexit":0,
    "ondragleave":0,
    "ondragover":0,
    "ondragstart":0,
    "ondrop":0,
    "ondurationchange":0,
    "onemptied":0,
    "onended":0,
    "onformdata":0,
    "oninput":0,
    "oninvalid":0,
    "onkeydown":0,
    "onkeypress":0,
    "onkeyup":0,
    "onload":0,
    "onloadeddata":0,
    "onloadedmetadata":0,
    "onloadend":0,
    "onloadstart":0,
    "onmousedown":0,
    "onmouseenter":0,
    "onmouseleave":0,
    "onmousemove":0,
    "onmouseout":0,
    "onmouseover":0,
    "onmouseup":0,
    "onwheel":0,
    "onpause":0,
    "onplay":0,
    "onplaying":0,
    "onprogress":0,
    "onratechange":0,
    "onreset":0,
    "onresize":0,
    "onscroll":0,
    "onseeked":0,
    "onseeking":0,
    "onselect":0,
    "onshow":0,
    "onstalled":0,
    "onsubmit":0,
    "onsuspend":0,
    "ontimeupdate":0,
    "onvolumechange":0,
    "onwaiting":0,
    "onselectstart":0,
    "ontoggle":0,
    "onpointercancel":0,
    "onpointerdown":0,
    "onpointerup":0,
    "onpointermove":0,
    "onpointerout":0,
    "onpointerover":0,
    "onpointerenter":0,
    "onpointerleave":0,
    "ongotpointercapture":0,
    "onlostpointercapture":0,
    "onmozfullscreenchange":0,
    "onmozfullscreenerror":0,
    "onanimationcancel":0,
    "onanimationend":0,
    "onanimationiteration":0,
    "onanimationstart":0,
    "ontransitioncancel":0,
    "ontransitionend":0,
    "ontransitionrun":0,
    "ontransitionstart":0,
    "onwebkitanimationend":0,
    "onwebkitanimationiteration":0,
    "onwebkitanimationstart":0,
    "onwebkittransitionend":0,
    "onerror":0,
    "onafterprint":0,
    "onbeforeprint":0,
    "onbeforeunload":0,
    "onhashchange":0,
    "onlanguagechange":0,
    "onmessage":0,
    "onmessageerror":0,
    "onoffline":0,
    "ononline":0,
    "onpagehide":0,
    "onpageshow":0,
    "onpopstate":0,
    "onrejectionhandled":0,
    "onstorage":0,
    "onunhandledrejection":0,
    "onunload":0,
}
user_sites = user_events.copy()
sites_attr = []
sites_handler = []
sites_jquery = []

files = os.scandir(PATH)
for f in files:
    domain = str(f.name).strip()
    missing_sites.remove(domain)
    raw_data = open(f)
    try:
        data = json.load(raw_data)
    except:
        if not raw_data.read().strip():
            missing_sites.append(domain)
            continue

    if data["sum"] > 0:
        #print(f.name, data["sum"])
        total_events += data["sum"]
        event_sites += 1

        events_attr += sum(data["attr"].values())
        events_handler += sum(data["handler"].values())
        events_jquery += sum(data["jquery"].values())

        has_attr_event = False
        has_handler_event = False
        has_jquery_event = False

        for k in user_events:
            has_event = False

            if k in data["attr"]:
                user_events[k] += data["attr"][k]
                has_event = True
                has_attr_event = True
            if k in data["handler"]:
                user_events[k] += data["handler"][k]
                has_event = True
                has_handler_event = True
            if k.replace("on", "") in data["jquery"]:
                user_events[k] += data["jquery"][k.replace("on", "")]
                has_event = True
                has_jquery_event = True

            if has_event:
                user_sites[k] += 1

        if has_attr_event:
            sites_attr.append(domain)
        if has_handler_event:
            sites_handler.append(domain)
        if has_jquery_event:
            sites_jquery.append(domain)
    else:
        pass
    total_sites += 1

print("Total sites: ", total_sites)
print("Missing sites: ", len(missing_sites))
print("Event sites: ", event_sites, "/", total_events)
print("- attr:\t\t", events_attr)
print("- handler:\t", events_handler)
print("- jquery:\t", events_jquery)
print("- User events:\n", sortDict(user_events))
print("- User sites:\n", sortDict(user_sites))
print("Processed: ", total_sites + len(missing_sites))
print("Sites with attr:", len(sites_attr))
print("Sites with handler:", len(sites_handler))
print("Sites with jquery:", len(sites_jquery))

with open(MISSING_DOMAINS_OFILE, "w") as f:
    f.writelines(list(map(lambda x: x + "\n", missing_sites)))

import matplotlib.pyplot as plt
import pandas as pd
import math

SMALL_SIZE = 8
MEDIUM_SIZE = 8
BIGGER_SIZE = 8

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

def top15(d):
    dn = {}
    for i, k in enumerate(sortDict(d).keys()):
        if i >= 15:
            break
        dn[k] = d[k]
    return dn

def filterDict(d, keys):
    dn = {}
    for k in keys:
        dn[k] = d[k]
    return dn

t15_events = top15(user_events)
t15_sites = top15(user_sites)

labels = [x for x in sortDict(t15_events).keys()]
for x in sortDict(t15_sites).keys():
    if x not in labels:
        labels.append(x)

plt_events = filterDict(user_events, labels)
plt_sites = filterDict(user_sites, labels)

d = {
    'Events': plt_events,
    'Websites': plt_sites,
}
df = pd.DataFrame(d)
g = df.plot(kind='barh', figsize=(9,6), color=['green', 'orange'])
#g = df.plot(kind='barh')
#g.set_xscale("log")
ax = g
xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()
# scale_factor = 1/10
# plt.xlim(xmin * scale_factor, xmax * scale_factor)
#plt.ylim(ymin * scale_factor, ymax * scale_factor)
for p in ax.patches:
    width = p.get_width()
    print(width, math.log(width)*2)
    plt.text(width + 25000, p.get_y()+0.55*p.get_height(),
             '{:1d}'.format(width), ha='center', va='center', fontsize=8)
plt.xlabel("Number of events or websites")
plt.ylabel("Event type")
#plt.show()
plt.savefig("/tmp/event_results.pdf")
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import concurrent.futures
import logging
import os
import json
import datetime

DOMAIN_FILE = "/data/domains/missing_domains.txt"
JS_COUNTER_SCRIPT = "/code/events_counter.js"
WORKER_COUNT = 4
MAX_SESSIONS = 1

def run_browser(args):
    domain = args[0]
    useJavascript = args[1]
    cntr = args[2]

    print("{}: Domain: {} JS: {}".format(cntr, domain, useJavascript))
    capas = DesiredCapabilities.CHROME.copy()
    capas['goog:chromeOptions'] = {}

    if not useJavascript:
        capas['goog:chromeOptions']['prefs'] =  {'profile.managed_default_content_settings.javascript': 2}

    try:
        driver = webdriver.Remote(command_executor="http://hub:4444/wd/hub", desired_capabilities=capas)
        time.sleep(1)

        driver.set_page_load_timeout(30)
        driver.implicitly_wait(30)

        driver.get('http://{}'.format(domain))

        # Wait for page to fully load
        time.sleep(15)

        script_output = driver.execute_script(open(JS_COUNTER_SCRIPT).read())

        data = json.loads(script_output)
        print(domain, data["sum"])

        with open("/data/event_counters/{}".format(domain), "w") as f:
            f.write(script_output + "\n")
    except Exception as e:
        print(e)
    finally:
        driver.quit()


time.sleep(2)

DOMAINS = open(DOMAIN_FILE)

def domain_iter():
    i = 0
    for domain in DOMAINS:
        i += 1
        for mode in [True]:
            yield [domain.strip(), mode, i]


with concurrent.futures.ThreadPoolExecutor(max_workers=WORKER_COUNT * MAX_SESSIONS) as executor:
    executor.map(run_browser, domain_iter())
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from vncdotool import api
import time
import concurrent.futures
import logging
import os
import json
import random
import datetime
import requests
import shutil
import urllib3
import threading
import _thread as thread
import queue

urllib3.disable_warnings()
print_lock = threading.Lock()

from config import WORKER_COUNT, DOMAIN_FILE, PAGELOAD_TIMEOUT, IMPLICITWAIT_TIMEOUT, REMOVE_CHROME_PROFILE, ENABLE_PROXY
MAX_SESSIONS = 1

def get_worker_id(cntr):
    return (cntr % WORKER_COUNT)

def sprint(s):
    with print_lock:
        print(s)

def get_driver(capabilities, chrome_id):
    return webdriver.Remote(command_executor="http://chrome{}:5555/wd/hub".format(chrome_id), desired_capabilities=capabilities)

def remove_chrome_dir(id):
    shutil.rmtree("/tmp/chrome/{}".format(id))

def do_work(work):
    return run_browser(work)

def worker_thread(thread_id):
    while not WORKER_QUEUE.empty():
        work = WORKER_QUEUE.get()
        work['worker_id'] = thread_id
        sprint("Working on: {}".format(work))
        start_time = int(time.time())

        error_occured = True
        try:
            error_occured = do_work(work)
        except Exception as e:
            #print(e)
            pass
        stop_time = int(time.time())

        # We had an error with the browser, let's wait until the timeout finishes
        if error_occured:
            time_to_wait = PAGELOAD_TIMEOUT + IMPLICITWAIT_TIMEOUT + 5 - (stop_time - start_time)
            if time_to_wait < 0:
                time_to_wait = 15 # weird error, let's wait a few seconds
            time.sleep(time_to_wait)
            # browser should be dead now, continue

        sprint("Work done: {} in {}s".format(work, stop_time - start_time))

def run_browser(work):
    domain = work['domain']
    cntr = work['counter']
    trace_id = None
    chrome_node_id = work['worker_id'] + 1
    has_error = False

    data = {
        'domain': domain,
        'action': 'get_trace',
        'origin': "python"
    }
    r = requests.post("https://fpnet_monitor:8898/", json=data, verify=False)
    ret = r.json()
    trace_id = ret['trace_id']

    try:
        if os.path.exists("/tmp/chrome/{}".format(trace_id)):
            remove_chrome_dir(trace_id)

        os.mkdir('/tmp/chrome/{}'.format(trace_id))
        shutil.copytree('/fpmon/chrome_app', '/tmp/chrome/{}/chrome_app'.format(trace_id))
    except:
        pass

    with open('/tmp/chrome/{}/chrome_app/content.js'.format(trace_id), 'a') as f:
        f.write("var glob_trace_id = '{}';\n".format(trace_id))
        f.write("var glob_orig_domain = '{}';\n".format(domain))

    os.system("chown -R 1000:1000 /tmp/chrome/{}/".format(trace_id))

    time.sleep(random.randint(1000,3000)/1000)

    sprint("{}: Domain: {}, Trace: {}, Node: {}".format(cntr, domain, trace_id, chrome_node_id))

    capas = DesiredCapabilities.CHROME.copy()
    capas['goog:chromeOptions'] = {}
    capas['goog:chromeOptions']['binary'] = '/fpmon/chrome/start_chrome'
    capas['goog:chromeOptions']['args'] = [
        '--ignore-certificate-errors',
        '--load-extension=/tmp/chrome/{}/chrome_app'.format(trace_id),
        '--disable-web-security',
        '--no-sandbox',
        '--start-maximized',
        '--user-data-dir=/tmp/chrome/{}'.format(trace_id),
        '--domain={}'.format(domain),
        '--traceid={}'.format(trace_id),
        '--container=chrome{}'.format(chrome_node_id),
        ]
    if ENABLE_PROXY:
        capas['goog:chromeOptions']['args'].append('--proxy-server=http://proxy{}:8080'.format(chrome_node_id))

    try:
        driver = get_driver(capas, chrome_node_id)

        driver.set_page_load_timeout(PAGELOAD_TIMEOUT)
        driver.implicitly_wait(IMPLICITWAIT_TIMEOUT)

        if ENABLE_PROXY:
            requests.get("http://startlogging/{}".format(domain), proxies={'http': 'http://proxy{}:8080'.format(chrome_node_id)})
        driver.get('http://{}'.format(domain))

        if driver.find_element_by_id('fpmon_success'):
            # if found: everything worked as expected
            data = {
                'action': "finish_trace",
                'domain': domain,
                'trace_id': trace_id,
                'origin': "python"
            }
        else:
            data = {
                'domain': domain,
                'action': "fail_trace",
                'reason': 'fpmon_success not found',
                'trace_id': trace_id,
                'origin': "python"
            }

    except Exception as e:
        data = {
            'domain': domain,
            'action': "fail_trace",
            'reason': str(e),
            'trace_id': trace_id,
            'origin': "python"
        }
    finally:
        try:
            data['url'] = driver.current_url
        except:
            pass

        if ENABLE_PROXY:
            requests.get("http://stoplogging", proxies={'http': 'http://proxy{}:8080'.format(chrome_node_id)})

        remove_it = REMOVE_CHROME_PROFILE
        r = requests.post("https://fpnet_monitor:8898/", json=data, verify=False)

    try:
        driver.quit()
    except Exception as e:
        if not 'Message: java.net.ConnectException: Connection refused (Connection refused)' in str(e):
            has_error = True
            remove_it = False

    time.sleep(random.randint(1000,3000)/1000)

    if remove_it:
        remove_chrome_dir(trace_id)

    if has_error or 'fail' in data['action']:
        return True
    else:
        return False



time.sleep(2)

from config import DOMAINS

WORKER_QUEUE = queue.SimpleQueue()
WORKER_THREADS = [threading.Thread(target=worker_thread, args=(i,)) for i in range(WORKER_COUNT)]

def domain_iter():
    for domain in DOMAINS:
        yield domain.strip()

work_counter = 0
for domain  in domain_iter():
    sprint("Queueing {} to queue".format(domain))
    WORKER_QUEUE.put({'domain': domain, 'counter': work_counter})
    work_counter += 1

for t in WORKER_THREADS:
    t.start()

for t in WORKER_THREADS:
    t.join()
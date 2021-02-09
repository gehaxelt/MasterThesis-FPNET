Fingerprinting Networks Scanner - FPNET
=============================================

This tool was developed and used in the thesis to scan large sets of websites for their fingerprinting activity. It is similar to [Kybranz' FPCRAWL](https://github.com/KybranzF/fpcrawl), but FPNET improves a few aspects in order to be more reliable, stable, accurate, and closer mimic real browsers.

## Usage

- First, put the list of domains as a text-file into `data/domains/`. 
- Copy `code/config.py.sample` to `code/config.py` and adjust the settings to suite your needs. You should at least edit the following variables:

```
DOMAIN_FILE = "/data/domains/top10000_alexa.txt"        # Path to the list of domains to scan
WORKER_COUNT = 20                                       # Number of parallel browser instances. NOTE: This variable will be overwritten by start-tmux.sh!
# REMEMBER TO ADJUST the hard timeout in fpmon/chrome/start_chrome to PAGELOAD_TIMEOUT + IMPLICITWAIT_TIMEOUT
PAGELOAD_TIMEOUT = 45                                   # How long to wait for a page to load?
IMPLICITWAIT_TIMEOUT = 45                               # How long to wait for an element to appear?
REMOVE_CHROME_PROFILE = True                            # Remove temporary chrome profiles? Use False for debugging purposes only, or provide enough space in /tmp/
ENABLE_PROXY = True                                     # Enable recording of the HTTP traffic using mitmproxy
```
- For a clean startup, containers must be started in a specific order. The script `start-tmux.sh` takes care of this. Its usage is `./start-tmux.sh <number parallel browser instances>`. 
- When the tmux-session shows up, switch to the pane containing `# sudo docker-compose up fpnet_scanner | tee $LOGPATH/scanner`, uncomment it and start the scan by executing the command. 

Depending on the chosen settings, a scan can take from 6 - 12 hours for the Alexa Top 10,000.

Once the scan finished, the recommended way to continue is: 

- Change into the `logs/<timestamp-of-scan>/` directory.
- To check the success / failure rates and possible error cases, run `python3 ../logs.py .`
- Run `python3 ../newdb.py .` to create the SQLite database. NOTE: By default, only pages with a page-score > 10 are considered. Modify `if line['score'] < 10:` to change this.
- Run `python3 ../paper_query.py .` to query the database for some first analysis results.
- After that, run the other analysis scripts depending on your scenario.

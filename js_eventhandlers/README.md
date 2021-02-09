JavaScript usage on the internet
=================================

This tool was an early version of FPNET, which was used to determine the usage of JavaScript "on"-event handlers on the internet. 

## Usage:

- First, put a file containing the domains to scan into `data/domains/`. 
- In `code/browser.py` adjust the following variables: 

```
DOMAIN_FILE = "/data/domains/missing_domains.txt"   # Path to the domain file
WORKER_COUNT = 4                                    # Number of parallel web browsers to run
```

To start the scanning process, switch into the `core/` folder and run `docker-compose up`. Make sure that at least `WORKER_COUNT` browsers are started, before the `js_eval2` container starts.

Note: In later experiments, the `selenium hub` turned out to suffer from frequent crashes or other issues, which were worked around in FPNET. 
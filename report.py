import os
from pathlib import Path
from urllib.parse import urlparse
import re

# 1) Number of unique pages
# 2) Longest page (# of words)
# 3) 50 most common words (ignoring stop words)
# 4) Number of subdomains in uci.edu, listed alphabetically and with number of pages in the subdomain

subdomains = dict()
def log_subdomain(url):
    parsed = urlparse(url)
    if parsed.hostname not in subdomains:
        subdomains[parsed.hostname] = 1
    else:
        subdomains[parsed.hostname] += 1

        
for file in Path('./webpages').iterdir():  
    with open(file) as f:
        url = f.readline().rstrip('\n')
        print(url)
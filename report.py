from pathlib import Path
from urllib.parse import urlparse
import nltk
import os
from scraper import is_valid
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

def computeWordFrequencies(tokens):
    freqs = dict()
    for i in range(len(tokens)):
        if tokens[i] in freqs:
            continue
        freqs[tokens[i]] = 1
        for j in range(i + 1, len(tokens)):
            if tokens[j] == tokens[i]:
                freqs[tokens[i]] += 1
    return freqs

def tokenizeWebpages():
    for file in Path('./webpages').iterdir():  
        with open(file) as f:
            url = f.readline().rstrip('\n')
            tokens = nltk.word_tokenize(' '.join(f.readlines()))
            with open('tokens/'+file.name, 'w') as wf:
                wf.write(url+'\n'+' '.join(tokens))

def numPages():
    n = 0
    for _ in Path('./webpages').iterdir():  
        n+=1
    return n

def longestPage():
    max_words = 0
    longest_page = ''
    for file in Path('./tokens').iterdir():  
        with open(file) as f:
            url = f.readline().rstrip('\n')
            tokens = f.readline().rstrip('\n').split(' ')
            if len(tokens) > max_words:
                max_words = len(tokens)
                longest_page = url
    return max_words, longest_page

n_pages = numPages()
max_words, longest_page = longestPage()

with open('report.txt', 'w') as report:
    report.write('Unique pages found: '+str(n_pages)+'\n'+
                 'Longest page is "' +str(longest_page)+'" with '+str(max_words)+' words')

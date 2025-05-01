from pathlib import Path
from urllib.parse import urlparse

# 1) Number of unique pages
# 2) Longest page (# of words)
# 3) 50 most common words (ignoring stop words)
# 4) Number of subdomains in uci.edu, listed alphabetically and with number of pages in the subdomain

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

def iteratePages():
    max_words = 0
    n_pages = 0
    word_freqs = dict()
    longest_page = ''
    subdomains = dict()
    for file in Path('./tokens').iterdir():  
        n_pages += 1
        with open(file) as f:
            url = f.readline().rstrip('\n')
            parsed = urlparse(url)
            subdomain = parsed.netloc.lower()
            subdomains[subdomain] = subdomains.get(subdomain,0)+1
            tokens = f.readline().rstrip('\n').split(' ')
            for token in tokens:
                word_freqs[token] = word_freqs.get(token, 0) + 1
            if len(tokens) > max_words:
                max_words = len(tokens)
                longest_page = url
    sorted_freqs = sorted(word_freqs.items(), key=lambda item: item[1], reverse=True)
    subdomains = sorted(subdomains.items(), key=lambda item: item[0])
    return n_pages, max_words, longest_page, sorted_freqs[:50], subdomains

n_pages, max_words, longest_page, top_50_words, subdomains = iteratePages()

pages_crawled_str = f"1. Unique pages crawled: {n_pages}"
longest_page_str = f"2. Longest page: {longest_page} ({max_words} words)"
top_50_lines = '\n'.join([f'{word}: {freq}' for word, freq in top_50_words])
top_50_words_str = f"3. Top 50 words:\n{top_50_lines}"
subdomains_lines = '\n'.join([f'{subdomain}: {count}' for subdomain, count in subdomains])
num_subdomains_str = f"4. Number of subdomains found: {len(subdomains)}\n{subdomains_lines}"

report_questions = [pages_crawled_str,longest_page_str,top_50_words_str,num_subdomains_str]
with open('report.txt', 'w') as report:
    report.write('\n\n'.join(report_questions))

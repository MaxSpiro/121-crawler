import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from stopwords import stopwords

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url: str, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scraped from resp.raw_response.content
    if resp.status != 200:
        print(resp.error)
        return list()
    
    links = list()
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for link in soup.find_all('a'):
        if link.get('href'):
            links.append(urldefrag(link.get('href')).url)


    # Process HTML
    text = soup.get_text()
    filename = url.replace('://','_').replace('/','_').replace('.','_')
    with open("webpages/"+filename, 'w') as f:
        f.write(text)
        
    return links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if '.' in parsed.path: # revisit
            return False 
        if not re.match(
            r".*\.(ics|cs|informatics|stat)\.uci\.edu|today\.uci\.edu",
            parsed.hostname.lower(),
        ):
            return False
        if parsed.hostname.lower()[
            :5
        ] == "today" and not parsed.path.lower().startswith(
            "/department/information_computer_sciences"
        ):
            return False
        return True

    except TypeError:
        print("TypeError for ", parsed)
        return False
    
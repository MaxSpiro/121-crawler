import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from utils import get_urlhash, get_logger
import nltk
from stopwords import stopwords
from persistent_index import PersistentSimhashIndex

error_logger = get_logger('errors')
index = PersistentSimhashIndex()

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
    try:
        if resp.status != 200:
            error_logger.error('URL: '+url+' returned status code ' + str(resp.status))
            if resp.error:
                error_logger.error('Error: '+resp.error)
            return list()
        
        # Only accept HTML
        content = resp.raw_response.content.lower()
        if (resp.headers and 'text/html' not in resp.headers['Content-Type']) or (b'<html' not in content and b'<!doctype html' not in content):
            error_logger.info(f'URL {url} is not HTML')
            return list()
        
        # Process HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        robots_tag = soup.find("meta",attrs={'name':'robots'})
        robots = robots_tag.get("content","").lower() if robots_tag else ""
        links = list()
        if 'nofollow' not in robots:
            for link in soup.find_all('a'):
                if link and link.get('href'):
                    href = link.get('href',"").strip()
                    if 'mailto:' in href or href.startswith('#'):
                        continue
                    new_url = urljoin(resp.raw_response.url, href)
                    links.append(urldefrag(new_url).url)
        if 'noindex' in robots:
            return links
        
        text = soup.get_text(separator=" ",strip=True)
        filename = get_urlhash(url)
        tokens = tokenize(clean_text(text))
        
        if len(tokens) < 10:
            error_logger.info('URL: '+url+' returned low information')
            return links
        
        try:
            similar_docs = getSimilarDocs(url, soup)
            if len(similar_docs) > 0:
                similar_docs_string = ', '.join(similar_docs)
                error_logger.error(f'Site {url} is similar to {similar_docs_string}')
                return links
        except:
            pass

        with open("tokens/"+filename, 'w') as f:
            f.write(url+"\n"+' '.join(tokens))
        
        with open("webpages/"+filename,'w') as f:
            f.write(url+"\n"+str(content))
            
        return links
    except Exception as e:
        error_logger.error(repr(e))
        return list()

def tokenize(text):
    return [token for token in nltk.word_tokenize(text) if token not in stopwords and len(token) > 2]

def clean_text(text):
    return re.sub(r"[^a-z\s]",'', text.lower())

def getSimilarDocs(url, soup: BeautifulSoup):
    tokens = []
    if soup.title:
        for word in tokenize(clean_text(soup.title.getText())):
            tokens.append((word, 3))
    for h in soup.find_all(['h1','h2','h3']):
        for word in tokenize(clean_text(h.get_text())):
            tokens.append((word, 2))
    for word in tokenize(clean_text(soup.get_text(separator=" ",strip=True))):
        tokens.append((word, 1))
    similarDocs = index.get_matches(tokens)
    index.add_doc(url, tokens)
    return similarDocs

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        url = url.lower()
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(src|rpm|css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|sql|txt|ppsx|img)$", parsed.path):
            return False
        # calendar link, download, login, sharing to twitter or facebook
        if re.match(r".*(ical|tribe_events?|tribe-bar-date|action=|share=(twitter|facebook)|do=).*", parsed.query):
            return False
        if 'calendar' in url:
            return False
        # filter dates for calendars
        if re.match(r"/(events|day|month).*/\d{4}-\d{2}(-\d{2})?.*", parsed.path):
            return False
        # file uploads and login form
        if re.match(r".*/wp-(content|login).*", parsed.path):
            return False
        # I used the regex from https://support.archive-it.org/hc/en-us/articles/208332963-Modify-crawl-scope-with-a-Regular-Expression which blocks URLS with repeated paths, but I modified it for my own needs to include repeated numbers in paths
        # Repeated paths (excluding the specified URL which has content and is not a crawler trap)
        if re.match(r"^.*?(/[a-zA-Z]+?/).*?\1.*$|^.*?/([a-zA-Z]+?/)\2.*$", url) and 'grape.ics.uci.edu/wiki/public/wiki' not in url:
            return False
        if not re.match(
            r".*(ics|cs|informatics|stat|today)\.uci\.edu",
            parsed.hostname,
        ):
            return False
        if "today.uci.edu" in parsed.hostname and "department/information_computer_sciences" not in parsed.path:
            return False

        return True

    except Exception as e:
        print(repr(e))
        return False
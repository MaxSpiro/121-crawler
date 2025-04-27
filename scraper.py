import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from utils import get_urlhash, get_logger

error_logger = get_logger('errors')
low_info_logger = get_logger('low_info')

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
        error_logger.error('URL: '+url+' returned status code ' + str(resp.status))
        if resp.error:
            error_logger.error('Error: '+resp.error)
        return list()
    
    links = list()
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for link in soup.find_all('a'):
        if link.get('href'):
            links.append(urldefrag(link.get('href')).url)


    # Process HTML
    text = soup.get_text()
    clean_text = re.sub(r'\n+','\n',text)
    if len(clean_text) < 5:
        low_info_logger.info('URL: '+url+' returned low information')
        if len(clean_text) > 0:
            low_info_logger.info('Page contents: '+clean_text)
    filename = get_urlhash(url)
    with open("webpages/"+filename, 'w') as f:
        f.write(url+"\n"+clean_text)
        
    return links


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
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|sql)$", parsed.path):
            return False
        # pdf without an extension
        if re.match(r".*/files/pdf/.*", parsed.path):
            return False
        # calendar link, download, login, sharing to twitter or facebook
        if re.match(r".*(ical=|tribe_events|action=|share=(twitter|facebook)).*", parsed.query):
            return False
        # calendar events (gray area: wics.*event/.*, some have text, most are useless)
        if re.match(r".*/events/(category|.*(day|20\d{2}-\d{2})).*", parsed.path):
            return False
        if re.match(r".*wics\.ics\.uci\.edu/events?/.*", url):
            return False
        # redirects
        if re.match(r".*ics\.uci\.edu/~.*", url):
            return False
        # file uploads and login form
        if re.match(r".*/wp-(content|login).*", parsed.path):
            return False
        if not re.match(
            r".*\.(ics|cs|informatics|stat)\.uci\.edu|today\.uci\.edu",
            parsed.hostname,
        ):
            return False
        
        if parsed.hostname[
            :5
        ] == "today" and not parsed.path.startswith(
            "/department/information_computer_sciences"
        ):
            return False
        return True

    except Exception as e:
        print(repr(e))
        return False
    
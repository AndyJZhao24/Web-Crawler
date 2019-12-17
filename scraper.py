import re
import lxml.etree
import lxml.html
from urllib.parse import urlparse, urldefrag
from colorama import Fore
import sys
import json

def scraper(url, resp, wordFreq, wordCount, subDom, stopwords):
    links = extract_next_links(url, resp, wordFreq, wordCount, subDom, stopwords)
    return [link for link in links if is_valid(link)]

def process_text(url, et, wordFreq, wordCount, stopwords):
    # Extracts text from page, excluding text in style, script, and a tags, and updates word count and frequency
    try:
        for text in et.xpath("//*[not(self::style|self::script|self::a)]/text()[normalize-space()]"):
            for word in text.lower().split():
                wordCount[url] += 1
                if word not in stopwords:
                    for token in re.findall("[a-zA-Z0-9]+", word):
                        if len(token) > 3:
                            wordFreq[token] += 1

    # If fail to extract text, such as encoding issue, set page's number of words to -1
    except:
        wordCount[url] = -1

def process_subDomain(url, wordFreq, wordCount, subDom):
    # Stores unique subdomains in ics.uci.edu and count number of pages crawled in that subdomain
    try:
        parsed = urlparse(url)
        if re.match(r"^.*(\.ics\.uci\.edu)", parsed.netloc.lower()):
            subDom[parsed.netloc.lower()] += 1
    except:
        print('Error Processing Subdomain. Saving Files.')
        with open('rsrc/wordFreq.json','w') as outfile:
            json.dump(wordFreq, outfile)
        with open('rsrc/wordCount.json','w') as outfile:
            json.dump(wordCount, outfile)
        with open('rsrc/subDom.json','w') as outfile:
            json.dump(subDom, outfile)
        sys.exit()


def extract_next_links(url, resp, wordFreq, wordCount, subDom, stopwords):
    result = []

    # Add url to default dict if not already in it and check if ics subdomain
    wordCount[url]
    process_subDomain(url, wordFreq, wordCount, subDom)

    if resp.status == 200:
        try:
            # Extract response content and store to etree object and makes links absolute.
            et = lxml.html.fromstring(resp.raw_response.content)
            et.make_links_absolute(url, resolve_base_href=True, handle_failures='discard')
        except:
            return result
        
        # Processes and updates word and frequency count
        process_text(url, et, wordFreq, wordCount, stopwords)
        
        # iterate through <a> only and extract the contents of the href property.
        # add href to list if valid and if defragged link is different from the defragged url
        for e in et.iter('a', 'A'):
            try:
                link = urldefrag(e.attrib['href'])[0]
                if link != urldefrag(url)[0] and is_valid(link):
                    result.append(link.rstrip('/ '))
            
            except:
                try:
                    link = urldefrag(e.attrib['HREF'])[0]
                    if link != urldefrag(url)[0] and is_valid(link):
                        result.append(link.rstrip('/ '))
                
                except:
                    pass

    else:
        # Print non-200 status codes in red for better visibility
        print(Fore.RED, resp.status, ": ", resp.error, Fore.RESET)

    return result

def is_valid(url):
    try:
        parsed = urlparse(url)
        
        # Checks if url contains any invalid symbols
        if not re.match(r"^(?:http(s)?://)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$", url):
            return False

        # Checks if scheme is valid
        if parsed.scheme not in set(["http", "https"]):
            return False

        urlSplit = url.rstrip(' /').split('/')
               
        urlSplitLen = len(urlSplit)
        if urlSplitLen > 4:
            for i in range(3, urlSplitLen - 1):
                if urlSplit[i] in urlSplit[i+1:]:
                    return False

        '''
        # Prevents infinite loop when applying absolute link to page such as uci.edu/news/index.php -> uci.edu/news/news/index.php...
        if re.match(r"^[\w\-. ]+\.[a-zA-Z0-9].*", urlSplit[-1]):
            if urlSplit[-2] in urlSplit[-3::-1]:
                return False
        # Prevents infinite loop when applying absolute link to same page such as uci.edu/news/news/news...
        else:
            if urlSplit[-1] in urlSplit[-2::-1]:
                return False
        '''

        # Blacklist
        if re.match(
            r"^.*today\.uci\.edu/department/information_computer_sciences/calendar.*"
#            + r"|^.*ics\.uci\.edu/community/.*\.php"
#            + r"|^.*evoke\.ics\.uci\.edu.*"
#            + r"|^.*ics\.uci\.edu/eppstein/pix.*"
#            + r"|^.*ics\.uci\.edu/alumni.*"
#            + r"|^.*alumni\.ics\.uci\.edu.*"
#            + r"|^.*timesheet\.ics\.uci\.edu.*"
#            + r"|^.*intranet\.ics\.uci\.edu/index\.phtml.*Please\+login.*"
#            + r"|^.*informatics\.uci\.edu/explore/books-we-have-written.*"
#            + r"|^.*hack\.ics\.uci\.edu/category/photos.*"
#            + r"|^.*hack\.ics\.uci\.edu/2015/11/23/hackuci-2015-gallery.*"
#            + r"|^.*archive\.ics\.uci\.edu/ml/machine-learning-databases.*"
#            + r"|^.*ics\.uci\.edu/honors/advising/advising.*"
#            + r"|^.*ics\.uci\.edu/.*\.php"
#            + r"|^.*ics\.uci\.edu/.*.php.*\.php.*"
            + r"|^.*\.ics.uci.edu/honors/index\.php"
            + r"|^.*\.ics\.uci\.edu/ugrad/current/policies/index\.php"
            + r"|^.*archive\.ics\.uci\.edu/ml/datasets\.php\?"
            + r"|^.*wics\.ics\.uci\.edu/events/today.*"
            + r"|^.*wics\.ics\.uci\.edu/events/.*[0-9]{4}-[0-9]{2}.*", url):
            return False
        
        # Makes sure links from today.uci.edu are all within /department/information_computer_sciences/
        if re.match(r"^(www.)?today\.uci\.edu", parsed.netloc.lower()):
            if not re.match(r"^(/department/information_computer_sciences/).*", parsed.path):
                return False
        
        # Makes sure links are within seeded domains
        elif not re.match(
            r"^([a-zA-Z0-9]+\.)*cs\.uci\.edu"
            + r"|^([a-zA-Z0-9]+\.)*ics\.uci\.edu"
            + r"|^([a-zA-Z0-9]+\.)*informatics\.uci\.edu"
            + r"|^([a-zA-Z0-9]+\.)*stat\.uci\.edu", parsed.netloc.lower()):
            return False
        
        # Checks if url has unwanted file extension
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|mpg"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|txt|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|img"
            + r"|dtd|_.DS_Store|ppsx|py|c|cpp|java|h|data|sql)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

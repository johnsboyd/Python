import re
import requests
import sys
import time
from bs4 import BeautifulSoup

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}

def fetch_results(search_term):
    assert isinstance(search_term, str), 'Search term must be a string'
    escaped_search_term = search_term.replace(' ', '+')
    escaped_search_term += '+site:genius.com'
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, 1, 'en')
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response

def parse_results(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    link = soup.find("div", class_="r").find('a')['href']
    return link

def parse_lyric(url):
    song_r = requests.get(url)
    song_soup = BeautifulSoup(song_r.text, 'html.parser')
    rawtext = song_soup.find("div", class_="lyrics").get_text()
    rawtext = rawtext.replace('-',' ')
    rawtext = rawtext.replace(';','')
    rawtext = rawtext.replace('.','')
    rawtext = rawtext.replace('’',"'")
    rawtext = rawtext.replace('`',"'")
    rawtext = re.sub(r'[()"]', '', rawtext)
    rawtext = re.sub(r"\[(.)*\]", '', rawtext)
    rawtext = re.sub(r'[\n]+', '\n', rawtext)
    return rawtext

def print_lyric(query):
    try:
        src = fetch_results(query)
        link = parse_results(src)
        lyric = parse_lyric(link)
        info = link.replace('https://genius.com/','')
        return info, lyric
    except AttributeError:
        raise Exception("Query retrieved null results")
    except AssertionError:
        raise Exception("Incorrect arguments parsed to function")
    except requests.HTTPError:
        raise Exception("You appear to have been blocked by Google")
    except requests.RequestException:
        raise Exception("Appears to be an issue with your connection")

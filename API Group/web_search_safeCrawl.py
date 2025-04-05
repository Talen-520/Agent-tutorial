from googlesearch import search
import json
from bs4 import BeautifulSoup
import requests
import textwrap
import urllib.robotparser
import time
import random

def is_crawlable(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        robot_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robot_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception as e:
        print(f"Error checking robots.txt: {e}")
        return True  # Assume crawlable if robots.txt check fails

def crawl_website(url):
    try:
        time.sleep(1) # Add delay to avoid being blocked.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        # remove unwanted tags
        for tag in soup(['script', 'style', 'meta', 'img', 'footer', 'header', 'form', 'nav', 'aside', 'svg', 'canvas', 'link']):
            tag.decompose()
        return soup.get_text(separator=' ', strip=True)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"Rate limited. Retrying {url} after delay.")
            time.sleep(random.randint(2, 5))  # Add random delay.
            return crawl_website(url)  # retry the function.
        else:
            print(f"Error during web crawling: {e}")
            return ""
    except Exception as e:
        print(f"General Error during web crawling: {e}")
        return ""

def web_search(query):
    try:
        serializable_results = []
        for result in search(query, num_results=2, advanced=True):
            # Check if the URL is crawlable, if not, skip it.
            if is_crawlable(result.url):
                serializable_result = {
                    'title': result.title,
                    'url': result.url,
                    'description': textwrap.shorten(result.description, width=200, placeholder="..."),
                    'content': crawl_website(result.url),
                }
                serializable_results.append(serializable_result)
            else:
                print(f"Skipping {result.url} due to robots.txt restrictions.")
        return json.dumps(serializable_results, indent=4)
    except Exception as e:
        print(f"Error during web search: {e}")
        return json.dumps([], indent=4) # return empty json array.

search_results = web_search("Yahoo Finance news Nvidia")
print(search_results)
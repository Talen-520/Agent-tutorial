from googlesearch import search
import json
from bs4 import BeautifulSoup
import requests
import textwrap
# uv add googlesearch-python
# uv add beautifulsoup4
def web_search(query):
    try:
        # result in {title, href, description}
        serializable_results = []
        for result in search(query, num_results=2, advanced=True):
            serializable_result = {
                'title': result.title,
                'url': result.url,
                'description': textwrap.shorten(result.description, width=200, placeholder="..."),
                # optional
                'content': crawl_website(result.url),
            }
            serializable_results.append(serializable_result)
        return json.dumps(serializable_results, indent=4)
    except Exception as e:
        print(f"Error during web search: {e}")
        return []


def crawl_website(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        # remove unwanted tags
        for tag in soup(['script', 'style', 'meta', 'img', 'footer', 'header','form', 'nav', 'aside', 'svg', 'canvas', 'link']):
            tag.decompose()
        # print(soup)
        # <p class="content">This is some <b>bold</b> text.</p> 
        # after get_text() it will be: This is some bold text.
        return soup.get_text(separator=' ', strip=True)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"Rate limited. Retrying {url} after delay.")
            time.sleep(random.randint(2, 5)) # Add random delay.
            return crawl_website(url) # retry the function.
        else:
            print(f"Error during web crawling: {e}")
            return 
    except Exception as e:
        print(f"General Error during web crawling: {e}")
        return ""


search_results = web_search("Yahoo Finance news Nvidia")
print(search_results)

#for result in json.loads(search_results):
 #   print(f"Title: {result['title']}\nURL: {result['url']}\nDescription: {result['description']}\n")

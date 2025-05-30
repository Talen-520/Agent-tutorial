# uv add googlesearch-python beautifulsoup4 requestsAdd commentMore actions
from googlesearch import search
import json
from bs4 import BeautifulSoup
import requests
import textwrap
import time
import random


def crawl_website(url):

    headers = {
        # Using a more common and recent User-Agent string to mimic a real browser
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    
    try:
        # Introduce a small random delay before making the request to be less aggressive
        time.sleep(random.uniform(1, 3)) 
        
        response = requests.get(url, headers=headers, timeout=10) # Added timeout for requests
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove unwanted tags that typically don't contain main content
        for tag in soup(['script', 'style', 'meta', 'img', 'footer', 'header', 'form', 'nav', 'aside', 'svg', 'canvas', 'link', 'iframe']):
            tag.decompose() # Remove the tag and its contents

        # Get all text, separating blocks with a space and stripping leading/trailing whitespace
        return soup.get_text(separator=' ', strip=True)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Error 403 Forbidden: Access denied for URL: {url}. This site might have strong anti-scraping measures.")
            return "" # Return empty string as we cannot access the content
        elif e.response.status_code == 429:
            print(f"Error 429 Rate Limited: Retrying {url} after a delay.")
            time.sleep(random.randint(5, 10)) # Wait longer for rate limiting
            return crawl_website(url) # Retry the function
        else:
            print(f"HTTP Error {e.response.status_code} during web crawling: {e} for URL: {url}")
            return "" # Return empty string for other HTTP errors
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to {url}. Details: {e}")
        return ""
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: Request to {url} timed out. Details: {e}")
        return ""
    except Exception as e:
        print(f"General Error during web crawling for URL {url}: {e}")
        return ""


def web_search(query):
    """
    Performs a web search using Google and optionally crawls the top 2 results.
    Returns results as a JSON formatted string.
    """
    serializable_results = []
    try:
        # Perform the search, getting up to 2 advanced results
        for result in search(query, num_results=2, advanced=True):
            # Create a dictionary for each search result
            serializable_result = {
                'title': result.title,
                'url': result.url,
                'description': textwrap.shorten(result.description, width=200, placeholder="..."),
                # Call crawl_website to get the content of the URL
                'content': crawl_website(result.url),
            }
            serializable_results.append(serializable_result)
        
        # Return the list of results as a pretty-printed JSON string
        return json.dumps(serializable_results, indent=4, ensure_ascii=False) # ensure_ascii=False to correctly display Chinese characters
    except Exception as e:
        print(f"Error during web search: {e}")
        return json.dumps({"error": str(e)}, indent=4, ensure_ascii=False) # Return error in JSON format


if __name__ == "__main__":
    # Example usage: Search for "凡人修仙传" and print the results
    search_results = web_search("英伟达新闻")
    print(search_results)
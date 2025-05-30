from googlesearch import search
import json
from bs4 import BeautifulSoup
import requests
import textwrap
import urllib.robotparser
import time
import random
from urllib.parse import urlparse

# Define a consistent User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def fetch_robots_txt(robots_url_to_fetch):
    """
    Fetches the robots.txt file from the given URL.
    Uses a common browser User-Agent.
    arg:
        robots_url_to_fetch (str): The URL of the robots.txt file to fetch.
    return:
        str: The content of the robots.txt file, or None if it couldn't be fetched.
    """
    print(f"Attempting to fetch robots.txt from: {robots_url_to_fetch}")
    try:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/plain",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(robots_url_to_fetch, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"Successfully fetched robots.txt from: {robots_url_to_fetch}")
            return response.text
        else:
            print(f"Failed to fetch robots.txt from {robots_url_to_fetch}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e: # Catching a broader range of request-related errors
        print(f"Error fetching robots.txt from {robots_url_to_fetch}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching robots.txt from {robots_url_to_fetch}: {e}")
        return None

def is_crawlable(page_url):
    """
    Checks if a given page_url is crawlable according to its domain's robots.txt.
    arg:
        page_url (str): The URL of the page to check.
    return:
        bool: True if the page is crawlable, False otherwise.
    """
    parsed_url = urlparse(page_url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc

    if not scheme or not netloc:
        print(f"Invalid URL (missing scheme or domain): {page_url}. Assuming not crawlable.")
        return False

    # Construct the URL for robots.txt
    # (e.g., for http://www.example.com/somepage/index.html -> http://www.example.com/robots.txt)
    robot_url = f"{scheme}://{netloc}/robots.txt"

    robots_content = fetch_robots_txt(robot_url)

    if robots_content is None:
        # If robots.txt is missing or inaccessible, a common policy is to assume crawlable.
        print(f"无法获取或解析 {robot_url}，默认允许爬取: {page_url}")
        return True

    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(robots_content.splitlines())

        # Check if our specific User-Agent is allowed to fetch the page_url
        can_fetch = rp.can_fetch(USER_AGENT, page_url)
        print(f"爬取权限检查 - URL: {page_url}, User-Agent: {USER_AGENT}, 允许: {can_fetch}")
        return can_fetch
    except Exception as e:
        print(f"解析robots.txt内容时发生错误 ({robot_url}): {e}，默认允许爬取: {page_url}")
        return True # Default to crawlable if there's an error during parsing.


def crawl_website(url):
    """
    Crawls the given URL and extracts textual content.
    Includes polite random delays and User-Agent spoofing.
    arg:
        url (str): The URL to crawl.
    return:
        str: Extracted text content from the page.
    """
    try:
        # Random delay between 1 and 3 seconds for politeness
        time.sleep(random.uniform(1, 3))
        print(f"Crawling: {url}")
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)

        soup = BeautifulSoup(response.content, "html.parser")
        # Remove common non-content tags
        for tag in soup(['script', 'style', 'meta', 'img', 'footer', 'header', 'form', 'nav', 'aside', 'svg', 'canvas', 'link', 'iframe', 'noscript', 'link']):
            tag.decompose()
        
        content = soup.get_text(separator=' ', strip=True)
        print(f"Successfully crawled and extracted content from: {url}")
        return content

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429: # Too Many Requests
            retry_delay = random.uniform(5, 10) # Retry after a longer, random delay
            print(f"速率限制 (429) for {url}，等待 {retry_delay:.2f} 秒后重试...")
            time.sleep(retry_delay)
            return crawl_website(url) # Recursive call to retry
        else:
            print(f"HTTP错误 [{e.response.status_code}] 爬取页面: {url}")
            return ""
    except requests.exceptions.RequestException as e: # Other request errors (timeout, connection error, etc.)
        print(f"爬取页面时发生请求错误: {url} - {type(e).__name__}: {str(e)}")
        return ""
    except Exception as e: # Catch any other unexpected errors during crawling/parsing
        print(f"爬取或解析页面时发生未知错误: {url} - {type(e).__name__}: {str(e)}")
        return ""

def web_search(query):
    """
    Performs a web search, checks robots.txt, crawls allowed pages,
    and returns results as a JSON string.
    arg:
        query (str): The search query.
    return:
        str: JSON string of search results with title, URL, description, and content.
    """
    try:
        serializable_results = []
        # Using iterator directly from search to process one by one
        search_results_iterator = search(query, num_results=5, advanced=True, sleep_interval=1, timeout=5)
        
        for result in search_results_iterator:
            print(f"\nProcessing search result: {result.title} ({result.url})")
            if is_crawlable(result.url):
                content = crawl_website(result.url)
                if content:  # Only add to results if content was successfully fetched
                    serializable_results.append({
                        'title': result.title,
                        'url': result.url,
                        'description': textwrap.shorten(result.description or "", width=200, placeholder="..."),
                        'content': textwrap.shorten(content, width=500, placeholder="... (content truncated)"), # Shorten content for summary
                    })
                else:
                    print(f"内容为空或爬取失败: {result.url}")
            else:
                print(f"跳过不允许爬取的URL (根据robots.txt): {result.url}")
        
        return json.dumps(serializable_results, indent=4, ensure_ascii=False)
    
    except Exception as e:
        print(f"网络搜索或处理过程中发生错误: {type(e).__name__} - {str(e)}")
        return json.dumps([], indent=4)

if __name__ == "__main__":
    print("开始搜索Nvidia新闻...")
    # Make sure to have internet connection for this to work.
    # The 'googlesearch' library can sometimes be unreliable or get blocked.
    search_json_output = web_search("Nvidia news")
    print("\n--- 搜索结果 (JSON) ---")
    print(search_json_output)
    print("\n--- 搜索完成 ---")
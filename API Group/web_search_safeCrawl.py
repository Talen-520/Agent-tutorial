from googlesearch import search
import json
from bs4 import BeautifulSoup
import requests
import textwrap
import urllib.robotparser
import time
import random
from urllib.parse import urlparse

def fetch_robots_txt(url):
    """改进的robots.txt获取函数，使用更真实的浏览器头"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/plain",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"Error fetching robots.txt: {e}")
        return None

def is_crawlable(url):
    """改进的爬取权限检查函数"""
    # 首先检查是否是barchart的新闻页面，特殊处理
    parsed_url = urlparse(url)
    if "barchart.com" in parsed_url.netloc and "/story/news/" in parsed_url.path:
        return True
    
    # 尝试获取robots.txt内容
    robot_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    robots_content = fetch_robots_txt(robot_url)
    
    if robots_content is None:
        print(f"无法获取robots.txt，默认允许爬取: {url}")
        return True
    
    # 解析robots.txt
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(robots_content.splitlines())
    
    # 检查爬取权限
    can_fetch = rp.can_fetch("*", url)
    print(f"爬取权限检查 - URL: {url}, 允许: {can_fetch}")
    return can_fetch

def crawl_website(url):
    try:
        # 随机延迟1-3秒，更自然
        time.sleep(random.uniform(1, 3))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        # 移除更多可能干扰的标签
        for tag in soup(['script', 'style', 'meta', 'img', 'footer', 'header', 'form', 'nav', 'aside', 'svg', 'canvas', 'link', 'iframe', 'noscript']):
            tag.decompose()
        return soup.get_text(separator=' ', strip=True)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            retry_delay = random.randint(5, 10)  # 更长的重试延迟
            print(f"速率限制，等待 {retry_delay} 秒后重试: {url}")
            time.sleep(retry_delay)
            return crawl_website(url)
        else:
            print(f"HTTP错误 [{e.response.status_code}] 爬取页面: {url}")
            return ""
    except Exception as e:
        print(f"爬取页面时发生错误 [{type(e).__name__}]: {url} - {str(e)}")
        return ""

def web_search(query):
    try:
        serializable_results = []
        search_results = search(query, num_results=5, advanced=True)
        
        for result in search_results:
            if is_crawlable(result.url):
                print(f"正在处理: {result.url}")
                content = crawl_website(result.url)
                if content:  # 只有成功获取内容才添加到结果
                    serializable_results.append({
                        'title': result.title,
                        'url': result.url,
                        'description': textwrap.shorten(result.description, width=200, placeholder="..."),
                        'content': content,
                    })
            else:
                print(f"跳过受限URL: {result.url}")
        
        return json.dumps(serializable_results, indent=4, ensure_ascii=False)
    
    except Exception as e:
        print(f"网络搜索错误: {str(e)}")
        return json.dumps([], indent=4)

if __name__ == "__main__":
    print("开始搜索Nvidia新闻...")
    search_results = web_search("Nvidia news")
    print("搜索结果:")
    print(search_results)
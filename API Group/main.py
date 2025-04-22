import requests
from bs4 import BeautifulSoup
import re

def get_yahoo_article_text(url):
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        # 发送请求获取页面内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取标题
        title_element = soup.find(class_=re.compile(r'cover-title yf-\w+'))
        title_text = title_element.get_text().strip() if title_element else "No title found"
        
        # 清理标题中的特殊字符和多余空格
        title_text = re.sub(r'[\xa0\u200b]+', ' ', title_text)
        title_text = re.sub(r'\s+', ' ', title_text)

        # 找到文章主体 - 新版雅虎财经结构
        content_text = soup.find('div', class_='atoms-wrapper')
        
        if not content_text:
            return {
                'title': title_text,
                'content': "No content found"
            }
        
        # 获取所有段落文本
        paragraphs = []
        for p in content_text.find_all('p'):
            # 过滤掉空段落或特定内容的段落
            text = p.get_text().strip()
            if text and not text.startswith(('Read more:', 'Related:', 'Follow us on')):
                # 清理文本中的特殊字符和多余空格
                text = re.sub(r'[\xa0\u200b]+', ' ', text)
                text = re.sub(r'\s+', ' ', text)
                paragraphs.append(text)
        
        # 合并段落并确保格式整洁
        content_text = '\n\n'.join(paragraphs)
        
        return {
            'title': title_text,
            'content': content_text if content_text else "No content available"
        }
    
    except requests.exceptions.RequestException as e:
        return {
            'title': "Error",
            'content': f"请求页面时出错: {str(e)}"
        }
    except Exception as e:
        return {
            'title': "Error",
            'content': f"处理文章内容时出错: {str(e)}"
        }

# 使用示例
url = "https://finance.yahoo.com/news/ai-stock-nvidia-broadcom-better-190000358.html"
article_data = get_yahoo_article_text(url)
print(article_data)
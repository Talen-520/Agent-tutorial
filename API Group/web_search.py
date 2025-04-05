from googlesearch import search
from bs4 import BeautifulSoup
import requests

def web_search(query):
    try:
        # result in {title, url, description}
        results = list(search(query, num_results=2, advanced=True))
        print("all in one: ",result)

        for result in results:
            print("title: ",result.title)
            print("url: ",result.url)
            print("description: ",result.description)
            print()
        return result
    except Exception as e:
        print(f"Error during web search: {e}")
        return []

web_search("Yahoo Finance news Nvidia")

# uv add googlesearch-python
from googlesearch import search

def web_search(query):
    search_results = list(search(query, num_results=2, advanced=True))
    print("All results (raw objects): ", search_results)
    print("--" * 20)

    for result_item in search_results:
        print("title: ", result_item.title)
        print("url: ", result_item.url)
        print("description: ", result_item.description)
        print()

    return search_results


# Example usage:
if __name__ == "__main__":
    found_results = web_search("bilibili")
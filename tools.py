from  langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """"Search The web for research and reliable information on the topic . Return Titles  , URLs and and snippets"""
    results=tavily.search(query=query, max_results=5)
    out=[]
    for r in results['results']:
        out.append(
            f"Title:{r['title']} \nURL:{r['url']} \nSnippet:{r['content'][:300]}\n\n"
        )

    return"\n----\n".join(out)
# print(web_search("What is the latest research on AI in healthcare?"))


@tool
def scrap_url(url : str) -> str:
    """"Scrape the content and return text content from  a given  URL for deeper reading """
    try:
        response = requests.get(url,timeout=10,headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style','nav','footer']):
            tag.decompose()
        return soup.get_text(separator='', strip=True)[:3000]
    except Exception as e:
        print(f"Error occurred while scraping {url}: {e}")
        return "Error occurred while scraping the URL."

if __name__ == "__main__":
    print(scrap_url.invoke("https://hindustantimes.com/technology/ai-is-transforming-healthcare-from-diagnosis-to-treatment-101681187091059.html"))
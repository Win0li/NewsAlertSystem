import httpx
import os
from dotenv import load_dotenv


load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

async def fetch_news(keyword: str):
    headers = {
        "Authorization" : NEWS_API_KEY
    }
    params = {
        "q": keyword,
        "sortBy": "publishedAt",
        "language: en"
        "pageSize": 10  # limit articles per request
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(NEWS_API_URL, params=params, headers=headers)
        response.raise_for_status()

    data = response.json()

    articles = []
    for article in data.get("articles", []):
        articles.append({
            "name": article["title"],
            "url": article["url"],
            "datePublished": article["publishedAt"],
            "provider": [{"name": article["source"]["name"]}],
        })

    return articles
    
    


import httpx
import os

BING_API_KEY = os.getenv("BING_API_KEY")
BING_API_URL = "https://api.bing.microsoft.com/v7.0/news/search"

async def fetch_news(keyword: str):
    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY
    }
    params = {
        "q": keyword,
        "mkt": "en-US",
        "sortBy": "Date",
        "count": 10  # limit articles per request
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(BING_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("value", [])
    
    


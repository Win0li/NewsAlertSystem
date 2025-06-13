from apscheduler.schedulers.background import BackgroundScheduler
import asyncio 
from .api_clients.bing_api import fetch_news

KEYWORDS = ["OpenAI", "China", "Stock Market", "SpaceX"]

async def run_job():
    
    for keyword in KEYWORDS:
        articles = await fetch_news(keyword)
        print(f"Articles for '{keyword}':")
        for article in articles:
            print(article['name'], "-", article['url'])

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(run_job, 'interval', minutes=5)
    scheduler.start()



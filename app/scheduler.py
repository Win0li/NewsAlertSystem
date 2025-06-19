from apscheduler.schedulers.background import BackgroundScheduler
import asyncio 
from .api_clients.bing_api import fetch_news
from .models import SessionLocal, Article
from datetime import datetime

KEYWORDS = ["OpenAI", "China", "Stock Market", "SpaceX"]

def run_job():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    db = SessionLocal()

    try: 
        for keyword in KEYWORDS:
            articles = loop.run_until_complete(fetch_news(keyword))
            for article in articles:
                existing = db.query(Article).filter_by(url=article["url"]).first()
                if existing:
                    continue
                
                new_article = Article(
                    title=article["name"],
                    url=article["url"],
                    published_at=datetime.fromisoformat(article["datePublished"].rstrip("Z")),
                    source=article.get("provider", [{}])[0].get("name", "Unknown"),
                    keyword=keyword)
                
                db.add(new_article)
        db.commit()
    
    except Exception as e:
        print("Error in run_job:", e)
    finally:
        db.close()

        

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(run_job, 'interval', minutes=5)
    scheduler.start()



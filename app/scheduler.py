from apscheduler.schedulers.background import BackgroundScheduler
import asyncio 
from .api_clients.news_api import fetch_news
from .models import Article, User
from datetime import datetime
from app.utils.alerts import send_email_alert
from .database import SessionLocal, KEYWORDS
import collections




def run_job():
    """
    Scheduled job to:
    1. Fetch news articles for predefined keywords using Bing API
    2. Deduplicate and store new articles in the database
    3. Identify users interested in those keywords
    4. Send each user a single email summarizing relevant new articles
    """
    print(f"[{datetime.now().isoformat()}] 🔄 run_job() started")
    
    # Create a fresh asyncio event loop for this background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    db = SessionLocal()

    # Store deduplicated articles by keyword
    keyword_to_articles = collections.defaultdict(list)

    # Map user email → list of articles to send
    user_alerts = collections.defaultdict(list)


    try:
        seen_urls = set()
        for keyword in KEYWORDS:
            # Fetch latest news articles for this keyword
            articles = loop.run_until_complete(fetch_news(keyword))
            for article in articles:
                # Skip if article already exists in the current staging process
                if article["url"] in seen_urls:
                    continue
                # Skip if article already exists in the DB
                existing = db.query(Article).filter_by(url=article["url"]).first()
                if existing:
                    continue
                
                seen_urls.add(article["url"])

                # Store in keyword dictionary
                keyword_to_articles[keyword].append(article)

                # Create and stage new article record for DB
                new_article = Article(
                    title=article["name"],
                    url=article["url"],
                    published_at=datetime.fromisoformat(article["datePublished"].rstrip("Z")),
                    source=article.get("source", "Unknown"),
                    keyword=keyword)

                db.add(new_article)
            # Persist all new articles
            print("breakpoint 1")
            # Identify users subscribed to this keyword
            matching_users = db.query(User).filter(User.keywords.any(keyword)).all()
            print("breakpoint 2")
            for user in matching_users:
                # Extend user's article list with all new articles for this keyword
                user_alerts[user.email].extend(keyword_to_articles[keyword])
            print("breakpoint 3")
        db.commit()
       
        print("breakpoint 4")
       
        # Send one email per user summarizing new articles
        
        for email, articles in user_alerts.items():
            body = generate_email_body(articles)
            loop.run_until_complete(send_email_alert(email, "NewsDrop Update", body))

        
        print(f"[{datetime.now().isoformat()}] ✅ run_job() completed successfully")
    
    except Exception as e:
        print("Error in run_job:", e)
        print(f"[{datetime.now().isoformat()}] ❌ Error in run_job: {e}")

    finally:
        db.close()


def generate_email_body(articles):
    body = "<h3>New Articles:</h3><ul>"
    for a in articles:
        body += f"<li><a href='{a['url']}'>{a['name']}</a></li>"
    body += "</ul>"
    return body

# Background scheduler instance used to run polling job periodically
scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Starts the background scheduler to run the job every 5 minutes.
    """
    scheduler.add_job(run_job, 'interval', minutes=5)
    scheduler.start()
    run_job()


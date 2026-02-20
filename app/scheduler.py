from __future__ import annotations

import asyncio
import collections
import os
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from .database import SessionLocal, KEYWORDS
from .ingestors.news_api import fetch_news
from .models import Article, User
from .utils.alerts import send_email_alert

# NEW: Truth RSS ingestor
from .ingestors.truthsocialrss import poll_once as poll_truth_once


# --------- Scheduler (single instance) ----------
scheduler = BackgroundScheduler()
_NEWS_JOB_ID = "newsapi_poll"
_TRUTH_JOB_ID = "truth_rss_poll"


def _get_or_create_loop() -> asyncio.AbstractEventLoop:
    """
    APScheduler runs jobs in a background thread.
    That thread often has no event loop. Create one once per thread.
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


# --------- NEWSAPI JOB (your existing logic, cleaned slightly) ----------
def run_news_job():
    print(f"[{datetime.now().isoformat()}] run_news_job() started")

    loop = _get_or_create_loop()
    db = SessionLocal()

    keyword_to_articles = collections.defaultdict(list)  # keyword -> new articles
    user_alerts = collections.defaultdict(list)          # email -> list of articles

    try:
        seen_urls = set()

        for keyword in KEYWORDS:
            articles = loop.run_until_complete(fetch_news(keyword))

            for article in articles:
                url = article.get("url")
                if not url:
                    continue

                if url in seen_urls:
                    continue

                # DB dedup
                existing = db.query(Article).filter_by(url=url).first()
                if existing:
                    continue

                seen_urls.add(url)

                keyword_to_articles[keyword].append(article)

                # Create Article row
                published_raw = (article.get("datePublished") or "").rstrip("Z")
                published_at = None
                try:
                    if published_raw:
                        published_at = datetime.fromisoformat(published_raw)
                except Exception:
                    published_at = datetime.utcnow()

                new_article = Article(
                    title=article.get("name", ""),
                    url=url,
                    published_at=published_at or datetime.utcnow(),
                    source=article.get("source", "Unknown"),
                    keyword=keyword,
                )
                db.add(new_article)

            # Users subscribed to this keyword
            matching_users = db.query(User).filter(User.keywords.any(keyword)).all()
            for user in matching_users:
                user_alerts[user.email].extend(keyword_to_articles[keyword])

        db.commit()

        # One email per user
        for email, arts in user_alerts.items():
            if not arts:
                continue
            body = generate_email_body(arts)
            loop.run_until_complete(send_email_alert(email, "NewsDrop Update", body))

        print(f"[{datetime.now().isoformat()}] run_news_job() completed")

    except Exception as e:
        db.rollback()
        print(f"[{datetime.now().isoformat()}] ERROR in run_news_job: {e}")

    finally:
        db.close()


def generate_email_body(articles):
    body = "<h3>New Articles:</h3><ul>"
    for a in articles:
        name = a.get("name") or a.get("title") or "Link"
        url = a.get("url", "#")
        body += f"<li><a href='{url}'>{name}</a></li>"
    body += "</ul>"
    return body


# --------- TRUTH RSS JOB (dedup + alert) ----------
# V0 persistent dedup: store keys in-memory.
# Replace with DB table later if you want dedup across restarts.
_truth_seen_links: set[str] = set()
_truth_primed: bool = False


def _truth_alert_recipient() -> Optional[str]:
    """
    Where should Truth alerts go?
    Set ALERT_EMAIL_TO in .env (or your shell) to route them.
    """
    return os.getenv("ALERT_EMAIL_TO")


def _format_truth_email(item: dict) -> str:
    title = item.get("title", "").strip()
    link = item.get("link", "").strip()
    desc = item.get("description", "").strip()

    # Keep it simple; you can style later
    body = f"<h3>Truth Social: New Post</h3>"
    if title:
        body += f"<p><b>{title}</b></p>"
    if desc:
        body += f"<p>{desc}</p>"
    if link:
        body += f"<p><a href='{link}'>{link}</a></p>"
    return body


def run_truth_rss_job():
    global _truth_primed

    print(f"[{datetime.now().isoformat()}] run_truth_rss_job() started")

    loop = _get_or_create_loop()

    try:
        items = poll_truth_once()  # list[dict] with title/link/description/source
        # Oldest-first alerting feels nicer
        items = list(reversed(items))

        # Prime on first run to avoid spamming existing feed items
        if not _truth_primed:
            for it in items:
                link = (it.get("link") or "").strip()
                if link:
                    _truth_seen_links.add(link)
            _truth_primed = True
            print(f"[{datetime.now().isoformat()}] run_truth_rss_job() primed ({len(_truth_seen_links)} seen)")
            return

        new_items = []
        for it in items:
            link = (it.get("link") or "").strip()
            if not link:
                continue
            if link in _truth_seen_links:
                continue
            _truth_seen_links.add(link)
            new_items.append(it)

        if not new_items:
            print(f"[{datetime.now().isoformat()}] run_truth_rss_job() no new items")
            return

        to_email = _truth_alert_recipient()
        if not to_email:
            # fallback: print if no recipient configured
            for it in new_items:
                print("[TRUTH ALERT]", it.get("title", ""), it.get("link", ""))
            return

        for it in new_items:
            body = _format_truth_email(it)
            loop.run_until_complete(send_email_alert(to_email, "Truth Social Alert (Unconfirmed)", body))

        print(f"[{datetime.now().isoformat()}] run_truth_rss_job() alerted {len(new_items)} items")

    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ERROR in run_truth_rss_job: {e}")


# --------- Scheduler control ----------
def start_scheduler():
    """
    Start scheduler (idempotent) and register jobs once.
    """
    # Avoid duplicate jobs if endpoint called twice
    existing_ids = {job.id for job in scheduler.get_jobs()}

    # if _NEWS_JOB_ID not in existing_ids:
    #     scheduler.add_job(
    #         run_news_job,
    #         "interval",
    #         minutes=5,
    #         id=_NEWS_JOB_ID,
    #         replace_existing=True,
    #         max_instances=1,
    #         coalesce=True,
    #         misfire_grace_time=60,
    #     )

    if _TRUTH_JOB_ID not in existing_ids:
        scheduler.add_job(
            run_truth_rss_job,
            "interval",
            seconds=15,
            id=_TRUTH_JOB_ID,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=30,
        )

    if not scheduler.running:
        scheduler.start()

    

    # Optional: run each once immediately
    run_truth_rss_job()
    # run_news_job()  # uncomment if you want instant NewsAPI run too


def stop_scheduler():
    """
    Stop scheduler safely.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
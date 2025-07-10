# 📰 NewsDropTracker

**NewsDropTracker** is an intelligent, keyword-based news alert system. It automatically fetches the latest articles from NewsAPI, stores them in a PostgreSQL database, and sends email alerts to subscribed users based on their selected topics — all on a scheduled interval using FastAPI and async background jobs.

---

## 🚀 Features

- 🔍 Periodic news scraping based on predefined keywords (e.g., “OpenAI”, “SpaceX”)
- 🗃️ Stores unique articles in a PostgreSQL database
- 📬 Sends automated email alerts to users when new articles match their keywords
- 🧠 Built using FastAPI, SQLAlchemy, APScheduler, and Mailgun
- 🔐 Environment-based configuration with `.env` support

---

## 🛆 Tech Stack

- **Backend:** FastAPI, SQLAlchemy
- **Scheduler:** APScheduler (runs background job every 5 minutes)
- **Database:** PostgreSQL
- **Email Service:** Mailgun SMTP + REST API
- **Async Client:** `httpx`

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourname/newsdroptracker.git
cd newsdroptracker
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your `.env` file

Create a `.env` file in the root directory and configure the following:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<your_db>
NEWS_API_KEY=your_newsapi_key
MAILGUN_API_KEY=your_mailgun_api_key
MAILGUN_USERNAME=your_smtp_username
MAILGUN_PASSWORD=your_smtp_password
MAILGUN_FROM=your_domain_name_here
```

### 5. Initialize the database

```bash
python -m app.scripts.init_db
```

### 6. Run the app

```bash
uvicorn app.main:app --reload
```

---

## 🧲 API Endpoints

Visit `http://localhost:8000/docs` to access the interactive Swagger UI.

Example endpoints:

- `POST /create_user` – Add a user to receive alerts
- `POST /send_email` – Manually test sending an email
- `GET /` – Health check

---

## 📬 Email Alerts

The system sends email alerts for new articles using **Mailgun**, via either:

- SMTP (used in `FastMail` async alerts)
- REST API (used in `/send_email` route for testing)

---

## 🗕️ Scheduler

The scheduler runs every 5 minutes to:

- Fetch the latest articles for each keyword
- Insert new articles into the database
- Identify matching users
- Send alerts via email

You can manually start or stop the scheduler using the `start_scheduler()` function in `scheduler.py`.

---

## 🛠️ Development Notes

- Use `logging` or `print` statements to monitor runtime performance (current run time is \~6 seconds per cycle).
- Future plans: add user authentication, frontend dashboard, or use Redis + Celery for scaling.

---

## 📄 License

This project is licensed under MIT. Feel free to fork, modify, and use it with attribution.

---

## ✍️ Author

Built by Winston

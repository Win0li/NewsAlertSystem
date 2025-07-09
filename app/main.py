from contextlib import asynccontextmanager
from fastapi import FastAPI
from .scheduler import start_scheduler, scheduler
from .routes import users
from .utils import alerts



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan= lifespan)
app.include_router(users.router)
app.include_router(alerts.router)

@app.get("/")
def read_root():
    return {"message": "News Tracker is running"}

@app.post("/start-scheduler")
def start_scheduler_endpoint():
    try:
        start_scheduler()
        return {"status": "Scheduler started"}
    except Exception as e:
        print(f"Exception during lifespan: {e}")
        raise 
    

@app.post("/stop-scheduler")
def stop_scheduler_endpoint():
    try:
        scheduler.shutdown()
        return {"status": "Scheduler stopped"}
    except Exception as e:
        return {"error": str(e)}
    
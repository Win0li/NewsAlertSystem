from contextlib import asynccontextmanager

from fastapi import FastAPI

from .scheduler import start_scheduler, scheduler



@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        start_scheduler()
        yield
    except Exception as e:
        print(f"Exception during lifespan: {e}")
        raise
    finally:
        try:
            scheduler.shutdown()
        except Exception as e:
            print(f"Error during scheduler shutdown: {e}")



app = FastAPI(lifespan= lifespan)

@app.get("/")
def read_root():
    return {"message": "News Tracker is running"}


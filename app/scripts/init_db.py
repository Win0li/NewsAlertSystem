from app.database import Base, engine
from app.models import User, Article

try:
    with engine.connect() as conn:
        print("✅ Successfully connected to the database!")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
except Exception as e:
    print("❌ Connection failed:", e)



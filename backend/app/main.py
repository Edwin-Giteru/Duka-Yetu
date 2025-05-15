from fastapi import FastAPI, Depends
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from backend.app.db.create_engine import engine
from backend.app.auth import auth_router
from backend.app.category import category_router


load_dotenv()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app.include_router(auth_router.router)
app.include_router(category_router.router)

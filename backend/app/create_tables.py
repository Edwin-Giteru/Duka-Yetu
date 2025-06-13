from backend.app.create_engine import engine
from backend.app.models import Base



print("Creating tables...")
Base.metadata.create_all(bind=engine)
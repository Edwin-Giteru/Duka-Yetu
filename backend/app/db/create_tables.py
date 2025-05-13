from backend.app.db.create_engine import engine
from backend.app.db.model.models import Base



print("Creating tables...")
Base.metadata.create_all(bind=engine)
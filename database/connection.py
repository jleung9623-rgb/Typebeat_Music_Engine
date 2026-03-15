# database/connection.py
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

# 1. Load the Environment Variables
# override=True ensures your local .env always takes precedence
load_dotenv(override=True)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "typebeat_ai_v7")

# 2. Construct the SQLAlchemy URL
# Notice we specify the exact driver: mysql+mysqlconnector
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# 3. Initialize the Engine
# The Engine is the "Factory". It manages a pool of connections for you automatically.
# Set echo=False in production, but you can set it to True if you want to see the raw SQL it generates.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False, 
    pool_recycle=3600, # Prevents MySQL from dropping idle connections after an hour
    pool_pre_ping=True # Verifies connections are alive before using them
)

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print(f"--- SUCCESS: SQLAlchemy Engine connected to '{DB_NAME}' ---")
except OperationalError as e:
    print(f"--- ERROR: Could not connect to the database. ---")
    print(f"--- Check your .env credentials or ensure your MySQL server is running. ---")
    sys.exit(1) # Kills the application immediately if the DB is down

# 4. Initialize the Session Factory
# When your main app needs to talk to the DB, it will ask this factory for a "Session".
# autoflush=False ensures SQLAlchemy doesn't prematurely push incomplete data.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Dependency Injector (For future use in your main logic)
def get_db():
    """Yields a database session and safely closes it when the transaction is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
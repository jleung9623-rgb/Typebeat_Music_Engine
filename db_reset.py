from database.connection import engine
from database.models import Base

def reset_database():
    print("--- WARNING: Wiping all data and resetting schema ---")
    # Removes all physical tables in the DB
    Base.metadata.drop_all(bind=engine)

    # Recreates the database on the current models.py
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: Database schema is now fresh and synced.")

if __name__ == "__main__":
    confirmation = input("Are you sure you want to wipe all data? (y/n): ")
    if confirmation.lower() == 'y':
        reset_database()
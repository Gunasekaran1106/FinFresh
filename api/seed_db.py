import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient

# Ensure app can be imported if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import hash_password

def seed_database():
    mongo_url = settings.mongodb_url
    db_name = settings.database_name
    
    print(f"Connecting to MongoDB at {mongo_url}...")
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    users_col = db["users"]
    transactions_col = db["transactions"]
    
    test_email = "test@example.com"
    
    # Check if test user exists, and clean up their records
    existing_user = users_col.find_one({"email": test_email})
    if existing_user:
        user_id_str = str(existing_user["_id"])
        print(f"Cleaning existing records for user: {test_email} (ID: {user_id_str})...")
        del_tx = transactions_col.delete_many({"user_id": user_id_str})
        del_usr = users_col.delete_one({"_id": existing_user["_id"]})
        print(f"Deleted {del_tx.deleted_count} transactions and {del_usr.deleted_count} user document.")
    
    # Create new test user
    print("Creating sample user test@example.com...")
    pwd_hash = hash_password("Str0ng!Pass")
    user_doc = {
        "name": "Test User",
        "email": test_email,
        "password_hash": pwd_hash,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = users_col.insert_one(user_doc)
    user_id = str(result.inserted_id)
    print(f"User created with ID: {user_id}")
    
    # Prepare sample transactions
    transactions = [
        # --- JUNE 2026 (Current Month) ---
        {
            "user_id": user_id,
            "type": "income",
            "category": "Salary",
            "amount": 5000.00,
            "description": "Monthly job salary",
            "date": datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "income",
            "category": "Freelance",
            "amount": 1200.00,
            "description": "Website development contract",
            "date": datetime(2026, 6, 3, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 3, 14, 30, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Housing",
            "amount": 1500.00,
            "description": "Apartment rent",
            "date": datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Food",
            "amount": 150.00,
            "description": "Weekly grocery shopping",
            "date": datetime(2026, 6, 2, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 2, 18, 15, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Utilities",
            "amount": 120.00,
            "description": "Electricity and internet bill",
            "date": datetime(2026, 6, 4, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 4, 11, 45, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Food",
            "amount": 80.00,
            "description": "Dinner at restaurant",
            "date": datetime(2026, 6, 5, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 5, 20, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "investment",
            "category": "Stocks",
            "amount": 800.00,
            "description": "S&P 500 ETF investment",
            "date": datetime(2026, 6, 2, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 2, 10, 15, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "investment",
            "category": "Crypto",
            "amount": 200.00,
            "description": "Bitcoin purchase",
            "date": datetime(2026, 6, 4, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 4, 16, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "debt",
            "category": "Student Loan",
            "amount": 300.00,
            "description": "Monthly student loan payment",
            "date": datetime(2026, 6, 3, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 3, 8, 30, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "debt",
            "category": "Credit Card",
            "amount": 150.00,
            "description": "Credit card balance payoff",
            "date": datetime(2026, 6, 5, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc)
        },
        
        # --- MAY 2026 (Previous Month) ---
        {
            "user_id": user_id,
            "type": "income",
            "category": "Salary",
            "amount": 5000.00,
            "description": "Monthly job salary",
            "date": datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "income",
            "category": "Freelance",
            "amount": 800.00,
            "description": "Logo design project",
            "date": datetime(2026, 5, 15, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 15, 17, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Housing",
            "amount": 1500.00,
            "description": "Apartment rent",
            "date": datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Food",
            "amount": 320.00,
            "description": "Monthly groceries",
            "date": datetime(2026, 5, 10, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 10, 15, 30, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Utilities",
            "amount": 95.00,
            "description": "Water and gas utilities",
            "date": datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 12, 11, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Entertainment",
            "amount": 150.00,
            "description": "Concert tickets",
            "date": datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 20, 19, 0, tzinfo=timezone.utc)
        },
        
        # --- APRIL 2026 (Two Months Ago) ---
        {
            "user_id": user_id,
            "type": "income",
            "category": "Salary",
            "amount": 5000.00,
            "description": "Monthly job salary",
            "date": datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Housing",
            "amount": 1500.00,
            "description": "Apartment rent",
            "date": datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Food",
            "amount": 290.00,
            "description": "Groceries",
            "date": datetime(2026, 4, 10, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 10, 14, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Utilities",
            "amount": 60.00,
            "description": "Home internet subscription",
            "date": datetime(2026, 4, 14, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 14, 10, 30, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Shopping",
            "amount": 110.00,
            "description": "New sneakers purchase",
            "date": datetime(2026, 4, 18, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 18, 16, 45, tzinfo=timezone.utc)
        },
        
        # --- MARCH 2026 (Three Months Ago) ---
        {
            "user_id": user_id,
            "type": "income",
            "category": "Salary",
            "amount": 5000.00,
            "description": "Monthly job salary",
            "date": datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Housing",
            "amount": 1500.00,
            "description": "Apartment rent",
            "date": datetime(2026, 3, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Food",
            "amount": 310.00,
            "description": "Groceries",
            "date": datetime(2026, 3, 12, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 3, 12, 13, 15, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Utilities",
            "amount": 85.00,
            "description": "Phone and internet utilities",
            "date": datetime(2026, 3, 15, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 3, 15, 11, 20, tzinfo=timezone.utc)
        },
        {
            "user_id": user_id,
            "type": "expense",
            "category": "Health",
            "amount": 50.00,
            "description": "Gym membership",
            "date": datetime(2026, 3, 22, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 3, 22, 17, 30, tzinfo=timezone.utc)
        }
    ]
    
    print(f"Seeding {len(transactions)} transactions...")
    tx_result = transactions_col.insert_many(transactions)
    print(f"Successfully seeded {len(tx_result.inserted_ids)} transactions.")

    # --- SEED SECOND USER FOR MODERATE / AT RISK HEALTH CHECK ---
    mod_email = "moderate@example.com"
    existing_mod = users_col.find_one({"email": mod_email})
    if existing_mod:
        mod_id_str = str(existing_mod["_id"])
        print(f"Cleaning existing records for user: {mod_email} (ID: {mod_id_str})...")
        transactions_col.delete_many({"user_id": mod_id_str})
        users_col.delete_one({"_id": existing_mod["_id"]})

    print(f"Creating sample user {mod_email}...")
    mod_doc = {
        "name": "Moderate User",
        "email": mod_email,
        "password_hash": pwd_hash,
        "created_at": datetime.now(timezone.utc)
    }
    result_mod = users_col.insert_one(mod_doc)
    mod_user_id = str(result_mod.inserted_id)
    print(f"User created with ID: {mod_user_id}")

    mod_transactions = [
        # --- Current Month (June 2026) ---
        # Low savings rate, high debt, no investments
        {
            "user_id": mod_user_id,
            "type": "income",
            "category": "Salary",
            "amount": 3000.00,
            "description": "Monthly job salary",
            "date": datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Housing",
            "amount": 1500.00,
            "description": "Apartment rent",
            "date": datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Food",
            "amount": 500.00,
            "description": "Groceries",
            "date": datetime(2026, 6, 2, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 2, 18, 15, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Utilities",
            "amount": 300.00,
            "description": "Electric and gas bill",
            "date": datetime(2026, 6, 4, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 4, 11, 45, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Entertainment",
            "amount": 400.00,
            "description": "Concert tickets",
            "date": datetime(2026, 6, 5, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 5, 20, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "debt",
            "category": "Credit Card",
            "amount": 1000.00,
            "description": "High credit card payment",
            "date": datetime(2026, 6, 3, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 6, 3, 8, 30, tzinfo=timezone.utc)
        },
        
        # --- Previous Month (May 2026) ---
        {
            "user_id": mod_user_id,
            "type": "income",
            "category": "Salary",
            "amount": 3000.00,
            "date": datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Housing",
            "amount": 1500.00,
            "date": datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Food",
            "amount": 550.00,
            "date": datetime(2026, 5, 10, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 10, 15, 30, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Utilities",
            "amount": 310.00,
            "date": datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 12, 11, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Entertainment",
            "amount": 350.00,
            "date": datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 5, 20, 19, 0, tzinfo=timezone.utc)
        },
        
        # --- Two Months Ago (April 2026) ---
        {
            "user_id": mod_user_id,
            "type": "income",
            "category": "Salary",
            "amount": 3000.00,
            "date": datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Housing",
            "amount": 1500.00,
            "date": datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Food",
            "amount": 490.00,
            "date": datetime(2026, 4, 10, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 10, 14, 0, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Utilities",
            "amount": 280.00,
            "date": datetime(2026, 4, 14, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 14, 10, 30, tzinfo=timezone.utc)
        },
        {
            "user_id": mod_user_id,
            "type": "expense",
            "category": "Shopping",
            "amount": 400.00,
            "date": datetime(2026, 4, 18, 0, 0, tzinfo=timezone.utc),
            "created_at": datetime(2026, 4, 18, 16, 45, tzinfo=timezone.utc)
        }
    ]
    
    print(f"Seeding {len(mod_transactions)} transactions for moderate user...")
    mod_tx_result = transactions_col.insert_many(mod_transactions)
    print(f"Successfully seeded {len(mod_tx_result.inserted_ids)} transactions for moderate user.")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()

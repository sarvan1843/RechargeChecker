import os
from datetime import datetime
from pymongo import MongoClient

# Fetch the MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "recharge_checker"

# Initialize MongoDB Client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_col = db["Users"]
otps_col = db["OTPs"]

def init_db():
    """
    Initializes the MongoDB database connections (Indexes etc can be added here).
    """
    print(f"Initializing MongoDB Database connected to: {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI}")
    # Create indexes for faster queries
    users_col.create_index("mobile", unique=True)
    users_col.create_index("email", unique=True)
    otps_col.create_index("email", unique=True)
    print("MongoDB Database initialized successfully.")

def create_user(mobile, pin_hash, email=None, full_name=None):
    """
    Inserts a new user document into the Users collection.
    """
    # Verify uniqueness
    if users_col.find_one({"mobile": str(mobile)}):
        raise Exception("Mobile number already registered")
        
    reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_doc = {
        "mobile": str(mobile),
        "pin_hash": str(pin_hash),
        "full_name": str(full_name or ""),
        "email": str(email or ""),
        "created_at": reg_date,
        "last_login": "",
        "status": "Active"
    }
    users_col.insert_one(user_doc)
    return True

def get_user_by_mobile(mobile):
    """
    Finds a user in the Users collection by mobile number.
    """
    user = users_col.find_one({"mobile": str(mobile)})
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user
    return None

def get_user_by_email(email):
    """
    Finds a user in the Users collection by email address.
    """
    if not email:
        return None
    user = users_col.find_one({"email": str(email).lower()})
    if user:
        user["_id"] = str(user["_id"])
        return user
    return None

def update_last_login(mobile):
    """
    Updates the Last Login timestamp for the user.
    """
    login_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users_col.update_one(
        {"mobile": str(mobile)},
        {"$set": {"last_login": login_date}}
    )

def store_otp(email, otp, expires_at):
    """
    Stores or replaces an OTP record in the OTPs collection.
    """
    otps_col.update_one(
        {"email": str(email).lower()},
        {"$set": {
            "email": str(email).lower(),
            "otp": str(otp),
            "expires_at": int(expires_at)
        }},
        upsert=True
    )

def get_otp(email):
    """
    Finds an OTP record in the OTPs collection.
    """
    otp_doc = otps_col.find_one({"email": str(email).lower()})
    if otp_doc:
        otp_doc["_id"] = str(otp_doc["_id"])
        return otp_doc
    return None

def delete_otp(email):
    """
    Deletes an OTP record from the OTPs collection.
    """
    otps_col.delete_one({"email": str(email).lower()})

# --- Admin Panel Functions ---

def get_all_users():
    """
    Returns all users for the Admin Panel.
    """
    users = list(users_col.find({}, {"_id": 0, "pin_hash": 0})) # Exclude ID and passwords
    return users

def toggle_user_status(email):
    """
    Toggles the user's status between Active and Banned.
    """
    user = users_col.find_one({"email": str(email).lower()})
    if user:
        new_status = "Banned" if user.get("status", "Active") == "Active" else "Active"
        users_col.update_one(
            {"email": str(email).lower()},
            {"$set": {"status": new_status}}
        )
        return new_status
    return None

def delete_user(email):
    """
    Deletes a user completely.
    """
    result = users_col.delete_one({"email": str(email).lower()})
    return result.deleted_count > 0

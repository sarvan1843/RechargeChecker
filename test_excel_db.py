import os
from pathlib import Path
from app.database import init_db, create_user, get_user_by_mobile, update_last_login
from app.auth import hash_password, verify_password

def run_tests():
    db_file = Path(__file__).resolve().parent / "users_db.xlsx"
    if os.path.exists(db_file):
        print("Removing existing test excel database...")
        os.remove(db_file)
        
    print("Step 1: Initializing Excel database...")
    init_db()
    
    assert os.path.exists(db_file), "Database file was not created!"
    print("Database file created successfully.")
    
    print("\nStep 2: Registering a test user...")
    mobile = "9999999999"
    pin = "1234"
    name = "Test User"
    email = "test@example.com"
    
    hashed = hash_password(pin)
    success = create_user(mobile, hashed, email, name)
    assert success, "Registration failed!"
    print("User registered successfully.")
    
    print("\nStep 3: Querying the registered user...")
    user = get_user_by_mobile(mobile)
    assert user is not None, "Failed to retrieve user!"
    assert user["mobile"] == mobile, "Mobile mismatch!"
    assert user["full_name"] == name, "Name mismatch!"
    assert user["email"] == email, "Email mismatch!"
    assert user["status"] == "Active", "Status mismatch!"
    print("User retrieved and fields verified successfully:")
    print(user)
    
    print("\nStep 4: Verifying user PIN authentication...")
    assert verify_password(pin, user["pin_hash"]), "Authentication failed!"
    assert not verify_password("1111", user["pin_hash"]), "Authentication error (should reject wrong PIN)!"
    print("Authentication verify tests passed.")
    
    print("\nStep 5: Updating last login...")
    update_last_login(mobile)
    user_after_login = get_user_by_mobile(mobile)
    assert user_after_login["last_login"] != "", "Last login was not updated!"
    print("Last login updated successfully:", user_after_login["last_login"])
    
    print("\nAll database Excel tests passed successfully!")

if __name__ == "__main__":
    run_tests()

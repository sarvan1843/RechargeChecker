import hashlib
import secrets
import hmac
import base64
import json
import time

SECRET_KEY = b"recharge-checker-secret-key-super-secure-2026"

def hash_password(password: str) -> str:
    """
    Hashes a pin/password with a secure random salt.
    """
    salt = secrets.token_hex(8)
    h = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{h}"

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies a pin/password against its hash.
    """
    if not hashed or ":" not in hashed:
        return False
    salt, h = hashed.split(":", 1)
    test_h = hashlib.sha256((password + salt).encode()).hexdigest()
    return h == test_h

def generate_token(mobile: str, expires_in_seconds: int = 86400) -> str:
    """
    Generates a secure signed token mapping to the user's mobile number.
    """
    expiry = int(time.time()) + expires_in_seconds
    payload = {"mobile": mobile, "exp": expiry}
    payload_json = json.dumps(payload)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")
    
    # Calculate HMAC signature
    sig = hmac.new(SECRET_KEY, payload_b64.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    
    return f"{payload_b64}.{sig_b64}"

def verify_token(token: str) -> str or None:
    """
    Verifies the signed token and returns the mobile number if valid.
    """
    try:
        if not token or "." not in token:
            return None
        payload_b64, sig_b64 = token.split(".", 1)
        
        # Verify signature
        expected_sig = hmac.new(SECRET_KEY, payload_b64.encode(), hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None
            
        # Add padding back if necessary for base64 decode
        padding = len(payload_b64) % 4
        if padding:
            payload_b64 += "=" * (4 - padding)
            
        payload_bytes = base64.urlsafe_b64decode(payload_b64.encode())
        payload = json.loads(payload_bytes.decode())
        
        # Check expiry
        if time.time() > payload["exp"]:
            print("Token expired.")
            return None
            
        return payload["mobile"]
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

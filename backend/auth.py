"""
SHEVAULT AI - Authentication and Database Services
"""
import sqlite3
import os
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "shevault.db")
SECRET_KEY = os.getenv("SHEVAULT_JWT_SECRET", "shevault_super_secret_jwt_key_2026_f4e8b9")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT DEFAULT 'Student',
        allow_storage INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    # Demo users seed if not exists
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()["count"]
    if count == 0:
        demo_users = [
            ("user_ananya", "Ananya Sharma", "ananya@shevault.ai", "Password123!", "Student"),
            ("user_priya", "Priya Patel", "priya@shevault.ai", "Password123!", "Freelancer"),
            ("user_ritu", "Ritu Sengupta", "ritu@shevault.ai", "Password123!", "Job Seeker")
        ]
        for uid, name, email, pwd, role in demo_users:
            salt = secrets.token_hex(16)
            pwd_hash = hash_password(pwd, salt)
            cursor.execute("""
                INSERT INTO users (id, name, email, password_hash, salt, role, allow_storage, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, name, email, pwd_hash, salt, role, 1, datetime.utcnow().isoformat()))
        conn.commit()
    conn.close()

def hash_password(password: str, salt: str) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex()

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    return hash_password(password, salt) == password_hash

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def register_user(name: str, email: str, password: str, role: str = "Student") -> Dict[str, Any]:
    email = email.lower().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise ValueError("An account with this email already exists.")
    
    user_id = f"user_{secrets.token_hex(8)}"
    salt = secrets.token_hex(16)
    pwd_hash = hash_password(password, salt)
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO users (id, name, email, password_hash, salt, role, allow_storage, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name.strip(), email, pwd_hash, salt, role, 1, now))
    
    conn.commit()
    conn.close()
    
    token = create_access_token({"sub": user_id, "email": email, "name": name, "role": role})
    return {
        "user": {"id": user_id, "name": name, "email": email, "role": role, "created_at": now},
        "token": token
    }

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    email = email.lower().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise ValueError("No account found with this email address.")
    
    if not verify_password(password, user["salt"], user["password_hash"]):
        raise ValueError("Incorrect password. Please verify and try again.")
    
    token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"]
    })
    
    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"],
            "allow_storage": bool(user["allow_storage"])
        },
        "token": token
    }

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, allow_storage, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return None
    return dict(user)

def update_user_profile(user_id: str, name: Optional[str] = None, role: Optional[str] = None, allow_storage: Optional[bool] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if name:
        cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name.strip(), user_id))
    if role:
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    if allow_storage is not None:
        cursor.execute("UPDATE users SET allow_storage = ? WHERE id = ?", (1 if allow_storage else 0, user_id))
        
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def change_user_password(user_id: str, old_password: str, new_password: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise ValueError("User not found.")
    
    if not verify_password(old_password, user["salt"], user["password_hash"]):
        conn.close()
        raise ValueError("Current password does not match.")
    
    salt = secrets.token_hex(16)
    pwd_hash = hash_password(new_password, salt)
    cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (pwd_hash, salt, user_id))
    conn.commit()
    conn.close()
    return True

def delete_user_account(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

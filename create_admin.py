#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import bcrypt
import base64
import os

def create_admin_user():
    db_name = 'data/users.db'
    # Ensure data directory exists
    try:
        os.makedirs(os.path.dirname(db_name), exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create data directory: {e}")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    # Delete existing admin if exists
    cursor.execute('DELETE FROM users WHERE username = ?', ('admin',))

    # Create admin user with bcrypt hash
    admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    admin_password_b64 = base64.b64encode(admin_password).decode('utf-8')
    cursor.execute('''
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
    ''', ('admin', admin_password_b64, 'System Administrator', 'admin'))

    conn.commit()
    conn.close()
    print("Admin user created successfully. Username: admin, Password: admin123")

if __name__ == "__main__":
    create_admin_user()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Database Viewer
Displays all users in the users.db database for debugging purposes.
WARNING: This script shows password hashes - use only for debugging!
"""

import sqlite3
import base64
import bcrypt
from datetime import datetime

def view_users_db():
    """Display all users in the database"""
    try:
        # Connect to database
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()

        # Get all users
        cursor.execute('''
            SELECT id, username, password_hash, full_name, email, role,
                   created_at, last_login, login_count, is_active
            FROM users
            ORDER BY id
        ''')

        users = cursor.fetchall()
        conn.close()

        if not users:
            print("No users found in database.")
            return

        print("=" * 80)
        print("USERS DATABASE VIEWER")
        print("=" * 80)
        print(f"Total users: {len(users)}")
        print()

        for user in users:
            (user_id, username, password_hash, full_name, email, role,
             created_at, last_login, login_count, is_active) = user

            print(f"ID: {user_id}")
            print(f"Username: {username}")
            print(f"Role: {role}")
            print(f"Full Name: {full_name or 'N/A'}")
            print(f"Email: {email or 'N/A'}")
            print(f"Active: {'Yes' if is_active else 'No'}")
            print(f"Login Count: {login_count}")
            print(f"Created: {created_at}")
            print(f"Last Login: {last_login or 'Never'}")

            # Password hash analysis
            print(f"Password Hash: {password_hash}")
            print(f"Hash Length: {len(password_hash)}")

            # Test if hash is valid
            try:
                decoded = base64.b64decode(password_hash)
                print(f"Base64 Decode: ✓ Success (length: {len(decoded)})")
                # Test if it's a valid bcrypt hash
                decoded_str = decoded.decode('utf-8')
                if decoded_str.startswith('$2b$') or decoded_str.startswith('$2a$'):
                    print("Hash Format: ✓ Valid bcrypt format")
                else:
                    print("Hash Format: ⚠ Not standard bcrypt format")
            except Exception as e:
                print(f"Base64 Decode: ✗ Failed - {e}")

            print("-" * 50)

    except Exception as e:
        print(f"Error accessing database: {e}")

def test_password_verification():
    """Test password verification for a specific user"""
    try:
        username = input("Enter username to test password verification: ").strip()
        if not username:
            return

        password = input("Enter password to test: ").strip()
        if not password:
            return

        from database import UserDatabase
        db = UserDatabase()
        success, message, role = db.authenticate_user(username, password)

        print(f"\nAuthentication Test for '{username}':")
        print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")
        print(f"Message: {message}")
        if success:
            print(f"Role: {role}")

    except Exception as e:
        print(f"Error testing authentication: {e}")

if __name__ == "__main__":
    print("User Database Viewer")
    print("===================")

    view_users_db()

    print("\n" + "=" * 50)
    choice = input("Test password verification? (y/n): ").lower().strip()
    if choice == 'y':
        test_password_verification()

    print("\nDone.")
import sqlite3
import bcrypt
from datetime import datetime
import pandas as pd

class CovidDatabase:
    def __init__(self, db_name='data/covid_data.db'):
        self.db_name = db_name
        self.create_tables()
    
    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS covid_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                date TEXT NOT NULL,
                confirmed INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                recovered INTEGER DEFAULT 0,
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_global_summary(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(confirmed) as total_confirmed,
                SUM(deaths) as total_deaths,
                SUM(recovered) as total_recovered,
                SUM(active) as total_active
            FROM covid_cases
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'total_confirmed': result[0] or 0,
                'total_deaths': result[1] or 0,
                'total_recovered': result[2] or 0,
                'total_active': result[3] or 0
            }
        return None
    
    def get_top_countries(self, metric='confirmed', limit=10):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        query = f'''
            SELECT country, 
                   SUM(confirmed) as confirmed,
                   SUM(deaths) as deaths,
                   SUM(recovered) as recovered,
                   SUM(active) as active
            FROM covid_cases
            GROUP BY country
            ORDER BY {metric} DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'country': row[0],
                'confirmed': row[1],
                'deaths': row[2],
                'recovered': row[3],
                'active': row[4]
            }
            for row in results
        ]
    
    def get_all_countries(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT country FROM covid_cases ORDER BY country')
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    def compare_countries(self, countries):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in countries])
        query = f'''
            SELECT country,
                   SUM(confirmed) as confirmed,
                   SUM(deaths) as deaths,
                   SUM(recovered) as recovered,
                   SUM(active) as active
            FROM covid_cases
            WHERE country IN ({placeholders})
            GROUP BY country
        '''
        
        cursor.execute(query, countries)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'country': row[0],
                'confirmed': row[1],
                'deaths': row[2],
                'recovered': row[3],
                'active': row[4]
            }
            for row in results
        ]
    
    def add_new_case(self, case_data):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO covid_cases (country, date, confirmed, deaths, recovered, active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                case_data['country'],
                case_data['date'],
                case_data['confirmed'],
                case_data['deaths'],
                case_data['recovered'],
                case_data['active']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding case: {e}")
            return False


class UserDatabase:
    def __init__(self, db_name='data/users.db'):
        self.db_name = db_name
        self.create_tables()
    
    def create_tables(self):
        """Create users table if it doesn't exist"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
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
        
        # Create default admin if not exists
        cursor.execute('SELECT username FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_password, 'System Administrator', 'admin'))
            conn.commit()
        
        conn.commit()
        conn.close()
    
    def register_user(self, username, password, full_name=None, email=None, role='user'):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return False, "Username already exists"
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, full_name, email, role))
            
            conn.commit()
            conn.close()
            return True, "Registration successful!"
        
        except Exception as e:
            print(f"Registration error: {e}")
            return False, "Registration failed"
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT password_hash, is_active, role
                FROM users 
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Invalid username or password", None
            
            password_hash, is_active, role = result
            
            if not is_active:
                conn.close()
                return False, "Account is disabled", None
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                # Update login statistics
                cursor.execute('''
                    UPDATE users 
                    SET last_login = ?, login_count = login_count + 1
                    WHERE username = ?
                ''', (datetime.now(), username))
                
                conn.commit()
                conn.close()
                return True, "Login successful", role
            else:
                conn.close()
                return False, "Invalid username or password", None
        
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, "Authentication failed", None
    
    def get_user_info(self, username):
        """Get user information"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, full_name, email, role, created_at, last_login, login_count
                FROM users
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'username': result[0],
                    'full_name': result[1],
                    'email': result[2],
                    'role': result[3],
                    'created_at': result[4],
                    'last_login': result[5],
                    'login_count': result[6]
                }
            return None
        
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def get_all_users(self):
        """Get list of all users (admin function)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, full_name, email, role, created_at, last_login, login_count, is_active
                FROM users
                ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'username': row[0],
                    'full_name': row[1],
                    'email': row[2],
                    'role': row[3],
                    'created_at': row[4],
                    'last_login': row[5],
                    'login_count': row[6],
                    'is_active': row[7]
                }
                for row in results
            ]
        
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user_count(self):
        """Get total number of registered users"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        
        except Exception as e:
            print(f"Error getting user count: {e}")
            return 0
    
    def get_user_statistics(self):
        """Get user statistics"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Active users
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            active_users = cursor.fetchone()[0]
            
            # Users registered today
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE DATE(created_at) = DATE('now')
            ''')
            today_registrations = cursor.fetchone()[0]
            
            # Users logged in today
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE DATE(last_login) = DATE('now')
            ''')
            today_logins = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'today_registrations': today_registrations,
                'today_logins': today_logins
            }
        
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'today_registrations': 0,
                'today_logins': 0
            }
    
    def update_user_profile(self, username, full_name=None, email=None):
        """Update user profile information"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if full_name:
                cursor.execute('UPDATE users SET full_name = ? WHERE username = ?', 
                             (full_name, username))
            
            if email:
                cursor.execute('UPDATE users SET email = ? WHERE username = ?', 
                             (email, username))
            
            conn.commit()
            conn.close()
            return True, "Profile updated successfully"
        
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False, "Failed to update profile"
    
    def deactivate_user(self, username):
        """Deactivate a user account"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET is_active = 0 WHERE username = ?', (username,))
            
            conn.commit()
            conn.close()
            return True, "User deactivated successfully"
        
        except Exception as e:
            print(f"Error deactivating user: {e}")
            return False, "Failed to deactivate user"
    
    def activate_user(self, username):
        """Activate a user account"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET is_active = 1 WHERE username = ?', (username,))
            
            conn.commit()
            conn.close()
            return True, "User activated successfully"
        
        except Exception as e:
            print(f"Error activating user: {e}")
            return False, "Failed to activate user"
    
    def is_admin(self, username):
        """Check if user is admin"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT role FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            conn.close()
            
            return result and result[0] == 'admin'
        
        except Exception as e:
            print(f"Error checking admin status: {e}")
            return False
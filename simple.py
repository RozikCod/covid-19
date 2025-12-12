import React, { useState } from 'react';
import { FileCode, Database, Server, Layout, Users, Activity, Download } from 'lucide-react';

const ProjectStructure = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const files = [
    {
      id: 'requirements',
      name: 'requirements.txt',
      icon: FileCode,
      color: 'bg-blue-500',
      description: 'Python dependencies',
      content: `pandas==2.1.0
numpy==1.24.3
flask==3.0.0
flask-cors==4.0.0
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.17.0
requests==2.31.0
bcrypt==4.0.1
python-dotenv==1.0.0
openpyxl==3.1.2`
    },
    {
      id: 'data_cleaning',
      name: 'data_cleaning.py',
      icon: Database,
      color: 'bg-green-500',
      description: 'Data cleaning and preprocessing',
      content: `import pandas as pd
import numpy as np
from datetime import datetime

class CovidDataCleaner:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        
    def load_data(self):
        """Load COVID-19 dataset"""
        try:
            self.df = pd.read_csv(self.filepath)
            print(f"Data loaded successfully: {self.df.shape}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def clean_data(self):
        """Clean and preprocess the data"""
        if self.df is None:
            print("Please load data first")
            return None
        
        # Make a copy
        df_clean = self.df.copy()
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        # Handle missing values
        # Fill numeric columns with 0
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        
        # Fill categorical columns with 'Unknown'
        categorical_cols = df_clean.select_dtypes(include=['object']).columns
        df_clean[categorical_cols] = df_clean[categorical_cols].fillna('Unknown')
        
        # Convert date columns
        date_columns = [col for col in df_clean.columns if 'date' in col.lower()]
        for col in date_columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            except:
                pass
        
        # Remove negative values in case/death counts
        count_cols = [col for col in df_clean.columns if any(x in col.lower() 
                     for x in ['case', 'death', 'confirmed', 'recovered'])]
        for col in count_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].clip(lower=0)
        
        # Standardize country names
        if 'country' in df_clean.columns:
            df_clean['country'] = df_clean['country'].str.strip().str.title()
        
        self.df = df_clean
        print(f"Data cleaned successfully: {self.df.shape}")
        return self.df
    
    def get_summary_statistics(self):
        """Get summary statistics of the cleaned data"""
        if self.df is None:
            return None
        
        summary = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': self.df.isnull().sum().to_dict(),
            'numeric_summary': self.df.describe().to_dict()
        }
        return summary
    
    def save_cleaned_data(self, output_path):
        """Save cleaned data to CSV"""
        if self.df is None:
            print("No data to save")
            return False
        
        try:
            self.df.to_csv(output_path, index=False)
            print(f"Cleaned data saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

# Example usage
if __name__ == "__main__":
    cleaner = CovidDataCleaner('covid_data.csv')
    if cleaner.load_data():
        cleaner.clean_data()
        cleaner.save_cleaned_data('covid_data_cleaned.csv')
        print(cleaner.get_summary_statistics())`
    },
    {
      id: 'database',
      name: 'database.py',
      icon: Database,
      color: 'bg-purple-500',
      description: 'Database operations',
      content: `import pandas as pd
import json
from datetime import datetime

class CovidDatabase:
    def __init__(self, csv_path='covid_data_cleaned.csv'):
        self.csv_path = csv_path
        self.df = None
        self.load_database()
    
    def load_database(self):
        """Load the COVID-19 database"""
        try:
            self.df = pd.read_csv(self.csv_path)
            # Convert date columns
            date_cols = [col for col in self.df.columns if 'date' in col.lower()]
            for col in date_cols:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            print(f"Database loaded: {len(self.df)} records")
            return True
        except FileNotFoundError:
            print("Database file not found, creating empty database")
            self.df = pd.DataFrame(columns=[
                'date', 'country', 'confirmed', 'deaths', 'recovered', 'active'
            ])
            return False
        except Exception as e:
            print(f"Error loading database: {e}")
            return False
    
    def save_database(self):
        """Save database to CSV"""
        try:
            self.df.to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def get_all_countries(self):
        """Get list of all countries"""
        if 'country' in self.df.columns:
            return sorted(self.df['country'].unique().tolist())
        return []
    
    def get_country_data(self, country):
        """Get all data for a specific country"""
        if self.df is None or country not in self.get_all_countries():
            return None
        return self.df[self.df['country'] == country].to_dict('records')
    
    def get_global_summary(self):
        """Get global COVID-19 summary"""
        if self.df is None:
            return None
        
        numeric_cols = ['confirmed', 'deaths', 'recovered', 'active']
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        summary = {}
        for col in available_cols:
            summary[f'total_{col}'] = int(self.df[col].sum())
        
        summary['total_countries'] = len(self.get_all_countries())
        summary['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return summary
    
    def get_top_countries(self, metric='confirmed', limit=10):
        """Get top countries by a specific metric"""
        if self.df is None or metric not in self.df.columns:
            return []
        
        top_countries = self.df.groupby('country')[metric].sum().nlargest(limit)
        return [{'country': country, metric: int(value)} 
                for country, value in top_countries.items()]
    
    def add_new_case(self, case_data):
        """Add a new COVID-19 case record"""
        try:
            new_row = pd.DataFrame([case_data])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.save_database()
            return True
        except Exception as e:
            print(f"Error adding new case: {e}")
            return False
    
    def compare_countries(self, countries):
        """Compare multiple countries"""
        if self.df is None:
            return None
        
        comparison = []
        for country in countries:
            if country in self.get_all_countries():
                country_data = self.df[self.df['country'] == country]
                numeric_cols = country_data.select_dtypes(include=['number']).columns
                stats = {'country': country}
                for col in numeric_cols:
                    stats[col] = int(country_data[col].sum())
                comparison.append(stats)
        
        return comparison

# User authentication
class UserDatabase:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def register_user(self, username, password):
        """Register a new user"""
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'password': password,  # In production, use bcrypt
            'registered_at': datetime.now().isoformat()
        }
        self.save_users()
        return True, "User registered successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        if username not in self.users:
            return False, "User not found"
        
        if self.users[username]['password'] == password:
            return True, "Login successful"
        return False, "Invalid password"`
    },
    {
      id: 'api',
      name: 'api.py',
      icon: Server,
      color: 'bg-orange-500',
      description: 'Flask API endpoints',
      content: `from flask import Flask, request, jsonify
from flask_cors import CORS
from database import CovidDatabase, UserDatabase
import pandas as pd

app = Flask(__name__)
CORS(app)

# Initialize databases
covid_db = CovidDatabase()
user_db = UserDatabase()

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({'status': 'healthy', 'message': 'COVID-19 API is running'})

# Authentication endpoints
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400
    
    success, message = user_db.register_user(username, password)
    return jsonify({'success': success, 'message': message}), 200 if success else 400

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400
    
    success, message = user_db.authenticate_user(username, password)
    return jsonify({'success': success, 'message': message, 'username': username if success else None}), 200 if success else 401

# COVID data endpoints
@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    countries = covid_db.get_all_countries()
    return jsonify({'countries': countries})

@app.route('/api/country/<country_name>', methods=['GET'])
def get_country_data(country_name):
    """Get data for a specific country"""
    data = covid_db.get_country_data(country_name)
    if data is None:
        return jsonify({'error': 'Country not found'}), 404
    return jsonify({'country': country_name, 'data': data})

@app.route('/api/global-summary', methods=['GET'])
def get_global_summary():
    """Get global COVID summary"""
    summary = covid_db.get_global_summary()
    return jsonify(summary)

@app.route('/api/top-countries', methods=['GET'])
def get_top_countries():
    """Get top countries by metric"""
    metric = request.args.get('metric', 'confirmed')
    limit = int(request.args.get('limit', 10))
    
    top_countries = covid_db.get_top_countries(metric, limit)
    return jsonify({'metric': metric, 'countries': top_countries})

@app.route('/api/compare', methods=['POST'])
def compare_countries():
    """Compare multiple countries"""
    data = request.json
    countries = data.get('countries', [])
    
    if not countries:
        return jsonify({'error': 'No countries provided'}), 400
    
    comparison = covid_db.compare_countries(countries)
    return jsonify({'comparison': comparison})

@app.route('/api/add-case', methods=['POST'])
def add_case():
    """Add a new COVID case"""
    data = request.json
    required_fields = ['country', 'confirmed', 'deaths', 'recovered']
    
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    success = covid_db.add_new_case(data)
    return jsonify({
        'success': success,
        'message': 'Case added successfully' if success else 'Failed to add case'
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get various statistics"""
    if covid_db.df is None:
        return jsonify({'error': 'No data available'}), 404
    
    stats = {
        'total_records': len(covid_db.df),
        'date_range': {
            'start': str(covid_db.df['date'].min()) if 'date' in covid_db.df.columns else None,
            'end': str(covid_db.df['date'].max()) if 'date' in covid_db.df.columns else None
        },
        'countries_count': len(covid_db.get_all_countries())
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    print("Starting COVID-19 Data Analysis API...")
    print("API will be available at http://localhost:5000")
    app.run(debug=True, port=5000)`
    },
    {
      id: 'app',
      name: 'app.py',
      icon: Layout,
      color: 'bg-pink-500',
      description: 'Main Streamlit application',
      content: `import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import CovidDatabase, UserDatabase
import requests

# Page configuration
st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize databases
@st.cache_resource
def init_databases():
    return CovidDatabase(), UserDatabase()

covid_db, user_db = init_databases()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Authentication Pages
def login_page():
    st.markdown('<h1 class="main-header">🦠 COVID-19 Data Analysis System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Login", use_container_width=True):
                if username and password:
                    success, message = user_db.authenticate_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
        
        with col_b:
            if st.button("Register", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()

def register_page():
    st.markdown('<h1 class="main-header">🦠 COVID-19 Data Analysis System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 Register New Account")
        username = st.text_input("Username", key="reg_username")
        password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Create Account", use_container_width=True):
                if username and password:
                    if password == confirm_password:
                        success, message = user_db.register_user(username, password)
                        if success:
                            st.success(message)
                            st.info("Please login with your new account")
                        else:
                            st.error(message)
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Please fill all fields")
        
        with col_b:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

# Dashboard Pages
def dashboard_page():
    st.markdown(f'<h1 class="main-header">🦠 COVID-19 Global Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"**Welcome, {st.session_state.username}!**")
    
    # Global Summary
    summary = covid_db.get_global_summary()
    
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Total Confirmed", "total_confirmed", "🔴"),
            ("Total Deaths", "total_deaths", "⚫"),
            ("Total Recovered", "total_recovered", "🟢"),
            ("Active Cases", "total_active", "🟡")
        ]
        
        for col, (label, key, emoji) in zip([col1, col2, col3, col4], metrics):
            with col:
                value = summary.get(key, 0)
                st.metric(label, f"{emoji} {value:,}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 Countries by Confirmed Cases")
        top_countries = covid_db.get_top_countries('confirmed', 10)
        if top_countries:
            df_top = pd.DataFrame(top_countries)
            fig = px.bar(df_top, x='country', y='confirmed', 
                        color='confirmed',
                        color_continuous_scale='Reds')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Top 10 Countries by Deaths")
        top_deaths = covid_db.get_top_countries('deaths', 10)
        if top_deaths:
            df_deaths = pd.DataFrame(top_deaths)
            fig = px.bar(df_deaths, x='country', y='deaths',
                        color='deaths',
                        color_continuous_scale='Greys')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Country-specific data
    st.markdown("---")
    st.subheader("🌍 Country-Specific Analysis")
    
    countries = covid_db.get_all_countries()
    selected_country = st.selectbox("Select a country", countries)
    
    if selected_country:
        country_data = covid_db.get_country_data(selected_country)
        if country_data:
            df_country = pd.DataFrame(country_data)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Total Records:** {len(df_country)}")
            with col2:
                numeric_cols = df_country.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.write(f"**Total Cases:** {int(df_country[numeric_cols[0]].sum()):,}")

def compare_page():
    st.markdown('<h1 class="main-header">⚖️ Compare Countries</h1>', unsafe_allow_html=True)
    
    countries = covid_db.get_all_countries()
    selected_countries = st.multiselect("Select countries to compare", countries, max_selections=5)
    
    if selected_countries and len(selected_countries) >= 2:
        comparison = covid_db.compare_countries(selected_countries)
        
        if comparison:
            df_compare = pd.DataFrame(comparison)
            
            # Display comparison table
            st.dataframe(df_compare, use_container_width=True)
            
            # Create comparison charts
            numeric_cols = [col for col in df_compare.columns if col != 'country']
            
            if numeric_cols:
                selected_metric = st.selectbox("Select metric to visualize", numeric_cols)
                
                fig = px.bar(df_compare, x='country', y=selected_metric,
                           color='country',
                           title=f"Comparison: {selected_metric.title()}")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least 2 countries to compare")

def add_case_page():
    st.markdown('<h1 class="main-header">➕ Add New COVID-19 Case</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("add_case_form"):
            country = st.text_input("Country")
            date = st.date_input("Date")
            confirmed = st.number_input("Confirmed Cases", min_value=0, value=0)
            deaths = st.number_input("Deaths", min_value=0, value=0)
            recovered = st.number_input("Recovered", min_value=0, value=0)
            active = st.number_input("Active Cases", min_value=0, value=0)
            
            submitted = st.form_submit_button("Add Case")
            
            if submitted:
                case_data = {
                    'country': country,
                    'date': str(date),
                    'confirmed': confirmed,
                    'deaths': deaths,
                    'recovered': recovered,
                    'active': active
                }
                
                if covid_db.add_new_case(case_data):
                    st.success("✅ Case added successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to add case")
    
    with col2:
        st.info("""
        ### Instructions
        1. Enter the country name
        2. Select the date
        3. Enter case numbers
        4. Click 'Add Case'
        """)

# Main app logic
def main():
    if not st.session_state.logged_in:
        if st.session_state.page == 'login':
            login_page()
        elif st.session_state.page == 'register':
            register_page()
    else:
        # Sidebar navigation
        with st.sidebar:
            st.title("📊 Navigation")
            st.markdown(f"**User:** {st.session_state.username}")
            st.markdown("---")
            
            page = st.radio("Go to", 
                          ["Dashboard", "Compare Countries", "Add New Case"])
            
            st.markdown("---")
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.page = 'login'
                st.rerun()
        
        # Display selected page
        if page == "Dashboard":
            dashboard_page()
        elif page == "Compare Countries":
            compare_page()
        elif page == "Add New Case":
            add_case_page()

if __name__ == "__main__":
    main()`
    },
    {
      id: 'sample_data',
      name: 'create_sample_data.py',
      icon: Database,
      color: 'bg-cyan-500',
      description: 'Generate sample COVID dataset',
      content: `import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_covid_data():
    """Create a sample COVID-19 dataset"""
    
    countries = ['United States', 'India', 'Brazil', 'United Kingdom', 'France',
                'Germany', 'Italy', 'Spain', 'Canada', 'Australia',
                'Japan', 'South Korea', 'China', 'Mexico', 'Argentina']
    
    # Generate data for the past 100 days
    start_date = datetime.now() - timedelta(days=100)
    dates = [start_date + timedelta(days=i) for i in range(100)]
    
    data = []
    
    for country in countries:
        base_confirmed = np.random.randint(100000, 5000000)
        base_deaths = int(base_confirmed * np.random.uniform(0.01, 0.03))
        base_recovered = int(base_confirmed * np.random.uniform(0.80, 0.95))
        
        for date in dates:
            # Add some randomness and growth
            confirmed = base_confirmed + np.random.randint(-10000, 50000)
            deaths = base_deaths + np.random.randint(-100, 1000)
            recovered = base_recovered + np.random.randint(-5000, 20000)
            active = confirmed - deaths - recovered
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'country': country,
                'confirmed': max(0, confirmed),
                'deaths': max(0, deaths),
                'recovered': max(0, recovered),
                'active': max(0, active)
            })
            
            # Update base values for next day
            base_confirmed = confirmed
            base_deaths = deaths
            base_recovered = recovered
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('covid_data.csv', index=False)
    print(f"Sample data created: {len(df)} records")
    print(f"Countries: {len(countries)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print("File saved as: covid_data.csv")
    
    return df

if __name__ == "__main__":
    create_sample_covid_data()`
    },
    {
      id: 'readme',
      name: 'README.md',
      icon: FileCode,
      color: 'bg-gray-500',
      description: 'Project documentation',
      content: `# COVID-19 Data Analysis Dashboard

A comprehensive COVID-19 data analysis system with interactive visualizations, user authentication, and data management capabilities.

## 📋 Features

- **User Authentication**: Secure login and registration system
- **Interactive Dashboard**: Real-time COVID-19 statistics and visualizations
- **Country Comparison**: Compare COVID-19 metrics across multiple countries
- **Data Management**: Add new COVID-19 cases to the database
- **Data Cleaning**: Automated data preprocessing and cleaning
- **REST API**: Flask-based API for data access
- **Beautiful UI**: Modern, responsive interface with Streamlit

## 🚀 Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install dependencies**:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. **Create sample dataset**:
\`\`\`bash
python create_sample_data.py
\`\`\`

4. **Clean the data**:
\`\`\`bash
python data_cleaning.py
\`\`\`

## 📊 Usage

### Option 1: Run Streamlit App (Recommended)
\`\`\`bash
streamlit run app.py
\`\`\`
Then open your browser to http://localhost:8501

### Option 2: Run API Server
\`\`\`bash
python api.py
\`\`\`
API will be available at http://localhost:5000

## 📁 Project Structure

\`\`\`
covid-analysis/
│
├── requirements.txt           # Python dependencies
├── create_sample_data.py     # Generate sample dataset
├── data_cleaning.py          # Data cleaning procedures
├── database.py               # Database operations
├── api.py                    # Flask REST API
├── app.py                    # Streamlit web application
├── covid_data.csv            # Raw COVID-19 dataset
├── covid_data_cleaned.csv    # Cleaned dataset
├── users.json                # User authentication data
└── README.md                 # Documentation
\`\`\`

## 🔑 API Endpoints

### Authentication
- \`POST /api/register\` - Register new user
- \`POST /api/login\` - User login

### COVID Data
- \`GET /api/countries\` - Get all countries
- \`GET /api/country/<name>\` - Get country data
- \`GET /api/global-summary\` - Get global statistics
- \`GET /api/top-countries\` - Get top countries by metric
- \`POST /api/compare\` - Compare multiple countries
- \`POST /api/add-case\` - Add new COVID case

## 📱 Application Pages

1. **Login Page** - Secure user authentication
2. **Registration Page** - New user signup
3. **Dashboard** - Global COVID-19 statistics with interactive charts
4. **Compare Countries** - Side-by-side country comparison
5. **Add New Case** - Submit new COVID-19 data

## 🛠️ Data Cleaning Features

- Remove duplicate records
- Handle missing values (numeric → 0, categorical → 'Unknown')
- Convert date columns to datetime format
- Remove negative values in case/death counts
- Standardize country names
- Generate summary statistics

## 💡 Tips

- Default login credentials will be created when you register
- Use the sidebar to navigate between pages
- Charts are interactive - hover for details
- Export data using pandas methods in the code

## 📞 Support

For issues or questions, refer to the documentation in each Python file or check the comments in the code.

## 🎯 Future Enhancements

- Machine learning predictions
- Email notifications
- Data export to Excel
- Advanced filtering
- Mobile app version

---
**Made with ❤️ for COVID-19 Data Analysis**
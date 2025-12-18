# -*- coding: utf-8 -*-
import streamlit as st
from database import CovidDatabase, UserDatabase

# Page configuration
st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
if 'role' not in st.session_state:
    st.session_state.role = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Import page modules from pages directory
import sys
import os
sys.path.append(os.path.dirname(__file__))

from pages.auth import login_page, register_page
from pages.dashboard import show as dashboard_show
from pages.compare import show as compare_show
from pages.add_case import show as add_case_show
from pages.users import show as users_show

def main():
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        }
        /* Hide the default file tree in sidebar */
        [data-testid="stSidebarNav"] {
            display: none;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # Authentication pages
        if st.session_state.page == 'login':
            login_page(user_db)
        else:
            register_page(user_db)
    else:
        # Main application with sidebar navigation
        with st.sidebar:
            st.title("📊 Navigation")
            st.markdown(f"**👤 User:** {st.session_state.username}")
            
            # Show role badge
            if st.session_state.role == 'admin':
                st.markdown("**🔑 Role:** <span style='color: #ffd700;'>Administrator</span>", unsafe_allow_html=True)
            else:
                st.markdown("**👥 Role:** User")
            
            st.markdown("---")
            
            # Navigation menu - Admin sees User Management, regular users don't
            if st.session_state.role == 'admin':
                menu_options = {
                    "🏠 Dashboard": "dashboard",
                    "⚖️ Compare Countries": "compare",
                    "➕ Add Case": "add_case",
                    "👥 User Management": "users"
                }
            else:
                menu_options = {
                    "🏠 Dashboard": "dashboard",
                    "⚖️ Compare Countries": "compare",
                    "➕ Add Case": "add_case"
                }
            
            page = st.radio(
                "Select Page",
                list(menu_options.keys()),
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.role = None
                st.session_state.page = 'login'
                st.rerun()
        
        # Route to appropriate page based on selection
        page_value = menu_options[page]
        
        if page_value == "dashboard":
            dashboard_show(covid_db)
        elif page_value == "compare":
            compare_show(covid_db)
        elif page_value == "add_case":
            add_case_show(covid_db)
        elif page_value == "users":
            users_show(user_db)

if __name__ == "__main__":
    main()
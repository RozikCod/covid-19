# -*- coding: utf-8 -*-
import streamlit as st

def login_page(user_db):
    """Display login page"""
    st.markdown('<h1 class="main-header">🦠 COVID-19 Data Analysis</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_btn = st.form_submit_button("Login", use_container_width=True)
            
            with col_b:
                register_btn = st.form_submit_button("Register", use_container_width=True)
        
        if login_btn:
            if username and password:
                success, msg, role = user_db.authenticate_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role  # Store user role
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
            else:
                st.error("❌ Please enter both username and password")
        
        if register_btn:
            st.session_state.page = 'register'
            st.rerun()
        
        st.markdown("---")
        
        # Show user statistics
        stats = user_db.get_user_statistics()
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("👥 Total Users", stats['total_users'])
        with col_stat2:
            st.metric("✅ Active Users", stats['active_users'])

def register_page(user_db):
    """Display registration page"""
    st.markdown('<h1 class="main-header">🦠 COVID-19 Data Analysis</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 📝 Create New Account")
        
        with st.form("register_form"):
            username = st.text_input("Username *", placeholder="Choose a username")
            full_name = st.text_input("Full Name", placeholder="Your full name (optional)")
            email = st.text_input("Email", placeholder="Your email (optional)")
            password = st.text_input("Password *", type="password", placeholder="Choose a password")
            confirm = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
            
            st.caption("* Required fields | Password must be at least 6 characters long")
            
            col_a, col_b = st.columns(2)
            with col_a:
                create_btn = st.form_submit_button("Create Account", use_container_width=True)
            
            with col_b:
                back_btn = st.form_submit_button("Back to Login", use_container_width=True)
        
        if create_btn:
            if username and password and confirm:
                if len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                elif password != confirm:
                    st.error("❌ Passwords don't match")
                else:
                    # Pass optional fields (can be None)
                    full_name_val = full_name if full_name.strip() else None
                    email_val = email if email.strip() else None
                    
                    success, msg = user_db.register_user(username, password, full_name_val, email_val)
                    if success:
                        st.success(f"✅ {msg}")
                        st.info("🔐 Please login with your new account")
                        st.balloons()
                    else:
                        st.error(f"❌ {msg}")
            else:
                st.error("❌ Please fill in all required fields (marked with *)")
        
        if back_btn:
            st.session_state.page = 'login'
            st.rerun()
        
        st.markdown("---")
        
        # Show registration statistics
        stats = user_db.get_user_statistics()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👥 Total Users", stats['total_users'])
        with col2:
            st.metric("🆕 Registered Today", stats['today_registrations'])
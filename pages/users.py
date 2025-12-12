import streamlit as st
import pandas as pd
from datetime import datetime

def show(user_db):
    """Display user management page"""
    
    # Check if user is admin
    if st.session_state.role != 'admin':
        st.error("🚫 Access Denied")
        st.warning("You don't have permission to access this page. This page is only available for administrators.")
        return
    
    st.markdown('<h1 class="main-header">👥 User Management</h1>', unsafe_allow_html=True)
    st.markdown("View and manage registered users - **Admin Only**")
    
    # User Statistics
    st.markdown("### 📊 User Statistics")
    stats = user_db.get_user_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: #667eea; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="color: white; margin: 0;">👥</h2>
            <h3 style="color: white; margin: 10px 0;">{stats['total_users']}</h3>
            <p style="color: white; margin: 0; font-size: 14px;">Total Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #51cf66; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="color: white; margin: 0;">✅</h2>
            <h3 style="color: white; margin: 10px 0;">{stats['active_users']}</h3>
            <p style="color: white; margin: 0; font-size: 14px;">Active Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #ffd43b; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="color: white; margin: 0;">🆕</h2>
            <h3 style="color: white; margin: 10px 0;">{stats['today_registrations']}</h3>
            <p style="color: white; margin: 0; font-size: 14px;">Registered Today</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: #ff6b6b; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="color: white; margin: 0;">🔑</h2>
            <h3 style="color: white; margin: 10px 0;">{stats['today_logins']}</h3>
            <p style="color: white; margin: 0; font-size: 14px;">Logins Today</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Current User Profile
    st.markdown("### 👤 Your Admin Profile")
    user_info = user_db.get_user_info(st.session_state.username)
    
    if user_info:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Username:** {user_info['username']}  
            **Full Name:** {user_info['full_name'] or 'Not provided'}  
            **Email:** {user_info['email'] or 'Not provided'}  
            **Role:** 🔑 Administrator
            """)
        
        with col2:
            st.markdown(f"""
            **Member Since:** {user_info['created_at'][:10] if user_info['created_at'] else 'N/A'}  
            **Last Login:** {user_info['last_login'][:19] if user_info['last_login'] else 'Never'}  
            **Total Logins:** {user_info['login_count']}
            """)
        
        # Update Profile
        with st.expander("✏️ Update Profile"):
            with st.form("update_profile"):
                new_full_name = st.text_input(
                    "Full Name", 
                    value=user_info['full_name'] or '',
                    placeholder="Your full name"
                )
                new_email = st.text_input(
                    "Email", 
                    value=user_info['email'] or '',
                    placeholder="Your email"
                )
                
                if st.form_submit_button("💾 Update Profile", use_container_width=True):
                    success, msg = user_db.update_user_profile(
                        st.session_state.username,
                        new_full_name if new_full_name else None,
                        new_email if new_email else None
                    )
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
    
    st.markdown("---")
    
    # All Users List
    st.markdown("### 📋 All Registered Users")
    
    users = user_db.get_all_users()
    
    if users:
        df_users = pd.DataFrame(users)
        
        # Search functionality
        search = st.text_input("🔍 Search users by username or name", "")
        if search:
            df_filtered = df_users[
                df_users['username'].str.contains(search, case=False) | 
                df_users['full_name'].fillna('').str.contains(search, case=False)
            ]
        else:
            df_filtered = df_users
        
        # Format dates for better display
        if not df_filtered.empty:
            df_display = df_filtered.copy()
            df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            df_display['last_login'] = pd.to_datetime(df_display['last_login'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
            df_display['is_active'] = df_display['is_active'].map({1: '✅ Active', 0: '❌ Inactive'})
            
            # Rename columns for better display
            df_display = df_display.rename(columns={
                'username': 'Username',
                'full_name': 'Full Name',
                'email': 'Email',
                'role': 'Role',
                'created_at': 'Registered',
                'last_login': 'Last Login',
                'login_count': 'Logins',
                'is_active': 'Status'
            })
            
            # Format role column
            df_display['Role'] = df_display['Role'].map({'admin': '🔑 Admin', 'user': '👤 User'})
            
            st.dataframe(
                df_display,
                use_container_width=True,
                height=400,
                column_config={
                    "Username": st.column_config.TextColumn("Username", width="medium"),
                    "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "Role": st.column_config.TextColumn("Role", width="small"),
                    "Registered": st.column_config.TextColumn("Registered", width="medium"),
                    "Last Login": st.column_config.TextColumn("Last Login", width="medium"),
                    "Logins": st.column_config.NumberColumn("Logins", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small")
                }
            )
            
            # Download users list
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download Users List (CSV)",
                data=csv,
                file_name=f"users_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No users found matching your search")
    else:
        st.warning("No users registered yet")
    
    st.markdown("---")
    
    # User Activity Chart
    st.markdown("### 📈 User Activity")
    
    if users:
        df_activity = pd.DataFrame(users)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Login count distribution
            import plotly.express as px
            
            fig = px.bar(
                df_activity.sort_values('login_count', ascending=False).head(10),
                x='username',
                y='login_count',
                title='Top 10 Most Active Users',
                labels={'username': 'Username', 'login_count': 'Number of Logins'},
                color='login_count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # User Actions Section
    st.markdown("### ⚙️ User Actions")
    
    with st.expander("🔧 Manage User Status"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Activate User")
            user_to_activate = st.selectbox(
                "Select user to activate",
                [u['username'] for u in users if not u['is_active']],
                key="activate_user"
            )
            if st.button("✅ Activate User", use_container_width=True):
                if user_to_activate:
                    success, msg = user_db.activate_user(user_to_activate)
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
        
        with col2:
            st.markdown("#### Deactivate User")
            user_to_deactivate = st.selectbox(
                "Select user to deactivate",
                [u['username'] for u in users if u['is_active'] and u['username'] != 'admin'],
                key="deactivate_user"
            )
            if st.button("❌ Deactivate User", use_container_width=True):
                if user_to_deactivate:
                    success, msg = user_db.deactivate_user(user_to_deactivate)
                    if success:
                        st.warning(f"⚠️ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
        
        with col2:
            # Active vs Inactive users
            active_count = df_activity['is_active'].sum()
            inactive_count = len(df_activity) - active_count
            
            fig = px.pie(
                values=[active_count, inactive_count],
                names=['Active', 'Inactive'],
                title='User Status Distribution',
                color_discrete_sequence=['#51cf66', '#ff6b6b']
            )
            st.plotly_chart(fig, use_container_width=True)
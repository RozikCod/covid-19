# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime, date

def show(covid_db):
    """Display add case page"""
    st.markdown('<h1 class="main-header">➕ Add New COVID-19 Case</h1>', unsafe_allow_html=True)
    st.markdown("Enter new COVID-19 case data for a country")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("add_case_form", clear_on_submit=True):
            st.markdown("### 📝 Case Information")
            
            # Basic Information
            col_a, col_b = st.columns(2)
            with col_a:
                country = st.text_input(
                    "Country Name *",
                    placeholder="e.g., United States",
                    help="Enter the country name"
                )
            
            with col_b:
                case_date = st.date_input(
                    "Date *",
                    value=date.today(),
                    max_value=date.today(),
                    help="Select the date of the case record"
                )
            
            st.markdown("### 📊 Case Statistics")
            
            col_c, col_d = st.columns(2)
            with col_c:
                confirmed = st.number_input(
                    "Confirmed Cases",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Total confirmed cases"
                )
                
                deaths = st.number_input(
                    "Deaths",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Total deaths"
                )
            
            with col_d:
                recovered = st.number_input(
                    "Recovered Cases",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Total recovered cases"
                )
                
                active = st.number_input(
                    "Active Cases",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Current active cases"
                )
            
            # Validation notes
            st.info("💡 **Note:** Active cases are typically calculated as: Confirmed - Deaths - Recovered")
            
            # Auto-calculate suggestion
            calculated_active = confirmed - deaths - recovered
            if calculated_active != active and confirmed > 0:
                st.warning(f"⚠️ Based on your input, active cases should be approximately: **{max(0, calculated_active):,}**")
            
            # Submit button
            st.markdown("---")
            submitted = st.form_submit_button("✅ Add Case Record", use_container_width=True)
            
            if submitted:
                # Validation
                if not country or not country.strip():
                    st.error("❌ Please enter a country name")
                elif confirmed == 0 and deaths == 0 and recovered == 0 and active == 0:
                    st.error("❌ Please enter at least one non-zero value")
                elif deaths > confirmed:
                    st.error("❌ Deaths cannot exceed confirmed cases")
                elif recovered > confirmed:
                    st.error("❌ Recovered cases cannot exceed confirmed cases")
                else:
                    # Prepare case data
                    case_data = {
                        'country': country.strip().title(),
                        'date': str(case_date),
                        'confirmed': int(confirmed),
                        'deaths': int(deaths),
                        'recovered': int(recovered),
                        'active': int(active)
                    }
                    
                    # Add to database
                    success = covid_db.add_new_case(case_data)
                    
                    if success:
                        st.success("✅ Case record added successfully!")
                        st.balloons()
                        
                        # Clear cache to reflect new data
                        st.cache_resource.clear()
                        
                        # Show summary
                        st.markdown("### 📋 Added Record Summary")
                        summary_col1, summary_col2 = st.columns(2)
                        with summary_col1:
                            st.write(f"**Country:** {case_data['country']}")
                            st.write(f"**Date:** {case_data['date']}")
                        with summary_col2:
                            st.write(f"**Confirmed:** {case_data['confirmed']:,}")
                            st.write(f"**Active:** {case_data['active']:,}")
                    else:
                        st.error("❌ Failed to add case record. Please try again.")
    
    with col2:
        st.markdown("### 📌 Quick Guide")
        st.markdown("""
        **How to add a case:**
        
        1. ✏️ Enter the country name
        2. 📅 Select the date
        3. 🔢 Enter case statistics
        4. ✅ Click 'Add Case Record'
        
        ---
        
        **Tips:**
        - All fields marked with * are required
        - Use accurate and verified data
        - Active cases = Confirmed - Deaths - Recovered
        - Check for validation warnings
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Recent Activity")
        
        # Show last added cases (if the database has this method)
        try:
            recent = covid_db.get_top_countries('confirmed', 5)
            if recent:
                st.markdown("**Top 5 Countries (Confirmed):**")
                for i, record in enumerate(recent, 1):
                    st.write(f"{i}. {record.get('country', 'N/A')}: {record.get('confirmed', 0):,}")
        except:
            st.info("No recent data available")
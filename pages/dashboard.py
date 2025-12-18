# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show(covid_db):
    """Display main dashboard page"""
    st.markdown('<h1 class="main-header">🦠 COVID-19 Global Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"**Welcome back, {st.session_state.username}!**")
    
    # Global Summary Metrics
    summary = covid_db.get_global_summary()
    
    if summary:
        st.markdown("### 🌍 Global Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Total Confirmed", "total_confirmed", "🔴", "#ff6b6b"),
            ("Total Deaths", "total_deaths", "⚫", "#4a4a4a"),
            ("Total Recovered", "total_recovered", "🟢", "#51cf66"),
            ("Active Cases", "total_active", "🟡", "#ffd43b")
        ]
        
        for col, (label, key, emoji, color) in zip([col1, col2, col3, col4], metrics):
            with col:
                value = summary.get(key, 0)
                st.markdown(f"""
                <div style="background: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2 style="color: white; margin: 0;">{emoji}</h2>
                    <h3 style="color: white; margin: 10px 0;">{value:,}</h3>
                    <p style="color: white; margin: 0; font-size: 14px;">{label}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Interactive World Map
    st.markdown("### 🗺️ Interactive World Map - COVID-19 Cases by Country")
    
    # Get all countries data for map
    all_countries = covid_db.get_all_countries()
    if all_countries:
        map_data = []
        for country in all_countries:
            country_data = covid_db.compare_countries([country])
            if country_data:
                map_data.append(country_data[0])
        
        if map_data:
            df_map = pd.DataFrame(map_data)
            
            # Metric selector for map
            col_metric, col_scale = st.columns([3, 1])
            with col_metric:
                map_metric = st.selectbox(
                    "Select metric to display on map",
                    ['confirmed', 'deaths', 'recovered', 'active'],
                    format_func=lambda x: x.replace('_', ' ').title()
                )
            
            with col_scale:
                color_scales = {
                    'confirmed': 'Reds',
                    'deaths': 'Greys',
                    'recovered': 'Greens',
                    'active': 'Oranges'
                }
                selected_scale = color_scales.get(map_metric, 'Reds')
            
            # Create choropleth map
            fig_map = px.choropleth(
                df_map,
                locations="country",
                locationmode='country names',
                color=map_metric,
                hover_name="country",
                hover_data={
                    'confirmed': ':,',
                    'deaths': ':,',
                    'recovered': ':,',
                    'active': ':,',
                    'country': False
                },
                color_continuous_scale=selected_scale,
                labels={map_metric: map_metric.replace('_', ' ').title()},
                title=f'{map_metric.title()} Cases Worldwide'
            )
            
            fig_map.update_layout(
                height=500,
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='natural earth'
                )
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Country details on click simulation
            st.markdown("#### 🔍 Country Details")
            selected_country = st.selectbox(
                "Select a country to view detailed information",
                df_map['country'].tolist()
            )
            
            if selected_country:
                country_info = df_map[df_map['country'] == selected_country].iloc[0]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Confirmed", f"{country_info['confirmed']:,}")
                with col2:
                    st.metric("Deaths", f"{country_info['deaths']:,}")
                with col3:
                    st.metric("Recovered", f"{country_info['recovered']:,}")
                with col4:
                    st.metric("Active", f"{country_info['active']:,}")
                
                # Calculate rates
                if country_info['confirmed'] > 0:
                    recovery_rate = (country_info['recovered'] / country_info['confirmed'] * 100)
                    mortality_rate = (country_info['deaths'] / country_info['confirmed'] * 100)
                    active_rate = (country_info['active'] / country_info['confirmed'] * 100)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Recovery Rate", f"{recovery_rate:.2f}%")
                    with col2:
                        st.metric("Mortality Rate", f"{mortality_rate:.2f}%")
                    with col3:
                        st.metric("Active Rate", f"{active_rate:.2f}%")
    
    st.markdown("---")
    
    # Statistics Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Top 10 Most Affected Countries")
        top_confirmed = covid_db.get_top_countries('confirmed', 10)
        if top_confirmed:
            df_top = pd.DataFrame(top_confirmed)
            
            # Create horizontal bar chart for better readability
            fig = px.bar(
                df_top, 
                y='country', 
                x='confirmed',
                orientation='h',
                color='confirmed',
                color_continuous_scale='Reds',
                labels={'confirmed': 'Confirmed Cases', 'country': 'Country'},
                text='confirmed'
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Confirmed Cases",
                yaxis_title="Country"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💀 Top 10 Countries by Deaths")
        top_deaths = covid_db.get_top_countries('deaths', 10)
        if top_deaths:
            df_deaths = pd.DataFrame(top_deaths)
            
            fig = px.bar(
                df_deaths,
                y='country',
                x='deaths',
                orientation='h',
                color='deaths',
                color_continuous_scale='Greys',
                labels={'deaths': 'Deaths', 'country': 'Country'},
                text='deaths'
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Deaths",
                yaxis_title="Country"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recovery and Mortality Analysis
    st.markdown("### 📈 Recovery & Mortality Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🟢 Top 10 Recovery Rates")
        top_recovered = covid_db.get_top_countries('recovered', 10)
        if top_recovered:
            df_recovered = pd.DataFrame(top_recovered)
            if 'confirmed' in df_recovered.columns and 'recovered' in df_recovered.columns:
                df_recovered['recovery_rate'] = (df_recovered['recovered'] / df_recovered['confirmed'] * 100).round(2)
                df_recovered = df_recovered.sort_values('recovery_rate', ascending=True)
                
                fig = px.bar(
                    df_recovered,
                    y='country',
                    x='recovery_rate',
                    orientation='h',
                    color='recovery_rate',
                    color_continuous_scale='Greens',
                    labels={'recovery_rate': 'Recovery Rate (%)', 'country': 'Country'},
                    text='recovery_rate'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔴 Top 10 Mortality Rates")
        if top_confirmed:
            df_mortality = pd.DataFrame(top_confirmed)
            if 'confirmed' in df_mortality.columns and 'deaths' in df_mortality.columns:
                df_mortality['mortality_rate'] = (df_mortality['deaths'] / df_mortality['confirmed'] * 100).round(2)
                df_mortality = df_mortality.sort_values('mortality_rate', ascending=True)
                
                fig = px.bar(
                    df_mortality,
                    y='country',
                    x='mortality_rate',
                    orientation='h',
                    color='mortality_rate',
                    color_continuous_scale='Reds',
                    labels={'mortality_rate': 'Mortality Rate (%)', 'country': 'Country'},
                    text='mortality_rate'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Comparative Pie Charts
    st.markdown("### 🥧 Global Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Cases Distribution (Top 10)")
        if top_confirmed:
            df_pie = pd.DataFrame(top_confirmed)
            fig = px.pie(
                df_pie,
                values='confirmed',
                names='country',
                title='Confirmed Cases Share',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Reds
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Status Distribution (Global)")
        if summary:
            status_data = pd.DataFrame({
                'Status': ['Active', 'Recovered', 'Deaths'],
                'Count': [
                    summary.get('total_active', 0),
                    summary.get('total_recovered', 0),
                    summary.get('total_deaths', 0)
                ]
            })
            
            fig = px.pie(
                status_data,
                values='Count',
                names='Status',
                title='Global Status Distribution',
                hole=0.4,
                color='Status',
                color_discrete_map={
                    'Active': '#ffd43b',
                    'Recovered': '#51cf66',
                    'Deaths': '#4a4a4a'
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Data Table with Search
    st.markdown("### 📋 All Countries Data")
    if map_data:
        df_all = pd.DataFrame(map_data)
        
        # Search functionality
        search = st.text_input("🔍 Search for a country", "")
        if search:
            df_filtered = df_all[df_all['country'].str.contains(search, case=False)]
        else:
            df_filtered = df_all
        
        # Sort options
        col1, col2 = st.columns([2, 1])
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                ['confirmed', 'deaths', 'recovered', 'active'],
                format_func=lambda x: x.replace('_', ' ').title()
            )
        with col2:
            sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
        
        df_sorted = df_filtered.sort_values(
            by=sort_by,
            ascending=(sort_order == "Ascending")
        )
        
        st.dataframe(
            df_sorted.style.format({
                'confirmed': '{:,.0f}',
                'deaths': '{:,.0f}',
                'recovered': '{:,.0f}',
                'active': '{:,.0f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df_sorted.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Data as CSV",
            data=csv,
            file_name="covid_data_all_countries.csv",
            mime="text/csv"
        )
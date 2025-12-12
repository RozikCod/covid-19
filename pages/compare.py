import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show(covid_db):
    """Display country comparison page"""
    st.markdown('<h1 class="main-header">⚖️ Compare Countries</h1>', unsafe_allow_html=True)
    st.markdown("Select multiple countries to compare their COVID-19 statistics")
    
    countries = covid_db.get_all_countries()
    
    if not countries:
        st.warning("⚠️ No countries available in the database")
        return
    
    # Country selection
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.multiselect(
            "Select countries to compare (2-5 countries)",
            countries,
            max_selections=5,
            help="Choose between 2 and 5 countries for comparison"
        )
    
    with col2:
        st.markdown("### Quick Stats")
        st.metric("Total Countries", len(countries))
        st.metric("Selected", len(selected))
    
    if selected and len(selected) >= 2:
        comparison = covid_db.compare_countries(selected)
        
        if comparison:
            df = pd.DataFrame(comparison)
            
            # Data Table
            st.markdown("### 📋 Comparison Table")
            st.dataframe(
                df.style.format({
                    col: "{:,.0f}" for col in df.columns if col != 'country'
                }),
                use_container_width=True,
                height=250
            )
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="covid_comparison.csv",
                mime="text/csv"
            )
            
            st.markdown("---")
            
            # Metric selection for visualization
            numeric_cols = [col for col in df.columns if col != 'country']
            
            if numeric_cols:
                col1, col2 = st.columns([2, 1])
                with col1:
                    metric = st.selectbox(
                        "Select metric to visualize",
                        numeric_cols,
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                
                with col2:
                    chart_type = st.radio("Chart Type", ["Bar Chart", "Pie Chart"])
                
                st.markdown(f"### 📊 {metric.replace('_', ' ').title()} Comparison")
                
                if chart_type == "Bar Chart":
                    fig = px.bar(
                        df,
                        x='country',
                        y=metric,
                        color='country',
                        title=f'{metric.replace("_", " ").title()} by Country',
                        labels={metric: metric.replace('_', ' ').title(), 'country': 'Country'}
                    )
                    fig.update_layout(showlegend=False, height=500)
                else:
                    fig = px.pie(
                        df,
                        values=metric,
                        names='country',
                        title=f'{metric.replace("_", " ").title()} Distribution',
                        hole=0.4
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Additional comparison charts
                st.markdown("---")
                st.markdown("### 📈 Multi-Metric Comparison")
                
                # Create grouped bar chart for all metrics
                if len(numeric_cols) > 1:
                    metrics_to_compare = st.multiselect(
                        "Select metrics to compare",
                        numeric_cols,
                        default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                    
                    if metrics_to_compare:
                        fig = go.Figure()
                        for metric in metrics_to_compare:
                            fig.add_trace(go.Bar(
                                name=metric.replace('_', ' ').title(),
                                x=df['country'],
                                y=df[metric]
                            ))
                        
                        fig.update_layout(
                            barmode='group',
                            title='Multi-Metric Comparison',
                            xaxis_title='Country',
                            yaxis_title='Count',
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Statistics summary
                st.markdown("---")
                st.markdown("### 📊 Statistical Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Highest Values**")
                    for col in numeric_cols[:3]:
                        max_country = df.loc[df[col].idxmax(), 'country']
                        max_value = df[col].max()
                        st.write(f"**{col.replace('_', ' ').title()}:** {max_country} ({max_value:,.0f})")
                
                with col2:
                    st.markdown("**Lowest Values**")
                    for col in numeric_cols[:3]:
                        min_country = df.loc[df[col].idxmin(), 'country']
                        min_value = df[col].min()
                        st.write(f"**{col.replace('_', ' ').title()}:** {min_country} ({min_value:,.0f})")
                
                with col3:
                    st.markdown("**Average Values**")
                    for col in numeric_cols[:3]:
                        avg_value = df[col].mean()
                        st.write(f"**{col.replace('_', ' ').title()}:** {avg_value:,.0f}")
        
        else:
            st.error("❌ Failed to retrieve comparison data")
    
    elif selected and len(selected) < 2:
        st.info("ℹ️ Please select at least 2 countries to compare")
    else:
        st.info("ℹ️ Select countries from the dropdown above to start comparing")
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("ED Performance Trajectory Calculator")

st.markdown("""
### Instructions:
1. Upload monthly ED attendance data
2. Enter target percentages for Type 1, and Type 3 performance
3. Click "Calculate Performance Trajectory" to generate future breach projections

The app will generate:
- Historic and projected performance charts
- Stacked bar charts showing breaches and attendances within 4 hours
""")

# Upload data
uploaded_file = st.file_uploader("Upload ED Attendance Data (CSV)", type=["csv"])
if uploaded_file:
    ed_data = pd.read_csv(uploaded_file, parse_dates=['Date'], dayfirst=True)
    st.dataframe(ed_data)
    
    ed_data['Overall Performance'] = 100 * (1 - (ed_data['Type 1 Breaches'] + ed_data['Type 3 Breaches']) / (ed_data['Type 1 Attendances'] + ed_data['Type 3 Attendances']))
    ed_data['Type 1 Performance'] = 100 * (1 - ed_data['Type 1 Breaches'] / ed_data['Type 1 Attendances'])
    ed_data['Type 3 Performance'] = 100 * (1 - ed_data['Type 3 Breaches'] / ed_data['Type 3 Attendances'])

    st.subheader("Historic Performance")
    with st.container():
        _, col1, _ = st.columns([1,5,1])
        with col1:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(ed_data['Date'], ed_data['Overall Performance'], label="Overall", marker="o", color='blue')
            ax.plot(ed_data['Date'], ed_data['Type 1 Performance'], label="Type 1", marker="o", color='orange')
            ax.plot(ed_data['Date'], ed_data['Type 3 Performance'], label="Type 3", marker="o", color='green')
            ax.set_xlabel("Date")
            ax.set_ylabel("Performance (%)")
            ax.legend()
            st.pyplot(fig)

    # Input performance targets
    st.markdown("**Enter Target Percentages:**")
    col1, col2, col3, col4, col5 = st.columns(5)
    start_performance = col1.number_input("Start of Year Type 1 Target (%)", min_value=0.0, max_value=100.0, value=75.0)
    end_performance = col2.number_input("End of Year Type 1 Target (%)", min_value=0.0, max_value=100.0, value=80.0)
    type3_performance = col3.number_input("Type 3 Target (%)", min_value=0.0, max_value=100.0, value=95.0)

    def calculate_breaches(data, type3_perf, start_perf, end_perf):
        future_data = data[data['Date'] >= dt.datetime(2025, 4, 1)].copy()
        monthly_performance = np.linspace(start_perf, end_perf, len(future_data))
        future_data['Type 1 Performance'] = monthly_performance
        future_data['Projected Type 3 Breaches'] = (future_data['Type 3 Attendances'] * (1 - type3_perf / 100)).round()
        future_data['Required Type 1 Breaches'] = (future_data['Type 1 Attendances'] * (1 - monthly_performance / 100)).round()
        future_data['Type 3 Performance'] = np.full(len(future_data), type3_perf)
        future_data['Overall Performance'] = 100 * (1 - (future_data['Required Type 1 Breaches'] + future_data['Projected Type 3 Breaches']) / (future_data['Type 1 Attendances'] + future_data['Type 3 Attendances']))
        return future_data

    if st.button("Calculate Performance Trajectory"):
        calculated_data = calculate_breaches(ed_data, type3_performance, start_performance, end_performance)
        st.subheader("Performance Projections")

        with st.container():
            _, col1, _ = st.columns([1,5,1])
            with col1:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(ed_data['Date'], ed_data['Overall Performance'], label="Overall (Historic)", marker="o", color='blue')
                ax.plot(ed_data['Date'], ed_data['Type 1 Performance'], label="Type 1 (Historic)", marker="o", color='orange')
                ax.plot(ed_data['Date'], ed_data['Type 3 Performance'], label="Type 3 (Historic)", marker="o", color='green')
                ax.plot(calculated_data['Date'], calculated_data['Overall Performance'], label="Overall (Projected)", linestyle='dotted', color='blue')
                ax.plot(calculated_data['Date'], calculated_data['Type 1 Performance'], label="Type 1 (Projected)", linestyle='dotted', color='orange')
                ax.plot(calculated_data['Date'], calculated_data['Type 3 Performance'], label="Type 3 (Projected)", linestyle='dotted', color='green')
                ax.set_xlabel("Date")
                ax.set_ylabel("Performance (%)")
                ax.legend()
                st.pyplot(fig)

        # Stacked bar charts
        st.subheader("Attendances vs Breaches")
        with st.container():
            _, col1, _ = st.columns([1,5,1])
            with col1:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
                
                # Type 1 bar chart with wider bars
                bar_width = 20  # Adjust this to change the bar width
                ax1.bar(calculated_data['Date'], 
                        calculated_data['Type 1 Attendances'] - calculated_data['Required Type 1 Breaches'], 
                        width=bar_width, label="Within Target", color='skyblue')
                ax1.bar(calculated_data['Date'], 
                        calculated_data['Required Type 1 Breaches'], 
                        width=bar_width, bottom=calculated_data['Type 1 Attendances'] - calculated_data['Required Type 1 Breaches'], 
                        label="Breaches", color='salmon')
                ax1.set_title("Type 1")
                ax1.legend()
            
                # Type 3 bar chart with wider bars
                ax2.bar(calculated_data['Date'], 
                        calculated_data['Type 3 Attendances'] - calculated_data['Projected Type 3 Breaches'], 
                        width=bar_width, label="Within Target", color='skyblue')
                ax2.bar(calculated_data['Date'], 
                        calculated_data['Projected Type 3 Breaches'], 
                        width=bar_width, bottom=calculated_data['Type 3 Attendances'] - calculated_data['Projected Type 3 Breaches'], 
                        label="Breaches", color='salmon')
                ax2.set_title("Type 3")
                ax2.legend()
                st.pyplot(fig)

            _, col1, col2, _ = st.columns([1,3,3,1])
            with col1:
                st.markdown("### Type 1 Monthly Data")
                st.dataframe(calculated_data[['Date', 'Type 1 Attendances', 'Required Type 1 Breaches', 'Type 1 Performance']].rename(columns={"Type 1 Attendances": "Projected Attendances", "Required Type 1 Breaches": "Projected Breaches", "Type 1 Performance": "Projected Performance"}))
            with col2:
                st.markdown("### Type 3 Monthly Data")
                st.dataframe(calculated_data[['Date', 'Type 3 Attendances', 'Projected Type 3 Breaches', 'Type 3 Performance']].rename(columns={"Type 3 Attendances": "Projected Attendances", "Projected Type 3 Breaches": "Projected Breaches", "Type 3 Performance": "Projected Performance"}))
        
        # Export data
        csv = calculated_data.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Trajectory Data", data=csv, file_name='calculated_ed_trajectory.csv', mime='text/csv')

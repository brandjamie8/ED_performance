import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("ED Performance Trajectory Calculator")

st.markdown("""
### Instructions:
1. Upload a CSV file with monthly ED attendance data, with dates in dd/mm/yyyy format.
2. Enter target percentages for overall, Type 1, and Type 3 performances.
3. Click "Calculate Performance Trajectory" to generate future projections.
4. Adjust breach reductions as needed.

The app will generate:
- Historic and projected performance charts
- Stacked bar charts showing breaches and attendances minus breaches
""")

# Upload data
uploaded_file = st.file_uploader("Upload ED Attendance Data (CSV)", type=["csv"])
if uploaded_file:
    ed_data = pd.read_csv(uploaded_file, parse_dates=['Date'], dayfirst=True)
    ed_data['Overall Performance'] = 100 * (1 - (ed_data['Type 1 Breaches'] + ed_data['Type 3 Breaches']) / (ed_data['Type 1 Attendances'] + ed_data['Type 3 Attendances']))
    ed_data['Type 1 Performance'] = 100 * (1 - ed_data['Type 1 Breaches'] / ed_data['Type 1 Attendances'])
    ed_data['Type 3 Performance'] = 100 * (1 - ed_data['Type 3 Breaches'] / ed_data['Type 3 Attendances'])

    st.subheader("Historic Performance")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ed_data['Date'], ed_data['Overall Performance'], label="Overall", marker="o")
    ax.plot(ed_data['Date'], ed_data['Type 1 Performance'], label="Type 1", marker="o")
    ax.plot(ed_data['Date'], ed_data['Type 3 Performance'], label="Type 3", marker="o")
    ax.set_xlabel("Date")
    ax.set_ylabel("Performance (%)")
    ax.legend()
    st.pyplot(fig)

    # Input performance targets
    st.markdown("### Enter Performance Targets:")
    col1, col2, col3, col4, col5 = st.columns(5)
    start_performance = col1.number_input("Start Year Target (%)", min_value=0.0, max_value=100.0, value=90.0)
    end_performance = col2.number_input("End Year Target (%)", min_value=0.0, max_value=100.0, value=95.0)
    type3_performance = col3.number_input("Type 3 Target (%)", min_value=0.0, max_value=100.0, value=98.0)

    def calculate_breaches(data, type3_perf, start_perf, end_perf):
        future_data = data[data['Date'] >= dt.datetime(2025, 4, 1)].copy()
        future_data['Projected Type 3 Breaches'] = (future_data['Type 3 Attendances'] * (1 - type3_perf / 100)).round()
        future_data['Required Type 1 Breaches'] = ((future_data['Type 1 Attendances'] + future_data['Type 3 Attendances']) *
                                                  (1 - np.linspace(start_perf, end_perf, len(future_data)) / 100) - 
                                                  future_data['Projected Type 3 Breaches']).clip(lower=0).round()
        return future_data

    if st.button("Calculate Performance Trajectory"):
        calculated_data = calculate_breaches(ed_data, type3_performance, start_performance, end_performance)
        st.subheader("Performance Projections")

        # Plot projected performance
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(calculated_data['Date'], calculated_data['Type 1 Performance'], label="Type 1 (Historic)", marker="o")
        ax.plot(calculated_data['Date'], calculated_data['Type 3 Performance'], label="Type 3 (Historic)", marker="o")
        ax.plot(calculated_data['Date'], 100 * (1 - calculated_data['Projected Type 3 Breaches'] / calculated_data['Type 3 Attendances']), label="Type 3 (Projected)", linestyle='dotted')
        ax.plot(calculated_data['Date'], 100 * (1 - calculated_data['Required Type 1 Breaches'] / calculated_data['Type 1 Attendances']), label="Type 1 (Projected)", linestyle='dotted')
        ax.set_xlabel("Date")
        ax.set_ylabel("Performance (%)")
        ax.legend()
        st.pyplot(fig)

        # Stacked bar charts
        st.subheader("Attendances vs Breaches")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.bar(calculated_data['Date'], calculated_data['Type 1 Attendances'] - calculated_data['Required Type 1 Breaches'], label="Attendances Minus Breaches", color='skyblue')
        ax1.bar(calculated_data['Date'], calculated_data['Required Type 1 Breaches'], bottom=calculated_data['Type 1 Attendances'] - calculated_data['Required Type 1 Breaches'], label="Breaches", color='salmon')
        ax1.set_title("Type 1")
        ax1.legend()

        ax2.bar(calculated_data['Date'], calculated_data['Type 3 Attendances'] - calculated_data['Projected Type 3 Breaches'], label="Attendances Minus Breaches", color='skyblue')
        ax2.bar(calculated_data['Date'], calculated_data['Projected Type 3 Breaches'], bottom=calculated_data['Type 3 Attendances'] - calculated_data['Projected Type 3 Breaches'], label="Breaches", color='salmon')
        ax2.set_title("Type 3")
        ax2.legend()

        st.pyplot(fig)

        st.subheader("Projected Monthly Data")
        st.table(calculated_data[['Date', 'Type 1 Attendances', 'Required Type 1 Breaches', 'Type 1 Performance']].rename(columns={"Type 1 Attendances": "Projected Attendances", "Required Type 1 Breaches": "Projected Breaches", "Type 1 Performance": "Projected Performance"}))
        st.table(calculated_data[['Date', 'Type 3 Attendances', 'Projected Type 3 Breaches', 'Type 3 Performance']].rename(columns={"Type 3 Attendances": "Projected Attendances", "Projected Type 3 Breaches": "Projected Breaches", "Type 3 Performance": "Projected Performance"}))

        # Export data
        csv = calculated_data.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Trajectory Data", data=csv, file_name='calculated_ed_trajectory.csv', mime='text/csv')

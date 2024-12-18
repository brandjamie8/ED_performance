import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

st.set_page_config(layout="wide")

st.title("ED Performance Trajectory Calculator")

# Upload data
uploaded_file = st.file_uploader("Upload ED Attendance Data (CSV)", type=["csv"])
if uploaded_file:
    ed_data = pd.read_csv(uploaded_file, parse_dates=['Date'])
    st.dataframe(ed_data.head())

    # Input performance targets
    start_performance = st.number_input("Start of Year Overall 4-Hour Performance Target (%)", min_value=0.0, max_value=100.0, value=90.0)
    end_performance = st.number_input("End of Year Overall 4-Hour Performance Target (%)", min_value=0.0, max_value=100.0, value=95.0)
    type3_performance = st.number_input("Type 3 4-Hour Performance Target (%)", min_value=0.0, max_value=100.0, value=98.0)

    # Calculate breach reduction for Type 1
    def calculate_breaches(ed_data, type3_perf, start_perf, end_perf):
        ed_data['Projected Type 3 Breaches'] = ed_data['Type 3 Attendances'] * (1 - type3_perf / 100)
        ed_data['Required Type 1 Breaches'] = ((ed_data['Type 1 Attendances'] + ed_data['Type 3 Attendances']) *
                                               (1 - np.linspace(start_perf, end_perf, len(ed_data)) / 100)) - ed_data['Projected Type 3 Breaches']
        ed_data['Required Type 1 Breaches'] = ed_data['Required Type 1 Breaches'].clip(lower=0)
        return ed_data

    if st.button("Calculate Performance Trajectory"):
        calculated_data = calculate_breaches(ed_data, type3_performance, start_performance, end_performance)
        st.subheader("Calculated Performance Trajectory")
        st.dataframe(calculated_data)

        # Export calculated data
        csv = calculated_data.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Trajectory Data", data=csv, file_name='calculated_ed_trajectory.csv', mime='text/csv')

    # Allow manual adjustments
    st.subheader("Adjust Type 1 Breach Reductions")
    ed_data['Type 1 Breach Reduction'] = st.number_input("Type 1 Breach Reduction (weekly average)", min_value=0, value=0)
    ed_data['Adjusted Type 1 Breaches'] = ed_data['Required Type 1 Breaches'] - ed_data['Type 1 Breach Reduction']
    ed_data['Adjusted Type 1 Breaches'] = ed_data['Adjusted Type 1 Breaches'].clip(lower=0)
    st.dataframe(ed_data)

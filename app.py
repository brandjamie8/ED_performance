import streamlit as st
import pandas as pd
import datetime as dt

# Helper Function to calculate breaches for Type 1 ED
def calculate_type1_breaches(df, overall_target):
    """
    Calculates the number of breaches for Type 1 to meet the overall target.
    Breaches are calculated using the formula:
    Overall Breach % = (Type1 Breaches + Type3 Breaches) / Total Attendances
    """
    results = []
    for _, row in df.iterrows():
        type3_attendances = row['Type 3 Attendances']
        type3_non_breaching_percent = row['Type 3 % Not Breaching'] / 100
        total_attendances = row['Type 1 Attendances'] + type3_attendances
        
        # Calculate Type 3 breaches
        type3_breaches = type3_attendances * (1 - type3_non_breaching_percent)
        
        # Calculate Type 1 breaches needed to meet overall target
        target_breaches = total_attendances * (overall_target / 100)
        type1_breaches = max(0, target_breaches - type3_breaches)  # Breaches cannot be negative
        
        results.append(type1_breaches)
    
    return results

# Streamlit App
st.title("ED Attendances and Breaches Calculator")

# Define the months for the next financial year (April 2025 - March 2026)
start_date = dt.date(2025, 4, 1)
months = [(start_date + dt.timedelta(days=30 * i)).strftime("%B %Y") for i in range(12)]

# User input for overall target breach percentage
st.sidebar.header("Target Settings")
overall_breach_target = st.sidebar.number_input("Overall Breach Target %", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

# Table Input - User to enter monthly data
st.header("Enter Monthly Attendances and Breach Rates")
def default_data():
    return pd.DataFrame({
        'Month': months,
        'Type 1 Attendances': [0] * 12,
        'Type 3 Attendances': [0] * 12,
        'Type 3 % Not Breaching': [100] * 12,
    })

data = st.data_editor(default_data(), num_rows="dynamic")

# Validate inputs
if any(data[["Type 1 Attendances", "Type 3 Attendances", "Type 3 % Not Breaching"]].isnull().sum() > 0):
    st.error("Please ensure all columns have valid values.")
else:
    # Calculate Type 1 breaches
    data['Type 1 Breaches'] = calculate_type1_breaches(data, overall_breach_target)

    # Display the table with results
    st.subheader("Results")
    st.dataframe(data)

    # Display summary
    st.write("### Summary")
    total_type1_breaches = data['Type 1 Breaches'].sum()
    total_attendances = data['Type 1 Attendances'].sum() + data['Type 3 Attendances'].sum()
    achieved_percentage = (total_type1_breaches / total_attendances) * 100 if total_attendances else 0
    
    st.write(f"**Total Type 1 Breaches:** {total_type1_breaches:.0f}")
    st.write(f"**Total Attendances:** {total_attendances:.0f}")
    st.write(f"**Achieved Breach %:** {achieved_percentage:.2f}%")

    # Plot results
    st.subheader("Breach Breakdown")
    st.bar_chart(data[['Month', 'Type 1 Breaches']].set_index('Month'))

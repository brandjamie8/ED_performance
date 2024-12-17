import streamlit as st
import pandas as pd
import numpy as np

def calculate_type1_breaches(df, target_percent):
    """
    Calculates the number of breaches for Type 1 ED to meet the overall breach target.
    """
    results = []
    for _, row in df.iterrows():
        total_attendances = row['Type 1 Attendances'] + row['Type 3 Attendances']
        type3_breaches = row['Type 3 Attendances'] * (1 - (row['Type 3 Compliance %'] / 100))
        
        # Breaches needed for overall compliance
        required_breaches = total_attendances * (1 - (target_percent / 100))
        type1_breaches = required_breaches - type3_breaches
        
        # Ensure non-negative breaches
        type1_breaches = max(0, type1_breaches)
        results.append(type1_breaches)
    return results

def main():
    st.title("ED Breach Calculator")
    st.write("Calculate the required breaches for Type 1 ED to meet your overall compliance target.")
    
    # Set months from April 2025
    months = pd.date_range(start="2025-04-01", periods=12, freq='MS').strftime('%B %Y')
    
    # User Input Table
    st.subheader("Input Data")
    st.write("Enter the monthly attendance and compliance details.")
    
    input_data = pd.DataFrame({
        'Month': months,
        'Type 1 Attendances': [0] * 12,
        'Type 3 Attendances': [0] * 12,
        'Type 3 Compliance %': [0] * 12,
    })

    edited_df = st.data_editor(input_data, num_rows="dynamic")
    
    # Overall compliance target input
    target_percent = st.number_input(
        "Enter the overall compliance target (%)", min_value=0.0, max_value=100.0, value=95.0, step=0.1
    )
    
    # Calculate breaches
    if st.button("Calculate Breaches"):
        if edited_df.empty:
            st.error("Please fill in the input table before calculating.")
        else:
            edited_df['Type 1 Breaches Required'] = calculate_type1_breaches(edited_df, target_percent)
            st.subheader("Results")
            st.dataframe(edited_df)

            st.download_button(
                label="Download Results as CSV",
                data=edited_df.to_csv(index=False),
                file_name="breach_results.csv",
                mime='text/csv'
            )

if __name__ == "__main__":
    main()

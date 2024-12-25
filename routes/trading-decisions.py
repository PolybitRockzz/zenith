import json
import os
import streamlit as st
from datetime import datetime

st.markdown("<h1 style='margin-top: 0px; padding-top: 0px;'>Trading Decisions</h1>", unsafe_allow_html=True)

# Function to find the earliest date in the JSON files
def get_earliest_date():
    history_files = [f for f in os.listdir('./data/history') if f.endswith('.json')]
    dates = []
    for file in history_files:
        file_date = datetime.strptime(file[:-5], "%Y-%m-%d")  # Extract date from filename
        dates.append(file_date)
    return min(dates) if dates else datetime.now()  # Return the earliest date or current date if no files

# Get the earliest date for the start date input
earliest_date = get_earliest_date()

# Date range selection in two columns
st.header("Filter by Date Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=earliest_date.date())
with col2:
    end_date = st.date_input("End Date", value=datetime.now().date())

def display_history_data(start_date, end_date):
    history_files = [f for f in os.listdir('./data/history') if f.endswith('.json')]
    history_files.sort(reverse=True)  # Sort files in descending order

    for file in history_files:
        file_date = datetime.strptime(file[:-5], "%Y-%m-%d")  # Extract date from filename
        if start_date <= file_date.date() <= end_date:  # Filter by date range
            file_path = os.path.join('./data/history', file)
            with open(file_path) as f:
                data = json.load(f)
                st.subheader(f"Research Data for {file[:-5]}")  # Remove .json extension for display
                st.json(data, expanded=False)
                st.divider()

# Call the function to display history data with the selected date range
display_history_data(start_date, end_date)
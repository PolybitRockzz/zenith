import streamlit as st
import yfinance as yf
import pandas as pd
import json
import datetime
import os

st.markdown("<h1 style='margin-top: 0px; padding-top: 0px;'>Home</h1>", unsafe_allow_html=True)

# Load data from JSON file
with open('./data/companies.json') as f:
    watchlist_data = json.load(f)

# Add current price and market capitalization to each stock in watchlist_data
for stock in watchlist_data:
    ticker = stock['ticker']
    stock_info = yf.Ticker(ticker).info
    stock['price'] = stock_info['currentPrice']  # Fetch current price
    stock['market_cap'] = stock_info.get('marketCap', 0)  # Fetch market capitalization

# Create DataFrame for watchlist and sort by market capitalization in descending order
watchlist_df = pd.DataFrame(watchlist_data).sort_values(by='market_cap', ascending=False)

# Load today's analysis results if the file exists
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
research_file_path = f'./data/history/{today_date}.json'

# Check if today's research file exists
if os.path.isfile(research_file_path):
    with open(research_file_path) as f:
        analysis_results = json.load(f)
    # Create a dictionary for quick lookup of actions
    action_lookup = {result['ticker']: result['action'] for result in analysis_results}
else:
    action_lookup = {}

# Display metrics in three columns
total_value = sum(stock['price'] * stock['quantity'] for stock in watchlist_data)
difference = total_value - sum(stock['investment'] for stock in watchlist_data)
st.subheader("Stock Metrics")

# Check if total_value is zero to avoid division by zero
if total_value == 0:
    delta_value = "N/A"  # or any other placeholder you prefer
else:
    delta_value = f"+{int(difference * 100 / total_value)}%"

st.metric(label="Holdings Value", value=f"${int(total_value)}", delta=delta_value, delta_color="normal")

def format_market_cap(market_cap):
    """Format market capitalization to a shortened string with full value in parentheses."""
    if market_cap >= 1_000_000_000_000:  # Trillions
        return f"{market_cap / 1_000_000_000_000:.0f}T (${market_cap:,.0f})"
    elif market_cap >= 1_000_000_000:  # Billions
        return f"{market_cap / 1_000_000_000:.0f}B (${market_cap:,.0f})"
    elif market_cap >= 1_000_000:  # Millions
        return f"{market_cap / 1_000_000:.0f}M (${market_cap:,.0f})"
    else:
        return f"${market_cap:,.0f}"

# Display watchlist stocks
st.subheader("Watchlist Stocks")
watchlist_df['market_cap'] = watchlist_df['market_cap'].apply(format_market_cap)  # Format market cap

# Add a new column for action
watchlist_df['action'] = watchlist_df['ticker'].apply(lambda ticker: action_lookup.get(ticker, "pending"))

st.table(watchlist_df[['name', 'ticker', 'price', 'investment', 'quantity', 'market_cap', 'action']].rename(columns={
    'name': 'Stock Name',
    'ticker': 'Ticker',
    'price': 'Current Price (in US$)',
    'investment': 'My Investment (in US$)',
    'quantity': 'Quantity',
    'market_cap': 'Market Capitalization',
    'action': 'Action'
}))

st.markdown("""
    <style>
        div[data-testid="stColumn"] {
            width: fit-content !important;
            flex: unset;
        }
        div[data-testid="stColumn"] * {
            width: fit-content !important;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

@st.dialog("Add & Buy Stock")
def add_and_buy_stock():
    ticker_input = st.text_input("Enter Ticker Symbol")
    quantity_input = st.number_input("Enter Quantity of Stocks", min_value=0, step=1)

    if st.button("Submit"):
        if ticker_input:  # Allow adding stock even if quantity is zero
            # Fetch company name from the API
            ticker_data = yf.Ticker(ticker_input)
            company_info = ticker_data.info

            company_name = company_info.get('longName', ticker_input)  # Fallback to ticker if name is not available

            # Check if the stock already exists in the watchlist
            stock_exists = next((stock for stock in watchlist_data if stock['ticker'] == ticker_input), None)

            if stock_exists:
                stock_exists['quantity'] += quantity_input
                stock_exists['investment'] += stock_exists['price'] * quantity_input
            else:
                # If the stock is not found, add a new entry
                new_stock = {
                    "name": company_name,
                    "ticker": ticker_input,
                    "investment": quantity_input * company_info.get('currentPrice', 0),  # Set investment to quantity * price of each share
                    "quantity": quantity_input
                }
                watchlist_data.append(new_stock)

            # Save the updated data back to the JSON file
            with open('./data/companies.json', 'w') as f:
                json.dump(watchlist_data, f, indent=4)

            st.success(f"Successfully added {quantity_input} shares of {company_name}.")
            st.rerun()
        else:
            st.error("Please enter a valid ticker.")

@st.dialog("Sell & Delete Stock")
def sell_and_delete_stock():
    ticker_input = st.text_input("Enter Ticker Symbol to Sell")
    quantity_input = st.number_input("Enter Quantity of Stocks to Sell", min_value=0, step=1)

    if st.button("Submit"):
        if ticker_input and quantity_input > 0:
            stock_exists = next((stock for stock in watchlist_data if stock['ticker'] == ticker_input), None)

            if stock_exists:
                if stock_exists['quantity'] >= quantity_input:
                    stock_exists['quantity'] -= quantity_input
                    stock_exists['investment'] -= stock_exists['price'] * quantity_input

                    if stock_exists['quantity'] == 0:
                        watchlist_data.remove(stock_exists)  # Remove stock if quantity is zero

                    # Save the updated data back to the JSON file
                    with open('./data/companies.json', 'w') as f:
                        json.dump(watchlist_data, f, indent=4)

                    st.success(f"Successfully sold {quantity_input} shares of {ticker_input}.")
                    st.rerun()
                else:
                    st.error("You do not have enough shares to sell.")
            else:
                st.error("Stock not found in watchlist.")
        else:
            st.error("Please enter a valid ticker and quantity.")

with col1:
    if st.button("Add & Buy Stock"):
        add_and_buy_stock()
with col2:
    if st.button("Sell & Delete Stock"):
        sell_and_delete_stock()
with col3:
    st.button("Download Data")
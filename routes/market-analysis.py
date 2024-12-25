import json
import requests
import streamlit as st
import google.generativeai as genai
import yfinance as yf
import datetime
import os

@st.dialog("Add & Buy Stock")
def add_and_buy_stock(ticker, quantity):
    with open('./data/companies.json') as f:
        watchlist_data = json.load(f)
    
    ticker_input = st.text_input("Enter Ticker Symbol", value=ticker)
    quantity_input = st.number_input("Enter Quantity of Stocks", min_value=0, step=1, value=quantity)

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
        else:
            st.error("Please enter a valid ticker.")

@st.dialog("Sell & Delete Stock")
def sell_and_delete_stock(ticker, quantity):
    with open('./data/companies.json') as f:
        watchlist_data = json.load(f)
    
    ticker_input = st.text_input("Enter Ticker Symbol to Sell", value=ticker)
    quantity_input = st.number_input("Enter Quantity of Stocks to Sell", min_value=0, step=1, value=quantity)

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
                else:
                    st.error("You do not have enough shares to sell.")
            else:
                st.error("Stock not found in watchlist.")
        else:
            st.error("Please enter a valid ticker and quantity.")


def main():
    st.markdown("<h1 style='margin-top: 0px; padding-top: 0px;'>Market Analysis</h1>", unsafe_allow_html=True)
    
    # API Keys
    news_api_key = '9520daaea79f47e99b19e8d93c50123c'
    gemini_api_key = 'AIzaSyDFOCIqOIF1o39ijCymc60XazvWTwiXEJQ'
    
    news_api_key = st.text_input('News API Key', value=news_api_key, type='password')
    gemini_api_key = st.text_input('Gemini API Key', value=gemini_api_key, type='password')
    
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    research_file_path = f'./data/history/{today_date}.json'
    
    # Check if today's research file exists
    research_file_exists = os.path.isfile(research_file_path)

    if st.button('Start Research', disabled=research_file_exists):
        # Initialize analysis results array
        analysis_results = []
        # Load companies from JSON file
        with open('./data/companies.json') as f:
            companies = json.load(f)

        # Loop through each company and fetch news
        for company in companies:
            name = company.get('name')
            if name:
                # Fetch top news for the ticker
                url = f'https://newsapi.org/v2/everything?q={name}&apiKey={news_api_key}'
                response = requests.get(url)
                news_data = response.json()
                
                # Display news articles
                if news_data.get('articles'):
                    prompt = f"I am providing you with the titles of the news articles for {name}. You are a financial analyst and you are going to analyze the news and provide strictly a json object with the following fields: summary, sentiment, and whether we should buy, sell, or hold the stock based on the news. The json object should be in the following format: {{'summary': 'summary of the news', 'sentiment': 'positive', 'action': 'buy'}}. The sentiment should be one of the following: positive, negative, or neutral. The action should be one of the following: buy, sell, or hold. The summary should be a short summary of the news article. Now, here are the news articles:\n"
                    i = 0
                    for article in news_data['articles']:
                        if i >= 10:
                            break
                        prompt += f"1. \"{article['title']}\" - from {article['author']} published on {article['publishedAt']}\n"
                        i += 1
                    
                    # Get response from GenAI
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash-exp")
                    response = model.generate_content(prompt)
                    
                    # Parse the output into JSON
                    response_text = response.text[response.text.index("```json\n") + 8 : response.text.rindex("\n```")]
                    response_json = json.loads(response_text)
                    
                    sentiment = [0,0,0]
                    for i in range(len(response_json)):
                        sentiment[['positive', 'neutral', 'negative'].index(response_json[i]['sentiment'])] += 1
                    action = [0,0,0]
                    for i in range(len(response_json)):
                        action[['buy', 'hold', 'sell'].index(response_json[i]['action'])] += 1
                    
                    st.header(f"{name} ({company['ticker']})")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Overall Sentiment: {['positive', 'neutral', 'negative'][sentiment.index(max(sentiment))]}")
                        st.write(f"Overall Action: {['buy', 'hold', 'sell'][action.index(max(action))]}")
                    with col2:
                        if st.button('Buy', key=f'buy_{company["ticker"]}', icon=':material/trending_up:'):
                            add_and_buy_stock(company['ticker'], 1)
                        st.button('Hold', key=f'hold_{company["ticker"]}', icon=':material/trending_flat:', disabled=True)
                        if st.button('Sell', key=f'sell_{company["ticker"]}', icon=':material/trending_down:'):
                            sell_and_delete_stock(company['ticker'], 1)
                    
                    st.json(response_text, expanded=False)
                    
                    st.divider()
                    
                    # Collect analysis results
                    analysis_results.append({
                        "name": name,
                        "ticker": company['ticker'],
                        "sentiment": ['positive', 'neutral', 'negative'][sentiment.index(max(sentiment))],
                        "action": ['buy', 'hold', 'sell'][action.index(max(action))],
                        "details": response_json
                    })
                else:
                    st.write(f"No news found for {name}.")

        # After processing all companies, save the analysis results to a JSON file
        if analysis_results:
            with open(research_file_path, 'w') as f:
                json.dump(analysis_results, f, indent=4)

    # Add "View Research" button
    if st.button('View Research', disabled=not research_file_exists):
        with open(research_file_path) as f:
            existing_data = json.load(f)
            
            for result in existing_data:
                st.header(f"{result['name']} ({result['ticker']})")
                st.write(f"Overall Sentiment: {result['sentiment']}")
                st.write(f"Overall Action: {result['action']}")
                st.json(result['details'], expanded=False)
                st.divider()

main()

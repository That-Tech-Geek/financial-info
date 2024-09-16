import streamlit as st
import yfinance as yf

# Function to fetch and display data for selected ticker
def display_ticker_data(ticker):
    stock = yf.Ticker(ticker)
    st.write(f"**Ticker:** {ticker}")
    st.write("**Company Info:**")
    st.write(stock.info)
    st.write("**Financials:**")
    st.write(stock.financials)
    st.write("**Quarterly Financials:**")
    st.write(stock.quarterly_financials)
    st.write("**Balance Sheet:**")
    st.write(stock.balance_sheet)
    st.write("**Quarterly Balance Sheet:**")
    st.write(stock.quarterly_balance_sheet)
    st.write("**Cashflow:**")
    st.write(stock.cashflow)
    st.write("**Quarterly Cashflow:**")
    st.write(stock.quarterly_cashflow)
    st.write("**Earnings:**")
    st.write(stock.earnings)
    st.write("**Quarterly Earnings:**")
    st.write(stock.quarterly_earnings)
    st.write("**Sustainability:**")
    st.write(stock.sustainability)
    st.write("**Recommendations:**")
    st.write(stock.recommendations)

# Streamlit app
st.title("Stock Data Fetcher")

# Input box for comma-delimited tickers
tickers_input = st.text_input("Enter a comma-separated list of tickers (e.g., AAPL, MSFT, GOOG)")

# Convert the input into a list of tickers
tickers_list = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

# Display tickers in a dropdown if any are entered
if tickers_list:
    selected_ticker = st.selectbox("Select a ticker to view data", options=tickers_list)

    # Display data for the selected ticker
    if selected_ticker:
        display_ticker_data(selected_ticker)

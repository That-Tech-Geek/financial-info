import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# File path to save the CSV
file_path = r"C:\\Users\\91891\\OneDrive\\Desktop\\AlfaZeta\\Fundraising Division\\Apparel Stocks.csv"

# Helper function to convert non-serializable data to serializable format
def serialize_data(data):
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, pd.Series):
        return data.to_dict()  # Convert Series to dictionary
    elif isinstance(data, pd.DataFrame):
        return data.to_dict()  # Convert DataFrame to dictionary
    elif isinstance(data, pd.Timestamp):
        return data.isoformat()  # Convert Timestamp to ISO format string
    elif isinstance(data, list):
        return [serialize_data(i) for i in data]
    return data

# Helper function to search for a financial parameter in multiple possible keys
def search_parameter(data, possible_keys):
    for key in possible_keys:
        if key in data and data[key] is not None:
            return data[key]
    return None

# Helper functions to calculate ratios
def calculate_total_current_assets(balance_sheet):
    return search_parameter(balance_sheet, [
        'Total Current Assets', 'Current Assets', 'Total Curr Assets', 'Current Assets Total', 'Current Assets (Total)'
    ])

def calculate_total_current_liabilities(balance_sheet):
    return search_parameter(balance_sheet, [
        'Total Current Liabilities', 'Current Liabilities', 'Total Curr Liab', 'Current Liabilities Total', 'Current Liabilities (Total)'
    ])

def calculate_total_assets(balance_sheet):
    return search_parameter(balance_sheet, [
        'Total Assets', 'Assets', 'Total Assets Net Minority Interest', 'Total Net Assets', 'Assets Total'
    ])

def calculate_total_liabilities(balance_sheet):
    return search_parameter(balance_sheet, [
        'Total Liabilities Net Minority Interest', 'Total Liabilities', 'Liabilities', 'Total Liabilities (Net of Minority Interest)', 'Liabilities Total'
    ])

def calculate_total_equity(total_assets, total_liabilities):
    return total_assets - total_liabilities if total_assets is not None and total_liabilities is not None else None

def calculate_inventory(balance_sheet):
    return search_parameter(balance_sheet, [
        'Inventory', 'Inventories', 'Stock', 'Stock-in-Trade'
    ])

def calculate_net_income(income_statement):
    return search_parameter(income_statement, [
        'Net Income', 'Net Profit', 'Profit After Tax', 'Net Earnings', 'Earnings After Tax'
    ])

def calculate_operating_income(income_statement):
    return search_parameter(income_statement, [
        'Operating Income', 'Operating Profit', 'EBIT', 'Earnings Before Interest and Taxes', 'Operating Earnings'
    ])

def calculate_interest_expense(income_statement):
    return search_parameter(income_statement, [
        'Interest Expense', 'Interest Costs', 'Interest Paid', 'Interest Charges', 'Finance Costs'
    ])

def calculate_cash_flow_investing(cash_flow_statement):
    return search_parameter(cash_flow_statement, [
        'Cash Flow From Continuing Investing Activities', 'Total Cash From Investing Activities',
        'Cash Flow From Investing', 'Investing Cash Flow', 'Cash Flow From Investments'
    ])

# Function to calculate financial ratios
def calculate_ratios(balance_sheet, income_statement, cash_flow_statement):
    ratios = {}

    # Calculate Total Current Assets
    total_current_assets = calculate_total_current_assets(balance_sheet)
    # Calculate Total Current Liabilities
    total_current_liabilities = calculate_total_current_liabilities(balance_sheet)
    
    if total_current_liabilities is None or total_current_assets is None:
        return {}

    # Total Assets
    total_assets = calculate_total_assets(balance_sheet)
    
    # Total Liabilities
    total_liabilities = calculate_total_liabilities(balance_sheet)
    
    # Total Equity
    total_equity = calculate_total_equity(total_assets, total_liabilities)
    
    # Debt-to-Equity Ratio
    if total_equity is not None and total_equity != 0:
        ratios['Debt-to-Equity Ratio'] = total_liabilities / total_equity
    else:
        ratios['Debt-to-Equity Ratio'] = float('inf')

    # Current Ratio
    if total_current_liabilities != 0:
        ratios['Current Ratio'] = total_current_assets / total_current_liabilities
    else:
        ratios['Current Ratio'] = float('inf')
    
    # Quick Ratio
    inventory = calculate_inventory(balance_sheet)
    if inventory is not None and total_current_liabilities != 0:
        ratios['Quick Ratio'] = (total_current_assets - inventory) / total_current_liabilities
    else:
        ratios['Quick Ratio'] = float('inf')

    # Return on Equity (ROE)
    net_income = calculate_net_income(income_statement)
    if net_income is not None and total_equity is not None and total_equity != 0:
        ratios['Return on Equity (ROE)'] = net_income / total_equity
    else:
        ratios['Return on Equity (ROE)'] = float('inf')

    # Interest Coverage Ratio
    operating_income = calculate_operating_income(income_statement)
    interest_expense = calculate_interest_expense(income_statement)
    if operating_income is not None and interest_expense is not None and interest_expense != 0:
        ratios['Interest Coverage Ratio'] = operating_income / interest_expense
    else:
        ratios['Interest Coverage Ratio'] = float('inf')

    # Cash Flow from Investing Activities
    cash_flow_investing = calculate_cash_flow_investing(cash_flow_statement)
    ratios['Cash Flow from Investing Activities'] = cash_flow_investing

    return ratios

# Function to fetch data for a single company
def fetch_company_data(ticker):
    try:
        # Fetch data from Yahoo Finance
        company = yf.Ticker(ticker)
        
        # Check if the data is available
        if not company.info or 'regularMarketPrice' not in company.info:
            raise ValueError(f"Ticker {ticker} is not valid or not available.")

        # Extract and serialize financial statements
        balance_sheet = serialize_data(company.balance_sheet.to_dict())
        income_statement = serialize_data(company.financials.to_dict())
        cash_flow_statement = serialize_data(company.cashflow.to_dict())
        financials = serialize_data(company.info)

        # Calculate financial ratios
        ratios = calculate_ratios(balance_sheet, income_statement, cash_flow_statement)

        # Return the data
        return {
            'Ticker': ticker,
            'Market Cap': financials.get('marketCap'),
            'Enterprise Value': financials.get('enterpriseValue'),
            'EBITDA': financials.get('ebitda'),
            'P/E Ratio': financials.get('trailingPE'),
            'P/S Ratio': financials.get('priceToSalesTrailing12Months'),
            **ratios
        }
    except Exception as e:
        return {
            'Ticker': ticker,
            'Error': str(e)
        }

# Main function to get user input and process data
def main():
    # Get input from the user
    tickers_input = input("Enter Company Tickers (e.g., AAPL, MSFT, TSLA) separated by commas: ")
    tickers = [ticker.strip() for ticker in tickers_input.split(",") if ticker.strip()]

    if tickers:
        # Create an empty DataFrame to store the results
        columns = ['Ticker', 'Market Cap', 'Enterprise Value', 'EBITDA', 'P/E Ratio', 'P/S Ratio',
                   'Debt-to-Equity Ratio', 'Current Ratio', 'Quick Ratio', 'Return on Equity (ROE)',
                   'Interest Coverage Ratio', 'Cash Flow from Investing Activities']
        valuation_df = pd.DataFrame(columns=columns)

        # Log for tickers that failed
        failed_tickers = []

        # Use ThreadPoolExecutor for multitasking with up to 5 workers
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all ticker tasks to the executor
            future_to_ticker = {executor.submit(fetch_company_data, ticker): ticker for ticker in tickers}

            # Process each completed future
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    # Get the result from the future
                    company_data = future.result()

                    # If there's no error, and data is valid, append the data to the DataFrame
                    if 'Error' not in company_data:
                        company_df = pd.DataFrame([company_data])
                        if not company_df.empty:
                            valuation_df = pd.concat([valuation_df, company_df], ignore_index=True)
                    else:
                        failed_tickers.append(company_data['Ticker'])
                except Exception as e:
                    failed_tickers.append(ticker)

        # Save the results to a CSV file
        valuation_df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")

        # Print failed tickers
        if failed_tickers:
            print(f"Failed to fetch data for the following tickers: {', '.join(failed_tickers)}")

if __name__ == "__main__":
    main()

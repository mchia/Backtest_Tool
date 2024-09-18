import yfinance as yf
import numpy as np
import pandas as pd

def get_financial_ratios(ticker):
    # Retrieve data
    stock: yf.Ticker = yf.Ticker(ticker)
    income_statement: pd.DataFrame = stock.financials
    balance_sheet: pd.DataFrame = stock.balance_sheet
    cash_flow: pd.DataFrame = stock.cashflow
    
    # Extract relevant financial figures
    try:
        net_income: float = income_statement.loc['Net Income'].iloc[0]
        total_revenue: float = income_statement.loc['Total Revenue'].iloc[0]
        shareholders_equity: float = balance_sheet.loc['Stockholders Equity'].iloc[0]

        current_assets: float = balance_sheet.loc['Current Assets'].iloc[0]
        other_current_assets: float = balance_sheet.loc['Other Current Assets'].iloc[0]
        total_current_assets: float = current_assets + other_current_assets

        current_liabilities: float = balance_sheet.loc['Current Liabilities'].iloc[0]
        other_current_liabilities: float = balance_sheet.loc['Other Current Liabilities'].iloc[0]
        total_current_liabilities: float = current_liabilities + other_current_liabilities
        
        # Extract cash flow metrics
        operating_cash_flow: float = cash_flow.loc['Operating Cash Flow'].iloc[0]
        capital_expenditures: float= cash_flow.loc['Capital Expenditure'].iloc[0]
        
        # Calculate ratios
        profit_margin: float = net_income / total_revenue
        debt_to_equity: float = total_current_liabilities / shareholders_equity
        current_ratio: float = total_current_assets / current_liabilities
        free_cash_flow: float = operating_cash_flow - capital_expenditures
        
        # Sharpe Ratio Calculation (requires historical returns and risk-free rate)
        # For simplicity, we'll use a placeholder value for the risk-free rate
        risk_free_rate : float= 0.02  # Example risk-free rate (2%)
        historical_returns: pd.DataFrame = stock.history(period='1y')['Close'].pct_change().dropna()
        average_return: float = historical_returns.mean()
        return_std: float = historical_returns.std()
        sharpe_ratio: float = (average_return - risk_free_rate) / return_std if return_std != 0 else np.nan
        
        if profit_margin > 0.2 and current_ratio > 1.5 and debt_to_equity < 1.0 and sharpe_ratio > 1.5:
            return "Excellent"
        elif profit_margin > 0.1 and current_ratio > 1.0 and debt_to_equity < 1.5 and sharpe_ratio > 1.0:
            return "Good"
        elif profit_margin > 0.05 and current_ratio > 0.5 and debt_to_equity < 2.0 and sharpe_ratio > 0.5:
            return "Average"
        elif profit_margin > 0 and current_ratio > 0.2 and debt_to_equity < 3.0 and sharpe_ratio > 0:
            return "Poor"
        else:
            return "Very Poor"
    except KeyError as e:
        return "Data Incomplete"

# Example usage
ticker = 'BTC-USD'
performance = get_financial_ratios(ticker)
print(f"The performance of {ticker} is: {performance}")
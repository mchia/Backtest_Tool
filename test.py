# import yfinance as yf
# import numpy as np
# import pandas as pd

# def get_financial_ratios(ticker):
#     # Retrieve data
#     stock: yf.Ticker = yf.Ticker(ticker)
#     income_statement: pd.DataFrame = stock.financials
#     balance_sheet: pd.DataFrame = stock.balance_sheet
#     cash_flow: pd.DataFrame = stock.cashflow
    
#     # Extract relevant financial figures
#     try:
#         net_income: float = income_statement.loc['Net Income'].iloc[0]
#         total_revenue: float = income_statement.loc['Total Revenue'].iloc[0]
#         shareholders_equity: float = balance_sheet.loc['Stockholders Equity'].iloc[0]

#         current_assets: float = balance_sheet.loc['Current Assets'].iloc[0]
#         other_current_assets: float = balance_sheet.loc['Other Current Assets'].iloc[0]
#         total_current_assets: float = current_assets + other_current_assets

#         current_liabilities: float = balance_sheet.loc['Current Liabilities'].iloc[0]
#         other_current_liabilities: float = balance_sheet.loc['Other Current Liabilities'].iloc[0]
#         total_current_liabilities: float = current_liabilities + other_current_liabilities
        
#         # Extract cash flow metrics
#         operating_cash_flow: float = cash_flow.loc['Operating Cash Flow'].iloc[0]
#         capital_expenditures: float= cash_flow.loc['Capital Expenditure'].iloc[0]
        
#         # Calculate ratios
#         profit_margin: float = net_income / total_revenue
#         debt_to_equity: float = total_current_liabilities / shareholders_equity
#         current_ratio: float = total_current_assets / current_liabilities
#         free_cash_flow: float = operating_cash_flow - capital_expenditures
        
#         # Sharpe Ratio Calculation (requires historical returns and risk-free rate)
#         # For simplicity, we'll use a placeholder value for the risk-free rate
#         risk_free_rate : float= 0.02  # Example risk-free rate (2%)
#         historical_returns: pd.DataFrame = stock.history(period='1y')['Close'].pct_change().dropna()
#         average_return: float = historical_returns.mean()
#         return_std: float = historical_returns.std()
#         sharpe_ratio: float = (average_return - risk_free_rate) / return_std if return_std != 0 else np.nan
        
#         if profit_margin > 0.2 and current_ratio > 1.5 and debt_to_equity < 1.0 and sharpe_ratio > 1.5:
#             return "Excellent"
#         elif profit_margin > 0.1 and current_ratio > 1.0 and debt_to_equity < 1.5 and sharpe_ratio > 1.0:
#             return "Good"
#         elif profit_margin > 0.05 and current_ratio > 0.5 and debt_to_equity < 2.0 and sharpe_ratio > 0.5:
#             return "Average"
#         elif profit_margin > 0 and current_ratio > 0.2 and debt_to_equity < 3.0 and sharpe_ratio > 0:
#             return "Poor"
#         else:
#             return "Very Poor"
#     except KeyError as e:
#         return "Data Incomplete"

# # Example usage
# ticker = 'AMZN'
# performance = get_financial_ratios(ticker)
# print(f"The performance of {ticker} is: {performance}")

import backtrader as bt
import pandas as pd

# Create a custom RSI indicator
class CustomRSI(bt.indicators.RSI):
    plotlines = dict(
        rsi=dict(color='#4CAF50', linewidth=2.0),  # Green RSI line
        lowerband=dict(color='blue', linestyle='--'),  # Blue dashed oversold line
        upperband=dict(color='red', linestyle='--'),  # Red dashed overbought line
    )

    plotinfo = dict(
        plot=True,
        subplot=True,
        plotname='Custom RSI',
        plotylimited=True,  # Limits the plot between 0 and 100
        plotvaluetags=False  # Disable value tags on the plot
    )

    

# Define the RSI Strategy
class RSI_Strategy(bt.Strategy):
    params = (
        ('Period', 14),
        ('Oversold', 30),
        ('Overbought', 70),
    )

    def __init__(self):
        self.rsi = CustomRSI(
            period=self.params.Period,
            upperband=self.params.Overbought,
            lowerband=self.params.Oversold,
        )

    def next(self):
        if self.rsi < self.params.Oversold:
            self.buy()
        elif self.rsi > self.params.Overbought:
            self.sell()

cerebro = bt.Cerebro()
import yfinance as yf
# Create a sample DataFrame
data: pd.DataFrame = yf.download(tickers='TSLA', start='2020-01-01', end='2024-01-01', interval='1d')

# Convert the DataFrame to Backtrader data feed
data_feed = bt.feeds.PandasData(dataname=data)

# Add the data feed to Cerebro
cerebro.adddata(data_feed)

# Add the strategy
cerebro.addstrategy(RSI_Strategy)

# Set initial cash
cerebro.broker.set_cash(1000)

# Run the strategy
cerebro.run()

# Plot the results
cerebro.plot()
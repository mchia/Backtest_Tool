# import backtrader as bt
# import yfinance as yf
# import pandas as pd

# class RSIStrategy(bt.Strategy):
#     params = (
#         ('rsi_period', 14),  # Period for RSI calculation
#         ('rsi_overbought', 70),  # RSI threshold to enter a short position
#         ('rsi_oversold', 30),  # RSI threshold to close short and go long
#     )

#     def __init__(self):
#         # Add RSI indicator to the strategy
#         self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)

#     def log(self, txt, dt=None):
#         ''' Logging function for strategy'''
#         dt = dt or self.datas[0].datetime.date(0)
#         print(f'{dt.isoformat()}, {txt}')

#     def next(self):
#         # If we're not in the market, check for entry conditions
#         if not self.position:
#             # Enter a short position if RSI is above the overbought threshold
#             if self.rsi > self.params.rsi_overbought:
#                 self.sell()  # Open a short position
#                 self.log(f'SELL ORDER EXECUTED: RSI {self.rsi[0]:.2f}, Price {self.data.close[0]:.2f}')
                
#         # If we're in a short position, check for exit conditions
#         elif self.position.size < 0:
#             # Close the short if RSI is below the oversold threshold
#             if self.rsi < self.params.rsi_oversold:
#                 self.close()  # Close the short position
#                 self.log(f'CLOSE SHORT: RSI {self.rsi[0]:.2f}, Price {self.data.close[0]:.2f}')

# # Create an instance of the Backtrader engine
# cerebro = bt.Cerebro()

# # Add the RSI strategy
# cerebro.addstrategy(RSIStrategy)

# # Get historical data for a stock using yfinance (Tesla stock in this case)
# data = yf.download(tickers='TSLA', start='2020-01-01', end='2024-09-30', interval='1d')
# data.index = pd.to_datetime(data.index)
# data_feed: bt.feeds.PandasData = bt.feeds.PandasData(dataname=data)

# # Add the data to the backtest
# cerebro.adddata(data_feed)

# # Set the starting cash for the backtest
# cerebro.broker.setcash(10000)

# # Set the commission and margin (this allows shorting with 2% margin)
# cerebro.broker.setcommission(commission=0.001, margin=0.02)  # Simulating margin trading with 2% margin

# # Enable cheating-on-close to simulate margin/shorting better
# cerebro.broker.set_coc(True)

# # Run the backtest
# print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
# cerebro.run()
# print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# # Plot the results
# cerebro.plot()

import backtrader as bt
import yfinance as yf
import pandas as pd

class ShortRSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),        # RSI period
        ('rsi_overbought', 70),    # RSI overbought threshold (for short entry)
        ('rsi_exit', 30),          # RSI exit threshold (for short exit)
        ('leverage', 2),           # Leverage factor for margin
    )

    def __init__(self):
        # RSI indicator
        self.rsi = bt.indicators.RSI(self.data, period=self.params.rsi_period)

    def next(self):
        # If RSI is above overbought level, enter a short position
        if not self.position and self.rsi < self.params.rsi_exit:
            self.buy()  # Enter short position

        # If RSI falls back below the exit level, close the short position
        elif self.position and self.rsi > self.params.rsi_overbought:
            self.close() 

# Set up the backtesting environment
cerebro = bt.Cerebro()

# Add data to Cerebro
data: pd.DataFrame = yf.download(tickers='BTC-USD', start='2022-01-01', end='2024-01-01', interval='1d')
data.index = pd.to_datetime(data.index)
data_feed: bt.feeds.PandasData = bt.feeds.PandasData(dataname=data)
cerebro.adddata(data_feed)

# Add the short selling strategy to Cerebro
cerebro.addstrategy(ShortRSIStrategy)

# Set leverage and commission (to simulate margin trading)
cerebro.broker.setcommission(leverage=2)  # Set 2x leverage for margin trading
cerebro.broker.set_cash(10000)            # Starting capital

# Run the backtest
cerebro.run()

# Plot the results
cerebro.plot()
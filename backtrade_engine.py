import pandas as pd
import backtrader as bt
import custom_visuals as cv
import matplotlib.pyplot as plt
from unittest.mock import patch

# Apply patch to bt.Cerebro.plot and overwrite it with cv.patched_plot to prevent show() from being called.
patch.object(target=bt.Cerebro, attribute='plot', new=cv.patched_plot).start()

class BacktraderEngine:
    def __init__(self, capital: int, datafeed: bt.feeds.PandasData, ticker: str, strategy: str, interval: str) -> None:
        """
        Initializes the cerebro engine with a capital, datafeed, ticker, and strategy.

        Parameters
        ----------
        capital : int
            The starting balance to be used for backtesting.
        datafeed : bt.feeds.PandasData
            The datasource containing historical stock data to be backtested against.
        ticker : str
            The stock ticker symbol (e.g., 'TSLA' for Tesla, 'AAPL' for Apple).
        strategy : str
            The trading strategy to be backtested e.g. MACD, RSI, Golden Crossover etc.

        Returns
        -------
        None
        """
        self.datafeed: pd.DataFrame = datafeed
        self.ticker: str = ticker
        self.strategy: str = strategy
        self.interval: str = interval

        self.cerebro: bt.Cerebro = bt.Cerebro(stdstats=False)
        self.cerebro.broker.set_cash(capital)
        self.cerebro.broker.setcommission(commission=0.001)
        
        # Add default observers manually
        self.cerebro.addobserver(cv.AccountValue)
        self.cerebro.addobserver(cv.Transactions)

    def execute(self) -> bt.Cerebro:
        """
        Method that uses the cerebro engine from backtrader, to backtest data.

        Returns
        -------
        self.cerebro
            The current instance of cerebro.
        """
        self.cerebro.adddata(data=self.datafeed)
        self.cerebro.addstrategy(strategy=self.strategy, ticker=self.ticker, interval=self.interval)
        self.cerebro.run()
        return self.cerebro

class BackPlotter:
    def __init__(self, bt_instance: bt.Cerebro) -> None:
        """
        Utilizes a cerebro instance to display a visual representation of trades performed by the backtest engine.

        Parameters
        ----------
        bt_instance : bt.Cerebro
            An active instance of cerebro that has already executed backtesting.
        
        Returns
        -------
        None
        """
        self.cerebro = bt_instance
        self.colour = '#4682B4'

    def plot_settings(self) -> None:
        """
        Method to control aspects of the plot's visual interface.

        Returns
        -------
        None
        """
        plt.rcParams['axes.facecolor'] = 'none'
        plt.rcParams['figure.facecolor'] = 'none'
        plt.rcParams['axes.edgecolor'] = self.colour
        plt.rcParams['axes.labelcolor'] = self.colour
        plt.rcParams['xtick.color'] = self.colour
        plt.rcParams['ytick.color'] = self.colour
        plt.rcParams["legend.labelcolor"] = self.colour

    def bt_plot(self) -> plt.Figure:
        """
        Plots the results of the backtest using the active cerebro instance.

        The plot will show candlestick charts, with custom colors for up and down bars, and
        no grid or volume overlay.

        Returns
        -------
        matplotlib.figure.Figure
            The figure object generated from the cerebro plot.
        """
        self.plot_settings()
        fig = self.cerebro.plot(
            style='candlestick',
            barup='#089981',
            bardown='#f23645',
            grid=False,
            voloverlay=False,
            volup='#089981',
            voldown='#f23645'
        )

        return fig[0][0]
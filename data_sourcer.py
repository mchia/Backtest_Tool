import pandas as pd
import yfinance as yf
import backtrader as bt
from typing import Optional
from ttkbootstrap.dialogs import Messagebox

class DataSourcer:
    """
    Class that sources historical data for backtesting, through the Yahoo Finance API and returns it as a Pandas Dataframe.
    Attributes
    ----------
    ticker : str
        The stock ticker symbol (e.g., 'TSLA' for Tesla, 'AAPL' for Apple).
    start : str
        The start date for the historical data in 'YYYY-MM-DD' format.
    end : str
        The end date for the historical data in 'YYYY-MM-DD' format.
    interval : str
        The data interval (e.g., '1d' for daily, '1wk' for weekly, '1mo' for monthly).

    Methods
    -------
    retrieve_data() -> Optional[bt.feeds.PandasData]
        Retrieves historical stock data from Yahoo Finance, converts it into a Backtrader 
        compatible format, and returns it. If data retrieval fails or the data is empty, 
        returns None.
    """
    def __init__(self, ticker: str, start_date: str, end_date: str, interval: str) -> None:
        """
        Initializes the DataSourcer with the ticker symbol, date range, and interval.

        Parameters
        ----------
        ticker : str
            The stock ticker symbol (e.g., 'TSLA' for Tesla, 'AAPL' for Apple).
        start_date : str
            The start date for the historical data in 'YYYY-MM-DD' format.
        end_date : str
            The end date for the historical data in 'YYYY-MM-DD' format.
        interval : str
            The data interval (e.g., '1d' for daily, '1wk' for weekly, '1mo' for monthly).

        Returns
        -------
        None
        """
        self.ticker: str = ticker
        self.start: str = start_date
        self.end: str = end_date
        self.interval: str = interval

    def retrieve_data(self) -> Optional[bt.feeds.PandasData]:
        """
        Method that uses the Yahoo Finance API to retrieve historical stock data.

        Returns
        -------
        bt.feeds.PandasData or None
            A Backtrader PandasData feed if data download is successful, None if the data is
            empty or an error occurs.
        """
        try:
            data: pd.DataFrame = yf.download(tickers=self.ticker, start=self.start, end=self.end, interval=self.interval)

            if data.empty:
                Messagebox.show_error(
                    title='Data Download Failed',
                    message=(
                        f"{self.ticker} may be delisted or the date range is invalid.\n"
                        "Check for special tickers (e.g., EURUSD=X for forex, BTC-USD for crypto)."
                    )
                )
                return None
        except ValueError as e:
            print(f"Error: {e}")
            return None
        
        data.index = pd.to_datetime(data.index)
        data_feed: bt.feeds.PandasData = bt.feeds.PandasData(dataname=data)
        
        return data_feed
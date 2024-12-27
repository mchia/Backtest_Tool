import pandas as pd
import yfinance as yf
import backtrader as bt
from typing import Optional, Tuple
from custom_methods import convert_number
from ttkbootstrap.dialogs import Messagebox

intervals: dict = {
    "1 Minute": "1m",
    "2 Minutes": "2m",
    "5 Minutes": "5m",
    "15 Minutes": "15m",
    "30 Minutes": "30m",
    "90 Minutes": "90m",
    "Hourly": "1h",
    "Daily": "1d",
    "5 Days": "5d",
    "Weekly": "1wk",
    "Monthly": "1mo",
    "3 Months": "3mo"
    }

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

    def retrieve_data(self) -> Optional[Tuple[bt.feeds.PandasData, pd.DataFrame]]:
        """
        Method that uses the Yahoo Finance API to retrieve historical stock data.

        Returns
        -------
        bt.feeds.PandasData or None
            A Backtrader PandasData feed if data download is successful, None if the data is
            empty or an error occurs.
        """
        try:
            data: pd.DataFrame = yf.download(tickers=self.ticker, start=self.start, end=self.end, interval=self.interval, multi_level_index=False)

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
        
        return (data_feed, data)
    
    def ticker_profile(self) -> dict:
        """
        Retrieves and formats information about a specific stock ticker using the Yahoo Finance API.

        This method queries the Yahoo Finance API to gather and display key details about the 
        stock ticker, including company name, ticker symbol, industry, sector, market cap, 
        and trading volume.

        Returns
        -------
        info_text : str
            A string containing the company's information, with each detail on a new line.
        """
        stock: yf.Ticker = yf.Ticker(self.ticker)
        stock_info: dict = stock.info

        insider_holders: str = f"{round(100 * stock_info.get('heldPercentInsiders', 0), 2)}%"
        institutional_holders: str = f"{round(100 * stock_info.get('heldPercentInstitutions', 0), 2)}%"

        short_ratio: float = stock_info.get('shortRatio', 'N/A')
        if short_ratio != 'N/A':
            if short_ratio <= 3:
                sentiment: str = 'Bullish'
            elif 3 < short_ratio <= 5:
                sentiment: str = 'Neutral'
            elif short_ratio > 5:
                sentiment: str = 'Bearish'
        else:
            sentiment: str = 'N/A'

        company_info: dict = {
            "Ticker": stock_info.get("symbol"),
            "Company Name": stock_info.get("longName"),
            "Industry": stock_info.get("industry") if stock_info.get("industry") else 'Unavailable',
            "Sector": stock_info.get("sector") if stock_info.get("sector") else 'Unavailable',
            "Market Cap": convert_number(value=stock_info.get("marketCap")),
            "Volume": convert_number(value=stock_info.get("volume")),
            "% of Shares Held by Insiders": insider_holders,
            "% of Shares Held by Institutions": institutional_holders,
            "Short Ratio": short_ratio,
            "Sentiment": sentiment
        }

        return company_info

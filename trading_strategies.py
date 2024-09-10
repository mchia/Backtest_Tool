import math
import pandas as pd
from backtrader import Strategy, indicators

class StrategyBase(Strategy):
    """
    Class provides a template for creating custom trading strategies by managing orders,
    tracking trades, and calculating various performance metrics.

    Attributes
    ----------
    ticker : str
        The stock ticker symbol (e.g., 'TSLA' for Tesla, 'AAPL' for Apple).
    interval : str
        The data interval (e.g., '1d' for daily, '1wk' for weekly).
    dataclose : float
        Reference to the closing price data.
    order : int or None
        The current order being processed (if any).
    buyprice : float or None
        The price at which a buy order was executed.
    buycomm : float or None
        The commission paid for the buy order.
    size_to_buy : float or None
        The size of the buy order.
    trades : int
        Total number of trades executed.
    wins : int
        Number of winning trades.
    losses : int
        Number of losing trades.
    total_gross_profit : float
        Total gross profit from winning trades.
    total_gross_losses : float
        Total gross losses from losing trades.
    total_net_profit : float
        Total net profit after accounting for commissions.
    total_net_losses : float
        Total net losses after accounting for commissions.
    total_fees : float
        Total fees paid.
    trade_id : int
        Unique identifier for each trade.
    """

    def __init__(self, ticker: str, interval: str) -> None:
        """
        Initializes the strategy with ticker symbol and data interval.

        Parameters
        ----------
        ticker : str
            The stock ticker symbol.
        interval : str
            The data interval.
        """
        self.ticker: str = ticker
        self.interval: str = interval
        self.initialize_indicators()

        self.dataclose: float = self.datas[0].close
        self.order: int = None
        self.buyprice: float = None
        self.buycomm: float = None
        self.size_to_buy: float = None

        self.trades: int = 0
        self.wins: int = 0
        self.losses: int = 0
        self.total_gross_profit: float = 0
        self.total_gross_losses: float = 0
        self.total_net_profit: float = 0
        self.total_net_losses: float = 0
        self.total_fees: float = 0
        self.trade_id: int = 1

    def start(self) -> None:
        """
        Initializes attributes and lists to hold trade data before the strategy starts running.

        Sets the initial capital and prepares lists for storing buy and sell transactions, as well as trade results.
        """
        self.capital = self.cerebro.broker.getvalue()
        self.buy_transactions: list = []
        self.sell_transactions: list = []
        self.trade_results: list = []

    def notify_order(self, order) -> None:
        """
        Handles order notifications and records transactions.

        Parameters
        ----------
        order : backtrader.Order
            The order object being notified.

        Returns
        -------
        None
        """
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_transactions.append(
                    [
                        self.trade_id,
                        self.datas[0].datetime.date(0),
                        order.executed.price,
                        order.executed.comm,
                        order.executed.size
                    ]
                )
            else:
                self.sell_transactions.append(
                    [
                        self.trade_id,
                        self.datas[0].datetime.date(0),
                        order.executed.price,
                        order.executed.comm
                    ]
                )
            self.bar_executed = len(self)

        self.order = None

    def notify_trade(self, trade) -> None:
        """
        Handles trade notifications and updates trade statistics.

        Parameters
        ----------
        trade : backtrader.Trade
            The trade object being notified.

        Returns
        -------
        None
        """
        if not trade.isclosed:
            return

        gross: float = trade.pnl
        net: float = trade.pnlcomm
        fees: float = net - gross

        if gross > 0:
            self.wins += 1
            self.total_gross_profit += gross
            self.total_net_profit += net
        elif gross < 0:
            self.losses += 1
            self.total_gross_losses += abs(gross)
            self.total_net_losses += abs(net)

        self.trades += 1
        self.total_fees += fees
        self.trade_results.append(
            [
                self.trade_id,
                round(trade.pnl, 0),
                round(trade.pnlcomm, 0),
                self.cerebro.broker.getcash()
            ]
        )

        self.trade_id += 1

    def print_trade_stats(self) -> None:
        """
        Prints a summary of trade statistics, including account balance, profit, loss, and the number of trades.

        Returns
        -------
        None
        """
        ending_balance: float = round(self.cerebro.broker.getcash(), 2)
        account_growth: float = round(100 * ((ending_balance - 100000) / 100000), 2)
        tgp: float = round(self.total_gross_profit, 2)
        tgl: float = round(self.total_net_losses, 2)

        tnp: float = round(self.total_net_profit, 2)
        tnl: float = round(self.total_net_losses, 2)

        total_fees: float = round(self.total_fees, 2)

        print(
            f'Starting Balance: ${self.capital}, Ending Balance: ${ending_balance}, Account Growth: {account_growth}%')
        print(
            f'Total Gross Profit: ${tgp}, Total Net Profit: ${tnp}')
        print(
            f'Total Gross Losses: ${tgl}, Total Net Losses: ${tnl}')
        print(f'Total Fees: ${total_fees}')
        print(f'Total Trades: {self.trades}, Wins: {self.wins}, Losses: {self.losses}')
        print(self.trade_results)

    def trade_logs(self) -> None:
        """
        Creates and prints detailed trade logs, including entry and exit transactions, fees, and trade results.

        Returns
        -------
        None
        """
        buy_table: pd.DataFrame = pd.DataFrame(data=self.buy_transactions, columns=['id', 'entry_date', 'entry_price', 'buying_fee', 'shares'])
        sell_table: pd.DataFrame = pd.DataFrame(data=self.sell_transactions, columns=['id', 'exit_date', 'exit_price', 'selling_fee'])
        results_table: pd.DataFrame = pd.DataFrame(data=self.trade_results, columns=['id', 'gross_earnings', 'net_earnings', 'acc_bal'])

        transaction_table: pd.DataFrame = pd.merge(buy_table, sell_table, on='id', how='inner')
        transaction_data: pd.DataFrame = pd.merge(transaction_table, results_table, on='id', how='inner')
        transaction_data['total_fees'] = transaction_data['buying_fee'] + transaction_data['selling_fee']
        transaction_data['percentage_gain'] = round((transaction_data['exit_price'] - transaction_data['entry_price']) / transaction_data['entry_price'] * 100, 2)
        transaction_data['trade_duration'] = (pd.to_datetime(transaction_data['exit_date']) - pd.to_datetime(transaction_data['entry_date'])).dt.days
        transaction_data['ticker'] = self.ticker
        transaction_data['interval'] = self.interval
        transaction_data['strategy'] = self.__class__.__name__
        transaction_data = transaction_data[
            ['id',
            'ticker',
            'interval',
            'strategy',
            'entry_date',
            'exit_date',
            'entry_price',
            'exit_price',
            'shares',
            'buying_fee',
            'selling_fee',
            'total_fees',
            'trade_duration',
            'percentage_gain',
            'gross_earnings',
            'net_earnings',
            'acc_bal']
        ]

        print(transaction_data)

    def initialize_indicators(self) -> None:
        """
        Method to initialize strategy-specific indicators.

        This method should be implemented by subclasses to set up any technical indicators required by the strategy.

        Raises
        ------
        NotImplementedError
            If not implemented by the subclass.
        """
        raise NotImplementedError("Must be implemented by the subclass")

    def buy_signal(self) -> bool:
        """
        Method to define the buy signal condition.

        This method should be implemented by subclasses to provide the logic for generating buy signals.

        Returns
        -------
        bool
            True if a buy signal is generated, otherwise False.

        Raises
        ------
        NotImplementedError
            If not implemented by the subclass.
        """
        raise NotImplementedError("Must be implemented by the subclass")

    def sell_signal(self) -> bool:
        """
        Method to define the sell signal condition.

        This method should be implemented by subclasses to provide the logic for generating sell signals.

        Returns
        -------
        bool
            True if a sell signal is generated, otherwise False.

        Raises
        ------
        NotImplementedError
            If not implemented by the subclass.
        """
        raise NotImplementedError("Must be implemented by the subclass")

    def next(self) -> None:
        """
        Method called on each iteration of the strategy.

        Checks if there is an active position. If not, it evaluates the buy signal and places a buy order if the signal is true.
        If there is an active position and the sell signal is true, it closes the position.

        Returns
        -------
        None
        """
        if not self.position:
            if self.buy_signal():
                size_to_buy: int = math.floor(self.broker.getvalue() / self.data.close[0]) * 0.8
                self.buy(size=size_to_buy)
        elif self.sell_signal():
            self.sell(size=self.position.size)

class RSI_Strategy(StrategyBase):
    """
    Strategy: RSI (Relative Strength Index)

    Indicators
    ----------
    RSI : backtrader.indicators.RSI
        Relative Strength Index calculated with a specified period.

    Buy Signal
    ----------
    Generated when the RSI is below the oversold threshold.

    Sell Signal
    ----------
    Generated when the RSI is above the overbought threshold.

    Parameters
    ----------
    rsi_period : int
        The period for calculating the RSI (default is 14).
    oversold : int
        The RSI value below which a buy signal is generated (default is 30).
    overbought : int
        The RSI value above which a sell signal is generated (default is 70).
    """

    params: tuple[tuple[str, int]] = (
        ('rsi_period', 14),
        ('oversold', 30),
        ('overbought', 70)
    )

    def initialize_indicators(self) -> None:
        """
        Initializes the RSI indicator with the specified period.

        Returns
        -------
        None
        """
        self.rsi = indicators.RSI(period=self.params.rsi_period)

    def buy_signal(self) -> bool:
        """
        Checks if a buy signal is generated.

        A buy signal is generated when the RSI is below the oversold threshold and there is no existing position.

        Returns
        -------
        bool
            True if the RSI is below the oversold threshold and there is no existing position, otherwise False.
        """
        return (
            self.position.size == 0
            and self.rsi < self.params.oversold
        )

    def sell_signal(self) -> bool:
        """
        Checks if a sell signal is generated.

        A sell signal is generated when the RSI is above the overbought threshold and there is an existing position.

        Returns
        -------
        bool
            True if the RSI is above the overbought threshold and there is an existing position, otherwise False.
        """
        return (
            self.position.size > 0
            and self.rsi > self.params.overbought
        )

class GoldenCross(StrategyBase):
    """
    Strategy: Golden Crossover

    Indicators
    ----------
    Fast MA : backtrader.indicators.EMA
        Exponential Moving Average with a short period (50 days).
    Slow MA : backtrader.indicators.EMA
        Exponential Moving Average with a long period (200 days).
    Golden Cross : backtrader.indicators.CrossOver
        Indicator to detect crossovers between the fast and slow EMAs.

    Buy Signal
    ----------
    Generated when the fast moving average crosses the slow moving average to the upside and the closing price is above the slow MA.

    Sell Signal
    ----------
    Generated when the slow moving average crosses the fast moving average to the downside.
    
    Parameters
    ----------
    fast : int
        The period for the fast EMA (default is 50).
    slow : int
        The period for the slow EMA (default is 200).
    """

    params: tuple[tuple[str, int]] = (
        ('fast', 50),
        ('slow', 200)
    )

    def initialize_indicators(self) -> None:
        """
        Initializes the EMA indicators and the crossover detector.

        Returns
        -------
        None
        """
        self.slow_ma = indicators.EMA(self.datas[0].close, period=self.params.fast, plotname='50d MA')
        self.fast_ma = indicators.EMA(self.datas[0].close, period=self.params.slow, plotname='200d MA')
        self.goldencross = indicators.CrossOver(self.slow_ma, self.fast_ma)

    def buy_signal(self) -> bool:
        """
        Checks if a buy signal is generated.

        A buy signal is generated when the fast moving average crosses the slow moving average to the upside, and the current price is above the slow MA.

        Returns
        -------
        bool
            True if the crossover is bullish and the price is above the slow MA, otherwise False.
        """
        return (
            self.position.size == 0
            and self.goldencross == 1
            and self.data.close[0] > (self.slow_ma[0] and self.slow_ma[-1])
            )

    def sell_signal(self) -> bool:
        """
        Checks if a sell signal is generated.

        A sell signal is generated when the slow moving average crosses the fast moving average to the downside and there is an existing position.

        Returns
        -------
        bool
            True if the crossover is bearish, otherwise False.
        """
        return (
            self.position.size > 0
            and self.goldencross == -1
            )

class Bollinger_Bands(StrategyBase):
    """
    Strategy: Bollinger Bands

    Indicators
    ----------
    Bollinger Bands : backtrader.indicators.BollingerBands
        Bollinger Bands calculated with a specified period and standard deviation factor.

    Buy Signal
    ----------
    Generated when the price closes below the bottom of the Bollinger Bands.

    Sell Signal
    ----------
    Generated when the price closes above the top of the Bollinger Bands.

    Parameters
    ----------
    period : int
        The period for calculating the Bollinger Bands (default is 20).
    stddev : int
        The number of standard deviations for the Bollinger Bands (default is 2).
    """
    
    params: tuple[tuple[str, int]] = (
        ('period', 20),
        ('stddev', 2)
    )

    def initialize_indicators(self):
        """
        Initializes the Bollinger Bands indicator.

        Returns
        -------
        None
        """
        self.bbands = indicators.BollingerBands(self.data, period=self.params.period, devfactor=self.params.stddev)

    def buy_signal(self) -> bool:
        """
        Checks if a buy signal is generated.

        A buy signal is generated when the price closes below the bottom of the Bollinger Bands and there is no existing position.

        Returns
        -------
        bool
            True if the price is below the bottom band and there is no existing position, otherwise False.
        """
        return (
            self.position.size == 0
            and self.data.close[0] <= self.bbands.lines.bot[0]
            )

    def sell_signal(self) -> bool:
        """
        Checks if a sell signal is generated.

        A sell signal is generated when the price closes above the top of the Bollinger Bands and there is an existing position.

        Returns
        -------
        bool
            True if the price is above the top band and there is an existing position, otherwise False.
        """
        return (
            self.position.size > 0
            and self.data.close[0] >= self.bbands.lines.top[0]
            )
    
class IchimokuCloud(StrategyBase):
    """
    Strategy: Ichimoku Cloud

    Indicators
    ----------
    Tenkan-sen : backtrader.indicators.Ichimoku
        The conversion line of the Ichimoku Cloud, calculated with a specified period.
    Kijun-sen : backtrader.indicators.Ichimoku
        The base line of the Ichimoku Cloud, calculated with a specified period.
    Senkou Span A : backtrader.indicators.Ichimoku
        The first leading span of the Ichimoku Cloud, calculated with a specified period.
    Senkou Span B : backtrader.indicators.Ichimoku
        The second leading span of the Ichimoku Cloud, calculated with a specified period.
    Chikou Span : backtrader.indicators.Ichimoku
        The lagging span of the Ichimoku Cloud, calculated with a specified shift.

    Buy Signal
    ----------
    Generated when:
    - The Tenkan-sen is above the Kijun-sen.
    - The current closing price is above both the Senkou Span A and Senkou Span B.

    Sell Signal
    ----------
    Generated when:
    - The Tenkan-sen is below the Kijun-sen.
    - The current closing price is below both the Senkou Span A and Senkou Span B.

    Parameters
    ----------
    tenkan : int
        The period for the Tenkan-sen calculation (default is 9).
    kijun : int
        The period for the Kijun-sen calculation (default is 26).
    senkou : int
        The period for the Senkou Span A and B calculations (default is 52).
    shift : int
        The shift for the Chikou Span calculation (default is 26).
    """

    params: tuple[tuple[str, int]] = (
        ('tenkan', 9),
        ('kijun', 26),
        ('senkou', 52),
        ('shift', 26)
    )

    def initialize_indicators(self) -> None:
        """
        Initializes the Ichimoku Cloud indicator components with the specified parameters.

        Returns
        -------
        None
        """
        self.ichi = indicators.Ichimoku(
            tenkan=self.params.tenkan,
            kijun=self.params.kijun,
            senkou=self.params.senkou,
            plot=True
        )

        self.tenkan_sen = self.ichi.tenkan_sen
        self.kijun_sen = self.ichi.kijun_sen
        self.senkou_span_a = self.ichi.senkou_span_a
        self.senkou_span_b = self.ichi.senkou_span_b
        self.chikou_span = self.ichi.chikou_span(-self.params.shift)

    def buy_signal(self) -> bool:
        """
        Checks if a buy signal is generated.

        A buy signal is generated when:
        - The Tenkan-sen is above the Kijun-sen.
        - The closing price is above both the Senkou Span A and Senkou Span B.
        - There is no existing position.

        Returns
        -------
        bool
            True if the conditions for a buy signal are met, otherwise False.
        """
        return (
            self.position.size == 0
            and (self.tenkan_sen[0] > self.kijun_sen[0])
            and (self.data.close[0] > self.senkou_span_a[0])
            and (self.data.close[0] > self.senkou_span_b[0])
            )

    def sell_signal(self) -> bool:
        """
        Checks if a sell signal is generated.

        A sell signal is generated when:
        - The Tenkan-sen is below the Kijun-sen.
        - The closing price is below both the Senkou Span A and Senkou Span B.
        - There is an existing position.

        Returns
        -------
        bool
            True if the conditions for a sell signal are met, otherwise False.
        """
        return (
            self.position.size > 0
            and (self.tenkan_sen[0] < self.kijun_sen[0])
            and (self.data.close[0] < self.senkou_span_a[0])
            and (self.data.close[0] < self.senkou_span_b[0])
            )

strategies_dict: dict = {
    "RSI Strategy": RSI_Strategy,
    "Bollinger Bands": Bollinger_Bands,
    "Golden Crossover": GoldenCross,
    "Ichimoku Cloud": IchimokuCloud
}

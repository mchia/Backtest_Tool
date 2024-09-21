import math
import pandas as pd
import ttkbootstrap as tb
from backtrader import Strategy, indicators
from custom_methods import thousand_separator
from strategy_params import strategy_params as strat

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

    def __init__(self, ticker: str, interval: str, capital: int, disp_pane: tb.Frame, params: dict = None) -> None:
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
        self.params = params if params else strat.get(self.__class__.__name__)
        self.display_pane = disp_pane
        self.capita = capital
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

        self.realised_balance: list[float] = []
        self.stop_loss: float|None = None
        self.stopped_out: int = 0
        self.stop_loss_flag: bool=  None

    def start(self) -> None:
        """
        Initializes attributes and lists to hold trade data before the strategy starts running.

        Sets the initial capital and prepares lists for storing buy and sell transactions, as well as trade results.
        """
        self.capital: float = self.cerebro.broker.getvalue()
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
                        order.executed.size,
                        self.stop_loss
                    ]
                )
            else:
                self.sell_transactions.append(
                    [
                        self.trade_id,
                        self.datas[0].datetime.date(0),
                        order.executed.price,
                        order.executed.comm,
                        self.stop_loss_flag
                    ]
                )
            self.bar_executed: int = len(self)

        self.order: int|None = None

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
        self.realised_balance.append(self.cerebro.broker.getcash())
        self.trade_results.append(
            [
                self.trade_id,
                round(trade.pnl, 0),
                round(trade.pnlcomm, 0),
                self.cerebro.broker.getcash()
            ]
        )

        self.trade_id += 1

    def print_trade_stats(self) -> dict:
        """
        Prints a summary of trade statistics, including account balance, profit, loss, and the number of trades.
        Clears existing row_frames before creating new ones.
        """
        capital: int = int(self.capital)

        realised_balance: float = self.realised_balance[-1]
        unrealised_balance: float = round(self.cerebro.broker.getvalue(), 2)
        portfolio_growth: float = 100 * ((unrealised_balance - capital) / capital)
        portfolio_growth: float|int = round(number=portfolio_growth, ndigits=2) if portfolio_growth < 1 else int(round(number=portfolio_growth, ndigits=2))

        unrealised_pnl: float = unrealised_balance - realised_balance
        realised_pnl: float = realised_balance - capital
        realised_growth: int = 100 * ((realised_balance - capital) / capital)
        realised_growth: float|int = round(number=realised_growth, ndigits=2) if realised_growth < 1 else int(round(number=realised_growth, ndigits=2))

        total_fees: float = abs(round(self.total_fees, 2))

        def acc_value(parameter: float) -> str:
            match parameter:
                case _ if parameter > capital:
                    str_val: str = f"▲ ${thousand_separator(value=abs(parameter))}  ▲"
                case _ if parameter < capital:
                    str_val: str = f"▼ ${thousand_separator(value=abs(parameter))}  ▼"

            return str_val
        
        def pl_value(parameter: float) -> str:
            match parameter:
                case _ if round(number=parameter, ndigits=0) == 0:
                    str_val: str = "$0"
                case _ if parameter > 0:
                    str_val: str = f"▲ ${thousand_separator(value=abs(parameter))}"
                case _ if parameter < 0:
                    str_val: str = f"▼ ${thousand_separator(value=abs(parameter))}"
            
            return str_val
        
        result_summary: dict = {
            "Opening Balance": f"${thousand_separator(value=capital)}",
            "Account Value": f"{acc_value(parameter=realised_balance)}{realised_growth}%",
            "Portfolio Value": f"{acc_value(parameter=unrealised_balance)}{portfolio_growth}%",
            "Realised P/L": pl_value(parameter=realised_pnl),
            "Unrealised P/L": pl_value(parameter=unrealised_pnl),
            "Fees": f"${thousand_separator(value=total_fees)}",
            "Trades (W/L)": f"{self.trades} ({self.wins}:{self.losses})",
            "Stop-Loss Hit": self.stopped_out
        }

        return result_summary

    def trade_logs(self) -> pd.DataFrame:
        """
        Creates and prints detailed trade logs, including entry and exit transactions, fees, and trade results.

        Returns
        -------
        None
        """
        buy_table: pd.DataFrame = pd.DataFrame(data=self.buy_transactions, columns=['id', 'entry_date', 'entry_price', 'buying_fee', 'shares', 'stop_loss'])
        sell_table: pd.DataFrame = pd.DataFrame(data=self.sell_transactions, columns=['id', 'exit_date', 'exit_price', 'selling_fee', 'stop_loss_flag'])
        results_table: pd.DataFrame = pd.DataFrame(data=self.trade_results, columns=['id', 'gross_earnings', 'net_earnings', 'acc_bal'])

        transaction_table: pd.DataFrame = pd.merge(buy_table, sell_table, on='id', how='left')
        transaction_data: pd.DataFrame = pd.merge(transaction_table, results_table, on='id', how='left')
        transaction_data['total_fees'] = transaction_data['buying_fee'] + transaction_data['selling_fee']
        transaction_data['percentage_gain'] = round((transaction_data['exit_price'] - transaction_data['entry_price']) / transaction_data['entry_price'] * 100, 2)
        transaction_data['trade_duration'] = (pd.to_datetime(transaction_data['exit_date']) - pd.to_datetime(transaction_data['entry_date'])).dt.days
        transaction_data['ticker'] = self.ticker
        transaction_data['interval'] = self.interval
        transaction_data['strategy'] = self.__class__.__name__
        transaction_data['exit_type'] = transaction_data.apply(lambda row: 'Stop-Loss' if row['stop_loss_flag'] == True else 'Standard', axis=1)
        transaction_data: pd.DataFrame = transaction_data[
            ['id',
            'ticker',
            'interval',
            'strategy',
            'entry_date',
            'exit_date',
            'entry_price',
            'stop_loss',
            'exit_price',
            'exit_type',
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

        return transaction_data

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
                self.entry_price: float = self.data.close[0]
                self.size_to_buy: int = math.floor(self.broker.getvalue() / self.entry_price) * 0.8
                self.stop_loss: float = self.entry_price * (1 - self.params.get('Stop-Loss %'))
                self.buy(size=self.size_to_buy)

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
    def initialize_indicators(self) -> None:
        """
        Initializes the RSI indicator with the specified period.

        Returns
        -------
        None
        """
        self.rsi: indicators = indicators.RSI(period=self.params.get('Period'))

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
            and self.rsi < self.params.get('Oversold')
        )

    def sell_signal(self) -> bool:
        """
        Checks if a sell signal is generated.

        A sell signal is generated when the RSI is above the overbought threshold, or the stop-loss is hit.

        Returns
        -------
        bool
            True if the RSI is above the overbought threshold or the stop-loss is hit, otherwise False.
        """
        if self.position.size > 0:
            if self.data.close[0] <= self.stop_loss:
                self.stopped_out += 1
                self.stop_loss_flag: bool = True
                return True

            elif self.rsi > self.params.get('Overbought'):
                self.stop_loss_flag: bool = False
                return True

        return False
    
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
    def initialize_indicators(self) -> None:
        """
        Initializes the EMA indicators and the crossover detector.

        Returns
        -------
        None
        """
        self.fast_val: int = self.params.get('Fast EMA')
        self.slow_val: int = self.params.get('Slow EMA')

        self.slow_ema: indicators = indicators.EMA(self.datas[0].close, period=self.fast_val, plotname=f'{self.fast_val}d EMA')
        self.fast_ema: indicators = indicators.EMA(self.datas[0].close, period=self.slow_val, plotname=f'{self.slow_val}d EMA')
        self.goldencross: indicators = indicators.CrossOver(self.slow_ema, self.fast_ema)

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
            and self.data.close[0] > (self.slow_ema[0] and self.slow_ema[-1])
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
            or self.data.close[0] <= self.stop_loss
            )

class BollingerBands(StrategyBase):
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
    def initialize_indicators(self):
        """
        Initializes the Bollinger Bands indicator.

        Returns
        -------
        None
        """
        self.bbands: indicators = indicators.BollingerBands(self.data, period=self.params.get('Period'), devfactor=self.params.get('Standard Dev'))

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
            or self.data.close[0] <= self.stop_loss
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
    def initialize_indicators(self) -> None:
        """
        Initializes the Ichimoku Cloud indicator components with the specified parameters.

        Returns
        -------
        None
        """
        self.ichi: indicators = indicators.Ichimoku(
            tenkan=self.params.get('Tenkan'),
            kijun=self.params.get('Kijun'),
            senkou=self.params.get('Senkou'),
            plot=True
        )

        self.tenkan_sen: float = self.ichi.tenkan_sen
        self.kijun_sen: float = self.ichi.kijun_sen
        self.senkou_span_a: float = self.ichi.senkou_span_a
        self.senkou_span_b: float = self.ichi.senkou_span_b
        self.chikou_span: int = self.ichi.chikou_span(-self.params.get('Shift'))

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
            or self.data.close[0] <= self.stop_loss
            )

class MACD(StrategyBase):
    def initialize_indicators(self) -> None:
        """
        Initializes the RSI indicator with the specified period.

        Returns
        -------
        None
        """
        self.macd: indicators = indicators.MACDHisto(
            self.data.close,
            period_me1=self.params.get('Fast MA'),
            period_me2=self.params.get('Slow MA'),
            period_signal=self.params.get('Signal')
        )

        self.crossover: indicators = indicators.CrossOver(self.macd.macd, self.macd.signal)

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
            and self.crossover > 0
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
            and self.macd < 0
            or self.data.close[0] <= self.stop_loss
        )

class GoldenRatio(StrategyBase):
    """
    Golden Ratio trading strategy based on Fibonacci retracement and extension levels.

    Parameters
    ----------
    lookback_period : int
        The number of periods to look back to determine the highest and lowest prices.
    extension_target : float
        The Fibonacci extension level for take profit.
    stop_loss_pct : float
        The percentage of loss to trigger a stop loss.
    """
    def initialize_indicators(self):
        self.highest: indicators = indicators.Highest(self.data.high, period=self.params.get('Lookback'), plot=False, subplot=False)
        self.lowest: indicators = indicators.Lowest(self.data.low, period=self.params.get('Lookback'), plot=False, subplot=False)
        self.entry_price: float|None = None
        self.fib_618: float|None = None
        self.fib_extension: float|None = None

    def buy_signal(self) -> bool:
        return (
            self.position.size == 0
            and self.data.close[0] <= (self.highest[0] - ((self.highest[0] - self.lowest[0]) * 0.618))
        )

    def next(self):
        if not self.position:
            if self.buy_signal():
                self.entry_price: float = self.data.close[0]
                self.fib_618: float = self.highest[0] - ((self.highest[0] - self.lowest[0]) * 0.618)
                self.fib_extension: float = self.highest[0] + ((self.highest[0] - self.lowest[0]) * self.params.get('Extension Target'))
                self.stop_loss: float = self.entry_price * (1 - self.params.get('Stop-Loss %'))

                size_to_buy: int = math.floor(self.broker.getvalue() / self.data.close[0]) * 0.8
                self.buy(size=size_to_buy)

        else:
            if self.sell_signal():
                self.sell(size=self.position.size)

    def sell_signal(self) -> bool:
        return (
            self.position.size > 0
            and (
                self.data.close[0] >= self.fib_extension
                or self.data.close[0] <= self.stop_loss
            )
        )

strategies_dict: dict[str, Strategy] = {
    "MACD Strategy": MACD,
    "RSI Strategy": RSI_Strategy,
    "Ichimoku Cloud": IchimokuCloud,
    "Bollinger Bands": BollingerBands,
    "Golden Crossover": GoldenCross,
    "Fibonacci Strategy": GoldenRatio
}

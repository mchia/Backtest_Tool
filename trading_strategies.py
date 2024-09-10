import math
import pandas as pd
from backtrader import Strategy, indicators

class StrategyBase(Strategy):
    def __init__(self, ticker: str, interval: str) -> None:
        self.ticker: str = ticker
        self.interval: str = interval
        self.initialize_indicators()

        # Strategy Parameters
        self.dataclose: float = self.datas[0].close
        self.order: int = None
        self.buyprice: float = None
        self.buycomm: float = None
        self.size_to_buy: float = None

        # Trade Statistics
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
        # Initialize attributes here to ensure they're set before the strategy runs
        self.capital = self.cerebro.broker.getvalue()

        # Lists to hold data
        self.buy_transactions: list = []
        self.sell_transactions: list = []
        self.trade_results: list = []

    def notify_order(self, order) -> None:
        """
        Method is kept for testing purposes.
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
    
    def print_trade_stats(self):
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

    def trade_logs(self):
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
        '''
        Raise NotImplementedError if subclass does not intiate an indicator.
        '''
        raise NotImplementedError("Must be implemented by the subclass")

    def buy_signal(self) -> bool:
        '''
        Raise NotImplementedError if subclass does not define a buy signal.
        '''
        raise NotImplementedError("Must be implemented by the subclass")

    def sell_signal(self) -> bool:
        '''
        Raise NotImplementedError if subclass does not define a sell signal.
        '''
        raise NotImplementedError("Must be implemented by the subclass")

    def next(self) -> None:
        '''
        If NotImplementedErros are not raised and there is no active position in the market.
        Then if a buy signal is recevied, execute a buy order.

        Otherwise, if a position is currently in the market and a sell signalk is received, close current position.
        '''
        if not self.position:
            if self.buy_signal():
                size_to_buy: int = math.floor(self.broker.getvalue() / self.data.close[0]) * 0.8
                self.buy(size=size_to_buy)
        elif self.sell_signal():
            self.sell(size=self.position.size)

class RSI_Strategy(StrategyBase):
    '''
    Strategy: RSI
    Indicators: Relative Strength Index (RSI)
    Buy Signal: When the RSI is below the oversold threshold.
    Sell Signal: When the RSI is above the overbought threshold.
    '''

    params: tuple[tuple[str, int]] = (
        ('rsi_period', 14),
        ('oversold', 30),
        ('overbought', 70)
    )

    def initialize_indicators(self) -> None:
        self.rsi = indicators.RSI(period=self.params.rsi_period)
        
    def buy_signal(self) -> bool:
        return (
            self.position.size == 0
            and self.rsi < self.params.oversold
        )

    def sell_signal(self) -> bool:
        return (
            self.position.size > 0
            and self.rsi > self.params.overbought
        )

class GoldenCross(StrategyBase):
    '''
    Stategy: Golden Crossover
    Indicators: 
        - x1 Fast Moving Average (50 Days)
        - x1 Slow Moving Average (200 Days)
    Buy Signal: When the fast moving average crosses the slow moving average to the upside.
    Sell Signal: When the slow moving average crosses the fast moving average to the downside.
    '''

    params: tuple[tuple[str, int]] = (
        ('fast', 50),
        ('slow', 200)
    )

    def initialize_indicators(self) -> None:
        self.slow_ma = indicators.EMA(self.datas[0].close, period=self.params.fast, plotname='50d MA')
        self.fast_ma = indicators.EMA(self.datas[0].close, period=self.params.slow, plotname='200d MA')
        self.goldencross = indicators.CrossOver(self.slow_ma, self.fast_ma)

    def buy_signal(self) -> bool:
        return (
            self.position.size == 0
            and self.goldencross == 1
            and self.data.close[0] > (self.slow_ma[0] and self.slow_ma[-1])
            )

    def sell_signal(self) -> bool:
        return (
            self.position.size > 0
            and self.goldencross == -1
            )

class Bollinger_Bands(StrategyBase):
    '''
    Strategy: Bollinger Bands
    Indicators: Bollinger Bands
    Buy Signal: When price closes below the bottom of the Bollinger Bands.
    Sell Signal: When price closes above the top of the Bollinger Bands.
    '''
    
    params: tuple[tuple[str, int]] = (
        ('period', 20),
        ('stddev', 2)
    )

    def initialize_indicators(self):
        self.bbands = indicators.BollingerBands(self.data, period=self.params.period, devfactor=self.params.stddev)

    def buy_signal(self) -> bool:
        return (
            self.position.size == 0
            and self.data.close[0] <= self.bbands.lines.bot[0]
            )

    def sell_signal(self) -> bool:
        return (
            self.position.size > 0
            and self.data.close[0] >= self.bbands.lines.top[0]
            )

class IchimokuCloud(StrategyBase):
    params: tuple[tuple[str, int]] = (
        ('tenkan', 9),
        ('kijun', 26),
        ('senkou', 52),
        ('shift', 26)
    )

    def initialize_indicators(self) -> None:
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
        return (
            self.position.size == 0
            and (self.tenkan_sen[0] > self.kijun_sen[0])
            and (self.data.close[0] > self.senkou_span_a[0])
            and (self.data.close[0] > self.senkou_span_b[0])
            )

    def sell_signal(self) -> bool:
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

from backtrader import Observer, observers, indicators

def patched_plot(self, plotter=None, numfigs=1, iplot=True, start=None, end=None,
                width=16, height=9, dpi=300, tight=True, use=None, **kwargs):
    """
    A monkey-patched version of the cerebro.plot() method that omits the `plotter.show()` call.
    This prevents a new window being opened for each plot, and instead embeds plots directly into
    a tkinter based window. 
    """
    if self._exactbars > 0:
        return

    if not plotter:
        from backtrader import plot  # Ensure you use the correct import path
        if self.p.oldsync:
            plotter = plot.Plot_OldSync(**kwargs)
        else:
            plotter = plot.Plot(**kwargs)

    figs = []
    for stratlist in self.runstrats:
        for si, strat in enumerate(stratlist):
            rfig = plotter.plot(strat, figid=si * 100,
                                numfigs=numfigs, iplot=iplot,
                                start=start, end=end, use=use)
            figs.append(rfig)

    return figs

def thousand_separator(value: int|float, decimals=2) -> str:
    """
    Adds thousands separators to numerical values, making them more readable. 

    Parameters
    ----------
    value : float or int
        The numerical value to which thousands separators should be applied.
    decimals : int, optional
        The number of decimal places to display in the result (default is 2).

    Returns
    -------
    str
        A string representation of the number with commas as thousand separators and 
        the specified number of decimal places.
    """
    num_formatted: str = '{:,.{}f}'.format(value, decimals)

    return num_formatted 

def convert_number(value: float) -> str:
    """
    Converts a large numerical value into a human-readable string format using common 
    abbreviations for large numbers (K for thousand, M for million, B for billion, 
    and T for trillion).

    Parameters
    ----------
    value : float
        The numerical value to be converted into a string.

    Returns
    -------
    str
        A formatted string representing the value in human-readable form:
        - Values >= 1 trillion are abbreviated with 'T'
        - Values >= 1 billion are abbreviated with 'B'
        - Values >= 1 million are abbreviated with 'M'
        - Values >= 1 thousand are abbreviated with 'K'
        - Smaller values are returned with two decimal places
    """
    match value:
        case value if value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"
        case value if value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        case value if value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        case value if value >= 1_000:
            return f"${value / 1_000:.2f}K"
        case _:
            return f"${value:.2f}"

class CustomEMA(indicators.EMA):
    plotlines: dict = dict(
        ema=dict(color='#FF9800', linewidth=1.0)
    )

    def __init__(self, color='#FF9800', **kwargs) -> None:
        super().__init__(**kwargs)
        self.plotlines.ema.color = color  
        self.plotinfo.subplot = False

class CustomBBands(indicators.BollingerBands):
    plotlines = dict(
        mid=dict(ls='-', color='#2962ff'),
        top=dict(color='#f23645'),
        bot=dict(color='#089981'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CustomRSI(indicators.RSI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    plotlines: dict = dict(
        rsi=dict(color='#7e57c2', linewidth=1.0)
    )

    plotinfo: dict = dict(
        plot=True,
        subplot=True,
        plotname='RSI',
        plotylimited=True,
        plotvaluetags=False
    )

class Transactions(observers.BuySell):
    """
    Customised version of Backtraders BuySell Observer.

    Modifications:
    - Renames 'buy' and 'sell' to 'Entry' and 'Exit' respectively.
    - Adjusts colors to be more muted, making them less bright and less intrusive.
    - Configures bar plot markers to appear above/below the high/low of candles.
    """

    params: tuple = (
        ('barplot', True),
        ('bardist', 0.015)
    )

    plotlines: dict = dict(
        buy=dict(
            marker='^',
            markersize=8.0,
            color='#4CAF50',
            fillstyle='full',
            ls='',
            label='Entry',
        ),
        sell=dict(
            marker='v',
            markersize=8.0,
            color='#F44336',
            fillstyle='full',
            ls='',
            label='Exit',
        )
    )

    plotinfo: dict = dict(
        plot=True, 
        subplot=False,
        plotlinelabels=True,
    )

class Portfolio(Observer):
    """
    Custom Observer displaying the value of the portfolio over the period of backtesting.
    Preferably contains dynamic colouring if:
        - Account Value > Capital: Green
        - Account Value < Capital: Red
        - Account Value = Capital: Transparent
    
    Cannot be achieved without using two separate lines but will cause overlap or disconnect if using float('nan') as a value.
    Backtrader does not currently support dynamic colouring in Observers.
    """
    alias = ('Portfolio Value',)
    lines = ('value', 'capital')

    plotinfo = dict(
        plot=True,
        subplot=True,
        plotlinelabels=True,
        plotvaluetags=False
    )

    plotlines = dict(
        value=dict(
            color='#2196F3',
            fillstyle='full',
            label='Portfolio',
            ls='-'
        ),
        capital=dict(
            color='#FF9800',
            fillstyle='full',
            label='Capital',
            ls='--'
        )
    )

    def __init__(self, capital: float):
        super().__init__()
        self.constant_capital = capital

    def next(self):
        account_value: float = self._owner.broker.getvalue()
        self.lines.value[0] = account_value
        self.lines.capital[0] = self.constant_capital
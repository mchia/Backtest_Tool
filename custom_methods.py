from backtrader import Observer, observers

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

class Transactions(observers.BuySell):
    """
    Customised version of Backtraders BuySell Observer.

    Modifications:
    - Renames 'buy' and 'sell' to 'Entry' and 'Exit' respectively.
    - Adjusts colors to be more muted, making them less bright and less intrusive.
    - Configures bar plot markers to appear above/below the high/low of candles.

    Inherits from
    -------------
    observers.BuySell
        The base observer class for BuySell transactions in Backtrader.
    """
    
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
    
    params: tuple = (
        ('barplot', True),
        ('bardist', 0.02)
    )

    plotinfo: dict = dict(
        plot=True, 
        subplot=False,
        plotlinelabels=True,
    )
    
class Portfolio(Observer):
    """
    This observer keeps track of the current cash amount and portfolio value in
    the broker (including the cash)

    Params: None
    """

    _stclock = True

    params = (
        ('fund', None),
    )

    alias: tuple[str] = ('Account Value')
    lines: tuple[str, str] = ('cash', 'value')

    plotinfo: dict = dict(
        plot=True,
        subplot=True,
        plotlinelabels=True
        )

    plotlines: dict = dict(
        value=dict(
            color='#607D8B',
            label='Account Value'
            ),
        cash=dict(
            color='red',
            label='Cash'
            ),
        )
    
    def start(self):
        if self.p.fund is None:
            self._fundmode = self._owner.broker.fundmode
        else:
            self._fundmode = self.p.fund

        if self._fundmode:
            self.plotlines.cash._plotskip = True
            self.plotlines.value._name = 'FundValue'

    def next(self):
        if not self._fundmode:
            self.lines.value[0] = value = self._owner.broker.getvalue()
            self.lines.cash[0] = self._owner.broker.getcash()
        else:
            self.lines.value[0] = self._owner.broker.fundvalue
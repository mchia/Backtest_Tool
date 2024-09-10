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

class AccountValue(Observer):
    """
    Custom Observer to display account value over time on a subplot.

    Attributes
    ----------
    alias : tuple
        A tuple containing the display name for the observer. Here it is set to 'Account Value'.
    lines : tuple
        A tuple defining the lines to be plotted. In this case, it includes a single line for account value.
    plotinfo : dict
        A dictionary specifying plot-related settings:
        - 'plot': Whether to plot the observer (True).
        - 'subplot': Whether the observer should be plotted in a subplot (True).
        - 'plotlinelabels': Whether to display labels for the plot lines (True).
    plotlines : dict
        A dictionary defining the appearance of the plot lines:
        - 'value': Specifies the color ('#607D8B') and label ('Account Value') for the account value line.

    Methods
    -------
    next()
        Updates the account value line with the current broker value.
    """
    alias = ('Account Value',)
    lines = ('value',)

    plotinfo: dict = dict(
        plot=True,
        subplot=True,
        plotlinelabels=True
        )

    plotlines: dict = dict(
        value=dict(
            color='#607D8B',
            label='Account Value'
            )
        )

    def next(self):
        self.lines.value[0] = self._owner.broker.getvalue()
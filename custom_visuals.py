from backtrader import Observer, observers

def patched_plot(self, plotter=None, numfigs=1, iplot=True, start=None, end=None,
                width=16, height=9, dpi=300, tight=True, use=None, **kwargs):
    '''
    This function is the exact same as cerebro.plot() with the exception of plotter.show() being removed.
    plotter.show() will always open a new window for any plot - this is by default in matplotlib.
    A separate window is not required as the plot is to be embedded directly into the current tkinter window from main.py
    '''
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
    '''
    Modifications to Backtrader's BuySell Observer:
        - Renames 'buy' and 'sell' to 'Entry' and 'Exit' respectively.
        - Colours: More muted, less bright and less intrusive.
        - Barplot: Set to True, making markers appear above/below the high/low of candles.
    '''
    
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
    '''
    Custom Observer to display account value over time.
    '''

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
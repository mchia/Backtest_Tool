import matplotlib
import pandas as pd
import backtrader as bt
import ttkbootstrap as tb
import custom_methods as cv
import matplotlib.pyplot as plt
from unittest.mock import patch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

matplotlib.use("TkAgg")

# Apply patch to bt.Cerebro.plot and overwrite it with cv.patched_plot to prevent show() from being called.
patch.object(target=bt.Cerebro, attribute='plot', new=cv.patched_plot).start()

class BacktraderEngine:
    """
    Class to control the execution of backtests through Backtraders Cerebro engine.

    Attributes
    ----------
    datafeed : pd.DataFrame
        A Pandas DataFrame containing the historical stock data to be used for backtesting.
    ticker : str
        The stock ticker symbol (e.g., 'TSLA' for Tesla, 'AAPL' for Apple).
    strategy : str
        The trading strategy to be applied in the backtest (e.g., MACD, RSI, Golden Crossover).
    interval : str
        The time interval for the data (e.g., 'Daily', 'Weekly').
    cerebro : bt.Cerebro
        An instance of the Backtrader cerebro engine, configured with the given parameters.

    Methods
    -------
    execute() -> bt.Cerebro
        Configures the cerebro engine with the provided datafeed and strategy, runs the backtest,
        and returns the cerebro instance.
    """
    def __init__(self, capital: int, datafeed: bt.feeds.PandasData, ticker: str, strategy: str, interval: str, commission: float, disp_pane: tb.Frame, params: dict|None, trade_type: int) -> None:
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
        trade_type : int
            The numerical representation of the trade type where:
                0 = Bearish -> Short Sell
                1 = Bullish -> Long

        Returns
        -------
        None
        """
        self.datafeed: pd.DataFrame = datafeed
        self.ticker: str = ticker
        self.strategy: str = strategy
        self.interval: str = interval
        self.display_pane = disp_pane
        self.params: dict|None = params
        self.capital: int = capital
        self.trade_style: int = trade_type
        self.cerebro: bt.Cerebro = bt.Cerebro(stdstats=False)
        self.cerebro.broker.set_cash(capital)
        self.cerebro.broker.setcommission(commission, leverage=2)
        
        # Add default observers manually
        self.cerebro.addobserver(cv.Portfolio, capital=self.capital)
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
        self.cerebro.addstrategy(
            strategy=self.strategy,
            capital=self.capital,
            ticker=self.ticker,
            interval=self.interval,
            disp_pane=self.display_pane,
            params=self.params,
            trade_style=self.trade_style
            )
        self.cerebro.run()
        return self.cerebro

class BackPlotter:
    """
    Class to control the visualization of trades executed by BacktraderEngine.

    Attributes
    ----------
    cerebro : bt.Cerebro
        An instance of the Backtrader cerebro engine that has already completed backtesting.
    
    Methods
    -------
    plot_settings() -> None
        Adjusts the visual appearance of the plot, setting the color for axes, labels, and ticks.
    
    bt_plot() -> plt.Figure
        Generates and returns a matplotlib figure object that visualizes the backtest results.

    display_plot() -> None
        Controls how the plot is embeded into a tkinter based canvas.
    """
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
        Utilises a patched version of cerebros plot method, which prevents the plot from automatically opening in a new window.

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
            voldown='#f23645',
            plotvaluetags=False,
            plotlinelabels=False,
            plotname=''
        )

        return fig[0][0]
    
    def display_plot(self, fig: plt.Figure, canvas: tb.Canvas) -> None:
        """
        Displays the given matplotlib figure in the GUI's canvas widget, replacing any 
        previous content, and embeds the associated navigation toolbar for interactive 
        control.

        The method does the following:
            1. Clears any previous widgets inside the canvas.
            2. Embeds the new matplotlib figure into the canvas.
            3. Adds a navigation toolbar to allow for zooming, panning, and saving the plot.
            4. Adjusts the layout to ensure proper sizing and placement.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The matplotlib figure object that contains the plot to be displayed in the GUI's canvas widget.
        
        canvas : tb.Canvas
            An instance of ttkbootstraps canvas, to embed the plot in.

        Returns
        -------
        None
            This method does not return any values. It updates the canvas widget with the new 
            plot and configures the associated toolbar for interaction.
        """
        for widget in canvas.winfo_children():
            widget.destroy()

        plt.close('all')
        fig.subplots_adjust(right=0.93, left=0.01)
        plot_canvas = FigureCanvasTkAgg(figure=fig, master=canvas)
        plot_canvas.draw()
        plot_canvas.get_tk_widget().pack(fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas=plot_canvas, window=canvas, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(anchor='w', padx=10)

        canvas.update_idletasks()
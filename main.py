import datetime
import pandas as pd
import backtrader as bt
import ttkbootstrap as tb
import trading_strategies as sb
from tkinter import filedialog
from data_sourcer import DataSourcer
from ttkbootstrap.dialogs import Messagebox
from strategy_params import strategy_params as strat
from backtrade_engine import BacktraderEngine, BackPlotter

intervals: dict = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo"
    }

class MainWindow:
    """
    MainWindow class for the Stock Backtesting Tool.

    This class sets up the main graphical user interface (GUI) for the backtesting tool,
    which includes three main panels:
        1. Selection Panel - For user inputs such as stock ticker, interval, balance, date range, and strategy selection.
        2. Plot Panel - For displaying the backtest results as a plot.
        3. Results Panel - For showing information about the ticker, performance metrics, and options to export trade and stock data.
    """
    def __init__(self) -> None:
        """
        Initializes the GUI for the Stock Backtesting Tool.

        This method sets up the main window, layout, and the three primary panels:
            - The Selection Panel for user inputs.
            - The Plot Panel for displaying backtest results.
            - The Results Panel for showing performance metrics and providing export options.

        Returns
        -------
        None
            This method does not return any values.
        """
        self.root: tb.Window = tb.Window(themename='superhero')
        self.screen_width: int = self.root.winfo_screenwidth()
        self.screen_height: int = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (self.screen_width, self.screen_height))
        self.root.title("Stock Backtesting Tool")
        self.panedwindow: tb.PanedWindow = tb.PanedWindow(self.root, orient='horizontal')
        self.panedwindow.pack(fill='both', expand=True)
        self.param_widgets: list = []

        self.selection_panel()
        self.display_params()
        self.plot_panel()
        self.results_panel()

    def selection_panel(self) -> None:
        """
        Sets up the Selection Panel of the GUI.

        This panel includes widgets for user inputs such as:
            - Ticker entry
            - Interval selection
            - Initial balance input
            - Commission input
            - Date range selection
            - Strategy selection
            - Execute Backtest button

        Returns
        -------
        None
        """
        self.selection_pane = tb.Frame(self.panedwindow, padding=10)
        self.panedwindow.add(child=self.selection_pane)

        # Title Label
        self.title: tb.Label = tb.Label(master=self.selection_pane, text='Backtester', font=('Segoe UI', 22, 'bold'), anchor='w')
        self.title.pack(anchor='w', pady=10)

        # Themer
        self.title: tb.Label = tb.Label(master=self.selection_pane, text='Theme', font=('Segoe UI', 16, 'bold'), anchor='w')
        self.title.pack(anchor='w')

        self.themer: tb.Combobox = tb.Combobox(master=self.selection_pane, values=list(tb.Style().theme_names()), width=19)
        self.themer.pack(anchor='w', pady=5)
        self.themer.set('superhero')
        self.themer.bind("<<ComboboxSelected>>", self.change_theme)

        # Ticker
        self.ticker_label: tb.Label = tb.Label(master=self.selection_pane, text='Ticker', font=('Segoe UI', 16 , 'bold'), anchor='w')
        self.ticker_label.pack(anchor='w', pady=(20,0))
        
        self.ticker_entry: tb.Entry = tb.Entry(master=self.selection_pane, width=20)
        self.ticker_entry.pack(anchor='w', pady=5)
        self.ticker_entry.insert(0, 'TSLA')

        # Interval
        self.interval_label: tb.Label = tb.Label(master=self.selection_pane, text='Interval', font=('Segoe UI', 16 , 'bold'), anchor='w')
        self.interval_label.pack(anchor='w', pady=(15, 0))

        self.interval: tb.Combobox = tb.Combobox(master=self.selection_pane, values=list(intervals.keys()), width=19)
        self.interval.pack(anchor='w', pady=5)
        self.interval.insert(0, 'Daily')

        # Capital
        self.initial_balance: tb.Label = tb.Label(master=self.selection_pane, text='Starting Balance', font=('Segoe UI', 16 , 'bold'), anchor='w')
        self.initial_balance.pack(anchor='w', pady=(15, 0))

        self.balance_entry: tb.Entry = tb.Entry(master=self.selection_pane, width=20)
        self.balance_entry.pack(anchor='w', pady=5)
        self.balance_entry.insert(0, '100000')

        # Commission
        self.commission_label: tb.Label = tb.Label(master=self.selection_pane, text='Commission', font=('Segoe UI', 16 , 'bold'), anchor='w')
        self.commission_label.pack(anchor='w', pady=(15, 0))

        self.commission_entry: tb.Entry = tb.Entry(master=self.selection_pane, width=20)
        self.commission_entry.pack(anchor='w', pady=5)
        self.commission_entry.insert(0, '0.001')

        # Date Selection
        self.date_label: tb.Label = tb.Label(master=self.selection_pane, text='Date Range', font=('Segoe UI', 16 , 'bold'), anchor='w')
        self.date_label.pack(anchor='w', pady=(15, 0))

        start_from = datetime.date.today().replace(year=datetime.date.today().year - 4)
        self.date_from: tb.DateEntry = tb.DateEntry(master=self.selection_pane, bootstyle='secondary', dateformat='%Y-%m-%d', width=17, startdate=start_from)
        self.date_from.pack(anchor='w', pady=5)

        self.date_to: tb.DateEntry = tb.DateEntry(master=self.selection_pane, bootstyle='secondary', dateformat='%Y-%m-%d', width=17)
        self.date_to.pack(anchor='w', pady=5)

        # Strategy Selection
        self.strategies: tb.Label = tb.Label(master=self.selection_pane, text='Strategy', font=('Segoe UI', 16 , 'bold'), anchor='w')
        self.strategies.pack(anchor='w', pady=(15, 0))

        self.base_strategies: tb.Combobox = tb.Combobox(master=self.selection_pane, values=list(sb.strategies_dict.keys()), width=19)
        self.base_strategies.pack(anchor='w', pady=5)
        self.base_strategies.insert(0, 'RSI Strategy')
        self.base_strategies.bind("<<ComboboxSelected>>", self.display_params)

        self.data_sourcing: tb.Button = tb.Button(master=self.selection_pane, text='Execute Backtest', command=self.execute_backtest)
        self.data_sourcing.pack(anchor='w', pady=20)

    def plot_panel(self) -> None:
        """
        Sets up the Plot Panel of the GUI.

        This panel includes:
            - A canvas widget for displaying the backtest results plot.

        Returns
        -------
        None
        """
        self.graph_pane = tb.Frame(self.panedwindow)
        self.panedwindow.add(self.graph_pane, weight=4)

        # Canvas to hold graph displaying trades.
        self.canvas: tb.Canvas = tb.Canvas(master=self.graph_pane)
        self.canvas.pack(fill='both', expand=True)

    def results_panel(self) -> None:
        """
        Sets up the Results Panel of the GUI.

        This panel includes widgets for displaying results and exporting data:
            - Information label for ticker-related details.
            - Performance label for backtest results.
            - Buttons for exporting historical stock data and trade data.

        Returns
        -------
        None
        """
        self.details_pane: tb.Frame = tb.Frame(self.panedwindow, padding=10)
        self.panedwindow.add(self.details_pane, weight=1)

        # Text box to display information related to ticker and trades.
        self.info_text: str | None = None
        self.information: tb.Label = tb.Label(master=self.details_pane, text=self.info_text, font=('Segoe UI', 16))
        self.information.pack(anchor='w', padx=10, pady=10)

        self.backtest_results: str | None = None
        self.performance: tb.Label = tb.Label(master=self.details_pane, text=self.backtest_results, font=('Segoe UI', 16))
        self.performance.pack(anchor='w', padx=10, pady=10)

        self.historical_data: pd.DataFrame | None = None
        self.export_hist: tb.Button = tb.Button(
            master=self.details_pane, 
            text='Export Stock Data', 
            command=lambda: self.export_csv(data=self.historical_data)
        )
        self.export_hist.pack(anchor='w', padx=10, pady=10)
        
        self.trade_logs: pd.DataFrame | None = None
        self.export_trades: tb.Button = tb.Button(
            master=self.details_pane, 
            text='Export Trade Data', 
            command=lambda: self.export_csv(data=self.trade_logs)
        )
        self.export_trades.pack(anchor='w', padx=10, pady=10)

    def display_params(self, event=None) -> None:
        """
        Creates labels and entry boxes based on the selected trading strategy,
        allowing users to customize the parameters of a strategy.

        Parameters
        ----------
        event : None
            The event that triggers this method, typically when a new strategy is selected 
            from a dropdown box. The event is passed automatically when binding strategy changes.

        Returns
        -------
        None
        """
        for widget in self.param_widgets:
            widget.destroy()
        self.param_widgets.clear()

        # Get selected strategy and parameters
        selected_strategy: str = self.base_strategies.get()
        strategy_class: bt.Strategy = sb.strategies_dict.get(selected_strategy)
        strategy_class_name: str = strategy_class.__name__
        params = strat.get(strategy_class_name, {})

        for key, value in params.items():
            frame = tb.Frame(master=self.selection_pane)
            frame.pack(anchor='w', pady=(5, 0))

            # Create and pack the label
            param_key = tb.Label(master=frame, text=key, font=('Segoe UI', 12), width=15, anchor='w')
            param_key.pack(side='left')

            # Create and pack the entry box
            param_entry = tb.Entry(master=frame, width=4)
            param_entry.pack(side='left')
            param_entry.insert(0, value)
            param_entry.configure(justify='center')

            # Store references to widgets for future use
            self.param_widgets.append(frame)

    def change_theme(self, event) -> None:
        """
        Updates the theme of the GUI whenever a new theme is selected from the dropdown 
        in a ttkbootstrap-based application.

        This method retrieves the selected theme using ttkbootstrap, applies it to the 
        entire GUI, and updates the background colors of specific widgets (e.g., canvas 
        and root window) to match the new theme's style.

    Parameters
    ----------
    event : ttkbootstrap.Event
        The event that triggers this method, typically when a new theme is selected 
        from a dropdown box. The event is passed automatically when binding theme changes.

    Returns
    -------
    None
        This method does not return any values but updates the theme and the background 
        colors of the widgets in the ttkbootstrap-based application.
    """
        selected_theme: str = self.themer.get()
        style: tb.Style = tb.Style(theme=selected_theme)

        theme_bg: str = style.colors.get('bg')

        # Update the colors of your widgets
        self.canvas.config(bg=theme_bg)
        self.root.config(bg=theme_bg)

        style.theme_use(selected_theme)

    def execute_backtest(self) -> None:
        """
        Executes a backtest based on user-provided inputs from the GUI fields. 

        The process involves:
            a) Retrieving the necessary values from the user entry fields (with dictionary lookups where applicable).
            b) Initializing the `DataSourcer` with retrieved values and calling the `retrieve_data()` method to get historical stock data as a pandas DataFrame.
            c) Initializing an instance of the `BacktraderEngine`, passing in the balance, stock data, strategy, and other parameters. This returns an instance of the Cerebro engine.
            d) Passing the Cerebro instance to `BackPlotter` for plotting the results and displaying the graph in the GUI.

        If any required fields are missing or invalid, an error message will be shown to the user. The method also handles potential exceptions during input retrieval and processing.

        Parameters
        ----------
        None
            This method does not accept any parameters, but it retrieves values from the Tkinter widgets (entry boxes, comboboxes, etc.) tied to the form fields.

        Raises
        ------
        ValueError
            Raised if the starting balance cannot be converted to an integer.
            In such cases, the method will log the error message and prevent the backtest from proceeding.

        Returns
        -------
        None
            This method does not return a value. However, it updates the following:
            - A plot is generated and displayed within the GUI via `self.display_plot()`.
            - The `self.info_text` attribute is updated with information about the selected ticker.
            - The `self.information` label is updated with the ticker information.
            - If there are missing fields, an error message will be shown to the user.
        """
        try:
            fields: dict = {
                'Ticker': self.ticker_entry.get().upper(),
                'Starting Balance': self.balance_entry.get(),
                'Start Date': self.date_from.entry.get(),
                'End Date': self.date_to.entry.get(),
                'Interval': self.interval.get(),
                'Strategy': self.base_strategies.get(),
                'Commission': self.commission_entry.get()
            }

            selected_interval: str|None = intervals.get(fields['Interval'])
            selected_strategy: str|None  = sb.strategies_dict.get(fields['Strategy'])
            balance: str|None = fields['Starting Balance']
            selected_balance: int|None = int(balance) if balance else None
            
            missing_fields: list = [name for name, value in fields.items() if not value]
            if missing_fields:
                Messagebox.show_error(
                    message=(f"Please fill out the following fields:\n{'\n'.join(missing_fields)}")
                )

        except ValueError as e:
            print(e)
        
        else:
            # Intialise DataSourcer and pass relevant parameters.
            source_data: pd.DataFrame = DataSourcer(
                ticker=fields['Ticker'],
                start_date=fields['Start Date'],
                end_date=fields['End Date'],
                interval=selected_interval
            )

            # Call retrieve_data() method to return:
                # datafeed: bt.feeds.PandasData
                # data: pd.DataFrame
            datafeed, data = source_data.retrieve_data()
            self.historical_data = data

            # Initialise BacktraderEngine -> Call execute() method -> Returns instance of Cerebro.
            backtrader: bt.Cerebro = BacktraderEngine(
                capital=selected_balance,
                datafeed=datafeed,
                ticker=fields['Ticker'],
                strategy=selected_strategy,
                interval=fields['Interval'],
                commission=float(fields['Commission']),
            ).execute()

            backtest_output: list = backtrader.runstrats[0][0]
            self.trade_logs: pd.DataFrame = backtest_output.trade_logs()
            self.backtest_results: str = backtest_output.print_trade_stats()
            self.performance.config(text=self.backtest_results)

            # Initalise BackPlotter
            plotter = BackPlotter(
                bt_instance=backtrader
            )
            fig = plotter.bt_plot()
            plotter.display_plot(fig=fig, canvas=self.canvas)

            self.info_text: str = source_data.ticker_profile()
            self.information.config(text=self.info_text)

    def export_csv(self, data: pd.DataFrame) -> None:
        """
        Exports the given DataFrame to a CSV file.
        """

        if any(df is not None and not df.empty for df in [self.trade_logs, self.historical_data]):
            file_path: str = filedialog.asksaveasfilename(defaultextension='.csv')
            if file_path:
                data.to_csv(path_or_buf=file_path, header=True, index=False)
        else:
            Messagebox.show_error("No data available to export.")


window = MainWindow()
window.root.mainloop()
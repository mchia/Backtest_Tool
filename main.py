import datetime
import pandas as pd
import backtrader as bt
import ttkbootstrap as tb
import customtkinter as ctk
from tkinter import filedialog
import trading_strategies as sb
from ttkbootstrap.dialogs import Messagebox
from data_sourcer import DataSourcer, intervals
from strategy_params import strategy_params as strat
from backtrade_engine import BacktraderEngine, BackPlotter

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
        """
        self.root: tb.Window = tb.Window(themename='superhero')
        self.screen_width: int = self.root.winfo_screenwidth()
        self.screen_height: int = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (self.screen_width, self.screen_height))
        self.root.title("Stock Backtesting Tool")
        self.root.iconphoto(True, tb.PhotoImage(file='backtrader_icon.png')) 
        self.panedwindow: tb.PanedWindow = tb.PanedWindow(self.root, orient='horizontal')
        self.panedwindow.pack(fill='both', expand=True)
        self.param_widgets: list = []
        self.temp_params: dict = {}
        self.trade_results: list = []
        self.ticker_profile: list = []
        self.widget_references: dict = {}

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
        header_font: tuple[str, int, str] = ('Segoe UI', 22, 'bold')
        subheader_font: tuple[str, int, str] = ('Segoe UI', 14, 'bold')
        entry_font: tuple[str, int] = ('Segoe UI', 12)
        entry_width: int = 20
        global_width: int = 18
        date_width: int = 14

        self.selection_pane = tb.Frame(self.panedwindow, padding=10)
        self.panedwindow.add(child=self.selection_pane)

        # Title Label
        self.title: tb.Label = tb.Label(master=self.selection_pane, text='Backtester', font=header_font, anchor='w', bootstyle='primary')
        self.title.pack(anchor='w', pady=10)

        # Themer
        self.title: tb.Label = tb.Label(master=self.selection_pane, text='Theme', font=subheader_font, anchor='w')
        self.title.pack(anchor='w')

        self.themer: tb.Combobox = tb.Combobox(master=self.selection_pane, values=list(tb.Style().theme_names()), width=global_width, font=entry_font)
        self.themer.pack(anchor='w', pady=5)
        self.themer.set('superhero')
        self.themer.bind("<<ComboboxSelected>>", self.change_theme)

        # Ticker
        self.ticker_label: tb.Label = tb.Label(master=self.selection_pane, text='Ticker', font=subheader_font, anchor='w')
        self.ticker_label.pack(anchor='w', pady=(10,0))
        
        self.ticker_entry: tb.Entry = tb.Entry(master=self.selection_pane, width=entry_width, font=entry_font)
        self.ticker_entry.pack(anchor='w', pady=5)
        self.ticker_entry.insert(0, 'TSLA')

        # Interval
        self.interval_label: tb.Label = tb.Label(master=self.selection_pane, text='Interval', font=subheader_font, anchor='w')
        self.interval_label.pack(anchor='w', pady=(10, 0))

        self.interval: tb.Combobox = tb.Combobox(master=self.selection_pane, values=list(intervals.keys()), width=global_width, font=entry_font)
        self.interval.pack(anchor='w', pady=5)
        self.interval.insert(0, 'Daily')
        self.interval.bind(sequence="<<ComboboxSelected>>", func=self.set_date)

        # Capital
        self.initial_balance: tb.Label = tb.Label(master=self.selection_pane, text='Starting Balance', font=subheader_font, anchor='w')
        self.initial_balance.pack(anchor='w', pady=(10, 0))

        self.balance_entry: tb.Entry = tb.Entry(master=self.selection_pane, width=entry_width, font=entry_font)
        self.balance_entry.pack(anchor='w', pady=5)
        self.balance_entry.insert(0, '100000')

        # Commission
        self.commission_label: tb.Label = tb.Label(master=self.selection_pane, text='Commission', font=subheader_font, anchor='w')
        self.commission_label.pack(anchor='w', pady=(10, 0))

        self.commission_entry: tb.Entry = tb.Entry(master=self.selection_pane, width=entry_width, font=entry_font)
        self.commission_entry.pack(anchor='w', pady=5)
        self.commission_entry.insert(0, '0.001')

        # Date Selection
        self.date_label: tb.Label = tb.Label(master=self.selection_pane, text='Date Range', font=subheader_font, anchor='w')
        self.date_label.pack(anchor='w', pady=(10, 0))
        
        self.date_start_frame: tb.Frame = tb.Frame(master=self.selection_pane)
        self.date_start_frame.pack(anchor='w', fill='x')

        start_from = datetime.date.today().replace(year=datetime.date.today().year - 4)
        self.date_from: tb.DateEntry = tb.DateEntry(master=self.date_start_frame, bootstyle='secondary', dateformat='%Y-%m-%d', width=date_width, startdate=start_from)
        self.date_from.pack(anchor='w', pady=5)

        self.date_to: tb.DateEntry = tb.DateEntry(master=self.selection_pane, bootstyle='secondary', dateformat='%Y-%m-%d', width=date_width)
        self.date_to.pack(anchor='w', pady=5)

        # Strategy Selection
        self.strategy_frame = tb.Frame(master=self.selection_pane)
        self.strategy_frame.pack(anchor='w', pady=(10, 0))  # Pack the frame to the left

        # Strategy Label
        self.strategies: tb.Label = tb.Label(master=self.strategy_frame, text='Strategy', font=subheader_font, anchor='w')
        self.strategies.pack(side='left', padx=(0, 10))  # Pack the label to the left

        self.bull_bear_switch: ctk.CTkSwitch = ctk.CTkSwitch(
            master=self.strategy_frame,
            command=self.toggle_switch, 
            text='Long',
            fg_color="#dc3545",
            progress_color="#198754",
            bg_color='transparent',
            border_color='transparent'
        )
        self.bull_bear_switch.pack(side='left')
        self.bull_bear_switch.select()

        self.base_strategies: tb.Combobox = tb.Combobox(master=self.selection_pane, values=list(sb.strategies_dict.keys()), width=global_width, font=entry_font)
        self.base_strategies.pack(anchor='w', pady=5)
        self.base_strategies.insert(0, 'RSI Strategy')
        self.base_strategies.bind(sequence="<<ComboboxSelected>>", func=self.display_params)

    def toggle_switch(self) -> None:
        """
        Configures the labels text to show either 'Long' or 'Short' depending when switch is interacted with.
        Note: self.bull_bear_switch.get() will return 0 and 1 only.
        In this case, 
        0 = Short
        1 = Long
        """
        
        if self.bull_bear_switch.get():
            trade_style: str = 'Long'
            self.bull_bear_switch.configure(fg_color='#dc3545', progress_color='#198754', text=trade_style, bg='transparent', border_color='transparent')
        else:
            trade_style: str = 'Short'
            self.bull_bear_switch.configure(fg_color='#dc3545', progress_color='#198754', text=trade_style, bg='transparent', border_color='transparent')

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
        header_font: tuple[str, int, str] = ('Segoe UI', 14, 'bold')

        self.details_pane: tb.Frame = tb.Frame(self.panedwindow, padding=10)
        self.panedwindow.add(self.details_pane, weight=1)

        self.profile_frame: tb.Frame = tb.Frame(master=self.details_pane)
        self.profile_frame.pack(anchor='w', fill='x')
        profile_label: tb.Label = tb.Label(master=self.profile_frame, text='Ticker Profile', font=header_font, bootstyle="info")
        profile_label.pack(fill='x', padx=5, pady=5, anchor='w')

        self.trade_results_frame: tb.Frame = tb.Frame(self.details_pane)
        self.trade_results_frame.pack(anchor='w', fill='x',)
        results_label: tb.Label = tb.Label(master=self.trade_results_frame, text='Trade Statistics', font=header_font, bootstyle="info")
        results_label.pack(fill='x', padx=5, pady=5, anchor='w')

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

    def set_date(self, event) -> None:
        """
        Automatically adjusts dates based on selected interval, due to constraints with the Yahoo Finance API.
        1m only has 7 day's worth of data available.
        Anything < 1d only has 60 days worth of data available.
        """
        interval: str = self.interval.get()
        end_date: datetime.date = datetime.date.today()

        if interval == "1 Minute":
            start_date: datetime.date = end_date - datetime.timedelta(days=7)
        elif interval in ['2 Minutes', '5 Minutes', '15 Minutes', '30 Minutes', 'Hourly', '90 Minutes']:
            start_date: datetime.date = end_date - datetime.timedelta(days=59)
        else:
            start_date = datetime.date.today().replace(year=datetime.date.today().year - 4)

        self.date_from.pack_forget()

        self.date_from = tb.DateEntry(
            master=self.date_start_frame,
            bootstyle='secondary',
            dateformat='%Y-%m-%d',
            width=14,
            startdate=start_date
        )
        self.date_from.pack(anchor='w', pady=5)
        
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
        # Clear any previously created widgets
        for widget in self.param_widgets:
            widget.destroy()
        self.param_widgets.clear()

        # Clear the Execute Backtest button if it already exists
        if hasattr(self, 'data_sourcing'):
            self.data_sourcing.destroy()

        # Get selected strategy and parameters
        selected_strategy: str = self.base_strategies.get()
        strategy_class: bt.Strategy = sb.strategies_dict.get(selected_strategy)
        strategy_class_name: str = strategy_class.__name__
        params = strat.get(strategy_class_name, {})

        for key, value in params.items():
            frame = tb.Frame(master=self.selection_pane)
            frame.pack(anchor='w', pady=(5, 0))

            label_font = ('Segoe UI', 12)
            entry_width = 4

            # Create and pack the label
            param_key = tb.Label(master=frame, text=key, font=label_font, width=15, anchor='w')
            param_key.pack(side='left')

            # Create and pack the entry box
            param_entry = tb.Entry(master=frame, width=entry_width, font=label_font)
            param_entry.pack(side='left')
            param_entry.insert(0, value)
            param_entry.configure(justify='center')

            self.temp_params[key] = value
            param_entry.bind('<KeyRelease>', lambda e, k=key, entry=param_entry: self.update_temp_params(k, entry))

            # Store references to widgets for future use
            self.param_widgets.append(frame)

        self.data_sourcing = tb.Button(master=self.selection_pane, text='Execute Backtest', command=self.execute_backtest)
        self.data_sourcing.pack(anchor='w', pady=20)

    def update_temp_params(self, key, entry) -> None:
        """Updates the temporary parameter dictionary with new values from entry boxes."""
        if key in ['Stop-Loss %', 'Extension Target']:
            self.temp_params[key] = float(entry.get())
        else:
            self.temp_params[key] = int(entry.get())

    def display_summary(self, data: dict, summary_type: str) -> None:
        """
        Creates labels based on the information provided and adds headers to separate sections.
        Additionally, stores references to the labels and value labels for dynamic theme updates.

        Parameters
        ----------
        data : dict
            Dictionary containing information to display as key-value pairs.
        summary_type : str
            Indicates the type of summary to display. Expected values are 'trade' or 'profile'.

        Returns
        -------
        None
        """
        theme: str = self.themer.get()
        dark_themes: list[str] = ['darkly', 'superhero', 'cyborg', 'vapor']        

        if summary_type == 'trade':
            widget_list: list = self.trade_results
            frame: tb.Frame = self.trade_results_frame
            value_cols: list[str] = ['Portfolio Value', 'Unrealised PnL', 'Account Value', 'Realised PnL', 'Avg PnL (%)', 'Avg PnL ($)']
        elif summary_type == 'profile':
            widget_list: list = self.ticker_profile
            frame: tb.Frame = self.profile_frame
            value_cols: list = []

        # Clear previous widgets and references
        for widget in widget_list:
            widget.destroy()
        widget_list.clear()

        # Store the widgets for later theme updates
        self.widget_references[summary_type] = []

        # Create and display new rows for the summary inside the appropriate frame
        for key, value in data.items():
            label_font: tuple[str, int, str] = ('Segoe UI', 12, 'bold')
            value_font: tuple[str, int] = ('Segoe UI', 12)

            row_frame: tb.Frame = tb.Frame(master=frame)
            row_frame.pack(fill='x', padx=5, pady=2)

            # Create the label for each statistic
            label: tb.Label = tb.Label(master=row_frame, text=f"{key}:", font=label_font, bootstyle="primary")
            label.pack(side='left', padx=5)

            # Set the bootstyle based on the theme and whether it's a value column
            if summary_type == 'trade' and key in value_cols:
                if '▲' in value:
                    bootstyle: str = "success"
                elif '▼' in value:
                    bootstyle: str = "danger"
                else:
                    bootstyle: str = "dark" if theme not in dark_themes else "light"
                
            else:                   
                bootstyle: str = "dark" if theme not in dark_themes else "light"

            # Create the value label
            value_label = tb.Label(master=row_frame, text=value, font=value_font, bootstyle=bootstyle)
            value_label.pack(side='left', padx=10)

            # Store widget references for future theme updates
            self.widget_references[summary_type].append((label, value_label))

            # Keep track of the row_frame for clearing later
            widget_list.append(row_frame)

    def change_theme(self, event) -> None:
        """
        Updates the theme of the GUI whenever a new theme is selected and applies 
        the new styles to the relevant summary widgets dynamically.
        """
        selected_theme: str = self.themer.get()
        style: tb.Style = tb.Style(theme=selected_theme)

        theme_bg: str = style.colors.get('bg')

        # Update the canvas and root window
        self.canvas.config(bg=theme_bg)
        self.root.config(bg=theme_bg)
        self.bull_bear_switch.configure(
        bg_color=theme_bg,
        border_color=theme_bg,
        fg_color='#dc3545',
        progress_color='#198754'
    )

        style.theme_use(themename=selected_theme)

        # Update all widgets in the summary frames with the new theme
        self.update_summary_widgets()

    def update_summary_widgets(self) -> None:
        """
        Updates the theme-related styles of all labels and value labels
        in the summaries displayed.
        """
        theme: str = self.themer.get()
        dark_themes: list[str] = ['darkly', 'superhero', 'cyborg', 'vapor', 'solar']

        # Loop through stored widget references and update their styles
        for summary_type, widget_list in self.widget_references.items():
            for label, value_label in widget_list:
                label.config(bootstyle="primary")

                if summary_type == 'trade':
                    bootstyle = "success" if '▲' in value_label.cget('text') else "danger"
                else:
                    bootstyle = "dark" if theme not in dark_themes else "light"

                value_label.config(bootstyle=bootstyle)
                
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
                'Commission': self.commission_entry.get(),
                'Trade Style': self.bull_bear_switch.get()
            }

            selected_interval: str|None = intervals.get(fields['Interval'])
            selected_strategy: str|None  = sb.strategies_dict.get(fields['Strategy'])
            balance: str|None = fields['Starting Balance']
            selected_balance: int|None = int(balance) if balance else None
            
            # Intialise DataSourcer and pass relevant parameters.
            source_data: pd.DataFrame = DataSourcer(
                ticker=fields['Ticker'],
                start_date=fields['Start Date'],
                end_date=fields['End Date'],
                interval=selected_interval
            )

            company_info: dict = source_data.ticker_profile()
            self.display_summary(data=company_info, summary_type='profile')

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
                disp_pane=self.details_pane,
                params=self.temp_params,
                trade_type=int(fields['Trade Style'])
            ).execute()

            backtest_output: list = backtrader.runstrats[0][0]
            self.trade_logs: pd.DataFrame = backtest_output.trade_logs()
            trade_dict: dict = backtest_output.print_trade_stats()
            self.display_summary(data=trade_dict, summary_type='trade')

        except IndexError:
            Messagebox.show_error(
                message='No data/trades found.\nCheck the following:\nTicker\nDate Range\nAccount Balance\nTrade Parameters',
                title='Error: Unavailable'
            )
        
        else:
            plotter = BackPlotter(
                bt_instance=backtrader
            )
            fig = plotter.bt_plot()
            plotter.display_plot(fig=fig, canvas=self.canvas)
    
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

if __name__ == '__main__':
    window = MainWindow()
    window.root.mainloop()
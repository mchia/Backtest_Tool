import matplotlib
import backtrader as bt
import pandas as pd
import yfinance as yf
import trading_strategies as sb
import ttkbootstrap as tb
import datetime
import matplotlib.pyplot as plt
from ttkbootstrap.dialogs import Messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from data_sourcer import DataSourcer
from backtrade_engine import BacktraderEngine, BackPlotter

matplotlib.use("TkAgg")

intervals: dict = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo"
    }

class MainWindow:
    def __init__(self) -> None:
        """
        Initializes the GUI for the Backtesting Tool.

        This method sets up the main components of the GUI, including:
            - The main window and layout with ttkbootstrap's `Window` and `PanedWindow`.
            - Selection pane to allow the user to input a stock ticker, interval, balance, 
            date range, and strategy.
            - A graph pane that will later display the backtest results as a plot.
            - A details pane to show information about the ticker and provide options to 
            export trade logs.

        The following elements are initialized:
            - Root window with screen size and title.
            - A paned window layout to organize the different sections.
            - Various widgets for user input such as entry fields, comboboxes, and buttons.
            - A canvas to display the plot generated from the backtest.
            - A details pane to show additional information about the trades.

        Returns
        -------
        None
            This method does not return any values.
        """
        self.root: tb.Window = tb.Window(themename='flatly')
        self.screen_width: int = self.root.winfo_screenwidth()
        self.screen_height: int = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (self.screen_width, self.screen_height))
        self.root.title("Backtesting Tool")
        
        # Base Pane
        self.panedwindow: tb.PanedWindow = tb.PanedWindow(self.root, orient='horizontal')
        self.panedwindow.pack(fill='both', expand=True)

        # Pane 1: Selection Pane
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
        self.themer.set('flatly')
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

        self.data_sourcing: tb.Button = tb.Button(master=self.selection_pane, text='Execute Backtest', command=self.execute_backtest)
        self.data_sourcing.pack(anchor='w', pady=20)

        # Frame 2: Graph Pane
        self.graph_pane = tb.Frame(self.panedwindow)
        self.panedwindow.add(self.graph_pane, weight=4)

        # Canvas to hold graph displaying trades.
        self.canvas: tb.Canvas = tb.Canvas(master=self.graph_pane)
        self.canvas.pack(fill='both', expand=True)

        # Frame 3: Details Pane
        self.details_pane: tb.Frame = tb.Frame(self.panedwindow, padding=10)
        self.panedwindow.add(self.details_pane, weight=1)

        # Text box to display information related to ticker and trades.
        self.info_text: str | None = None
        self.information: tb.Label = tb.Label(master=self.details_pane, text=self.info_text, font=('Segoe UI', 16))
        self.information.pack(anchor='w', padx=10, pady=10)

        self.export_label: tb.Label = tb.Label(master=self.details_pane, text='Trade Log', font=('Segoe UI', 16))
        self.export_label.pack(anchor='w', padx=10, pady=10)
        self.export_csv: tb.Button = tb.Button(master=self.details_pane, text='Export CSV', command=self.execute_backtest)
        self.export_csv.pack(anchor='w', padx=10, pady=10)

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
                'Strategy': self.base_strategies.get()
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
            # Intialise DataSourcer -> Call retrieve_date() method -> Return historical data as a pandas dataframe.
            stock_data: pd.DataFrame = DataSourcer(
                ticker=fields['Ticker'],
                start_date=fields['Start Date'],
                end_date=fields['End Date'],
                interval=selected_interval
            ).retrieve_data()

            # Initialise BacktraderEngine -> Call execute() method -> Returns instance of Cerebro.
            backtrader: bt.Cerebro = BacktraderEngine(
                capital=selected_balance,
                datafeed=stock_data,
                ticker=fields['Ticker'],
                strategy=selected_strategy,
                interval=fields['Interval']
            ).execute()

            ins: list = backtrader.runstrats[0][0]
            ins.trade_logs()

            # Initalise BackPlotter -> Call bt_plot() -> Returns the plot as a figure.
            fig: plt.Figure = BackPlotter(
                bt_instance=backtrader
            ).bt_plot()

            self.display_plot(fig)
            self.info_text: str = self.get_ticker_info(ticker=fields['Ticker'])
            self.information.config(text=self.info_text)

    def display_plot(self, fig) -> None:
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
            The matplotlib figure object that contains the plot to be displayed 
            in the GUI's canvas widget.

        Returns
        -------
        None
            This method does not return any values. It updates the canvas widget with the new 
            plot and configures the associated toolbar for interaction.
        """
        for widget in self.canvas.winfo_children():
            widget.destroy()

        plt.close('all')
        fig.subplots_adjust(right=0.93, left=0.01)
        plot_canvas = FigureCanvasTkAgg(figure=fig, master=self.canvas)
        plot_canvas.draw()
        plot_canvas.get_tk_widget().pack(fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas=plot_canvas, window=self.canvas, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(anchor='w', padx=10)

        self.canvas.update_idletasks()

    def get_ticker_info(self, ticker: str) -> str:
        stock = yf.Ticker(ticker)
        stock_info: dict = stock.info

        company_info: dict = {
            "Company Name": stock_info.get("longName"),
            "Ticker": stock_info.get("symbol"),
            "Industry": stock_info.get("industry"),
            "Sector": stock_info.get("sector"),
            "Market Cap": stock_info.get("marketCap"),
            "Volume": stock_info.get("volume"),
            # "Financials": stock_info.financials if stock_info.financials is not None else "No financials available"
        }

        info_text: str = "\n".join(f"{key}: {value}" for key, value in company_info.items())
        
        return info_text

if __name__ == "__main__":
    window = MainWindow()
    window.root.mainloop()

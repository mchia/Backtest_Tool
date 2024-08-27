import pandas as pd
import tkinter as tk
import yfinance as yf
import datetime as dt
import backtrader as bt
import customtkinter as ctk

pre_built_strategies: set = {'RSI', 'BollingerBands', 'Golden Crossover'}

class main_window:
    def __init__(self) -> None:
        self.app: tk.Tk = tk.Tk()
        self.app.geometry("600x600")
        self.app.title("Backtesting Tool")

        # Entry box for Ticker to backtest.
        self.ticker: tk.Label = tk.Label(master=self.app, text="Ticker").grid(row=2)
        self.ticker_entry: tk.Entry = tk.Entry(self.ticker).grid(row=2, column=1)

        # Entry boxes for date range to backtest.
        self.start_date: tk.Label = tk.Label(master=self.app, text="Start Date").grid(row=3)
        self.start_date_entry: tk.Entry = tk.Entry(self.start_date).grid(row=3, column=1)

        self.end_date: tk.Label = tk.Label(master=self.app, text="End Date").grid(row=4)
        self.end_date_entry: tk.Entry = tk.Entry(self.end_date).grid(row=4, column=1)

    def parameters(self):
        pass

    def run(self):
        self.app.mainloop()

if __name__ == '__main__':
    main_window().run()
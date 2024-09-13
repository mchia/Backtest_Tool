strategy_params: dict = {
    'RSI_Strategy': {
        'Period': 14,
        'Oversold': 30,
        'Overbought': 70
    },
    'GoldenCross': {
        'Fast EMA': 50,
        'Slow EMA': 200
    },
    'BollingerBands': {
        'Period': 20,
        'Standard Dev': 2
    },
    'IchimokuCloud': {
        'Tenkan': 9,
        'Kijun': 26,
        'Senkou': 52,
        'Shift': 26
    },
    'MACD': {
        'Fast MA': 12,
        'Slow MA': 26,
        'Signal': 9
    },
    'GoldenRatio': {
        'Lookback': 20,
        'Extension Target': 1.618,
        'Stop-Loss %': 0.1
    }
}

Refactored code for GUI into methods for each panel.
Moved all strategy parameters into a separate py file.
Added a for loop to generate labels and entries for all parameters -> Dictionary updating to be
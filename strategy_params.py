strategy_params: dict = {
    'RSI_Strategy': {
        'Period': 14,
        'Oversold': 30,
        'Overbought': 70,
        'Stop-Loss %': 0.1
    },
    'GoldenCross': {
        'Fast EMA': 50,
        'Slow EMA': 200,
        'Stop-Loss %': 0.1
    },
    'BollingerBands': {
        'Period': 20,
        'Standard Dev': 2,
        'Stop-Loss %': 0.1
    },
    'IchimokuCloud': {
        'Tenkan': 9,
        'Kijun': 26,
        'Senkou': 52,
        'Shift': 26,
        'Stop-Loss %': 0.1
    },
    'MACD': {
        'Fast MA': 12,
        'Slow MA': 26,
        'Signal': 9,
        'Stop-Loss %': 0.1
    },
    'GoldenRatio': {
        'Lookback': 20,
        'Extension Target': 1.618,
        'Stop-Loss %': 0.1
    }
}
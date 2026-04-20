# -*- coding: utf-8 -*-


import json
import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================================
# Streamlit 基本設定
# =========================================================
st.set_page_config(
    page_title="金融看板與程式交易平台",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #fffbea;
    }
    section[data-testid="stSidebar"] {
        background-color: #fff7d6;
    }
    .main-title-box {
        background: #fff1b8;
        padding: 16px 20px;
        border-radius: 14px;
        border: 1px solid #f1dea0;
        margin-bottom: 12px;
    }
    .main-title-box h1 {
        color: #6b4f00;
        text-align: center;
        margin: 0;
        font-size: 2rem;
    }
    .main-title-box h3 {
        color: #8a6d1d;
        text-align: center;
        margin: 6px 0 0 0;
        font-weight: 500;
    }
    .summary-card {
        background: #fffdf2;
        border: 1px solid #f0e4b8;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .small-note {
        color: #7d6a2d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title-box">
    <h1>金融看板與程式交易平台</h1>
    <h3>Financial Dashboard and Program Trading</h3>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 商品資料
# =========================================================
choices = [
    '台積電 2330: 2020.01.02 至 2025.04.16',
    '大台指期貨2024.12到期: 2023.12 至 2024.4.11',
    '小台指期貨2024.12到期: 2023.12 至 2024.4.11',
    '英業達 2356: 2020.01.02 至 2024.04.12',
    '堤維西 1522: 2020.01.02 至 2024.04.12',
    '0050 台灣50ETF: 2020.01.02 至 2025.03.10',
    '00631L 台灣50正2: 2023.04.17 至 2025.04.17',
    '華碩 2357: 2023.04.17 至 2025.04.16',
    '金融期貨 CBF: 2023.04.17 至 2025.04.17',
    '電子期貨 CCF: 2023.04.17 至 2025.04.16',
    '小型電子期貨 CDF: 2020.03.02 至 2025.04.14',
    '非金電期貨 CEF: 2023.04.17 至 2025.04.16',
    '摩台期貨 CMF: 2023.04.17 至 2025.04.17',
    '小型金融期貨 CQF: 2023.04.17 至 2025.04.17',
    '美元指數期貨 FXF: 2020.03.02 至 2025.04.14'
]

product_info = {
    choices[0]: ('exported/kbars_1min_2330_2020-01-02_To_2025-04-16.pkl', '台積電 2330', '2020-01-02', '2025-04-16'),
    choices[1]: ('exported/kbars_TXF202412_2023-12-21-2024-04-11.pkl', '大台指期貨', '2023-12-21', '2024-04-11'),
    choices[2]: ('exported/kbars_MXF202412_2023-12-21-2024-04-11.pkl', '小台指期貨', '2023-12-21', '2024-04-11'),
    choices[3]: ('exported/kbars_2356_2020-01-01-2024-04-12.pkl', '英業達 2356', '2020-01-02', '2024-04-12'),
    choices[4]: ('exported/kbars_1522_2020-01-01-2024-04-12.pkl', '堤維西 1522', '2020-01-02', '2024-04-12'),
    choices[5]: ('exported/kbars_1min_0050_2020-01-02_To_2025-03-10.pkl', '台灣50ETF 0050', '2020-01-02', '2025-03-10'),
    choices[6]: ('exported/kbars_1min_00631L_2023-04-17_To_2025-04-17.pkl', '台灣50正2 00631L', '2023-04-17', '2025-04-17'),
    choices[7]: ('exported/kbars_1min_2357_2023-04-17_To_2025-04-16.pkl', '華碩 2357', '2023-04-17', '2025-04-16'),
    choices[8]: ('exported/kbars_1min_CBF_2023-04-17_To_2025-04-17.pkl', '金融期貨 CBF', '2023-04-17', '2025-04-17'),
    choices[9]: ('exported/kbars_1min_CCF_2023-04-17_To_2025-04-16.pkl', '電子期貨 CCF', '2023-04-17', '2025-04-16'),
    choices[10]: ('exported/kbars_1min_CDF_2020-03-02_To_2025-04-14.pkl', '小型電子期貨 CDF', '2020-03-02', '2025-04-14'),
    choices[11]: ('exported/kbars_1min_CEF_2023-04-17_To_2025-04-16.pkl', '非金電期貨 CEF', '2023-04-17', '2025-04-16'),
    choices[12]: ('exported/kbars_1min_CMF_2023-04-17_To_2025-04-17.pkl', '摩台期貨 CMF', '2023-04-17', '2025-04-17'),
    choices[13]: ('exported/kbars_1min_CQF_2023-04-17_To_2025-04-17.pkl', '小型金融期貨 CQF', '2023-04-17', '2025-04-17'),
    choices[14]: ('exported/kbars_1min_FXF_2020-03-02_To_2025-04-14.pkl', '美元指數期貨 FXF', '2020-03-02', '2025-04-14'),
}

contract_multipliers = {
    choices[0]: 1000,
    choices[1]: 200,
    choices[2]: 50,
    choices[3]: 1000,
    choices[4]: 1000,
    choices[5]: 1000,
    choices[6]: 1000,
    choices[7]: 1000,
    choices[8]: 1000,
    choices[9]: 1000,
    choices[10]: 200,
    choices[11]: 200,
    choices[12]: 30,
    choices[13]: 250,
    choices[14]: 1000
}

# =========================================================
# 基礎函式
# =========================================================
@st.cache_data(ttl=3600, show_spinner="正在讀取資料...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_pickle(path).copy()
    df["time"] = pd.to_datetime(df["time"])
    return df

def ensure_positive_int(value, default_value=1):
    try:
        value = int(value)
        return max(1, value)
    except Exception:
        return default_value

def clamp_series(series, lower=None, upper=None):
    s = series.copy()
    if lower is not None:
        s = s.clip(lower=lower)
    if upper is not None:
        s = s.clip(upper=upper)
    return s

def get_resample_rule(unit: str, value: int) -> str:
    value = max(1, int(value))
    if unit == "分鐘":
        return f"{value}min"
    elif unit == "小時":
        return f"{value}h"
    elif unit == "日":
        return f"{value}D"
    elif unit == "週":
        return f"{value}W"
    elif unit == "月":
        return f"{value}ME"
    return "1h"

@st.cache_data(ttl=3600, show_spinner="正在重整 K 棒...")
def resample_ohlcv(df: pd.DataFrame, rule: str, product_name: str) -> pd.DataFrame:
    x = df.copy().sort_values("time")
    x = x.set_index("time")

    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    }
    if "amount" in x.columns:
        agg["amount"] = "sum"

    out = x.resample(rule).agg(agg).dropna(subset=["open", "high", "low", "close"]).reset_index()
    out["product"] = product_name
    if "amount" not in out.columns:
        out["amount"] = 0
    return out

# =========================================================
# 技術指標
# =========================================================
def calc_ma(df, period=10):
    period = ensure_positive_int(period, 10)
    return df["close"].rolling(window=period, min_periods=period).mean()

def calc_ema(df, period=10):
    period = ensure_positive_int(period, 10)
    return df["close"].ewm(span=period, adjust=False).mean()

def calc_rsi(df, period=14):
    period = ensure_positive_int(period, 14)
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(period, min_periods=period).mean()
    loss = (-delta.clip(upper=0)).rolling(period, min_periods=period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return clamp_series(rsi, 0, 100)

def calc_bb(df, period=20, num_std_dev=2.0):
    period = ensure_positive_int(period, 20)
    sma = df["close"].rolling(window=period, min_periods=period).mean()
    std = df["close"].rolling(window=period, min_periods=period).std()
    upper = sma + std * num_std_dev
    lower = sma - std * num_std_dev
    return sma, upper, lower, std

def calc_macd(df, fast_period=12, slow_period=26, signal_period=9):
    fast_period = ensure_positive_int(fast_period, 12)
    slow_period = ensure_positive_int(slow_period, 26)
    signal_period = ensure_positive_int(signal_period, 9)
    ema_fast = df["close"].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    hist = macd - signal
    return ema_fast, ema_slow, macd, signal, hist

def calc_atr(df, period=14):
    period = ensure_positive_int(period, 14)
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=period).mean()
    return atr

def calc_obv(df):
    direction = np.sign(df["close"].diff()).fillna(0)
    obv = (direction * df["volume"]).fillna(0).cumsum()
    return obv

def calc_cci(df, period=20):
    period = ensure_positive_int(period, 20)
    tp = (df["high"] + df["low"] + df["close"]) / 3
    sma = tp.rolling(period, min_periods=period).mean()
    mad = tp.rolling(period, min_periods=period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    cci = (tp - sma) / (0.015 * mad.replace(0, np.nan))
    return cci

def calc_kd(df, k_period=14, d_period=3):
    k_period = ensure_positive_int(k_period, 14)
    d_period = ensure_positive_int(d_period, 3)
    low_min = df["low"].rolling(window=k_period, min_periods=k_period).min()
    high_max = df["high"].rolling(window=k_period, min_periods=k_period).max()
    denom = (high_max - low_min).replace(0, np.nan)
    rsv = 100 * (df["close"] - low_min) / denom
    k = rsv.ewm(alpha=1 / d_period, adjust=False).mean()
    d = k.ewm(alpha=1 / d_period, adjust=False).mean()
    return clamp_series(k, 0, 100), clamp_series(d, 0, 100)

def calc_willr(df, period=14):
    period = ensure_positive_int(period, 14)
    high_max = df["high"].rolling(window=period, min_periods=period).max()
    low_min = df["low"].rolling(window=period, min_periods=period).min()
    willr = -100 * (high_max - df["close"]) / (high_max - low_min).replace(0, np.nan)
    return clamp_series(willr, -100, 0)

def calc_mfi(df, period=14):
    period = ensure_positive_int(period, 14)
    tp = (df["high"] + df["low"] + df["close"]) / 3
    mf = tp * df["volume"]
    pos_mf = mf.where(tp > tp.shift(), 0.0)
    neg_mf = mf.where(tp < tp.shift(), 0.0)
    mfr = pos_mf.rolling(period, min_periods=period).sum() / neg_mf.rolling(period, min_periods=period).sum().replace(0, np.nan)
    mfi = 100 - (100 / (1 + mfr))
    return clamp_series(mfi, 0, 100)

def calc_roc(df, period=12):
    period = ensure_positive_int(period, 12)
    return ((df["close"] - df["close"].shift(period)) / df["close"].shift(period)) * 100

def calc_mom(df, period=10):
    period = ensure_positive_int(period, 10)
    return df["close"] - df["close"].shift(period)

def calc_trix(df, period=15):
    period = ensure_positive_int(period, 15)
    ema1 = df["close"].ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    return 100 * (ema3 - ema3.shift()) / ema3.shift()

def calc_psar(df, af_start=0.02, af_step=0.02, af_max=0.2):
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    if len(df) == 0:
        return pd.Series(dtype=float)

    psar = np.full(len(close), np.nan)
    trend = 1
    af = af_start
    ep = high[0]
    psar[0] = low[0]

    for i in range(1, len(close)):
        prev_psar = psar[i - 1]
        psar[i] = prev_psar + af * (ep - prev_psar)

        if trend == 1:
            psar[i] = min(psar[i], low[i - 1], low[i])
            if high[i] > ep:
                ep = high[i]
                af = min(af + af_step, af_max)
            if close[i] < psar[i]:
                trend = -1
                ep = low[i]
                af = af_start
                psar[i] = ep
        else:
            psar[i] = max(psar[i], high[i - 1], high[i])
            if low[i] < ep:
                ep = low[i]
                af = min(af + af_step, af_max)
            if close[i] > psar[i]:
                trend = 1
                ep = high[i]
                af = af_start
                psar[i] = ep

    return pd.Series(psar, index=df.index)

def calc_vwap(df):
    price_volume = ((df["high"] + df["low"] + df["close"]) / 3) * df["volume"]
    return price_volume.cumsum() / df["volume"].replace(0, np.nan).cumsum()

def calc_donchian(df, period=20):
    period = ensure_positive_int(period, 20)
    upper = df["high"].rolling(period, min_periods=period).max()
    lower = df["low"].rolling(period, min_periods=period).min()
    middle = (upper + lower) / 2
    return upper, middle, lower

def calc_adx(df, period=14):
    period = ensure_positive_int(period, 14)
    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period, min_periods=period).mean()
    plus_di = 100 * (plus_dm.rolling(period, min_periods=period).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.rolling(period, min_periods=period).mean() / atr.replace(0, np.nan))
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.rolling(period, min_periods=period).mean()
    return clamp_series(adx, 0, 100), plus_di, minus_di

def add_all_indicators(df, params):
    data = df.copy()

    data["MA_short"] = calc_ma(data, params["ma_short"])
    data["MA_long"] = calc_ma(data, params["ma_long"])
    data["EMA_short"] = calc_ema(data, params["ema_short"])
    data["EMA_long"] = calc_ema(data, params["ema_long"])

    data["RSI"] = calc_rsi(data, params["rsi_period"])
    data["RSI_50"] = 50

    sma, upper, lower, bb_std = calc_bb(data, params["bb_period"], params["bb_std"])
    data["BB_SMA"] = sma
    data["BB_UPPER"] = upper
    data["BB_LOWER"] = lower
    data["BB_STD"] = bb_std
    data["BB_WIDTH"] = (upper - lower) / sma.replace(0, np.nan)

    ema_fast, ema_slow, macd, signal, hist = calc_macd(data, params["macd_fast"], params["macd_slow"], params["macd_signal"])
    data["EMA_FAST"] = ema_fast
    data["EMA_SLOW"] = ema_slow
    data["MACD"] = macd
    data["MACD_SIGNAL"] = signal
    data["MACD_HIST"] = hist

    data["ATR"] = calc_atr(data, params["atr_period"])
    data["OBV"] = calc_obv(data)
    data["CCI"] = calc_cci(data, params["cci_period"])
    data["K"], data["D"] = calc_kd(data, params["k_period"], params["d_period"])
    data["WILLR"] = calc_willr(data, params["willr_period"])
    data["MFI"] = calc_mfi(data, params["mfi_period"])
    data["ROC"] = calc_roc(data, params["roc_period"])
    data["MOM"] = calc_mom(data, params["mom_period"])
    data["TRIX"] = calc_trix(data, params["trix_period"])
    data["PSAR"] = calc_psar(data)
    data["VWAP"] = calc_vwap(data)
    data["DON_UPPER"], data["DON_MID"], data["DON_LOWER"] = calc_donchian(data, params["donchian_period"])
    data["ADX"], data["PLUS_DI"], data["MINUS_DI"] = calc_adx(data, params["adx_period"])

    return data

# =========================================================
# 回測引擎
# =========================================================
def mark_to_market_equity(equity_curve, current_equity):
    equity_curve.append(current_equity)

def calculate_performance(trades, choice):
    if not trades:
        return pd.DataFrame({
            "項目": ["交易數", "總盈虧", "勝率", "平均每筆", "最大單筆虧損", "最大單筆獲利", "最大回落", "報酬風險比"],
            "數值": [0, 0, 0, 0, 0, 0, 0, 0]
        })

    multiplier = contract_multipliers.get(choice, 1)
    pnl_list = [t["pnl"] * multiplier for t in trades]
    total_profit = float(np.sum(pnl_list))
    win_rate = float(np.mean([p > 0 for p in pnl_list])) if pnl_list else 0
    avg_profit = float(np.mean(pnl_list)) if pnl_list else 0
    max_loss = float(np.min(pnl_list)) if pnl_list else 0
    max_win = float(np.max(pnl_list)) if pnl_list else 0

    eq = np.cumsum(pnl_list)
    running_max = np.maximum.accumulate(eq)
    drawdown = running_max - eq
    mdd = float(np.max(drawdown)) if len(drawdown) > 0 else 0
    rr = total_profit / mdd if mdd != 0 else np.nan

    return pd.DataFrame({
        "項目": ["交易數", "總盈虧", "勝率", "平均每筆", "最大單筆虧損", "最大單筆獲利", "最大回落", "報酬風險比"],
        "數值": [
            len(trades),
            round(total_profit, 2),
            round(win_rate, 4),
            round(avg_profit, 2),
            round(max_loss, 2),
            round(max_win, 2),
            round(mdd, 2),
            round(rr, 4) if pd.notna(rr) else np.nan
        ]
    })

def close_trade(position, exit_time, exit_price, reason):
    pnl = 0.0
    if position["side"] == "long":
        pnl = (exit_price - position["entry_price"]) * position["qty"]
    else:
        pnl = (position["entry_price"] - exit_price) * position["qty"]

    return {
        "side": position["side"],
        "entry_time": position["entry_time"],
        "entry_price": position["entry_price"],
        "exit_time": exit_time,
        "exit_price": exit_price,
        "qty": position["qty"],
        "pnl": pnl,
        "reason": reason
    }

def backtest_strategy(df, strategy_name, params):
    data = df.copy().reset_index(drop=True)
    trades = []
    signals = []
    position = None
    stop_price = None

    qty = int(params["qty"])
    stop_loss = float(params["stop_loss"])

    def buy_signal(i):
        if strategy_name == "移動平均線策略":
            return (
                pd.notna(data.loc[i-1, "MA_short"]) and
                pd.notna(data.loc[i-1, "MA_long"]) and
                data.loc[i-1, "MA_short"] <= data.loc[i-1, "MA_long"] and
                data.loc[i, "MA_short"] > data.loc[i, "MA_long"]
            )
        elif strategy_name == "RSI逆勢策略":
            return pd.notna(data.loc[i, "RSI"]) and data.loc[i, "RSI"] < params["oversold"]
        elif strategy_name == "布林通道策略":
            return pd.notna(data.loc[i, "BB_LOWER"]) and data.loc[i, "close"] < data.loc[i, "BB_LOWER"]
        elif strategy_name == "MACD策略":
            return (
                pd.notna(data.loc[i-1, "MACD"]) and pd.notna(data.loc[i-1, "MACD_SIGNAL"]) and
                data.loc[i-1, "MACD"] <= data.loc[i-1, "MACD_SIGNAL"] and
                data.loc[i, "MACD"] > data.loc[i, "MACD_SIGNAL"]
            )
        elif strategy_name == "KD策略":
            return (
                pd.notna(data.loc[i-1, "K"]) and pd.notna(data.loc[i-1, "D"]) and
                data.loc[i-1, "K"] <= data.loc[i-1, "D"] and
                data.loc[i, "K"] > data.loc[i, "D"] and
                data.loc[i, "K"] < params["oversold"]
            )
        elif strategy_name == "網格交易策略":
            return False
        elif strategy_name == "多策略組合":
            score = 0
            if pd.notna(data.loc[i, "MA_short"]) and pd.notna(data.loc[i, "MA_long"]) and data.loc[i, "MA_short"] > data.loc[i, "MA_long"]:
                score += params["w_ma"]
            if pd.notna(data.loc[i, "RSI"]) and data.loc[i, "RSI"] < params["oversold"]:
                score += params["w_rsi"]
            if pd.notna(data.loc[i, "BB_LOWER"]) and data.loc[i, "close"] < data.loc[i, "BB_LOWER"]:
                score += params["w_bb"]
            return score >= params["buy_threshold"]
        return False

    def sell_signal(i):
        if strategy_name == "移動平均線策略":
            return (
                pd.notna(data.loc[i-1, "MA_short"]) and
                pd.notna(data.loc[i-1, "MA_long"]) and
                data.loc[i-1, "MA_short"] >= data.loc[i-1, "MA_long"] and
                data.loc[i, "MA_short"] < data.loc[i, "MA_long"]
            )
        elif strategy_name == "RSI逆勢策略":
            return pd.notna(data.loc[i, "RSI"]) and data.loc[i, "RSI"] > params["overbought"]
        elif strategy_name == "布林通道策略":
            return pd.notna(data.loc[i, "BB_UPPER"]) and data.loc[i, "close"] > data.loc[i, "BB_UPPER"]
        elif strategy_name == "MACD策略":
            return (
                pd.notna(data.loc[i-1, "MACD"]) and pd.notna(data.loc[i-1, "MACD_SIGNAL"]) and
                data.loc[i-1, "MACD"] >= data.loc[i-1, "MACD_SIGNAL"] and
                data.loc[i, "MACD"] < data.loc[i, "MACD_SIGNAL"]
            )
        elif strategy_name == "KD策略":
            return (
                pd.notna(data.loc[i-1, "K"]) and pd.notna(data.loc[i-1, "D"]) and
                data.loc[i-1, "K"] >= data.loc[i-1, "D"] and
                data.loc[i, "K"] < data.loc[i, "D"] and
                data.loc[i, "K"] > params["overbought"]
            )
        elif strategy_name == "網格交易策略":
            return False
        elif strategy_name == "多策略組合":
            score = 0
            if pd.notna(data.loc[i, "MA_short"]) and pd.notna(data.loc[i, "MA_long"]) and data.loc[i, "MA_short"] < data.loc[i, "MA_long"]:
                score += params["w_ma"]
            if pd.notna(data.loc[i, "RSI"]) and data.loc[i, "RSI"] > params["overbought"]:
                score += params["w_rsi"]
            if pd.notna(data.loc[i, "BB_UPPER"]) and data.loc[i, "close"] > data.loc[i, "BB_UPPER"]:
                score += params["w_bb"]
            return score >= params["sell_threshold"]
        return False

    # 網格交易單獨處理
    if strategy_name == "網格交易策略":
        base_price = float(data.loc[0, "close"])
        grid_pct = params["grid_pct"]
        max_layers = params["max_layers"]
        grid_size = base_price * grid_pct
        buy_levels = [base_price - (i + 1) * grid_size for i in range(max_layers)]
        sell_levels = [base_price + (i + 1) * grid_size for i in range(max_layers)]

        open_positions = []

        for i in range(1, len(data) - 1):
            price = float(data.loc[i, "close"])
            next_open = float(data.loc[i + 1, "open"])
            next_time = data.loc[i + 1, "time"]

            # 分層買入
            for lvl_idx, lvl in enumerate(buy_levels):
                if price <= lvl and len(open_positions) <= lvl_idx:
                    open_positions.append({
                        "side": "long",
                        "entry_time": next_time,
                        "entry_price": next_open,
                        "qty": qty
                    })
                    signals.append({
                        "time": next_time,
                        "price": next_open,
                        "type": "buy",
                        "label": f"網格買 {lvl_idx+1}"
                    })

            # 分層賣出
            while open_positions and price >= sell_levels[len(open_positions) - 1]:
                pos = open_positions.pop()
                trade = close_trade(pos, next_time, next_open, "grid_take_profit")
                trades.append(trade)
                signals.append({
                    "time": next_time,
                    "price": next_open,
                    "type": "sell",
                    "label": "網格賣"
                })

        # 最後平倉
        if open_positions:
            final_time = data.loc[len(data) - 1, "time"]
            final_price = float(data.loc[len(data) - 1, "close"])
            for pos in open_positions:
                trades.append(close_trade(pos, final_time, final_price, "final_close"))
                signals.append({
                    "time": final_time,
                    "price": final_price,
                    "type": "sell",
                    "label": "期末平倉"
                })

        return trades, signals

    # 一般策略
    for i in range(2, len(data) - 1):
        next_open = float(data.loc[i + 1, "open"])
        next_time = data.loc[i + 1, "time"]
        current_close = float(data.loc[i, "close"])

        if position is None:
            if buy_signal(i):
                position = {
                    "side": "long",
                    "entry_time": next_time,
                    "entry_price": next_open,
                    "qty": qty
                }
                stop_price = next_open - stop_loss
                signals.append({"time": next_time, "price": next_open, "type": "buy", "label": "買進"})

            elif sell_signal(i):
                position = {
                    "side": "short",
                    "entry_time": next_time,
                    "entry_price": next_open,
                    "qty": qty
                }
                stop_price = next_open + stop_loss
                signals.append({"time": next_time, "price": next_open, "type": "sell", "label": "放空"})

        else:
            if position["side"] == "long":
                stop_price = max(stop_price, current_close - stop_loss)
                exit_cond = sell_signal(i) or current_close < stop_price
                if exit_cond:
                    trade = close_trade(position, next_time, next_open, "long_exit")
                    trades.append(trade)
                    signals.append({"time": next_time, "price": next_open, "type": "sell", "label": "平多"})
                    position = None
                    stop_price = None

            elif position["side"] == "short":
                stop_price = min(stop_price, current_close + stop_loss)
                exit_cond = buy_signal(i) or current_close > stop_price
                if exit_cond:
                    trade = close_trade(position, next_time, next_open, "short_exit")
                    trades.append(trade)
                    signals.append({"time": next_time, "price": next_open, "type": "buy", "label": "平空"})
                    position = None
                    stop_price = None

    if position is not None:
        final_time = data.loc[len(data) - 1, "time"]
        final_price = float(data.loc[len(data) - 1, "close"])
        trade = close_trade(position, final_time, final_price, "final_close")
        trades.append(trade)
        signals.append({
            "time": final_time,
            "price": final_price,
            "type": "sell" if position["side"] == "long" else "buy",
            "label": "期末平倉"
        })

    return trades, signals

# =========================================================
# 圖表函式
# =========================================================
def create_main_chart(df, overlays, signals=None):
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.05
    )

    fig.add_trace(
        go.Candlestick(
            x=df["time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="K線"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df["time"],
            y=df["volume"],
            name="成交量"
        ),
        row=2, col=1
    )

    if overlays.get("ma"):
        fig.add_trace(go.Scatter(x=df["time"], y=df["MA_short"], mode="lines", name="MA短"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=df["MA_long"], mode="lines", name="MA長"), row=1, col=1)

    if overlays.get("ema"):
        fig.add_trace(go.Scatter(x=df["time"], y=df["EMA_short"], mode="lines", name="EMA短"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=df["EMA_long"], mode="lines", name="EMA長"), row=1, col=1)

    if overlays.get("bb"):
        fig.add_trace(go.Scatter(x=df["time"], y=df["BB_UPPER"], mode="lines", name="BB上軌"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=df["BB_SMA"], mode="lines", name="BB中軌"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=df["BB_LOWER"], mode="lines", name="BB下軌"), row=1, col=1)

    if overlays.get("vwap"):
        fig.add_trace(go.Scatter(x=df["time"], y=df["VWAP"], mode="lines", name="VWAP"), row=1, col=1)

    if overlays.get("psar"):
        fig.add_trace(go.Scatter(
            x=df["time"],
            y=df["PSAR"],
            mode="markers",
            name="PSAR",
            marker=dict(size=5)
        ), row=1, col=1)

    if overlays.get("donchian"):
        fig.add_trace(go.Scatter(x=df["time"], y=df["DON_UPPER"], mode="lines", name="Donchian上"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=df["DON_LOWER"], mode="lines", name="Donchian下"), row=1, col=1)

    # 買賣點
    if signals:
        buy_signals = [s for s in signals if s["type"] == "buy"]
        sell_signals = [s for s in signals if s["type"] == "sell"]

        if buy_signals:
            fig.add_trace(go.Scatter(
                x=[s["time"] for s in buy_signals],
                y=[s["price"] for s in buy_signals],
                mode="markers+text",
                name="買點",
                text=[s["label"] for s in buy_signals],
                textposition="top center",
                marker=dict(symbol="triangle-up", size=12, color="green")
            ), row=1, col=1)

        if sell_signals:
            fig.add_trace(go.Scatter(
                x=[s["time"] for s in sell_signals],
                y=[s["price"] for s in sell_signals],
                mode="markers+text",
                name="賣點",
                text=[s["label"] for s in sell_signals],
                textposition="bottom center",
                marker=dict(symbol="triangle-down", size=12, color="red")
            ), row=1, col=1)

    fig.update_layout(
        height=760,
        xaxis_rangeslider_visible=True,
        legend_orientation="h",
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig

def create_indicator_chart(df, indicator_name):
    fig = go.Figure()

    if indicator_name == "RSI":
        fig.add_trace(go.Scatter(x=df["time"], y=df["RSI"], mode="lines", name="RSI"))
        fig.add_hline(y=70, line_dash="dash")
        fig.add_hline(y=30, line_dash="dash")
        fig.update_yaxes(range=[0, 100])

    elif indicator_name == "MACD":
        fig.add_trace(go.Bar(x=df["time"], y=df["MACD_HIST"], name="Histogram"))
        fig.add_trace(go.Scatter(x=df["time"], y=df["MACD"], mode="lines", name="MACD"))
        fig.add_trace(go.Scatter(x=df["time"], y=df["MACD_SIGNAL"], mode="lines", name="Signal"))

    elif indicator_name == "ATR":
        fig.add_trace(go.Scatter(x=df["time"], y=df["ATR"], mode="lines", name="ATR"))

    elif indicator_name == "OBV":
        fig.add_trace(go.Scatter(x=df["time"], y=df["OBV"], mode="lines", name="OBV"))

    elif indicator_name == "CCI":
        fig.add_trace(go.Scatter(x=df["time"], y=df["CCI"], mode="lines", name="CCI"))
        fig.add_hline(y=100, line_dash="dash")
        fig.add_hline(y=-100, line_dash="dash")

    elif indicator_name == "KD":
        fig.add_trace(go.Scatter(x=df["time"], y=df["K"], mode="lines", name="K"))
        fig.add_trace(go.Scatter(x=df["time"], y=df["D"], mode="lines", name="D"))
        fig.add_hline(y=80, line_dash="dash")
        fig.add_hline(y=20, line_dash="dash")
        fig.update_yaxes(range=[0, 100])

    elif indicator_name == "WILLR":
        fig.add_trace(go.Scatter(x=df["time"], y=df["WILLR"], mode="lines", name="WILLR"))
        fig.add_hline(y=-20, line_dash="dash")
        fig.add_hline(y=-80, line_dash="dash")
        fig.update_yaxes(range=[-100, 0])

    elif indicator_name == "MFI":
        fig.add_trace(go.Scatter(x=df["time"], y=df["MFI"], mode="lines", name="MFI"))
        fig.add_hline(y=80, line_dash="dash")
        fig.add_hline(y=20, line_dash="dash")
        fig.update_yaxes(range=[0, 100])

    elif indicator_name == "ROC":
        fig.add_trace(go.Scatter(x=df["time"], y=df["ROC"], mode="lines", name="ROC"))

    elif indicator_name == "MOM":
        fig.add_trace(go.Scatter(x=df["time"], y=df["MOM"], mode="lines", name="MOM"))

    elif indicator_name == "TRIX":
        fig.add_trace(go.Scatter(x=df["time"], y=df["TRIX"], mode="lines", name="TRIX"))

    elif indicator_name == "ADX":
        fig.add_trace(go.Scatter(x=df["time"], y=df["ADX"], mode="lines", name="ADX"))
        fig.add_trace(go.Scatter(x=df["time"], y=df["PLUS_DI"], mode="lines", name="+DI"))
        fig.add_trace(go.Scatter(x=df["time"], y=df["MINUS_DI"], mode="lines", name="-DI"))
        fig.add_hline(y=25, line_dash="dash")
        fig.update_yaxes(range=[0, 100])

    elif indicator_name == "BB_WIDTH":
        fig.add_trace(go.Scatter(x=df["time"], y=df["BB_WIDTH"], mode="lines", name="BB Width"))

    fig.update_layout(
        height=320,
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_rangeslider_visible=True
    )
    return fig

def create_equity_curve(trades, choice):
    multiplier = contract_multipliers.get(choice, 1)
    if not trades:
        return go.Figure()

    pnl = [t["pnl"] * multiplier for t in trades]
    eq = np.cumsum(pnl)
    x = [t["exit_time"] for t in trades]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=eq, mode="lines+markers", name="累積損益"))
    fig.update_layout(
        height=350,
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig

# =========================================================
# 左側控制區
# =========================================================
with st.sidebar:
    st.header("資料與參數設定")

    choice = st.selectbox("選擇金融商品", choices, index=0)
    pkl_path, product_name, default_start, default_end = product_info[choice]
    df_original = load_data(pkl_path)

    start_date = st.date_input("開始日期", pd.to_datetime(default_start).date())
    end_date = st.date_input("結束日期", pd.to_datetime(default_end).date())

    st.markdown("---")
    st.subheader("K 棒週期")
    timeframe_mode = st.selectbox("時間單位", ["分鐘", "小時", "日", "週", "月"], index=1)

    if timeframe_mode == "分鐘":
        tf_value = st.number_input("每根 K 棒分鐘數", min_value=1, max_value=1440, value=60, step=1)
    elif timeframe_mode == "小時":
        tf_value = st.number_input("每根 K 棒小時數", min_value=1, max_value=24, value=1, step=1)
    elif timeframe_mode == "日":
        tf_value = st.number_input("每根 K 棒天數", min_value=1, max_value=365, value=1, step=1)
    elif timeframe_mode == "週":
        tf_value = st.number_input("每根 K 棒週數", min_value=1, max_value=52, value=1, step=1)
    else:
        tf_value = st.number_input("每根 K 棒月數", min_value=1, max_value=24, value=1, step=1)

    st.markdown("---")
    st.subheader("技術指標參數")

    params = {
        "ma_short": st.slider("MA 短期", 1, 200, 5),
        "ma_long": st.slider("MA 長期", 2, 300, 20),
        "ema_short": st.slider("EMA 短期", 1, 200, 8),
        "ema_long": st.slider("EMA 長期", 2, 300, 21),
        "rsi_period": st.slider("RSI 週期", 1, 100, 14),
        "bb_period": st.slider("布林通道週期", 2, 200, 20),
        "bb_std": st.slider("布林標準差倍數", 0.5, 5.0, 2.0, 0.1),
        "macd_fast": st.slider("MACD 快線", 1, 100, 12),
        "macd_slow": st.slider("MACD 慢線", 2, 200, 26),
        "macd_signal": st.slider("MACD 訊號線", 1, 100, 9),
        "atr_period": st.slider("ATR 週期", 1, 100, 14),
        "cci_period": st.slider("CCI 週期", 1, 100, 20),
        "k_period": st.slider("KD K 週期", 1, 100, 14),
        "d_period": st.slider("KD D 平滑", 1, 20, 3),
        "willr_period": st.slider("WILLR 週期", 1, 100, 14),
        "mfi_period": st.slider("MFI 週期", 1, 100, 14),
        "roc_period": st.slider("ROC 週期", 1, 100, 12),
        "mom_period": st.slider("MOM 週期", 1, 100, 10),
        "trix_period": st.slider("TRIX 週期", 1, 100, 15),
        "donchian_period": st.slider("Donchian 週期", 2, 200, 20),
        "adx_period": st.slider("ADX 週期", 2, 100, 14),
    }

    st.markdown("---")
    st.subheader("主圖疊加")
    overlay_ma = st.checkbox("MA", value=True)
    overlay_ema = st.checkbox("EMA", value=False)
    overlay_bb = st.checkbox("布林通道", value=True)
    overlay_vwap = st.checkbox("VWAP", value=True)
    overlay_psar = st.checkbox("PSAR", value=False)
    overlay_donchian = st.checkbox("Donchian", value=False)

    st.markdown("---")
    st.subheader("回測策略")
    strategy_choice = st.selectbox(
        "策略選擇",
        [
            "移動平均線策略",
            "RSI逆勢策略",
            "布林通道策略",
            "MACD策略",
            "KD策略",
            "網格交易策略",
            "多策略組合"
        ],
        index=0
    )

    backtest_params = {
        "qty": st.number_input("下單口數 / 張數", min_value=1, max_value=1000, value=1),
        "stop_loss": st.number_input("移動停損點數", min_value=0.0, value=30.0, step=1.0),
        "oversold": st.slider("超賣", 1, 50, 30),
        "overbought": st.slider("超買", 50, 99, 70),
        "grid_pct": st.slider("網格間距 (%)", 0.1, 10.0, 2.0, 0.1) / 100.0,
        "max_layers": st.slider("網格最大層數", 1, 20, 5),
        "buy_threshold": st.slider("買入分數門檻", 0.0, 2.0, 0.8, 0.05),
        "sell_threshold": st.slider("賣出分數門檻", 0.0, 2.0, 0.8, 0.05),
        "w_ma": st.slider("MA 權重", 0.0, 1.0, 0.4, 0.05),
        "w_rsi": st.slider("RSI 權重", 0.0, 1.0, 0.3, 0.05),
        "w_bb": st.slider("BB 權重", 0.0, 1.0, 0.3, 0.05),
    }

    run_backtest = st.button("開始回測", use_container_width=True)

# =========================================================
# 資料處理
# =========================================================
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

df_filtered = df_original[(df_original["time"] >= start_ts) & (df_original["time"] <= end_ts)].copy()

if df_filtered.empty:
    st.error("目前選擇區間沒有資料。")
    st.stop()

rule = get_resample_rule(timeframe_mode, tf_value)
kbar_df = resample_ohlcv(df_filtered, rule, product_name)

if len(kbar_df) < 10:
    st.warning("重整後 K 棒太少，請縮短週期或增加日期範圍。")

indicator_df = add_all_indicators(kbar_df, params)

# =========================================================
# 右邊兩頁版面
# =========================================================
left_col, right_col = st.columns([1, 2.5], gap="large")

with left_col:
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.subheader("資料摘要")
    st.write(f"商品：**{product_name}**")
    st.write(f"區間：**{start_ts.date()} ~ {end_ts.date()}**")
    st.write(f"K棒：**{timeframe_mode} / {tf_value}**")
    st.write(f"筆數：**{len(indicator_df):,}**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.subheader("指標檢查")
    checks = []
    checks.append("RSI 正常" if indicator_df["RSI"].dropna().between(0, 100).all() else "RSI 超出範圍")
    checks.append("KD 正常" if indicator_df["K"].dropna().between(0, 100).all() and indicator_df["D"].dropna().between(0, 100).all() else "KD 超出範圍")
    checks.append("MFI 正常" if indicator_df["MFI"].dropna().between(0, 100).all() else "MFI 超出範圍")
    checks.append("WILLR 正常" if indicator_df["WILLR"].dropna().between(-100, 0).all() else "WILLR 超出範圍")
    checks.append("ADX 正常" if indicator_df["ADX"].dropna().between(0, 100).all() else "ADX 超出範圍")
    for c in checks:
        st.write(f"- {c}")
    st.markdown('<div class="small-note">新增：VWAP、Donchian、ADX；主頁直接 K 線；可畫買賣點。</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    tab_basic, tab_backtest = st.tabs(["基本圖表", "回測分析"])

    with tab_basic:
        st.subheader("主頁 K 線圖")
        main_fig = create_main_chart(
            indicator_df,
            overlays={
                "ma": overlay_ma,
                "ema": overlay_ema,
                "bb": overlay_bb,
                "vwap": overlay_vwap,
                "psar": overlay_psar,
                "donchian": overlay_donchian
            },
            signals=None
        )
        st.plotly_chart(main_fig, use_container_width=True)

        selected_indicators = st.multiselect(
            "選擇要顯示的附加指標",
            ["RSI", "MACD", "ATR", "OBV", "CCI", "KD", "WILLR", "MFI", "ROC", "MOM", "TRIX", "ADX", "BB_WIDTH"],
            default=["RSI", "MACD", "ATR"]
        )

        for name in selected_indicators:
            st.plotly_chart(create_indicator_chart(indicator_df, name), use_container_width=True)

    with tab_backtest:
        st.subheader("回測結果與買賣點")

        if run_backtest:
            trades, signals = backtest_strategy(indicator_df, strategy_choice, backtest_params)

            bt_fig = create_main_chart(
                indicator_df,
                overlays={
                    "ma": overlay_ma,
                    "ema": overlay_ema,
                    "bb": overlay_bb,
                    "vwap": overlay_vwap,
                    "psar": overlay_psar,
                    "donchian": overlay_donchian
                },
                signals=signals
            )
            st.plotly_chart(bt_fig, use_container_width=True)

            perf_df = calculate_performance(trades, choice)
            st.dataframe(perf_df, use_container_width=True, hide_index=True)

            eq_fig = create_equity_curve(trades, choice)
            if len(eq_fig.data) > 0:
                st.plotly_chart(eq_fig, use_container_width=True)

            if trades:
                trades_df = pd.DataFrame(trades)
                trades_df["entry_time"] = pd.to_datetime(trades_df["entry_time"])
                trades_df["exit_time"] = pd.to_datetime(trades_df["exit_time"])
                trades_df["pnl_value"] = trades_df["pnl"] * contract_multipliers.get(choice, 1)
                st.subheader("交易紀錄")
                st.dataframe(
                    trades_df[["side", "entry_time", "entry_price", "exit_time", "exit_price", "qty", "pnl_value", "reason"]],
                    use_container_width=True
                )
            else:
                st.warning("沒有產生交易紀錄，請調整策略或參數。")

        else:
            st.info("請先在左邊設定參數後按「開始回測」。")

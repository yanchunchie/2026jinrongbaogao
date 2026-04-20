# -*- coding: utf-8 -*-
"""
升級版金融資料視覺化看板 / 程式交易平台
- 左側：參數與策略設定
- 右側：K線、指標、回測、最佳化結果
- 首頁直接顯示 K 線圖
- 新增小時 K 線
- 保留選擇區塊
- 淡黃色背景與標題
- 新增網格交易、自訂策略、簡易最佳化
"""

import os
import math
import json
import random
import datetime
from itertools import product

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as stc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import indicator_forKBar_short
from order_streamlit import Record


# =========================================================
# 基本設定
# =========================================================
st.set_page_config(
    page_title="金融看板與程式交易平台",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 淡黃色背景 / 標題
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
# 讀取資料
# =========================================================
@st.cache_data(ttl=3600, show_spinner="正在讀取資料...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_pickle(path)
    df = df.copy()
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    return df


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
    choices[12]: 1,
    choices[13]: 250,
    choices[14]: 1000
}


# =========================================================
# 工具函數
# =========================================================
def safe_last_valid_start(series: pd.Series) -> int:
    valid_idx = series.first_valid_index()
    return 0 if valid_idx is None else int(valid_idx)


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


def performance_summary(choice, order_record):
    multiplier = contract_multipliers.get(choice, 1)
    if "摩台期貨" in choice:
        multiplier *= 30

    total_profit = order_record.GetTotalProfit() * multiplier
    avg_profit = order_record.GetAverageProfit() * multiplier
    avg_profit_rate = order_record.GetAverageProfitRate()
    avg_earn = order_record.GetAverEarn() * multiplier
    avg_loss = order_record.GetAverLoss() * multiplier
    win_rate = order_record.GetWinRate()
    acc_loss = order_record.GetAccLoss() * multiplier
    mdd = order_record.GetMDD() * multiplier
    rr = total_profit / mdd if mdd not in [0, None] else np.nan

    return pd.DataFrame({
        "項目": [
            "交易總盈虧", "平均每次盈虧", "平均投資報酬率", "平均獲利",
            "平均虧損", "勝率", "最大連續虧損", "最大回落 MDD", "報酬風險比"
        ],
        "數值": [
            round(total_profit, 2),
            round(avg_profit, 2),
            round(avg_profit_rate, 4) if pd.notna(avg_profit_rate) else np.nan,
            round(avg_earn, 2),
            round(avg_loss, 2),
            round(win_rate, 4) if pd.notna(win_rate) else np.nan,
            round(acc_loss, 2),
            round(mdd, 2),
            round(rr, 4) if pd.notna(rr) else np.nan
        ]
    })


@st.cache_data(ttl=3600, show_spinner="正在轉換 K 棒週期...")
def to_dictionary(df, product_name):
    return {
        "time": df["time"].to_numpy(),
        "product": np.repeat(product_name, len(df)),
        "open": df["open"].to_numpy(),
        "high": df["high"].to_numpy(),
        "low": df["low"].to_numpy(),
        "close": df["close"].to_numpy(),
        "volume": df["volume"].to_numpy(),
        "amount": df["amount"].to_numpy() if "amount" in df.columns else np.zeros(len(df))
    }


@st.cache_data(ttl=3600, show_spinner="正在重整 K 棒...")
def change_cycle(date_str, cycle_duration_minutes, kbar_dic, product_name):
    kbar = indicator_forKBar_short.KBar(date_str, cycle_duration_minutes)

    for i in range(len(kbar_dic["time"])):
        kbar.AddPrice(
            kbar_dic["time"][i],
            kbar_dic["open"][i],
            kbar_dic["close"][i],
            kbar_dic["low"][i],
            kbar_dic["high"][i],
            kbar_dic["volume"][i]
        )

    new_dic = {
        "time": kbar.TAKBar["time"],
        "product": np.repeat(product_name, len(kbar.TAKBar["time"])),
        "open": kbar.TAKBar["open"],
        "high": kbar.TAKBar["high"],
        "low": kbar.TAKBar["low"],
        "close": kbar.TAKBar["close"],
        "volume": kbar.TAKBar["volume"]
    }
    return pd.DataFrame(new_dic)


# =========================================================
# 指標
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
    direction = direction.replace({-1: -1, 1: 1})
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
    vwap = price_volume.cumsum() / df["volume"].replace(0, np.nan).cumsum()
    return vwap

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
# 圖表
# =========================================================
def create_main_candlestick_chart(df, overlays):
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
        go.Bar(x=df["time"], y=df["volume"], name="成交量"),
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
            x=df["time"], y=df["PSAR"], mode="markers", name="PSAR", marker=dict(size=5)
        ), row=1, col=1)

    if overlays.get("donchian"):
        fig.add_trace(go.Scatter(x=df["time"], y=df["DON_UPPER"], mode="lines", name="Donchian上"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=df["DON_LOWER"], mode="lines", name="Donchian下"), row=1, col=1)

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


# =========================================================
# 策略回測
# =========================================================
def get_record(choice):
    is_future = ("期貨" in choice) or ("指數期" in choice)
    if is_future:
        return Record(spread=3.628e-4, tax=0.00002, commission=0.0002, isFuture=True)
    return Record(spread=3.628e-4, tax=0.003, commission=0.001425, isFuture=False)


def backtest_ma_strategy(record_obj, df, short_period, long_period, stop_loss, qty):
    data = df.copy()
    data["MA_S"] = calc_ma(data, short_period)
    data["MA_L"] = calc_ma(data, long_period)

    start_idx = max(safe_last_valid_start(data["MA_S"]), safe_last_valid_start(data["MA_L"]))
    stop_price = None

    for i in range(start_idx + 1, len(data) - 1):
        if record_obj.GetOpenInterest() == 0:
            if data["MA_S"].iloc[i - 1] <= data["MA_L"].iloc[i - 1] and data["MA_S"].iloc[i] > data["MA_L"].iloc[i]:
                record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] - stop_loss
            elif data["MA_S"].iloc[i - 1] >= data["MA_L"].iloc[i - 1] and data["MA_S"].iloc[i] < data["MA_L"].iloc[i]:
                record_obj.Order("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] + stop_loss

        elif record_obj.GetOpenInterest() > 0:
            stop_price = max(stop_price, data["close"].iloc[i] - stop_loss)
            exit_cross = data["MA_S"].iloc[i] < data["MA_L"].iloc[i]
            exit_stop = data["close"].iloc[i] < stop_price
            if exit_cross or exit_stop:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], record_obj.GetOpenInterest())

        elif record_obj.GetOpenInterest() < 0:
            stop_price = min(stop_price, data["close"].iloc[i] + stop_loss)
            exit_cross = data["MA_S"].iloc[i] > data["MA_L"].iloc[i]
            exit_stop = data["close"].iloc[i] > stop_price
            if exit_cross or exit_stop:
                record_obj.Cover("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], -record_obj.GetOpenInterest())

    return record_obj


def backtest_rsi_strategy(record_obj, df, rsi_period, oversold, overbought, stop_loss, qty):
    data = df.copy()
    data["RSI"] = calc_rsi(data, rsi_period)
    start_idx = safe_last_valid_start(data["RSI"])
    stop_price = None

    for i in range(start_idx + 1, len(data) - 1):
        rsi = data["RSI"].iloc[i]

        if record_obj.GetOpenInterest() == 0:
            if rsi < oversold:
                record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] - stop_loss
            elif rsi > overbought:
                record_obj.Order("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] + stop_loss

        elif record_obj.GetOpenInterest() > 0:
            stop_price = max(stop_price, data["close"].iloc[i] - stop_loss)
            if data["close"].iloc[i] < stop_price or rsi > overbought:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], record_obj.GetOpenInterest())

        elif record_obj.GetOpenInterest() < 0:
            stop_price = min(stop_price, data["close"].iloc[i] + stop_loss)
            if data["close"].iloc[i] > stop_price or rsi < oversold:
                record_obj.Cover("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], -record_obj.GetOpenInterest())

    return record_obj


def backtest_bb_strategy(record_obj, df, bb_period, bb_std, stop_loss, qty):
    data = df.copy()
    data["MID"], data["UP"], data["LOW"], _ = calc_bb(data, bb_period, bb_std)
    start_idx = max(safe_last_valid_start(data["MID"]), safe_last_valid_start(data["UP"]), safe_last_valid_start(data["LOW"]))
    stop_price = None

    for i in range(start_idx + 1, len(data) - 1):
        if record_obj.GetOpenInterest() == 0:
            if data["close"].iloc[i] < data["LOW"].iloc[i]:
                record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] - stop_loss
            elif data["close"].iloc[i] > data["UP"].iloc[i]:
                record_obj.Order("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] + stop_loss

        elif record_obj.GetOpenInterest() > 0:
            stop_price = max(stop_price, data["close"].iloc[i] - stop_loss)
            if data["close"].iloc[i] > data["MID"].iloc[i] or data["close"].iloc[i] < stop_price:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], record_obj.GetOpenInterest())

        elif record_obj.GetOpenInterest() < 0:
            stop_price = min(stop_price, data["close"].iloc[i] + stop_loss)
            if data["close"].iloc[i] < data["MID"].iloc[i] or data["close"].iloc[i] > stop_price:
                record_obj.Cover("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], -record_obj.GetOpenInterest())

    return record_obj


def backtest_macd_strategy(record_obj, df, fast_period, slow_period, signal_period, stop_loss, qty):
    data = df.copy()
    _, _, data["MACD"], data["SIGNAL"], _ = calc_macd(data, fast_period, slow_period, signal_period)
    start_idx = max(safe_last_valid_start(data["MACD"]), safe_last_valid_start(data["SIGNAL"]))
    stop_price = None

    for i in range(start_idx + 1, len(data) - 1):
        bull = data["MACD"].iloc[i - 1] <= data["SIGNAL"].iloc[i - 1] and data["MACD"].iloc[i] > data["SIGNAL"].iloc[i]
        bear = data["MACD"].iloc[i - 1] >= data["SIGNAL"].iloc[i - 1] and data["MACD"].iloc[i] < data["SIGNAL"].iloc[i]

        if record_obj.GetOpenInterest() == 0:
            if bull:
                record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] - stop_loss
            elif bear:
                record_obj.Order("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] + stop_loss

        elif record_obj.GetOpenInterest() > 0:
            stop_price = max(stop_price, data["close"].iloc[i] - stop_loss)
            if bear or data["close"].iloc[i] < stop_price:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], record_obj.GetOpenInterest())

        elif record_obj.GetOpenInterest() < 0:
            stop_price = min(stop_price, data["close"].iloc[i] + stop_loss)
            if bull or data["close"].iloc[i] > stop_price:
                record_obj.Cover("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], -record_obj.GetOpenInterest())

    return record_obj


def backtest_kd_strategy(record_obj, df, k_period, d_period, oversold, overbought, stop_loss, qty):
    data = df.copy()
    data["K"], data["D"] = calc_kd(data, k_period, d_period)
    start_idx = max(safe_last_valid_start(data["K"]), safe_last_valid_start(data["D"]))
    stop_price = None

    for i in range(start_idx + 1, len(data) - 1):
        bull = data["K"].iloc[i - 1] <= data["D"].iloc[i - 1] and data["K"].iloc[i] > data["D"].iloc[i]
        bear = data["K"].iloc[i - 1] >= data["D"].iloc[i - 1] and data["K"].iloc[i] < data["D"].iloc[i]

        if record_obj.GetOpenInterest() == 0:
            if bull and data["K"].iloc[i] < oversold:
                record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] - stop_loss
            elif bear and data["K"].iloc[i] > overbought:
                record_obj.Order("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] + stop_loss

        elif record_obj.GetOpenInterest() > 0:
            stop_price = max(stop_price, data["close"].iloc[i] - stop_loss)
            if bear or data["close"].iloc[i] < stop_price:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], record_obj.GetOpenInterest())

        elif record_obj.GetOpenInterest() < 0:
            stop_price = min(stop_price, data["close"].iloc[i] + stop_loss)
            if bull or data["close"].iloc[i] > stop_price:
                record_obj.Cover("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], -record_obj.GetOpenInterest())

    return record_obj


def backtest_grid_strategy(record_obj, df, grid_pct=0.02, max_layers=5, qty=1):
    """
    簡化版網格交易：
    - 以第一根 close 為基準
    - 每跌一格加碼買，回到上一格以上出場
    - 只示範多單網格
    """
    data = df.copy()
    if len(data) < 3:
        return record_obj

    base_price = data["close"].iloc[0]
    grid_size = base_price * grid_pct
    buy_levels = [base_price - i * grid_size for i in range(1, max_layers + 1)]
    sell_levels = [base_price + i * grid_size for i in range(1, max_layers + 1)]

    current_layer = 0
    for i in range(1, len(data) - 1):
        price = data["close"].iloc[i]

        if current_layer < max_layers and price <= buy_levels[current_layer]:
            record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
            current_layer += 1

        elif current_layer > 0:
            target_sell_idx = max(current_layer - 1, 0)
            if price >= sell_levels[target_sell_idx]:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], min(qty, record_obj.GetOpenInterest()))
                current_layer -= 1

    return record_obj


def backtest_multi_strategy(record_obj, df, params, stop_loss, qty):
    data = df.copy()
    data["MA_S"] = calc_ma(data, params["ma_short"])
    data["MA_L"] = calc_ma(data, params["ma_long"])
    data["RSI"] = calc_rsi(data, params["rsi_period"])
    data["BB_MID"], data["BB_UP"], data["BB_LOW"], _ = calc_bb(data, params["bb_period"], params["bb_std"])

    start_idx = max(
        safe_last_valid_start(data["MA_S"]),
        safe_last_valid_start(data["MA_L"]),
        safe_last_valid_start(data["RSI"]),
        safe_last_valid_start(data["BB_MID"]),
    )
    stop_price = None
    signal_rows = []

    for i in range(start_idx + 1, len(data) - 1):
        buy_score = 0.0
        sell_score = 0.0

        ma_signal = 0.0
        rsi_signal = 0.0
        bb_signal = 0.0

        if data["MA_S"].iloc[i] > data["MA_L"].iloc[i]:
            buy_score += params["w_ma"]
            ma_signal = params["w_ma"]
        elif data["MA_S"].iloc[i] < data["MA_L"].iloc[i]:
            sell_score += params["w_ma"]
            ma_signal = -params["w_ma"]

        if data["RSI"].iloc[i] < params["oversold"]:
            buy_score += params["w_rsi"]
            rsi_signal = params["w_rsi"]
        elif data["RSI"].iloc[i] > params["overbought"]:
            sell_score += params["w_rsi"]
            rsi_signal = -params["w_rsi"]

        if data["close"].iloc[i] < data["BB_LOW"].iloc[i]:
            buy_score += params["w_bb"]
            bb_signal = params["w_bb"]
        elif data["close"].iloc[i] > data["BB_UP"].iloc[i]:
            sell_score += params["w_bb"]
            bb_signal = -params["w_bb"]

        signal_rows.append({
            "time": data["time"].iloc[i],
            "buy_score": buy_score,
            "sell_score": sell_score,
            "MA_signal": ma_signal,
            "RSI_signal": rsi_signal,
            "BB_signal": bb_signal
        })

        if record_obj.GetOpenInterest() == 0:
            if buy_score >= params["buy_threshold"]:
                record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] - stop_loss
            elif sell_score >= params["sell_threshold"]:
                record_obj.Order("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] + stop_loss

        elif record_obj.GetOpenInterest() > 0:
            stop_price = max(stop_price, data["close"].iloc[i] - stop_loss)
            if sell_score >= params["sell_threshold"] or data["close"].iloc[i] < stop_price:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], record_obj.GetOpenInterest())

        elif record_obj.GetOpenInterest() < 0:
            stop_price = min(stop_price, data["close"].iloc[i] + stop_loss)
            if buy_score >= params["buy_threshold"] or data["close"].iloc[i] > stop_price:
                record_obj.Cover("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], -record_obj.GetOpenInterest())

    signals_df = pd.DataFrame(signal_rows)
    return record_obj, signals_df


def backtest_custom_strategy(record_obj, df, custom_rules, stop_loss, qty):
    """
    自訂策略規則：
    custom_rules = [
      {"left":"RSI", "op":"<", "right":30, "side":"buy"},
      {"left":"MACD", "op":">", "right":"MACD_SIGNAL", "side":"buy"},
      {"left":"RSI", "op":">", "right":70, "side":"sell"}
    ]
    """
    data = df.copy()
    stop_price = None

    def get_value(row, value):
        if isinstance(value, str) and value in row.index:
            return row[value]
        return value

    def eval_rule(row, rule):
        left = get_value(row, rule["left"])
        right = get_value(row, rule["right"])
        op = rule["op"]

        if pd.isna(left) or pd.isna(right):
            return False

        if op == ">":
            return left > right
        if op == "<":
            return left < right
        if op == ">=":
            return left >= right
        if op == "<=":
            return left <= right
        if op == "==":
            return left == right
        return False

    for i in range(1, len(data) - 1):
        row = data.iloc[i]

        buy_rules = [r for r in custom_rules if r["side"] == "buy"]
        sell_rules = [r for r in custom_rules if r["side"] == "sell"]

        buy_signal = all(eval_rule(row, r) for r in buy_rules) if buy_rules else False
        sell_signal = all(eval_rule(row, r) for r in sell_rules) if sell_rules else False

        if record_obj.GetOpenInterest() == 0:
            if buy_signal:
                record_obj.Order("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] - stop_loss
            elif sell_signal:
                record_obj.Order("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], qty)
                stop_price = data["open"].iloc[i + 1] + stop_loss

        elif record_obj.GetOpenInterest() > 0:
            stop_price = max(stop_price, data["close"].iloc[i] - stop_loss)
            if sell_signal or data["close"].iloc[i] < stop_price:
                record_obj.Cover("Sell", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], record_obj.GetOpenInterest())

        elif record_obj.GetOpenInterest() < 0:
            stop_price = min(stop_price, data["close"].iloc[i] + stop_loss)
            if buy_signal or data["close"].iloc[i] > stop_price:
                record_obj.Cover("Buy", data["product"].iloc[i + 1], data["time"].iloc[i + 1], data["open"].iloc[i + 1], -record_obj.GetOpenInterest())

    return record_obj


# =========================================================
# 側邊欄：參數區
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

    timeframe_mode = st.selectbox(
        "時間單位",
        ["分鐘", "小時", "日", "週", "月"],
        index=1
    )

    if timeframe_mode == "分鐘":
        tf_value = st.number_input("每根 K 棒分鐘數", min_value=1, max_value=1440, value=60, step=1)
        cycle_duration = tf_value
    elif timeframe_mode == "小時":
        tf_value = st.number_input("每根 K 棒小時數", min_value=1, max_value=24, value=1, step=1)
        cycle_duration = tf_value * 60
    elif timeframe_mode == "日":
        tf_value = st.number_input("每根 K 棒天數", min_value=1, max_value=365, value=1, step=1)
        cycle_duration = tf_value * 1440
    elif timeframe_mode == "週":
        tf_value = st.number_input("每根 K 棒週數", min_value=1, max_value=52, value=1, step=1)
        cycle_duration = tf_value * 7 * 1440
    else:
        tf_value = st.number_input("每根 K 棒月數", min_value=1, max_value=24, value=1, step=1)
        cycle_duration = tf_value * 30 * 1440

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
    st.subheader("主圖疊加顯示")
    overlay_ma = st.checkbox("MA", value=True)
    overlay_ema = st.checkbox("EMA", value=False)
    overlay_bb = st.checkbox("布林通道", value=True)
    overlay_vwap = st.checkbox("VWAP", value=True)
    overlay_psar = st.checkbox("PSAR", value=False)
    overlay_donchian = st.checkbox("Donchian", value=False)

    st.markdown("---")
    st.subheader("回測設定")
    strategy_choice = st.selectbox(
        "選擇交易策略",
        [
            "移動平均線策略",
            "RSI逆勢策略",
            "布林通道策略",
            "MACD策略",
            "KD策略",
            "網格交易策略",
            "多策略組合",
            "自訂策略"
        ],
        index=0
    )

    order_qty = st.number_input("下單口數 / 張數", min_value=1, max_value=1000, value=1)
    move_stop_loss = st.number_input("移動停損點數", min_value=0.0, value=30.0, step=1.0)

    # 策略參數
    oversold = st.slider("超賣值", 1, 50, 30)
    overbought = st.slider("超買值", 50, 99, 70)

    grid_pct = st.slider("網格間距 (%)", 0.1, 10.0, 2.0, 0.1) / 100.0
    max_layers = st.slider("網格最大層數", 1, 20, 5)

    st.markdown("---")
    st.subheader("多策略組合參數")
    buy_threshold = st.slider("買入分數門檻", 0.0, 2.0, 0.8, 0.05)
    sell_threshold = st.slider("賣出分數門檻", 0.0, 2.0, 0.8, 0.05)
    w_ma = st.slider("MA 權重", 0.0, 1.0, 0.4, 0.05)
    w_rsi = st.slider("RSI 權重", 0.0, 1.0, 0.3, 0.05)
    w_bb = st.slider("BB 權重", 0.0, 1.0, 0.3, 0.05)

    st.markdown("---")
    st.subheader("自訂策略")
    st.caption("欄位名稱可用：RSI, MACD, MACD_SIGNAL, close, MA_short, MA_long, K, D, MFI, ADX, VWAP")
    custom_rules_text = st.text_area(
        "輸入 JSON 規則",
        value=json.dumps([
            {"left": "RSI", "op": "<", "right": 30, "side": "buy"},
            {"left": "MACD", "op": ">", "right": "MACD_SIGNAL", "side": "buy"},
            {"left": "RSI", "op": ">", "right": 70, "side": "sell"}
        ], ensure_ascii=False, indent=2),
        height=220
    )

    st.markdown("---")
    optimize_switch = st.checkbox("啟用簡易最佳化", value=False)
    optimize_target = st.selectbox("最佳化目標", ["交易總盈虧", "報酬風險比"], index=0)

    run_backtest = st.button("開始回測", use_container_width=True)


# =========================================================
# 資料處理
# =========================================================
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

df_filtered = df_original[(df_original["time"] >= start_ts) & (df_original["time"] <= end_ts)].copy()

if df_filtered.empty:
    st.error("目前選擇的日期區間沒有資料。")
    st.stop()

kbar_dic = to_dictionary(df_filtered, product_name)
date_str = pd.to_datetime(start_ts).strftime("%Y-%m-%d")
kbar_df = change_cycle(date_str, float(cycle_duration), kbar_dic, product_name)
kbar_df["time"] = pd.to_datetime(kbar_df["time"])

if len(kbar_df) < 30:
    st.warning("重整後的 K 棒數量太少，請放大日期區間或改小 K 棒週期。")

indicator_df = add_all_indicators(kbar_df, params)

# 額外給自訂策略欄位名稱相容
indicator_df["MA_short"] = indicator_df["MA_short"]
indicator_df["MA_long"] = indicator_df["MA_long"]


# =========================================================
# 主畫面
# =========================================================
left_info, right_chart = st.columns([1, 2.4], gap="large")

with left_info:
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.subheader("目前資料摘要")
    st.write(f"商品：**{product_name}**")
    st.write(f"時間範圍：**{start_ts.date()} ~ {end_ts.date()}**")
    st.write(f"K 棒單位：**{timeframe_mode} / {tf_value}**")
    st.write(f"筆數：**{len(indicator_df):,}**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.subheader("指標合理性檢查")
    check_msgs = []

    if indicator_df["RSI"].dropna().between(0, 100).all():
        check_msgs.append("RSI 範圍正常（0~100）")
    else:
        check_msgs.append("RSI 有超出 0~100，已建議檢查資料")

    if indicator_df["K"].dropna().between(0, 100).all() and indicator_df["D"].dropna().between(0, 100).all():
        check_msgs.append("KD 範圍正常（0~100）")
    else:
        check_msgs.append("KD 有超出 0~100")

    if indicator_df["MFI"].dropna().between(0, 100).all():
        check_msgs.append("MFI 範圍正常（0~100）")
    else:
        check_msgs.append("MFI 有超出 0~100")

    if indicator_df["WILLR"].dropna().between(-100, 0).all():
        check_msgs.append("WILLR 範圍正常（-100~0）")
    else:
        check_msgs.append("WILLR 有超出 -100~0")

    if indicator_df["ADX"].dropna().between(0, 100).all():
        check_msgs.append("ADX 範圍正常（0~100）")
    else:
        check_msgs.append("ADX 有超出 0~100")

    for msg in check_msgs:
        st.write(f"- {msg}")

    st.markdown('<div class="small-note">新增指標：VWAP、Donchian、ADX，可更方便做趨勢/突破/均值回歸判斷。</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_chart:
    st.subheader("主頁 K 線圖")
    main_fig = create_main_candlestick_chart(
        indicator_df,
        overlays={
            "ma": overlay_ma,
            "ema": overlay_ema,
            "bb": overlay_bb,
            "vwap": overlay_vwap,
            "psar": overlay_psar,
            "donchian": overlay_donchian
        }
    )
    st.plotly_chart(main_fig, use_container_width=True)

tab1, tab2, tab3, tab4 = st.tabs(["技術指標", "策略回測", "最佳化", "資料表"])

with tab1:
    indicators_to_show = st.multiselect(
        "選擇要顯示的指標",
        ["RSI", "MACD", "ATR", "OBV", "CCI", "KD", "WILLR", "MFI", "ROC", "MOM", "TRIX", "ADX", "BB_WIDTH"],
        default=["RSI", "MACD", "ATR"]
    )
    for indicator_name in indicators_to_show:
        st.plotly_chart(create_indicator_chart(indicator_df, indicator_name), use_container_width=True)

with tab2:
    st.subheader("回測結果")

    order_record = None
    signals_df = pd.DataFrame()

    if run_backtest:
        try:
            order_record = get_record(choice)

            if strategy_choice == "移動平均線策略":
                order_record = backtest_ma_strategy(
                    order_record, indicator_df, params["ma_short"], params["ma_long"], move_stop_loss, int(order_qty)
                )

            elif strategy_choice == "RSI逆勢策略":
                order_record = backtest_rsi_strategy(
                    order_record, indicator_df, params["rsi_period"], oversold, overbought, move_stop_loss, int(order_qty)
                )

            elif strategy_choice == "布林通道策略":
                order_record = backtest_bb_strategy(
                    order_record, indicator_df, params["bb_period"], params["bb_std"], move_stop_loss, int(order_qty)
                )

            elif strategy_choice == "MACD策略":
                order_record = backtest_macd_strategy(
                    order_record, indicator_df, params["macd_fast"], params["macd_slow"], params["macd_signal"], move_stop_loss, int(order_qty)
                )

            elif strategy_choice == "KD策略":
                order_record = backtest_kd_strategy(
                    order_record, indicator_df, params["k_period"], params["d_period"], oversold, overbought, move_stop_loss, int(order_qty)
                )

            elif strategy_choice == "網格交易策略":
                order_record = backtest_grid_strategy(
                    order_record, indicator_df, grid_pct=grid_pct, max_layers=max_layers, qty=int(order_qty)
                )

            elif strategy_choice == "多策略組合":
                order_record, signals_df = backtest_multi_strategy(
                    order_record,
                    indicator_df,
                    {
                        "ma_short": params["ma_short"],
                        "ma_long": params["ma_long"],
                        "rsi_period": params["rsi_period"],
                        "bb_period": params["bb_period"],
                        "bb_std": params["bb_std"],
                        "oversold": oversold,
                        "overbought": overbought,
                        "buy_threshold": buy_threshold,
                        "sell_threshold": sell_threshold,
                        "w_ma": w_ma,
                        "w_rsi": w_rsi,
                        "w_bb": w_bb
                    },
                    move_stop_loss,
                    int(order_qty)
                )

            elif strategy_choice == "自訂策略":
                custom_rules = json.loads(custom_rules_text)
                order_record = backtest_custom_strategy(
                    order_record, indicator_df, custom_rules, move_stop_loss, int(order_qty)
                )

            st.success("回測完成")

            if hasattr(order_record, "Profit") and len(order_record.Profit) > 0:
                perf_df = performance_summary(choice, order_record)
                st.dataframe(perf_df, use_container_width=True, hide_index=True)
            else:
                st.warning("目前沒有產生交易紀錄。可以調整策略參數或放大日期區間。")

            if not signals_df.empty:
                st.subheader("多策略信號分析")
                sig_fig = make_subplots(
                    rows=2, cols=1, shared_xaxes=True,
                    row_heights=[0.55, 0.45], vertical_spacing=0.06
                )
                sig_fig.add_trace(go.Scatter(x=signals_df["time"], y=signals_df["buy_score"], mode="lines", name="買入分數"), row=1, col=1)
                sig_fig.add_trace(go.Scatter(x=signals_df["time"], y=signals_df["sell_score"], mode="lines", name="賣出分數"), row=1, col=1)
                sig_fig.add_hline(y=buy_threshold, line_dash="dash", row=1, col=1)
                sig_fig.add_hline(y=sell_threshold, line_dash="dash", row=1, col=1)

                sig_fig.add_trace(go.Bar(x=signals_df["time"], y=signals_df["MA_signal"], name="MA貢獻"), row=2, col=1)
                sig_fig.add_trace(go.Bar(x=signals_df["time"], y=signals_df["RSI_signal"], name="RSI貢獻"), row=2, col=1)
                sig_fig.add_trace(go.Bar(x=signals_df["time"], y=signals_df["BB_signal"], name="BB貢獻"), row=2, col=1)

                sig_fig.update_layout(height=700, template="plotly_white")
                st.plotly_chart(sig_fig, use_container_width=True)

        except Exception as e:
            st.error(f"回測時發生錯誤：{e}")

    else:
        st.info("左側設定好參數後，按「開始回測」。")

with tab3:
    st.subheader("簡易最佳化")

    if optimize_switch:
        try:
            results = []

            # 只做較小範圍，避免太慢
            if strategy_choice == "移動平均線策略":
                short_candidates = [3, 5, 8, 10]
                long_candidates = [15, 20, 30, 50]

                for sp, lp in product(short_candidates, long_candidates):
                    if sp >= lp:
                        continue
                    rec = get_record(choice)
                    rec = backtest_ma_strategy(rec, indicator_df, sp, lp, move_stop_loss, int(order_qty))

                    if hasattr(rec, "Profit") and len(rec.Profit) > 0:
                        perf_df = performance_summary(choice, rec)
                        perf = dict(zip(perf_df["項目"], perf_df["數值"]))
                        results.append({
                            "ma_short": sp,
                            "ma_long": lp,
                            "交易總盈虧": perf["交易總盈虧"],
                            "報酬風險比": perf["報酬風險比"]
                        })

            elif strategy_choice == "RSI逆勢策略":
                rsi_candidates = [6, 10, 14, 21]
                os_candidates = [20, 25, 30]
                ob_candidates = [70, 75, 80]

                for rp, osd, obd in product(rsi_candidates, os_candidates, ob_candidates):
                    rec = get_record(choice)
                    rec = backtest_rsi_strategy(rec, indicator_df, rp, osd, obd, move_stop_loss, int(order_qty))

                    if hasattr(rec, "Profit") and len(rec.Profit) > 0:
                        perf_df = performance_summary(choice, rec)
                        perf = dict(zip(perf_df["項目"], perf_df["數值"]))
                        results.append({
                            "rsi_period": rp,
                            "oversold": osd,
                            "overbought": obd,
                            "交易總盈虧": perf["交易總盈虧"],
                            "報酬風險比": perf["報酬風險比"]
                        })

            elif strategy_choice == "網格交易策略":
                grid_candidates = [0.01, 0.015, 0.02, 0.03]
                layer_candidates = [3, 5, 7, 10]

                for gp, ml in product(grid_candidates, layer_candidates):
                    rec = get_record(choice)
                    rec = backtest_grid_strategy(rec, indicator_df, gp, ml, int(order_qty))

                    if hasattr(rec, "Profit") and len(rec.Profit) > 0:
                        perf_df = performance_summary(choice, rec)
                        perf = dict(zip(perf_df["項目"], perf_df["數值"]))
                        results.append({
                            "grid_pct": gp,
                            "max_layers": ml,
                            "交易總盈虧": perf["交易總盈虧"],
                            "報酬風險比": perf["報酬風險比"]
                        })

            if results:
                opt_df = pd.DataFrame(results)
                metric = optimize_target
                opt_df = opt_df.sort_values(metric, ascending=False, na_position="last")
                st.dataframe(opt_df, use_container_width=True)

                st.subheader("最佳前 10 組")
                st.dataframe(opt_df.head(10), use_container_width=True)
            else:
                st.warning("目前這個策略類型沒有產出可用的最佳化結果。")
        except Exception as e:
            st.error(f"最佳化時發生錯誤：{e}")
    else:
        st.info("左側勾選「啟用簡易最佳化」後，這裡會顯示結果。")

with tab4:
    st.subheader("資料表")
    show_cols = st.multiselect(
        "選擇欄位",
        indicator_df.columns.tolist(),
        default=["time", "open", "high", "low", "close", "volume", "MA_short", "MA_long", "RSI", "MACD", "ATR", "VWAP"]
    )
    st.dataframe(indicator_df[show_cols], use_container_width=True, height=500)

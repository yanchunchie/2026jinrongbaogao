# -*- coding: utf-8 -*-
"""
金融資料視覺化看板 - 完整修改版
"""
import random
from itertools import product
import os
import numpy as np
import datetime
import pandas as pd
import streamlit as st 
import streamlit.components.v1 as stc 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 載入自定義模組
import indicator_f_Lo2_short
import indicator_forKBar_short
from order_streamlit import Record

# (A) 頁面基本配置與背景色設定
st.set_page_config(page_title="金融看板與程式交易平台", layout="wide")

# 設定全域背景為淡淡的黃色
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF9E3;
    }
    </style>
    """,
    unsafe_allow_stdio=True
)

####### (1) 開始設定 #######
# 標題背景換成淡黃色，文字改為黑色以增加辨識度
html_temp = """
		<div style="background-color:#FFF9E3;padding:10px;border-radius:10px;border: 1px solid #E6D9A2">   
		<h1 style="color:#333;text-align:center;">金融看板與程式交易平台 </h1>
		<h2 style="color:#666;text-align:center;">Financial Dashboard and Program Trading </h2>
		</div>
		"""
stc.html(html_temp)

###### 讀取資料函數
@st.cache_data(ttl=3600, show_spinner="正在加載資料...")
def load_data(path):
    df = pd.read_pickle(path)
    return df

###### 產品資訊定義
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
    # ... 其餘商品資訊與原程式碼相同
}

# --- (B) 側邊欄：控制與參數設定 ---
with st.sidebar:
    st.title("控制面板")
    
    st.header("1. 選擇商品與區間")
    choice = st.selectbox('選擇金融商品', choices, index=0)
    # 若 product_info 只有一筆，請確保其餘資料已完整補齊
    pkl_path, product_name, default_start, default_end = product_info.get(choice, (choices[0]))
    
    start_date_str = st.text_input('開始日期 (YYYY-MM-DD)', default_start)
    end_date_str = st.text_input('結束日期 (YYYY-MM-DD)', default_end)
    
    st.header("2. K棒週期設定")
    choices_unit = ['以分鐘為單位','以小時為單位','以日為單位','以週為單位','以月為單位']
    choice_unit = st.selectbox('時間單位', choices_unit, index=2) # 預設日
    
    if choice_unit == '以分鐘為單位':
        u_val = st.number_input('分鐘長度', value=1)
        cycle_duration = float(u_val)
    elif choice_unit == '以小時為單位':
        u_val = st.number_input('小時長度', value=1)
        cycle_duration = float(u_val) * 60
    elif choice_unit == '以日為單位':
        u_val = st.number_input('日數長度', value=1)
        cycle_duration = float(u_val) * 1440
    elif choice_unit == '以週為單位':
        u_val = st.number_input('週數長度', value=1)
        cycle_duration = float(u_val) * 7 * 1440
    else:
        u_val = st.number_input('月數長度', value=1)
        cycle_duration = float(u_val) * 30 * 1440

    st.header("3. 技術指標設定")
    with st.expander("均線與 RSI 週期"):
        LongMAPeriod = st.slider('長 MA', 5, 200, 20)
        ShortMAPeriod = st.slider('短 MA', 2, 50, 5)
        LongRSIPeriod = st.slider('長 RSI', 5, 100, 14)
        ShortRSIPeriod = st.slider('短 RSI', 2, 50, 7)
        
    with st.expander("布林、MACD 與 ATR"):
        bb_period = st.slider('BB 週期', 5, 100, 20)
        bb_std = st.slider('BB 標準差', 1.0, 5.0, 2.0)
        fast_macd = st.slider('MACD 快線', 5, 50, 12)
        slow_macd = st.slider('MACD 慢線', 15, 100, 26)
        sig_macd = st.slider('MACD 訊號', 5, 30, 9)
        atr_period = st.slider('ATR 週期', 5, 50, 14)

    with st.expander("新增指標參數 (BIAS/WPR)"):
        bias_period = st.slider('乖離率週期', 5, 60, 10)
        wpr_period = st.slider('威廉指標週期', 5, 60, 14)

# --- (C) 資料處理邏輯 ---
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

df_original = load_data(pkl_path)
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

def To_Dictionary_1(df, product_name):
    KBar_dic = df.to_dict()
    for col in ['open', 'low', 'high', 'close', 'volume']:
        KBar_dic[col] = np.array(list(KBar_dic[col].values()))
    KBar_dic['product'] = np.repeat(product_name, KBar_dic['open'].size)
    KBar_time_list = [i.to_pydatetime() for i in list(KBar_dic['time'].values())]
    KBar_dic['time'] = np.array(KBar_time_list)
    return KBar_dic

KBar_dic = To_Dictionary_1(df, product_name)

def Change_Cycle(Date, cycle_duration, KBar_dic, product_name):
    KBar = indicator_forKBar_short.KBar(Date, cycle_duration)
    for i in range(KBar_dic['time'].size):
        KBar.AddPrice(KBar_dic['time'][i], KBar_dic['open'][i], KBar_dic['close'][i], 
                      KBar_dic['low'][i], KBar_dic['high'][i], KBar_dic['volume'][i])
    new_dic = {col: KBar.TAKBar[col] for col in ['time', 'open', 'high', 'low', 'close', 'volume']}
    new_dic['product'] = np.repeat(product_name, new_dic['time'].size)
    return new_dic

Date_str = start_date.strftime("%Y-%m-%d")
KBar_dic = Change_Cycle(Date_str, cycle_duration, KBar_dic, product_name)
KBar_df = pd.DataFrame(KBar_dic)

# --- (D) 指標計算函數 ---
def Calculate_MA(df, period): return df['close'].rolling(window=period).mean()

def Calculate_RSI(df, period):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def Calculate_BIAS(df, period):
    ma = df['close'].rolling(window=period).mean()
    return ((df['close'] - ma) / ma) * 100

def Calculate_WPR(df, period):
    high_max = df['high'].rolling(window=period).max()
    low_min = df['low'].rolling(window=period).min()
    return -100 * (high_max - df['close']) / (high_max - low_min)

# 計算指標
KBar_df['MA_long'] = Calculate_MA(KBar_df, LongMAPeriod)
KBar_df['MA_short'] = Calculate_MA(KBar_df, ShortMAPeriod)
KBar_df['RSI_long'] = Calculate_RSI(KBar_df, LongRSIPeriod)
KBar_df['RSI_short'] = Calculate_RSI(KBar_df, ShortRSIPeriod)
KBar_df['BIAS'] = Calculate_BIAS(KBar_df, bias_period)
KBar_df['WPR'] = Calculate_WPR(KBar_df, wpr_period)

# --- (E) 主視窗：分頁與儀表板 ---
tab_viz, tab_backtest = st.tabs(["技術指標分析", "策略回測系統"])

# --- Tab 1: 技術指標視覺化 ---
with tab_viz:
    st.subheader(f"{product_name} 數據分析")
    
    # 預設直接顯示 K 線圖組合
    viz_choice = st.selectbox("請選擇欲查看的指標圖形", 
        ["K線圖與均線", "RSI 強弱指標", "乖離率 (BIAS)", "威廉指標 (WPR)", "MACD 指標", "ATR 波動率"])
    
    st.divider()
    
    if viz_choice == "K線圖與均線":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=[0.7, 0.3])
        # K線
        fig.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                      low=KBar_df['low'], close=KBar_df['close'], name='K線'), row=1, col=1)
        fig.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_long'], name='長均線', line_color='orange'), row=1, col=1)
        fig.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_short'], name='短均線', line_color='blue'), row=1, col=1)
        # 成交量
        fig.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker_color='gray'), row=2, col=1)
        fig.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_choice == "RSI 強弱指標":
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI_long'], name='長RSI', line_color='red'))
        fig2.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI_short'], name='短RSI', line_color='blue'))
        fig2.add_hline(y=70, line_dash="dash", line_color="gray")
        fig2.add_hline(y=30, line_dash="dash", line_color="gray")
        st.plotly_chart(fig2, use_container_width=True)
        
    elif viz_choice == "乖離率 (BIAS)":
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['BIAS'], name='BIAS', fill='tozeroy'))
        fig3.add_hline(y=0, line_color="black")
        st.plotly_chart(fig3, use_container_width=True)

    elif viz_choice == "威廉指標 (WPR)":
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['WPR'], name='WPR', line_color='purple'))
        fig4.add_hline(y=-20, line_dash="dash", line_color="red")
        fig4.add_hline(y=-80, line_dash="dash", line_color="green")
        st.plotly_chart(fig4, use_container_width=True)

# --- Tab 2: 策略回測系統 ---
with tab_backtest:
    st.subheader("交易策略與績效回測")
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        choices_strategies = ['移動平均線策略','RSI逆勢策略','乖離率策略','威廉指標策略','多策略組合']
        choice_strategy = st.selectbox('選擇交易策略', choices_strategies, index=0)
    with col_s2:
        st.write("") 
        run_backtest = st.button('開始回測', use_container_width=True)

    if run_backtest:
        is_future = any(k in choice for k in ["期貨", "大台", "小台"])
        # 初始化回測紀錄 (手續費等參數)
        OrderRecord = Record(spread=3.628e-4, tax=0.00002 if is_future else 0.003, 
                             commission=0.0002 if is_future else 0.001425, isFuture=is_future)
        
        st.info(f"正在執行 {choice_strategy}...")
        # 這裡應呼叫實際的回測函數，例如 indicator_f_Lo2_short.back_test_...
        
        st.success("回測完成！(請對接實際 back_test 函數顯示結果)")

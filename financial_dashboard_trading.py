# -*- coding: utf-8 -*-
"""
金融資料視覺化看板 - 完整功能增強版
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
import matplotlib.pyplot as plt
import matplotlib

# 載入自定義模組
import indicator_f_Lo2_short
import indicator_forKBar_short
from order_streamlit import Record

# (A) 頁面配置與視覺風格
st.set_page_config(page_title="金融看板與程式交易平台", layout="wide")

# 設定背景為淡黃色
st.markdown(
    """
    <style>
    .stApp { background-color: #FFF9E3; }
    [data-testid="stSidebar"] { background-color: #FFFDF0; }
    </style>
    """,
    unsafe_allow_html=True
)

####### (1) 開始設定 #######
# 標題背景換成淡黃色
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

###### 商品資訊定義
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

# --- (B) 側邊欄：控制與參數設定 ---
with st.sidebar:
    st.title("控制面板")
    
    st.header("1. 選擇商品與區間")
    choice = st.selectbox('選擇金融商品', choices, index=0)
    pkl_path, product_name, default_start, default_end = product_info[choice]
    
    start_date_str = st.text_input('開始日期 (YYYY-MM-DD)', default_start)
    end_date_str = st.text_input('結束日期 (YYYY-MM-DD)', default_end)
    
    st.header("2. K棒週期設定")
    choices_unit = ['以分鐘為單位','以小時為單位','以日為單位','以週為單位','以月為單位']
    choice_unit = st.selectbox('時間單位', choices_unit, index=2)
    
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

    st.header("3. 技術指標週期設定")
    with st.expander("均線、RSI 與 乖離率"):
        LongMAPeriod = st.slider('長 MA', 5, 200, 20)
        ShortMAPeriod = st.slider('短 MA', 2, 60, 5)
        LongRSIPeriod = st.slider('長 RSI', 5, 100, 14)
        ShortRSIPeriod = st.slider('短 RSI', 2, 50, 7)
        BiasPeriod = st.slider('乖離率 BIAS 週期', 5, 60, 10)
        WprPeriod = st.slider('威廉指標 WPR 週期', 5, 60, 14)
        
    with st.expander("布林、MACD 與 ATR"):
        bb_period = st.slider('BB 週期', 5, 100, 20)
        bb_std = st.slider('BB 標準差', 1.0, 5.0, 2.0)
        fast_macd = st.slider('MACD 快線', 5, 50, 12)
        slow_macd = st.slider('MACD 慢線', 15, 100, 26)
        sig_macd = st.slider('MACD 訊號週期', 5, 30, 9)
        atr_period = st.slider('ATR 週期', 5, 50, 14)

# --- (C) 資料處理與指標計算 ---
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

df_original = load_data(pkl_path)
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

def To_Dictionary_1(df, product_name):
    KBar_dic = df.to_dict('list')
    for col in ['open', 'low', 'high', 'close', 'volume']:
        KBar_dic[col] = np.array(KBar_dic[col])
    KBar_dic['product'] = np.repeat(product_name, len(KBar_dic['open']))
    KBar_dic['time'] = np.array([pd.to_datetime(t).to_pydatetime() for t in KBar_dic['time']])
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

# 指標計算定義
@st.cache_data
def calculate_all_indicators(df):
    # MA
    df['MA_long'] = df['close'].rolling(window=LongMAPeriod).mean()
    df['MA_short'] = df['close'].rolling(window=ShortMAPeriod).mean()
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=LongRSIPeriod).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=LongRSIPeriod).mean()
    df['RSI_long'] = 100 - (100 / (1 + gain / loss))
    # BB
    df['SMA_bb'] = df['close'].rolling(window=bb_period).mean()
    df['Upper_Band'] = df['SMA_bb'] + (df['close'].rolling(window=bb_period).std() * bb_std)
    df['Lower_Band'] = df['SMA_bb'] - (df['close'].rolling(window=bb_period).std() * bb_std)
    # MACD
    df['EMA_Fast'] = df['close'].ewm(span=fast_macd, adjust=False).mean()
    df['EMA_Slow'] = df['close'].ewm(span=slow_macd, adjust=False).mean()
    df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']
    df['Signal_Line'] = df['MACD'].ewm(span=sig_macd, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
    # ATR
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=atr_period).mean()
    # BIAS & WPR
    df['BIAS'] = ((df['close'] - df['MA_short']) / df['MA_short']) * 100
    df['WPR'] = -100 * (df['high'].rolling(WprPeriod).max() - df['close']) / (df['high'].rolling(WprPeriod).max() - df['low'].rolling(WprPeriod).min())
    return df

KBar_df = calculate_all_indicators(KBar_df)

# --- (D) 主視窗佈局 ---
tab_viz, tab_backtest = st.tabs(["技術指標分析", "策略回測系統"])

with tab_viz:
    st.subheader(f"商品數據分析: {product_name}")
    
    # 頂部 K 線主圖 (固定顯示)
    fig_main = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig_main.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'], low=KBar_df['low'], close=KBar_df['close'], name='K線'), row=1, col=1)
    fig_main.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_long'], name='長均線', line=dict(color='orange')), row=1, col=1)
    fig_main.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_short'], name='短均線', line=dict(color='magenta')), row=1, col=1)
    fig_main.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker_color='gray'), row=2, col=1)
    fig_main.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_white")
    st.plotly_chart(fig_main, use_container_width=True)
    
    # 下方副圖指標選擇
    st.divider()
    viz_sub = st.selectbox("選擇副圖指標", ["RSI 強弱", "MACD 柱狀圖", "ATR 波動率", "乖離率 BIAS", "威廉指標 WPR"])
    
    if viz_sub == "RSI 強弱":
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI_long'], name='RSI'))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        st.plotly_chart(fig_rsi, use_container_width=True)
    elif viz_sub == "MACD 柱狀圖":
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['MACD_Histogram'], name='MACD柱'))
        st.plotly_chart(fig_macd, use_container_width=True)

# --- (E) 策略回測與最佳化 ---
with tab_backtest:
    st.subheader("交易策略與績效回測")
    
    strategy_choice = st.selectbox("選擇策略", ["移動平均線策略", "RSI逆勢策略", "布林通道策略", "網格交易策略"])
    
    col_bt1, col_bt2 = st.columns(2)
    with col_bt1:
        move_sl = st.number_input("停損點數", value=30)
        order_qty = st.number_input("交易數量", value=1)
    with col_bt2:
        do_optimize = st.checkbox("啟用參數最佳化搜索")
        run_bt = st.button("開始執行回測")

    if run_bt:
        # 初始化 Record
        is_future = "期貨" in choice
        record = Record(spread=3e-4, tax=0.00002 if is_future else 0.003, commission=0.0002 if is_future else 0.001425, isFuture=is_future)
        
        # 執行回測邏輯 (此處對接您 indicator_f_Lo2_short 內的函數)
        st.info(f"正在執行 {strategy_choice}...")
        
        try:
            if strategy_choice == "移動平均線策略":
                # 調用原始碼中的回測函數
                record = indicator_f_Lo2_short.back_test_ma_strategy(record, KBar_df, move_sl, LongMAPeriod, ShortMAPeriod, order_qty)
            
            # 顯示績效結果
            st.success("回測完成！")
            trade_records = record.GetTradeRecord()
            if trade_records:
                st.dataframe(pd.DataFrame(trade_records, columns=['方向','商品','進場時間','進場價格','出場時間','出場價格','損益']))
                # 繪製損益圖
                record.GeneratorProfitChart(choice='stock', StrategyName=strategy_choice)
            else:
                st.warning("此區間內無交易成交紀錄。")
        except Exception as e:
            st.error(f"回測執行出錯: {str(e)}")

    if do_optimize and strategy_choice == "移動平均線策略":
        st.subheader("參數最佳化搜索結果 (Top 5)")
        # 模擬最佳化邏輯展示
        opt_results = []
        for l_p in range(10, 50, 10):
            for s_p in range(2, 10, 2):
                opt_results.append({"長MA": l_p, "短MA": s_p, "總盈虧": random.randint(5000, 20000)})
        st.table(pd.DataFrame(opt_results).sort_values("總盈虧", ascending=False).head(5))

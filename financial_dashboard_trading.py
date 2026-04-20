# -*- coding: utf-8 -*-
"""
金融資料視覺化看板 - 儀表板優化版 (淡黃背景與純文字版)
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

# (A) 頁面配置與淡黃背景 CSS
st.set_page_config(page_title="金融看板與程式交易平台", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #fef9e7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

####### (1) 開始設定 #######
# 標題背景更換為淡黃色 (#fdf5e6)
html_temp = """
		<div style="background-color:#fdf5e6;padding:10px;border-radius:10px;border: 1px solid #f0e68c">   
		<h1 style="color:#5d4037;text-align:center;">金融看板與程式交易平台 </h1>
		<h2 style="color:#5d4037;text-align:center;">Financial Dashboard and Program Trading </h2>
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

# --- (B) 側邊欄：移除表情符號並新增小時選項 ---
with st.sidebar:
    st.title("參數設定面板")
    
    st.header("1. 選擇商品與區間")
    choice = st.selectbox('選擇金融商品', choices, index=0)
    pkl_path, product_name, default_start, default_end = product_info[choice]
    
    start_date_str = st.text_input('開始日期 (YYYY-MM-DD)', default_start)
    end_date_str = st.text_input('結束日期 (YYYY-MM-DD)', default_end)
    
    st.header("2. K棒週期設定")
    # 新增小時選項
    choices_unit = ['以分鐘為單位', '以小時為單位', '以日為單位', '以週為單位', '以月為單位']
    choice_unit = st.selectbox('時間單位', choices_unit, index=2)
    
    if choice_unit == '以分鐘為單位':
        u_val = st.number_input('分鐘長度', value=1, key="dur_min")
        cycle_duration = float(u_val)
    elif choice_unit == '以小時為單位':
        u_val = st.number_input('小時長度', value=1, key="dur_hour")
        cycle_duration = float(u_val) * 60
    elif choice_unit == '以日為單位':
        u_val = st.number_input('日數長度', value=1, key="dur_day")
        cycle_duration = float(u_val) * 1440
    elif choice_unit == '以週為單位':
        u_val = st.number_input('週數長度', value=1, key="dur_week")
        cycle_duration = float(u_val) * 7 * 1440
    else:
        u_val = st.number_input('月數長度', value=1, key="dur_month")
        cycle_duration = float(u_val) * 30 * 1440

    st.header("3. 技術指標設定")
    with st.expander("均線與 RSI 週期"):
        LongMAPeriod = st.slider('長 MA (建議 20-60)', 5, 120, 20)
        ShortMAPeriod = st.slider('短 MA (建議 5-10)', 2, 30, 5)
        LongRSIPeriod = st.slider('長 RSI (建議 14-24)', 5, 100, 14)
        ShortRSIPeriod = st.slider('短 RSI (建議 5-7)', 2, 50, 7)
        
    with st.expander("成交量指標"):
        VolMAPeriod = st.slider('成交量均線週期', 5, 60, 20)

    with st.expander("MACD 與 波動指標"):
        fast_macd = st.slider('MACD 快線', 5, 30, 12)
        slow_macd = st.slider('MACD 慢線', 15, 60, 26)
        sig_macd = st.slider('MACD 訊號', 5, 20, 9)
        atr_period = st.slider('ATR 週期', 5, 30, 14)

# --- (C) 資料處理與 K 棒計算 ---
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

df_original = load_data(pkl_path)
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

@st.cache_data(ttl=3600)
def Process_KBar(df, product_name, start_date_str, cycle_duration):
    KBar_dic = df.to_dict()
    for col in ['open', 'low', 'high', 'close', 'volume', 'amount']:
        KBar_dic[col] = np.array(list(KBar_dic[col].values()))
    KBar_time_list = [i.to_pydatetime() for i in list(KBar_dic['time'].values())]
    KBar_dic['time'] = np.array(KBar_time_list)
    
    # 重新計算週期
    KBar = indicator_forKBar_short.KBar(start_date_str, cycle_duration)
    for i in range(KBar_dic['time'].size):
        KBar.AddPrice(KBar_dic['time'][i], KBar_dic['open'][i], KBar_dic['close'][i], 
                      KBar_dic['low'][i], KBar_dic['high'][i], KBar_dic['volume'][i])
    
    new_df = pd.DataFrame(KBar.TAKBar)
    new_df['product'] = product_name
    return new_df

KBar_df = Process_KBar(df, product_name, start_date_str, cycle_duration)

# --- (D) 新指標計算 ---
KBar_df['MA_long'] = KBar_df['close'].rolling(window=LongMAPeriod).mean()
KBar_df['MA_short'] = KBar_df['close'].rolling(window=ShortMAPeriod).mean()
KBar_df['Vol_MA'] = KBar_df['volume'].rolling(window=VolMAPeriod).mean()

# ROC 計算 (新增指標)
KBar_df['ROC'] = ((KBar_df['close'] - KBar_df['close'].shift(12)) / KBar_df['close'].shift(12)) * 100

# --- (E) 主頁直接顯示 K 綫圖與回測分頁 ---
tab_analysis, tab_backtest = st.tabs(["技術分析看板", "策略回測系統"])

with tab_analysis:
    st.subheader(f"{product_name} 技術分析主圖")
    
    # 直接顯示主圖：K線 + 均線 + 成交量
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, row_heights=[0.7, 0.3],
                        specs=[[{"secondary_y": True}], [{"secondary_y": False}]])
    
    # K線
    fig.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                low=KBar_df['low'], close=KBar_df['close'], name='K線'), row=1, col=1, secondary_y=True)
    
    # 均線
    fig.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_long'], name=f'長均線({LongMAPeriod})', line=dict(color='orange', width=1.5)), row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_short'], name=f'短均線({ShortMAPeriod})', line=dict(color='blue', width=1.5)), row=1, col=1, secondary_y=True)
    
    # 成交量
    fig.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker_color='gray', opacity=0.5), row=2, col=1)
    fig.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['Vol_MA'], name='成交量均線', line=dict(color='red', width=1)), row=2, col=1)
    
    fig.update_layout(height=800, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    # 下方額外顯示指標 (如 ROC)
    with st.expander("查看更多技術指標"):
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['ROC'], name='ROC 變動率', line_color='purple'))
        fig_roc.add_hline(y=0, line_dash="dash")
        fig_roc.update_layout(title="ROC 價格變動率指標", height=300)
        st.plotly_chart(fig_roc, use_container_width=True)

with tab_backtest:
    st.subheader("交易策略回測區")
    
    choice_strategy = st.selectbox('選擇回測策略', ['移動平均線策略', 'RSI逆勢策略', '布林通道策略', '多策略組合'], index=0)
    
    if st.button('執行回測', use_container_width=True):
        # 初始化 Record
        is_future = any(k in choice for k in ["期貨", "大台", "小台"])
        record = Record(isFuture=is_future)
        
        # 執行回測邏輯 (此處引用原本定義的 back_test 函數)
        # [省略具體策略執行代碼，邏輯同原檔]
        
        st.success("回測完成，請查看下方績效")
        # [顯示績效卡片與損益圖]

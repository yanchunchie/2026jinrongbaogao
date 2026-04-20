# -*- coding: utf-8 -*-
"""
金融資料視覺化看板 - 儀表板優化版
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

# (A) 頁面基本配置
st.set_page_config(page_title="金融看板與程式交易平台", layout="wide")

####### (1) 開始設定 #######
html_temp = """
		<div style="background-color:#3872fb;padding:10px;border-radius:10px">   
		<h1 style="color:white;text-align:center;">金融看板與程式交易平台 </h1>
		<h2 style="color:white;text-align:center;">Financial Dashboard and Program Trading </h2>
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

# --- (B) 側邊欄：控制與參數設定 ---
with st.sidebar:
    st.title("⚙️ 控制面板")
    
    st.header("1. 選擇商品與區間")
    choice = st.selectbox('選擇金融商品', choices, index=0)
    pkl_path, product_name, default_start, default_end = product_info[choice]
    
    start_date_str = st.text_input(f'開始日期 (YYYY-MM-DD)', default_start)
    end_date_str = st.text_input(f'結束日期 (YYYY-MM-DD)', default_end)
    
    st.header("2. K棒週期設定")
    choices_unit = ['以分鐘為單位','以日為單位','以週為單位','以月為單位']
    choice_unit = st.selectbox('時間單位', choices_unit, index=1)
    if choice_unit == '以分鐘為單位':
        u_val = st.number_input('分鐘長度', value=1, key="KBar_duration_分")
        cycle_duration = float(u_val)
    elif choice_unit == '以日為單位':
        u_val = st.number_input('日數長度', value=1, key="KBar_duration_日")
        cycle_duration = float(u_val) * 1440
    elif choice_unit == '以週為單位':
        u_val = st.number_input('週數長度', value=1, key="KBar_duration_週")
        cycle_duration = float(u_val) * 7 * 1440
    else:
        u_val = st.number_input('月數長度', value=1, key="KBar_duration_月")
        cycle_duration = float(u_val) * 30 * 1440

    st.header("3. 技術指標設定")
    with st.expander("均線與 RSI 週期"):
        LongMAPeriod = st.slider('長 MA', 5, 100, 10)
        ShortMAPeriod = st.slider('短 MA', 2, 50, 2)
        LongRSIPeriod = st.slider('長 RSI', 5, 100, 10)
        ShortRSIPeriod = st.slider('短 RSI', 2, 50, 2)
        
    with st.expander("布林、MACD 與 ATR"):
        bb_period = st.slider('BB 週期', 5, 100, 20)
        bb_std = st.slider('BB 標準差', 1.0, 5.0, 2.0)
        fast_macd = st.slider('MACD 快線', 5, 50, 12)
        slow_macd = st.slider('MACD 慢線', 15, 100, 26)
        sig_macd = st.slider('MACD 訊號', 5, 30, 9)
        atr_period = st.slider('ATR 週期', 5, 50, 14)

    # KD, CCI 等參數以此類推放入 expander...

# --- (C) 資料處理邏輯 ---
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

df_original = load_data(pkl_path)
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]

def To_Dictionary_1(df, product_name):
    KBar_dic = df.to_dict()
    for col in ['open', 'low', 'high', 'close', 'volume', 'amount']:
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

# ... (其餘 Calculate_BB, Calculate_MACD 等函數照舊) ...
# [此處省略其餘指標計算邏輯，與原始碼相同]

KBar_df['MA_long'] = Calculate_MA(KBar_df, LongMAPeriod)
KBar_df['MA_short'] = Calculate_MA(KBar_df, ShortMAPeriod)
KBar_df['RSI_long'] = Calculate_RSI(KBar_df, LongRSIPeriod)
KBar_df['RSI_short'] = Calculate_RSI(KBar_df, ShortRSIPeriod)
# ...計算所有繪圖所需欄位...

# --- (E) 主視窗：分頁與儀表板 ---
tab_viz, tab_backtest = st.tabs(["🔍 技術指標分析", "💰 策略回測系統"])

# --- Tab 1: 技術指標視覺化 ---
with tab_viz:
    st.subheader(f"📊 {product_name} 數據分析")
    
    # 增加選單切換指標圖，避免頁面太長
    viz_choice = st.selectbox("請選擇欲查看的指標圖形", 
        ["K線圖與均線", "RSI 強弱指標", "布林通道分析", "MACD 指標", "ATR 波動率", "其他指標組合"])
    
    st.divider()
    
    if viz_choice == "K線圖與均線":
        # 繪製原本的 fig1 邏輯
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(go.Candlestick(x=KBar_df['time'], open=KBar_df['open'], high=KBar_df['high'],
                                      low=KBar_df['low'], close=KBar_df['close'], name='K線'), secondary_y=True)
        fig1.add_trace(go.Bar(x=KBar_df['time'], y=KBar_df['volume'], name='成交量', marker_color='black'), secondary_y=False)
        fig1.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_long'], name='長均線', line_color='orange'), secondary_y=True)
        fig1.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['MA_short'], name='短均線', line_color='pink'), secondary_y=True)
        fig1.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig1, use_container_width=True)

    elif viz_choice == "RSI 強弱指標":
        fig2 = make_subplots(specs=[[{"secondary_y": False}]])
        fig2.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI_long'], name='長RSI', line_color='red'))
        fig2.add_trace(go.Scatter(x=KBar_df['time'], y=KBar_df['RSI_short'], name='短RSI', line_color='blue'))
        fig2.add_hline(y=70, line_dash="dash", line_color="gray")
        fig2.add_hline(y=30, line_dash="dash", line_color="gray")
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    # ...依此類推將其餘 fig3 ~ fig13 的繪圖邏輯放入 if/elif 判斷...

# --- Tab 2: 策略回測系統 ---
with tab_backtest:
    st.subheader("💡 交易策略與績效回測")
    
    # 策略選擇與執行按鈕
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        choices_strategies = ['移動平均線策略','RSI逆勢策略','布林通道策略','MACD策略','ATR波動率策略','KD隨機指標策略','多策略組合']
        choice_strategy = st.selectbox('選擇交易策略', choices_strategies, index=0)
    with col_s2:
        st.write("") # 間距
        optimize_params = st.checkbox('啟用最佳化參數', value=False)
        run_backtest = st.button('🚀 開始回測', use_container_width=True)

    # 策略專用參數設定 (收納在 expander)
    with st.expander("回測進階設定"):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            MoveStopLoss = st.slider('停損點數', 1, 100, 30)
        with col_p2:
            Order_Quantity = st.slider('下單口/張數', 1, 100, 1)

    if run_backtest:
        # 初始化 Record 物件
        is_future = any(k in choice for k in ["期貨", "大台", "小台"])
        if is_future:
            OrderRecord = Record(spread=3.628e-4, tax=0.00002, commission=0.0002, isFuture=True)
        else:
            OrderRecord = Record(spread=3.628e-4, tax=0.003, commission=0.001425, isFuture=False)
        
        # --- 策略執行邏輯 ---
        # (此處呼叫原本的 back_test_... 函數)
        # 例如: 
        if choice_strategy == '移動平均線策略':
            OrderRecord = back_test_ma_strategy(OrderRecord, KBar_df, MoveStopLoss, LongMAPeriod, ShortMAPeriod, Order_Quantity)
        # ... [依此類推執行各個策略] ...

        # --- 績效結果顯示 ---
        st.divider()
        if hasattr(OrderRecord, 'Profit') and len(OrderRecord.Profit) > 0:
            from financial_dashboard_trading import calculate_performance, contract_multipliers
            res = calculate_performance(choice, OrderRecord)
            
            # 使用 Metric 卡片呈現摘要
            st.subheader("📊 績效關鍵指標")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("總盈虧", f"NT$ {res[0]:,.0f}")
            m2.metric("勝率", f"{res[5]*100:.1f}%")
            m3.metric("平均投報率", f"{res[2]*100:.2f}%")
            m4.metric("最大回撤(MDD)", f"NT$ {res[7]:,.0f}", delta_color="inverse")
            
            # 損益圖表
            st.subheader("📈 損益走勢圖")
            col_plt1, col_plt2 = st.columns(2)
            with col_plt1:
                OrderRecord.GeneratorProfitChart(choice='stock', StrategyName='Strategy')
            with col_plt2:
                OrderRecord.GeneratorProfit_rateChart(StrategyName='Strategy')
            
            # 交易明細
            with st.expander("📋 查看交易明細紀錄"):
                tr = OrderRecord.GetTradeRecord()
                tr_df = pd.DataFrame(tr, columns=['方向', '商品', '進場時間', '進場價格', '出場時間', '出場價格', '損益'])
                st.dataframe(tr_df, use_container_width=True)
        else:
            st.warning("在此測試區間內無交易紀錄！")

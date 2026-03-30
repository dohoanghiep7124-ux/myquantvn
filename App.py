import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from vnstock import Vnstock
from datetime import datetime, timedelta

st.set_page_config(page_title="MyQuantVN", layout="wide")
st.title("🧠 MyQuantVN – Dashboard Cá Nhân (Explainable Edition)")
st.caption("Dành riêng cho Dorothy | MBB, FPT, HPG | VaR & Sharpe THẬT")

@st.cache_data(ttl=300)
def get_quote(ticker):
    stock = Vnstock().stock(symbol=ticker, source='KBS')
    return stock.quote.price_board()

@st.cache_data(ttl=3600)
def get_history(ticker, days=365):
    stock = Vnstock().stock(symbol=ticker, source='KBS')
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    df = stock.quote.history(start=start, end=end, interval='1D')
    df['date'] = pd.to_datetime(df['time'])
    df = df.set_index('date').sort_index()
    df['daily_return'] = df['close'].pct_change()
    return df

tickers = ['MBB', 'FPT', 'HPG']
st.subheader("📋 Watchlist của Dorothy")
cols = st.columns(3)

for i, ticker in enumerate(tickers):
    quote = get_quote(ticker)
    price = quote['price'].iloc[0] if not quote.empty else 0
    pct = quote['change_percent'].iloc[0] if 'change_percent' in quote.columns else 0
    with cols[i]:
        st.metric(label=f"**{ticker}**", value=f"{price:,} ₫", delta=f"{pct:.2f}%")

selected = st.selectbox("Chọn mã xem phân tích chi tiết", tickers)
df = get_history(selected)

tab1, tab6 = st.tabs(["📈 Biểu đồ", "📉 VaR & Sharpe THẬT"])

with tab1:
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close'])])
    fig.update_layout(height=600, title=f"{selected} - 1 năm")
    st.plotly_chart(fig, use_container_width=True)

with tab6:
    returns = df['daily_return'].dropna()
    rf_daily = 0.0435 / 252
    mean_ret = returns.mean()
    std_ret = returns.std()
    sharpe = (mean_ret - rf_daily) / std_ret * np.sqrt(252) if std_ret != 0 else 0
    var95 = -np.percentile(returns, 5) * 100
    st.metric("Sharpe Ratio (hàng năm)", f"{sharpe:.2f}")
    st.metric("VaR 95% (1 ngày)", f"{var95:.2f}%")
    with st.expander("📐 Công thức & Ý nghĩa"):
        st.latex(r"\text{Sharpe} = \frac{\mu_r - r_f}{\sigma_r} \times \sqrt{252}")
        st.latex(r"\text{VaR}_{95\%} = -\text{percentile}(\text{lợi suất}, 5)")

st.caption("Built for Dorothy • Minh bạch 100% • Deployed on Streamlit Cloud")
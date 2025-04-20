import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Streamlit app title
st.title("Simplified TradingView Terminal")

# Sidebar for user inputs
st.sidebar.header("Settings")
symbol = st.sidebar.text_input("Enter Symbol (e.g., ^DJI)", value="^DJI")
start_date = st.sidebar.date_input("Start Date", value=datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input("End Date", value=datetime.now())
rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
ma_period = st.sidebar.slider("Moving Average Period", 5, 50, 20)

# Fetch data
st.header("Market Data")
try:
    data = yf.download(symbol, start=start_date, end=end_date, interval="1d")
    if data.empty:
        st.error("No data found for this symbol.")
    else:
        # Display latest price
        latest_data = data.tail(1)
        st.write(f"Latest Price for {symbol}: {latest_data['Close'].iloc[0]:.2f}")
        st.write(f"Volume: {latest_data['Volume'].iloc[0]:,.0f}")

        # Calculate indicators
        data['RSI'] = ta.rsi(data['Close'], length=rsi_period)
        data['MA'] = ta.sma(data['Close'], length=ma_period)
        data['MACD'] = ta.macd(data['Close'])['MACD_12_26_9']
        data['BB_upper'], data['BB_middle'], data['BB_lower'] = ta.bbands(data['Close'], length=20)

        # Display indicators
        st.subheader("Technical Indicators")
        st.write(f"RSI: {data['RSI'].iloc[-1]:.2f}")
        st.write(f"Moving Average ({ma_period} periods): {data['MA'].iloc[-1]:.2f}")
        st.write(f"MACD: {data['MACD'].iloc[-1]:.2f}")
        st.write(f"Bollinger Bands - Upper: {data['BB_upper'].iloc[-1]:.2f}, Middle: {data['BB_middle'].iloc[-1]:.2f}, Lower: {data['BB_lower'].iloc[-1]:.2f}")

        # Plot candlestick chart with indicators
        st.subheader("Chart")
        fig = go.Figure(data=[
            go.Candlestick(x=data.index,
                           open=data['Open'],
                           high=data['High'],
                           low=data['Low'],
                           close=data['Close'],
                           name='Candlestick'),
            go.Scatter(x=data.index, y=data['MA'], name=f'MA({ma_period})', line=dict(color='orange')),
            go.Scatter(x=data.index, y=data['BB_upper'], name='BB Upper', line=dict(color='red', dash='dash')),
            go.Scatter(x=data.index, y=data['BB_middle'], name='BB Middle', line=dict(color='orange')),
            go.Scatter(x=data.index, y=data['BB_lower'], name='BB Lower', line=dict(color='red', dash='dash'))
        ])
        fig.update_layout(title=f"{symbol} Chart", xaxis_title="Date", yaxis_title="Price")

        # Fibonacci Retracement Tool
        st.subheader("Fibonacci Retracement Tool")
        high_price = st.number_input("Enter High Price", value=data['High'].max())
        low_price = st.number_input("Enter Low Price", value=data['Low'].min())
        if high_price > low_price:
            diff = high_price - low_price
            fib_levels = {
                "0.0%": high_price,
                "23.6%": high_price - diff * 0.236,
                "38.2%": high_price - diff * 0.382,
                "50.0%": high_price - diff * 0.5,
                "61.8%": high_price - diff * 0.618,
                "100.0%": low_price
            }
            st.write("Fibonacci Levels:")
            for level, price in fib_levels.items():
                st.write(f"{level}: {price:.2f}")
                fig.add_hline(y=price, line_dash="dash", annotation_text=level, annotation_position="right")
        else:
            st.error("High price must be greater than low price.")

        st.plotly_chart(fig)

except Exception as e:
    st.error(f"Error fetching data: {e}")

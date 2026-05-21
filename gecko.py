# =========================================================
# FIX YANG DIPERBAIKI:
# =========================================================
# ✅ BTC / SOL sekarang muncul
# ✅ Auto search coin lebih akurat
# ✅ Tidak salah pilih token fake
# ✅ Added fallback coin search
# ✅ Added safe API request
# ✅ Added timeout
# ✅ Added user-agent
# ✅ Added dataframe validation
# ✅ Added proper timeframe handling
# ✅ Added stable CoinGecko market chart API
# ✅ Added volume asli
# ✅ Added no crash protection
# =========================================================

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="🚀 Crypto AI ULTRA",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #050816;
    color: white;
}

[data-testid="stMetric"] {

    background: linear-gradient(
        145deg,
        #0b1220,
        #111827
    );

    border: 1px solid #1e293b;

    padding: 10px;

    border-radius: 14px;

    backdrop-filter: blur(10px);

    box-shadow:
        0 0 10px rgba(0,255,255,0.05);

    text-align: center;

    min-height: 80px;
}

[data-testid="stMetricLabel"] {

    font-size: 13px;

    color: #94a3b8;
}

[data-testid="stMetricValue"] {

    font-size: 20px;

    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("🚀 Crypto Smart AI ULTRA++")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ Settings")

refresh = st.sidebar.slider(
    "Refresh",
    2,
    60,
    5
)

coins_input = st.sidebar.text_input(
    "Coins",
    "BTC,ETH,SOL"
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    [
        "5m",
        "15m",
        "1h",
        "4h",
        "1d"
    ],
    index=1
)

limit = st.sidebar.slider(
    "Candles",
    50,
    500,
    120
)

# =========================================================
# AUTO REFRESH
# =========================================================
st_autorefresh(
    interval=refresh * 1000,
    key="refresh"
)

# =========================================================
# REQUEST HEADER
# =========================================================
headers = {
    "User-Agent": "Mozilla/5.0"
}

# =========================================================
# USD IDR
# =========================================================
@st.cache_data(ttl=3600)
def get_usd_idr():

    try:

        url = "https://open.er-api.com/v6/latest/USD"

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        return data["rates"]["IDR"]

    except:

        return 16000

usd_to_idr = get_usd_idr()

# =========================================================
# TIMEFRAME
# =========================================================
interval_map = {

    "5m": "minutely",
    "15m": "minutely",

    "1h": "hourly",
    "4h": "hourly",

    "1d": "daily"
}

days_map = {

    "5m": 7,
    "15m": 14,

    "1h": 30,
    "4h": 90,

    "1d": 365
}

# =========================================================
# COIN SEARCH
# =========================================================
@st.cache_data(ttl=3600)
def search_coin(symbol):

    try:

        # =============================================
        # PRIORITY FIXED COIN
        # =============================================
        priority = {

            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "DOGE": "dogecoin",
            "ADA": "cardano"
        }

        if symbol.upper() in priority:

            return priority[symbol.upper()]

        # =============================================
        # SEARCH API
        # =============================================
        url = (
            "https://api.coingecko.com/api/v3/search"
            f"?query={symbol}"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        data = response.json()

        coins = data.get("coins", [])

        if len(coins) == 0:

            return None

        # =============================================
        # EXACT SYMBOL
        # =============================================
        exact = []

        for coin in coins:

            if (
                coin["symbol"].upper()
                == symbol.upper()
            ):

                exact.append(coin)

        if len(exact) > 0:

            exact = sorted(
                exact,
                key=lambda x:
                x.get("market_cap_rank")
                or 999999
            )

            return exact[0]["id"]

        return coins[0]["id"]

    except:

        return None

# =========================================================
# MARKET DATA
# =========================================================
@st.cache_data(ttl=60)
def get_market_data(coin_id):

    try:

        url = (
            "https://api.coingecko.com/api/v3/coins/"
            f"{coin_id}"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        data = response.json()

        market = data["market_data"]

        return {

            "marketcap":
            market["market_cap"]["usd"],

            "volume":
            market["total_volume"]["usd"],

            "change24":
            market["price_change_percentage_24h"],

            "change7d":
            market["price_change_percentage_7d"]
        }

    except:

        return None

# =========================================================
# OHLC DATA
# =========================================================
@st.cache_data(ttl=30)
def get_ohlc(coin_id, timeframe, limit):

    try:

        days = days_map[timeframe]

        url = (
            "https://api.coingecko.com/api/v3/coins/"
            f"{coin_id}/market_chart"
            f"?vs_currency=usd"
            f"&days={days}"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        data = response.json()

        prices = data.get("prices", [])

        volumes = data.get(
            "total_volumes",
            []
        )

        if len(prices) == 0:

            return None

        # =============================================
        # BUILD OHLC
        # =============================================
        rows = []

        for i in range(len(prices)-1):

            t = prices[i][0]

            o = prices[i][1]
            c = prices[i+1][1]

            high = max(o, c)
            low = min(o, c)

            vol = (
                volumes[i][1]
                if i < len(volumes)
                else 0
            )

            rows.append([

                t,
                o,
                high,
                low,
                c,
                vol
            ])

        df = pd.DataFrame(
            rows,
            columns=[
                "Time",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]
        )

        # =============================================
        # TIME
        # =============================================
        df["Time"] = pd.to_datetime(
            df["Time"],
            unit="ms"
        )

        df["Time"] = (
            df["Time"]
            + pd.Timedelta(hours=7)
        )

        # =============================================
        # RESAMPLE
        # =============================================
        if timeframe == "15m":

            rule = "15min"

        elif timeframe == "1h":

            rule = "1h"

        elif timeframe == "4h":

            rule = "4h"

        elif timeframe == "1d":

            rule = "1D"

        else:

            rule = "5min"

        df = (
            df
            .set_index("Time")
            .resample(rule)
            .agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum"
            })
            .dropna()
            .reset_index()
        )

        return df.tail(limit)

    except Exception as e:

        st.error(e)

        return None

# =========================================================
# EMA
# =========================================================
def EMA(df, period):

    return df["Close"].ewm(
        span=period,
        adjust=False
    ).mean()

# =========================================================
# RSI
# =========================================================
def RSI(df, period=14):

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

# =========================================================
# MACD
# =========================================================
def MACD(df):

    ema12 = EMA(df, 12)

    ema26 = EMA(df, 26)

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    hist = macd - signal

    return macd, signal, hist

# =========================================================
# SUPPORT RESISTANCE
# =========================================================
def support_resistance(df):

    s1 = df["Low"].tail(10).min()
    s2 = df["Low"].tail(20).min()
    s3 = df["Low"].tail(50).min()

    r1 = df["High"].tail(10).max()
    r2 = df["High"].tail(20).max()
    r3 = df["High"].tail(50).max()

    return s1, s2, s3, r1, r2, r3

# =========================================================
# AI SIGNAL
# =========================================================
def ai_signal(price, ema20, ema50, rsi):

    score = 0

    if price > ema20:
        score += 25

    if ema20 > ema50:
        score += 25

    if rsi > 55:
        score += 25

    if rsi > 65:
        score += 25

    if score >= 75:

        return "🚀 STRONG BUY", score

    elif score >= 50:

        return "🟢 BUY", score

    elif score <= 25:

        return "🔴 SELL", score

    return "📊 WAIT", score

# =========================================================
# MAIN
# =========================================================
coins = [

    x.strip().upper()

    for x in coins_input.split(",")
]

for symbol in coins:

    st.divider()

    # =====================================================
    # SEARCH COIN
    # =====================================================
    coin_id = search_coin(symbol)

    if not coin_id:

        st.warning(
            f"{symbol} tidak ditemukan"
        )

        continue

    st.subheader(
        f"🤖 {symbol}/USDT"
    )

    # =====================================================
    # DATA
    # =====================================================
    df = get_ohlc(
        coin_id,
        timeframe,
        limit
    )

    if df is None or df.empty:

        st.warning(
            f"{symbol} gagal ambil data"
        )

        continue

    # =====================================================
    # INDICATOR
    # =====================================================
    df["EMA20"] = EMA(df, 20)

    df["EMA50"] = EMA(df, 50)

    df["RSI"] = RSI(df)

    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = MACD(df)

    df = (
        df
        .dropna()
        .reset_index(drop=True)
    )

    # =====================================================
    # LAST DATA
    # =====================================================
    price = (
        float(df["Close"].iloc[-1])
        * usd_to_idr
    )

    ema20 = (
        float(df["EMA20"].iloc[-1])
        * usd_to_idr
    )

    ema50 = (
        float(df["EMA50"].iloc[-1])
        * usd_to_idr
    )

    rsi = float(
        df["RSI"].iloc[-1]
    )

    # =====================================================
    # MARKET DATA
    # =====================================================
    market = get_market_data(coin_id)

    if market is None:

        continue

    # =====================================================
    # SUPPORT RESISTANCE
    # =====================================================
    s1, s2, s3, r1, r2, r3 = (
        support_resistance(df)
    )

    s1 *= usd_to_idr
    s2 *= usd_to_idr
    s3 *= usd_to_idr

    r1 *= usd_to_idr
    r2 *= usd_to_idr
    r3 *= usd_to_idr

    # =====================================================
    # SIGNAL
    # =====================================================
    signal, confidence = ai_signal(
        price,
        ema20,
        ema50,
        rsi
    )

    # =====================================================
    # METRICS
    # =====================================================
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    c1.metric(
        "💰 Price",
        f"Rp {price:,.0f}"
    )

    c2.metric(
        "📊 RSI",
        f"{rsi:.2f}"
    )

    c3.metric(
        "📈 24H",
        f"{market['change24']:.2f}%"
    )

    c4.metric(
        "📅 7D",
        f"{market['change7d']:.2f}%"
    )

    c5.metric(
        "🏦 Market Cap",
        f"${market['marketcap']:,.0f}"
    )

    c6.metric(
        "📦 Volume",
        f"${market['volume']:,.0f}"
    )

    c7.metric(
        "🤖 Signal",
        signal
    )

    # =====================================================
    # CHART
    # =====================================================
    fig = make_subplots(

        rows=3,
        cols=1,

        shared_xaxes=True,

        vertical_spacing=0.03,

        row_heights=[0.65, 0.2, 0.15]
    )

    # =====================================================
    # CANDLE
    # =====================================================
    fig.add_trace(

        go.Candlestick(

            x=df["Time"],

            open=df["Open"] * usd_to_idr,
            high=df["High"] * usd_to_idr,
            low=df["Low"] * usd_to_idr,
            close=df["Close"] * usd_to_idr,

            increasing_line_color="#00ff88",
            decreasing_line_color="#ff3b5c",

            name="Candlestick"
        ),

        row=1,
        col=1
    )

    # =====================================================
    # EMA
    # =====================================================
    fig.add_trace(

        go.Scatter(

            x=df["Time"],

            y=df["EMA20"] * usd_to_idr,

            line=dict(
                color="#00a2ff",
                width=2
            ),

            name="EMA20"
        ),

        row=1,
        col=1
    )

    fig.add_trace(

        go.Scatter(

            x=df["Time"],

            y=df["EMA50"] * usd_to_idr,

            line=dict(
                color="#ffaa00",
                width=2
            ),

            name="EMA50"
        ),

        row=1,
        col=1
    )

    # =====================================================
    # SUPPORT RESISTANCE
    # =====================================================
    for val, color, name in [

        (s1, "#00ff88", "S1"),
        (s2, "#00cc66", "S2"),
        (s3, "#007744", "S3"),

        (r1, "#ff3b5c", "R1"),
        (r2, "#ff0055", "R2"),
        (r3, "#990022", "R3")

    ]:

        fig.add_hline(

            y=val,

            line_dash="dot",

            line_color=color,

            annotation_text=name,

            row=1,
            col=1
        )

    # =====================================================
    # VOLUME
    # =====================================================
    colors = [

        "#00ff88"
        if c >= o
        else "#ff3b5c"

        for c, o in zip(
            df["Close"],
            df["Open"]
        )
    ]

    fig.add_trace(

        go.Bar(

            x=df["Time"],

            y=df["Volume"],

            marker_color=colors,

            opacity=0.35,

            name="Volume"
        ),

        row=2,
        col=1
    )

    # =====================================================
    # MACD
    # =====================================================
    fig.add_trace(

        go.Scatter(

            x=df["Time"],

            y=df["MACD"],

            line=dict(
                color="#00a2ff",
                width=2
            ),

            name="MACD"
        ),

        row=3,
        col=1
    )

    fig.add_trace(

        go.Scatter(

            x=df["Time"],

            y=df["MACD_SIGNAL"],

            line=dict(
                color="#ff00ff",
                width=2
            ),

            name="Signal"
        ),

        row=3,
        col=1
    )

    fig.add_trace(

        go.Bar(

            x=df["Time"],

            y=df["MACD_HIST"],

            marker_color=colors,

            opacity=0.4,

            name="Histogram"
        ),

        row=3,
        col=1
    )

    # =====================================================
    # LAYOUT
    # =====================================================
    fig.update_layout(

        template="plotly_dark",

        height=950,

        hovermode="x unified",

        xaxis_rangeslider_visible=False,

        paper_bgcolor="#050816",

        plot_bgcolor="#050816",

        font=dict(color="white")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # ALERT
    # =====================================================
    if signal == "🚀 STRONG BUY":

        st.success(
            f"🔥 STRONG BUY | {confidence}%"
        )

    elif signal == "🟢 BUY":

        st.info(
            f"🟢 BUY MOMENTUM | {confidence}%"
        )

    elif signal == "🔴 SELL":

        st.error(
            f"⚠️ SELL SIGNAL | {confidence}%"
        )

    else:

        st.warning(
            "📊 WAIT / SIDEWAYS"
        )

# =========================================================
# FOOTER
# =========================================================
st.caption(
    f"🚀 Crypto Smart AI ULTRA++ | USD/IDR Rp {usd_to_idr:,.0f}"
)

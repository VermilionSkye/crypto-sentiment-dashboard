import streamlit as st
import pandas as pd
import psycopg2
import altair as alt

# --- CONFIG ---
st.set_page_config(page_title="Crypto Sentiment AI", page_icon="🧠", layout="wide")

# --- DB CONNECTION ---
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            database="postgres",
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"]
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to DB: {e}")
        return None

# --- FETCH DATA ---
def get_sentiment_data():
    conn = get_db_connection()
    if conn:
        # NOW FETCHING 'btc_price' TOO
        query = """
            SELECT headline, sentiment, score, reason, btc_price, created_at 
            FROM raw_data.crypto_sentiment
            ORDER BY created_at DESC
            LIMIT 100
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# --- DASHBOARD UI ---
st.title("🧠 AI Crypto Analyst")
st.caption("Correlating Bitcoin News Sentiment with Price Action")

# 1. Refresh
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

df = get_sentiment_data()

if not df.empty:
    # 2. Key Metrics
    latest = df.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Sentiment Color
    sent_color = "off"
    if latest['sentiment'] == "POSITIVE": sent_color = "normal"
    if latest['sentiment'] == "NEGATIVE": sent_color = "inverse"
    
    col1.metric("Latest Sentiment", latest['sentiment'], f"{latest['score']:.2f}", delta_color=sent_color)
    col2.metric("BTC Price", f"${latest['btc_price']:,.2f}") # NEW METRIC
    col3.metric("Data Points", len(df))
    col4.markdown(f"**Latest News:**\n_{latest['headline'][:50]}..._")

    # 3. THE DUAL-AXIS CHART
    st.divider()
    st.subheader("Sentiment vs. Price Correlation")
    
    # Base Chart
    base = alt.Chart(df).encode(x='created_at:T')

    # Layer A: Price Line (Right Axis)
    line = base.mark_line(color='#FFA500', opacity=0.5).encode(
        y=alt.Y('btc_price', axis=alt.Axis(title='Bitcoin Price ($)', titleColor='#FFA500')),
        tooltip=['created_at', 'btc_price']
    )

    # Layer B: Sentiment Dots (Left Axis)
    points = base.mark_circle(size=100).encode(
        y=alt.Y('score', axis=alt.Axis(title='Sentiment Score (-1 to 1)')),
        color=alt.Color('sentiment', scale=alt.Scale(domain=['POSITIVE', 'NEGATIVE', 'NEUTRAL'], range=['green', 'red', 'gray'])),
        tooltip=['headline', 'score', 'btc_price', 'reason']
    ).interactive()

    # Combine them
    chart = alt.layer(line, points).resolve_scale(
        y='independent' # This creates the dual axis!
    )
    
    st.altair_chart(chart, use_container_width=True)

    # 4. Logs
    st.divider()
    st.subheader("🔍 Analysis Logs")
    for index, row in df.iterrows():
        icon = "⚪"
        if row['sentiment'] == "POSITIVE": icon = "🟢"
        if row['sentiment'] == "NEGATIVE": icon = "🔴"
        
        with st.expander(f"{icon} {row['headline']}"):
            st.write(f"**AI Reasoning:** {row['reason']}")
            st.caption(f"Price: ${row['btc_price']:,.2f} | Score: {row['score']} | Time: {row['created_at']}")

else:
    st.info("Waiting for data... Run your Lambda Producer!")
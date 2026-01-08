import streamlit as st
import pandas as pd
import psycopg2
import altair as alt

# --- CONFIG ---
st.set_page_config(page_title="Crypto Sentiment AI", page_icon="🧠", layout="wide")

# --- DB CONNECTION ---
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
        query = """
            SELECT headline, sentiment, score, reason, btc_price, created_at 
            FROM raw_data.crypto_sentiment
            ORDER BY created_at DESC
            LIMIT 100
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        # THE FIX: Force 'btc_price' to be numeric. 
        df['btc_price'] = pd.to_numeric(df['btc_price'], errors='coerce')
        
        return df
    return pd.DataFrame()

# --- DASHBOARD UI ---
st.title("🧠 AI Crypto Analyst")
st.caption("Correlating Bitcoin News Sentiment with Price Action")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

df = get_sentiment_data()

if not df.empty:
    latest = df.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Sentiment Color
    sent_color = "off"
    if latest['sentiment'] == "POSITIVE": sent_color = "normal"
    if latest['sentiment'] == "NEGATIVE": sent_color = "inverse"
    
    col1.metric("Latest Sentiment", latest['sentiment'], f"{latest['score']:.2f}", delta_color=sent_color)
    
    # Price Display Logic
    price = latest['btc_price']
    if pd.notna(price) and price > 0:
        price_display = f"${price:,.2f}"
    else:
        price_display = "—"
        
    col2.metric("BTC Price", price_display) 
    col3.metric("Data Points", len(df))
    col4.markdown(f"**Latest News:**\n_{latest['headline'][:50]}..._")

    # --- DUAL AXIS CHART ---
    st.divider()
    st.subheader("Sentiment vs. Price Correlation")
    
    base = alt.Chart(df).encode(x='created_at:T')

    # Line Chart (Price) 
    line = base.mark_line(color='#FFA500', opacity=0.5).encode(
        y=alt.Y('btc_price', axis=alt.Axis(title='Bitcoin Price ($)', titleColor='#FFA500')),
        tooltip=['created_at', 'btc_price']
    )

    # Dot Chart (Sentiment)
    points = base.mark_circle(size=100).encode(
        y=alt.Y('score', axis=alt.Axis(title='Sentiment Score (-1 to 1)')),
        color=alt.Color('sentiment', scale=alt.Scale(domain=['POSITIVE', 'NEGATIVE', 'NEUTRAL'], range=['green', 'red', 'gray'])),
        tooltip=['headline', 'score', 'btc_price', 'reason']
    ).interactive()

    chart = alt.layer(line, points).resolve_scale(y='independent')
    st.altair_chart(chart, use_container_width=True)

    # --- LOGS ---
    st.divider()
    st.subheader("🔍 Analysis Logs")
    for index, row in df.iterrows():
        icon = "⚪"
        if row['sentiment'] == "POSITIVE": icon = "🟢"
        if row['sentiment'] == "NEGATIVE": icon = "🔴"
        
        p_val = row['btc_price']
        p_str = f"${p_val:,.2f}" if (pd.notna(p_val) and p_val > 0) else "—"
        
        with st.expander(f"{icon} {row['headline']}"):
            st.write(f"**AI Reasoning:** {row['reason']}")
            st.caption(f"Price: {p_str} | Score: {row['score']} | Time: {row['created_at']}")

else:
    st.info("Waiting for data... Run your Lambda Producer!")
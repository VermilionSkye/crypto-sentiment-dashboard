import streamlit as st
import pandas as pd
import psycopg2
import altair as alt

# --- CONFIG ---
st.set_page_config(page_title="Crypto Sentiment AI", page_icon="🧠", layout="wide")

# --- DB CONNECTION (Reusing your Secrets) ---
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
        # We fetch the latest 50 records
        query = """
            SELECT headline, sentiment, score, reason, created_at 
            FROM raw_data.crypto_sentiment
            ORDER BY created_at DESC
            LIMIT 50
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# --- DASHBOARD UI ---
st.title("🧠 AI Crypto Analyst")
st.caption("Tracking Bitcoin Sentiment using Llama 3 & AWS Lambda")

# 1. Refresh Button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# 2. Load Data
df = get_sentiment_data()

if not df.empty:
    # 3. Key Metrics
    latest = df.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    # Color logic for the metrics
    delta_color = "off" # Default grey
    if latest['sentiment'] == "POSITIVE": delta_color = "normal" # Green
    if latest['sentiment'] == "NEGATIVE": delta_color = "inverse" # Red
    
    col1.metric("Latest Sentiment", latest['sentiment'], f"{latest['score']:.2f}", delta_color=delta_color)
    col2.metric("Data Points Analyzed", len(df))
    col3.info(f"Latest Headline:\n\n_{latest['headline']}_")

    # 4. The Chart
    st.divider()
    st.subheader("Sentiment Trend (Last 50 News Items)")
    
    # We map sentiment text to colors manually
    chart = alt.Chart(df).mark_circle(size=100).encode(
        x=alt.X('created_at', title='Time'),
        y=alt.Y('score', title='Sentiment Score (-1 to 1)'),
        color=alt.Color('sentiment', scale=alt.Scale(domain=['POSITIVE', 'NEGATIVE', 'NEUTRAL'], range=['green', 'red', 'gray'])),
        tooltip=['headline', 'reason', 'score', 'created_at']
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

    # 5. Detailed Logs
    st.divider()
    st.subheader("🔍 Analyst Logs (Llama 3 Reasoning)")
    
    for index, row in df.iterrows():
        # Emoji based on sentiment
        icon = "⚪"
        if row['sentiment'] == "POSITIVE": icon = "🟢"
        if row['sentiment'] == "NEGATIVE": icon = "🔴"
        
        with st.expander(f"{icon} {row['headline']}"):
            st.write(f"**AI Reasoning:** {row['reason']}")
            st.caption(f"Score: {row['score']} | Time: {row['created_at']}")

else:
    st.info("Waiting for data... Run your Lambda Producer to fetch news!")
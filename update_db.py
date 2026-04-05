import psycopg2
import streamlit as st

DB_HOST = st.secrets["DB_HOST"]
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]

try:
    print("🔌 Connecting...")
    conn = psycopg2.connect(host=DB_HOST, database="postgres", user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()

    print("🔨 Adding 'btc_price' column...")
    # This command adds the new column if it doesn't exist
    cur.execute("ALTER TABLE raw_data.crypto_sentiment ADD COLUMN IF NOT EXISTS btc_price FLOAT;")
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Success! Database upgraded.")

except Exception as e:
    print(f"❌ Error: {e}")

import psycopg2
# ⚠️ PASTE YOUR ACTUAL CREDENTIALS (or use st.secrets if running via Streamlit)
DB_HOST = "de-project-db.c7cq8ky609tw.eu-north-1.rds.amazonaws.com"
DB_USER = "tani"
DB_PASSWORD = "QwUqK8H2YKP6l3gDnyh9"

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
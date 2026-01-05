# Crypto Sentiment Dashboard

A serverless data pipeline that uses AWS Lambda, SQS, and Llama 3 (AI) to analyze real-time Bitcoin news sentiment and visualize trends on a Streamlit dashboard.

## Architecture

This project demonstrates a decoupled "Producer-Consumer" architecture:

1.  **News Producer (AWS Lambda):** Fetches real-time market news from NewsAPI and pushes distinct articles into an AWS SQS Queue.
2.  **Sentiment Engine (AWS Lambda):** Triggered by the Queue, this function processes articles using the Llama 3 LLM (via Groq API) to determine sentiment (Positive/Negative/Neutral) and generate reasoning.
3.  **Storage (AWS RDS):** Structured sentiment data is stored in a PostgreSQL database.
4.  **Dashboard (Streamlit):** A frontend web app that connects to the database to visualize sentiment trends, confidence scores, and AI reasoning logs.

## Tech Stack

* **Cloud Infrastructure:** AWS Lambda, AWS SQS, AWS RDS (PostgreSQL)
* **AI/LLM:** Llama 3.3 (70B) via Groq API
* **Frontend:** Streamlit, Altair (for visualization)
* **Language:** Python 3.12
* **Libraries:** `boto3`, `psycopg2`, `urllib3`, `pandas`

## Setup Instructions

### Prerequisites
* AWS Account (Free Tier)
* Groq Cloud API Key
* NewsAPI Key
* Python 3.12 installed locally

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/VermilionSkye/crypto-sentiment-dashboard.git](https://github.com/VermilionSkye/crypto-sentiment-dashboard.git)
    cd crypto-sentiment-dashboard
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure Secrets:
    Create a `.streamlit/secrets.toml` file (do not commit this to Git) with your database credentials:
    ```toml
    DB_HOST = "your-rds-endpoint.amazonaws.com"
    DB_USER = "postgres"
    DB_PASSWORD = "your-password"
    ```

4.  Run the Dashboard:
    ```bash
    streamlit run app.py
    ```

## Live Demo

[https://crypto-sentiment-dashboard-vs.streamlit.app/]
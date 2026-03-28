import os
import urllib3
import json
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import streamlit as st

def fetch_neso_data(query_url="https://api.neso.energy/api/3/action/datastore_search_sql?sql=SELECT * from \"f93d1835-75bc-43e5-84ad-12472b180a98\""):
    print("📥 Fetching data from NESO API...")
    http = urllib3.PoolManager()
    resp = http.request("GET", query_url)
    data = pd.DataFrame(json.loads(resp.data)['result']['records'])
    print(f'Fetch {len(data)} rows')
    return data

def clean_data(data):
    print("🧹 Cleaning data...")
    cols = data.columns.tolist()
    non_perc_cols = [col for col in cols if not col.endswith('_perc')]
    perc_cols = [col for col in cols if col.endswith('_perc')]
    cols = non_perc_cols + perc_cols
    remove = ['DATETIME', 'CARBON_INTENSITY', '_full_text', '_id']
    cols = ['CARBON_INTENSITY'] + [col for col in cols if col not in remove]
    data_sorted = pd.concat([
    data['DATETIME'].astype('datetime64[ns]'), 
    data[cols].astype(float)
    ], axis=1)
    print(data_sorted.info())
    return data_sorted

def get_engine():
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    port = os.getenv("DB_PORT")
    if not all([host, database, username, password]):
        if "postgres" in st.secrets:
        # Access secrets from .streamlit/secrets.toml
            db = st.secrets["postgres"]
            host = db.get("host")
            database = db.get("database")
            username = db.get("username")
            password = db.get("password")
            port = db.get("port")
    print([host, database, username, password, port])
    # Create connection engine
    engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")
    return engine

def export_to_sql(df, engine):
    print(f"💾 Saving {len(df)} rows to database...")
    df.to_sql("generation_data", engine, if_exists="replace", index=False)
    print("Data exported to PostgreSQL successfully.")
    

def main():
    print("🚀 Starting Data Ingestion Pipeline...")
    # 2. Fetch
    df = fetch_neso_data()
    
    # 3. Clean
    sorted_df = clean_data(df)

    # 1. Get engine
    engine = get_engine()
    
    # 4. Export
    export_to_sql(sorted_df, engine)

if __name__ == "__main__":
    main()

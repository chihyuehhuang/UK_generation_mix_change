import sys
import os
from src.frontend import *
from src.models import * 
from src.ingest import get_engine
import streamlit as st
import pandas as pd
from sqlalchemy import text
import psycopg2


# Set page config
st.set_page_config(page_title="UK Generation Mix Clustering", layout="wide")

## --- Data Loading ---
# 1. Secure Database Connection
# @st.cache_resource # Use cache_resource for database engines

@st.cache_data(ttl=3600)
def load_data_from_db():
    engine = get_engine()
    col_query = text('SELECT column_name FROM information_schema.columns WHERE table_name = \'generation_data\';')
    with engine.connect() as conn:
        col_result = conn.execute(col_query)
        col_names = [row[0] for row in col_result.fetchall()]
    exclude_cols = ['DATETIME'] # I do not add other columns to exclude because it may be used in the future.
    kept_cols = [col for col in col_names if col not in exclude_cols]
    sum_query_string = ", ".join([f'SUM("{col}") AS "{col}"' for col in kept_cols])
    query = text(f'SELECT DATE_TRUNC(\'month\',"DATETIME") AS "DATETIME", {sum_query_string} FROM public.generation_data WHERE EXTRACT(YEAR FROM "DATETIME") < 2025 GROUP BY 1 ORDER BY 1;')
    with engine.connect() as conn:
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall())
        if not df.empty:
            df.columns = result.keys() # Ensure column names are preserved
            df = df.set_index('DATETIME')
    print(df.info())
    return df

## --- Title and Description ---
st.title("UK Electricity Generation Mix: Clustering Analysis")
st.markdown("""
This app analyzes how the UK's energy generation profile has changed over time 
using K-Means clustering (data source: [NESO](https://www.neso.energy/data-portal/historic-generation-mix/historic_gb_generation_mix)).
""")
st.divider()
try:
    data = load_data_from_db()
    
    if data.empty:
        st.warning("Connected to database, but no records were found.")
    else:
        # pre-process data
        # Convert from MW to GWh
        for col in data.columns:
            if 'perc' not in col:
                data[col] = data[col] / 2 / 1000

        data['WIND'] += data['WIND_EMB']
        data['WIND_perc'] += data['WIND_EMB_perc']
        data.drop(columns=['WIND_EMB', 'WIND_EMB_perc'], inplace=True)

        aggregate_cols = ['RENEWABLE', 'FOSSIL', 'ZERO_CARBON', 'LOW_CARBON', 'GENERATION', 'DATETIME', 'CARBON_INTENSITY']
        generation = [col for col in data.columns if col not in aggregate_cols and '_perc' not in col] # perc from index 18
        generation_perc = [col + '_perc' for col in generation]
        cols = generation

        # --- Side bar for user inputs
        # style
        load_css()
        
        # max n_clusters
        st.sidebar.header("Model Parameters")
        n_clusters = st.sidebar.selectbox(
        "Select the maximum number of clusters", 
        options=np.arange(2, 7),
        index=0)
        st.markdown("Running KMean clustering with " + ", ".join([str(i) for i in np.arange(2, n_clusters+1)]) + " clusters")

        #data selection
        X = data[cols]
        freq = st.sidebar.selectbox(
        "Select data frequency", 
        ['monthly', 'monthly (de-seasoned)', 'yearly'],
        index=1)

        X = data.groupby(data.index.to_period(freq[0].upper())).sum()
        X.set_index(X.index.to_timestamp(), inplace=True)
        X.index.name = 'Date'
        X = X[[col.upper() for col in cols]]
        X_display = X.copy()
        if freq == "monthly (de-seasoned)" :
            X_avg = X.groupby(X.index.month).mean()
            X_avg.index.name = 'Month'
            X_deseasoned = X.copy()
            for idx in X_deseasoned.index:
                month = idx.month
                X_deseasoned.loc[idx] = X_deseasoned.loc[idx] - X_avg.loc[month]

            X = X_deseasoned
       
        # run KMean clustering with the selected max n_clusters
        @st.cache_data(show_spinner="Running K-Means Clustering Analysis... Please wait.")
        def clustering_analysis_standard(X, n_clusters):
            kmeans_model, labels, db_scores = [], [], []
            for n_cluster in range(2, n_clusters+1):
                kmeans = cluster_analysis(X, n_cluster)
                kmeans_model.append(kmeans[0])
                labels.append(kmeans[1])
                db_scores.append(kmeans[2])
                 
            optimal_n_clusters = db_scores.index(min(db_scores)) + 2
            st.write(f'Optimal number of clusters: {optimal_n_clusters} (with Davies-Bouldin score: {db_scores[optimal_n_clusters - 2]})')
            optimal_label = labels[optimal_n_clusters - 2]
            return optimal_label
        
        @st.cache_data(show_spinner="Due to the smaller sample size (<30), Boostrap is employed to calculate the stability. It may take a while.")
        def clustering_analysis_small_sample(X, n_clusters):
            kmeans_model, labels, db_scores, sh_scores = [], [], [], []
            for n_cluster in range(2, n_clusters+1):
                kmeans = cluster_analysis(X, n_cluster, n_init=100, max_iter=1000, stab=True, silhouette=True)
                kmeans_model.append(kmeans[0])
                labels.append(kmeans[1])
                db_scores.append(kmeans[2])
                sh_scores.append(kmeans[3])
            optimal_n_clusters = db_scores.index(min(db_scores)) + 2
            st.write(f'Optimal number of clusters: {optimal_n_clusters} (with Davies-Bouldin score: {db_scores[optimal_n_clusters - 2]})')
            optimal_label = labels[optimal_n_clusters - 2]
            return optimal_label
        
        if len(X) < 30:
            optimal_label = clustering_analysis_small_sample(X, n_clusters)
        else:
            optimal_label = clustering_analysis_standard(X, n_clusters)
        
        st.subheader("UK Generation Mix Overtime")
        bar_fig = stacked_bar(X_display, cols, optimal_label)
        st.plotly_chart(bar_fig, width='stretch')

        # Select graph
        for col in cols:
            if col not in st.session_state:
                st.session_state[col] = False

        def select_all():
            for col in cols:
                st.session_state[col] = True

        def clear_all():
            for col in cols:
                st.session_state[col] = False

        col1, col2 = st.sidebar.columns(2)

        col1.button("Select All", on_click=select_all)
        col2.button("Clear All", on_click=clear_all)

        selected_cols = []
        for col in cols:
            if st.sidebar.checkbox(col, key=col):
                selected_cols.append(col)

        if selected_cols :
            for col in selected_cols:
                line_fig = interactive_line(X_display, col, optimal_label)
                st.plotly_chart(line_fig, width='stretch', key = f"chart_{col}")


except Exception as e:
    st.error(f"Failed to connect to Database: {e}")
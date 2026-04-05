from flask import Flask, jsonify, request, render_template
from src.ingest import load_data_from_db
from src.models import clustering_analysis_standard, clustering_analysis_small_sample
from src.frontend import interactive_scatter, stacked_bar
# Initialize the Flask application
app = Flask(__name__)

# route to get column names from the database
@app.route('/api/get_cols', methods=['GET'])
def get_cols():
    data = load_data_from_db()
    df = data.copy()
    cols = df.columns.tolist()

    df['WIND'] += df['WIND_EMB']
    df['WIND_perc'] += df['WIND_EMB_perc']
    df.drop(columns=['WIND_EMB', 'WIND_EMB_perc'], inplace=True)

    aggregate_cols = ['RENEWABLE', 'FOSSIL', 'ZERO_CARBON', 'LOW_CARBON', 'GENERATION', 'DATETIME', 'CARBON_INTENSITY']
    generation = [col for col in df.columns if col not in aggregate_cols and '_perc' not in col] # perc from index 18
    cols = generation

    return jsonify({"cols": cols})

# route to run clustering
@app.route('/api/run_clustering', methods=['POST'])
def run_clustering():
    # 1. Get the inputs sent by the JavaScript fetch()
    req = request.get_json()
    n_clusters = req['n_clusters']
    freq = req['frequency']
    selected_cols = req['type']
    
    # 2. Run your existing Python logic
    data = load_data_from_db()
    df = data.copy()
    cols = df.columns.tolist()

    df['WIND'] += df['WIND_EMB']
    df['WIND_perc'] += df['WIND_EMB_perc']
    df.drop(columns=['WIND_EMB', 'WIND_EMB_perc'], inplace=True)

    aggregate_cols = ['RENEWABLE', 'FOSSIL', 'ZERO_CARBON', 'LOW_CARBON', 'GENERATION', 'DATETIME', 'CARBON_INTENSITY']
    generation = [col for col in df.columns if col not in aggregate_cols and '_perc' not in col] # perc from index 18
    cols = generation

    # data selection
    X = data[cols]
    X = data.groupby(data.index.to_period(freq[0].upper())).sum()
    X.set_index(X.index.to_timestamp(), inplace=True)

    X.index.name = 'Date'
    X = X[[col.upper() for col in cols]]
    X_display = X.copy()
    if freq == "Monthly (de-seasoned)" :
        X_avg = X.groupby(X.index.month).mean()
        X_avg.index.name = 'Month'
        X_deseasoned = X.copy()
        for idx in X_deseasoned.index:
            month = idx.month
            X_deseasoned.loc[idx] = X_deseasoned.loc[idx] - X_avg.loc[month]

        X = X_deseasoned

    if len(X) < 30:
        optimal_n_clusters, optimal_label, n_clusters_range, db_scores = clustering_analysis_small_sample(X, n_clusters)
    else:
        optimal_n_clusters, optimal_label, n_clusters_range, db_scores = clustering_analysis_standard(X, n_clusters)

    # main bar chart
    main_chart = stacked_bar(X_display, cols, optimal_label, timeformat='%Y-%m')

    # indiviual scatter plot
    scatter_plots = {}
    for col in cols:
        print(col)
        scatter_plots[col] = interactive_scatter(X_display, col, optimal_label, timeformat='%Y-%m')

    return jsonify({
        "optimal_n_clusters": optimal_n_clusters,
        "labels": optimal_label.tolist(), # Convert numpy array to list for JSON serialization
        "n_clusters_range": n_clusters_range,
        "db_scores": db_scores,
        "main_chart": main_chart,
        "scatter_plots": scatter_plots
    })

# Route for the home page
@app.route('/')
def home():
    # This tells Flask to look in the "templates" folder for index.html
    return render_template('index.html')

# Run the server
if __name__ == '__main__':
    # debug=True automatically reloads the server when you make code changes!
    app.run(host='0.0.0.0', port=8080, debug=True)
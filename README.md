# Porject: Structural change in UK power generation mix (k-means clustering analysis)

## Overview
This project uses k-means clustering analysis to analyse UK generation mix data and search for the structural change in UK generation mix.
The data is downloaded from the [National Energy System Operator (NESO)](https://www.neso.energy/data-portal)

This repository contains three scripts:

1. The [first notebook](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/01_data_import%20(first).ipynb) downloads the data via NESO API and export it to PostgreSQL database.
2. The [second notebook](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/02_data_update.ipynb) updates the database.
However, it is not necessary to frequently update the data, as the main purpose is to find the long-term structural change.
3. The [third notebook](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/03_clustering_analysis.ipynb) performs the clustering analysis.
It includes data preprocessing, analysis and findings.

## Implementation
### Option 1: Run in the container
Step 1: Build & start containers for both postgreSQL & Jupyter Notebook <br>
```docker-compose up -d```

Step 2: Get the URL <br>
```docker logs energy_jupyter```

Step3: Copy the URL to the browser & run the Jupyter Notebook <br>

### Option 2: Run on local machine
Step 1: Setup the PostgreSQL on your local machine
Make sure the host, username, port, password are identical with the setting.
They are the alternative value in
```
host = os.getenv("DB_HOST", "localhost")
database = os.getenv("DB_NAME", "energy_forecast")
username = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASS", "1234")
port = os.getenv("DB_PORT", "5432")
```
For example, set the host to "localhost".
Step2: Run the Jupyter Notebook.
If you have any question, please contact me by 📫 [hello@chihyuehhuang.com](mailto:hello@chihyuehhuang.com).

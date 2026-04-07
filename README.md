# Porject: Identifying Structural Changes in UK Power Generation Mix: A Clustering Analysis Approach

## Overview
This project uses k-means clustering analysis to identify the structural changes in UK Electricity Generation Mix.
The data is downloaded from the [National Energy System Operator (NESO)](https://www.neso.energy/data-portal)

## Legacy Streamlit app
The Streamlit app was developed as a [prototype](https://github.com/chihyuehhuang/UK_generation_mix_change/tree/main/v1_streamlit_prototype), which will not be updated in the future. It is deployed on [Streamlit Cloud Community](https://ukgenerationmixchange.streamlit.app/)

## Analytics
This repository contains three scripts:

1. [Data import](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/01_data_import%20(first).ipynb): download the data via NESO API and exports it to the PostgreSQL database.
2. [Data update](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/02_data_update.ipynb): update the database.
However, it is not necessary to update the data frequently, as the main purpose is to identify long-term structural change.
3. [Clustering analysis](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/03_clustering_analysis.ipynb): perform the clustering analysis.

## Implementation (Docker & Flask app)
### Running locally
:exclamation: Please run [Data import](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/01_data_import%20(first).ipynb) to create DB before running [Clustering analysis](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/notebooks/03_clustering_analysis.ipynb).

#### Option 1: Run with Docker (recommended)
Step 1: Create .env file. Check [.env.example](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/.env.example).
DB_HOST should match the service name in [docker-compose.yml](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/docker-compose.yml)

Step 2: Build & start containers for both postgreSQL, Jupyter Notebook & Streamlit <br>
```docker-compose up -d```

Step 3: Get the URL & check if data is ingested.

Streamlit:<br>
```docker logs energy_flask_app```

:exclamation: the data ingestion is tied with [energy_flask_app Dockerfile](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/Dockerfile). Please wait until the data is succesfully ingested before access notebook & streamlit app.

Notebook:<br>
```docker logs energy_jupyter```

PostgreSQL:<br>
(Not necessary to check)
```docker logs energy_db```

Step 4: Copy the URL to the browser and run the Jupyter Notebook & Flask app <br>

#### Option 2: Outside of Docker
Step 1: Set up PostgreSQL on your local machine and make sure the host, username, port, and password match the settings.

Step 2: Store environment information created in step 1 in .streamlit/secrets.toml.

Example file: [secrets.toml.example](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/.streamlit/secrets.toml.example)

Step 3: Run the Jupyter Notebook in your IDEs. For Flask app,

```python app.py``` or <br>
```py app.py```

### Deploy to server
#### 1. PostgreSQL: I use free plan on [render.com](https://render.com/) for PostgreSQL.

Step 1: Create PostgreSQL service.

Step 2: Dashboard -> Services -> choose your db -> Connections -> Copy "External Database URL"

Step 3. Open [data_ingestor.bat](https://github.com/chihyuehhuang/UK_generation_mix_change/blob/main/data_ingestor.bat), replace "DATABASE_URL" to your "External Database URL" and run the bash file to ingest data to your Render database.

#### 2. Deploy: Flask app is deployed with docker on Render.com.
Step 1: Commit your local repository to GitHub & create a WebService on Render to deploy. Make sure you select "Docker" as runtime.

Step 2: In Dashboard -> Environment, set up your DB information, which should be identical as the details set up in the PostgreSQL on Render.com.

If you have any question, please contact me by 📫 [hello@chihyuehhuang.com](mailto:hello@chihyuehhuang.com).

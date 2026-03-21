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
Step 1:
Under CMD/PowerShell/Terminal
`docker-compose up -d`
`docker logs energy_jupyter`
Copy the URL to the browser & run the Jupyter Notebook

### Option 2: Run on local machine

If you have any question, please contact me by 📫 [hello@chihyuehhuang.com](mailto:hello@chihyuehhuang.com).

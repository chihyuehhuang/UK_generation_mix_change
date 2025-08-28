import pip
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score, adjusted_rand_score
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

rng = np.random.default_rng(0)
def stability(X, n_clusters, lab_full, B=200, random_state=1, **kwargs):
    # Convert DataFrame to NumPy array
    if isinstance(X, pd.DataFrame):
        X_array = X.values
    else:
        X_array = np.array(X)

    # bootstrap sample and calculate stability score
    n = X_array.shape[0]
    scores = []
    for _ in range(B):
        idx = rng.choice(n, n, replace=True)
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, **kwargs).fit(X_array[idx])
        lab = kmeans.labels_
        scores.append(adjusted_rand_score(lab_full[idx], lab))
    return np.mean(scores)

def cluster_analysis(X, n_clusters, random_state=1, verbose=True, stab=False, silhouette=False, **kwargs):
    kmeans = KMeans(n_clusters=n_clusters,random_state=random_state, **kwargs).fit(X)
    
    # output information
    labels = kmeans.labels_
    db_score = round(davies_bouldin_score(X, labels), 4)
    
    if silhouette:
        sh_score = round(silhouette_score(X, labels), 4)
    
    if stab:
        stability_score = round(stability(X, n_clusters, labels, random_state=random_state, **kwargs), 4)

    # print
    if verbose:
        if silhouette or stab:
            print(f'n_cluster:{n_clusters}, db_score:{db_score}', end=', ')
        else:
            print(f'n_cluster:{n_clusters}, db_score:{db_score}')

        if silhouette:
            print(f'silhouette_score:{sh_score}')

        if stab:
            print(f'stability:{stability_score}')

    if silhouette and stab:
        return kmeans, labels, db_score, sh_score, stability_score
    elif silhouette:
        return kmeans, labels, db_score, sh_score
    elif stab:
        return kmeans, labels, db_score, stability_score
    else:
        return kmeans, labels, db_score

def clustering_chart(X, kmean_model, labels):
    fig, ax = plt.subplots(figsize=(10, 5))
    scatter = ax.scatter(kmean_model.transform(X)[:, 0], kmean_model.transform(X)[:, 1], c=labels, cmap='cividis')
    ax.set_title('Clustering Chart')
    plt.colorbar(scatter)
    return fig, ax

def detailed_chart(data, cols, labels, timeformat='%Y-%m-%d'):
    no_clusters = []
    for idx in labels:
        if idx not in no_clusters:
            no_clusters.append(idx)
    fig, axs = plt.subplots(len(cols),1, figsize=(10, 5*len(cols)))
    for i, col in enumerate(cols):
        axs[i].scatter(data.index, data[col], c=labels, cmap='cividis')
        axs[i].set_title(col.replace('_perc', ''))
        for j in range(1, len(no_clusters)):
            axs[i].vlines(x=min(data.index[labels == no_clusters[j]]), ymin=0, ymax=data[col].max(), color='r', linestyle='-')
            axs[i].annotate(min(data.index[labels == no_clusters[j]]).strftime(timeformat), xy=(min(data.index[labels == no_clusters[j]]), data[col].max()), color='r')
    return fig, axs

def focus_chart(data, labels, col1=['COAL', 'GAS'], col2=['WIND','SOLAR', 'HYDRO'], col1_name='fossil',col2_name='Renewable'):
    fig, axs = plt.subplots(1, 1, figsize=(10, 5))
    x = data[col1]
    if len(col1) > 1:
        x = data[col1].sum(axis=1)
    else:
        x = data[col1]

    if len(col2) > 1:
        y = data[col2].sum(axis=1)
    else:
        y = data[col2]
        
    axs.scatter(x, y, c=labels, cmap='cividis')
    axs.set_xlabel(col1_name)
    axs.set_ylabel(col2_name)
    return fig, axs
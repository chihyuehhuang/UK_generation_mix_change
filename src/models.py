from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score, adjusted_rand_score
import numpy as np
import pandas as pd


# stability(): calculate statbility scores by boostraping
rng = np.random.default_rng(0)
def stability(X:pd.DataFrame, n_clusters: int, lab_full: pd.DataFrame, B:int=200, random_state:int=1, **kwargs) -> float :
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

# clustering analysis(): perform k-mean clustering & report Davies Bouldin index, Sulhouette scores & stability scores
def cluster_analysis(X:pd.DataFrame, n_clusters, random_state=1, verbose=True, stab=False, silhouette=False, **kwargs):
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
import matplotlib.pyplot as plt

# --- visualisation (Jupyter Notebook)
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
    fig_h = 3
    fig_w = 5
    fig, axs = plt.subplots(len(cols),1, figsize=(fig_w, fig_h*len(cols)), layout="constrained")
    base_fs = fig_h * 2
    # handle only 1 subplot
    if len(cols) == 1:
        axs = [axs]
    
    for i, col in enumerate(cols):
        axs[i].scatter(data.index, data[col], c=labels, cmap='cividis', s=base_fs)
        axs[i].set_title(col.replace('_perc', ''), fontsize=base_fs+2)
        axs[i].tick_params(axis='both', which='major', labelsize=base_fs)
        for j in range(1, len(no_clusters)):
            axs[i].vlines(x=min(data.index[labels == no_clusters[j]]), ymin=0, ymax=data[col].max(), color='r', linestyle='-', linewidth=base_fs/10)
            axs[i].annotate(min(data.index[labels == no_clusters[j]]).strftime(timeformat), xy=(min(data.index[labels == no_clusters[j]]), data[col].max(),), color='r', fontsize=base_fs - 1)
            axs[i].set_ylabel('GWh', fontsize=base_fs)

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
    axs.set_xlabel(col1_name + '(GWh)')
    axs.set_ylabel(col2_name + '(GWh)')
    return fig, axs
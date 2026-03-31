import os
import pandas as pd
import plotly.express as px
import plotly.colors as pc
import streamlit as st

def get_cass_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docker_path = os.path.join(base_dir, "src", "styles", "main.css")
    if os.path.exists(docker_path):
        return docker_path
    local_path = os.path.abspath(os.path.join(base_dir, "..", "src", "styles", "main.css"))
    if os.path.exists(local_path):
        return local_path
    raise FileNotFoundError("Could not find main.css in Docker or Local paths!")

def load_css(cass_path=get_cass_path()):
    """Loads a local CSS file and injects it into the Streamlit app."""
    try:
        with open(cass_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file '{cass_path}' not found.")

ENERGY_COLORS = {
    'WIND': '#0F8554',       # Prism Green
    'SOLAR': '#EDAD08',      # Prism Yellow
    'GAS': '#1D6996',        # Prism Blue
    'NUCLEAR': '#5F4690',    # Prism Deep Purple
    'COAL': '#CC503E',       # Prism Red (Highlights carbon intensity)
    'BIOMASS': '#E17C05',    # Prism Orange
    'HYDRO': '#38A6A5',      # Prism Teal (Aquatic feel)
    'STORAGE': '#94346E',    # Prism Magenta
    'IMPORTS': '#994E95',    # Prism Light Plum
    'OTHER': '#666666'       # Prism Grey
}
# interactive_stacked bar charts
def stacked_bar(data, cols, labels, timeformat='%Y-%m'):
    df_melted = data.reset_index().melt(
        id_vars='Date',
        value_vars=cols,
        var_name='Fuel Type',
        value_name='GWh'
    )

    fig = px.bar(
        df_melted, 
        x='Date', 
        y='GWh', 
        color='Fuel Type',
        title="UK Generation Mix Over Time (Stacked)",
        labels={'GWh': 'Generation (GWh)', 'Date': 'Date'},
        template="plotly_dark", # Matches your dark theme
        color_discrete_map=ENERGY_COLORS # High contrast colors
    )

    no_clusters = pd.Series(labels).unique()
    for j in range(1, len(no_clusters)):
        change_point = min(data.index[labels == no_clusters[j]])
        change_point_str = change_point.strftime(timeformat)
        fig.add_vline(
            x=change_point.timestamp() * 1000, 
            line_dash="dash", 
            line_color="red",
            annotation_text=change_point_str, 
            annotation_xanchor="left", # Anchors the text to the line without math
        )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Energy Output (GWh)",
        hovermode="x unified", # Shows all fuel values for a single date on hover
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        font=dict(family="Playfair Display, serif") # Matches your config.toml font
    )

    return fig

def interactive_scatter(data, col, labels, timeformat= '%Y-%m'):
    df = data.reset_index()
    line_color = ENERGY_COLORS.get(col.upper(), '#1f77b4')

    df['Cluster'] = labels
    cluster_map = dict(zip(df['Cluster'].unique(), [str(i) for i in range(1, len(df['Cluster'].unique())+1)]))
    df['Cluster'] = df['Cluster'].map(cluster_map)
    unique_clusters = sorted(df['Cluster'].unique())
    color_map = {
        cluster: px.colors.label_rgb(
            px.colors.find_intermediate_color(
                px.colors.hex_to_rgb(line_color), px.colors.hex_to_rgb("#FFFFFF"), i / len(unique_clusters))
        ) for i, cluster in enumerate(unique_clusters)
    }
    print(color_map)

    fig = px.scatter(
        df, 
        x='Date', 
        y=col,
        color='Cluster',
        title=f"{col.title()} generation over time", 
        color_discrete_map=color_map)


    for j in range(1, len(unique_clusters)):
        change_point = min(data.index[df['Cluster'] == unique_clusters[j]])
        change_point_str = change_point.strftime(timeformat)
        fig.add_vline(
            x=change_point.timestamp() * 1000, 
            line_dash="dash", 
            line_color="red",
            annotation_text=change_point_str, 
            annotation_xanchor="left", # Anchors the text to the line without math
        )
    fig.update_xaxes(rangeslider_visible=True)
    return fig
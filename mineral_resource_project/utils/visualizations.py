import plotly.express as px
import pandas as pd

def generate_emissions_chart(data):
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Mineral', y='Carbon Emissions', title='Carbon Emissions by Mineral')
    return fig.to_html(full_html=False)

def generate_cost_vs_reserve_chart(data):
    df = pd.DataFrame(data)
    fig = px.scatter(df, x='Reserve Size', y='Extraction Cost', color='Mineral', title='Cost vs Reserve Size')
    return fig.to_html(full_html=False)


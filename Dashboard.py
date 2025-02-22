import pandas as pd
import streamlit as st
import plotly.express as px

url = "https://docs.google.com/spreadsheets/d/12yiz9UT0UMYM1plz5XvXvq_tb5kVJiGISSyILUjn-hU/export?format=csv"

df = pd.read_csv(url)

# Set vizualization as wide
st.set_page_config(layout="wide")

# Chart about performance in videocards
fig_per = px.bar(
    df,
    x ="Placa de Vídeo",
    y = "Desempenho",
    title ="Desempenho",
    text_auto = True,
    color_discrete_sequence=["#5863f8"] # Change color to purple   
)
# Some adjusts in the title and details
fig_per.update_layout(
    title_font_size = 36,
    xaxis_title = None,
    yaxis_title = None,
    title = {'x': 0.5, 'xanchor': 'center'}
)

# Change data from y to white
fig_per.update_traces(textfont=dict(color="white"))

# Line to define the minimum
fig_per.add_hline(
    y=40,
    line_dash="dash",
    line_color="white",
)

# Chart about Cost x Benefit
fig_cxb = px.bar(
    df,
    x ="Placa de Vídeo",
    y = "CxB",
    title ="CxB",
    text_auto = True,
    color_discrete_sequence=["#429720"]    
)

# Some adjusts in the title and details
fig_cxb.update_layout(
    title_font_size = 36,
    xaxis_title = None,
    yaxis_title = None,
    title = {'x': 0.5, 'xanchor': 'center'}
)

# Change data from y to white
fig_cxb.update_traces(textfont=dict(color="white"))

# Line to define the minimum
fig_cxb.add_hline(
    y=35,
    line_dash="dash",
    line_color="white",
)

#Show the two charts
st.plotly_chart(fig_per, use_container_width=True)
st.plotly_chart(fig_cxb, use_container_width=True)

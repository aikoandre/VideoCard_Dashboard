import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import plotly.express as px

# Import file with password to the service account
filename = "large-language-models-437500-8f75cfce8601.json"
scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Link APIs with the account
creds = ServiceAccountCredentials.from_json_keyfile_name(
    filename=filename, scopes=scopes
)

# Connect with the account and allow acess with password
client = gspread.authorize(creds)

# Location of the archive in Google Drive
full_sheet = client.open(
    title="Placa de Vídeo CxB", 
    folder_id="1HHVkEg_OQtjO5YCL7iCIH8oQ_GRdpqnF",
)

# Select page 1 and show all the table
sheet = full_sheet.get_worksheet(0)
data = sheet.get_all_records()
df = pd.DataFrame(data)

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

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set view to wide display
st.set_page_config(layout="wide")

# Import CSV file
df = pd.read_csv("video_card.csv", sep=",", decimal=".")

# Convert column to string type
df["Placa de Vídeo"] = df["Placa de Vídeo"].astype(str)

# Calculate the average of "Valor"
average = df["CxB"].mean()

col1, col2, col3 = st.columns(3)

# Select box in the sidebar
with col2:
    select_model = st.selectbox("Select a Video Card", df["Placa de Vídeo"].unique())
    model_select = df[df["Placa de Vídeo"] == select_model]["Valor"].values[0]

# VRAM of the selected model
with col1:
    vram_model = df[df["Placa de Vídeo"] == select_model]["VRAM"].values[0]

    # Custom HTML/CSS for "Valor" of the selected model
    st.markdown(
        f"""
        <div style="
            background: #1E1E1E;
            padding: 5px;
            border-radius: 10px;
            text-align: center;
            margin: 5px 0;
            width: auto;">
            <h1 style="color: #ffffff; font-size: 30px; margin: 5px 0;">R$ {model_select:,.2f}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# Custom HTML/CSS for "VRAM" of the selected model
with col3:
    st.markdown(
        f"""
        <div style="
            background: #1E1E1E;
            padding: 5px;
            border-radius: 10px;
            text-align: center;
            margin: 5px 0;">
            <h1 style="color: #ffffff; font-size: 30px; margin: 5px 0;">{vram_model} VRAM</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

col1, col2 = st.columns(2)

order = df.sort_values(by="Valor", ascending=True)["Placa de Vídeo"]

# Create the highlight in the two charts
hl_cxb = ["#328538" if model != select_model else "#68FF84" for model in df["Placa de Vídeo"]]
hl_per_1080p = ["#b9faf8" if model != select_model else "#68A5FF" for model in df["Placa de Vídeo"]]
hl_per_1440p = ["#10e5de" if model != select_model else "#68A5FF" for model in df["Placa de Vídeo"]]

# Chart of CxB column in bars
fig_cxb = px.bar(df, x="Placa de Vídeo", y="CxB",
                 title="Cost-Benefit",
                 category_orders={"Placa de Vídeo": order},
                 text=df["CxB"])

# Update highlight in the chart
fig_cxb.update_traces(marker_color=hl_cxb)

# Settings of the layout
fig_cxb.update_layout(title_x=0.45,  # Center the title
                      title_font_size=36,
                      margin=dict(l=20, r=20, t=60, b=20),
                      autosize=True)

# Hide labels from the x and y axes
fig_cxb.update_xaxes(title_text="")  # Hide x title
fig_cxb.update_yaxes(title_text="")  # Hide y title

# Data labels for CxB chart
fig_cxb.update_traces(
    textposition="outside",
    textfont=dict(size=12, color="white")
)

# Add average line in the chart
fig_cxb.add_hline(
    y=average,
    line_dash="dash",
    line_color="white",
)

# Show the chart fig_cxb
st.plotly_chart(fig_cxb, use_container_width=True)

# Create the initial bar chart using go.Figure
fig_per = go.Figure()

# Add the "1080p Ultra" trace
fig_per.add_trace(
    go.Bar(x=df["Placa de Vídeo"],
           y=df["1080p Ultra"],
           name="1080p Ultra",
           text=df["1080p Ultra"],
           marker_color=hl_per_1080p)
)

# Add the "1440p Ultra" trace
fig_per.add_trace(
    go.Bar(x=df["Placa de Vídeo"],
           y=df["1440p Ultra"],
           name="1440p Ultra",
           text=df["1440p Ultra"],
           marker_color=hl_per_1440p)
)

# Settings of the layout
fig_per.update_layout(title_text="Performance",
                      title_x=0.44,  # Center the title
                      title_font_size=36,
                      margin=dict(l=20, r=20, t=60, b=20),
                      autosize=True,
                      barmode='group',
                      xaxis=dict(categoryorder='array', categoryarray=order))

# Hide labels from the x and y axes
fig_per.update_xaxes(title_text="")  # Hide x title
fig_per.update_yaxes(title_text="")  # Hide y title

# Data labels
fig_per.update_traces(
    textposition="outside",
    textfont=dict(size=12, color="white")
)

# Show the chart fig_per
st.plotly_chart(fig_per, use_container_width=True)

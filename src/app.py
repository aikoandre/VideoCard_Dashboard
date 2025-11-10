import streamlit as st
import altair as alt
from utils import carregar_dados

df = carregar_dados()
df = df.sort_values(by='passmark_g3d_score', ascending=True).reset_index(drop=True)

st.set_page_config(
    layout='wide',
    page_title='Graphic Cards',
    page_icon=':bar_chart:',
)

st.markdown("""
<style>
.card-custom {
    background: rgba(128, 128, 128, 0.2) !important;
    color: var(--text-color) !important;
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(128, 128, 128, 0.3);
    margin-bottom: 8px;
}
.card-custom .label { font-size: 20px; color: var(--text-color); opacity: 0.7; }
.card-custom .value { font-size: 28px; font-weight: bold; color: var(--text-color); }
</style>
""", unsafe_allow_html=True)
card = df['tpu_model_name'].tolist()

col1, col2, col3 = st.columns([1, 2, 1], gap="large")

with col2:
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    selected_card = st.selectbox('Select a Graphic Card', card)
    
card_data = df[df['tpu_model_name'] == selected_card].iloc[0]

with col1:
    st.markdown(
        f"""
        <div class="card-custom" style="height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <span class="label">VRAM</span><br>
            <span class="value">{card_data['vram']}</span>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card-custom">
            <span class="label">Bus Interface</span><br>
            <span class="value">{card_data.get('bus_interface', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div class="card-custom">
            <span class="label">Memory Type</span><br>
            <span class="value">{card_data.get('memory_type', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True
    )

base1 = alt.Chart(df).encode(
    x=alt.X('tpu_model_name', sort=None, axis=alt.Axis(title=None, labelLimit=200)),
    y=alt.Y('passmark_g3d_score', title=None),
    tooltip=['tpu_model_name', 'passmark_g3d_score'],
      color=alt.condition(
        alt.datum['tpu_model_name'] == selected_card,
        alt.value('#98FFA0'),
        alt.value('#008B0C')
    )
)
    
bar1 = base1.mark_bar()
text1 = base1.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='#ffffff'
).encode(
    text=alt.Text('passmark_g3d_score', format='.2s')
)

chart1 = (bar1 + text1).properties(
    title=alt.TitleParams(
        text='Performance',
        anchor='middle',
        fontSize=25,
    ),
    width=900,
    height=500,
)

st.altair_chart(chart1, use_container_width=True)

st.dataframe(df, use_container_width=True, hide_index=True)
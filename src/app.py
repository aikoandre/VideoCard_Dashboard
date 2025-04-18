import streamlit as st
import altair as alt
from utils import carregar_dados
import os

csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Hardware.csv')
df = carregar_dados(csv_path)
df = df.sort_values(by='1080p Ultra', ascending=True).reset_index(drop=True)

st.set_page_config(
    layout='wide',
    page_title='Placas de Vídeo',
    page_icon=':bar_chart:',
)

st.markdown("""
<style>
.card-custom {
    background: #222 !important;
    color: #fff !important;
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 2px 8px #00000010;
    border: 1px solid #222;
    margin-bottom: 8px;
}
.card-custom .label { font-size: 20px; color: #ccc; }
.card-custom .value { font-size: 28px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

placas = df['Placa de Vídeo'].tolist()

col1, col2, col3 = st.columns(3, gap="large")

with col2:
    placa_selecionada = st.selectbox('Selecione uma Placa de Vídeo', placas)
    
dados_placa = df[df['Placa de Vídeo'] == placa_selecionada].iloc[0]

with col1:
    st.markdown(
        f"""
        <div class="card-custom">
            <span class="label">Valor</span><br>
            <span class="value">R$ {int(dados_placa['Valor']):,}</span>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card-custom">
            <span class="label">VRAM</span><br>
            <span class="value">{dados_placa['VRAM']}</span>
        </div>
        """, unsafe_allow_html=True
    )


st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

base = alt.Chart(df).encode(
    x=alt.X('Placa de Vídeo', sort=None, axis=alt.Axis(title=None)),
    y=alt.Y('CxB', title=None),
    tooltip=['Placa de Vídeo', 'CxB'],
    color=alt.condition(
      alt.datum['Placa de Vídeo'] == placa_selecionada,
      alt.value('#D3B2FF'),
      alt.value('#9F56FF')
    )
)

barras1 = base.mark_bar()
texto1 = base.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='#ffffff'
  ).encode(
      text=alt.Text('CxB', format='.2f')
  )

chart1 = (barras1 + texto1).properties(
    title=alt.TitleParams(
        text='Custo x Benefício',
        anchor='middle',
        fontSize=20,
      ),
      width=900,
      height=500,
    )

st.altair_chart(chart1, use_container_width=True)

base2 = alt.Chart(df).encode(
    x=alt.X('Placa de Vídeo', sort=None, axis=alt.Axis(title=None)),
    y=alt.Y('1080p Ultra', title=None),
    tooltip=['Placa de Vídeo', '1080p Ultra'],
      color=alt.condition(
        alt.datum['Placa de Vídeo'] == placa_selecionada,
        alt.value('#98FFA0'),
        alt.value('#008B0C')
    )
)
    
barras2 = base2.mark_bar()
texto2 = base2.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='#ffffff'
).encode(
    text=alt.Text('1080p Ultra', format='.1f')
)

chart2 = (barras2 + texto2).properties(
    title=alt.TitleParams(
        text='Desempenho',
        anchor='middle',
        fontSize=20,
    ),
    width=900,
    height=500,
)

st.altair_chart(chart2, use_container_width=True)

st.dataframe(df, use_container_width=True, hide_index=True)
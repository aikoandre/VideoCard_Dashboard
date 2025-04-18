import pandas as pd

def carregar_dados(caminho_csv):
  df = pd.read_csv(caminho_csv, encoding='latin1')
  df.columns = [col.replace('�', 'í') for col in df.columns]
  df['Valor'] = (
    df['Valor']
    .astype(str)
    .str.replace('R$', '', regex=False)
    .str.replace(',', '.', regex=False)  # Troca vírgula por ponto
    .str.replace('.', '', regex=False)   # Remove pontos dos milhares
    .str.strip()
    .astype(float)
  )

  df['1080p Ultra'] = df['1080p Ultra'].astype(str).str.replace(',', '.').astype(float)
  return df
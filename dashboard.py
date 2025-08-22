import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Indicadores Operacionais",
    page_icon="🎨",
    layout="wide"
)

# --- IDENTIDADE VISUAL E ESTILOS (CSS) COM AS NOVAS CORES ---
st.markdown("""
<style>
    /* FUNDO DA PÁGINA */
    .main .block-container {
        background-color: #FCE4EC; /* Fundo claro da página */
    }
    
    /* CABEÇALHO (TÍTULO PRINCIPAL) */
    .main > div:first-child {
        background-color: #D81B60; /* Fundo do cabeçalho */
        padding: 1rem 1rem 0 1rem;
        border-radius: 0 0 10px 10px;
    }
    h1 {
        color: white !important;
        text-align: center;
        padding-bottom: 15px;
    }
    
    /* ESTILO GERAL DOS CARDS */
    .metric-card {
        background-color: #FFFFFF; /* Fundo dos cards */
        border: 2px solid #FF9800; /* Borda laranja dos cards */
        border-radius: 10px;
        padding: 25px 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* TÍTULOS E TEXTOS */
    .page-header { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px; }
    .card-title { font-size: 18px; font-weight: bold; color: #757575; margin-bottom: 10px; } /* Texto cinza */
    .metric-value { font-size: 36px; font-weight: bold; color: #333333; }
    .metric-subtext { font-size: 14px; color: #757575; } /* Texto cinza */
    .text-red { color: #D32F2F !important; font-weight: bold; } /* Texto vermelho */

    /* BOTÕES */
    .stButton>button {
        background-color: #F06292; /* Botões rosa escuro */
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #D81B60;
        color: white;
    }

    /* BARRA LATERAL */
    [data-testid="stSidebar"] { background-color: #FFFFFF; }

</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES AUXILIARES ---

@st.cache_data
def carregar_dados(arquivo_carregado):
    try:
        df = pd.read_excel(arquivo_carregado) if arquivo_carregado.name.endswith(('.xls', '.xlsx')) else pd.read_csv(arquivo_carregado)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}"); return None

    colunas_map = {
        'data_atendimento': 'Data', 'Total de entrantes': 'Entrantes',
        'Atendidos': 'Atendidos', 'Total de tickets Resolvidos': 'Resolvidos',
        '% Avaliações CSAT 4 e 5': 'CSAT_pc', 'TMA': 'TMA_str', 'TMR': 'TMR_str',
        'Líder': 'Líder', 'agente_email': 'Operador'
    }
    try:
        df = df.rename(columns=colunas_map)
    except Exception:
        st.error("Erro ao renomear colunas."); return None

    def clean_percentage(pc):
        if isinstance(pc, str): return float(pc.replace('%', '').replace(',', '.'))
        return float(pc) * 100 if isinstance(pc, (int, float)) else 0

    def tempo_para_segundos(ts):
        if isinstance(ts, (str, int, float)):
            ts = str(ts); parts = ts.split(':')
            if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
        return np.nan

    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['CSAT'] = df['CSAT_pc'].apply(clean_percentage)
    df['TMA_segundos'] = df['TMA_str'].apply(tempo_para_segundos)
    df['TMR_segundos'] = df['TMR_str'].apply(tempo_para_segundos)
    return df

def segundos_para_tempo_str(s):
    if pd.isna(s): return "00:00"
    minutos, segundos = divmod(int(s), 60)
    return f"{minutos:02d}:{segundos:02d}"

# --- PÁGINAS DO DASHBOARD ---

def pagina_geral(df):
    st.markdown('<p class="page-header">Visão Geral da Operação</p>', unsafe_allow_html=True)
    atendidos, resolvidos = df['Atendidos'].sum(), df['Resolvidos'].sum()
    taxa_res = (resolvidos / atendidos) * 100 if atendidos > 0 else 0
    csat_medio = (df['CSAT'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    tma_medio = (df['TMA_segundos'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="metric-card"><span class="card-title">Taxa de Resolução</span><p class="metric-value">{taxa_res:.1f}%</p><span class="metric-subtext">{int(resolvidos)} de {int(atendidos)}</span></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><span class="card-title">CSAT Médio</span><p class="metric-value">{csat_medio:.1f}%</p><span class="metric-subtext">Satisfação do Cliente</span></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><span class="card-title">TMA Médio</span><p class="metric-value">{segundos_para_tempo_str(tma_medio)}</p><span class="metric-subtext">Tempo de Atendimento</span></div>', unsafe_allow_html=True)

def pagina_lideres(df):
    st.markdown('<p class="page-header">Desempenho por Líder</p>', unsafe_allow_html=True)
    stats = df.groupby('Líder').agg(Atendidos=('Atendidos', 'sum'), Resolvidos=('Resolvidos', 'sum')).reset_index()
    stats['Taxa_Resolucao'] = (stats['Resolvidos'] / stats['Atendidos']) * 100
    
    cols = st.columns(len(stats))
    for i, row in stats.iterrows():
        cols[i].markdown(f'<div class="metric-card"><p class="card-title" style="font-size: 20px;">{row["Líder"]}</p><p class="metric-value">{row.Taxa_Resolucao:.1f}%</p><span class="metric-subtext">Resolução</span></div>', unsafe_allow_html=True)

def pagina_ranking(df):
    st.markdown('<p class="page-header">Ranking Geral de Agentes</p>', unsafe_allow_html=True)
    stats = df.groupby('Operador').agg(Atendidos=('Atendidos', 'sum'), Resolvidos=('Resolvidos', 'sum')).reset_index()
    stats['% Resolvidos'] = (stats['Resolvidos'] / stats['Atendidos']) * 100
    ranking = stats.sort_values(by='% Resolvidos', ascending=False).reset_index(drop=True)
    st.dataframe(ranking[['Operador', '% Resolvidos']], use_container_width=True)

def pagina_melhorias(df):
    st.markdown('<p class="page-header">Oportunidades de Melhoria</p>', unsafe_allow_html=True)
    
    media_csat_geral = (df['CSAT'] * df['Atendidos']).sum() / df['Atendidos'].sum()
    
    stats = df.groupby('Operador').agg(Atendidos=('Atendidos', 'sum'), CSAT_pond=('CSAT', lambda x: (x * df.loc[x.index, 'Atendidos']).sum())).reset_index()
    stats['CSAT'] = stats['CSAT_pond'] / stats['Atendidos']
    
    detratores = stats.sort_values(by='CSAT', ascending=True).head(3)
    detratores['delta'] = detratores['CSAT'] - media_csat_geral
    
    cols = st.columns(3)
    for i, row in detratores.iterrows():
        cols[i].markdown(f"""
        <div class="metric-card">
            <p class="card-title">{row['Operador'].split('@')[0]}</p>
            <p class="metric-value">{row.CSAT:.1f}%</p>
            <span class="metric-subtext text-red">{row.delta:.1f}% vs média</span>
        </div>""", unsafe_allow_html=True)
        cols[i].button("Criar Plano de Ação", key=f"btn_{i}")

# --- APLICAÇÃO PRINCIPAL ---
def main():
    st.title("Dashboard de Indicadores")
    
    uploaded_file = st.sidebar.file_uploader("Faça o upload do seu arquivo", type=['csv', 'xlsx', 'xls'])

    if uploaded_file:
        df = carregar_dados(uploaded_file)
        if df is not None:
            st.sidebar.success("Arquivo carregado!")
            st.sidebar.header("Navegação")
            paginas = ["Visão Geral", "Desempenho por Líder", "Ranking Geral", "Oportunidades de Melhoria"]
            pagina_selecionada = st.sidebar.radio("Escolha uma página:", paginas)
            
            if pagina_selecionada == "Visão Geral": pagina_geral(df)
            elif pagina_selecionada == "Desempenho por Líder": pagina_lideres(df)
            elif pagina_selecionada == "Ranking Geral": pagina_ranking(df)
            elif pagina_selecionada == "Oportunidades de Melhoria": pagina_melhorias(df)
    else:
        st.info("Para começar, faça o upload de um arquivo na barra lateral.")

if __name__ == '__main__':
    main()

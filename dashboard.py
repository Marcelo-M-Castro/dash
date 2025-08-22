import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Performance Operacional",
    page_icon="🚀",
    layout="wide"
)

# --- ESTILOS VISUAIS (CSS) ---
st.markdown("""
<style>
    /* FUNDO E LAYOUT */
    .main .block-container {
        padding: 2rem;
        background-color: #F8F9FA;
    }
    
    /* CABEÇALHO E TÍTULOS */
    .main > div:first-child {
        background-color: #004D7A;
        padding: 1rem;
        border-radius: 0 0 10px 10px;
    }
    h1 {
        color: white !important;
        text-align: center;
    }
    .page-header {
        font-size: 28px;
        font-weight: bold;
        color: #004D7A;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 10px;
    }

    /* CARTÕES DE MÉTRICA */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 20px;
        text-align: center;
        border-top: 5px solid #007ACC;
        height: 100%;
    }
    .metric-card.good { border-top-color: #28A745; }
    .metric-card.warning { border-top-color: #FFC107; }
    
    .card-title {
        font-size: 16px;
        font-weight: bold;
        color: #6C757D;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #343A40;
    }
    
    /* BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }
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
        'data_atendimento': 'Data', 'Total de entrantes': 'Entrantes', 'Atendidos': 'Atendidos',
        'Total de Tickets': 'Tickets', 'Total de tickets Resolvidos': 'Resolvidos',
        '% Avaliações CSAT 4 e 5': 'CSAT_pc', '% Atendidos 1 min': 'SLA_pc',
        'TMA': 'TMA_str', 'TMR': 'TMR_str', 'Líder': 'Líder', 'agente_email': 'Operador'
    }
    try:
        df = df.rename(columns=colunas_map)
    except Exception:
        st.error("Erro ao renomear colunas."); return None

    def clean_percentage(pc):
        if isinstance(pc, str): return float(pc.replace('%', '').replace(',', '.'))
        return float(pc) * 100 if isinstance(pc, (int, float)) else 0

    def tempo_para_segundos(ts):
        if isinstance(ts, str):
            parts = ts.split(':');
            if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
        return np.nan

    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['CSAT'] = df['CSAT_pc'].apply(clean_percentage)
    df['SLA'] = df['SLA_pc'].apply(clean_percentage)
    df['TMA_segundos'] = df['TMA_str'].apply(tempo_para_segundos)
    return df

def segundos_para_tempo_str(s):
    if pd.isna(s): return "00:00"
    minutos, segundos = divmod(int(s), 60)
    return f"{minutos:02d}:{segundos:02d}"

# --- PÁGINAS DO DASHBOARD ---

def pagina_geral(df):
    st.markdown('<p class="page-header">Visão Geral da Operação</p>', unsafe_allow_html=True)
    
    # Cálculos ponderados
    atendidos = df['Atendidos'].sum()
    resolvidos = df['Resolvidos'].sum()
    taxa_res = (resolvidos / atendidos) * 100 if atendidos > 0 else 0
    csat_medio = (df['CSAT'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    tma_medio = (df['TMA_segundos'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    sla_medio = (df['SLA'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    total_tickets = df['Tickets'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card good"><span class="card-title">📈 Taxa de Resolução</span><p class="metric-value">{taxa_res:.1f}%</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card good"><span class="card-title">😊 CSAT Médio</span><p class="metric-value">{csat_medio:.1f}%</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card warning"><span class="card-title">⏱️ TMA Médio</span><p class="metric-value">{segundos_para_tempo_str(tma_medio)}</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card good"><span class="card-title">⚡ Atend. em 1 min (SLA)</span><p class="metric-value">{sla_medio:.1f}%</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<p class="page-header" style="font-size: 22px;">Tendência Diária</p>', unsafe_allow_html=True)
    
    daily_stats = df.groupby('Data').agg(
        Atendimentos=('Atendidos', 'sum'),
        TMA_total=('TMA_segundos', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        Atendidos_total=('Atendidos', 'sum')
    ).reset_index()
    daily_stats['TMA Médio (seg)'] = daily_stats['TMA_total'] / daily_stats['Atendidos_total']
    
    base = alt.Chart(daily_stats).encode(x=alt.X('Data:T', title='Data'))
    line_atend = base.mark_line(color='#007ACC', point=True).encode(y=alt.Y('Atendimentos:Q', title='Atendimentos'))
    line_tma = base.mark_line(color='#FFC107', point=True).encode(y=alt.Y('TMA Médio (seg):Q', title='TMA Médio (seg)'))
    
    chart = alt.layer(line_atend, line_tma).resolve_scale(y='independent').interactive()
    st.altair_chart(chart, use_container_width=True)


def pagina_ranking(df):
    st.markdown('<p class="page-header">Ranking de Performance Individual</p>', unsafe_allow_html=True)
    
    stats = df.groupby('Operador').agg(
        Atendidos=('Atendidos', 'sum'),
        Resolvidos=('Resolvidos', 'sum'),
        CSAT_wsum=('CSAT', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        SLA_wsum=('SLA', lambda x: (x * df.loc[x.index, 'Atendidos']).sum())
    ).reset_index()

    stats['Taxa de Resolução'] = (stats['Resolvidos'] / stats['Atendidos']) * 100
    stats['CSAT'] = stats['CSAT_wsum'] / stats['Atendidos']
    stats['SLA'] = stats['SLA_wsum'] / stats['Atendidos']
    
    ranking = stats.sort_values(by='Taxa de Resolução', ascending=False).reset_index(drop=True)
    st.dataframe(
        ranking[['Operador', 'Taxa de Resolução', 'CSAT', 'SLA', 'Atendidos']],
        use_container_width=True,
        column_config={
            "Taxa de Resolução": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
            "CSAT": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
            "SLA": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
        }
    )

# --- APLICAÇÃO PRINCIPAL ---
def main():
    st.title("Performance Operacional")
    
    uploaded_file = st.sidebar.file_uploader("Faça o upload do seu arquivo", type=['csv', 'xlsx', 'xls'])

    if uploaded_file:
        df = carregar_dados(uploaded_file)
        if df is not None:
            st.sidebar.success("Dados carregados!")
            st.sidebar.header("Navegação")
            paginas = ["Visão Geral", "Ranking Individual"]
            pagina_selecionada = st.sidebar.radio("Escolha uma página:", paginas)
            
            if pagina_selecionada == "Visão Geral":
                pagina_geral(df)
            elif pagina_selecionada == "Ranking Individual":
                pagina_ranking(df)
    else:
        st.info("Para começar, faça o upload de um arquivo de dados na barra lateral.")

if __name__ == '__main__':
    main()

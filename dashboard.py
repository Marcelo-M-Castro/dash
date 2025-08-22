import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ============================
# CONFIGURAÇÃO DA PÁGINA
# ============================
st.set_page_config(
    page_title="Dashboard de Performance Operacional",
    page_icon="📊",
    layout="wide"
)

# ============================
# ESTILOS VISUAIS (CSS)
# ============================
st.markdown("""
<style>
/* FUNDO E LAYOUT */
.main .block-container { padding: 2rem; background-color: #F7F9FB; }
/* CABEÇALHO */
.main > div:first-child { background-color: #0B2B40; padding: 1.5rem; border-radius: 0 0 10px 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
h1 { color: white !important; text-align: center; }
/* TÍTULOS */
.page-header { font-size: 26px; font-weight: bold; color: #0B2B40; margin-bottom: 1rem; }
.section-header { font-size: 20px; font-weight: bold; color: #38A3A5; margin-top: 2rem; margin-bottom: 1rem; border-bottom: 2px solid #E0E0E0; padding-bottom: 10px; }
/* CARTÕES DE MÉTRICA */
.metric-card, .metric-card-leader { background-color: #FFFFFF; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); padding: 15px; height: 100%; }
.metric-card { border-left: 6px solid #38A3A5; }
.metric-card-leader { border-top: 4px solid #004D7A; }
.card-title { font-size: 16px; color: #6C757D; }
.metric-value { font-size: 28px; font-weight: bold; color: #0B2B40; }
.metric-delta { font-size: 14px; }
.text-green { color: #28a745; }
.text-red { color: #d32f2f; }
/* BARRA LATERAL */
[data-testid="stSidebar"] { background-color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# ============================
# FUNÇÕES AUXILIARES
# ============================
@st.cache_data
def carregar_dados(arquivo_carregado):
    try:
        if arquivo_carregado.name.endswith(('xls','xlsx')):
            df = pd.read_excel(arquivo_carregado)
        else:
            df = pd.read_csv(arquivo_carregado)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

    colunas_map = {
        'data_atendimento': 'Data',
        'Total de entrantes': 'Entrantes',
        'Atendidos': 'Atendidos',
        'Total de Tickets': 'Tickets',
        'Total de tickets Resolvidos': 'Resolvidos',
        '% Avaliações CSAT 4 e 5': 'CSAT_pc',
        '% Atendidos 1 min': 'SLA_pc',
        'TMA': 'TMA_str',
        'TMR': 'TMR_str',
        'Líder': 'Líder',
        'agente_email': 'Operador'
    }

    try:
        df = df.rename(columns=colunas_map)
    except Exception:
        st.error("Erro ao renomear colunas.")
        return None

    # Conversões
    def clean_percentage(pc):
        if isinstance(pc, str):
            return float(pc.replace('%','').replace(',','.'))
        if isinstance(pc, (int,float)):
            return float(pc)
        return 0

    def tempo_para_segundos(ts):
        if isinstance(ts,str):
            parts = ts.split(':')
            if len(parts) == 3:
                return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            if len(parts) == 2:
                return int(parts[0])*60 + int(parts[1])
        return np.nan

    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['CSAT'] = df['CSAT_pc'].apply(clean_percentage)
    df['SLA'] = df['SLA_pc'].apply(clean_percentage)
    df['TMA_segundos'] = df['TMA_str'].apply(tempo_para_segundos)
    df['TMR_segundos'] = df['TMR_str'].apply(tempo_para_segundos)

    return df

def segundos_para_tempo_str(s):
    if pd.isna(s):
        return "00:00"
    minutos, segundos = divmod(int(s),60)
    return f"{minutos:02d}:{segundos:02d}"

# ============================
# PÁGINAS DO DASHBOARD
# ============================

def pagina_geral(df):
    st.markdown('<p class="page-header">Visão Geral da Operação</p>', unsafe_allow_html=True)

    entrantes = df['Entrantes'].sum()
    atendidos = df['Atendidos'].sum()
    resolvidos = df['Resolvidos'].sum()
    taxa_res = (resolvidos/atendidos*100) if atendidos>0 else 0
    csat = (df['CSAT']*df['Atendidos']).sum()/atendidos if atendidos>0 else 0
    tma = (df['TMA_segundos']*df['Atendidos']).sum()/atendidos if atendidos>0 else 0
    tmr = (df['TMR_segundos']*df['Atendidos']).sum()/atendidos if atendidos>0 else 0
    media_dia = atendidos/df['Data'].nunique() if df['Data'].nunique()>0 else 0

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("📞 Total de Entrantes", f"{int(entrantes):,}")
    col2.metric("🤝 Total Atendidos", f"{int(atendidos):,}")
    col3.metric("✅ Total Resolvidos", f"{int(resolvidos):,}")
    col4.metric("📈 Taxa de Resolução (TMPR)", f"{taxa_res:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    col5,col6,col7,col8 = st.columns(4)
    col5.metric("😊 CSAT Médio", f"{csat:.1f}%")
    col6.metric("⏱️ TMA Médio", segundos_para_tempo_str(tma))
    col7.metric("⏱️ TMR Médio", segundos_para_tempo_str(tmr))
    col8.metric("📅 Média Atendimentos/Dia", f"{media_dia:.0f}")

    st.markdown('<p class="section-header">Tendência Diária</p>', unsafe_allow_html=True)
    daily_stats = df.groupby('Data').agg(Atendimentos=('Atendidos','sum')).reset_index()
    chart = alt.Chart(daily_stats).mark_area(
        line={'color':'#38A3A5'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='white', offset=0), alt.GradientStop(color='#38A3A5', offset=1)],
            x1=1,x2=1,y1=1,y2=0
        )
    ).encode(x=alt.X('Data:T', title='Data'), y=alt.Y('Atendimentos:Q', title='Nº de Atendimentos')).interactive()
    st.altair_chart(chart, use_container_width=True)

def pagina_melhorias(df):
    st.markdown('<p class="page-header">Oportunidades de Melhoria</p>', unsafe_allow_html=True)

    # Converter percentuais
    df['% Total de tickets Resolvidos'] = df['% Total de tickets Resolvidos'].str.rstrip('%').astype(float)
    df['% Avaliações CSAT 4 e 5'] = df['% Avaliações CSAT 4 e 5'].str.rstrip('%').astype(float)
    df['% Atendidos 1 min'] = df['% Atendidos 1 min'].str.rstrip('%').astype(float)

    media_res = df['% Total de tickets Resolvidos'].mean()
    media_csat = df['% Avaliações CSAT 4 e 5'].mean()
    media_sla = df['% Atendidos 1 min'].mean()

    # Agrupar por operador
    stats = df.groupby('agente_email', as_index=False

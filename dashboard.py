import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ============================
# CONFIGURAÇÃO DA PÁGINA
# ============================
st.set_page_config(
    page_title="Dashboard de Performance",
    page_icon="📊",
    layout="wide"
)

# ============================
# ESTILOS MODERNOS
# ============================
st.markdown("""
<style>
/* FUNDO PRINCIPAL */
.main .block-container {
    padding: 2rem;
    background-color: #F5F7FA;
}

/* CABEÇALHO */
.main > div:first-child {
    background-color: #1F3C59;
    padding: 1.5rem;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
h1 { color: white !important; text-align: center; font-weight: 700; }

/* TÍTULOS */
.page-header { font-size: 28px; font-weight: 700; color: #1F3C59; margin-bottom: 1rem; }
.section-header { font-size: 22px; font-weight: 600; color: #007ACC; margin-top: 2rem; margin-bottom: 1rem; border-bottom: 2px solid #E0E0E0; padding-bottom: 10px; }

/* CARTÕES DE MÉTRICAS */
.metric-card, .metric-card-leader {
    background-color: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
    padding: 20px;
    margin-bottom: 1rem;
    transition: transform 0.2s;
}
.metric-card:hover, .metric-card-leader:hover { transform: translateY(-3px); }
.metric-card { border-left: 6px solid #007ACC; }
.metric-card-leader { border-top: 5px solid #FF6F61; }
.card-title { font-size: 18px; font-weight: 600; color: #333; margin-bottom: 0.5rem; }
.metric-value { font-size: 28px; font-weight: 700; color: #1F3C59; margin-bottom: 0.3rem; }
.metric-delta { font-size: 14px; font-weight: 500; }
.text-green { color: #28a745; font-weight: 600; }
.text-red { color: #d32f2f; font-weight: 600; }

/* BARRA LATERAL */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ============================
# FUNÇÕES AUXILIARES
# ============================

@st.cache_data
def carregar_dados(arquivo):
    try:
        if arquivo.name.endswith(('xls','xlsx')):
            df = pd.read_excel(arquivo)
        else:
            df = pd.read_csv(arquivo)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return None

    # Renomear colunas
    rename_map = {
        'data_atendimento':'Data',
        'Total de entrantes':'Entrantes',
        'Atendidos':'Atendidos',
        'Total de Tickets':'Tickets',
        'Total de tickets Resolvidos':'Resolvidos',
        '% Avaliações CSAT 4 e 5':'CSAT_pc',
        '% Atendidos 1 min':'SLA_pc',
        'TMA':'TMA_str',
        'TMR':'TMR_str',
        'Líder':'Líder',
        'agente_email':'Operador'
    }
    df = df.rename(columns=rename_map)

    # Conversão de percentuais e tempos
    def clean_pct(x):
        if isinstance(x,str):
            return float(x.strip('%').replace(',','.'))
        return float(x or 0)

    def tempo_segundos(ts):
        if isinstance(ts,str):
            parts = ts.split(':')
            if len(parts)==3:
                return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            if len(parts)==2:
                return int(parts[0])*60 + int(parts[1])
        return np.nan

    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['CSAT'] = df['CSAT_pc'].apply(clean_pct)
    df['SLA'] = df['SLA_pc'].apply(clean_pct)
    df['TMA_segundos'] = df['TMA_str'].apply(tempo_segundos)
    df['TMR_segundos'] = df['TMR_str'].apply(tempo_segundos)

    return df

def segundos_para_str(seg):
    if pd.isna(seg):
        return "00:00"
    m,s = divmod(int(seg),60)
    return f"{m:02d}:{s:02d}"

# ============================
# PÁGINAS
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

    # KPIs principais
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("📞 Entrantes", f"{int(entrantes):,}")
    col2.metric("🤝 Atendidos", f"{int(atendidos):,}")
    col3.metric("✅ Resolvidos", f"{int(resolvidos):,}")
    col4.metric("📈 Taxa de Resolução", f"{taxa_res:.1f}%")

    col5,col6,col7,col8 = st.columns(4)
    col5.metric("😊 CSAT Médio", f"{csat:.1f}%")
    col6.metric("⏱️ TMA Médio", segundos_para_str(tma))
    col7.metric("⏱️ TMR Médio", segundos_para_str(tmr))
    col8.metric("📅 Média Atendimentos/Dia", f"{media_dia:.0f}")

    st.markdown('<p class="section-header">Tendência Diária</p>', unsafe_allow_html=True)
    trend = df.groupby('Data').agg(Atendidos=('Atendidos','sum')).reset_index()
    chart = alt.Chart(trend).mark_line(point=True).encode(
        x='Data:T',
        y='Atendidos:Q',
        tooltip=['Data','Atendidos']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def pagina_melhorias(df):
    st.markdown('<p class="page-header">Oportunidades de Melhoria</p>', unsafe_allow_html=True)
    
    # Agrupar por operador
    stats = df.groupby('Operador', as_index=False).agg(
        Atendidos=('Atendidos','sum'),
        Resolvidos=('Resolvidos','sum'),
        CSAT_wsum=('CSAT', lambda x: (x*df.loc[x.index,'Atendidos']).sum()),
        SLA_wsum=('SLA', lambda x: (x*df.loc[x.index,'Atendidos']).sum())
    )
    stats['% Resolvidos'] = stats['Resolvidos']/stats['Atendidos']*100
    stats['CSAT'] = stats['CSAT_wsum']/stats['Atendidos']
    stats['Atend_1min'] = stats['SLA_wsum']/stats['Atendidos']

    # Métricas médias
    media_res = stats['% Resolvidos'].mean()
    media_csat = stats['CSAT'].mean()
    media_sla = stats['Atend_1min'].mean()

    detratores = stats.sort_values('CSAT').head(9)  # top 9
    st.markdown("### Agentes com menor CSAT")

    # Cards responsivos (3 por linha)
    n_cols = 3
    for i in range(0,len(detratores), n_cols):
        row = detratores.iloc[i:i+n_cols]
        cols = st.columns(len(row))
        for j, (_, r) in enumerate(row.iterrows()):
            delta_res = r['% Resolvidos'] - media_res
            delta_csat = r['CSAT'] - media_csat
            delta_sla = r['Atend_1min'] - media_sla
            with cols[j]:
                st.markdown(f"""
                    <div class="metric-card-leader">
                        <p class="card-title">{r['Operador'].split('@')[0]}</p>
                        <hr>
                        <p><strong>CSAT:</strong> {r['CSAT']:.1f}% <span class="metric-delta {'text-green' if delta_csat>=0 else 'text-red'}">({delta_csat:+.1f}%)</span></p>
                        <p><strong>Resolução:</strong> {r['% Resolvidos']:.1f}% <span class="metric-delta {'text-green' if delta_res>=0 else 'text-red'}">({delta_res:+.1f}%)</span></p>
                        <p><strong>Atend. 1 min:</strong> {r['Atend_1min']:.1f}% <span class="metric-delta {'text-green' if delta_sla>=0 else 'text-red'}">({delta_sla:+.1f}%)</span></p>
                    </div>
                """, unsafe_allow_html=True)

# ============================
# APP PRINCIPAL
# ============================

def main():
    st.title("Dashboard de Performance")

    uploaded_file = st.sidebar.file_uploader("Carregue o arquivo CSV/XLSX", type=['csv','xlsx','xls'])
    if uploaded_file:
        df = carregar_dados(uploaded_file)
        if df is not None:
            st.sidebar.success("Dados carregados!")
            paginas = ["Visão Geral", "Oportunidades de Melhoria"]
            pagina_selecionada = st.sidebar.radio("Selecione a página:", paginas)
            if pagina_selecionada == "Visão Geral":
                pagina_geral(df)
            else:
                pagina_melhorias(df)
        else:
            st.sidebar.error("Erro ao carregar os dados.")
    else:
        st.info("Por favor, carregue um arquivo para iniciar a análise.")

if __name__ == "__main__":
    main()

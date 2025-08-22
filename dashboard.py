import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Performance Operacional",
    page_icon="📊",
    layout="wide"
)

# --- ESTILOS VISUAIS (CSS) ---
st.markdown("""
<style>
    /* FUNDO E LAYOUT */
    .main .block-container {
        padding: 2rem;
        background-color: #F7F9FB;
    }
    
    /* CABEÇALHO E TÍTULOS */
    .main > div:first-child {
        background-color: #0B2B40; /* Azul Escuro */
        padding: 1.5rem;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    h1 {
        color: white !important;
        text-align: center;
    }
    .page-header {
        font-size: 26px;
        font-weight: bold;
        color: #0B2B40;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        color: #38A3A5; /* Teal */
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 10px;
    }

    /* CARTÕES DE MÉTRICA */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 15px;
        border-left: 6px solid #38A3A5; /* Borda Teal */
        height: 100%;
    }
    .metric-card-leader {
        background-color: #FFFFFF;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 20px;
        border-top: 4px solid #004D7A;
    }
    
    .card-title { font-size: 16px; color: #6C757D; }
    .metric-value { font-size: 28px; font-weight: bold; color: #0B2B40; }
    .metric-delta { font-size: 14px; }
    .text-green { color: #28a745; }
    .text-red { color: #d32f2f; }

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
            parts = ts.split(':')
            if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
        return np.nan

    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['CSAT'] = df['CSAT_pc'].apply(clean_percentage)
    df['SLA'] = df['SLA_pc'].apply(clean_percentage)
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

    # Cálculos
    entrantes, atendidos, resolvidos = df['Entrantes'].sum(), df['Atendidos'].sum(), df['Resolvidos'].sum()
    taxa_res = (resolvidos / atendidos) * 100 if atendidos > 0 else 0
    csat = (df['CSAT'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    tma = (df['TMA_segundos'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    tmr = (df['TMR_segundos'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    media_dia = atendidos / df['Data'].nunique() if df['Data'].nunique() > 0 else 0

    # Layout em 2 linhas
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📞 TOTAL DE ENTRANTES", f"{int(entrantes):,}")
    with col2: st.metric("🤝 TOTAL ATENDIDOS", f"{int(atendidos):,}")
    with col3: st.metric("✅ TOTAL RESOLVIDOS", f"{int(resolvidos):,}")
    with col4: st.metric("📈 TAXA DE RESOLUÇÃO (TMPR)", f"{taxa_res:.1f}%")
    
    st.markdown("<br>", unsafe_allow_html=True) # Espaçador
    
    col5, col6, col7, col8 = st.columns(4)
    with col5: st.metric("😊 CSAT MÉDIO", f"{csat:.1f}%")
    with col6: st.metric("⏱️ TMA MÉDIO", segundos_para_tempo_str(tma))
    with col7: st.metric(" respond TMR MÉDIO", segundos_para_tempo_str(tmr))
    with col8: st.metric("📅 MÉDIA DE ATENDIMENTO/DIA", f"{media_dia:.0f}")

    st.markdown('<p class="section-header">Tendência Diária</p>', unsafe_allow_html=True)
    daily_stats = df.groupby('Data').agg(Atendimentos=('Atendidos', 'sum')).reset_index()
    chart = alt.Chart(daily_stats).mark_area(
        line={'color':'#38A3A5'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='white', offset=0), alt.GradientStop(color='#38A3A5', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Atendimentos:Q', title='Nº de Atendimentos')
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def pagina_analise_lideres(df):
    st.markdown('<p class="page-header">Análise de Desempenho por Líder</p>', unsafe_allow_html=True)
    
    stats = df.groupby('Líder').agg(
        Entrantes=('Entrantes', 'sum'), Atendidos=('Atendidos', 'sum'), Resolvidos=('Resolvidos', 'sum'),
        Atendidos_sum_csat=('Atendidos', 'sum'), CSAT_wsum=('CSAT', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        TMA_wsum=('TMA_segundos', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        TMR_wsum=('TMR_segundos', lambda x: (x * df.loc[x.index, 'Atendidos']).sum())
    ).reset_index()

    stats['Taxa Resolvidos'] = (stats['Resolvidos'] / stats['Atendidos']) * 100
    stats['CSAT'] = stats['CSAT_wsum'] / stats['Atendidos_sum_csat']
    stats['TMA'] = stats['TMA_wsum'] / stats['Atendidos_sum_csat']
    stats['TMR'] = stats['TMR_wsum'] / stats['Atendidos_sum_csat']
    
    # Cards de Desempenho
    st.markdown('<p class="section-header">Desempenho Individual</p>', unsafe_allow_html=True)
    cols = st.columns(len(stats))
    for i, row in stats.iterrows():
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card-leader">
                <p class="card-title" style="font-size: 20px; text-align: center; font-weight: bold;">{row['Líder']}</p>
                <hr>
                <p style="text-align: left;"><strong>Resolução:</strong> <span style="float: right; font-weight: bold;">{row['Taxa Resolvidos']:.1f}%</span></p>
                <p style="text-align: left;"><strong>CSAT:</strong> <span style="float: right; font-weight: bold;">{row['CSAT']:.1f}%</span></p>
                <p style="text-align: left;"><strong>TMA:</strong> <span style="float: right; font-weight: bold;">{segundos_para_tempo_str(row['TMA'])}</span></p>
                <p style="text-align: left;"><strong>TMR:</strong> <span style="float: right; font-weight: bold;">{segundos_para_tempo_str(row['TMR'])}</span></p>
                <p style="text-align: left;"><strong>Total Atendidos:</strong> <span style="float: right; font-weight: bold;">{int(row['Atendidos'])}</span></p>
            </div>
            """, unsafe_allow_html=True)

    # Tabela de Ranking
    st.markdown('<p class="section-header">Ranking Geral de Desempenho</p>', unsafe_allow_html=True)
    ranking = stats[['Líder', 'Taxa Resolvidos', 'CSAT', 'TMA', 'TMR']].set_index('Líder')
    st.dataframe(
        ranking.style
        .format({'Taxa Resolvidos': '{:.1f}%', 'CSAT': '{:.1f}%', 'TMA': segundos_para_tempo_str, 'TMR': segundos_para_tempo_str})
        .highlight_max(subset=['Taxa Resolvidos', 'CSAT'], color='#D4EDDA', axis=0) # Verde para o melhor
        .highlight_min(subset=['TMA', 'TMR'], color='#D4EDDA', axis=0) # Verde para o menor tempo
    )

def pagina_melhorias(df):
    st.markdown('<p class="page-header">Oportunidades de Melhoria</p>', unsafe_allow_html=True)
    
    # Médias Gerais
    media_csat = (df['CSAT'] * df['Atendidos']).sum() / df['Atendidos'].sum()
    media_sla = (df['SLA'] * df['Atendidos']).sum() / df['Atendidos'].sum()
    media_res = (df['Resolvidos'].sum() / df['Atendidos'].sum()) * 100
    
    stats = df.groupby('Operador').agg(
        Atendidos=('Atendidos', 'sum'), Resolvidos=('Resolvidos', 'sum'),
        CSAT_wsum=('CSAT', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        SLA_wsum=('SLA', lambda x: (x * df.loc[x.index, 'Atendidos']).sum())
    ).reset_index()

    stats['% Resolvidos'] = (stats['Resolvidos'] / stats['Atendidos']) * 100
    stats['CSAT'] = stats['CSAT_wsum'] / stats['Atendidos']
    stats['Atend. 1 min'] = stats['SLA_wsum'] / stats['Atendidos']
    
    detratores = stats.sort_values(by='CSAT', ascending=True).head(3)
    
    st.markdown("Abaixo estão os 3 agentes com menor CSAT, destacando pontos de atenção.")
    
    cols = st.columns(3)
    for i, row in detratores.iterrows():
        delta_res = row['% Resolvidos'] - media_res
        delta_csat = row['CSAT'] - media_csat
        delta_sla = row['Atend. 1 min'] - media_sla
        
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card-leader">
                <p class="card-title" style="text-align: center; font-weight: bold;">{row['Operador'].split('@')[0]}</p>
                <hr>
                <p><strong>CSAT:</strong> {row['CSAT']:.1f}% <span class="metric-delta { 'text-green' if delta_csat >= 0 else 'text-red' }">({delta_csat:+.1f}%)</span></p>
                <p><strong>Resolução:</strong> {row['% Resolvidos']:.1f}% <span class="metric-delta { 'text-green' if delta_res >= 0 else 'text-red' }">({delta_res:+.1f}%)</span></p>
                <p><strong>Atend. 1 min:</strong> {row['Atend. 1 min']:.1f}% <span class="metric-delta { 'text-green' if delta_sla >= 0 else 'text-red' }">({delta_sla:+.1f}%)</span></p>
            </div>
            """, unsafe_allow_html=True)

# --- APLICAÇÃO PRINCIPAL ---
def main():
    st.title("Dashboard de Performance")
    
    uploaded_file = st.sidebar.file_uploader("Faça o upload do seu arquivo", type=['csv', 'xlsx', 'xls'])

    if uploaded_file:
        df = carregar_dados(uploaded_file)
        if df is not None:
            st.sidebar.success("Dados carregados!")
            st.sidebar.header("Navegação")
            paginas = ["Visão Geral", "Análise de Líderes", "Oportunidades de Melhoria"]
            
            # Nota sobre a ausência da coluna 'Categoria'
            if 'Categoria' not in df.columns:
                st.sidebar.warning("A análise por 'Categoria' não está disponível (coluna ausente no arquivo).")
            
            pagina_selecionada = st.sidebar.radio("Escolha uma página:", paginas)
            
            if pagina_selecionada == "Visão Geral": pagina_geral(df)
            elif pagina_selecionada == "Análise de Líderes": pagina_analise_lideres(df)
            elif pagina_selecionada == "Oportunidades de Melhoria": pagina_melhorias(df)
    else:
        st.sidebar.info("Para começar, faça o upload de um arquivo de dados.")
        st.info("Bem-vindo! Por favor, carregue um arquivo na barra lateral para iniciar a análise.")

if __name__ == '__main__':
    main()

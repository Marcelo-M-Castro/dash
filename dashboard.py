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
.main .block-container { padding: 2rem; background-color: #F5F7FA; }

.main > div:first-child { background-color: #1F3C59; padding: 1.5rem; border-radius: 0 0 12px 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
h1 { color: white !important; text-align: center; font-weight: 700; }

.page-header { font-size: 28px; font-weight: 700; color: #1F3C59; margin-bottom: 1rem; }
.section-header { font-size: 22px; font-weight: 600; color: #007ACC; margin-top: 2rem; margin-bottom: 1rem; border-bottom: 2px solid #E0E0E0; padding-bottom: 10px; }

.metric-card { background-color: #FFFFFF; border-radius: 12px; box-shadow: 0 5px 18px rgba(0,0,0,0.08); padding: 20px; margin-bottom: 1rem; border-left: 6px solid #007ACC; }

.card-title { font-size: 18px; font-weight: 600; color: #333; margin-bottom: 0.5rem; }
.metric-value { font-size: 28px; font-weight: 700; color: #1F3C59; margin-bottom: 0.3rem; }

.metric-delta { font-size: 14px; font-weight: 500; }
.text-green { color: #28a745; }
.text-red { color: #d32f2f; }

[data-testid="stSidebar"] { background-color: #FFFFFF; padding: 1rem; }
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
# PÁGINA VISÃO GERAL
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
    chart = alt.Chart(trend).mark_line(point=True, color='#007ACC').encode(
        x='Data:T',
        y='Atendidos:Q',
        tooltip=['Data','Atendidos']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

# ============================
# PÁGINA OPORTUNIDADES DE MELHORIA
# ============================
def pagina_melhorias(df):
    st.markdown('<p class="page-header">Oportunidades de Melhoria</p>', unsafe_allow_html=True)

    # Estatísticas gerais
    media_csat = (df['CSAT']*df['Atendidos']).sum()/df['Atendidos'].sum()
    media_sla = (df['SLA']*df['Atendidos']).sum()/df['Atendidos'].sum()
    media_res = (df['Resolvidos'].sum()/df['Atendidos'].sum())*100

    stats = df.groupby('Operador').agg(
        Atendidos=('Atendidos','sum'),
        Resolvidos=('Resolvidos','sum'),
        CSAT_wsum=('CSAT', lambda x: (x*df.loc[x.index,'Atendidos']).sum()),
        SLA_wsum=('SLA', lambda x: (x*df.loc[x.index,'Atendidos']).sum())
    ).reset_index()

    stats['% Resolvidos'] = stats['Resolvidos']/stats['Atendidos']*100
    stats['CSAT'] = stats['CSAT_wsum']/stats['Atendidos']
    stats['Atend_1min'] = stats['SLA_wsum']/stats['Atendidos']

    # Seleciona os 5 piores agentes por CSAT
    piores = stats.sort_values('CSAT').head(5)

    cols = st.columns(len(piores))
    for i, row in piores.iterrows():
        delta_res = row['% Resolvidos'] - media_res
        delta_csat = row['CSAT'] - media_csat
        delta_sla = row['Atend_1min'] - media_sla

        with cols[i % 5]:  # evita IndexError
            st.markdown(f"""
                <div class="metric-card">
                    <p class="card-title" style="text-align:center">{row['Operador'].split('@')[0]}</p>
                    <hr>
                    <p>CSAT: {row['CSAT']:.1f}% <span class="metric-delta {'text-green' if delta_csat>=0 else 'text-red'}">({delta_csat:+.1f}%)</span></p>
                    <p>Resolução: {row['% Resolvidos']:.1f}% <span class="metric-delta {'text-green' if delta_res>=0 else 'text-red'}">({delta_res:+.1f}%)</span></p>
                    <p>Atend. 1 min: {row['Atend_1min']:.1f}% <span class="metric-delta {'text-green' if delta_sla>=0 else 'text-red'}">({delta_sla:+.1f}%)</span></p>
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
            paginas = ["Visão Geral","Oportunidades de Melhoria"]
            pagina = st.sidebar.radio("Escolha uma página:", paginas)
            if pagina=="Visão Geral":
                pagina_geral(df)
            elif pagina=="Oportunidades de Melhoria":
                pagina_melhorias(df)
        else:
            st.sidebar.error("Erro ao carregar os dados.")
    else:
        st.info("Por favor, carregue um arquivo para iniciar a análise.")

if __name__=="__main__":
    main()

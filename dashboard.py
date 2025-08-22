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

# --- ESTILOS VISUAIS MODERNOS (CSS) ---
st.markdown("""
<style>
/* FUNDO */
.main .block-container {
    padding: 2rem;
    background-color: #F4F6F8;
}

/* CABEÇALHO */
.main > div:first-child {
    background-color: #0B2B40;
    padding: 1.5rem;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
h1 { color: white !important; text-align: center; }

/* TÍTULOS DE SEÇÃO */
.page-header { font-size: 26px; font-weight: bold; color: #0B2B40; margin-bottom: 1rem; }
.section-header { font-size: 20px; font-weight: bold; color: #38A3A5; margin-top: 2rem; margin-bottom: 1rem; border-bottom: 2px solid #E0E0E0; padding-bottom: 8px; }

/* CARDS DE MÉTRICAS */
.metric-card, .metric-card-leader {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.metric-card:hover, .metric-card-leader:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}
.card-title { font-size: 18px; font-weight: bold; color: #0B2B40; margin-bottom: 8px; }
.metric-value { font-size: 26px; font-weight: bold; color: #0B2B40; }
.metric-delta { font-size: 14px; }
.text-green { color: #28a745; }
.text-red { color: #d32f2f; }

/* BARRA LATERAL */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
@st.cache_data
def carregar_dados(arquivo_carregado):
    try:
        if arquivo_carregado.name.endswith(('.xls', '.xlsx')):
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

    df = df.rename(columns=colunas_map)

    def clean_percentage(pc):
        if isinstance(pc, str):
            return float(pc.replace('%', '').replace(',', '.'))
        return float(pc) * 100 if isinstance(pc, (int, float)) else 0

    def tempo_para_segundos(ts):
        if isinstance(ts, str):
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
    minutos, segundos = divmod(int(s), 60)
    return f"{minutos:02d}:{segundos:02d}"

def criar_card(titulo, valor, delta=None, cor_valor="#0B2B40"):
    delta_html = f'<span class="{ "text-green" if delta >=0 else "text-red" }">({delta:+.1f}%)</span>' if delta is not None else ""
    st.markdown(f"""
    <div class="metric-card">
        <p class="card-title">{titulo}</p>
        <p class="metric-value" style="color:{cor_valor};">{valor} {delta_html}</p>
    </div>
    """, unsafe_allow_html=True)

# --- PÁGINAS ---
def pagina_geral(df):
    st.markdown('<p class="page-header">Visão Geral da Operação</p>', unsafe_allow_html=True)

    # Cálculos
    entrantes = df['Entrantes'].sum()
    atendidos = df['Atendidos'].sum()
    resolvidos = df['Resolvidos'].sum()
    taxa_res = (resolvidos / atendidos) * 100 if atendidos > 0 else 0
    csat = (df['CSAT'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    tma = (df['TMA_segundos'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    tmr = (df['TMR_segundos'] * df['Atendidos']).sum() / atendidos if atendidos > 0 else 0
    media_dia = atendidos / df['Data'].nunique() if df['Data'].nunique() > 0 else 0

    # Cards
    cols = st.columns(4)
    criar_card("📞 TOTAL DE ENTRANTES", f"{int(entrantes):,}", cor_valor="#0B2B40")
    criar_card("🤝 TOTAL ATENDIDOS", f"{int(atendidos):,}", cor_valor="#0B2B40")
    criar_card("✅ TOTAL RESOLVIDOS", f"{int(resolvidos):,}", cor_valor="#0B2B40")
    criar_card("📈 TAXA DE RESOLUÇÃO (TMPR)", f"{taxa_res:.1f}%", cor_valor="#0B2B40")

    st.markdown("<br>", unsafe_allow_html=True)

    cols2 = st.columns(4)
    criar_card("😊 CSAT MÉDIO", f"{csat:.1f}%", cor_valor="#38A3A5")
    criar_card("⏱️ TMA MÉDIO", segundos_para_tempo_str(tma), cor_valor="#38A3A5")
    criar_card("⏱️ TMR MÉDIO", segundos_para_tempo_str(tmr), cor_valor="#38A3A5")
    criar_card("📅 MÉDIA ATEND/DIA", f"{media_dia:.0f}", cor_valor="#38A3A5")

    # Gráfico de tendência
    st.markdown('<p class="section-header">Tendência Diária</p>', unsafe_allow_html=True)
    daily_stats = df.groupby('Data').agg(Atendimentos=('Atendidos', 'sum')).reset_index()
    chart = alt.Chart(daily_stats).mark_line(point=True).encode(
        x='Data:T',
        y='Atendimentos:Q',
        tooltip=['Data', 'Atendimentos']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

# --- MAIN ---
def main():
    st.title("Dashboard de Performance")
    uploaded_file = st.sidebar.file_uploader("Faça o upload do seu arquivo", type=['csv', 'xlsx', 'xls'])
    if uploaded_file:
        df = carregar_dados(uploaded_file)
        if df is not None:
            st.sidebar.success("Dados carregados!")
            st.sidebar.header("Navegação")
            paginas = ["Visão Geral"]
            pagina_selecionada = st.sidebar.radio("Escolha uma página:", paginas)
            if pagina_selecionada == "Visão Geral":
                pagina_geral(df)
    else:
        st.info("Bem-vindo! Por favor, carregue um arquivo na barra lateral para iniciar a análise.")

if __name__ == '__main__':
    main()

import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Indicadores Operacionais",
    page_icon="✨",
    layout="wide"
)

# --- IDENTIDADE VISUAL E ESTILOS (CSS) ---
st.markdown("""
<style>
    /* Cor de fundo da página principal */
    .main .block-container {
        background-color: #F0F2F6;
    }
    
    /* Estilo geral dos cartões */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 25px 20px; /* Mais preenchimento vertical */
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Título principal de cada página */
    .page-header {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 20px;
    }

    /* Título dentro de um cartão */
    .card-title {
        font-size: 18px;
        font-weight: bold;
        color: #5a5a5a;
        margin-bottom: 10px;
    }
    
    /* Valor principal da métrica no cartão */
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #333333;
    }
    
    /* Descrição ou subtexto no cartão */
    .metric-subtext {
        font-size: 14px;
        color: #888888;
    }

    /* Estilo para a tabela do ranking */
    .dataframe-container {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
    }

</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES AUXILIARES ---

@st.cache_data
def carregar_dados(arquivo_carregado):
    try:
        if arquivo_carregado.name.endswith('.csv'):
            df = pd.read_csv(arquivo_carregado)
        else:
            df = pd.read_excel(arquivo_carregado)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

    colunas_map = {
        'data_atendimento': 'Data', 'Total de entrantes': 'Entrantes',
        'Atendidos': 'Atendidos', 'Total de tickets Resolvidos': 'Resolvidos',
        '% Avaliações CSAT 4 e 5': 'CSAT_pc', 'TMA': 'TMA_str', 'TMR': 'TMR_str',
        'Líder': 'Líder', 'agente_email': 'Operador'
    }
    try:
        df = df.rename(columns=colunas_map)
    except Exception:
        st.error("Erro ao renomear colunas. Verifique se os nomes no arquivo correspondem ao esperado.")
        return None

    def clean_percentage(pc_str):
        if isinstance(pc_str, str): return float(pc_str.replace('%', '').replace(',', '.'))
        return float(pc_str) * 100 if isinstance(pc_str, (int, float)) else 0

    def tempo_para_segundos(tempo_str):
        if isinstance(tempo_str, (str, int, float)):
            tempo_str = str(tempo_str)
            parts = tempo_str.split(':')
            if len(parts) == 3: return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            if len(parts) == 2: return int(parts[0]) * 60 + int(parts[1])
        return np.nan

    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['CSAT'] = df['CSAT_pc'].apply(clean_percentage)
    df['TMA_segundos'] = df['TMA_str'].apply(tempo_para_segundos)
    df['TMR_segundos'] = df['TMR_str'].apply(tempo_para_segundos)
    
    return df

def segundos_para_tempo_str(segundos):
    if pd.isna(segundos): return "00:00"
    segundos = int(segundos)
    minutos, segundos_restantes = divmod(segundos, 60)
    return f"{minutos:02d}:{segundos_restantes:02d}"

# --- PÁGINAS DO DASHBOARD ---

def pagina_geral(df):
    st.markdown('<p class="page-header">Indicadores Operacionais Gerais</p>', unsafe_allow_html=True)
    
    total_atendidos = df['Atendidos'].sum()
    total_resolvidos = df['Resolvidos'].sum()
    taxa_resolucao_geral = (total_resolvidos / total_atendidos) * 100 if total_atendidos > 0 else 0
    csat_medio = (df['CSAT'] * df['Atendidos']).sum() / df['Atendidos'].sum() if df['Atendidos'].sum() > 0 else 0
    tma_medio_seg = (df['TMA_segundos'] * df['Atendidos']).sum() / df['Atendidos'].sum() if df['Atendidos'].sum() > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="card-title">Taxa de Resolução</span>
            <p class="metric-value">{taxa_resolucao_geral:.1f}%</p>
            <span class="metric-subtext">{int(total_resolvidos)} resolvidos de {int(total_atendidos)} atendidos</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <span class="card-title">CSAT Médio</span>
            <p class="metric-value">{csat_medio:.1f}%</p>
            <span class="metric-subtext">Média ponderada de satisfação</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <span class="card-title">TMA Médio</span>
            <p class="metric-value">{segundos_para_tempo_str(tma_medio_seg)}</p>
            <span class="metric-subtext">Tempo médio de atendimento</span>
        </div>
        """, unsafe_allow_html=True)

def pagina_lideres(df):
    st.markdown('<p class="page-header">Desempenho por Líder</p>', unsafe_allow_html=True)
    
    lideres_stats = df.groupby('Líder').agg(
        Atendidos_sum=('Atendidos', 'sum'),
        Resolvidos_sum=('Resolvidos', 'sum'),
        CSAT_weighted_sum=('CSAT', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        TMA_weighted_sum=('TMA_segundos', lambda x: (x * df.loc[x.index, 'Atendidos']).sum())
    ).reset_index()

    lideres_stats['Taxa_Resolucao'] = (lideres_stats['Resolvidos_sum'] / lideres_stats['Atendidos_sum']) * 100
    lideres_stats['CSAT_medio'] = lideres_stats['CSAT_weighted_sum'] / lideres_stats['Atendidos_sum']
    lideres_stats['TMA_medio'] = lideres_stats['TMA_weighted_sum'] / lideres_stats['Atendidos_sum']
    
    colunas = st.columns(len(lideres_stats))
    for i, row in lideres_stats.iterrows():
        with colunas[i]:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-title" style="font-size: 20px;">{row['Líder']}</p>
                <p class="metric-value" style="font-size: 28px;">{row.Taxa_Resolucao:.1f}%</p>
                <span class="metric-subtext">Resolução</span>
                <hr style="margin: 10px 0;">
                <span class="metric-subtext">CSAT: {row.CSAT_medio:.1f}% | TMA: {segundos_para_tempo_str(row.TMA_medio)}</span>
            </div>
            """, unsafe_allow_html=True)

def pagina_ranking(df):
    st.markdown('<p class="page-header">Ranking Geral de Desempenho</p>', unsafe_allow_html=True)
    
    operador_stats = df.groupby('Operador').agg(
        Atendidos=('Atendidos', 'sum'),
        Resolvidos=('Resolvidos', 'sum'),
        CSAT_total=('CSAT', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        TMA_total=('TMA_segundos', lambda x: (x * df.loc[x.index, 'Atendidos']).sum())
    ).reset_index()

    operador_stats['% Resolvidos'] = (operador_stats['Resolvidos'] / operador_stats['Atendidos']) * 100
    operador_stats['CSAT'] = operador_stats['CSAT_total'] / operador_stats['Atendidos']
    operador_stats['TMA'] = operador_stats['TMA_total'] / operador_stats['Atendidos']
    
    ranking = operador_stats.sort_values(by='% Resolvidos', ascending=False).reset_index(drop=True)
    ranking.index = ranking.index + 1
    ranking['TMA'] = ranking['TMA'].apply(segundos_para_tempo_str)
    
    df_display = ranking[['Operador', '% Resolvidos', 'CSAT', 'TMA']]

    def highlight_top3(s):
        if s.name == 'Operador':
            return ['background-color: #FCE4EC; font-weight: bold' if s.index in [1, 2, 3] else '' for v in s]
        return ['' for v in s]
        
    st.dataframe(
        df_display.style.format({'% Resolvidos': '{:.1f}%', 'CSAT': '{:.1f}%'}).apply(highlight_top3, axis=1),
        use_container_width=True
    )

# --- APLICAÇÃO PRINCIPAL ---
def main():
    st.sidebar.title("Dashboard Operacional")
    
    uploaded_file = st.sidebar.file_uploader("Faça o upload do seu arquivo", type=['csv', 'xlsx', 'xls'])

    if uploaded_file:
        df = carregar_dados(uploaded_file)
        
        if df is not None:
            st.sidebar.success("Arquivo carregado!")
            st.sidebar.header("Navegação")
            
            paginas = ["Visão Geral", "Desempenho por Líder", "Ranking Geral"]
            if 'Categoria' in df.columns: paginas.append("Categorias") # Condicional

            pagina_selecionada = st.sidebar.radio("Escolha uma página:", paginas)
            
            if pagina_selecionada == "Visão Geral":
                pagina_geral(df)
            elif pagina_selecionada == "Desempenho por Líder":
                pagina_lideres(df)
            elif pagina_selecionada == "Ranking Geral":
                pagina_ranking(df)
            elif pagina_selecionada == "Categorias":
                 st.warning("Página de Categorias ainda em construção.") # Placeholder

    else:
        st.info("Para começar, faça o upload de um arquivo Excel ou CSV na barra lateral.")

if __name__ == '__main__':
    main()

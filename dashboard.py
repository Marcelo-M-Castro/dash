import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Indicadores Operacionais",
    page_icon="📊",
    layout="wide"
)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .metric-card { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; height: 100%; }
    .metric-card h4 { font-size: 16px; font-weight: bold; color: #333333; }
    .metric-card p { font-size: 32px; font-weight: bold; color: #333333; margin-top: 5px; }
    .metric-card span { font-size: 14px; color: #888888; }
</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES AUXILIARES ---

@st.cache_data
def carregar_dados(arquivo_carregado):
    """ Carrega e processa os dados do arquivo (Excel ou CSV) com as novas colunas. """
    try:
        if arquivo_carregado.name.endswith('.csv'):
            df = pd.read_csv(arquivo_carregado)
        else:
            df = pd.read_excel(arquivo_carregado)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None, None

    # Mapeamento das colunas do SEU arquivo para os nomes que o script usa internamente
    colunas_map = {
        'data_atendimento': 'Data',
        'Total de entrantes': 'Entrantes',
        'Atendidos': 'Atendidos',
        'Total de tickets Resolvidos': 'Resolvidos',
        '% Avaliações CSAT 4 e 5': 'CSAT',
        'TMA': 'TMA_str',
        'TMR': 'TMR_str',
        'Líder': 'Líder',
        'agente_email': 'Operador'
    }

    try:
        df = df.rename(columns=colunas_map)
    except Exception:
        st.error("Erro ao renomear colunas. Verifique se os nomes no arquivo correspondem à lista fornecida.")
        return None, None

    # Processamento dos dados
    def clean_percentage(pc_str):
        if isinstance(pc_str, str):
            return float(pc_str.replace('%', '').replace(',', '.'))
        return float(pc_str) * 100 if isinstance(pc_str, (int, float)) else 0

    def tempo_para_segundos(tempo_str):
        if isinstance(tempo_str, str):
            parts = list(map(int, tempo_str.split(':')))
            if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
            if len(parts) == 2: return parts[0] * 60 + parts[1]
        return np.nan

    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['CSAT'] = df['CSAT'].apply(clean_percentage)
    df['TMA_segundos'] = df['TMA_str'].astype(str).apply(tempo_para_segundos)
    df['TMR_segundos'] = df['TMR_str'].astype(str).apply(tempo_para_segundos)
    
    return df

def segundos_para_tempo_str(segundos):
    if pd.isna(segundos): return "00:00"
    segundos = int(segundos)
    minutos, segundos_restantes = divmod(segundos, 60)
    return f"{minutos:02d}:{segundos_restantes:02d}"

# --- PÁGINAS DO DASHBOARD ---

def pagina_geral(df):
    st.header("Indicadores Operacionais Gerais")
    
    total_entrantes = df['Entrantes'].sum()
    total_atendidos = df['Atendidos'].sum()
    total_resolvidos = df['Resolvidos'].sum()
    
    taxa_atendimento = (total_atendidos / total_entrantes) * 100 if total_entrantes > 0 else 0
    taxa_resolucao_geral = (total_resolvidos / total_atendidos) * 100 if total_atendidos > 0 else 0
    
    # Média ponderada do CSAT pelo número de atendimentos
    csat_medio = (df['CSAT'] * df['Atendidos']).sum() / df['Atendidos'].sum() if df['Atendidos'].sum() > 0 else 0
    
    # Média ponderada de TMA/TMR pelo número de atendimentos
    tma_medio_seg = (df['TMA_segundos'] * df['Atendidos']).sum() / df['Atendidos'].sum() if df['Atendidos'].sum() > 0 else 0
    tmr_medio_seg = (df['TMR_segundos'] * df['Atendidos']).sum() / df['Atendidos'].sum() if df['Atendidos'].sum() > 0 else 0

    dias_unicos = df['Data'].nunique()
    media_atend_dia = total_atendidos / dias_unicos if dias_unicos > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("TOTAL DE ENTRANTES", int(total_entrantes))
        st.metric("TAXA DE RESOLUÇÃO", f"{taxa_resolucao_geral:.1f}%")
    with col2:
        st.metric("TOTAL ATENDIDOS", int(total_atendidos), f"{taxa_atendimento:.1f}% dos entrantes")
        st.metric("TMA MÉDIO", segundos_para_tempo_str(tma_medio_seg))
    with col3:
        st.metric("TOTAL RESOLVIDOS", int(total_resolvidos), f"{taxa_resolucao_geral:.1f}% dos atendidos")
        st.metric("TMR MÉDIO", segundos_para_tempo_str(tmr_medio_seg))
    with col4:
        st.metric("CSAT MÉDIO", f"{csat_medio:.1f}%")
        st.metric("MÉDIA DE ATENDIMENTO/DIA", f"{media_atend_dia:.0f}")

def pagina_categorias(df):
    st.header("Resolvidos por Categoria")
    st.warning("O arquivo de dados carregado não contém a coluna 'Categoria'. Esta página não pode ser exibida.")

def pagina_lideres(df):
    st.header("Desempenho por Líder")

    lideres_stats = df.groupby('Líder').agg(
        Atendidos=('Atendidos', 'sum'),
        Resolvidos=('Resolvidos', 'sum'),
        CSAT_total=('CSAT', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        Atendidos_total_csat=('Atendidos', 'sum'),
        TMA_total=('TMA_segundos', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
        TMR_total=('TMR_segundos', lambda x: (x * df.loc[x.index, 'Atendidos']).sum()),
    ).reset_index()

    lideres_stats['Taxa_Resolucao'] = (lideres_stats['Resolvidos'] / lideres_stats['Atendidos']) * 100
    lideres_stats['CSAT_medio'] = lideres_stats['CSAT_total'] / lideres_stats['Atendidos_total_csat']
    lideres_stats['TMA_medio'] = lideres_stats['TMA_total'] / lideres_stats['Atendidos_total_csat']
    lideres_stats['TMR_medio'] = lideres_stats['TMR_total'] / lideres_stats['Atendidos_total_csat']

    colunas = st.columns(len(lideres_stats))
    for i, row in lideres_stats.iterrows():
        with colunas[i]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{row['Líder']}</h4>
                <p style="font-size: 22px;">{int(row.Atendidos)}</p><span>Atendidos</span>
                <p style="font-size: 22px;">{int(row.Resolvidos)} ({row.Taxa_Resolucao:.0f}%)</p><span>Resolvidos</span>
                <p style="font-size: 22px;">{row.CSAT_medio:.1f}%</p><span>CSAT Médio</span>
                <hr>
                <span>TMA: {segundos_para_tempo_str(row.TMA_medio)} | TMR: {segundos_para_tempo_str(row.TMR_medio)}</span>
            </div>""", unsafe_allow_html=True)

# --- APLICAÇÃO PRINCIPAL ---
def main():
    st.title("Dashboard de Indicadores Operacionais")
    
    uploaded_file = st.sidebar.file_uploader("Faça o upload do seu arquivo (Excel ou CSV)", type=['csv', 'xlsx', 'xls'])

    if uploaded_file:
        df = carregar_dados(uploaded_file)
        
        if df is not None:
            st.sidebar.success("Arquivo carregado com sucesso!")
            st.sidebar.header("Navegação")
            
            paginas = ["Visão Geral", "Desempenho por Líder"]
            # Adiciona a página de categorias apenas se a coluna existir
            if 'Categoria' in df.columns:
                paginas.append("Categorias")

            pagina_selecionada = st.sidebar.radio("Escolha uma página:", paginas)
            
            if pagina_selecionada == "Visão Geral":
                pagina_geral(df)
            elif pagina_selecionada == "Desempenho por Líder":
                pagina_lideres(df)
            elif pagina_selecionada == "Categorias":
                pagina_categorias(df)
    else:
        st.info("Para começar, faça o upload de um arquivo na barra lateral.")

if __name__ == '__main__':
    main()

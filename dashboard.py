import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Indicadores Operacionais",
    page_icon="📊",
    layout="wide"
)

# --- ESTILOS CSS PARA REPLICAR O VISUAL ---
st.markdown("""
<style>
    /* Estilo geral do container de métricas */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
    }
    .metric-card-highlight {
        border: 2px solid #28a745; /* Verde para destaque */
    }
    .metric-card h3 {
        font-size: 18px;
        color: #5a5a5a;
        margin-bottom: 5px;
    }
    .metric-card h4 {
        font-size: 16px;
        font-weight: bold;
        color: #333333;
    }
    .metric-card p {
        font-size: 32px;
        font-weight: bold;
        color: #333333;
        margin-top: 5px;
    }
    .metric-card span {
        font-size: 14px;
        color: #888888;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
    }
    .detrator-card {
        border: 1px solid #e83e8c;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES AUXILIARES ---

@st.cache_data
def carregar_dados(arquivo_carregado):
    """
    Carrega e processa os dados do arquivo CSV carregado pelo usuário.
    """
    try:
        df = pd.read_csv(arquivo_carregado)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None, None

    # Suposições dos nomes das colunas - ajuste se necessário
    colunas_esperadas = {
        'entrante_col': 'Data de Entrada',
        'atendido_col': 'Status da Chamada',
        'resolvido_col': 'Status da Chamada',
        'csat_col': 'CSAT',
        'tma_col': 'TMA',
        'tmr_col': 'TMR',
        'categoria_col': 'Categoria',
        'lider_col': 'Líder',
        'operador_col': 'Operador'
    }

    # Validação se as colunas existem
    for col in colunas_esperadas.values():
        if col not in df.columns:
            st.error(f"Coluna esperada '{col}' não encontrada no arquivo. Por favor, verifique o CSV.")
            return None, None
            
    # Função para converter 'HH:MM:SS' ou 'MM:SS' em segundos
    def tempo_para_segundos(tempo_str):
        if isinstance(tempo_str, str):
            partes = list(map(int, tempo_str.split(':')))
            if len(partes) == 3: return partes[0] * 3600 + partes[1] * 60 + partes[2]
            if len(partes) == 2: return partes[0] * 60 + partes[1]
        return np.nan

    df['TMA_segundos'] = df[colunas_esperadas['tma_col']].apply(tempo_para_segundos)
    df['TMR_segundos'] = df[colunas_esperadas['tmr_col']].apply(tempo_para_segundos)
    df['Atendido'] = df[colunas_esperadas['atendido_col']].apply(lambda x: 1 if x in ['Atendido', 'Resolvido'] else 0)
    df['Resolvido'] = df[colunas_esperadas['resolvido_col']].apply(lambda x: 1 if x == 'Resolvido' else 0)
    df['Data'] = pd.to_datetime(df[colunas_esperadas['entrante_col']]).dt.date

    return df, colunas_esperadas

def segundos_para_tempo_str(segundos):
    """Converte segundos para uma string no formato MM:SS."""
    if pd.isna(segundos): return "00:00"
    segundos = int(segundos)
    minutos, segundos_restantes = divmod(segundos, 60)
    return f"{minutos:02d}:{segundos_restantes:02d}"

# --- FUNÇÕES DE RENDERIZAÇÃO DE PÁGINA ---

def pagina_geral(df, cols):
    st.header("Indicadores Operacionais Gerais")
    
    total_entrantes = len(df)
    total_atendidos = df['Atendido'].sum()
    total_resolvidos = df['Resolvido'].sum()
    taxa_atendimento = (total_atendidos / total_entrantes) * 100 if total_entrantes > 0 else 0
    taxa_resolucao_geral = (total_resolvidos / total_atendidos) * 100 if total_atendidos > 0 else 0
    csat_medio = df[cols['csat_col']].mean()
    tma_medio_seg = df['TMA_segundos'].mean()
    tmr_medio_seg = df['TMR_segundos'].mean()
    dias_unicos = df['Data'].nunique()
    media_atend_dia = total_atendidos / dias_unicos if dias_unicos > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="TOTAL DE ENTRANTES", value=total_entrantes, help="Todos os contatos recebidos")
        st.metric(label="TMPR (TAXA DE RESOLUÇÃO)", value=f"{taxa_resolucao_geral:.1f}%")
    with col2:
        st.metric(label="TOTAL ATENDIDOS", value=total_atendidos, delta=f"{taxa_atendimento:.1f}% dos entrantes")
        st.metric(label="TMA MÉDIO", value=segundos_para_tempo_str(tma_medio_seg), help="Tempo médio de atendimento")
    with col3:
        st.metric(label="TOTAL RESOLVIDOS", value=total_resolvidos, delta=f"{taxa_resolucao_geral:.1f}% dos atendidos")
        st.metric(label="TMR MÉDIO", value=segundos_para_tempo_str(tmr_medio_seg), help="Tempo médio de resposta")
    with col4:
        st.metric(label="CSAT MÉDIO", value=f"{csat_medio:.1f}%", help="Satisfação do cliente")
        st.metric(label="MÉDIA DE ATENDIMENTO/DIA", value=f"{media_atend_dia:.0f}")

def pagina_categorias(df, cols):
    st.header("Resolvidos por Categoria")
    
    categorias = df[cols['categoria_col']].unique()
    colunas = st.columns(len(categorias))

    for i, categoria in enumerate(categorias):
        with colunas[i]:
            df_cat = df[df[cols['categoria_col']] == categoria]
            atendimentos = df_cat['Atendido'].sum()
            resolvidos = df_cat['Resolvido'].sum()
            taxa_resolucao = (resolvidos / atendimentos * 100) if atendimentos > 0 else 0
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>{categoria}</h3>
                <p style="font-size: 24px;">{taxa_resolucao:.0f}%</p>
                <progress value="{int(taxa_resolucao)}" max="100"></progress>
                <hr>
                <div style="display: flex; justify-content: space-between; text-align: left;">
                    <span>Atendimentos:</span> <strong>{atendimentos}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; text-align: left;">
                    <span>Resolvidos:</span> <strong>{resolvidos}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

def pagina_lideres(df, cols):
    st.header("Desempenho por Líder")

    lideres_stats = df.groupby(cols['lider_col']).agg(
        Entrantes=(cols['entrante_col'], 'count'),
        Atendidos=('Atendido', 'sum'),
        Resolvidos=('Resolvido', 'sum'),
        CSAT=(cols['csat_col'], 'mean'),
        TMA_medio=('TMA_segundos', 'mean'),
        TMR_medio=('TMR_segundos', 'mean')
    ).reset_index()
    lideres_stats['Taxa_Resolucao'] = (lideres_stats['Resolvidos'] / lideres_stats['Atendidos']) * 100

    colunas_lideres = st.columns(len(lideres_stats))
    for i, row in lideres_stats.iterrows():
        with colunas_lideres[i]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{row[cols['lider_col']]}</h4>
                <div style="display: flex; justify-content: space-around;">
                    <div><span>ATENDIDOS</span><p style="font-size: 22px;">{row.Atendidos}</p></div>
                    <div><span>RESOLVIDOS</span><p style="font-size: 22px;">{row.Resolvidos} ({row.Taxa_Resolucao:.0f}%)</p></div>
                </div>
                <div><span>CSAT</span><p style="font-size: 22px;">{row.CSAT:.1f}%</p></div>
                <hr>
                <div style="text-align: left;">
                    <span>TMA: {segundos_para_tempo_str(row.TMA_medio)}</span><br>
                    <span>TMR: {segundos_para_tempo_str(row.TMR_medio)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def pagina_melhorias(df, cols):
    st.header("Oportunidades de Melhoria")
    st.write("Análise dos 3 operadores com menores indicadores para planos de ação.")
    
    media_geral_resolucao = (df['Resolvido'].sum() / df['Atendido'].sum()) * 100
    media_geral_csat = df[cols['csat_col']].mean()
    
    operador_stats = df.groupby(cols['operador_col']).agg(
        Atendidos=('Atendido', 'sum'),
        Resolvidos=('Resolvido', 'sum'),
        CSAT=(cols['csat_col'], 'mean')
    ).reset_index()
    operador_stats['Taxa_Resolucao'] = (operador_stats['Resolvidos'] / operador_stats['Atendidos']) * 100
    operador_stats.dropna(inplace=True)
    
    detratores = operador_stats.sort_values('CSAT', ascending=True).head(3)
    
    colunas_detratores = st.columns(3)
    for i, row in detratores.iterrows():
        with colunas_detratores[i]:
            delta_resolucao = row.Taxa_Resolucao - media_geral_resolucao
            delta_csat = row.CSAT - media_geral_csat
            st.markdown(f"""
            <div class="metric-card detrator-card">
                <h4>{i+1}º detrator: {row[cols['operador_col']]}</h4>
                <div style="text-align: left; color: #dc3545; font-weight: bold;">
                    <span>% Resolvidos: {row.Taxa_Resolucao:.1f}% ({delta_resolucao:+.1f}%)</span><br>
                    <span>CSAT: {row.CSAT:.1f}% ({delta_csat:+.1f}%)</span>
                </div>
                <hr>
                <div style="display: flex; justify-content: space-around;">
                    <span>Atendidos: {row.Atendidos}</span>
                    <span>Resolvidos: {row.Resolvidos}</span>
                </div>
                <br>
                <button style="width: 100%; border-radius: 5px; background-color: #e83e8c; color: white; border: none; padding: 10px;">Plano de Ação</button>
            </div>
            """, unsafe_allow_html=True)

# --- APLICAÇÃO PRINCIPAL ---

def main():
    st.title("Dashboard de Indicadores Operacionais")
    
    uploaded_file = st.sidebar.file_uploader(
        "Faça o upload do seu arquivo CSV", 
        type=['csv']
    )

    if uploaded_file is not None:
        df, colunas_esperadas = carregar_dados(uploaded_file)
        
        if df is not None:
            st.sidebar.success("Arquivo carregado com sucesso!")
            st.sidebar.header("Navegação")
            pagina_selecionada = st.sidebar.radio(
                "Escolha uma página:",
                ["Visão Geral", "Categorias", "Líderes", "Melhorias"]
            )
            
            if pagina_selecionada == "Visão Geral":
                pagina_geral(df, colunas_esperadas)
            elif pagina_selecionada == "Categorias":
                pagina_categorias(df, colunas_esperadas)
            elif pagina_selecionada == "Líderes":
                pagina_lideres(df, colunas_esperadas)
            elif pagina_selecionada == "Melhorias":
                pagina_melhorias(df, colunas_esperadas)
    else:
        st.info("Para começar, faça o upload de um arquivo CSV na barra lateral.")
        st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)

if __name__ == '__main__':
    main()

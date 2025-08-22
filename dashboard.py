import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Indicadores Operacionais",
    page_icon="📊",
    layout="wide"
)

# --- CARREGAMENTO E PREPARAÇÃO DOS DADOS ---
# Cache para otimizar o carregamento dos dados
@st.cache_data
def carregar_dados(caminho_arquivo):
    """
    Carrega e processa os dados do arquivo CSV.
    Assume que as colunas de tempo (TMA, TMR) estão em formato de texto 'HH:MM:SS'
    e as converte para segundos para facilitar os cálculos.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {caminho_arquivo}. Por favor, certifique-se de que o arquivo está na mesma pasta que o script.")
        return None

    # Suposições dos nomes das colunas - ajuste se necessário
    colunas_esperadas = {
        'entrante_col': 'Data de Entrada',  # Coluna com data/hora para contar entrantes
        'atendido_col': 'Status da Chamada', # Coluna para verificar se foi atendido
        'resolvido_col': 'Status da Chamada',# Coluna para verificar se foi resolvido
        'csat_col': 'CSAT',                 # Coluna de CSAT (0-100)
        'tma_col': 'TMA',                   # Tempo Médio de Atendimento
        'tmr_col': 'TMR',                   # Tempo Médio de Resposta
        'categoria_col': 'Categoria',       # Categoria do atendimento
        'lider_col': 'Líder',               # Nome do Líder
        'operador_col': 'Operador'          # Nome do Operador
    }

    # Renomear colunas para o padrão usado no script
    # Adicione aqui o mapeamento das suas colunas se os nomes forem diferentes
    # Ex: df.rename(columns={'Nome Antigo': 'Nome Novo'}, inplace=True)

    # Função para converter 'HH:MM:SS' ou 'MM:SS' em segundos
    def tempo_para_segundos(tempo_str):
        if isinstance(tempo_str, str):
            partes = list(map(int, tempo_str.split(':')))
            if len(partes) == 3: # HH:MM:SS
                return partes[0] * 3600 + partes[1] * 60 + partes[2]
            elif len(partes) == 2: # MM:SS
                return partes[0] * 60 + partes[1]
        return np.nan # Retorna NaN se o formato for inválido ou o valor não for string

    # Aplicar conversão e tratar erros
    df['TMA_segundos'] = df[colunas_esperadas['tma_col']].apply(tempo_para_segundos)
    df['TMR_segundos'] = df[colunas_esperadas['tmr_col']].apply(tempo_para_segundos)

    # Criar colunas para o cálculo de atendidos e resolvidos
    df['Atendido'] = df[colunas_esperadas['atendido_col']].apply(lambda x: 1 if x in ['Atendido', 'Resolvido'] else 0)
    df['Resolvido'] = df[colunas_esperadas['resolvido_col']].apply(lambda x: 1 if x == 'Resolvido' else 0)

    # Converter coluna de data para cálculos de média por dia
    df['Data'] = pd.to_datetime(df[colunas_esperadas['entrante_col']]).dt.date


    return df, colunas_esperadas

def segundos_para_tempo_str(segundos):
    """Converte segundos para uma string no formato MM:SS."""
    if pd.isna(segundos):
        return "00:00"
    segundos = int(segundos)
    minutos = segundos // 60
    segundos_restantes = segundos % 60
    return f"{minutos:02d}:{segundos_restantes:02d}"


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
    }
    .metric-card-highlight {
        border: 2px solid #28a745; /* Verde para destaque */
    }
    .metric-card h3 {
        font-size: 18px;
        color: #5a5a5a;
        margin-bottom: 5px;
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
    /* Estilo para os botões de navegação */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES PARA RENDERIZAR AS PÁGINAS ---

def pagina_geral(df, cols):
    st.header("Indicadores Operacionais Gerais")
    
    # Cálculos
    total_entrantes = len(df)
    total_atendidos = df['Atendido'].sum()
    total_resolvidos = df['Resolvido'].sum()
    taxa_atendimento = (total_atendidos / total_entrantes) * 100 if total_entrantes > 0 else 0
    taxa_resolucao_geral = (total_resolvidos / total_atendidos) * 100 if total_atendidos > 0 else 0
    csat_medio = df[cols['csat_col']].mean()
    tmpr = taxa_resolucao_geral # Usando taxa de resolução como TMPR conforme PDF
    tma_medio_seg = df['TMA_segundos'].mean()
    tmr_medio_seg = df['TMR_segundos'].mean()
    dias_unicos = df['Data'].nunique()
    media_atend_dia = total_atendidos / dias_unicos if dias_unicos > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>TOTAL DE ENTRANTES</h3>
            <p>{total_entrantes}</p>
            <span>Todos os contatos recebidos</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>TMPR</h3>
            <p>{tmpr:.1f}%</p>
            <span>Taxa de resolução</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>TOTAL ATENDIDOS</h3>
            <p>{total_atendidos}</p>
            <span>{taxa_atendimento:.1f}% dos entrantes</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>TMA MÉDIO</h3>
            <p>{segundos_para_tempo_str(tma_medio_seg)}</p>
            <span>Tempo médio de atendimento</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>TOTAL RESOLVIDOS</h3>
            <p>{total_resolvidos}</p>
            <span>{taxa_resolucao_geral:.1f}% dos atendidos</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>TMR MÉDIO</h3>
            <p>{segundos_para_tempo_str(tmr_medio_seg)}</p>
            <span>Tempo médio de resposta</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>CSAT MÉDIO</h3>
            <p>{csat_medio:.1f}%</p>
            <span>Satisfação do cliente</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>MÉDIA DE ATENDIMENTO/DIA</h3>
            <p>{media_atend_dia:.0f}</p>
            <span>Quantidade média</span>
        </div>
        """, unsafe_allow_html=True)

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
            
            # Cartão da categoria
            st.markdown(f"""
            <div class="metric-card">
                <h3>{categoria}</h3>
                <p style="font-size: 24px;">{taxa_resolucao:.0f}%</p>
                <progress value="{taxa_resolucao}" max="100"></progress>
                <hr>
                <div style="display: flex; justify-content: space-between; text-align: left;">
                    <span>Atendimentos:</span> <strong>{atendimentos}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; text-align: left;">
                    <span>Resolvidos:</span> <strong>{resolvidos}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; text-align: left;">
                    <span>Taxa de Resolução:</span> <strong>{taxa_resolucao:.0f}%</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)


def pagina_lideres(df, cols):
    st.header("Desempenho por Líder")

    lideres_stats = df.groupby(cols['lider_col']).agg(
        Entrantes=('Entrantes', 'count'),
        Atendidos=('Atendido', 'sum'),
        Resolvidos=('Resolvido', 'sum'),
        CSAT=(cols['csat_col'], 'mean'),
        TMA_medio=('TMA_segundos', 'mean'),
        TMR_medio=('TMR_segundos', 'mean')
    ).reset_index()

    lideres_stats['Taxa_Resolucao'] = (lideres_stats['Resolvidos'] / lideres_stats['Atendidos']) * 100
    
    # Destacar o líder do meio (exemplo visual)
    num_lideres = len(lideres_stats)
    colunas_lideres = st.columns(num_lideres)

    for i, row in lideres_stats.iterrows():
        with colunas_lideres[i]:
            highlight_class = "metric-card-highlight" if i == 1 else "" # Destaque no segundo
            st.markdown(f"""
            <div class="metric-card {highlight_class}">
                <h3>{row[cols['lider_col']]}</h3>
                <div style="display: flex; justify-content: space-around;">
                    <div><span>ENTRANTES</span><p style="font-size: 22px;">{row.Entrantes}</p></div>
                    <div><span>ATENDIDOS</span><p style="font-size: 22px;">{row.Atendidos}</p></div>
                </div>
                <div style="display: flex; justify-content: space-around; margin-top: 10px;">
                    <div><span>RESOLVIDOS</span><p style="font-size: 22px;">{row.Resolvidos} ({row.Taxa_Resolucao:.0f}%)</p></div>
                    <div><span>CSAT</span><p style="font-size: 22px;">{row.CSAT:.1f}%</p></div>
                </div>
                <hr>
                <div style="text-align: left;">
                    <span>TMA: {segundos_para_tempo_str(row.TMA_medio)}</span><br>
                    <span>TMR: {segundos_para_tempo_str(row.TMR_medio)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Ranking Geral
    st.subheader("🏆 Ranking Geral de Desempenho")
    ranking_col1, ranking_col2, ranking_col3 = st.columns(3)

    with ranking_col1:
        melhor_tma = lideres_stats.sort_values('TMA_medio', ascending=True).iloc[0]
        st.info(f"**1º Thays**\n\n🥇 Melhor TMA: {segundos_para_tempo_str(melhor_tma.TMA_medio)}")
    with ranking_col2:
        melhor_csat = lideres_stats.sort_values('CSAT', ascending=False).iloc[0]
        st.info(f"**2º Camila**\n\n🥇 Melhor CSAT: {melhor_csat.CSAT:.1f}%")
    with ranking_col3:
        melhor_tmr = lideres_stats.sort_values('TMR_medio', ascending=True).iloc[0]
        st.info(f"**3º Larissa**\n\n🥇 Melhor TMR: {segundos_para_tempo_str(melhor_tmr.TMR_medio)}")

def pagina_melhorias(df, cols):
    st.header("Oportunidades de Melhoria")
    st.write("Análise dos 3 operadores com menores indicadores para planos de ação.")
    
    # Médias gerais
    media_geral_resolucao = (df['Resolvido'].sum() / df['Atendido'].sum()) * 100 if df['Atendido'].sum() > 0 else 0
    media_geral_csat = df[cols['csat_col']].mean()
    
    # Stats por operador
    operador_stats = df.groupby(cols['operador_col']).agg(
        Entrantes=('Entrantes', 'count'),
        Atendidos=('Atendido', 'sum'),
        Resolvidos=('Resolvido', 'sum'),
        CSAT=(cols['csat_col'], 'mean')
    ).reset_index()

    operador_stats['Taxa_Resolucao'] = (operador_stats['Resolvidos'] / operador_stats['Atendidos']) * 100
    operador_stats.dropna(inplace=True) # Remover operadores sem todos os dados

    # Identificar os 3 piores (ex: por CSAT)
    detratores = operador_stats.sort_values('CSAT', ascending=True).head(3)
    
    colunas_detratores = st.columns(3)
    
    for i, row in detratores.iterrows():
        with colunas_detratores[i]:
            delta_resolucao = row.Taxa_Resolucao - media_geral_resolucao
            delta_csat = row.CSAT - media_geral_csat

            st.markdown(f"""
            <div class="metric-card">
                <h4>{i+1}º detrator: {row[cols['operador_col']]}</h4>
                <div style="text-align: left; color: #dc3545; font-weight: bold;">
                    <span>% Resolvidos: {row.Taxa_Resolucao:.1f}% ({delta_resolucao:+.1f}%)</span><br>
                    <span>CSAT: {row.CSAT:.1f}% ({delta_csat:+.1f}%)</span>
                </div>
                <hr>
                <div style="display: flex; justify-content: space-between;">
                    <span>Entrantes: {row.Entrantes}</span>
                    <span>Atendidos: {row.Atendidos}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Resolvidos: {row.Resolvidos}</span>
                    <span>Tickets: {row.Entrantes}</span>
                </div>
                <br>
                <button style="width: 100%; border-radius: 5px; background-color: #e83e8c; color: white; border: none; padding: 10px;">Plano de Ação</button>
            </div>
            """, unsafe_allow_html=True)

# --- APLICAÇÃO PRINCIPAL ---

def main():
    st.title("Dashboard de Indicadores Operacionais")
    st.markdown("Inspirado em meutudo.com.br | Semana: 11/08-15/08")

    # Carregar dados
    df, colunas_esperadas = carregar_dados('Tempos Operacionais (1).xlsx - Sheet1.csv')

    if df is not in None:
        # Navegação
        if 'page' not in st.session_state:
            st.session_state.page = 'Geral'
        
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2,3])
        with col1:
            if st.button("Visão Geral", key='geral'):
                st.session_state.page = 'Geral'
        with col2:
            if st.button("Categorias", key='categorias'):
                st.session_state.page = 'Categorias'
        with col3:
            if st.button("Líderes", key='lideres'):
                st.session_state.page = 'Líderes'
        with col4:
            if st.button("Melhorias", key='melhorias'):
                st.session_state.page = 'Melhorias'
        
        st.markdown("<hr>", unsafe_allow_html=True)

        # Renderizar página selecionada
        if st.session_state.page == 'Geral':
            pagina_geral(df, colunas_esperadas)
        elif st.session_state.page == 'Categorias':
            pagina_categorias(df, colunas_esperadas)
        elif st.session_state.page == 'Líderes':
            pagina_lideres(df, colunas_esperadas)
        elif st.session_state.page == 'Melhorias':
            pagina_melhorias(df, colunas_esperadas)

if __name__ == '__main__':
    main()
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==================
# CONFIGURAÇÃO INICIAL
# ==================
st.set_page_config(page_title="Dashboard Performance", layout="wide")

# ==================
# FUNÇÕES AUXILIARES
# ==================
def calcular_metricas(df):
    df['resolvido'] = df['status'] == 'Resolvido'
    df['atend_1min'] = df['tempo_resposta'] <= 60
    return df

# ==================
# PÁGINAS DO DASHBOARD
# ==================
def pagina_overview(df):
    st.title("📊 Visão Geral")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Atendimentos", len(df))
    col2.metric("% Resolvidos", f"{100*df['resolvido'].mean():.1f}%")
    col3.metric("% Até 1 min", f"{100*df['atend_1min'].mean():.1f}%")

    st.subheader("Distribuição por Canal")
    canais = df['canal'].value_counts()
    fig, ax = plt.subplots()
    canais.plot(kind="bar", ax=ax)
    st.pyplot(fig)


def pagina_lideres(df):
    st.title("👩‍💼 Análise por Líderes")
    lideres = df['lider'].unique().tolist()
    lider_sel = st.selectbox("Selecione um líder", ["Todos"] + lideres)
    if lider_sel != "Todos":
        df = df[df['lider'] == lider_sel]

    st.subheader("Métricas por Agente")
    resumo = df.groupby("agente").agg({
        "resolvido": "mean",
        "atend_1min": "mean",
        "id": "count"
    }).reset_index()
    resumo.columns = ["Agente", "% Resolvidos", "% Até 1 min", "Qtd Atendimentos"]
    st.dataframe(resumo, use_container_width=True)


def pagina_melhorias(df):
    st.markdown('<p class="page-header">Oportunidades de Melhoria</p>', unsafe_allow_html=True)

    # Conversão de colunas percentuais e tempo
    def perc_to_float(pc):
        if isinstance(pc, str):
            return float(pc.replace('%','').replace(',','.'))
        return float(pc)

    df['% Total de tickets Resolvidos'] = df['% Total de tickets Resolvidos'].apply(perc_to_float)
    df['% Avaliações CSAT 4 e 5'] = df['% Avaliações CSAT 4 e 5'].apply(perc_to_float)
    df['% Atendidos 1 min'] = df['% Atendidos 1 min'].apply(perc_to_float)

    media_res = df['% Total de tickets Resolvidos'].mean()
    media_csat = df['% Avaliações CSAT 4 e 5'].mean()
    media_sla = df['% Atendidos 1 min'].mean()

    # Agrupa por agente
    stats = df.groupby('agente_email', as_index=False).agg(
        Atendidos=('Atendidos', 'sum'),
        Resolvidos=('Total de tickets Resolvidos', 'sum'),
        pct_resolvidos=('% Total de tickets Resolvidos', 'mean'),
        csat=('% Avaliações CSAT 4 e 5', 'mean'),
        sla=('% Atendidos 1 min', 'mean'),
        TMA=('TMA', 'first'),  # pode ajustar média se necessário
        TMR=('TMR', 'first')
    )

    # Ordena pelos menores CSAT (detratores)
    stats = stats.sort_values('csat').head(3)

    n_cols = 3  # número de colunas por linha
    for i in range(0, len(stats), n_cols):
        cols = st.columns(n_cols)
        for j, (_, row) in enumerate(stats.iloc[i:i+n_cols].iterrows()):
            with cols[j]:
                delta_res = row['pct_resolvidos'] - media_res
                delta_csat = row['csat'] - media_csat
                delta_sla = row['sla'] - media_sla

                st.markdown(f"""
                    <div class="metric-card-leader">
                        <p class="card-title" style="text-align:center; font-weight:bold;">{row['agente_email'].split('@')[0]}</p>
                        <hr>
                        <p><strong>CSAT:</strong> {row['csat']:.1f}% 
                            <span class="metric-delta {'text-green' if delta_csat>=0 else 'text-red'}">({delta_csat:+.1f}%)</span></p>
                        <p><strong>Resolução:</strong> {row['pct_resolvidos']:.1f}% 
                            <span class="metric-delta {'text-green' if delta_res>=0 else 'text-red'}">({delta_res:+.1f}%)</span></p>
                        <p><strong>Atendidos 1 min:</strong> {row['sla']:.1f}% 
                            <span class="metric-delta {'text-green' if delta_sla>=0 else 'text-red'}">({delta_sla:+.1f}%)</span></p>
                        <p><strong>Total Atendidos:</strong> {int(row['Atendidos'])}</p>
                        <p><strong>TMA:</strong> {row['TMA']}</p>
                        <p><strong>TMR:</strong> {row['TMR']}</p>
                    </div>
                """, unsafe_allow_html=True)



# ==================
# MAIN
# ==================
def main():
    st.sidebar.title("📌 Navegação")
    pagina = st.sidebar.radio("Ir para:", ["Visão Geral", "Análise por Líderes", "Oportunidades de Melhoria"])

    # Simulação de base
    data = {
        "id": range(1, 101),
        "status": ["Resolvido"]*70 + ["Pendente"]*30,
        "tempo_resposta": [30, 90, 45, 120, 15]*20,
        "canal": ["Chat", "WhatsApp", "Email", "Chat", "WhatsApp"]*20,
        "lider": ["Líder A", "Líder B", "Líder A", "Líder C", "Líder B"]*20,
        "agente": ["Agente 1", "Agente 2", "Agente 3", "Agente 4", "Agente 5"]*20
    }
    df = pd.DataFrame(data)
    df = calcular_metricas(df)

    if pagina == "Visão Geral":
        pagina_overview(df)
    elif pagina == "Análise por Líderes":
        pagina_lideres(df)
    elif pagina == "Oportunidades de Melhoria":
        pagina_melhorias(df)


if __name__ == "__main__":
    main()



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
    st.title("🚀 Oportunidades de Melhoria")
    
    # Agrupamento por agente
    resumo = df.groupby("agente").agg({
        "resolvido": "mean",
        "atend_1min": "mean",
        "id": "count"
    }).reset_index()
    resumo.columns = ["agente", "pct_resolvidos", "atend_1min", "qtd"]

    # Ordena para mostrar os piores primeiro
    df_sorted = resumo.sort_values(["pct_resolvidos", "atend_1min"]).head(12)

    st.subheader("Agentes com maiores oportunidades")
    cols = st.columns(3)
    for i, row in enumerate(df_sorted.itertuples()):
        col = cols[i % 3]  # distribui os cards automaticamente
        with col:
            st.markdown(f"### {row.agente}")
            st.metric("% Resolvidos", f"{row.pct_resolvidos:.1f}%")
            st.metric("% Até 1 min", f"{row.atend_1min:.1f}%")
            st.metric("Qtd Atendimentos", row.qtd)


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

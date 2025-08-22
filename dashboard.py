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
    st.header("🔎 Oportunidades de Melhoria")

    # Selecionar líder (filtro opcional)
    lideres = df["Líder"].dropna().unique()
    lider_filtro = st.selectbox("Filtrar por Líder", options=["Todos"] + sorted(lideres.tolist()))
    if lider_filtro != "Todos":
        df = df[df["Líder"] == lider_filtro]

    # Ordenar agentes pela % de tickets resolvidos (menores primeiro = maiores oportunidades)
    df_sorted = df.groupby("agente_email", as_index=False).agg({
        "Total de Tickets": "sum",
        "Total de tickets Resolvidos": "sum",
        "% Total de tickets Resolvidos": "mean",
        "% Avaliações CSAT 4 e 5": "mean",
        "% Atendidos 1 min": "mean",
        "TMA": "mean",
        "TMR": "mean"
    }).sort_values(by="% Total de tickets Resolvidos", ascending=True)

    st.write("Agentes com maiores oportunidades de melhoria (ordenados pelo % resolvidos):")

    cols = st.columns(3)  # grid de 3 colunas
    for i, row in enumerate(df_sorted.itertuples()):
        col = cols[i % 3]  # distribui automaticamente
        with col:
            st.markdown(f"### 👤 {row.agente_email}")
            st.metric("🎯 % Resolvidos", f"{row._4:.1f}%")  
            st.metric("⭐ CSAT 4 e 5", f"{row._5:.1f}%")
            st.metric("⚡ Atendidos até 1 min", f"{row._6:.1f}%")
            st.metric("⏱️ TMA", f"{row.TMA:.1f} min")
            st.metric("⌛ TMR", f"{row.TMR:.1f} min")
            st.metric("📊 Total Tickets", row._2)



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


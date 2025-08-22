import streamlit as st

def pagina_melhorias(df):
    # CSS para estilizar os cards no mesmo estilo do HTML
    st.markdown(
        """
        <style>
        .improvement-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .improvement-card {
            background: #fff;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .improvement-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        }
        .improvement-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        .leader-avatar-small img {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            object-fit: cover;
        }
        .improvement-rank {
            font-weight: bold;
            color: #d22688;
            margin-right: 8px;
        }
        .improvement-metrics {
            margin: 10px 0;
        }
        .improvement-metric {
            display: flex;
            justify-content: space-between;
            margin: 4px 0;
            padding: 6px 8px;
            border-radius: 8px;
        }
        .improvement-metric.negative {
            background: #fbeaea;
            color: #a94442;
        }
        .improvement-metric.positive {
            background: #e6f7ed;
            color: #2e7d32;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            margin: 2px 0;
            color: #555;
        }
        .action-btn {
            background: #4f3f91;
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 8px;
            margin-top: 10px;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Aqui você define como ordenar os "piores" agentes
    # Exemplo: ordenar pelo % resolvidos (coluna "pct_resolvidos")
    df_sorted = df.sort_values("pct_resolvidos").head(5)

    # Construção dinâmica dos cards
    cards_html = '<div class="improvement-grid">'
    for i, row in enumerate(df_sorted.itertuples(), 1):
        cards_html += f"""
        <div class="improvement-card">
            <div class="improvement-header">
                <div class="improvement-rank">{i}º detrator</div>
                <div class="leader-avatar-small">
                    <img src="https://via.placeholder.com/42" alt="{row.agente}">
                </div>
                <div>
                    <h3>{row.agente}</h3>
                    <span class="email">{row.email}</span>
                </div>
            </div>
            <div class="improvement-metrics">
                <div class="improvement-metric {'negative' if row.pct_resolvidos < 60 else 'positive'}">
                    <span>% Resolvidos</span><span>{row.pct_resolvidos:.1f}%</span>
                </div>
                <div class="improvement-metric {'negative' if row.atend_1min < 70 else 'positive'}">
                    <span>Atend. 1 min</span><span>{row.atend_1min:.1f}%</span>
                </div>
            </div>
            <div class="stat-row"><span>Entrantes: {row.entrantes}</span><span>Atendidos: {row.atendidos}</span></div>
            <div class="stat-row"><span>Tickets: {row.tickets}</span><span>Resolvidos: {row.resolvidos}</span></div>
            <button class="action-btn">Plano de Ação</button>
        </div>
        """
    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)

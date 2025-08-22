import streamlit as st

def pagina_melhorias(df):
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
            color: #d9534f;
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
        .stat-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            margin: 2px 0;
            color: #555;
        }
        .action-btn {
            background: #007bff;
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

    st.markdown(
        """
        <div class="improvement-grid">

            <div class="improvement-card">
                <div class="improvement-header">
                    <div class="improvement-rank">1º detrator</div>
                    <div class="leader-avatar-small">
                        <img src="https://via.placeholder.com/42" alt="José Abreu">
                    </div>
                    <div>
                        <h3>José Abreu</h3>
                        <span class="email">jose.abreu@empresa.com</span>
                    </div>
                </div>
                <div class="improvement-metrics">
                    <div class="improvement-metric negative">
                        <span>% Resolvidos</span><span>43.6%</span>
                    </div>
                    <div class="improvement-metric negative">
                        <span>Atend. 1 min</span><span>54.6%</span>
                    </div>
                </div>
                <div class="stat-row"><span>Entrantes: 219</span><span>Atendidos: 218</span></div>
                <div class="stat-row"><span>Tickets: 197</span><span>Resolvidos: 86</span></div>
                <button class="action-btn">Plano de Ação</button>
            </div>

            <div class="improvement-card">
                <div class="improvement-header">
                    <div class="improvement-rank">2º detrator</div>
                    <div class="leader-avatar-small">
                        <img src="https://via.placeholder.com/42" alt="Júlio Lopes">
                    </div>
                    <div>
                        <h3>Júlio Lopes</h3>
                        <span class="email">julio.lopes@empresa.com</span>
                    </div>
                </div>
                <div class="improvement-metrics">
                    <div class="improvement-metric negative">
                        <span>% Resolvidos</span><span>47.2%</span>
                    </div>
                    <div class="improvement-metric negative">
                        <span>CSAT</span><span>83.3%</span>
                    </div>
                </div>
                <div class="stat-row"><span>Entrantes: 189</span><span>Atendidos: 188</span></div>
                <div class="stat-row"><span>Tickets: 216</span><span>Resolvidos: 102</span></div>
                <button class="action-btn">Plano de Ação</button>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

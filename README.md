# 📊 Dashboard de Indicadores Operacionais

Este projeto é uma implementação de um Dashboard de Indicadores Operacionais utilizando Python e a biblioteca Streamlit. O objetivo é visualizar métricas de desempenho de uma equipe de atendimento, permitindo análises por categoria, por líder e identificando oportunidades de melhoria.

O dashboard foi inspirado visualmente em um design específico e utiliza dados de um arquivo CSV para gerar as visualizações de forma dinâmica.

## ✨ Funcionalidades

O dashboard é dividido em quatro seções principais:

* **Visão Geral**: Apresenta os KPIs (Key Performance Indicators) gerais da operação, como total de chamadas, atendimentos, taxa de resolução e tempos médios (TMA, TMR).
* **Categorias**: Detalha a performance de resolução por cada categoria de atendimento.
* **Líderes**: Mostra um comparativo de desempenho entre os líderes de equipe e apresenta um ranking geral.
* **Melhorias**: Identifica os operadores com os indicadores mais baixos para auxiliar em planos de ação e desenvolvimento.

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para rodar o dashboard no seu computador.

### Pré-requisitos

* Python 3.8+ instalado
* O arquivo de dados `Tempos Operacionais (1).xlsx - Sheet1.csv` na mesma pasta do projeto.

### 1. Clone o Repositório

```bash
git clone [URL-DO-SEU-REPOSITÓRIO-NO-GITHUB]
cd [NOME-DA-PASTA-DO-PROJETO]
```

### 2. Crie um Ambiente Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

O arquivo `requirements.txt` contém todas as bibliotecas necessárias. Instale-as com o seguinte comando:

```bash
pip install -r requirements.txt
```

### 4. Execute o Aplicativo Streamlit

Com as dependências instaladas, inicie o servidor do Streamlit:

```bash
streamlit run dashboard.py
```

Seu navegador será aberto automaticamente no endereço `http://localhost:8501` com o dashboard em execução.

## 📁 Estrutura do Projeto

```
.
├── dashboard.py               # Script principal da aplicação Streamlit
├── requirements.txt           # Lista de dependências Python
├── Tempos Operacionais (1).xlsx - Sheet1.csv  # Arquivo de dados (deve ser adicionado)
└── README.md                  # Esta documentação
```

## 📝 Suposições sobre os Dados

Para que o dashboard funcione corretamente, o arquivo CSV de entrada deve conter as seguintes colunas (ou ser ajustado no código):
* `Data de Entrada`
* `Status da Chamada`
* `CSAT`
* `TMA` (formato 'HH:MM:SS')
* `TMR` (formato 'HH:MM:SS')
* `Categoria`
* `Líder`
* `Operador`
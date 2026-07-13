# 💰 Salário Médio por Estado no Brasil — Dashboard

Dashboard interativo em **Python + Streamlit** que exibe o **rendimento médio mensal**
da população ocupada por Unidade da Federação (UF), consumindo dados da
**PNAD Contínua (IBGE)** através da **API SIDRA**.

Ao passar o mouse sobre cada estado no mapa, são exibidos os **Top 3 setores/grupamentos
de atividade** com maior rendimento médio naquele estado.

---

## 📁 Estrutura do projeto

```
salario-medio-dashboard/
├── app/
│   ├── main.py                  # Ponto de entrada Streamlit
│   ├── config/
│   │   └── settings.py          # Constantes, URLs da API, mapeamentos de UF
│   ├── services/
│   │   ├── ibge_api.py          # Cliente da API SIDRA/IBGE (com cache e retry)
│   │   └── data_processing.py   # Transformação/normalização dos dados
│   ├── components/
│   │   ├── map_view.py          # Mapa coroplético (Plotly) com hover top-3 setores
│   │   ├── sidebar.py           # Filtros (ano/trimestre)
│   │   └── metrics.py           # Cards de métricas (média Brasil, maior/menor UF)
│   └── utils/
│       ├── geo.py               # GeoJSON dos estados brasileiros
│       └── formatting.py        # Formatação de moeda BRL, etc.
├── assets/
│   ├── css/
│   │   └── style.css            # Estilos customizados (tema do print)
│   └── img/
├── data/
│   └── cache/                   # Cache local de respostas da API (JSON)
├── tests/
│   └── test_ibge_api.py
├── .streamlit/
│   └── config.toml              # Tema Streamlit
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py
```

## 🔌 Fontes de dados (API IBGE)

- **Localidades (UFs, malha geográfica)**: `https://servicodados.ibge.gov.br/api/v1/localidades/estados`
- **SIDRA — Rendimento médio mensal por UF** (PNAD Contínua, Tabela 6407):
  `https://apisidra.ibge.gov.br/values/t/6407/n3/all/v/5933/p/last/c58/allxt`
- **SIDRA — Rendimento médio por UF e Grupamento de atividade** (Tabela 5436):
  `https://apisidra.ibge.gov.br/values/t/5436/n3/all/v/5929/p/last/c11913/all`

> A aplicação sempre tenta consultar a API ao vivo primeiro. Caso a API esteja
> indisponível (comum em ambientes com rede restrita), a aplicação usa
> automaticamente um **cache local em `data/cache/`** com uma amostra de dados
> compatível com o schema real da API, para que o dashboard nunca quebre.

## 🖱️ Interatividade

- Mapa coroplético do Brasil, cor por faixa de salário médio (igual à legenda do exemplo).
- **Hover** em cada estado mostra:
  - Rendimento médio mensal da UF
  - **Top 3 setores de atividade** com maior média salarial naquele estado
- Filtro de trimestre/ano na sidebar.
- Cards com Média Brasil, Maior UF, Menor UF.

## 🧪 Testes

```bash
pytest tests/
```

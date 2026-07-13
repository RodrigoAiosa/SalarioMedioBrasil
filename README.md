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

- **Design estilo landing page**, tema escuro forçado (independente do tema
  claro/escuro do navegador do usuário), título "SALÁRIOMÉDIO" em branco,
  cards com efeito glass/glow e destaque na primeira linha.
- Mapa coroplético do Brasil, cor por faixa de salário médio (igual à legenda do exemplo).
- **Hover** em cada estado mostra:
  - Rendimento médio mensal da UF
  - **Top 3 setores de atividade** com maior média salarial naquele estado
- Filtro de região na sidebar (mapa).
- Cards com Média Brasil, Maior UF, Menor UF.
- **Aba "📈 Histórico (MoM / YoY)"**:
  - Filtro de janela temporal (1, 2, 3, 5 ou 10 anos) na sidebar.
  - Gráfico de evolução do rendimento médio nacional.
  - Tabela com **Período (MêsAno)**, rendimento médio, **% QoQ** (variação
    entre trimestres — a PNAD Contínua de rendimento é divulgada
    trimestralmente, não mensalmente, então esta é a variação "MoM" aplicada
    à granularidade real da pesquisa) e **% YoY** (mesmo trimestre do ano anterior).

## 🧪 Testes

```bash
pytest tests/
```

CI configurado em `.github/workflows/ci.yml` (roda os testes automaticamente
em Python 3.11 e 3.12 a cada push/PR na branch `main`).

## 🔄 Atualizando o cache local manualmente

Em um ambiente com acesso à internet, é possível "congelar" uma foto atual
dos dados do IBGE em `data/cache/`, útil antes de um deploy:

```bash
python scripts/refresh_cache.py
```

## 🐳 Rodando com Docker

```bash
docker compose up --build
```

Ou diretamente com Docker:

```bash
docker build -t salario-medio-dashboard .
docker run -p 8501:8501 salario-medio-dashboard
```

Acesse em `http://localhost:8501`.

## ☁️ Deploy

- **Streamlit Community Cloud**: aponte para o repositório e defina
  `app/main.py` como arquivo principal.
- **Docker/Cloud Run/ECS/Azure Container Apps**: use a imagem gerada pelo
  `Dockerfile` incluso.

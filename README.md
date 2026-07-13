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
>
> Para o filtro de **Ano de referência**, o cache local inclui um snapshot por
> UF para cada ano de 2015 a 2023 (`rendimento_uf_<ano>04.json`), derivado
> proporcionalmente da série histórica nacional real (fator de crescimento
> trimestral) aplicado ao snapshot de 2024 — isso garante que o filtro
> funcione mesmo offline. Em produção, com acesso à API, cada ano é consultado
> ao vivo na Tabela SIDRA 6407 usando o código de período `<ano>04`.

## 🖱️ Interatividade

- **Design estilo landing page**, tema escuro forçado (independente do tema
  claro/escuro do navegador do usuário), título "SALÁRIOMÉDIO" em branco,
  cards com efeito glass/glow e destaque na primeira linha.
- **Filtro de Ano de referência** na sidebar: ao selecionar um ano (2015 até o
  ano corrente, calculado dinamicamente pela data do sistema — ex.: 2026), o
  mapa, os 3 cards de resumo (Média Brasil, Maior UF, Menor UF) e o Top 3
  de setores no hover são **recalculados automaticamente**. A opção do ano
  mais recente **sempre consulta a API ao vivo** (parâmetro `p=last` do SIDRA),
  então nunca fica desatualizada — não é necessário editar código a cada
  virada de ano/trimestre.
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

## 🐞 Correções aplicadas

- **`ImportError` ao importar `app.config.settings` no Streamlit Community Cloud**:
  o módulo chamava `CACHE_DIR.mkdir(parents=True, exist_ok=True)` direto na
  importação, sem tratamento de erro. Em algumas plataformas de deploy o
  diretório do repositório é montado como **somente leitura**, e essa chamada
  lançava `PermissionError`/`OSError` — como isso ocorre durante o próprio
  `import`, o Streamlit exibe isso como `ImportError` na linha que importa o
  módulo. Corrigido envolvendo a criação do diretório em `try/except OSError`
  (a gravação de cache em `ibge_api.py` já era protegida da mesma forma).
- **Hover trocado entre estados ao filtrar por região**: o filtro de região
  reindexava o DataFrame do mapa (`reset_index`) mas não recalculava o texto
  de hover na mesma ordem, fazendo com que, por exemplo, o hover do Rio de
  Janeiro exibisse dados do Distrito Federal. Corrigido aplicando a mesma
  máscara booleana simultaneamente ao DataFrame e ao texto de hover antes de
  resetar os índices. Há um teste de regressão dedicado em
  `tests/test_ibge_api.py::test_hover_text_permanece_alinhado_apos_filtro_regiao`.
- **Escala de cores do mapa "estourada"**: o `zmax` do mapa usava o teto
  genérico (99999) da última faixa da legenda, esmagando toda a escala real
  de valores (2.720–6.845+) e deixando quase todos os estados com a mesma cor
  clara. Corrigido para usar o mínimo/máximo reais dos dados carregados.

## ☁️ Troubleshooting no Streamlit Community Cloud

Se o app não subir no Streamlit Cloud, confira nesta ordem:

1. **Reboot completo do app** — no menu "⋮ → Reboot app", para limpar módulos
   Python em cache de um deploy anterior (comum após atualizar arquivos).
2. **Confirme que TODOS os arquivos foram enviados ao GitHub**, inclusive os
   `__init__.py` vazios (`app/__init__.py`, `app/config/__init__.py`,
   `app/services/__init__.py`, `app/components/__init__.py`,
   `app/utils/__init__.py`) — sem eles, `app` não é reconhecido como pacote
   Python. Rode `git status` / `git ls-files app/` localmente para checar.
3. **`requirements.txt` precisa estar na raiz do repositório** (mesmo nível
   do arquivo `README.md`), não dentro de `app/`.
4. **Main file path**, ao configurar o app no Streamlit Cloud, deve ser
   `app/main.py`.
5. Veja os **logs completos** em "Manage app" (canto inferior direito) — a
   mensagem exibida na tela é propositalmente resumida pelo Streamlit por
   segurança, mas o log completo mostra o traceback real.

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

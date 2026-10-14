/**
 * Proxy para a API SIDRA do IBGE (PNAD Contínua).
 *
 * O index.html consulta /api/sidra?path=/values/t/6407/... e esta função
 * repassa a requisição para apisidra.ibge.gov.br, com cache de 6h na CDN da
 * Vercel. Só são aceitos os caminhos das tabelas usadas pelo painel.
 */
const BASE = "https://apisidra.ibge.gov.br";
const PERMITIDOS = [
  // Rendimento médio por UF (Tabela 6407)
  /^\/values\/t\/6407\/n3\/all\/v\/5933\/p\/(last|\d{6})\/c58\/allxt$/,
  // Série histórica nacional (Tabela 6407, nível Brasil)
  /^\/values\/t\/6407\/n1\/1\/v\/5933\/p\/(all|last \d{1,2})\/c58\/allxt$/,
  // Rendimento por UF e grupamento de atividade (Tabela 5436)
  /^\/values\/t\/5436\/n3\/all\/v\/5929\/p\/(last|\d{6})\/c11913\/all$/,
];

module.exports = async (req, res) => {
  const path = String((req.query && req.query.path) || "");
  if (!PERMITIDOS.some((re) => re.test(path))) {
    return res.status(400).json({ erro: "consulta não permitida" });
  }

  let ultimoErro = null;
  for (let tentativa = 0; tentativa < 3; tentativa++) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 15000);
      const resp = await fetch(BASE + path.split("/").map(encodeURIComponent).join("/"), {
        headers: {
          Accept: "application/json",
          "User-Agent": "Mozilla/5.0 (compatible; SalarioMedio/1.0; +https://salariomediobrasil.vercel.app)",
        },
        signal: controller.signal,
      });
      clearTimeout(timer);
      if (!resp.ok) {
        ultimoErro = `HTTP ${resp.status}`;
        if (resp.status >= 500 || resp.status === 429) {
          await new Promise((r) => setTimeout(r, 800 * (tentativa + 1)));
          continue;
        }
        return res.status(resp.status).json({ erro: ultimoErro });
      }
      const dados = await resp.json();
      res.setHeader("Cache-Control", "public, s-maxage=21600, stale-while-revalidate=86400");
      return res.status(200).json(dados);
    } catch (e) {
      ultimoErro = e.name === "AbortError" ? "timeout" : "erro de conexão";
      await new Promise((r) => setTimeout(r, 800 * (tentativa + 1)));
    }
  }
  return res.status(502).json({ erro: ultimoErro || "falha ao consultar o SIDRA" });
};

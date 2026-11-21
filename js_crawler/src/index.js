const VALID_TYPES = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"];

const RELACAO_ESTADOS_BANCO = {
  adequado: 5,
  estavel: 4,
  reduzido: 3,
  alerta: 2,
  critico: 1,
};

function normalizarStatusParaInteiro(statusTexto) {
  const chave = statusTexto
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();

  return RELACAO_ESTADOS_BANCO[chave] ?? null;
}

function getBrazilDateISO() {
  // Formata no fuso do Brasil (ex.: 20/11/2026 -> 2026-11-20)
  const parts = new Intl.DateTimeFormat("pt-BR", {
    timeZone: "America/Sao_Paulo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());

  const day = parts.find((p) => p.type === "day").value;
  const month = parts.find((p) => p.type === "month").value;
  const year = parts.find((p) => p.type === "year").value;
  return `${year}-${month}-${day}`;
}

function decodeHtmlBytes(arrayBuffer) {
  // Tenta UTF-8 primeiro; se a página vier em ISO-8859-1 (Latin-1), faz o decode correto
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(arrayBuffer);
  } catch {
    return new TextDecoder("iso-8859-1").decode(arrayBuffer);
  }
}

function stripTags(html) {
  return html
    .replace(/<[^>]*>/g, " ")
    .replace(/ /gi, " ")
    .replace(/\u00a0/g, " ")
    .replace(/&/gi, "&")
    .replace(/á/gi, "á")
    .replace(/é/gi, "é")
    .replace(/í/gi, "í")
    .replace(/ó/gi, "ó")
    .replace(/ú/gi, "ú")
    .replace(/ã/gi, "ã")
    .replace(/õ/gi, "õ")
    .replace(/ç/gi, "ç")
    .replace(/&/gi, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function parseHemoscHTML(html) {
  // Cada tipo sanguíneo fica dentro de um <div class="tudo_home_estq">
  const cardMatches = [
    ...html.matchAll(
      /<div[^>]*class=["'][^"']*tudo_home_estq[^"']*["'][^>]*>([\s\S]*?)<\/div>/gi
    ),
  ];

  const results = [];

  for (const match of cardMatches) {
    const cardHtml = match[1];

    // Extrai o conteúdo de <p ...> ... </p>, ex.: "A-<br><span ...>Estável</span>"
    const pMatch = cardHtml.match(/<p[^>]*>([\s\S]*?)<\/p>/i);
    if (!pMatch) continue;

    const parts = pMatch[1].split(/<br\s*\/?>/i);
    const tipo = stripTags(parts[0] || "");
    const statusTexto = stripTags(parts.slice(1).join(" ") || "");

    if (!VALID_TYPES.includes(tipo) || !statusTexto) continue;

    const estadoNumerico = normalizarStatusParaInteiro(statusTexto);
    if (estadoNumerico !== null) {
      results.push({
        tipo,
        estado_do_estoque: estadoNumerico,
        estado_texto: statusTexto,
      });
    }
  }

  return results;
}

async function coletarESalvar(env) {
  const response = await fetch("https://www.hemosc.org.br/", {
    headers: {
      "User-Agent":
        "Mozilla/5.0 (compatible; HemOscTracker/1.0; +https://hemosc.org.br)",
    },
  });

  if (!response.ok) {
    throw new Error(`Erro HTTP ao acessar HEMOSC: ${response.status}`);
  }

  const buffer = await response.arrayBuffer();
  const html = decodeHtmlBytes(buffer);
  const itens = parseHemoscHTML(html);

  if (itens.length === 0) {
    throw new Error(
      "Nenhum tipo sanguíneo encontrado no HTML. Pode ter mudado a estrutura da página."
    );
  }

  const dataColeta = getBrazilDateISO();

  const stmt = env.DB.prepare(`
    INSERT INTO registro_estoque_hemosc (tipo_sanguineo_id, data_do_registro, estado_do_estoque)
    SELECT id, ?, ?
    FROM tipo_sanguineo
    WHERE tipo_sanguineo = ?
    ON CONFLICT(tipo_sanguineo_id, data_do_registro)
    DO UPDATE SET estado_do_estoque = excluded.estado_do_estoque
  `);
  
  const batch = itens.map((item) =>
    stmt.bind(dataColeta, item.estado_do_estoque, item.tipo)
  );
  await env.DB.batch(batch);

  return {
    ok: true,
    data_do_registro: dataColeta,
    quantidade_salva: itens.length,
    itens,
  };
}

async function listarEstoque(env) {
  const { results } = await env.DB.prepare(`
    SELECT
      r.id,
      t.tipo_sanguineo,
      r.data_do_registro,
      r.estado_do_estoque
    FROM registro_estoque_hemosc r
    JOIN tipo_sanguineo t ON t.id = r.tipo_sanguineo_id
    ORDER BY r.data_do_registro DESC, t.id ASC
  `).all();

  return results;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(coletarESalvar(env));
  },

  async fetch(request, env) {
    const url = new URL(request.url);

    try {
      if (url.pathname === "/estoque" && request.method === "GET") {
        const dados = await listarEstoque(env);
        return Response.json(dados);
      }

      if (url.pathname === "/coletar" && request.method === "POST") {
        const resultado = await coletarESalvar(env);
        return Response.json(resultado);
      }

      return Response.json(
        { error: "Rota não encontrada. Use GET /estoque ou POST /coletar." },
        { status: 404 }
      );
    } catch (err) {
      return Response.json(
        { ok: false, error: err.message },
        { status: 500 }
      );
    }
  },
};
"""Gera site-versao-final/web/i18n/lugares.json: os nomes de lugar que o site nunca traduz (regra do José, 15/11/2026), para o
js/i18n.js. Lê web/dados/busca_municipios.json (os 1.794 municípios do Nordeste, IBGE) e grava:
  m: [[cod IBGE, nome, UF], ...]     os municípios (o cod liga a página ao nome: roca.html#/<cod>/…, painel.html?cod=<cod>)
  uf: {UF: nome do estado}           os 9 estados do Nordeste
  vocab: [nome, ...]                 municípios cujo nome é também palavra do site (Barro, Areia, Baixio, Capim…): só valem como
                                     lugar no contexto (o município da página ou colado numa UF). Sai de onde o nome aparece em
                                     minúscula no texto do site (web/js, web/*.html, web/dados/*.json), mais EXTRA.
Rodar de novo quando o texto do site mudar muito. Uso:
  E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_i18n_lugares.py"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
WEB = RAIZ / "web"
SAIDA = WEB / "i18n" / "lugares.json"
UF = {"MA": "Maranhão", "PI": "Piauí", "CE": "Ceará", "RN": "Rio Grande do Norte", "PB": "Paraíba", "PE": "Pernambuco",
      "AL": "Alagoas", "SE": "Sergipe", "BA": "Bahia"}
# palavras do site que são nome de município e podem vir com maiúscula sem aparecer em minúscula (início de frase, rótulo)
EXTRA = ["Barra", "Brasileira", "Central", "Correntes", "Flores", "Floresta", "Jardim", "Lagoa", "Pedra", "Porto", "Saúde"]
# os arquivos com nome de município (não servem para achar palavra do site)
FORA = {"busca_municipios.json", "municipios_ne.json", "malha_ne.json", "nordeste.json"}

mun = json.loads((WEB / "dados" / "busca_municipios.json").read_text(encoding="utf-8"))["municipios"]
nomes = sorted({m["nome"] for m in mun})
textos = [p.read_text(encoding="utf-8", errors="ignore") for p in list((WEB / "js").rglob("*.js")) + list(WEB.glob("*.html"))
          + [q for q in (WEB / "dados").rglob("*.json") if q.name not in FORA]]
corpo = "\n".join(textos)
perto = [n for n in nomes if n.lower() in corpo]  # a busca simples primeiro (rápida); a regex só nos que passaram
vocab = sorted({n for n in perto if re.search(r"(?<![\w])" + re.escape(n.lower()) + r"(?![\w])", corpo)} | (set(EXTRA) & set(nomes)))
saida = {"fonte": "IBGE via web/dados/busca_municipios.json; ferramentas/preparar_i18n_lugares.py",
         "m": [[m["cod"], m["nome"], m["uf"]] for m in sorted(mun, key=lambda m: m["cod"])], "uf": UF, "vocab": vocab}
SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{len(saida['m'])} municípios, {len(vocab)} também palavras do site: {vocab}")
print(f"{SAIDA}: {SAIDA.stat().st_size // 1024} KB")

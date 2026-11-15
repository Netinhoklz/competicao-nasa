"""Constantes e utilitarios compartilhados pelos scripts de download e pelas secoes do notebook.

Todos os dados ficam no E: (C: esta quase cheio). Coordenadas em graus (EPSG:4326).
BBOX = (lon_min, lat_min, lon_max, lat_max).
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path

# Na maquina de trabalho valem os dados completos do E: (~11 GB). Em qualquer outra (clone do GitHub ou pacote de entrega),
# valem os dados de execucao que vem em <raiz>/dados, ao lado de scripts/ (site-versao-final/ferramentas/montar_entrega.py).
# QUADRA_DADOS=local forca os locais tambem aqui, para testar o clone e o pacote.
_LOCAL = Path(__file__).resolve().parents[1]
_E = Path("E:/campeonato-nasa")
_USA_LOCAL = (_LOCAL / "dados").is_dir() and (os.environ.get("QUADRA_DADOS") == "local" or not (_E / "dados").is_dir())
RAIZ = _LOCAL if _USA_LOCAL else _E
DADOS = RAIZ / "dados"
DERIV = DADOS / "derivados"      # series/tabelas tratadas para cruzar bases
REF = DADOS / "referencia"        # limites (IBGE, Natural Earth)
LOGS = RAIZ / "logs"
ESTUDO_CDL = RAIZ / "estudo_cdl"  # CDL fica fora de DADOS (so EUA, estudo)

# Certificados: o repositorio do Windows nao confia em algumas raizes; o pacote do Git confia.
CA_BUNDLE = "C:/Program Files/Git/mingw64/etc/ssl/certs/ca-bundle.crt"
if os.path.exists(CA_BUNDLE):  # em outra maquina (pacote de entrega) vale o certificado padrao do Python
    os.environ.setdefault("SSL_CERT_FILE", CA_BUNDLE)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", CA_BUNDLE)
    os.environ.setdefault("CURL_CA_BUNDLE", CA_BUNDLE)

# Ceara (limite IBGE: -41.414..-37.253 lon, -7.846..-2.784 lat) com folga
BBOX_CE = (-41.5, -8.0, -37.0, -2.5)
# Nordeste sem Fernando de Noronha
BBOX_NE = (-48.8, -18.4, -34.7, -1.0)

# Areas agricolas de interesse no Ceara para dados de alta resolucao (centro lon, lat).
# Coordenadas aproximadas; meia-largura padrao de 0.05 grau (~11 km de lado).
AOIS = {
    "apodi_jaguaribe": (-37.95, -5.20, "Chapada do Apodi / Limoeiro do Norte - fruticultura irrigada"),
    "cariri": (-39.35, -7.30, "Cariri (Crato/Barbalha) - cana, graos de sequeiro"),
    "sertao_central": (-39.02, -4.97, "Sertao Central (Quixada) - milho/feijao de sequeiro, pastagem"),
    "ibiapaba": (-40.99, -3.73, "Serra da Ibiapaba (Tianguá/Ubajara) - horticultura, clima ameno"),
}
AOI_MEIA = 0.05


def bbox_aoi(nome: str, meia: float = AOI_MEIA):
    lon, lat, _ = AOIS[nome]
    return (lon - meia, lat - meia, lon + meia, lat + meia)


def pasta(dataset: str) -> Path:
    p = DADOS / dataset
    p.mkdir(parents=True, exist_ok=True)
    return p


def registrar_manifesto(dataset: str, info: dict, base: Path | None = None) -> Path:
    """Acrescenta/atualiza MANIFESTO.json do dataset (fonte, URL, recorte, periodo, arquivos, tamanhos)."""
    p = (base or pasta(dataset)) / "MANIFESTO.json"
    atual = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    atual.update(info)
    atual["atualizado_em"] = datetime.now().isoformat(timespec="seconds")
    p.write_text(json.dumps(atual, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return p


def sessao_http(retries: int = 5):
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    s = requests.Session()
    r = Retry(total=retries, backoff_factor=1.5, status_forcelist=(429, 500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=r, pool_maxsize=16))
    s.mount("http://", HTTPAdapter(max_retries=r, pool_maxsize=16))
    s.headers["User-Agent"] = "Mozilla/5.0 (space-apps-research)"
    s.verify = CA_BUNDLE
    return s


def baixar(url: str, destino: Path, sessao=None, chunk: int = 1 << 20) -> Path:
    """Download com retomada simples (pula se ja existe com mesmo tamanho)."""
    s = sessao or sessao_http()
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    with s.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        if destino.exists() and total and destino.stat().st_size == total:
            return destino
        with open(tmp, "wb") as f:
            for b in r.iter_content(chunk):
                f.write(b)
    tmp.replace(destino)
    return destino


def ceara_gdf():
    import geopandas as gpd
    return gpd.read_file(REF / "ceara_uf.geojson")


def municipios_ce_gdf():
    import geopandas as gpd
    return gpd.read_file(REF / "ceara_municipios.geojson")


def nordeste_gdf():
    import geopandas as gpd
    return gpd.read_file(REF / "nordeste_ufs.geojson")


def paises_gdf():
    import geopandas as gpd
    return gpd.read_file("zip://" + str(REF / "ne_110m_admin_0_countries.zip"))


def terra_gdf():
    import geopandas as gpd
    return gpd.read_file("zip://" + str(REF / "ne_50m_land.zip"))


def tamanho_pasta(p: Path) -> int:
    return sum(f.stat().st_size for f in Path(p).rglob("*") if f.is_file())


class Cronometro:
    def __init__(self, rotulo: str):
        self.rotulo = rotulo

    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, *a):
        print(f"[{self.rotulo}] {time.time() - self.t0:.1f}s", flush=True)

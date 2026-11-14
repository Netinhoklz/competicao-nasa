"""Bases que exigem Earthdata Login: SMAP, GLDAS, NLDAS, IMERG V07 recente, VIIRS VNP13.

--metadados  : consulta o CMR (aberto, sem login): extensao espacial, periodo, granulos por ano, ultimo granulo.
--dados      : (exige C:/Users/<voce>/_netrc com urs.earthdata.nasa.gov) baixa recortes do Ceara.
"""
import argparse
import json
import sys
import urllib.parse

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import BBOX_CE, pasta, registrar_manifesto, sessao_http  # noqa: E402

CMR = "https://cmr.earthdata.nasa.gov/search/"
COLECOES = {
    # rotulo: (short_name, versao ou None)
    "SMAP L3 umidade 9 km diaria (SPL3SMP_E)": ("SPL3SMP_E", "006"),
    "SMAP L4 umidade superficie+raiz 9 km 3h (SPL4SMGP)": ("SPL4SMGP", "008"),
    "GLDAS-2.1 Noah 0,25 mensal": ("GLDAS_NOAH025_M", "2.1"),
    "GLDAS-2.2 CLSM 0,25 diario (com GRACE-DA, agua subterranea)": ("GLDAS_CLSM025_DA1_D", "2.2"),
    "NLDAS-2 Noah 0,125 mensal": ("NLDAS_NOAH0125_M", "2.0"),
    "IMERG V07 Late diario": ("GPM_3IMERGDL", "07"),
    "IMERG V07 Final diario": ("GPM_3IMERGDF", "07"),
    "IMERG V07 Final mensal": ("GPM_3IMERGM", "07"),
    "VIIRS VNP13A1 NDVI 500 m 16 d": ("VNP13A1", "002"),
    "VIIRS VNP13C2 NDVI 0,05 mensal (CMG)": ("VNP13C2", "002"),
}


def cmr_json(s, caminho, **q):
    r = s.get(CMR + caminho + "?" + urllib.parse.urlencode(q, doseq=True), timeout=90)
    r.raise_for_status()
    return r


def metadados():
    s = sessao_http()
    saida = {}
    for rot, (sn, ver) in COLECOES.items():
        q = {"short_name": sn}
        if ver:
            q["version"] = ver
        ents = cmr_json(s, "collections.json", **q).json()["feed"]["entry"]
        if not ents:
            saida[rot] = {"short_name": sn, "erro": "nao encontrado"}
            continue
        e = ents[0]
        cid = e["id"]
        caixas = e.get("boxes") or []
        ult = cmr_json(s, "granules.json", collection_concept_id=cid, sort_key="-start_date", page_size=1).json()["feed"]["entry"]
        pri = cmr_json(s, "granules.json", collection_concept_id=cid, sort_key="start_date", page_size=1).json()["feed"]["entry"]
        por_ano = {}
        a0 = int((e.get("time_start") or "2000")[:4])
        for ano in range(a0, 2027):
            r = cmr_json(s, "granules.json", collection_concept_id=cid, page_size=0,
                         temporal=f"{ano}-01-01T00:00:00Z,{ano}-12-31T23:59:59Z")
            por_ano[ano] = int(r.headers.get("CMR-Hits", 0))
        # granulos que tocam o Ceara (para estimar volume do recorte)
        r = cmr_json(s, "granules.json", collection_concept_id=cid, page_size=0,
                     bounding_box=",".join(map(str, BBOX_CE)))
        saida[rot] = {
            "short_name": sn, "versao": e.get("version_id"), "concept_id": cid, "titulo": e.get("title"),
            "caixa_espacial (S W N E)": caixas, "inicio": e.get("time_start"), "fim": e.get("time_end"),
            "primeiro_granulo": pri[0]["time_start"] if pri else None,
            "ultimo_granulo": ult[0]["time_start"] if ult else None,
            "granulos_por_ano": por_ano, "granulos_ceara": int(r.headers.get("CMR-Hits", 0)),
            "centro_de_dados": e.get("data_center"), "online": e.get("online_access_flag"),
            "nuvem": e.get("cloud_hosted"),
        }
        print(rot, "|", saida[rot]["caixa_espacial (S W N E)"], "|", saida[rot]["inicio"], "->", saida[rot]["ultimo_granulo"], flush=True)
    p = pasta("earthdata_metadados") / "cmr_colecoes.json"
    p.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    registrar_manifesto("earthdata_metadados", {"fonte": "NASA CMR (aberto)", "arquivo": str(p), "colecoes": list(COLECOES)})
    print("gravado", p)


def dados():
    from pathlib import Path
    netrc = [Path.home() / "_netrc", Path.home() / ".netrc"]
    if not any(p.exists() for p in netrc):
        sys.exit("Sem _netrc do Earthdata; crie C:/Users/<voce>/_netrc e rode de novo.")
    raise SystemExit("Modo --dados: implementado quando as credenciais existirem (AppEEARS para SMAP/VIIRS; OPeNDAP para GLDAS/IMERG).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadados", action="store_true")
    ap.add_argument("--dados", action="store_true")
    a = ap.parse_args()
    if a.metadados:
        metadados()
    if a.dados:
        dados()

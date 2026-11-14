"""Baixa legendas (valor -> rotulo) das funcoes de renderizacao dos ImageServers GAEZ v4.
Saida: dados/gaez/legendas_gaez.json  {servico: {funcao: [{"rotulo":..., "valores":...}]}}
"""
import sys
import json

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

sys.stdout.reconfigure(encoding="utf-8")
P = DADOS / "gaez"
s = sessao_http()
saida = {}
for sv in ["LR", "res01", "res05", "res06", "res07"]:
    info = s.get(f"https://gaez-services.fao.org/server/rest/services/{sv}/ImageServer", params={"f": "json"}, timeout=60).json()
    funcs = [f["name"] for f in info.get("rasterFunctionInfos", []) if f["name"] != "None"]
    saida[sv] = {}
    for fn in funcs:
        try:
            r = s.get(f"https://gaez-services.fao.org/server/rest/services/{sv}/ImageServer/legend",
                      params={"f": "json", "renderingRule": json.dumps({"rasterFunction": fn})}, timeout=60).json()
            itens = []
            for lyr in r.get("layers", []):
                for leg in lyr.get("legend", []):
                    itens.append({"rotulo": leg.get("label"), "valores": leg.get("values")})
            saida[sv][fn] = itens
            print(sv, "|", fn, "|", len(itens), "itens |", [i["rotulo"] for i in itens][:6], flush=True)
        except Exception as e:
            print(sv, fn, "ERRO", e, flush=True)
(P / "legendas_gaez.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok")

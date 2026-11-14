"""Testa a credencial do Earthdata (_netrc) sem imprimir a senha.

1) le o _netrc; 2) pede/obtem um token no URS; 3) testa acesso a GES DISC (GLDAS/IMERG) e NSIDC (SMAP); 4) AppEEARS.
"""
import netrc
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

ARQ = Path.home() / "_netrc"
usuario, _, senha = netrc.netrc(str(ARQ)).authenticators("urs.earthdata.nasa.gov")
print("usuario no _netrc:", usuario, "| tamanho da senha:", len(senha))

s = sessao_http(retries=1)
r = s.get("https://urs.earthdata.nasa.gov/api/users/tokens", auth=(usuario, senha), timeout=60)
print("URS tokens:", r.status_code, "(200 = credencial valida, 401 = usuario/senha errados)")
if r.status_code != 200:
    print(r.text[:300])
    sys.exit(1)

# GES DISC (GLDAS) - arquivo pequeno via OPeNDAP com recorte minimo
url = ("https://hydro1.gesdisc.eosdis.nasa.gov/opendap/GLDAS/GLDAS_NOAH025_M.2.1/2020/"
       "GLDAS_NOAH025_M.A202001.021.nc4.dds")
r2 = s.get(url, auth=(usuario, senha), timeout=90, allow_redirects=True)
print("GES DISC OPeNDAP (GLDAS):", r2.status_code, r2.url[:90])
print("   ", r2.text[:200].replace("\n", " ") if r2.ok else r2.text[:300].replace("\n", " "))

# AppEEARS login
r3 = s.post("https://appeears.earthdatacloud.nasa.gov/api/login", auth=(usuario, senha), timeout=90)
print("AppEEARS login:", r3.status_code)

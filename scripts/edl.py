"""Autenticacao Earthdata (EDL) a partir do _netrc: token bearer + sessao requests. Nunca imprime a senha."""
import netrc
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

URS = "https://urs.earthdata.nasa.gov"


def credenciais():
    u, _, p = netrc.netrc(str(Path.home() / "_netrc")).authenticators("urs.earthdata.nasa.gov")
    return u, p


@lru_cache(maxsize=1)
def token_edl() -> str:
    u, p = credenciais()
    s = sessao_http(retries=2)
    r = s.post(f"{URS}/api/users/find_or_create_token", auth=(u, p), timeout=60)
    r.raise_for_status()
    return r.json()["access_token"]


def sessao_edl():
    s = sessao_http()
    s.headers["Authorization"] = f"Bearer {token_edl()}"
    return s

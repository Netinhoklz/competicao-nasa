"""Leitura da configuracao do condado piloto e caminhos do projeto."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config" / "pilot_county.toml"


@dataclass(frozen=True)
class Caminhos:
    raw: Path
    interim: Path
    processed: Path

    def criar(self) -> "Caminhos":
        for p in (self.raw, self.interim, self.processed):
            p.mkdir(parents=True, exist_ok=True)
        return self


def carregar_config(caminho: str | Path | None = None) -> dict:
    caminho = Path(caminho or CONFIG_PADRAO)
    with open(caminho, "rb") as f:
        cfg = tomllib.load(f)
    c = cfg["caminhos"]
    cfg["_caminhos"] = Caminhos(*(RAIZ / c[k] for k in ("raw", "interim", "processed"))).criar()
    return cfg

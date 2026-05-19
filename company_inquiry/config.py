from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SiteConfig:
    key: str
    company_name: str
    api_url: str = ""
    token: str = ""
    method: str = "GET"
    type: str = "web"
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    search_url: str = ""
    timeout: int = 12

    @property
    def display_name(self) -> str:
        return self.company_name or self.key

    @property
    def has_api(self) -> bool:
        return bool(self.api_url and self.api_url.lower() != "test")


def load_sites(config_path: str | Path) -> list[SiteConfig]:
    path = Path(config_path)
    with path.open("r", encoding="utf-8-sig") as file:
        raw = json.load(file)

    sites: list[SiteConfig] = []
    for key, value in raw.items():
        if key == "_comment":
            continue
        if not isinstance(value, dict):
            continue

        method = value.get("method") or value.get("mapping") or "GET"
        sites.append(
            SiteConfig(
                key=key,
                company_name=str(value.get("company_name") or key),
                api_url=str(value.get("api_url") or ""),
                token=str(value.get("token") or ""),
                method=str(method).upper(),
                type=str(value.get("type") or "web"),
                headers=dict(value.get("headers") or {}),
                params=dict(value.get("params") or {}),
                body=dict(value.get("body") or {}),
                search_url=str(value.get("search_url") or ""),
                timeout=int(value.get("timeout") or 12),
            )
        )
    return sites


def find_site(sites: list[SiteConfig], key: str) -> SiteConfig | None:
    return next((site for site in sites if site.key == key), None)


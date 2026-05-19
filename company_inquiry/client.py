from __future__ import annotations

import json
from string import Formatter
from typing import Any
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from .config import SiteConfig


RISK_KEYWORDS = {
    "outsourcing": ["外包", "人力外包", "劳务派遣", "驻场", "外派", "项目外派", "乙方", "派遣"],
    "agency": ["人力资源", "猎头", "招聘流程外包", "RPO", "服务外包"],
    "warning": ["拖欠", "避雷", "离职率", "加班严重", "试用期裁员", "薪资倒挂"],
}


def query_site(site: SiteConfig, company: str) -> dict[str, Any]:
    company = company.strip()
    if not company:
        raise ValueError("请输入公司名称")

    if not site.has_api:
        return _manual_result(site, company)

    headers = _render_mapping(site.headers, company)
    if site.token and "Authorization" not in headers:
        headers["Authorization"] = f"Bearer {site.token}"

    params = _render_mapping(site.params, company) or {"q": company}
    body = _render_mapping(site.body, company)
    method = site.method.upper()
    url = site.api_url

    if method == "GET":
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{urlencode(params)}"
        payload = None
    else:
        payload = json.dumps(body or params).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    request = Request(url, data=payload, headers=headers, method=method)
    with urlopen(request, timeout=site.timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        raw_bytes = response.read()
        text = raw_bytes.decode("utf-8", errors="replace")

    parsed: Any
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None

    analysis_text = json.dumps(parsed, ensure_ascii=False) if parsed is not None else text
    return {
        "site": _site_payload(site),
        "company": company,
        "mode": "api",
        "status": "success",
        "content_type": content_type,
        "summary": analyze_text(analysis_text),
        "raw": parsed if parsed is not None else text[:4000],
    }


def analyze_text(text: str) -> dict[str, Any]:
    found: dict[str, list[str]] = {}
    lowered = text.lower()
    for category, keywords in RISK_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword.lower() in lowered]
        if hits:
            found[category] = hits

    score = min(100, sum(len(items) for items in found.values()) * 20)
    if score >= 60:
        level = "high"
        label = "高风险"
    elif score >= 20:
        level = "medium"
        label = "需要核实"
    else:
        level = "low"
        label = "未发现明显外包信号"

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_label": label,
        "keywords": found,
    }


def _manual_result(site: SiteConfig, company: str) -> dict[str, Any]:
    search_url = site.search_url or f"https://www.baidu.com/s?wd={quote_plus(company + ' ' + site.display_name)}"
    search_url = search_url.replace("{company}", quote_plus(company))
    text = f"{company} {site.display_name}"
    return {
        "site": _site_payload(site),
        "company": company,
        "mode": "manual",
        "status": "success",
        "summary": analyze_text(text),
        "raw": {
            "message": "该站点还没有配置真实 API。可以先打开检索入口人工查看，后续把 api_url/token/method 写入 Companys.json 即可接入自动查询。",
            "search_url": search_url,
            "outsourcing_checks": [
                "公司名称是否包含人力资源、外包、劳务派遣、企业管理咨询等字样",
                "招聘岗位是否出现驻场、外派、乙方项目、长期出差等描述",
                "评价中是否频繁出现薪资拖欠、项目制、合同主体不一致等信息",
            ],
        },
    }


def _render_mapping(mapping: dict[str, Any], company: str) -> dict[str, Any]:
    return {key: _render_value(value, company) for key, value in mapping.items()}


def _render_value(value: Any, company: str) -> Any:
    if isinstance(value, str):
        fields = {name for _, name, _, _ in Formatter().parse(value) if name}
        if "company" in fields:
            return value.format(company=company)
    if isinstance(value, dict):
        return _render_mapping(value, company)
    if isinstance(value, list):
        return [_render_value(item, company) for item in value]
    return value


def _site_payload(site: SiteConfig) -> dict[str, Any]:
    return {
        "key": site.key,
        "company_name": site.display_name,
        "type": site.type,
        "has_api": site.has_api,
    }


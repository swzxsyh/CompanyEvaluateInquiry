from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .client import query_site
from .config import find_site, load_sites


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "Companys.json"


class InquiryHandler(BaseHTTPRequestHandler):
    server_version = "CompanyInquiry/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(INDEX_HTML)
            return
        if parsed.path == "/api/sites":
            sites = load_sites(CONFIG_PATH)
            payload = [
                {
                    "key": site.key,
                    "company_name": site.display_name,
                    "type": site.type,
                    "has_api": site.has_api,
                }
                for site in sites
            ]
            self._send_json({"sites": payload})
            return
        if parsed.path == "/api/search":
            self._handle_search(parse_qs(parsed.query))
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        print(f"[web] {self.address_string()} - {format % args}")

    def _handle_search(self, query: dict[str, list[str]]) -> None:
        company = _first(query, "company")
        site_key = _first(query, "site")
        sites = load_sites(CONFIG_PATH)
        site = find_site(sites, site_key)
        if site is None:
            self._send_json({"status": "error", "message": "未知招聘网站"}, HTTPStatus.BAD_REQUEST)
            return
        try:
            result = query_site(site, company)
        except Exception as exc:
            self._send_json(
                {
                    "status": "error",
                    "message": str(exc),
                    "site": {"key": site.key, "company_name": site.display_name},
                },
                HTTPStatus.BAD_REQUEST,
            )
            return
        self._send_json(result)

    def _send_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), InquiryHandler)
    print(f"CompanyEvaluateInquiry 已启动: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        server.server_close()


def _first(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key) or [""]
    return values[0].strip()


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>公司评价查询</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --line: #dde4ef;
      --text: #162033;
      --muted: #657386;
      --accent: #1976d2;
      --accent-strong: #0d47a1;
      --warn: #b45309;
      --danger: #b91c1c;
      --ok: #047857;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    .app {
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr);
      min-height: 100vh;
    }
    aside {
      background: #101827;
      color: #eef4ff;
      padding: 24px 16px;
      border-right: 1px solid #0a1020;
    }
    .brand {
      font-size: 18px;
      font-weight: 700;
      margin: 0 0 20px;
    }
    .site-list {
      display: grid;
      gap: 8px;
    }
    .site-button {
      width: 100%;
      border: 1px solid transparent;
      background: transparent;
      color: inherit;
      text-align: left;
      padding: 11px 12px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-size: 14px;
    }
    .site-button:hover, .site-button.active {
      background: #1d2a44;
      border-color: #34496e;
    }
    .badge {
      font-size: 12px;
      color: #b9c7dc;
      border: 1px solid #42577a;
      border-radius: 999px;
      padding: 2px 7px;
      flex: 0 0 auto;
    }
    main {
      padding: 28px;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 18px;
    }
    .toolbar {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      display: grid;
      grid-template-columns: minmax(160px, 1fr) auto;
      gap: 10px;
      align-items: center;
    }
    input {
      height: 42px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0 12px;
      font-size: 15px;
      outline: none;
    }
    input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(25, 118, 210, .13);
    }
    .query-button {
      height: 42px;
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: white;
      font-size: 15px;
      font-weight: 650;
      padding: 0 18px;
      cursor: pointer;
    }
    .query-button:hover { background: var(--accent-strong); }
    .content {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      min-height: 420px;
      overflow: hidden;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
    }
    .result-head {
      padding: 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    h1 {
      font-size: 18px;
      margin: 0;
    }
    .risk {
      font-weight: 700;
      border-radius: 999px;
      padding: 6px 10px;
      background: #e8eef8;
      color: var(--muted);
    }
    .risk.low { background: #dff8ec; color: var(--ok); }
    .risk.medium { background: #fff0d4; color: var(--warn); }
    .risk.high { background: #ffe4e6; color: var(--danger); }
    .result-body {
      padding: 18px;
      overflow: auto;
    }
    .hint {
      color: var(--muted);
      line-height: 1.7;
      max-width: 760px;
    }
    .checks {
      margin: 14px 0;
      padding-left: 20px;
      color: var(--text);
      line-height: 1.7;
    }
    a { color: var(--accent); }
    pre {
      margin: 14px 0 0;
      padding: 14px;
      border-radius: 8px;
      background: #0f172a;
      color: #e2e8f0;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.55;
    }
    @media (max-width: 760px) {
      .app { grid-template-columns: 1fr; }
      aside {
        border-right: 0;
        border-bottom: 1px solid #0a1020;
      }
      .site-list { grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
      main { padding: 16px; }
      .toolbar { grid-template-columns: 1fr; }
      .query-button { width: 100%; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <p class="brand">公司评价查询</p>
      <div id="siteList" class="site-list"></div>
    </aside>
    <main>
      <form id="searchForm" class="toolbar">
        <input id="companyInput" name="company" placeholder="输入公司名称，例如：某某科技" autocomplete="off">
        <button class="query-button" type="submit">查询</button>
      </form>
      <section class="content">
        <div class="result-head">
          <h1 id="title">选择左侧网站后查询</h1>
          <span id="risk" class="risk">等待查询</span>
        </div>
        <div id="result" class="result-body">
          <p class="hint">左侧是 Companys.json 中配置的招聘/评价网站。搜索公司名后点击网站，页面会查询该站点配置的 API；如果暂未配置真实 API，会给出对应站点的检索入口和外包判断清单。</p>
        </div>
      </section>
    </main>
  </div>
  <script>
    const siteList = document.querySelector("#siteList");
    const form = document.querySelector("#searchForm");
    const input = document.querySelector("#companyInput");
    const title = document.querySelector("#title");
    const risk = document.querySelector("#risk");
    const result = document.querySelector("#result");
    let sites = [];
    let activeSite = "";

    async function loadSites() {
      const response = await fetch("/api/sites");
      const data = await response.json();
      sites = data.sites || [];
      activeSite = sites[0]?.key || "";
      renderSites();
    }

    function renderSites() {
      siteList.innerHTML = sites.map(site => `
        <button class="site-button ${site.key === activeSite ? "active" : ""}" data-key="${site.key}" type="button">
          <span>${escapeHtml(site.company_name)}</span>
          <span class="badge">${site.has_api ? "API" : "检索"}</span>
        </button>
      `).join("");
    }

    siteList.addEventListener("click", event => {
      const button = event.target.closest(".site-button");
      if (!button) return;
      activeSite = button.dataset.key;
      renderSites();
      if (input.value.trim()) {
        search();
      }
    });

    form.addEventListener("submit", event => {
      event.preventDefault();
      search();
    });

    async function search() {
      const company = input.value.trim();
      if (!company) {
        result.innerHTML = `<p class="hint">请先输入公司名称。</p>`;
        return;
      }
      const site = sites.find(item => item.key === activeSite);
      title.textContent = `${company} · ${site?.company_name || "未知站点"}`;
      risk.className = "risk";
      risk.textContent = "查询中";
      result.innerHTML = `<p class="hint">正在查询 ${escapeHtml(site?.company_name || "")}...</p>`;

      const response = await fetch(`/api/search?site=${encodeURIComponent(activeSite)}&company=${encodeURIComponent(company)}`);
      const data = await response.json();
      if (!response.ok || data.status === "error") {
        risk.textContent = "查询失败";
        result.innerHTML = `<p class="hint">${escapeHtml(data.message || "请求失败")}</p>`;
        return;
      }
      renderResult(data);
    }

    function renderResult(data) {
      const summary = data.summary || {};
      risk.className = `risk ${summary.risk_level || ""}`;
      risk.textContent = `${summary.risk_label || "未评估"} · ${summary.risk_score || 0}`;
      const raw = data.raw || {};
      const checks = Array.isArray(raw.outsourcing_checks)
        ? `<ul class="checks">${raw.outsourcing_checks.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
        : "";
      const link = raw.search_url
        ? `<p><a href="${escapeAttr(raw.search_url)}" target="_blank" rel="noreferrer">打开 ${escapeHtml(data.site.company_name)} 检索入口</a></p>`
        : "";
      const keywords = summary.keywords && Object.keys(summary.keywords).length
        ? `<p class="hint">命中的风险词：${escapeHtml(JSON.stringify(summary.keywords))}</p>`
        : `<p class="hint">暂未从返回内容中命中明显风险词。</p>`;
      result.innerHTML = `
        <p class="hint">${escapeHtml(raw.message || "接口返回如下。")}</p>
        ${link}
        ${checks}
        ${keywords}
        <pre>${escapeHtml(JSON.stringify(raw, null, 2))}</pre>
      `;
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function escapeAttr(value) {
      return escapeHtml(value).replaceAll("`", "&#096;");
    }

    loadSites();
  </script>
</body>
</html>
"""


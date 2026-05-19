# CompanyEvaluateInquiry

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

CompanyEvaluateInquiry 是一个用于聚合招聘网站、评价网站公司信息的 Python Web 小工具。输入公司名称后，可以在多个来源中查看对应公司信息，并辅助判断是否存在外包、劳务派遣、驻场外派等风险信号。

## Features

- 通过浏览器使用，无需额外前端构建流程。
- 左侧展示已配置的招聘/评价网站，顶部输入公司名称。
- 支持通过 `Companys.json` 配置式扩展新的招聘网站或评价网站。
- 支持 `GET` / `POST` 接口调用、自定义请求头、Token 和参数模板。
- 未配置真实 API 的站点会展示人工检索入口和外包判断清单。
- 对接口返回文本做基础关键词分析，输出风险等级和命中词。

## Preview

启动后访问：

```text
http://127.0.0.1:8000
```

页面包含：

- 公司搜索框
- 招聘/评价网站列表
- 查询结果区
- 外包风险提示和原始返回内容

## Requirements

- Python 3.10+

当前核心功能只依赖 Python 标准库。`requirements.txt` 中保留了早期调研依赖，后续如果迁移到 Django/FastAPI 可继续复用。

## Quick Start

```bash
git clone https://github.com/<your-name>/CompanyEvaluateInquiry.git
cd CompanyEvaluateInquiry
python main.py
```

指定端口：

```bash
python main.py --port 8080
```

指定监听地址：

```bash
python main.py --host 0.0.0.0 --port 8000
```

## Configuration

所有招聘/评价站点都配置在 `Companys.json` 中。新增站点时添加一个新的顶层配置项即可：

```json
{
  "example": {
    "company_name": "示例招聘网站",
    "api_url": "https://example.com/api/search",
    "token": "",
    "method": "GET",
    "type": "web",
    "headers": {
      "User-Agent": "Mozilla/5.0"
    },
    "params": {
      "keyword": "{company}"
    },
    "search_url": "https://example.com/search?q={company}"
  }
}
```

字段说明：

- `company_name`：页面左侧展示名称。
- `api_url`：真实接口地址。为空或 `test` 时不调用接口，只展示人工检索入口。
- `token`：接口需要令牌时填写；当前默认以 `Authorization: Bearer <token>` 发送。
- `method`：接口请求方法，支持 `GET` 和 `POST`。
- `headers`：自定义请求头。
- `params`：GET 查询参数，或 POST 未设置 `body` 时的请求体来源。
- `body`：POST JSON 请求体。
- `search_url`：没有 API 时的人工检索入口。
- `timeout`：接口超时时间，单位为秒，默认 `12`。

`headers`、`params`、`body`、`search_url` 中的 `{company}` 会被替换为用户输入的公司名。

## Project Structure

```text
.
├── Companys.json              # 招聘/评价站点配置
├── main.py                    # Web 服务启动入口
├── company_inquiry/
│   ├── client.py              # 站点查询和风险分析
│   ├── config.py              # 配置读取和站点模型
│   └── web.py                 # Web 页面和 HTTP API
├── OriginalCode/              # 早期代码兼容入口
├── requirements.txt
└── README.md
```

## API

本地服务提供两个接口：

```text
GET /api/sites
```

返回当前配置的招聘/评价网站列表。

```text
GET /api/search?site=<site_key>&company=<company_name>
```

查询某个站点的公司信息。

## Roadmap

- 为不同招聘软件封装独立适配器，处理登录态、分页、限流和字段映射。
- 增加本地缓存，避免重复请求同一家公司。
- 增加更完整的风险规则，例如工商经营范围、招聘岗位描述、评价关键词综合评分。
- 支持导出查询报告。
- 如需更复杂的用户管理或任务队列，可迁移到 Django/FastAPI。

## Compliance Notice

如果对接招聘网站或评价网站，请优先使用官方开放接口，并遵守目标网站的服务条款、robots.txt、登录授权和访问频率限制。请勿将本项目用于绕过访问控制、批量抓取受保护数据或违反目标网站规则的用途。

## License

This project is licensed under the [MIT License](LICENSE).


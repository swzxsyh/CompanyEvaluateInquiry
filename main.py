from __future__ import annotations

import argparse

from company_inquiry.web import run_server


def main() -> None:
    parser = argparse.ArgumentParser(description="启动公司评价查询 Web 服务")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", default=8000, type=int, help="监听端口，默认 8000")
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地查看器服务（替代 python -m http.server）。

功能：
  1. 静态托管当前目录（spark_3dgs.html / LCC-Web-0.6.2 / 上传的 LCC 数据集等）。
  2. 接收浏览器 POST 上传：POST /__upload/<uid>/<relpath>  （请求体为文件二进制），
     保存到 ./__upload/<uid>/<relpath>，供 LCC Web SDK 以 HTTP URL 加载多文件数据集。

用法：
  python server.py [port]
默认端口 8137。
"""

import os
import sys
import json
import http.server
import socketserver

ROOT = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(ROOT, "__upload__")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        if self.path.startswith("/__upload__/"):
            rel = self.path[len("/__upload__/"):].lstrip("/")
            # 防目录穿越：规范化后必须仍在 UPLOAD_DIR 内
            dest = os.path.normpath(os.path.join(UPLOAD_DIR, rel))
            if not dest.startswith(os.path.normpath(UPLOAD_DIR)):
                self.send_error(400, "Invalid upload path")
                return
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                length = int(self.headers.get("Content-Length", 0))
                with open(dest, "wb") as f:
                    f.write(self.rfile.read(length))
            except Exception as e:  # noqa: BLE001
                self.send_error(500, "Upload failed: %s" % e)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "path": rel}).encode("utf-8"))
        else:
            self.send_error(405, "Method Not Allowed")

    def end_headers(self):
        # 允许跨域（同源时无害，便于本地调试）
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[server] " + (fmt % args) + "\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8137
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print("Serving %s on http://127.0.0.1:%d" % (ROOT, port))
        print("Open: http://localhost:%d/spark_3dgs.html" % port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()

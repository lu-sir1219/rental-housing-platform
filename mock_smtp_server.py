"""虚拟 SMTP 服务器 — 接收邮件并保存为 HTML 文件。

启动: python mock_smtp_server.py
邮件保存在: ./test_emails/ 目录
首页: ./test_emails/index.html
"""
import asyncio
import os
import json
from datetime import datetime, timezone

HOST = "localhost"
PORT = 1025
OUT_DIR = os.path.join(os.path.dirname(__file__), "test_emails")

os.makedirs(OUT_DIR, exist_ok=True)

INDEX_PATH = os.path.join(OUT_DIR, "index.html")


def build_index(emails: list[dict]) -> str:
    rows = ""
    for i, e in enumerate(reversed(emails)):
        rows += f"""<tr>
<td>{e['time']}</td>
<td>{e['from']}</td>
<td>{e['to']}</td>
<td><a href="{e['file']}" target="_blank">{e['subject']}</a></td>
</tr>"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Rental-Housing 虚拟收件箱</title>
<style>
body {{ font-family: system-ui; background: #f0f2f5; padding: 24px; }}
h1 {{ color: #1e293b; }}
h1 span {{ font-size: 14px; color: #64748b; font-weight: normal; }}
table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
th {{ background: #2563eb; color: white; padding: 12px 16px; text-align: left; font-size: 14px; }}
td {{ padding: 10px 16px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
tr:hover {{ background: #f8fafc; }}
a {{ color: #2563eb; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style></head>
<body>
<h1>Rental-Housing <span>虚拟收件箱</span></h1>
<p style="color:#64748b">SMTP: {HOST}:{PORT} | 共 {len(emails)} 封</p>
<table>
<tr><th>时间</th><th>发件人</th><th>收件人</th><th>主题</th></tr>
{rows if rows else '<tr><td colspan="4" style="text-align:center;color:#94a3b8;padding:40px;">暂无邮件，等待发送...</td></tr>'}
</table>
<p style="color:#94a3b8;font-size:12px;margin-top:16px;">刷新页面查看新邮件</p>
</body>
</html>"""


def update_index():
    emails = []
    for f in sorted(os.listdir(OUT_DIR)):
        if f.endswith(".json"):
            path = os.path.join(OUT_DIR, f)
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                html_file = f.replace(".json", ".html")
                emails.append({
                    "time": data.get("time", ""),
                    "from": data.get("from", ""),
                    "to": data.get("to", ""),
                    "subject": data.get("subject", ""),
                    "file": html_file,
                })
            except Exception:
                pass
    emails.sort(key=lambda x: x["time"])
    with open(INDEX_PATH, "w", encoding="utf-8") as fp:
        fp.write(build_index(emails))


def save_email(mail_from: str, rcpt_to: str, raw: str):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    safe_id = ts

    subject = "(无主题)"
    html_body = raw
    headers_end = raw.find("\r\n\r\n")
    if headers_end > 0:
        header_section = raw[:headers_end]
        for h in header_section.split("\r\n"):
            if h.lower().startswith("subject:"):
                subject = h[8:].strip()
        html_body = raw[headers_end + 4:]

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{subject}</title>
<style>
body {{ font-family: system-ui; padding: 20px; max-width: 700px; margin: auto; }}
.meta {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
.meta p {{ margin: 4px 0; font-size: 14px; color: #475569; }}
</style></head>
<body>
<div class="meta">
<p><strong>发件人:</strong> {mail_from}</p>
<p><strong>收件人:</strong> {rcpt_to}</p>
<p><strong>主题:</strong> {subject}</p>
<p><strong>时间:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
</div>
<hr>
{html_body}
</body>
</html>"""

    html_path = os.path.join(OUT_DIR, f"{safe_id}.html")
    json_path = os.path.join(OUT_DIR, f"{safe_id}.json")
    with open(html_path, "w", encoding="utf-8") as fp:
        fp.write(full_html)
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump({
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "from": mail_from,
            "to": rcpt_to,
            "subject": subject,
        }, fp, ensure_ascii=False)

    update_index()
    print(f"[SMTP] 邮件已保存: {html_path}")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"[SMTP] 新连接: {addr}")

    writer.write(b"220 Mock SMTP Server\r\n")
    await writer.drain()

    mail_from = ""
    rcpt_to = ""
    data_lines: list[str] = []
    in_data = False
    in_auth_login = False
    auth_state = 0  # 0=idle, 1=waiting username, 2=waiting password

    while True:
        try:
            line = (await asyncio.wait_for(reader.readline(), timeout=30)).decode("utf-8", errors="replace")
        except asyncio.TimeoutError:
            break
        if not line:
            break

        raw_line = line.rstrip("\r\n")
        upper = raw_line.upper()
        print(f"[SMTP] C: {raw_line}")

        # ── DATA 模式（收集邮件内容）────────────────────
        if in_data:
            if raw_line == ".":
                in_data = False
                save_email(mail_from, rcpt_to, "\n".join(data_lines))
                writer.write(b"250 OK\r\n")
                await writer.drain()
                mail_from = ""
                rcpt_to = ""
                data_lines = []
            else:
                data_lines.append(raw_line)
            continue

        # ── AUTH LOGIN 交互 ──────────────────────────────
        if in_auth_login or upper.startswith("AUTH"):
            if upper == "AUTH LOGIN" or upper.startswith("AUTH LOGIN "):
                in_auth_login = True
                auth_state = 1
                # 检查是否带有 initial-response（AUTH LOGIN <base64-user>）
                parts = raw_line.split(" ", 2)
                if len(parts) >= 3:
                    # 客户端一次发了 username
                    writer.write(b"334 UGFzc3dvcmQ6\r\n")  # "Password:"
                    auth_state = 2
                else:
                    writer.write(b"334 VXNlcm5hbWU6\r\n")  # "Username:"
                await writer.drain()
                continue
            elif in_auth_login and auth_state == 1:
                # 收到用户名 base64
                writer.write(b"334 UGFzc3dvcmQ6\r\n")  # "Password:"
                auth_state = 2
                await writer.drain()
                continue
            elif in_auth_login and auth_state == 2:
                # 收到密码 base64 — 认证成功
                in_auth_login = False
                auth_state = 0
                writer.write(b"235 2.7.0 Authentication successful\r\n")
                await writer.drain()
                continue
            elif upper == "AUTH PLAIN" or upper.startswith("AUTH PLAIN "):
                # PLAIN 简单接受
                writer.write(b"235 2.7.0 Authentication successful\r\n")
                await writer.drain()
                continue
            else:
                # 未知 AUTH 命令
                writer.write(b"235 2.7.0 Authentication successful\r\n")
                await writer.drain()
                continue

        # ── 常规 SMTP 命令 ───────────────────────────────
        if upper.startswith("EHLO"):
            writer.write(b"250-Hello\r\n250-AUTH LOGIN PLAIN\r\n250 SMTPUTF8\r\n")
        elif upper.startswith("HELO"):
            writer.write(b"250 Hello\r\n")
        elif upper.startswith("MAIL FROM:"):
            mail_from = raw_line[10:].strip()
            writer.write(b"250 OK\r\n")
        elif upper.startswith("RCPT TO:"):
            rcpt_to = raw_line[8:].strip()
            writer.write(b"250 OK\r\n")
        elif upper == "DATA":
            in_data = True
            writer.write(b"354 Start mail input; end with <CRLF>.<CRLF>\r\n")
        elif upper == "QUIT":
            writer.write(b"221 Bye\r\n")
            await writer.drain()
            break
        elif upper == "STARTTLS":
            writer.write(b"220 Ready to start TLS\r\n")
        elif upper == "NOOP":
            writer.write(b"250 OK\r\n")
        elif upper == "RSET":
            mail_from = ""
            rcpt_to = ""
            data_lines = []
            in_data = False
            writer.write(b"250 OK\r\n")
        else:
            writer.write(b"500 Unknown command\r\n")
        await writer.drain()

    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass
    print(f"[SMTP] 连接关闭: {addr}")


async def main():
    update_index()
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"虚拟 SMTP 服务器已启动: {HOST}:{PORT}")
    print(f"邮件保存目录: {OUT_DIR}")
    print(f"收件箱首页: file:///{INDEX_PATH.replace(chr(92), '/')}")
    print()
    print("按 Ctrl+C 停止")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已停止")

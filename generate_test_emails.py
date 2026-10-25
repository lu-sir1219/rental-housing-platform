"""鐩存帴鐢熸垚娴嬭瘯閭欢 HTML 鈫?娴忚鍣ㄦ墦寮€楠岃瘉銆?
涓嶄緷璧?SMTP銆丆elery 鎴栦换浣曞閮ㄦ湇鍔°€?"""
import os
import json
import webbrowser
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "test_emails")
os.makedirs(OUT_DIR, exist_ok=True)

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

emails = [
    {
        "subject": "銆愭敮浠樸€戞敮浠樿鍗曞凡鍒涘缓锛岃鍦?4灏忔椂鍐呭畬鎴愭敮浠?,
        "file": f"{ts}_payment_created.html",
        "html": """\
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fa;padding:24px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;">
<tr><td style="background:linear-gradient(135deg,#2563eb,#1d4ed8);padding:32px 40px;text-align:center;">
<h1 style="margin:0;color:#ffffff;font-size:22px;">绉熸埧鏅鸿兘骞冲彴</h1>
</td></tr>
<tr><td style="padding:32px 40px;">
<h2 style="color:#1e293b;font-size:20px;">鏀粯璁㈠崟宸插垱寤?/h2>
<p style="color:#475569;font-size:15px;line-height:1.7;">浜茬埍鐨?<strong>testuser</strong>锛屾偍濂斤紒</p>
<p style="color:#475569;font-size:15px;line-height:1.7;">鎮ㄧ殑绉熸埧璁㈠崟鏀粯宸茬敓鎴愶紝璇峰湪 <span style="color:#dc2626;font-weight:bold;">24灏忔椂鍐?/span> 瀹屾垚鏀粯锛岄€炬湡璁㈠崟灏嗚嚜鍔ㄥ彇娑堛€?/p>

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;padding:20px;margin-bottom:24px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>璁㈠崟缂栧彿锛?/strong>#42</p>
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>鎴挎簮鍚嶇О锛?/strong>娴锋穩瀛﹁嫅鍏瘬 A-301</p>
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>鏀粯閲戦锛?/strong>CNY 6,000.00</p>
<p style="margin:0;color:#dc2626;font-size:14px;"><strong>鏀粯鎴锛?/strong>2026-08-07 18:00锛堝墿浣欑害24灏忔椂锛?/p>
</td></tr>
</table>

<div style="text-align:center;margin:28px 0;">
<a href="http://localhost:5173/booking/order/42/payment-status" style="display:inline-block;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#ffffff;text-decoration:none;padding:14px 48px;border-radius:8px;font-size:16px;font-weight:bold;">绔嬪嵆鏀粯</a>
</div>

<p style="color:#94a3b8;font-size:13px;">鎵€鏈夐噾棰濄€佽鍗曞強鍚堝悓浠ヨ鍗曡鎯呴〉璁板綍涓哄噯銆?/p>
</td></tr>
<tr><td style="background:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;">
<p style="margin:0 0 8px;color:#64748b;font-size:12px;">姝ら偖浠剁敱绯荤粺鑷姩鍙戦€侊紝璇峰嬁鐩存帴鍥炲銆?br>濡傞渶甯姪锛岃鑱旂郴瀹㈡湇锛歴upport@rental-platform.com</p>
<p style="margin:0;color:#94a3b8;font-size:12px;">&copy; 2026 绉熸埧鏅鸿兘骞冲彴 鐗堟潈鎵€鏈?/p>
</td></tr>
</table>
</td></tr></table>
</body>
</html>"""
    },
    {
        "subject": "銆愬悎鍚屻€戝悎鍚屽凡鐢熸垚锛岃鍦?鏃ュ唴瀹屾垚绛剧讲",
        "file": f"{ts}_contract_generated.html",
        "html": """\
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fa;padding:24px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;">
<tr><td style="background:linear-gradient(135deg,#2563eb,#1d4ed8);padding:32px 40px;text-align:center;">
<h1 style="margin:0;color:#ffffff;font-size:22px;">绉熸埧鏅鸿兘骞冲彴</h1>
</td></tr>
<tr><td style="padding:32px 40px;">
<h2 style="color:#1e293b;font-size:20px;">鍚堝悓宸茬敓鎴愶紝璇风缃?/h2>
<p style="color:#475569;font-size:15px;line-height:1.7;">浜茬埍鐨?<strong>testuser</strong>锛屾偍濂斤紒</p>
<p style="color:#475569;font-size:15px;line-height:1.7;">鎮ㄧ殑绉熻祦鍚堝悓宸茬敓鎴愶紝璇峰湪 <span style="color:#dc2626;font-weight:bold;">7鏃ュ唴</span> 瀹屾垚绛剧讲銆傞€炬湡鏈缃茬殑璁㈠崟灏嗚鍙栨秷锛屾娂閲戜笉浜堥€€杩樸€?/p>

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:20px;margin-bottom:24px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#166534;font-size:14px;"><strong>鍚堝悓缂栧彿锛?/strong>HRTA-20260806-00000042-V1</p>
<p style="margin:0 0 8px;color:#166534;font-size:14px;"><strong>璁㈠崟缂栧彿锛?/strong>#42</p>
<p style="margin:0 0 8px;color:#166534;font-size:14px;"><strong>鎴挎簮鍚嶇О锛?/strong>娴锋穩瀛﹁嫅鍏瘬 A-301</p>
<p style="margin:0;color:#dc2626;font-size:14px;"><strong>绛剧讲鎴锛?/strong>2026-08-13 18:00锛堝墿浣?澶╋級</p>
</td></tr>
</table>

<div style="text-align:center;margin:28px 0;">
<a href="http://localhost:5173/booking/order/42/payment-status" style="display:inline-block;background:linear-gradient(135deg,#16a34a,#15803d);color:#ffffff;text-decoration:none;padding:14px 48px;border-radius:8px;font-size:16px;font-weight:bold;">鏌ョ湅骞剁缃插悎鍚?/a>
</div>

<p style="color:#94a3b8;font-size:13px;">鎵€鏈夐噾棰濄€佽鍗曞強鍚堝悓浠ヨ鍗曡鎯呴〉璁板綍涓哄噯銆?/p>
</td></tr>
<tr><td style="background:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;">
<p style="margin:0 0 8px;color:#64748b;font-size:12px;">姝ら偖浠剁敱绯荤粺鑷姩鍙戦€侊紝璇峰嬁鐩存帴鍥炲銆?br>濡傞渶甯姪锛岃鑱旂郴瀹㈡湇锛歴upport@rental-platform.com</p>
<p style="margin:0;color:#94a3b8;font-size:12px;">&copy; 2026 绉熸埧鏅鸿兘骞冲彴 鐗堟潈鎵€鏈?/p>
</td></tr>
</table>
</td></tr></table>
</body>
</html>"""
    },
    {
        "subject": "銆愰璁€戦璁㈡垚鍔燂紒鍏ヤ綇鏃ユ湡 2026-09-01",
        "file": f"{ts}_booking_succeeded.html",
        "html": """\
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fa;padding:24px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;">
<tr><td style="background:linear-gradient(135deg,#2563eb,#1d4ed8);padding:32px 40px;text-align:center;">
<h1 style="margin:0;color:#ffffff;font-size:22px;">绉熸埧鏅鸿兘骞冲彴</h1>
</td></tr>
<tr><td style="padding:32px 40px;">
<h2 style="color:#1e293b;font-size:20px;">棰勮鎴愬姛锛?/h2>
<p style="color:#475569;font-size:15px;line-height:1.7;">浜茬埍鐨?<strong>testuser</strong>锛屾伃鍠滐紒</p>
<p style="color:#475569;font-size:15px;line-height:1.7;">鎮ㄧ殑绉熸埧棰勮宸茬‘璁ゆ垚鍔燂紝璇锋寜鏃跺姙鐞嗗叆浣忋€?/p>

<table width="100%" cellpadding="0" cellspacing="0" style="background:#fefce8;border:1px solid #fef08a;border-radius:8px;padding:20px;margin-bottom:24px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#854d0e;font-size:14px;"><strong>璁㈠崟缂栧彿锛?/strong>#42</p>
<p style="margin:0 0 8px;color:#854d0e;font-size:14px;"><strong>鎴挎簮鍚嶇О锛?/strong>娴锋穩瀛﹁嫅鍏瘬 A-301</p>
<p style="margin:0 0 8px;color:#854d0e;font-size:14px;"><strong>鍏ヤ綇鏃ユ湡锛?/strong>2026-09-01</p>
<p style="margin:0 0 8px;color:#854d0e;font-size:14px;"><strong>绉熸湡锛?/strong>12 涓湀</p>
<p style="margin:0 0 8px;color:#854d0e;font-size:14px;"><strong>鍚堝悓缂栧彿锛?/strong>HRTA-20260806-00000042-V1</p>
<p style="margin:0;color:#854d0e;font-size:14px;"><strong>鏀粯閲戦锛?/strong>CNY 6,000.00</p>
</td></tr>
</table>

<div style="text-align:center;margin:28px 0;">
<a href="http://localhost:5173/booking/order/42/payment-status" style="display:inline-block;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#ffffff;text-decoration:none;padding:14px 48px;border-radius:8px;font-size:16px;font-weight:bold;">鏌ョ湅璁㈠崟璇︽儏</a>
</div>

<p style="color:#94a3b8;font-size:13px;">鎵€鏈夐噾棰濄€佽鍗曞強鍚堝悓浠ヨ鍗曡鎯呴〉璁板綍涓哄噯銆?/p>
</td></tr>
<tr><td style="background:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;">
<p style="margin:0 0 8px;color:#64748b;font-size:12px;">姝ら偖浠剁敱绯荤粺鑷姩鍙戦€侊紝璇峰嬁鐩存帴鍥炲銆?br>濡傞渶甯姪锛岃鑱旂郴瀹㈡湇锛歴upport@rental-platform.com</p>
<p style="margin:0;color:#94a3b8;font-size:12px;">&copy; 2026 绉熸埧鏅鸿兘骞冲彴 鐗堟潈鎵€鏈?/p>
</td></tr>
</table>
</td></tr></table>
</body>
</html>"""
    },
]

# 淇濆瓨閭欢
for e in emails:
    html_path = os.path.join(OUT_DIR, e["file"])
    json_path = html_path.replace(".html", ".json")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(e["html"])
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "from": "noreply@rental-platform.com",
            "to": "your-email@example.com",
            "subject": e["subject"],
        }, f, ensure_ascii=False)
    print(f"[OK] {e['file']}")

# 鏋勫缓棣栭〉
all_emails = []
for f in sorted(os.listdir(OUT_DIR)):
    if f.endswith(".json") and f.startswith(ts):
        with open(os.path.join(OUT_DIR, f), "r", encoding="utf-8") as fp:
            all_emails.append(json.load(fp))

rows = ""
for e in all_emails:
    html_file = e.get("file", "").replace(".json", ".html")
    if not html_file:
        html_file = e.get("file", "")
    rows += f"""<tr>
<td>{e.get('time', '')}</td>
<td>{e.get('from', '')}</td>
<td>{e.get('to', '')}</td>
<td><a href="{html_file}" target="_blank">{e.get('subject', '')}</a></td>
</tr>"""

index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Rental-Housing 铏氭嫙鏀朵欢绠?/title>
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
.note {{ background: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 16px; margin: 20px 0; color: #854d0e; font-size: 14px; }}
</style></head>
<body>
<h1>Rental-Housing <span>铏氭嫙鏀朵欢绠?鈥?娴嬭瘯閭欢棰勮</span></h1>
<div class="note">
    <strong>鎻愮ず锛?/strong>浠ヤ笅鏄ā鎷熺湡瀹炲満鏅殑閫氱煡閭欢銆傚疄闄呯郴缁熶腑锛岃繖浜涢偖浠跺皢閫氳繃 QQ閭 SMTP 鍙戦€佸埌鐢ㄦ埛閭銆?    鍙偣鍑婚偖浠朵富棰樻煡鐪嬪畬鏁存覆鏌撴晥鏋溿€?</div>
<table>
<tr><th>鏃堕棿</th><th>鍙戜欢浜?/th><th>鏀朵欢浜?/th><th>涓婚</th></tr>
{rows}
</table>
<p style="color:#94a3b8;font-size:12px;margin-top:16px;">
    铏氭嫙 SMTP 鏀朵欢绠?| 閭欢淇濆瓨鍦?<code>test_emails/</code> 鐩綍
</p>
</body>
</html>"""

index_path = os.path.join(OUT_DIR, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_html)

url = f"file:///{index_path.replace(chr(92), '/')}"
print(f"\n[OK] 鍏辩敓鎴?{len(emails)} 灏佹祴璇曢偖浠?)
print(f"[OPEN] {url}")

webbrowser.open(url)

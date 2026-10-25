"""鍙戦€佹祴璇曢偖浠跺埌 your-email@example.com 鈥?妯℃嫙閫氱煡閭欢鏁堟灉銆?
浣跨敤 QQ 閭 SMTP锛岄渶瑕佹巿鏉冪爜锛堝湪 QQ 閭璁剧疆 鈫?璐︽埛 鈫?POP3/SMTP 鏈嶅姟涓敓鎴愶級銆?"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 鈹€鈹€ 閰嶇疆 鈹€鈹€
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@example.com"  # 鍙戜欢浜猴紙浣犺嚜宸憋級
TO_EMAIL = "your-email@example.com"       # 鏀朵欢浜猴紙浣犺嚜宸憋級

# 鈹€鈹€ 鎺堟潈鐮?鈹€鈹€
import getpass
AUTH_CODE = getpass.getpass("璇疯緭鍏?QQ 閭鎺堟潈鐮侊紙16浣嶏紝涓嶆槸QQ瀵嗙爜锛? ")

# 鈹€鈹€ 鏋勫缓娴嬭瘯閭欢 鈹€鈹€
now = datetime.now().strftime("%Y-%m-%d %H:%M")

msg = MIMEMultipart("alternative")
msg["Subject"] = f"銆愮鎴垮钩鍙?- 娴嬭瘯閭欢銆戦€氱煡绯荤粺楠岃瘉 {now}"
msg["From"] = f"绉熸埧骞冲彴 <{SENDER_EMAIL}>"
msg["To"] = TO_EMAIL

html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fa;padding:24px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;">

<!-- Header -->
<tr>
<td style="background:linear-gradient(135deg,#2563eb,#1d4ed8);padding:32px 40px;text-align:center;">
<h1 style="margin:0;color:#ffffff;font-size:22px;">绉熸埧鏅鸿兘骞冲彴</h1>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:32px 40px;">

<h2 style="color:#1e293b;font-size:20px;">馃摤 閫氱煡绯荤粺娴嬭瘯閭欢</h2>
<p style="color:#475569;font-size:15px;line-height:1.7;">
鎮ㄥソ锛佽繖鏄竴灏佹潵鑷鎴挎櫤鑳藉钩鍙扮殑<strong>娴嬭瘯閭欢</strong>銆?</p>

<!-- Info Card -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;padding:20px;margin-bottom:24px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>鍙戦€佹椂闂达細</strong>{now}</p>
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>閭欢绫诲瀷锛?/strong>閫氱煡绯荤粺杩為€氭€ф祴璇?/p>
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>SMTP 鐘舵€侊細</strong>鉁?QQ閭 SMTP 杩炴帴姝ｅ父</p>
<p style="margin:0;color:#0c4a6e;font-size:14px;"><strong>璇存槑锛?/strong>濡傛灉浣犳敹鍒拌繖灏侀偖浠讹紝璇存槑閭欢閫氶亾宸叉墦閫?/p>
</td></tr>
</table>

<!-- 妯℃嫙閫氱煡閭欢鏍峰紡 -->
<h3 style="color:#1e293b;font-size:17px;">馃搵 杩欐槸鏈潵绉熷浼氭敹鍒扮殑閫氱煡閭欢绀轰緥锛?/h3>

<!-- 妯℃嫙锛氭敮浠樺垱寤洪€氱煡 -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin-bottom:16px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#2563eb;font-size:15px;"><strong>馃挸 鏀粯璁㈠崟宸插垱寤?/strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">璁㈠崟缂栧彿锛?strong>#42</strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">鎴挎簮鍚嶇О锛?strong>娴锋穩瀛﹁嫅鍏瘬 A-301</strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">鏀粯閲戦锛?strong>CNY 6,000.00</strong></p>
<p style="margin:0;color:#dc2626;font-size:14px;">鈴?鏀粯鎴锛?strong>2026-08-07 18:00锛堝墿浣欑害24灏忔椂锛?/strong></p>
</td></tr>
</table>

<!-- 妯℃嫙锛氬悎鍚岀敓鎴愰€氱煡 -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:20px;margin-bottom:16px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#166534;font-size:15px;"><strong>馃搫 鍚堝悓宸茬敓鎴愶紝璇风缃?/strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">鍚堝悓缂栧彿锛?strong>HRTA-20260806-00000042-V1</strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">绛剧讲鎴锛?strong>2026-08-13 18:00锛堝墿浣?澶╋級</strong></p>
<p style="margin:0;color:#64748b;font-size:14px;">閫炬湡鏈缃茬殑璁㈠崟灏嗚鍙栨秷锛屾娂閲戜笉浜堥€€杩樸€?/p>
</td></tr>
</table>

</td>
</tr>

<!-- Footer -->
<tr>
<td style="background:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;">
<p style="margin:0 0 8px;color:#64748b;font-size:12px;">
姝ら偖浠剁敱绯荤粺鑷姩鍙戦€侊紝璇峰嬁鐩存帴鍥炲銆?br>
濡傞渶甯姪锛岃鑱旂郴瀹㈡湇锛歴upport@rental-platform.com
</p>
<p style="margin:0;color:#94a3b8;font-size:12px;">
漏 2026 绉熸埧鏅鸿兘骞冲彴 鐗堟潈鎵€鏈?</p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>
"""

msg.attach(MIMEText(html, "html", "utf-8"))

try:
    print(f"姝ｅ湪杩炴帴 {SMTP_HOST}:{SMTP_PORT} ...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
    server.ehlo()
    server.starttls()
    server.ehlo()
    print(f"姝ｅ湪鐧诲綍 {SENDER_EMAIL} ...")
    server.login(SENDER_EMAIL, AUTH_CODE)
    print(f"姝ｅ湪鍙戦€佸埌 {TO_EMAIL} ...")
    server.sendmail(SENDER_EMAIL, TO_EMAIL, msg.as_string())
    server.quit()
    print(f"\n鉁?閭欢鍙戦€佹垚鍔燂紒璇锋鏌?{TO_EMAIL} 鐨勬敹浠剁锛堝彲鑳藉湪鍨冨溇绠憋級銆?)
except smtplib.SMTPAuthenticationError:
    print("\n鉂?鐧诲綍澶辫触锛氭巿鏉冪爜閿欒銆傝鍦?QQ閭璁剧疆鈫掕处鎴封啋POP3/SMTP鏈嶅姟 涓敓鎴愭巿鏉冪爜銆?)
except Exception as e:
    print(f"\n鉂?鍙戦€佸け璐? {e}")

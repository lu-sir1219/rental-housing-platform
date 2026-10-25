"""鐩存帴鍙戦€佹祴璇曢偖浠跺埌 your-email@example.com锛堢粫杩?Celery锛屽悓姝ュ彂閫侊級銆?
浣跨敤鏂瑰紡锛?    python send_email_direct.py

鍓嶆彁锛歜ackend/.env 涓凡閰嶇疆 SMTP_PASSWORD锛圦Q 鎺堟潈鐮侊級銆?濡傛灉鏈厤缃紝鑴氭湰浼氭彁绀哄苟閫€鍑恒€?"""
import asyncio
import os
import sys

# 鍔犺浇 .env
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(env_path)

# 瑕嗙洊鐜鍙橀噺鍚庨噸鏂板鍏?settings
from app.services.email_service import EmailService


async def main():
    svc = EmailService()

    # 妫€鏌ラ厤缃?    if not svc.settings.smtp_password or svc.settings.smtp_password == "PLACEHOLDER_QQ_AUTH_CODE":
        print("=" * 60)
        print("  SMTP 鏈厤缃?QQ 鎺堟潈鐮?)
        print("=" * 60)
        print()
        print("  璇峰湪 backend/.env 涓皢 SMTP_PASSWORD 鏀逛负浣犵殑 QQ 鎺堟潈鐮侊細")
        print("    1. 鐧诲綍 QQ閭 鈫?璁剧疆 鈫?璐︽埛")
        print("    2. 鎵惧埌 POP3/SMTP鏈嶅姟 鈫?鐢熸垚鎺堟潈鐮?)
        print("    3. 澶嶅埗 16 浣嶆巿鏉冪爜")
        print("    4. 淇敼 backend/.env: SMTP_PASSWORD=浣犵殑鎺堟潈鐮?)
        print()
        print("  鐒跺悗閲嶆柊杩愯: python send_email_direct.py")
        print()
        return

    to_email = "your-email@example.com"
    subject = "銆愮鎴垮钩鍙?- 娴嬭瘯閭欢銆戦€氱煡绯荤粺楠岃瘉"

    html_body = """\
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

<h2 style="color:#1e293b;font-size:20px;">閫氱煡绯荤粺娴嬭瘯閭欢</h2>
<p style="color:#475569;font-size:15px;line-height:1.7;">
鎮ㄥソ锛佽繖鏄竴灏佹潵鑷鎴挎櫤鑳藉钩鍙扮殑<strong>娴嬭瘯閭欢</strong>銆?</p>

<!-- Info Card -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;padding:20px;margin-bottom:24px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>鍙戦€侀€氶亾锛?/strong>QQ閭 SMTP (smtp.qq.com:587)</p>
<p style="margin:0 0 8px;color:#0c4a6e;font-size:14px;"><strong>SMTP 鐘舵€侊細</strong>QQ閭 SMTP 杩炴帴姝ｅ父</p>
<p style="margin:0;color:#0c4a6e;font-size:14px;"><strong>璇存槑锛?/strong>濡傛灉浣犳敹鍒拌繖灏侀偖浠讹紝璇存槑閭欢閫氶亾宸叉墦閫?/p>
</td></tr>
</table>

<!-- 妯℃嫙閫氱煡閭欢鏍峰紡 -->
<h3 style="color:#1e293b;font-size:17px;">鏈潵绉熷浼氭敹鍒扮殑閫氱煡閭欢绀轰緥锛?/h3>

<!-- 妯℃嫙锛氭敮浠樺垱寤洪€氱煡 -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin-bottom:16px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#2563eb;font-size:15px;"><strong>[鏀粯] 鏀粯璁㈠崟宸插垱寤?/strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">璁㈠崟缂栧彿锛?strong>#42</strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">鎴挎簮鍚嶇О锛?strong>娴锋穩瀛﹁嫅鍏瘬 A-301</strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">鏀粯閲戦锛?strong>CNY 6,000.00</strong></p>
<p style="margin:0;color:#dc2626;font-size:14px;">鏀粯鎴锛?strong>24灏忔椂鍐?/strong></p>
</td></tr>
</table>

<!-- 妯℃嫙锛氬悎鍚岀敓鎴愰€氱煡 -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:20px;margin-bottom:16px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#166534;font-size:15px;"><strong>[鍚堝悓] 鍚堝悓宸茬敓鎴愶紝璇风缃?/strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">鍚堝悓缂栧彿锛?strong>HRTA-20260806-00000042-V1</strong></p>
<p style="margin:0 0 6px;color:#64748b;font-size:14px;">绛剧讲鎴锛?strong>7澶╁唴</strong></p>
<p style="margin:0;color:#64748b;font-size:14px;">閫炬湡鏈缃茬殑璁㈠崟灏嗚鍙栨秷锛屾娂閲戜笉浜堥€€杩樸€?/p>
</td></tr>
</table>

<!-- 妯℃嫙锛氶璁㈡垚鍔?-->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#fefce8;border:1px solid #fef08a;border-radius:8px;padding:20px;margin-bottom:16px;">
<tr><td style="padding:8px 0;">
<p style="margin:0 0 8px;color:#854d0e;font-size:15px;"><strong>[棰勮] 棰勮鎴愬姛锛?/strong></p>
<p style="margin:0;color:#64748b;font-size:14px;">鎴挎簮宸茬‘璁わ紝鍏ヤ綇鏃ユ湡锛?strong>2026-09-01</strong></p>
</td></tr>
</table>

<p style="color:#94a3b8;font-size:13px;margin-top:24px;">
鎵€鏈夐噾棰濄€佽鍗曞強鍚堝悓浠ヨ鍗曡鎯呴〉璁板綍涓哄噯銆?</p>

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
&copy; 2026 绉熸埧鏅鸿兘骞冲彴 鐗堟潈鎵€鏈?</p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>
"""

    print(f"姝ｅ湪鍙戦€佹祴璇曢偖浠跺埌 {to_email} ...")
    print(f"SMTP: {svc.settings.smtp_host}:{svc.settings.smtp_port}")
    print(f"鍙戜欢浜? {svc.settings.smtp_user}")

    try:
        result = await svc.send(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
        )
        print(f"缁撴灉: {result}")
        if result.get("status") == "sent":
            print(f"[OK] 閭欢鍙戦€佹垚鍔燂紒璇锋鏌?{to_email} 鐨勬敹浠剁锛堝彲鑳藉湪鍨冨溇绠憋級銆?)
        else:
            print(f"[SKIP] 閭欢鏈彂閫? {result.get('reason', 'unknown')}")
    except Exception as e:
        print(f"[FAIL] 鍙戦€佸け璐? {e}")


if __name__ == "__main__":
    asyncio.run(main())

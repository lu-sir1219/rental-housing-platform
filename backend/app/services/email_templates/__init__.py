"""閭欢 HTML 妯℃澘娓叉煋銆?
妯℃澘鍒嗕负涓ゅ眰锛?- base.html: 瀹屾暣 HTML 鏂囨。锛孋SS 鏍峰紡锛岀敤 {{body}} 浣滀负鍐呭鍗犱綅绗?- 鍚勬ā鏉? 鍙湁 body 鍐呭 HTML锛屽彉閲忕敤 {var_name} 鏍煎紡

娓叉煋娴佺▼锛氬厛 fill body 妯℃澘 鈫?鏇挎崲 base 涓殑 {{body}} 鈫?fill base 鍙橀噺
"""

from datetime import datetime
from pathlib import Path

_TEMPLATE_DIR = Path(__file__).parent

# 缂撳瓨宸茶鍙栫殑妯℃澘鍐呭
_cache: dict[str, str] = {}


def render(template_name: str, **kwargs) -> str:
    """璇诲彇妯℃澘鏂囦欢骞跺～鍏呭彉閲忋€?
    Args:
        template_name: 妯℃澘鏂囦欢鍚嶏紙涓嶅惈 .html 鍚庣紑锛夛紝濡?"welcome"
        **kwargs: 妯℃澘鍙橀噺锛屽父鐢ㄥ彉閲忥細
            app_name, support_email, current_year锛坆ase 灞傦級
            user_name, property_title, ...锛堜笟鍔″眰锛?
    Returns:
        娓叉煋鍚庣殑瀹屾暣 HTML 瀛楃涓?    """
    # 1. 璇诲彇 body 妯℃澘骞跺～鍏呬笟鍔″彉閲?    body_template = _read(template_name + ".html")
    body_html = body_template.format(**kwargs)

    # 2. 璇诲彇 base 妯℃澘锛屾浛鎹?{{body}} 鍗犱綅绗?    base = _read("base.html")
    html = base.replace("{{body}}", body_html)

    # 3. 濉厖 base 灞傚彉閲忥紙鎻愪緵榛樿鍊硷級
    return html.format(
        app_name=kwargs.get("app_name", "Rental Housing"),
        support_email=kwargs.get("support_email", "support@example.com"),
        current_year=kwargs.get("current_year", str(datetime.utcnow().year)),
    )


def _read(filename: str) -> str:
    """璇诲彇妯℃澘鏂囦欢鍘熷鍐呭锛堝甫缂撳瓨锛夈€?""
    if filename not in _cache:
        path = _TEMPLATE_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"閭欢妯℃澘涓嶅瓨鍦? {path}")
        _cache[filename] = path.read_text(encoding="utf-8")
    return _cache[filename]

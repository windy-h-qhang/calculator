import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class CurrencyRateService:
    API_BASE = "https://api.frankfurter.dev"
    LEGACY_API_BASE = "https://api.frankfurter.app/latest"
    COMMON_CURRENCIES = [
        ("USD", "美元"),
        ("CNY", "人民币"),
        ("EUR", "欧元"),
        ("JPY", "日元"),
        ("GBP", "英镑"),
        ("HKD", "港币"),
        ("AUD", "澳元"),
        ("CAD", "加元"),
        ("CHF", "瑞士法郎"),
        ("SGD", "新加坡元"),
        ("KRW", "韩元"),
        ("THB", "泰铢"),
        ("NZD", "新西兰元"),
        ("SEK", "瑞典克朗"),
        ("NOK", "挪威克朗"),
        ("DKK", "丹麦克朗"),
        ("INR", "印度卢比"),
        ("BRL", "巴西雷亚尔"),
        ("MXN", "墨西哥比索"),
        ("ZAR", "南非兰特"),
    ]

    @classmethod
    def fetch_rate(cls, base, quote):
        base = base.upper()
        quote = quote.upper()
        if base == quote:
            return {
                "base": base,
                "quote": quote,
                "rate": 1.0,
                "date": datetime.now().date().isoformat(),
            }

        try:
            return cls.fetch_v2_rate(base, quote)
        except Exception:
            return cls.fetch_legacy_rate(base, quote)

    @classmethod
    def fetch_v2_rate(cls, base, quote):
        payload = cls.get_json(f"{cls.API_BASE}/v2/rate/{base}/{quote}")
        if "rate" not in payload:
            raise ValueError("汇率响应中缺少 rate 字段")
        return {
            "base": payload.get("base", base),
            "quote": payload.get("quote", quote),
            "rate": float(payload["rate"]),
            "date": payload.get("date", ""),
        }

    @classmethod
    def fetch_legacy_rate(cls, base, quote):
        query = urlencode({"base": base, "symbols": quote})
        payload = cls.get_json(f"{cls.LEGACY_API_BASE}?{query}")
        rates = payload.get("rates", {})
        if quote not in rates:
            raise ValueError(f"无法获取 {base} 到 {quote} 的汇率")

        return {
            "base": payload.get("base", base),
            "quote": quote,
            "rate": float(rates[quote]),
            "date": payload.get("date", ""),
        }

    @staticmethod
    def get_json(url):
        request = Request(
            url,
            headers={
                "User-Agent": "PyQt-Calculator/1.0",
                "Accept": "application/json",
            },
        )
        with urlopen(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))

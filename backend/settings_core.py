from backend.persistence import get_store


class SettingsService:
    DEFAULTS = {
        "theme": "深色",
        "default_mode": "标准",
        "angle_mode": "DEG",
        "precision": 6,
        "default_currency_base": "USD",
        "default_currency_quote": "CNY",
        "auto_refresh_currency": True,
    }

    THEMES = ["深色", "浅色", "跟随系统"]
    DEFAULT_MODES = ["标准", "科学", "绘图", "高等数学", "程序员", "汇率转换", "单位换算", "日期计算"]

    @classmethod
    def get_settings(cls):
        return get_store().get_settings(cls.DEFAULTS)

    @classmethod
    def update_settings(cls, values):
        current = cls.get_settings()
        clean = {}
        for key, value in values.items():
            if key not in cls.DEFAULTS:
                continue
            clean[key] = cls.normalize(key, value)
        current.update(clean)
        get_store().set_settings(clean)
        return current

    @classmethod
    def normalize(cls, key, value):
        if key == "theme":
            return value if value in cls.THEMES else cls.DEFAULTS[key]
        if key == "default_mode":
            return value if value in cls.DEFAULT_MODES else cls.DEFAULTS[key]
        if key == "angle_mode":
            return value if value in {"DEG", "RAD"} else cls.DEFAULTS[key]
        if key == "precision":
            return max(0, min(12, int(value)))
        if key == "auto_refresh_currency":
            return bool(value)
        return str(value)

    @classmethod
    def effective_theme(cls):
        theme = cls.get_settings().get("theme", "深色")
        if theme == "跟随系统":
            return "深色"
        return theme

class UnitConverter:
    CATEGORIES = {
        "长度": {
            "base": "米",
            "units": {
                "毫米": 0.001,
                "厘米": 0.01,
                "米": 1.0,
                "千米": 1000.0,
                "英寸": 0.0254,
                "英尺": 0.3048,
                "码": 0.9144,
                "英里": 1609.344,
            },
        },
        "面积": {
            "base": "平方米",
            "units": {
                "平方毫米": 0.000001,
                "平方厘米": 0.0001,
                "平方米": 1.0,
                "公顷": 10000.0,
                "平方千米": 1000000.0,
                "平方英尺": 0.09290304,
                "英亩": 4046.8564224,
            },
        },
        "体积": {
            "base": "升",
            "units": {
                "毫升": 0.001,
                "升": 1.0,
                "立方米": 1000.0,
                "茶匙": 0.00492892159375,
                "汤匙": 0.01478676478125,
                "液量盎司": 0.0295735295625,
                "杯": 0.2365882365,
                "品脱": 0.473176473,
                "加仑": 3.785411784,
            },
        },
        "质量": {
            "base": "千克",
            "units": {
                "毫克": 0.000001,
                "克": 0.001,
                "千克": 1.0,
                "吨": 1000.0,
                "盎司": 0.028349523125,
                "磅": 0.45359237,
            },
        },
        "温度": {
            "base": "摄氏度",
            "units": {
                "摄氏度": "celsius",
                "华氏度": "fahrenheit",
                "开尔文": "kelvin",
            },
        },
        "速度": {
            "base": "米/秒",
            "units": {
                "米/秒": 1.0,
                "千米/小时": 1 / 3.6,
                "英里/小时": 0.44704,
                "节": 0.514444444,
                "英尺/秒": 0.3048,
            },
        },
        "时间": {
            "base": "秒",
            "units": {
                "毫秒": 0.001,
                "秒": 1.0,
                "分钟": 60.0,
                "小时": 3600.0,
                "天": 86400.0,
                "周": 604800.0,
                "年": 31557600.0,
            },
        },
        "数据大小": {
            "base": "字节",
            "units": {
                "位": 0.125,
                "字节": 1.0,
                "KB": 1024.0,
                "MB": 1024.0**2,
                "GB": 1024.0**3,
                "TB": 1024.0**4,
            },
        },
        "能量": {
            "base": "焦耳",
            "units": {
                "焦耳": 1.0,
                "千焦": 1000.0,
                "卡路里": 4.184,
                "千卡": 4184.0,
                "瓦时": 3600.0,
                "千瓦时": 3600000.0,
            },
        },
        "功率": {
            "base": "瓦",
            "units": {
                "瓦": 1.0,
                "千瓦": 1000.0,
                "马力": 745.699872,
                "英制马力": 745.699872,
                "英热单位/小时": 0.29307107,
            },
        },
    }

    @classmethod
    def categories(cls):
        return list(cls.CATEGORIES.keys())

    @classmethod
    def units(cls, category):
        return list(cls.CATEGORIES[category]["units"].keys())

    @classmethod
    def convert(cls, value, category, from_unit, to_unit):
        value = float(value)
        if category not in cls.CATEGORIES:
            raise ValueError("未知单位类型")
        units = cls.CATEGORIES[category]["units"]
        if from_unit not in units or to_unit not in units:
            raise ValueError("未知单位")
        if category == "温度":
            return cls.convert_temperature(value, from_unit, to_unit)
        base_value = value * units[from_unit]
        return base_value / units[to_unit]

    @staticmethod
    def convert_temperature(value, from_unit, to_unit):
        if from_unit == "摄氏度":
            celsius = value
        elif from_unit == "华氏度":
            celsius = (value - 32) * 5 / 9
        elif from_unit == "开尔文":
            celsius = value - 273.15
        else:
            raise ValueError("未知温度单位")

        if to_unit == "摄氏度":
            return celsius
        if to_unit == "华氏度":
            return celsius * 9 / 5 + 32
        if to_unit == "开尔文":
            return celsius + 273.15
        raise ValueError("未知温度单位")

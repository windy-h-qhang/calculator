import sympy as sp


class AdvancedMathEngine:
    VARIABLES = {
        name: sp.symbols(name)
        for name in ("x", "y", "z", "t", "a", "b", "c", "n")
    }
    LOCALS = {
        **VARIABLES,
        "pi": sp.pi,
        "π": sp.pi,
        "e": sp.E,
        "E": sp.E,
        "oo": sp.oo,
        "inf": sp.oo,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "asin": sp.asin,
        "acos": sp.acos,
        "atan": sp.atan,
        "sqrt": sp.sqrt,
        "ln": sp.log,
        "log": sp.log,
        "log10": lambda value: sp.log(value, 10),
        "exp": sp.exp,
        "abs": sp.Abs,
    }

    @classmethod
    def calculate(
        cls,
        operation,
        expression,
        variable="x",
        order=1,
        point="0",
        lower="",
        upper="",
    ):
        symbol = cls.variable(variable)
        expr = cls.parse_equation_or_expression(expression)
        steps = []

        if operation == "求导":
            result = sp.diff(expr, symbol)
            steps.append(f"对 {symbol} 求一阶导数。")
            steps.append(f"d/d{symbol}({sp.sstr(expr)})")
        elif operation == "偏导":
            result = sp.diff(expr, symbol)
            steps.append(f"把其他变量视为常量，对 {symbol} 求偏导。")
            steps.append(f"∂/∂{symbol}({sp.sstr(expr)})")
        elif operation == "高阶导数":
            order = cls.safe_int(order, default=2)
            result = sp.diff(expr, symbol, order)
            steps.append(f"对 {symbol} 连续求导 {order} 次。")
            steps.append(f"d^{order}/d{symbol}^{order}({sp.sstr(expr)})")
        elif operation == "不定积分":
            result = sp.integrate(expr, symbol)
            steps.append(f"对 {symbol} 做不定积分。")
            steps.append("结果省略积分常数 C。")
        elif operation == "定积分":
            lower_value = cls.parse_expression(lower)
            upper_value = cls.parse_expression(upper)
            result = sp.integrate(expr, (symbol, lower_value, upper_value))
            steps.append(f"在区间 [{sp.sstr(lower_value)}, {sp.sstr(upper_value)}] 上积分。")
        elif operation == "极限":
            point_value = cls.parse_expression(point)
            result = sp.limit(expr, symbol, point_value)
            steps.append(f"计算 {symbol} -> {sp.sstr(point_value)} 的双侧极限。")
        elif operation == "左极限":
            point_value = cls.parse_expression(point)
            result = sp.limit(expr, symbol, point_value, dir="-")
            steps.append(f"计算 {symbol} -> {sp.sstr(point_value)}- 的左极限。")
        elif operation == "右极限":
            point_value = cls.parse_expression(point)
            result = sp.limit(expr, symbol, point_value, dir="+")
            steps.append(f"计算 {symbol} -> {sp.sstr(point_value)}+ 的右极限。")
        elif operation == "泰勒展开":
            point_value = cls.parse_expression(point)
            order = cls.safe_int(order, default=6)
            result = sp.series(expr, symbol, point_value, order)
            steps.append(f"在 {symbol} = {sp.sstr(point_value)} 处展开到 {order - 1} 阶。")
        elif operation == "方程求解":
            equation = cls.parse_equation(expression)
            result = sp.solve(equation, symbol)
            steps.append(f"把方程整理为关于 {symbol} 的代数方程。")
            steps.append("返回满足方程的精确解。")
        elif operation == "化简":
            result = sp.simplify(expr)
            steps.append("对表达式做代数化简。")
        else:
            raise ValueError("不支持的运算类型")

        simplified = cls.simplify_result(result, operation)
        return {
            "operation": operation,
            "exact": sp.sstr(simplified),
            "pretty": cls.pretty(simplified),
            "numeric": cls.numeric_text(simplified),
            "steps": steps,
        }

    @classmethod
    def parse_equation_or_expression(cls, text):
        if "=" in text:
            equation = cls.parse_equation(text)
            return equation.lhs - equation.rhs
        return cls.parse_expression(text)

    @classmethod
    def parse_equation(cls, text):
        if "=" not in text:
            expression = cls.parse_expression(text)
            return sp.Eq(expression, 0)
        left, right = text.split("=", 1)
        return sp.Eq(cls.parse_expression(left), cls.parse_expression(right))

    @classmethod
    def parse_expression(cls, text):
        text = str(text).strip()
        if not text:
            raise ValueError("请输入表达式")
        normalized = cls.normalize(text)
        return sp.sympify(normalized, locals=cls.LOCALS)

    @classmethod
    def variable(cls, name):
        name = (name or "x").strip()
        if name not in cls.VARIABLES:
            cls.VARIABLES[name] = sp.symbols(name)
            cls.LOCALS[name] = cls.VARIABLES[name]
        return cls.VARIABLES[name]

    @staticmethod
    def normalize(text):
        return (
            text.replace("^", "**")
            .replace("π", "pi")
            .replace("∞", "oo")
            .replace("√", "sqrt")
        )

    @staticmethod
    def safe_int(value, default):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = default
        return max(1, parsed)

    @staticmethod
    def numeric_text(result):
        try:
            if isinstance(result, (list, tuple)):
                return ", ".join(sp.sstr(sp.N(item, 12)) for item in result)
            numeric = sp.N(result, 12)
            return sp.sstr(numeric)
        except Exception:
            return "不可用"

    @staticmethod
    def simplify_result(result, operation):
        if operation == "泰勒展开":
            return result
        if isinstance(result, list):
            return [sp.simplify(item) for item in result]
        if isinstance(result, tuple):
            return tuple(sp.simplify(item) for item in result)
        return sp.simplify(result)

    @staticmethod
    def pretty(value):
        return sp.pretty(value, use_unicode=True)

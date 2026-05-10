import ast
import math
import operator as op
from dataclasses import dataclass


class SafeCalculator:
    """A small AST-based calculator to avoid using eval directly."""

    OPERATORS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Mod: op.mod,
        ast.Pow: op.pow,
        ast.USub: op.neg,
        ast.UAdd: op.pos,
    }
    FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sqrt": math.sqrt,
        "log": math.log10,
        "ln": math.log,
        "abs": abs,
    }
    CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    @classmethod
    def calculate(cls, expression: str, variables=None):
        try:
            node = ast.parse(expression, mode="eval").body
            return cls._eval(node, variables or {})
        except ZeroDivisionError as exc:
            raise ZeroDivisionError("除数不能为 0") from exc
        except Exception as exc:
            raise ValueError("表达式错误") from exc

    @classmethod
    def _eval(cls, node, variables=None):
        variables = variables or {}
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("非法数字")

        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            if node.id in cls.CONSTANTS:
                return cls.CONSTANTS[node.id]
            raise ValueError("未知常量")

        if isinstance(node, ast.BinOp):
            left = cls._eval(node.left, variables)
            right = cls._eval(node.right, variables)
            operator_type = type(node.op)
            if operator_type not in cls.OPERATORS:
                raise ValueError("不支持的运算符")
            return cls.OPERATORS[operator_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = cls._eval(node.operand, variables)
            operator_type = type(node.op)
            if operator_type not in cls.OPERATORS:
                raise ValueError("不支持的符号")
            return cls.OPERATORS[operator_type](operand)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("非法函数")
            if node.func.id == "fact":
                return cls._factorial(node.args, variables)
            if node.func.id == "reciprocal":
                return cls._reciprocal(node.args, variables)
            if node.func.id not in cls.FUNCTIONS:
                raise ValueError("不支持的函数")
            if len(node.args) != 1:
                raise ValueError("函数参数错误")
            return cls.FUNCTIONS[node.func.id](cls._eval(node.args[0], variables))

        raise ValueError("非法表达式")

    @classmethod
    def _factorial(cls, args, variables=None):
        if len(args) != 1:
            raise ValueError("函数参数错误")
        value = cls._eval(args[0], variables)
        if not float(value).is_integer() or value < 0:
            raise ValueError("阶乘只支持非负整数")
        return math.factorial(int(value))

    @classmethod
    def _reciprocal(cls, args, variables=None):
        if len(args) != 1:
            raise ValueError("函数参数错误")
        value = cls._eval(args[0], variables)
        if value == 0:
            raise ZeroDivisionError("除数不能为 0")
        return 1 / value


@dataclass(frozen=True)
class HistoryItem:
    expression: str
    result: str


class CalculationHistory:
    def __init__(self, limit=30):
        self.limit = limit
        self._items = []

    def add(self, expression, result):
        item = HistoryItem(expression=expression, result=str(result))
        self._items.insert(0, item)
        if len(self._items) > self.limit:
            self._items = self._items[: self.limit]

    def clear(self):
        self._items.clear()

    def items(self):
        return list(self._items)

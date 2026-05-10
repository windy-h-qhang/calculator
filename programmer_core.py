import ast
import operator as op
import re


class ProgrammerCalculatorEngine:
    WORD_SIZES = {
        "QWORD": 64,
        "DWORD": 32,
        "WORD": 16,
        "BYTE": 8,
    }
    BASES = {
        "HEX": 16,
        "DEC": 10,
        "OCT": 8,
        "BIN": 2,
    }
    OPERATORS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod,
        ast.BitAnd: op.and_,
        ast.BitOr: op.or_,
        ast.BitXor: op.xor,
        ast.LShift: op.lshift,
        ast.RShift: op.rshift,
    }
    UNARY_OPERATORS = {
        ast.Invert: op.invert,
        ast.USub: op.neg,
        ast.UAdd: op.pos,
    }

    @classmethod
    def evaluate(cls, expression, base_name, word_size_name, signed=False):
        expression = expression.strip()
        if not expression:
            return 0

        python_expression = cls.to_python_expression(expression, base_name)
        node = ast.parse(python_expression, mode="eval").body
        value = cls.eval_node(node)
        return cls.apply_width(value, word_size_name, signed)

    @classmethod
    def to_python_expression(cls, expression, base_name):
        base = cls.BASES[base_name]
        replacements = {
            "AND": "&",
            "OR": "|",
            "XOR": "^",
            "NOT": "~",
            "LSH": "<<",
            "RSH": ">>",
            "MOD": "%",
            "×": "*",
            "÷": "//",
        }
        normalized = expression.upper()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        token_pattern = r"(?<![A-Z0-9])([A-F0-9]+)(?![A-Z0-9])"

        def convert_token(match):
            token = match.group(1)
            if cls.is_number_token(token, base):
                return str(int(token, base))
            return token

        return re.sub(token_pattern, convert_token, normalized)

    @classmethod
    def eval_node(cls, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)
            if operator_type not in cls.OPERATORS:
                raise ValueError("不支持的运算符")
            left = cls.eval_node(node.left)
            right = cls.eval_node(node.right)
            if operator_type in {ast.FloorDiv, ast.Mod} and right == 0:
                raise ZeroDivisionError("除数不能为 0")
            return cls.OPERATORS[operator_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)
            if operator_type not in cls.UNARY_OPERATORS:
                raise ValueError("不支持的符号")
            return cls.UNARY_OPERATORS[operator_type](cls.eval_node(node.operand))

        raise ValueError("表达式错误")

    @classmethod
    def apply_width(cls, value, word_size_name, signed=False):
        bits = cls.WORD_SIZES[word_size_name]
        masked = value & cls.mask(bits)
        if signed and masked >= 1 << (bits - 1):
            return masked - (1 << bits)
        return masked

    @classmethod
    def unsigned_value(cls, value, word_size_name):
        bits = cls.WORD_SIZES[word_size_name]
        return value & cls.mask(bits)

    @classmethod
    def mask(cls, bits):
        return (1 << bits) - 1

    @classmethod
    def format_value(cls, value, base_name, word_size_name, signed=False):
        if base_name == "DEC" and signed:
            return str(cls.apply_width(value, word_size_name, signed=True))

        unsigned = cls.unsigned_value(value, word_size_name)
        if base_name == "DEC":
            return str(unsigned)
        if base_name == "HEX":
            return f"{unsigned:X}"
        if base_name == "OCT":
            return oct(unsigned)[2:].upper()
        if base_name == "BIN":
            return cls.bit_string(value, word_size_name).replace(" ", "")
        raise ValueError("未知进制")

    @classmethod
    def conversion_rows(cls, value, word_size_name, signed=False):
        return {
            "HEX": cls.format_value(value, "HEX", word_size_name, signed),
            "DEC": cls.format_value(value, "DEC", word_size_name, signed),
            "OCT": cls.format_value(value, "OCT", word_size_name, signed),
            "BIN": cls.bit_string(value, word_size_name),
        }

    @classmethod
    def bit_string(cls, value, word_size_name):
        bits = cls.WORD_SIZES[word_size_name]
        unsigned = cls.unsigned_value(value, word_size_name)
        raw = f"{unsigned:0{bits}b}"
        return " ".join(raw[index : index + 4] for index in range(0, len(raw), 4))

    @classmethod
    def is_number_token(cls, token, base):
        allowed = "0123456789ABCDEF"[:base]
        return bool(token) and all(char in allowed for char in token)

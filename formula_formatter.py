import html

from advanced_math_core import AdvancedMathEngine


class FormulaFormatter:
    @staticmethod
    def pretty_expression(text):
        text = (text or "").strip()
        if not text:
            return ""
        try:
            if "=" in text:
                equation = AdvancedMathEngine.parse_equation(text)
                return AdvancedMathEngine.pretty(equation)
            expression = AdvancedMathEngine.parse_expression(text)
            return AdvancedMathEngine.pretty(expression)
        except Exception:
            return text

    @staticmethod
    def html_formula(text):
        pretty = FormulaFormatter.pretty_expression(text)
        if not pretty:
            pretty = " "
        return f"<pre>{html.escape(pretty)}</pre>"

    @staticmethod
    def html_block(title, content):
        return (
            f"<div class='section-title'>{html.escape(title)}</div>"
            f"<pre>{html.escape(content or '')}</pre>"
        )

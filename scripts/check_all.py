import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def check_backend():
    from backend.advanced_math_core import AdvancedMathEngine
    from backend.calculator_core import SafeCalculator
    from backend.currency_core import CurrencyRateService
    from backend.programmer_core import ProgrammerCalculatorEngine

    assert SafeCalculator.calculate("1+2*3") == 7
    assert round(SafeCalculator.calculate("sin(pi/2)"), 12) == 1
    assert SafeCalculator.calculate("x**2 + 1", {"x": 3}) == 10

    assert AdvancedMathEngine.calculate("求导", "x^3", "x")["exact"] == "3*x**2"
    assert AdvancedMathEngine.calculate("定积分", "x^2", "x", lower="0", upper="1")["exact"] == "1/3"
    assert AdvancedMathEngine.calculate("极限", "sin(x)/x", "x", point="0")["exact"] == "1"

    assert ProgrammerCalculatorEngine.evaluate("C+1", "HEX", "BYTE") == 13
    assert ProgrammerCalculatorEngine.evaluate("F XOR A", "HEX", "BYTE") == 5
    assert ProgrammerCalculatorEngine.evaluate("255 + 1", "DEC", "BYTE") == 0

    same_rate = CurrencyRateService.fetch_rate("USD", "USD")
    assert same_rate["rate"] == 1.0


def check_pyqt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QKeyEvent
    from PyQt5.QtWidgets import QApplication

    from frontends.pyqt.advanced_math_widget import AdvancedMathPanel
    from frontends.pyqt.calculator_ui import Calculator
    from frontends.pyqt.currency_widget import CurrencyConverterPanel
    from frontends.pyqt.graphing_widget import GraphingPanel
    from frontends.pyqt.programmer_widget import ProgrammerPanel

    app = QApplication.instance() or QApplication([])

    window = Calculator()
    window.set_programmer_mode()
    window.finish_resize_animation(window.target_size(), False)
    assert window.programmer_mode
    assert not window.history_panel.isVisible()

    programmer = ProgrammerPanel()
    programmer.set_base("HEX")
    for char in "C+1":
        programmer.keyPressEvent(QKeyEvent(QKeyEvent.KeyPress, 0, Qt.NoModifier, char))
    programmer.keyPressEvent(QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Return, Qt.NoModifier, ""))
    assert programmer.display.text() == "D"
    programmer.keyPressEvent(QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier, ""))
    assert programmer.display.text() == "0"

    graph = GraphingPanel()
    graph.function_input.setText("x^2 + 1/x")
    assert graph.formula_preview.text()
    graph.add_function()
    assert graph.function_list.count() == 1

    advanced = AdvancedMathPanel()
    advanced.operation_box.setCurrentText("极限")
    advanced.expression_input.setText("sin(x)/x")
    advanced.point_input.setText("0")
    advanced.calculate()
    assert advanced.history_list.count() == 1
    assert "精确结果" in advanced.result_view.toHtml()

    currency = CurrencyConverterPanel()
    assert not currency.has_loaded_rate
    currency.current_rate = {"base": "USD", "quote": "CNY", "rate": 6.8, "date": "test"}
    currency.amount_input.setText("2")
    currency.convert(add_history=True)
    assert currency.result_label.text() == "2.0000 USD = 13.6000 CNY"
    assert currency.history_list.count() == 1

    app.processEvents()


def main():
    check_backend()
    check_pyqt()
    print("All checks passed.")


if __name__ == "__main__":
    main()

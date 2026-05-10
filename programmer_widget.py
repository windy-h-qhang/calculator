from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from programmer_core import ProgrammerCalculatorEngine


class ProgrammerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.base_name = "DEC"
        self.word_size = "QWORD"
        self.signed_mode = False
        self.expression = ""
        self.value = 0
        self.setStyleSheet(self.panel_style())
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        main = QVBoxLayout()
        main.setSpacing(10)

        header = QLabel("程序员")
        header.setObjectName("Header")

        controls = QHBoxLayout()
        self.word_size_box = QComboBox()
        self.word_size_box.addItems(["QWORD", "DWORD", "WORD", "BYTE"])
        self.word_size_box.currentTextChanged.connect(self.set_word_size)

        self.signed_box = QComboBox()
        self.signed_box.addItems(["无符号", "有符号"])
        self.signed_box.currentTextChanged.connect(self.set_signed_mode)

        controls.addWidget(QLabel("字长"))
        controls.addWidget(self.word_size_box)
        controls.addWidget(QLabel("整数"))
        controls.addWidget(self.signed_box)
        controls.addStretch()

        self.expression_display = QLineEdit()
        self.expression_display.setReadOnly(True)
        self.expression_display.setAlignment(Qt.AlignRight)
        self.expression_display.setPlaceholderText("整数表达式")

        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setObjectName("Display")

        self.base_grid = QGridLayout()
        self.base_labels = {}
        for row, name in enumerate(["HEX", "DEC", "OCT", "BIN"]):
            title = QLabel(name)
            title.setObjectName("BaseName")
            value = QLabel("")
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value.setObjectName("BaseValue")
            self.base_labels[name] = value
            self.base_grid.addWidget(title, row, 0)
            self.base_grid.addWidget(value, row, 1)

        base_buttons = QHBoxLayout()
        self.base_buttons = {}
        for name in ["HEX", "DEC", "OCT", "BIN"]:
            button = QPushButton(name)
            button.clicked.connect(lambda _checked, value=name: self.set_base(value))
            self.base_buttons[name] = button
            base_buttons.addWidget(button)

        keypad = self.create_keypad()

        main.addWidget(header)
        main.addLayout(controls)
        main.addWidget(self.expression_display)
        main.addWidget(self.display)
        main.addLayout(self.base_grid)
        main.addLayout(base_buttons)
        main.addLayout(keypad)

        side = QVBoxLayout()
        bit_title = QLabel("位视图")
        bit_title.setObjectName("SubHeader")
        self.bit_view = QLabel("")
        self.bit_view.setWordWrap(True)
        self.bit_view.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.bit_view.setObjectName("BitView")

        history_title = QLabel("历史记录")
        history_title.setObjectName("SubHeader")
        self.history_list = QListWidget()
        clear_history = QPushButton("清空历史")
        clear_history.clicked.connect(self.history_list.clear)

        side.addWidget(bit_title)
        side.addWidget(self.bit_view)
        side.addWidget(history_title)
        side.addWidget(self.history_list, 1)
        side.addWidget(clear_history)

        layout.addLayout(main, 2)
        layout.addLayout(side, 1)
        self.setLayout(layout)
        self.refresh_display()

    def create_keypad(self):
        grid = QGridLayout()
        buttons = [
            ["A", "B", "C", "D", "E", "F"],
            ["NOT", "AND", "OR", "XOR", "LSH", "RSH"],
            ["7", "8", "9", "÷", "MOD", "⌫"],
            ["4", "5", "6", "×", "(", ")"],
            ["1", "2", "3", "-", "+", "="],
            ["±", "0", "C", "", "", ""],
        ]
        self.input_buttons = {}
        for row, button_row in enumerate(buttons):
            for col, text in enumerate(button_row):
                if not text:
                    continue
                button = QPushButton(text)
                button.setFixedHeight(42)
                button.clicked.connect(lambda _checked, value=text: self.handle_button(value))
                self.input_buttons[text] = button
                grid.addWidget(button, row, col)
        return grid

    def handle_button(self, text):
        if text == "C":
            self.expression = ""
            self.value = 0
        elif text == "⌫":
            self.expression = self.expression[:-1].rstrip()
        elif text == "=":
            self.calculate()
            return
        elif text == "±":
            self.value = -self.value
            self.expression = ProgrammerCalculatorEngine.format_value(
                self.value, self.base_name, self.word_size, self.signed_mode
            )
        elif text == "NOT":
            self.value = ProgrammerCalculatorEngine.apply_width(
                ~self.current_expression_value(), self.word_size, self.signed_mode
            )
            self.expression = ProgrammerCalculatorEngine.format_value(
                self.value, self.base_name, self.word_size, self.signed_mode
            )
        elif text in {"AND", "OR", "XOR", "LSH", "RSH", "MOD", "+", "-", "×", "÷"}:
            self.expression = f"{self.expression.strip()} {text} "
        else:
            self.expression += text
        self.refresh_display()

    def calculate(self):
        try:
            result = ProgrammerCalculatorEngine.evaluate(
                self.expression, self.base_name, self.word_size, self.signed_mode
            )
        except Exception as exc:
            self.display.setText(str(exc))
            return

        expression = self.expression
        self.value = result
        self.expression = ProgrammerCalculatorEngine.format_value(
            result, self.base_name, self.word_size, self.signed_mode
        )
        self.add_history(expression, self.expression)
        self.refresh_display()

    def current_expression_value(self):
        return ProgrammerCalculatorEngine.evaluate(
            self.expression or "0", self.base_name, self.word_size, self.signed_mode
        )

    def set_base(self, base_name):
        try:
            self.value = self.current_expression_value()
        except Exception:
            pass
        self.base_name = base_name
        self.expression = ProgrammerCalculatorEngine.format_value(
            self.value, self.base_name, self.word_size, self.signed_mode
        )
        self.refresh_display()

    def set_word_size(self, word_size):
        self.word_size = word_size
        self.value = ProgrammerCalculatorEngine.apply_width(
            self.value, self.word_size, self.signed_mode
        )
        self.expression = ProgrammerCalculatorEngine.format_value(
            self.value, self.base_name, self.word_size, self.signed_mode
        )
        self.refresh_display()

    def set_signed_mode(self, text):
        self.signed_mode = text == "有符号"
        self.expression = ProgrammerCalculatorEngine.format_value(
            self.value, self.base_name, self.word_size, self.signed_mode
        )
        self.refresh_display()

    def add_history(self, expression, result):
        if expression.strip():
            self.history_list.insertItem(0, QListWidgetItem(f"{expression} = {result}"))

    def refresh_display(self):
        self.expression_display.setText(self.expression)
        try:
            preview_value = self.current_expression_value()
        except Exception:
            preview_value = self.value

        self.display.setText(
            ProgrammerCalculatorEngine.format_value(
                preview_value, self.base_name, self.word_size, self.signed_mode
            )
        )
        rows = ProgrammerCalculatorEngine.conversion_rows(
            preview_value, self.word_size, self.signed_mode
        )
        for name, text in rows.items():
            self.base_labels[name].setText(text)
        self.bit_view.setText(rows["BIN"])
        self.refresh_button_states()

    def refresh_button_states(self):
        allowed = set("0123456789ABCDEF"[: ProgrammerCalculatorEngine.BASES[self.base_name]])
        for text, button in self.input_buttons.items():
            if len(text) == 1 and text in "0123456789ABCDEF":
                button.setEnabled(text in allowed)
        for name, button in self.base_buttons.items():
            button.setProperty("active", name == self.base_name)
            button.setStyleSheet(self.active_button_style() if name == self.base_name else "")

    @staticmethod
    def panel_style():
        return """
            ProgrammerPanel {
                background-color: #202124;
            }
            QLabel {
                color: #f1f3f4;
                font-weight: 600;
            }
            QLabel#Header {
                font-size: 22px;
                font-weight: 700;
            }
            QLabel#SubHeader {
                font-size: 16px;
                font-weight: 700;
            }
            QLabel#BaseName {
                color: #8ab4f8;
            }
            QLabel#BaseValue, QLabel#BitView {
                background-color: #171a1f;
                border: 1px solid #3c4043;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 8px;
                font-family: Menlo, Consolas, monospace;
            }
            QLabel#BitView {
                line-height: 150%;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #1f2328;
                border: 1px solid #5f6368;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 8px;
                selection-background-color: #174ea6;
            }
            QLineEdit#Display {
                font-size: 30px;
                font-weight: 700;
            }
            QPushButton {
                background-color: #3c4043;
                border: 1px solid #6f757d;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4b5055;
            }
            QPushButton:pressed {
                background-color: #303438;
            }
            QPushButton:disabled {
                color: #737980;
                background-color: #282c30;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #30363d;
            }
        """

    @staticmethod
    def active_button_style():
        return """
            QPushButton {
                background-color: #174ea6;
                border: 1px solid #8ab4f8;
                border-radius: 6px;
                color: #ffffff;
                padding: 8px;
            }
        """

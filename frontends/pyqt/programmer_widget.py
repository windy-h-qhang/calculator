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

from backend.programmer_core import ProgrammerCalculatorEngine


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
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(16)

        main = QVBoxLayout()
        main.setSpacing(12)

        header = QLabel("程序员")
        header.setObjectName("Header")

        controls = QHBoxLayout()
        self.word_size_box = QComboBox()
        self.word_size_box.addItems(["QWORD", "DWORD", "WORD", "BYTE"])
        self.configure_combo_box(self.word_size_box, 150)
        self.word_size_box.currentTextChanged.connect(self.set_word_size)

        self.signed_box = QComboBox()
        self.signed_box.addItems(["无符号", "有符号"])
        self.configure_combo_box(self.signed_box, 150)
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
            ["±", "0", "CE", "", "", ""],
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
        if text == "CE":
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
        elif len(text) == 1 and text in "0123456789ABCDEF":
            if self.expression == "0":
                self.expression = text
            else:
                self.expression += text
        else:
            self.expression += text
        self.refresh_display()

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text().upper()

        if text and text in "0123456789ABCDEF":
            if self.is_digit_allowed(text):
                self.handle_button(text)
            return

        key_map = {
            "+": "+",
            "-": "-",
            "*": "×",
            "/": "÷",
            "%": "MOD",
            "(": "(",
            ")": ")",
            "&": "AND",
            "|": "OR",
            "^": "XOR",
            "~": "NOT",
            "=": "=",
        }
        if text and text in key_map:
            self.handle_button(key_map[text])
            return

        if key in {Qt.Key_Return, Qt.Key_Enter}:
            self.handle_button("=")
            return
        if key == Qt.Key_Backspace:
            self.handle_button("⌫")
            return
        if key == Qt.Key_Escape:
            self.handle_button("CE")
            return
        if key == Qt.Key_Less:
            self.handle_button("LSH")
            return
        if key == Qt.Key_Greater:
            self.handle_button("RSH")
            return

        super().keyPressEvent(event)

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

    def is_digit_allowed(self, text):
        allowed = set("0123456789ABCDEF"[: ProgrammerCalculatorEngine.BASES[self.base_name]])
        return text in allowed

    @staticmethod
    def configure_combo_box(combo_box, width):
        combo_box.setMinimumWidth(width)
        combo_box.view().setMinimumWidth(width)

    @staticmethod
    def panel_style():
        return """
            ProgrammerPanel {
                background-color: #1e2228;
                border: 1px solid #303640;
                border-radius: 8px;
            }
            QLabel {
                color: #f4f6f8;
                font-weight: 600;
            }
            QLabel#Header {
                font-size: 28px;
                font-weight: 800;
            }
            QLabel#SubHeader {
                font-size: 16px;
                font-weight: 700;
            }
            QLabel#BaseName {
                color: #8ab4f8;
            }
            QLabel#BaseValue, QLabel#BitView {
                background-color: #111419;
                border: 1px solid #303640;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 10px;
                font-family: Menlo, Consolas, monospace;
            }
            QLabel#BitView {
                line-height: 150%;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #191d23;
                border: 1px solid #5c6572;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 9px 10px;
                selection-background-color: #155fbf;
            }
            QComboBox {
                min-height: 34px;
                padding-right: 28px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e2228;
                border: 1px solid #5c6572;
                color: #f4f6f8;
                selection-background-color: #203a5e;
                outline: 0;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 4px 12px;
            }
            QLineEdit#Display {
                font-size: 30px;
                font-weight: 800;
                background-color: #111419;
            }
            QPushButton {
                background-color: #343940;
                border: 1px solid #5c6572;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 8px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #40464f;
                border-color: #7b8592;
            }
            QPushButton:pressed {
                background-color: #252a31;
            }
            QPushButton:disabled {
                color: #737980;
                background-color: #252a31;
                border-color: #343940;
            }
            QListWidget::item {
                background-color: #1e2228;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 10px;
                margin: 3px;
            }
        """

    @staticmethod
    def active_button_style():
        return """
            QPushButton {
                background-color: #203a5e;
                border: 1px solid #75a7ea;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px;
                font-weight: 800;
            }
        """


from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from advanced_math_widget import AdvancedMathPanel
from calculator_core import CalculationHistory, SafeCalculator
from graphing_widget import GraphingPanel


class Calculator(QWidget):
    STANDARD_SIZE = QSize(640, 560)
    STANDARD_COMPACT_SIZE = QSize(400, 560)
    SCIENTIFIC_SIZE = QSize(780, 640)
    SCIENTIFIC_COMPACT_SIZE = QSize(540, 640)
    GRAPH_SIZE = QSize(1120, 720)
    ADVANCED_SIZE = QSize(1040, 680)

    def __init__(self):
        super().__init__()
        self.expression = ""
        self.result_ready = False
        self.history = CalculationHistory()
        self.history_visible = True
        self.scientific_mode = False
        self.graph_mode = False
        self.advanced_mode = False
        self.angle_mode = "DEG"
        self.resize_animation = None
        self.setWindowTitle("PyQt 计算器")
        self.setObjectName("CalculatorWindow")
        self.resize(self.STANDARD_SIZE)
        self.setMinimumSize(self.STANDARD_COMPACT_SIZE)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(self.window_style())
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        calculator_layout = QVBoxLayout()
        calculator_layout.setSpacing(12)

        top_bar = QHBoxLayout()
        self.menu_bar = self.create_menu_bar()

        self.history_button = QPushButton("隐藏历史")
        self.history_button.setFixedHeight(34)
        self.history_button.setStyleSheet(self.mode_button_style())
        self.history_button.clicked.connect(self.toggle_history_panel)

        top_bar.addWidget(self.menu_bar)
        top_bar.addStretch()
        top_bar.addWidget(self.history_button)
        calculator_layout.addLayout(top_bar)

        self.content_stack = QStackedLayout()
        calculator_page = QWidget()
        calculator_page_layout = QVBoxLayout()
        calculator_page_layout.setContentsMargins(0, 0, 0, 0)
        calculator_page_layout.setSpacing(12)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setText("0")
        self.display.setFont(QFont("Arial", 28))
        self.display.setFixedHeight(80)
        self.display.setStyleSheet(
            """
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 12px;
                padding: 10px;
                color: #222;
            }
            """
        )
        calculator_page_layout.addWidget(self.display)

        self.keyboard_stack = QStackedLayout()
        self.keyboard_stack.addWidget(self.create_keyboard(self.standard_buttons()))
        self.keyboard_stack.addWidget(self.create_keyboard(self.scientific_buttons(), button_height=50))

        calculator_page_layout.addLayout(self.keyboard_stack)
        calculator_page.setLayout(calculator_page_layout)

        self.graph_panel = GraphingPanel()
        self.advanced_panel = AdvancedMathPanel()
        self.content_stack.addWidget(calculator_page)
        self.content_stack.addWidget(self.graph_panel)
        self.content_stack.addWidget(self.advanced_panel)
        calculator_layout.addLayout(self.content_stack)
        main_layout.addLayout(calculator_layout)
        self.history_panel = self.create_history_panel()
        main_layout.addWidget(self.history_panel)
        self.setLayout(main_layout)

    def create_menu_bar(self):
        menu_bar = QMenuBar()
        menu_bar.setFixedHeight(34)
        menu_bar.setStyleSheet(self.menu_bar_style())

        mode_menu = menu_bar.addMenu("模式")
        self.mode_action_group = QActionGroup(self)
        self.mode_action_group.setExclusive(True)

        self.standard_action = QAction("标准", self, checkable=True)
        self.scientific_action = QAction("科学", self, checkable=True)
        self.graph_action = QAction("绘图", self, checkable=True)
        self.advanced_action = QAction("高等数学", self, checkable=True)
        self.standard_action.setChecked(True)

        self.standard_action.triggered.connect(self.set_standard_mode)
        self.scientific_action.triggered.connect(self.set_scientific_mode)
        self.graph_action.triggered.connect(self.set_graph_mode)
        self.advanced_action.triggered.connect(self.set_advanced_mode)

        for action in (
            self.standard_action,
            self.scientific_action,
            self.graph_action,
            self.advanced_action,
        ):
            self.mode_action_group.addAction(action)
            mode_menu.addAction(action)

        angle_menu = menu_bar.addMenu("角度")
        self.angle_action_group = QActionGroup(self)
        self.angle_action_group.setExclusive(True)
        self.deg_action = QAction("角度 DEG", self, checkable=True)
        self.rad_action = QAction("弧度 RAD", self, checkable=True)
        self.deg_action.setChecked(True)
        self.deg_action.triggered.connect(lambda: self.set_angle_mode("DEG"))
        self.rad_action.triggered.connect(lambda: self.set_angle_mode("RAD"))
        for action in (self.deg_action, self.rad_action):
            self.angle_action_group.addAction(action)
            angle_menu.addAction(action)

        return menu_bar

    @staticmethod
    def standard_buttons():
        return [
            ["C", "⌫", "(", ")"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "-"],
            ["±", "0", ".", "+"],
            ["%", "^", "=", ""],
        ]

    @staticmethod
    def scientific_buttons():
        return [
            ["C", "⌫", "(", ")", "π", "e"],
            ["sin", "cos", "tan", "log", "ln", "√"],
            ["asin", "acos", "atan", "x²", "x³", "x!"],
            ["7", "8", "9", "÷", "1/x", "^"],
            ["4", "5", "6", "×", "%", "abs"],
            ["1", "2", "3", "-", ".", "="],
            ["±", "0", "+", "", "", ""],
        ]

    def create_keyboard(self, buttons, button_height=60):
        keyboard = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        for row, button_row in enumerate(buttons):
            for col, text in enumerate(button_row):
                if not text:
                    continue

                button = QPushButton(text)
                button.setFont(QFont("Arial", 18))
                button.setFixedHeight(button_height)
                button.clicked.connect(lambda _checked, value=text: self.on_button_clicked(value))

                if text == "=":
                    button.setStyleSheet(self.equal_button_style())
                    grid_layout.addWidget(button, row, col)
                elif text in {"+", "-", "×", "÷", "^", "%"}:
                    button.setStyleSheet(self.operator_button_style())
                    grid_layout.addWidget(button, row, col)
                elif text in {
                    "C",
                    "⌫",
                    "(",
                    ")",
                    "±",
                    "sin",
                    "cos",
                    "tan",
                    "asin",
                    "acos",
                    "atan",
                    "log",
                    "ln",
                    "√",
                    "x²",
                    "x³",
                    "x!",
                    "1/x",
                    "abs",
                    "π",
                    "e",
                }:
                    button.setStyleSheet(self.function_button_style())
                    grid_layout.addWidget(button, row, col)
                else:
                    button.setStyleSheet(self.number_button_style())
                    grid_layout.addWidget(button, row, col)

        keyboard.setLayout(grid_layout)
        return keyboard

    def create_history_panel(self):
        panel = QWidget()
        panel.setFixedWidth(230)

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        title = QLabel("历史记录")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #f1f3f4;")

        clear_button = QPushButton("清空")
        clear_button.setFixedHeight(32)
        clear_button.setStyleSheet(self.history_clear_button_style())
        clear_button.clicked.connect(self.clear_history)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)

        self.history_empty_label = QLabel("暂无历史记录")
        self.history_empty_label.setAlignment(Qt.AlignCenter)
        self.history_empty_label.setStyleSheet("color: #aeb4bb; padding: 12px;")

        self.history_list = QListWidget()
        self.history_list.setStyleSheet(self.history_list_style())
        self.history_list.itemClicked.connect(self.use_history_item)

        panel_layout.addLayout(header_layout)
        panel_layout.addWidget(self.history_empty_label)
        panel_layout.addWidget(self.history_list)
        panel.setLayout(panel_layout)
        self.refresh_history()
        return panel

    def keyPressEvent(self, event):
        if self.graph_mode or self.advanced_mode:
            super().keyPressEvent(event)
            return

        key = event.key()
        text = event.text()

        if text and text in "0123456789.":
            self.on_button_clicked(text)
            return

        key_map = {
            "+": "+",
            "-": "-",
            "*": "×",
            "/": "÷",
            "%": "%",
            "^": "^",
            "(": "(",
            ")": ")",
            "=": "=",
        }
        if text and text in key_map:
            self.on_button_clicked(key_map[text])
            return

        if key in {Qt.Key_Return, Qt.Key_Enter}:
            self.on_button_clicked("=")
            return
        if key == Qt.Key_Backspace:
            self.on_button_clicked("⌫")
            return
        if key == Qt.Key_Escape or text.lower() == "c":
            self.on_button_clicked("C")
            return

        scientific_shortcuts = {
            "s": "sin",
            "o": "cos",
            "t": "tan",
            "l": "log",
            "n": "ln",
            "r": "√",
            "p": "π",
            "e": "e",
        }
        shortcut = scientific_shortcuts.get(text.lower())
        if self.scientific_mode and shortcut:
            self.on_button_clicked(shortcut)
            return

        super().keyPressEvent(event)

    def on_button_clicked(self, text):
        if text == "C":
            self.clear()
        elif text == "⌫":
            self.backspace()
        elif text == "=":
            self.calculate_result()
        elif text == "±":
            self.toggle_sign()
        elif text in {"sin", "cos", "tan", "asin", "acos", "atan", "log", "ln", "√", "abs"}:
            self.append_function(text)
        elif text in {"x²", "x³", "x!", "1/x"}:
            self.wrap_expression(text)
        elif text == "π":
            self.append_text("pi")
        else:
            self.append_text(text)

    def append_text(self, text):
        symbol_map = {
            "×": "*",
            "÷": "/",
            "^": "**",
        }
        actual_text = symbol_map.get(text, text)
        if self.result_ready and not self.is_continuing_operator(actual_text):
            self.expression = ""
        self.result_ready = False
        self.expression += actual_text
        self.update_display()

    def append_function(self, text):
        if self.result_ready:
            self.expression = ""
            self.result_ready = False

        function_map = {
            "√": "sqrt",
            "sin": "sin",
            "cos": "cos",
            "tan": "tan",
            "asin": "asin",
            "acos": "acos",
            "atan": "atan",
            "log": "log",
            "ln": "ln",
            "abs": "abs",
        }
        function_name = function_map[text]
        if text in {"sin", "cos", "tan"} and self.angle_mode == "DEG":
            self.expression += f"{function_name}(pi/180*"
        elif text in {"asin", "acos", "atan"} and self.angle_mode == "DEG":
            self.expression += f"180/pi*{function_name}("
        else:
            self.expression += f"{function_name}("
        self.update_display()

    def wrap_expression(self, text):
        if not self.expression:
            return

        self.result_ready = False
        if text == "x²":
            self.expression = f"({self.expression})**2"
        elif text == "x³":
            self.expression = f"({self.expression})**3"
        elif text == "x!":
            self.expression = f"fact({self.expression})"
        elif text == "1/x":
            self.expression = f"reciprocal({self.expression})"
        self.update_display()

    def clear(self):
        self.expression = ""
        self.result_ready = False
        self.display.setText("0")

    def backspace(self):
        if self.result_ready:
            self.clear()
            return

        self.expression = self.expression[:-1]
        self.update_display()

    def toggle_sign(self):
        self.result_ready = False
        if not self.expression:
            self.expression = "-"
        else:
            self.expression = f"-({self.expression})"
        self.update_display()

    def calculate_result(self):
        if not self.expression:
            return

        try:
            expression = self.expression
            expression_text = self.format_expression(expression)
            result = SafeCalculator.calculate(self.expression)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression = str(result)
            self.display.setText(str(result))
            self.history.add(expression_text, result)
            self.refresh_history()
            self.result_ready = True
        except Exception as exc:
            self.expression = ""
            self.result_ready = False
            self.display.setText(str(exc))

    def clear_history(self):
        self.history.clear()
        self.refresh_history()

    def refresh_history(self):
        self.history_list.clear()
        items = self.history.items()
        self.history_empty_label.setVisible(not items)
        self.history_list.setVisible(bool(items))

        for history_item in items:
            item = QListWidgetItem(f"{history_item.expression} =\n{history_item.result}")
            item.setData(Qt.UserRole, history_item.result)
            item.setTextAlignment(Qt.AlignRight)
            self.history_list.addItem(item)

    def use_history_item(self, item):
        self.expression = item.data(Qt.UserRole)
        self.result_ready = True
        self.update_display()

    def toggle_scientific_mode(self):
        if self.scientific_mode:
            self.set_standard_mode()
        else:
            self.set_scientific_mode()

    def set_standard_mode(self):
        self.graph_mode = False
        self.advanced_mode = False
        self.scientific_mode = False
        self.content_stack.setCurrentIndex(0)
        self.keyboard_stack.setCurrentIndex(0)
        self.standard_action.setChecked(True)
        self.restore_history_for_calculator_mode()
        self.animate_to_layout_size()

    def set_scientific_mode(self):
        self.graph_mode = False
        self.advanced_mode = False
        self.scientific_mode = True
        self.content_stack.setCurrentIndex(0)
        self.keyboard_stack.setCurrentIndex(1)
        self.scientific_action.setChecked(True)
        self.restore_history_for_calculator_mode()
        self.animate_to_layout_size()

    def set_graph_mode(self):
        self.graph_mode = True
        self.advanced_mode = False
        self.content_stack.setCurrentIndex(1)
        self.graph_action.setChecked(True)
        self.history_panel.setVisible(False)
        self.history_button.setVisible(False)
        self.animate_to_layout_size()

    def set_advanced_mode(self):
        self.graph_mode = False
        self.advanced_mode = True
        self.content_stack.setCurrentIndex(2)
        self.advanced_action.setChecked(True)
        self.history_panel.setVisible(False)
        self.history_button.setVisible(False)
        self.animate_to_layout_size()

    def update_calculator_mode(self):
        self.keyboard_stack.setCurrentIndex(1 if self.scientific_mode else 0)
        self.animate_to_layout_size()

    def toggle_history_panel(self):
        if self.graph_mode or self.advanced_mode:
            return
        self.history_visible = not self.history_visible
        self.history_button.setText("隐藏历史" if self.history_visible else "显示历史")
        if self.history_visible:
            self.history_panel.setVisible(True)
        self.animate_to_layout_size(hide_history_after=not self.history_visible)

    def restore_history_for_calculator_mode(self):
        self.history_button.setVisible(True)
        self.history_button.setText("隐藏历史" if self.history_visible else "显示历史")
        self.history_panel.setVisible(self.history_visible)

    def toggle_graph_mode(self):
        if self.graph_mode:
            self.set_standard_mode()
        else:
            self.set_graph_mode()

    def toggle_angle_mode(self):
        self.set_angle_mode("RAD" if self.angle_mode == "DEG" else "DEG")

    def set_angle_mode(self, mode):
        self.angle_mode = mode
        self.deg_action.setChecked(mode == "DEG")
        self.rad_action.setChecked(mode == "RAD")

    def target_size(self):
        if self.advanced_mode:
            return self.ADVANCED_SIZE
        if self.graph_mode:
            return self.GRAPH_SIZE
        if self.scientific_mode and self.history_visible:
            return self.SCIENTIFIC_SIZE
        if self.scientific_mode:
            return self.SCIENTIFIC_COMPACT_SIZE
        if self.history_visible:
            return self.STANDARD_SIZE
        return self.STANDARD_COMPACT_SIZE

    def minimum_size_for_current_mode(self):
        if self.advanced_mode:
            return QSize(760, 520)
        if self.graph_mode:
            return QSize(760, 520)
        if self.scientific_mode:
            return QSize(540, 640)
        if self.history_visible:
            return QSize(640, 560)
        return QSize(400, 560)

    def animate_to_layout_size(self, hide_history_after=False):
        target = self.target_size()
        start = self.size()
        if start == target:
            if hide_history_after:
                self.history_panel.setVisible(False)
            self.setMinimumSize(self.minimum_size_for_current_mode())
            self.setMaximumSize(16777215, 16777215)
            return

        if self.resize_animation:
            self.resize_animation.stop()

        min_width = min(start.width(), target.width())
        min_height = min(start.height(), target.height())
        max_width = max(start.width(), target.width())
        max_height = max(start.height(), target.height())
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)

        self.resize_animation = QPropertyAnimation(self, b"size")
        self.resize_animation.setDuration(220)
        self.resize_animation.setStartValue(start)
        self.resize_animation.setEndValue(target)
        self.resize_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.resize_animation.finished.connect(
            lambda: self.finish_resize_animation(target, hide_history_after)
        )
        self.resize_animation.start()

    def finish_resize_animation(self, target, hide_history_after):
        if hide_history_after:
            self.history_panel.setVisible(False)
        self.resize(target)
        self.setMinimumSize(self.minimum_size_for_current_mode())
        self.setMaximumSize(16777215, 16777215)

    def update_display(self):
        if not self.expression:
            self.display.setText("0")
            return

        self.display.setText(self.format_expression(self.expression))

    @staticmethod
    def is_continuing_operator(text):
        return text in {"+", "-", "*", "/", "**", "%"}

    @staticmethod
    def format_expression(expression):
        display_text = expression
        display_text = display_text.replace("**", "^")
        display_text = display_text.replace("*", "×")
        display_text = display_text.replace("/", "÷")
        display_text = display_text.replace("pi", "π")
        display_text = display_text.replace("sqrt", "√")
        display_text = display_text.replace("fact", "!")
        display_text = display_text.replace("reciprocal", "1/")
        return display_text

    @staticmethod
    def number_button_style():
        return """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 12px;
                color: #222;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """

    @staticmethod
    def operator_button_style():
        return """
            QPushButton {
                background-color: #e8f0fe;
                border: 1px solid #b8cdf8;
                border-radius: 12px;
                color: #1a5fd0;
            }
            QPushButton:hover {
                background-color: #d9e8ff;
            }
            QPushButton:pressed {
                background-color: #c8dcff;
            }
        """

    @staticmethod
    def function_button_style():
        return """
            QPushButton {
                background-color: #f7f7f7;
                border: 1px solid #d0d0d0;
                border-radius: 12px;
                color: #444;
            }
            QPushButton:hover {
                background-color: #ededed;
            }
            QPushButton:pressed {
                background-color: #dddddd;
            }
        """

    @staticmethod
    def equal_button_style():
        return """
            QPushButton {
                background-color: #1a73e8;
                border: 1px solid #1a73e8;
                border-radius: 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1669d6;
            }
            QPushButton:pressed {
                background-color: #125ab8;
            }
        """

    @staticmethod
    def history_clear_button_style():
        return """
            QPushButton {
                background-color: #f7f7f7;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                color: #444;
                padding: 0 10px;
            }
            QPushButton:hover {
                background-color: #ededed;
            }
            QPushButton:pressed {
                background-color: #dddddd;
            }
        """

    @staticmethod
    def history_list_style():
        return """
            QListWidget {
                background-color: #1f2328;
                border: 1px solid #5f6368;
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item {
                border-bottom: 1px solid #3c4043;
                padding: 10px 8px;
                color: #f1f3f4;
            }
            QListWidget::item:hover {
                background-color: #26364f;
            }
            QListWidget::item:selected {
                background-color: #174ea6;
                color: #ffffff;
            }
        """

    @staticmethod
    def mode_button_style():
        return """
            QPushButton {
                background-color: #f8fafd;
                border: 1px solid #c8cdd3;
                border-radius: 8px;
                color: #222;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #f2f2f2;
            }
            QPushButton:pressed {
                background-color: #e4e4e4;
            }
        """

    @staticmethod
    def menu_bar_style():
        return """
            QMenuBar {
                background-color: #2b2f33;
                border: 1px solid #5f6368;
                border-radius: 8px;
                color: #f1f3f4;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                border-radius: 6px;
                padding: 5px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3c4043;
            }
            QMenu {
                background-color: #2b2f33;
                border: 1px solid #5f6368;
                color: #f1f3f4;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 28px 6px 18px;
            }
            QMenu::item:selected {
                background-color: #174ea6;
            }
            QMenu::indicator:checked {
                background-color: #8ab4f8;
                border-radius: 5px;
            }
        """

    @staticmethod
    def window_style():
        return """
            Calculator {
                background-color: #202124;
            }
            #CalculatorWindow {
                background-color: #202124;
            }
            QWidget {
                color: #f1f3f4;
            }
            QLabel {
                color: #f1f3f4;
            }
        """

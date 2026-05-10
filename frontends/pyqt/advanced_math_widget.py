import html

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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from backend.advanced_math_core import AdvancedMathEngine
from frontends.pyqt.formula_formatter import FormulaFormatter


class AdvancedMathPanel(QWidget):
    OPERATIONS = [
        "求导",
        "偏导",
        "高阶导数",
        "不定积分",
        "定积分",
        "极限",
        "左极限",
        "右极限",
        "泰勒展开",
        "方程求解",
        "化简",
    ]

    def __init__(self):
        super().__init__()
        self.history = []
        self.setStyleSheet(self.panel_style())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        header = QLabel("高等数学")
        header.setObjectName("Header")

        input_grid = QGridLayout()
        input_grid.setHorizontalSpacing(10)
        input_grid.setVerticalSpacing(8)

        self.operation_box = QComboBox()
        self.operation_box.addItems(self.OPERATIONS)
        self.operation_box.setMinimumWidth(130)
        self.operation_box.view().setMinimumWidth(150)

        self.expression_input = QLineEdit()
        self.expression_input.setPlaceholderText("输入表达式或方程，例如 sin(x)/x、x^3-2*x+1、x^2=4")
        self.expression_input.returnPressed.connect(self.calculate)
        self.expression_input.textChanged.connect(self.update_formula_preview)

        self.variable_input = QLineEdit("x")
        self.order_input = QLineEdit("2")
        self.point_input = QLineEdit("0")
        self.lower_input = QLineEdit("0")
        self.upper_input = QLineEdit("1")

        input_grid.addWidget(QLabel("运算"), 0, 0)
        input_grid.addWidget(self.operation_box, 0, 1)
        input_grid.addWidget(QLabel("表达式"), 0, 2)
        input_grid.addWidget(self.expression_input, 0, 3, 1, 5)

        input_grid.addWidget(QLabel("变量"), 1, 0)
        input_grid.addWidget(self.variable_input, 1, 1)
        input_grid.addWidget(QLabel("阶数"), 1, 2)
        input_grid.addWidget(self.order_input, 1, 3)
        input_grid.addWidget(QLabel("趋近/展开点"), 1, 4)
        input_grid.addWidget(self.point_input, 1, 5)
        input_grid.addWidget(QLabel("下限"), 1, 6)
        input_grid.addWidget(self.lower_input, 1, 7)
        input_grid.addWidget(QLabel("上限"), 1, 8)
        input_grid.addWidget(self.upper_input, 1, 9)

        self.formula_preview = QLabel("")
        self.formula_preview.setObjectName("FormulaPreview")
        self.formula_preview.setTextFormat(Qt.RichText)
        self.formula_preview.setMinimumHeight(64)

        action_row = QHBoxLayout()
        calculate_button = QPushButton("计算")
        calculate_button.clicked.connect(self.calculate)
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear)
        action_row.addWidget(calculate_button)
        action_row.addWidget(clear_button)
        action_row.addStretch()

        examples = QLabel(
            "示例：limit sin(x)/x, x->0 输入表达式 sin(x)/x，运算选“极限”；"
            "定积分输入 x^2，下限 0，上限 1。"
        )
        examples.setWordWrap(True)
        examples.setObjectName("Hint")

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setPlaceholderText("结果会显示在这里，包括精确形式、近似值和简明步骤。")

        content_row = QHBoxLayout()
        result_column = QVBoxLayout()
        result_column.addWidget(self.result_view, 1)

        history_column = QVBoxLayout()
        history_title_row = QHBoxLayout()
        history_title = QLabel("历史记录")
        history_title.setObjectName("SubHeader")
        clear_history_button = QPushButton("清空")
        clear_history_button.clicked.connect(self.clear_history)
        history_title_row.addWidget(history_title)
        history_title_row.addStretch()
        history_title_row.addWidget(clear_history_button)

        self.history_list = QListWidget()
        self.history_list.setFixedWidth(260)
        self.history_list.itemClicked.connect(self.restore_history_item)
        history_column.addLayout(history_title_row)
        history_column.addWidget(self.history_list, 1)

        content_row.addLayout(result_column, 1)
        content_row.addLayout(history_column)

        layout.addWidget(header)
        layout.addLayout(input_grid)
        layout.addWidget(self.formula_preview)
        layout.addLayout(action_row)
        layout.addWidget(examples)
        layout.addLayout(content_row, 1)
        self.setLayout(layout)

    def update_formula_preview(self):
        text = self.expression_input.text().strip()
        if not text:
            self.formula_preview.setText("")
            return
        self.formula_preview.setText(FormulaFormatter.html_formula(text))

    def calculate(self):
        try:
            result = AdvancedMathEngine.calculate(
                self.operation_box.currentText(),
                self.expression_input.text(),
                variable=self.variable_input.text(),
                order=self.order_input.text(),
                point=self.point_input.text(),
                lower=self.lower_input.text(),
                upper=self.upper_input.text(),
            )
        except Exception as exc:
            self.result_view.setHtml(self.error_html(str(exc)))
            return

        steps = "\n".join(f"{index}. {step}" for index, step in enumerate(result["steps"], 1))
        result_html = self.result_html(result, steps)
        self.result_view.setHtml(result_html)
        self.add_history(result, result_html)

    def add_history(self, result, result_html):
        entry = {
            "operation": self.operation_box.currentText(),
            "expression": self.expression_input.text(),
            "variable": self.variable_input.text(),
            "order": self.order_input.text(),
            "point": self.point_input.text(),
            "lower": self.lower_input.text(),
            "upper": self.upper_input.text(),
            "html": result_html,
        }
        self.history.insert(0, entry)
        self.history = self.history[:30]
        self.refresh_history()

    def refresh_history(self):
        self.history_list.clear()
        for entry in self.history:
            item = QListWidgetItem(
                f"{entry['operation']}\n{FormulaFormatter.pretty_expression(entry['expression'])}"
            )
            item.setData(Qt.UserRole, entry)
            self.history_list.addItem(item)

    def restore_history_item(self, item):
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        self.operation_box.setCurrentText(entry["operation"])
        self.expression_input.setText(entry["expression"])
        self.variable_input.setText(entry["variable"])
        self.order_input.setText(entry["order"])
        self.point_input.setText(entry["point"])
        self.lower_input.setText(entry["lower"])
        self.upper_input.setText(entry["upper"])
        self.result_view.setHtml(entry["html"])

    def clear_history(self):
        self.history.clear()
        self.history_list.clear()

    def result_html(self, result, steps):
        return self.html_document(
            "".join(
                [
                    f"<div class='meta'>运算：{html.escape(result['operation'])}</div>",
                    FormulaFormatter.html_block("精确结果", result["exact"]),
                    FormulaFormatter.html_block("公式显示", result["pretty"]),
                    FormulaFormatter.html_block("近似值", result["numeric"]),
                    FormulaFormatter.html_block("步骤", steps or "1. 直接计算表达式。"),
                ]
            )
        )

    def error_html(self, message):
        return self.html_document(f"<div class='error'>错误：{html.escape(message)}</div>")

    @staticmethod
    def html_document(body):
        return (
            "<html><head><style>"
            "body { background: #1f2328; color: #f1f3f4; font-family: -apple-system, Arial; }"
            ".meta { color: #aeb4bb; font-weight: 700; margin-bottom: 12px; }"
            ".section-title { color: #8ab4f8; font-weight: 700; margin-top: 14px; }"
            "pre { background: #171a1f; border: 1px solid #3c4043; border-radius: 6px; "
            "padding: 10px; color: #f1f3f4; font-family: Menlo, Consolas, monospace; "
            "font-size: 15px; white-space: pre-wrap; }"
            ".error { color: #ffb4ab; font-weight: 700; }"
            "</style></head><body>"
            f"{body}"
            "</body></html>"
        )

    def clear(self):
        self.expression_input.clear()
        self.result_view.clear()

    @staticmethod
    def panel_style():
        return """
            AdvancedMathPanel {
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
            QLabel#Hint {
                color: #aab2bd;
                font-weight: 400;
            }
            QLabel#FormulaPreview {
                background-color: #111419;
                border: 1px solid #303640;
                border-radius: 8px;
                color: #dce8ff;
                padding: 12px;
                font-family: Menlo, Consolas, monospace;
                font-size: 15px;
                font-weight: 400;
            }
            QLineEdit, QComboBox, QTextEdit {
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
            QLineEdit {
                min-height: 24px;
            }
            QPushButton {
                background-color: #343940;
                border: 1px solid #5c6572;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 9px 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #40464f;
                border-color: #7b8592;
            }
            QPushButton:pressed {
                background-color: #252a31;
            }
            QListWidget {
                background-color: #191d23;
                border: 1px solid #303640;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 8px;
            }
            QListWidget::item {
                background-color: #1e2228;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 10px;
                margin: 3px;
            }
            QListWidget::item:selected {
                background-color: #203a5e;
                border-color: #75a7ea;
                color: #ffffff;
            }
        """

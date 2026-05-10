import math

from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from calculator_core import SafeCalculator
from formula_formatter import FormulaFormatter


class PlotCanvas(QWidget):
    COLORS = [
        QColor("#1a73e8"),
        QColor("#d93025"),
        QColor("#188038"),
        QColor("#9334e6"),
        QColor("#f29900"),
        QColor("#00acc1"),
    ]

    def __init__(self):
        super().__init__()
        self.functions = []
        self.scale = 42.0
        self.origin = QPoint(300, 220)
        self.drag_start = None
        self.origin_start = QPoint(self.origin)
        self.hover = None
        self.setMouseTracking(True)
        self.setMinimumHeight(390)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #9aa0a6;")

    def set_functions(self, functions):
        self.functions = functions
        self.update()

    def reset_view(self):
        self.scale = 42.0
        self.origin = QPoint(self.width() // 2, self.height() // 2)
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#ffffff"))
        self.draw_grid(painter)
        self.draw_functions(painter)
        self.draw_hover(painter)

    def draw_grid(self, painter):
        minor_pen = QPen(QColor("#eeeeee"), 1)
        axis_pen = QPen(QColor("#8a8a8a"), 1.5)
        label_pen = QPen(QColor("#666666"), 1)

        step = self.grid_step()
        start_x = math.floor(self.screen_to_math_x(0) / step) * step
        end_x = self.screen_to_math_x(self.width())
        value = start_x
        painter.setFont(QFont("Arial", 9))

        while value <= end_x:
            screen_x = int(round(self.math_to_screen_x(value)))
            painter.setPen(axis_pen if abs(value) < 1e-9 else minor_pen)
            painter.drawLine(screen_x, 0, screen_x, self.height())
            if abs(value) > 1e-9:
                painter.setPen(label_pen)
                painter.drawText(screen_x + 3, self.origin.y() + 14, self.format_number(value))
            value += step

        start_y = math.floor(self.screen_to_math_y(self.height()) / step) * step
        end_y = self.screen_to_math_y(0)
        value = start_y
        while value <= end_y:
            screen_y = int(round(self.math_to_screen_y(value)))
            painter.setPen(axis_pen if abs(value) < 1e-9 else minor_pen)
            painter.drawLine(0, screen_y, self.width(), screen_y)
            if abs(value) > 1e-9:
                painter.setPen(label_pen)
                painter.drawText(self.origin.x() + 4, screen_y - 3, self.format_number(value))
            value += step

    def draw_functions(self, painter):
        for index, item in enumerate(self.functions):
            if not item.get("visible", True):
                continue

            color = self.COLORS[index % len(self.COLORS)]
            pen = QPen(color, 2.2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            path = QPainterPath()
            has_point = False
            previous_y = None
            screen_x = 0.0
            sample_step = 0.5

            while screen_x <= self.width():
                x = self.screen_to_math_x(screen_x)
                try:
                    y = SafeCalculator.calculate(item["expression"], {"x": x})
                except Exception:
                    has_point = False
                    previous_y = None
                    screen_x += sample_step
                    continue

                if not isinstance(y, (int, float)) or not math.isfinite(y):
                    has_point = False
                    previous_y = None
                    screen_x += sample_step
                    continue

                screen_y = self.math_to_screen_y(y)
                if previous_y is not None and abs(screen_y - previous_y) > self.height() * 1.4:
                    has_point = False

                if not has_point:
                    path.moveTo(screen_x, screen_y)
                    has_point = True
                else:
                    path.lineTo(screen_x, screen_y)
                previous_y = screen_y
                screen_x += sample_step

            painter.drawPath(path)

    def draw_hover(self, painter):
        if not self.hover:
            return

        screen_x, screen_y, x, y, expression, color = self.hover
        painter.setPen(QPen(color, 1.5))
        painter.drawLine(screen_x, 0, screen_x, self.height())
        painter.drawLine(0, screen_y, self.width(), screen_y)
        painter.setBrush(color)
        painter.drawEllipse(QPointF(screen_x, screen_y), 5, 5)

        text = f"{expression}: ({self.format_number(x)}, {self.format_number(y)})"
        painter.setFont(QFont("Arial", 10))
        metrics = painter.fontMetrics()
        box_width = metrics.horizontalAdvance(text) + 16
        box_height = 28
        box_x = min(screen_x + 12, self.width() - box_width - 8)
        box_y = max(8, screen_y - box_height - 10)
        painter.fillRect(box_x, box_y, box_width, box_height, QColor("#ffffff"))
        painter.setPen(QPen(QColor("#c8c8c8"), 1))
        painter.drawRect(box_x, box_y, box_width, box_height)
        painter.setPen(QPen(QColor("#222222"), 1))
        painter.drawText(box_x + 8, box_y + 19, text)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        cursor = event.pos()
        math_x = self.screen_to_math_x(cursor.x())
        math_y = self.screen_to_math_y(cursor.y())
        self.scale = max(10.0, min(240.0, self.scale * factor))
        self.origin = QPoint(
            int(cursor.x() - math_x * self.scale),
            int(cursor.y() + math_y * self.scale),
        )
        self.update_hover(cursor)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.pos()
            self.origin_start = QPoint(self.origin)

    def mouseMoveEvent(self, event):
        if self.drag_start:
            delta = event.pos() - self.drag_start
            self.origin = self.origin_start + delta
        self.update_hover(event.pos())
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = None

    def leaveEvent(self, _event):
        self.hover = None
        self.update()

    def update_hover(self, pos):
        nearest = None
        x = self.screen_to_math_x(pos.x())
        for index, item in enumerate(self.functions):
            if not item.get("visible", True):
                continue
            try:
                y = SafeCalculator.calculate(item["expression"], {"x": x})
            except Exception:
                continue
            if not isinstance(y, (int, float)) or not math.isfinite(y):
                continue

            screen_y = self.math_to_screen_y(y)
            distance = abs(screen_y - pos.y())
            if distance <= 18 and (nearest is None or distance < nearest[0]):
                nearest = (
                    distance,
                    pos.x(),
                    int(screen_y),
                    x,
                    y,
                    item["label"],
                    self.COLORS[index % len(self.COLORS)],
                )
        self.hover = nearest[1:] if nearest else None

    def grid_step(self):
        target_pixels = 70
        raw = target_pixels / self.scale
        power = 10 ** math.floor(math.log10(raw))
        for multiplier in (1, 2, 5, 10):
            step = multiplier * power
            if step * self.scale >= target_pixels:
                return step
        return 10 * power

    def math_to_screen_x(self, value):
        return self.origin.x() + value * self.scale

    def math_to_screen_y(self, value):
        return self.origin.y() - value * self.scale

    def screen_to_math_x(self, value):
        return (value - self.origin.x()) / self.scale

    def screen_to_math_y(self, value):
        return (self.origin.y() - value) / self.scale

    @staticmethod
    def format_number(value):
        if abs(value) >= 10000 or (0 < abs(value) < 0.001):
            return f"{value:.2e}"
        return f"{value:.4g}"


class GraphingPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.functions = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.setStyleSheet(self.panel_style())

        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        input_label = QLabel("y =")
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("输入函数，例如 sin(x)、x^2、log(x)、2*x")
        self.function_input.setFixedHeight(38)
        self.function_input.returnPressed.connect(self.add_function)
        self.function_input.textChanged.connect(self.update_formula_preview)

        add_button = QPushButton("添加")
        add_button.setFixedHeight(38)
        add_button.clicked.connect(self.add_function)

        reset_top_button = QPushButton("重置视图")
        reset_top_button.setFixedHeight(38)
        reset_top_button.clicked.connect(self.canvas_reset)

        input_row.addWidget(input_label)
        input_row.addWidget(self.function_input, 1)
        input_row.addWidget(add_button)
        input_row.addWidget(reset_top_button)

        self.formula_preview = QLabel("")
        self.formula_preview.setObjectName("FormulaPreview")
        self.formula_preview.setTextFormat(Qt.RichText)
        self.formula_preview.setMinimumHeight(58)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(8)

        title = QLabel("函数")
        title.setFont(QFont("Arial", 16, QFont.Bold))

        self.error_label = QLabel("")
        self.error_label.setFixedHeight(18)
        self.error_label.setStyleSheet("color: #ffb4ab;")

        self.function_list = QListWidget()
        self.function_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.function_list.setStyleSheet(self.function_list_style())
        self.function_list.itemChanged.connect(self.update_function_visibility)

        remove_button = QPushButton("删除选中")
        remove_button.setFixedHeight(34)
        remove_button.clicked.connect(self.remove_selected)
        clear_button = QPushButton("清空函数")
        clear_button.setFixedHeight(34)
        clear_button.clicked.connect(self.clear_functions)

        self.canvas = PlotCanvas()

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(self.error_label)
        sidebar_layout.addWidget(self.function_list, 1)
        sidebar_layout.addWidget(remove_button)
        sidebar_layout.addWidget(clear_button)
        sidebar.setLayout(sidebar_layout)

        body_layout.addWidget(sidebar)
        body_layout.addWidget(self.canvas, 1)

        layout.addLayout(input_row)
        layout.addWidget(self.formula_preview)
        layout.addLayout(body_layout, 1)
        self.setLayout(layout)

    def add_function(self):
        raw_expression = self.function_input.text().strip()
        if not raw_expression:
            return

        expression = self.normalize_expression(raw_expression)
        try:
            SafeCalculator.calculate(expression, {"x": 1.0})
        except Exception as exc:
            self.error_label.setText(str(exc))
            return

        label = self.format_label(raw_expression)
        formatted_label = self.format_formula_label(raw_expression)
        self.functions.append(
            {
                "expression": expression,
                "label": label,
                "display": formatted_label,
                "visible": True,
            }
        )
        self.refresh_function_list()
        self.function_input.clear()
        self.error_label.setText("")
        self.canvas.set_functions(self.functions)

    def remove_selected(self):
        row = self.function_list.currentRow()
        if row < 0:
            return
        del self.functions[row]
        self.refresh_function_list()
        self.canvas.set_functions(self.functions)

    def clear_functions(self):
        self.functions.clear()
        self.refresh_function_list()
        self.canvas.set_functions(self.functions)

    def canvas_reset(self):
        self.canvas.reset_view()

    def update_formula_preview(self):
        text = self.function_input.text().strip()
        if not text:
            self.formula_preview.setText("")
            return
        self.formula_preview.setText(
            f"<span class='formula-prefix'>y =</span>{FormulaFormatter.html_formula(text)}"
        )

    def refresh_function_list(self):
        self.function_list.blockSignals(True)
        self.function_list.clear()
        for index, item in enumerate(self.functions):
            list_item = QListWidgetItem(item.get("display", item["label"]))
            color = PlotCanvas.COLORS[index % len(PlotCanvas.COLORS)]
            list_item.setIcon(self.color_icon(color))
            list_item.setFlags(
                list_item.flags()
                | Qt.ItemIsUserCheckable
                | Qt.ItemIsEnabled
                | Qt.ItemIsSelectable
            )
            list_item.setCheckState(Qt.Checked if item.get("visible", True) else Qt.Unchecked)
            self.function_list.addItem(list_item)
        self.function_list.blockSignals(False)

    def update_function_visibility(self, item):
        row = self.function_list.row(item)
        if row < 0:
            return
        self.functions[row]["visible"] = item.checkState() == Qt.Checked
        self.canvas.set_functions(self.functions)

    @staticmethod
    def color_icon(color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(color)
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawRoundedRect(2, 2, 12, 12, 3, 3)
        painter.end()
        return QIcon(pixmap)

    @staticmethod
    def normalize_expression(expression):
        expression = expression.strip()
        if expression.startswith("y="):
            expression = expression[2:].strip()
        elif expression.startswith("y ="):
            expression = expression.split("=", 1)[1].strip()
        return expression.replace("^", "**").replace("π", "pi")

    @staticmethod
    def format_label(expression):
        expression = expression.strip()
        if expression.startswith("y"):
            return expression
        return f"y = {expression}"

    @staticmethod
    def format_formula_label(expression):
        expression = expression.strip()
        if expression.startswith("y"):
            return FormulaFormatter.pretty_expression(expression)
        pretty = FormulaFormatter.pretty_expression(expression)
        return f"y = {pretty}"

    @staticmethod
    def function_list_style():
        return """
            QListWidget {
                background-color: #1f2328;
                border: 1px solid #5f6368;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px 6px;
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
    def panel_style():
        return """
            GraphingPanel {
                background-color: #202124;
            }
            QLabel {
                color: #f1f3f4;
                font-weight: 600;
            }
            QLabel#FormulaPreview {
                background-color: #171a1f;
                border: 1px solid #3c4043;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 8px 10px;
                font-family: Menlo, Consolas, monospace;
                font-size: 15px;
                font-weight: 400;
            }
            QLineEdit {
                background-color: #1f2328;
                border: 1px solid #5f6368;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 0 10px;
                selection-background-color: #174ea6;
            }
            QLineEdit::placeholder {
                color: #aeb4bb;
            }
            QPushButton {
                background-color: #3c4043;
                border: 1px solid #6f757d;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #4b5055;
            }
            QPushButton:pressed {
                background-color: #303438;
            }
        """

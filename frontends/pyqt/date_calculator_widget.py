from datetime import date

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QCheckBox, QDateEdit, QGridLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from backend.date_core import DateCalculator
from backend.persistence import get_store


class DateCalculatorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.panel_style())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        header = QLabel("日期计算")
        header.setObjectName("Header")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        for editor in (self.start_date, self.end_date):
            editor.setCalendarPopup(True)
            editor.setDisplayFormat("yyyy-MM-dd")
            editor.setDate(QDate.currentDate())

        self.include_end = QCheckBox("包含结束日期")
        diff_button = QPushButton("计算相差天数")
        diff_button.clicked.connect(self.calculate_difference)

        self.days_input = QLineEdit("30")
        self.weekdays_only = QCheckBox("只计算工作日")
        add_button = QPushButton("加减天数")
        add_button.clicked.connect(self.calculate_add_days)

        grid.addWidget(QLabel("开始日期"), 0, 0)
        grid.addWidget(self.start_date, 0, 1)
        grid.addWidget(QLabel("结束日期"), 0, 2)
        grid.addWidget(self.end_date, 0, 3)
        grid.addWidget(self.include_end, 1, 1)
        grid.addWidget(diff_button, 1, 3)
        grid.addWidget(QLabel("天数"), 2, 0)
        grid.addWidget(self.days_input, 2, 1)
        grid.addWidget(self.weekdays_only, 2, 2)
        grid.addWidget(add_button, 2, 3)

        self.result_label = QLabel("")
        self.result_label.setObjectName("Result")

        layout.addWidget(header)
        layout.addLayout(grid)
        layout.addWidget(self.result_label)
        layout.addStretch()
        self.setLayout(layout)
        self.calculate_difference()

    def selected_start(self):
        return self.start_date.date().toString("yyyy-MM-dd")

    def selected_end(self):
        return self.end_date.date().toString("yyyy-MM-dd")

    def calculate_difference(self):
        result = DateCalculator.difference(
            self.selected_start(),
            self.selected_end(),
            self.include_end.isChecked(),
        )
        text = (
            f"{result['start']} 到 {result['end']}\n"
            f"相差 {result['days']} 天\n"
            f"约 {result['weeks']:.2f} 周"
        )
        self.result_label.setText(text)
        get_store().add_history("date", "日期差", text)

    def calculate_add_days(self):
        result = DateCalculator.add_days(
            self.selected_start(),
            int(self.days_input.text() or "0"),
            self.weekdays_only.isChecked(),
        )
        text = f"{result['start']} 加 {result['days']} 天\n= {result['result']}"
        self.result_label.setText(text)
        get_store().add_history("date", "加减天数", text)

    @staticmethod
    def panel_style():
        return """
            DateCalculatorPanel {
                background-color: #1e2228;
                border: 1px solid #303640;
                border-radius: 8px;
            }
            QLabel, QCheckBox { color: #f4f6f8; font-weight: 600; }
            QLabel#Header { font-size: 28px; font-weight: 800; }
            QLabel#Result {
                background-color: #111419;
                border: 1px solid #303640;
                border-radius: 8px;
                color: #f4f6f8;
                font-size: 24px;
                font-weight: 800;
                padding: 18px;
            }
            QLineEdit, QDateEdit {
                background-color: #191d23;
                border: 1px solid #5c6572;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 9px 10px;
                selection-background-color: #155fbf;
            }
            QPushButton {
                background-color: #343940;
                border: 1px solid #5c6572;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 9px 16px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #40464f; border-color: #7b8592; }
        """

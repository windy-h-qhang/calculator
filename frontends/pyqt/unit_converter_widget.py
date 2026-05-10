from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from backend.persistence import get_store
from backend.unit_converter import UnitConverter


class UnitConverterPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.panel_style())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        header = QLabel("单位换算")
        header.setObjectName("Header")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.category_box = QComboBox()
        self.category_box.addItems(UnitConverter.categories())
        self.category_box.currentTextChanged.connect(self.refresh_units)

        self.value_input = QLineEdit("1")
        self.value_input.setAlignment(Qt.AlignRight)
        self.value_input.textChanged.connect(self.convert)
        self.value_input.returnPressed.connect(lambda: self.convert(add_history=True))

        self.from_unit = QComboBox()
        self.to_unit = QComboBox()
        self.from_unit.currentTextChanged.connect(self.convert)
        self.to_unit.currentTextChanged.connect(self.convert)

        swap_button = QPushButton("交换")
        swap_button.clicked.connect(self.swap_units)

        grid.addWidget(QLabel("类型"), 0, 0)
        grid.addWidget(self.category_box, 0, 1)
        grid.addWidget(QLabel("数值"), 1, 0)
        grid.addWidget(self.value_input, 1, 1)
        grid.addWidget(QLabel("从"), 2, 0)
        grid.addWidget(self.from_unit, 2, 1)
        grid.addWidget(QLabel("到"), 3, 0)
        grid.addWidget(self.to_unit, 3, 1)
        grid.addWidget(swap_button, 4, 1)

        self.result_label = QLabel("")
        self.result_label.setObjectName("Result")

        layout.addWidget(header)
        layout.addLayout(grid)
        layout.addWidget(self.result_label)
        layout.addStretch()
        self.setLayout(layout)
        self.refresh_units()

    def refresh_units(self):
        units = UnitConverter.units(self.category_box.currentText())
        for combo in (self.from_unit, self.to_unit):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(units)
            combo.blockSignals(False)
        if len(units) > 1:
            self.to_unit.setCurrentIndex(1)
        self.convert()

    def convert(self, add_history=False):
        try:
            result = UnitConverter.convert(
                self.value_input.text() or "0",
                self.category_box.currentText(),
                self.from_unit.currentText(),
                self.to_unit.currentText(),
            )
        except Exception as exc:
            self.result_label.setText(str(exc))
            return
        text = (
            f"{float(self.value_input.text() or 0):,.6g} {self.from_unit.currentText()}\n"
            f"= {result:,.10g} {self.to_unit.currentText()}"
        )
        self.result_label.setText(text)
        if add_history:
            get_store().add_history("unit", self.category_box.currentText(), text)

    def swap_units(self):
        from_index = self.from_unit.currentIndex()
        self.from_unit.setCurrentIndex(self.to_unit.currentIndex())
        self.to_unit.setCurrentIndex(from_index)
        self.convert(add_history=True)

    @staticmethod
    def panel_style():
        return """
            UnitConverterPanel {
                background-color: #1e2228;
                border: 1px solid #303640;
                border-radius: 8px;
            }
            QLabel { color: #f4f6f8; font-weight: 600; }
            QLabel#Header { font-size: 28px; font-weight: 800; }
            QLabel#Result {
                background-color: #111419;
                border: 1px solid #303640;
                border-radius: 8px;
                color: #f4f6f8;
                font-size: 28px;
                font-weight: 800;
                padding: 18px;
            }
            QLineEdit, QComboBox {
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

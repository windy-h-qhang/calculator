from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QLabel, QSpinBox, QPushButton, QVBoxLayout, QWidget

from backend.settings_core import SettingsService


class SettingsPanel(QWidget):
    settings_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.panel_style())
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        header = QLabel("设置")
        header.setObjectName("Header")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.theme_box = QComboBox()
        self.theme_box.addItems(SettingsService.THEMES)
        self.default_mode_box = QComboBox()
        self.default_mode_box.addItems(SettingsService.DEFAULT_MODES)
        self.angle_box = QComboBox()
        self.angle_box.addItems(["DEG", "RAD"])
        self.precision_spin = QSpinBox()
        self.precision_spin.setRange(0, 12)
        self.base_currency = QComboBox()
        self.quote_currency = QComboBox()
        currencies = ["USD", "CNY", "EUR", "JPY", "GBP", "HKD", "AUD", "CAD", "CHF", "SGD"]
        self.base_currency.addItems(currencies)
        self.quote_currency.addItems(currencies)
        self.auto_refresh = QCheckBox("启动汇率模式时自动联网刷新")

        grid.addWidget(QLabel("主题"), 0, 0)
        grid.addWidget(self.theme_box, 0, 1)
        grid.addWidget(QLabel("启动模式"), 1, 0)
        grid.addWidget(self.default_mode_box, 1, 1)
        grid.addWidget(QLabel("角度模式"), 2, 0)
        grid.addWidget(self.angle_box, 2, 1)
        grid.addWidget(QLabel("小数精度"), 3, 0)
        grid.addWidget(self.precision_spin, 3, 1)
        grid.addWidget(QLabel("默认源货币"), 4, 0)
        grid.addWidget(self.base_currency, 4, 1)
        grid.addWidget(QLabel("默认目标货币"), 5, 0)
        grid.addWidget(self.quote_currency, 5, 1)
        grid.addWidget(self.auto_refresh, 6, 1)

        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self.save_settings)
        self.status_label = QLabel("")
        self.status_label.setObjectName("Hint")

        layout.addWidget(header)
        layout.addLayout(grid)
        layout.addWidget(save_button)
        layout.addWidget(self.status_label)
        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        settings = SettingsService.get_settings()
        self.theme_box.setCurrentText(settings["theme"])
        self.default_mode_box.setCurrentText(settings["default_mode"])
        self.angle_box.setCurrentText(settings["angle_mode"])
        self.precision_spin.setValue(int(settings["precision"]))
        self.base_currency.setCurrentText(settings["default_currency_base"])
        self.quote_currency.setCurrentText(settings["default_currency_quote"])
        self.auto_refresh.setChecked(bool(settings["auto_refresh_currency"]))

    def save_settings(self):
        settings = SettingsService.update_settings(
            {
                "theme": self.theme_box.currentText(),
                "default_mode": self.default_mode_box.currentText(),
                "angle_mode": self.angle_box.currentText(),
                "precision": self.precision_spin.value(),
                "default_currency_base": self.base_currency.currentText(),
                "default_currency_quote": self.quote_currency.currentText(),
                "auto_refresh_currency": self.auto_refresh.isChecked(),
            }
        )
        self.status_label.setText("设置已保存")
        self.settings_changed.emit(settings)

    @staticmethod
    def panel_style():
        return """
            SettingsPanel {
                background-color: #1e2228;
                border: 1px solid #303640;
                border-radius: 8px;
            }
            QLabel, QCheckBox { color: #f4f6f8; font-weight: 600; }
            QLabel#Header { font-size: 28px; font-weight: 800; }
            QLabel#Hint { color: #aab2bd; }
            QComboBox, QSpinBox {
                background-color: #191d23;
                border: 1px solid #5c6572;
                border-radius: 8px;
                color: #f4f6f8;
                padding: 9px 10px;
            }
            QPushButton {
                background-color: #2278e8;
                border: 1px solid #2278e8;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 16px;
                font-weight: 800;
            }
            QPushButton:hover { background-color: #155fbf; }
        """

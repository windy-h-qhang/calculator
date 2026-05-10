from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
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

from backend.currency_core import CurrencyRateService
from backend.persistence import get_store
from backend.settings_core import SettingsService


class RateFetchWorker(QObject):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, base, quote):
        super().__init__()
        self.base = base
        self.quote = quote

    def run(self):
        try:
            self.finished.emit(CurrencyRateService.fetch_rate(self.base, self.quote))
        except Exception as exc:
            self.failed.emit(str(exc))


class CurrencyConverterPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_rate = None
        self.worker_thread = None
        self.worker = None
        self.has_loaded_rate = False
        self.setStyleSheet(self.panel_style())
        self.init_ui()
        self.load_persistent_history()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        header = QLabel("汇率转换")
        header.setObjectName("Header")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.amount_input = QLineEdit("1")
        self.amount_input.textChanged.connect(lambda _text: self.convert(add_history=False))
        self.amount_input.returnPressed.connect(lambda: self.convert(add_history=True))

        self.from_currency = QComboBox()
        self.to_currency = QComboBox()
        for code, name in CurrencyRateService.COMMON_CURRENCIES:
            label = f"{code} - {name}"
            self.from_currency.addItem(label, code)
            self.to_currency.addItem(label, code)
        self.from_currency.setMinimumWidth(150)
        self.to_currency.setMinimumWidth(150)
        self.from_currency.view().setMinimumWidth(190)
        self.to_currency.view().setMinimumWidth(190)
        settings = SettingsService.get_settings()
        self.from_currency.setCurrentIndex(
            self.find_currency_index(self.from_currency, settings.get("default_currency_base", "USD"))
        )
        self.to_currency.setCurrentIndex(
            self.find_currency_index(self.to_currency, settings.get("default_currency_quote", "CNY"))
        )
        self.from_currency.currentIndexChanged.connect(self.refresh_rate)
        self.to_currency.currentIndexChanged.connect(self.refresh_rate)

        swap_button = QPushButton("交换")
        swap_button.clicked.connect(self.swap_currencies)
        convert_button = QPushButton("转换")
        convert_button.clicked.connect(lambda: self.convert(add_history=True))
        refresh_button = QPushButton("联网刷新")
        refresh_button.clicked.connect(self.refresh_rate)

        grid.addWidget(QLabel("金额"), 0, 0)
        grid.addWidget(self.amount_input, 0, 1)
        grid.addWidget(QLabel("从"), 0, 2)
        grid.addWidget(self.from_currency, 0, 3)
        grid.addWidget(QLabel("到"), 0, 4)
        grid.addWidget(self.to_currency, 0, 5)
        grid.addWidget(swap_button, 0, 6)
        grid.addWidget(convert_button, 0, 7)
        grid.addWidget(refresh_button, 0, 8)

        self.result_label = QLabel("正在获取汇率...")
        self.result_label.setObjectName("Result")
        self.rate_label = QLabel("")
        self.rate_label.setObjectName("Hint")

        history_row = QHBoxLayout()
        history_title = QLabel("转换记录")
        history_title.setObjectName("SubHeader")
        clear_history = QPushButton("清空")
        clear_history.clicked.connect(self.clear_history)
        history_row.addWidget(history_title)
        history_row.addStretch()
        history_row.addWidget(clear_history)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.restore_history_item)

        layout.addWidget(header)
        layout.addLayout(grid)
        layout.addWidget(self.result_label)
        layout.addWidget(self.rate_label)
        layout.addLayout(history_row)
        layout.addWidget(self.history_list, 1)
        self.setLayout(layout)

    def ensure_rate_loaded(self):
        if not self.has_loaded_rate:
            self.refresh_rate()

    def selected_base(self):
        return self.from_currency.currentData()

    def selected_quote(self):
        return self.to_currency.currentData()

    def refresh_rate(self):
        base = self.selected_base()
        quote = self.selected_quote()
        if not base or not quote:
            return

        self.rate_label.setText(f"正在联网获取 {base} -> {quote} 汇率...")
        self.has_loaded_rate = True
        self.worker_thread = QThread()
        self.worker = RateFetchWorker(base, quote)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_rate_loaded)
        self.worker.failed.connect(self.on_rate_failed)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def on_rate_loaded(self, data):
        self.current_rate = data
        self.rate_label.setText(
            f"1 {data['base']} = {data['rate']:.8g} {data['quote']}    "
            f"数据日期：{data['date']}"
        )
        self.convert(add_history=False)

    def on_rate_failed(self, message):
        self.current_rate = None
        self.rate_label.setText(f"汇率获取失败：{message}")
        self.result_label.setText("请检查网络后重试。")

    def convert(self, add_history=False):
        if not self.current_rate:
            return
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            self.result_label.setText("请输入有效金额")
            return

        converted = amount * self.current_rate["rate"]
        base = self.current_rate["base"]
        quote = self.current_rate["quote"]
        result_text = f"{amount:,.4f} {base} = {converted:,.4f} {quote}"
        self.result_label.setText(result_text)
        if add_history:
            self.add_history(result_text)

    def add_history(self, text):
        self.history_list.insertItem(0, QListWidgetItem(text))
        get_store().add_history("currency", "汇率转换", text)

    def swap_currencies(self):
        from_index = self.from_currency.currentIndex()
        to_index = self.to_currency.currentIndex()
        self.from_currency.blockSignals(True)
        self.to_currency.blockSignals(True)
        self.from_currency.setCurrentIndex(to_index)
        self.to_currency.setCurrentIndex(from_index)
        self.from_currency.blockSignals(False)
        self.to_currency.blockSignals(False)
        self.refresh_rate()

    def restore_history_item(self, item):
        self.result_label.setText(item.text())

    def clear_history(self):
        self.history_list.clear()
        get_store().clear_history("currency")

    def load_persistent_history(self):
        self.history_list.clear()
        for item in get_store().list_history("currency", 30):
            self.history_list.addItem(QListWidgetItem(item["result"]))

    @staticmethod
    def find_currency_index(combo, code):
        for index in range(combo.count()):
            if combo.itemData(index) == code:
                return index
        return 0

    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.convert(add_history=True)
            return
        super().keyPressEvent(event)

    @staticmethod
    def panel_style():
        return """
            CurrencyConverterPanel {
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
            QLabel#Result {
                background-color: #111419;
                border: 1px solid #303640;
                border-radius: 8px;
                color: #f4f6f8;
                font-size: 30px;
                font-weight: 800;
                padding: 18px;
            }
            QLabel#Hint {
                color: #aab2bd;
                font-weight: 400;
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

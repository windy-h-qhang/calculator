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

from currency_core import CurrencyRateService


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

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

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
        self.from_currency.setCurrentIndex(self.find_currency_index(self.from_currency, "USD"))
        self.to_currency.setCurrentIndex(self.find_currency_index(self.to_currency, "CNY"))
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
            QLabel#Result {
                background-color: #171a1f;
                border: 1px solid #3c4043;
                border-radius: 8px;
                color: #f1f3f4;
                font-size: 28px;
                font-weight: 700;
                padding: 18px;
            }
            QLabel#Hint {
                color: #aeb4bb;
                font-weight: 400;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #1f2328;
                border: 1px solid #5f6368;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 8px;
                selection-background-color: #174ea6;
            }
            QComboBox {
                min-height: 28px;
                padding-right: 28px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2f33;
                border: 1px solid #6f757d;
                color: #f1f3f4;
                selection-background-color: #174ea6;
                outline: 0;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 4px 12px;
            }
            QPushButton {
                background-color: #3c4043;
                border: 1px solid #6f757d;
                border-radius: 6px;
                color: #f1f3f4;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4b5055;
            }
            QPushButton:pressed {
                background-color: #303438;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #30363d;
            }
            QListWidget::item:selected {
                background-color: #174ea6;
                color: #ffffff;
            }
        """

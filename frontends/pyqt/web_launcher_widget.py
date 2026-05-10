from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from frontends.django_web.server import DEFAULT_URL, start_server_once


class WebLauncherPanel(QWidget):
    def __init__(self, url=DEFAULT_URL):
        super().__init__()
        self.url = url
        self.server_started = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(
            """
            WebLauncherPanel {
                background-color: #1e2228;
                border: 1px solid #303640;
                border-radius: 8px;
            }
            QLabel {
                color: #f4f6f8;
            }
            """
        )
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addStretch()

        title = QLabel("网站地址")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))

        self.url_button = QPushButton(self.url)
        self.url_button.setCursor(Qt.PointingHandCursor)
        self.url_button.setMinimumHeight(52)
        self.url_button.clicked.connect(self.open_web_calculator)
        self.url_button.setStyleSheet(
            """
            QPushButton {
                background-color: #111419;
                border: 1px solid #5c6572;
                border-radius: 8px;
                color: #8ab4f8;
                font-size: 18px;
                font-weight: 700;
                padding: 10px 16px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #203a5e;
                border-color: #75a7ea;
            }
            QPushButton:pressed {
                background-color: #155fbf;
                color: #ffffff;
            }
            """
        )

        layout.addWidget(title)
        layout.addWidget(self.url_button)
        layout.addStretch()
        self.setLayout(layout)

    def ensure_server(self):
        if self.server_started:
            return
        self.url = start_server_once()
        self.url_button.setText(self.url)
        self.server_started = True

    def open_web_calculator(self):
        self.ensure_server()
        QDesktopServices.openUrl(QUrl(self.url))

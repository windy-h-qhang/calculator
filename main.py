import sys

from PyQt5.QtWidgets import QApplication

from calculator_ui import Calculator


def main():
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

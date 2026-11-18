import sys

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main() -> None:
    """Responsible for launching the application."""

    app: QApplication = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
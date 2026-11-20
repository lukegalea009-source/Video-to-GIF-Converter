import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from frontend.main_window import MainWindow


def load_stylesheet() -> str:
    """Reads application stylesheet."""
    stylesheet_path = Path(__file__).resolve().parent / "frontend" / "styles" / "dark_theme.qss"

    stylesheet = stylesheet_path.read_text(
        encoding="utf-8"
    )
    
    return stylesheet


def main() -> None:
    """Responsible for launching the application."""

    app: QApplication = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
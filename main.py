from sys import argv
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
)




def main() -> None:

    app: QApplication = QApplication(argv)

    window: QMainWindow = QMainWindow()
    window.setWindowTitle("Video-to-GIF Converter")
    window.resize(900, 600)

    window.show()
    app.exec()


if __name__ == "__main__":
    main()
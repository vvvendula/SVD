import sys
from PySide6.QtWidgets import QApplication
from LorenzMainWindow import LorenzMainWindow


def main():
    app = QApplication(sys.argv)
    window = LorenzMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
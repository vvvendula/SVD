import sys
from PySide6.QtWidgets import QApplication
from LorenzMainWindow import LorenzMainWindow
from porovnani_spline import vykresli_trajektorii, animate


def main():
    app = QApplication(sys.argv)
    window = LorenzMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

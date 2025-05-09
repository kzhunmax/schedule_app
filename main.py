from PyQt6.QtWidgets import QApplication
from database import init_db
from ui.main_window import MainWindow
import sys

if __name__ == "__main__":
    init_db() # initialize database if table is not c
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
from PyQt6.QtWidgets import QApplication
from src.database import init_db
from src.ui.main_window import MainWindow
import sys

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
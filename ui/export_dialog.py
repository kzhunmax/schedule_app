import sqlite3
from language import tr
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from models import Lesson
from utils import export_to_csv, export_to_json
from database import DB_PATH


class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("app.export.title"))
        self.setMinimumWidth(300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        csv_btn = QPushButton(tr("app.export.csv"))
        json_btn = QPushButton(tr("app.export.json"))

        csv_btn.clicked.connect(self.export_as_csv)
        json_btn.clicked.connect(self.export_as_json)

        layout.addWidget(csv_btn)
        layout.addWidget(json_btn)

        self.setLayout(layout)

    def export_as_csv(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons")
        rows = cursor.fetchall()
        conn.close()

        lessons = [Lesson(*row) for row in rows]
        export_to_csv(lessons, self)
        self.accept()

    def export_as_json(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons")
        rows = cursor.fetchall()
        conn.close()

        lessons = [Lesson(*row) for row in rows]
        export_to_json(lessons, self)
        self.accept()

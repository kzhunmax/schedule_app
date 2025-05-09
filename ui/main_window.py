import sqlite3
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QComboBox
)
from PyQt6.QtGui import QFont, QIcon
from database import DB_PATH
from models import Lesson
from ui.lesson_dialog import LessonDialog
from utils import export_to_csv, export_to_json, import_from_csv, import_from_json
from settings import save_theme, load_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Planner")
        self.setGeometry(100, 100, 800, 600)
        with open("styles/dark_theme.qss", "r") as f:
            self.setStyleSheet(f.read())

        # Load theme
        self.load_current_theme()

        # Icon of program
        icon_path = os.path.join(os.path.dirname(__file__), "..", "images", "icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # Initialize UI
        self.init_ui()
        self.load_table()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Top Toolbar (settings + theme buttons)
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(10, 5, 10, 5)

        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon("images/icons/cil-settings.png"))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setFixedSize(40, 40)

        self.theme_btn = QPushButton()
        self.update_theme_button_icon()
        self.theme_btn.setToolTip("Toggle Theme")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)

        toolbar.addWidget(self.settings_btn)
        toolbar.addWidget(self.theme_btn)
        toolbar.addStretch()

        # Day selector
        top_layout = QHBoxLayout()
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.day_combo.currentIndexChanged.connect(self.load_table)
        top_layout.addWidget(QLabel("Choose day:"))
        top_layout.addWidget(self.day_combo)

        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Subject", "Time", "Type", "Room", "Action"])
        self.table.horizontalHeader().setFont(QFont("Arial", 14, QFont.Weight.Bold))

        # Settings Button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon("images/icons/cil-settings.png"))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setFixedSize(40, 40)

        # Theme Toggle Button
        self.theme_btn = QPushButton()
        self.theme_btn.setToolTip("Theme")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.update_theme_button_icon()

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add")
        edit_btn = QPushButton("✏️ Edit")
        del_btn = QPushButton("🗑️ Delete")
        export_csv_btn = QPushButton("📁 CSV Export")
        export_json_btn = QPushButton("📦 JSON Export")
        import_csv_btn = QPushButton("📥 CSV Import")
        import_json_btn = QPushButton("📥 JSON Import")

        # Connect signals
        add_btn.clicked.connect(self.add_lesson)
        edit_btn.clicked.connect(self.edit_lesson)
        del_btn.clicked.connect(self.delete_lesson)
        export_csv_btn.clicked.connect(self.export_to_csv)
        export_json_btn.clicked.connect(self.export_to_json)
        import_csv_btn.clicked.connect(self.import_from_csv)
        import_json_btn.clicked.connect(self.import_from_json)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(export_csv_btn)
        btn_layout.addWidget(export_json_btn)
        btn_layout.addWidget(import_csv_btn)
        btn_layout.addWidget(import_json_btn)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(toolbar)
        layout.addLayout(top_layout)
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)

        main_widget.setLayout(layout)

    def load_table(self):
        day = self.day_combo.currentText()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons WHERE day=?", (day,))
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            lesson = Lesson(*row)
            self.table.setItem(i, 0, QTableWidgetItem(lesson.subject))
            self.table.setItem(i, 1, QTableWidgetItem(lesson.time))
            self.table.setItem(i, 2, QTableWidgetItem(lesson.type))
            self.table.setItem(i, 3, QTableWidgetItem(lesson.room))

            delete_button = QPushButton("❌")
            delete_button.setStyleSheet("padding: 4px;")
            delete_button.clicked.connect(lambda _, r=i, lid=lesson.id: self.delete_row(lid))  # type: ignore
            self.table.setCellWidget(i, 4, delete_button)

    def add_lesson(self):
        dialog = LessonDialog(parent=self)
        if dialog.exec() == LessonDialog.DialogCode.Accepted:
            lesson = dialog.get_data()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lessons (day, subject, time, type, room)
                VALUES (?, ?, ?, ?, ?)
            """, (lesson.day, lesson.subject, lesson.time, lesson.type, lesson.room))
            conn.commit()
            conn.close()
            self.load_table()

    def edit_lesson(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        item = self.table.item(selected, 0)
        if not item:
            return
        lesson_id = self.get_lesson_id(selected)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons WHERE id=?", (lesson_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return

        lesson = Lesson(*row)
        dialog = LessonDialog(lesson=lesson, parent=self)
        if dialog.exec() == LessonDialog.DialogCode.Accepted:
            updated = dialog.get_data()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lessons SET day=?, subject=?, time=?, type=?, room=?
                WHERE id=?
            """, (updated.day, updated.subject, updated.time, updated.type, updated.room, lesson_id))
            conn.commit()
            conn.close()
            self.load_table()

    def delete_lesson(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        lesson_id = self.get_lesson_id(selected)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
        conn.commit()
        conn.close()
        self.load_table()

    def delete_row(self, lesson_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
        conn.commit()
        conn.close()
        self.load_table()

    def get_lesson_id(self, row):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        day = self.day_combo.currentText()
        subject = self.table.item(row, 0).text()
        cursor.execute("SELECT id FROM lessons WHERE day=? AND subject=?", (day, subject))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def export_to_csv(self):
        day = self.day_combo.currentText()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons WHERE day=?", (day,))
        rows = cursor.fetchall()
        conn.close()

        lessons = [Lesson(*row) for row in rows]
        export_to_csv(lessons, self)

    def export_to_json(self):
        day = self.day_combo.currentText()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons WHERE day=?", (day,))
        rows = cursor.fetchall()
        conn.close()

        lessons = [Lesson(*row) for row in rows]
        export_to_json(lessons, self)

    def import_from_csv(self):
        lessons = import_from_csv(self)
        self.bulk_insert_lessons(lessons)

    def import_from_json(self):
        lessons = import_from_json(self)
        self.bulk_insert_lessons(lessons)

    def bulk_insert_lessons(self, lessons):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Clear current day first
        current_day = self.day_combo.currentText()
        cursor.execute("DELETE FROM lessons WHERE day=?", (current_day,))

        # Insert new lessons
        for lesson in lessons:
            cursor.execute("""
                INSERT INTO lessons (day, subject, time, type, room)
                VALUES (?, ?, ?, ?, ?)
            """, (current_day, lesson.subject, lesson.time, lesson.type, lesson.room))
        conn.commit()
        conn.close()
        self.load_table()

    def update_theme_button_icon(self):
        current_theme = load_theme()
        icon_path = "images/icons/cil-moon.png" if current_theme == "dark_theme" else "images/icons/cil-lightbulb.png"
        self.theme_btn.setIcon(QIcon(icon_path))

    def load_current_theme(self):
        current_theme = load_theme()
        qss_file = f"styles/{current_theme}.qss"
        try:
            with open(qss_file, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("An error has occurred while loading theme:", e)

    def toggle_theme(self):
        current = load_theme()
        new_theme = "light_theme" if current == "dark_theme" else "dark_theme"
        save_theme(new_theme)
        self.load_current_theme()
        self.update_theme_button_icon()
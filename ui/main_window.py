import sqlite3
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolButton
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from database import DB_PATH
from models import Lesson
from ui.lesson_dialog import LessonDialog
from utils import export_to_csv, export_to_json, import_from_csv, import_from_json
from settings import save_theme, load_theme, load_language
from ui.settings_dialog import SettingsDialog
from ui.schedule_view import ScheduleView
from language import set_language, tr, load_translations


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Planner")
        self.setGeometry(100, 100, 1200, 700)
        self.load_current_theme()
        self.setWindowIcon(QIcon("images/icon.png"))

        load_translations()

        # Порядок мов і їх коди
        self.languages = [("English", "en"), ("Українська", "ukr"), ("Polska", "pl")]
        self.current_language_index = self.load_language_index()

        self.init_ui()
        self.load_lessons()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        self.schedule_view = ScheduleView()

        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar.setSpacing(5)

        # Кнопка перемикання мови
        self.language_button = QToolButton()
        self.language_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.language_button.setFixedHeight(40)
        self.language_button.setObjectName("sidebarButton")
        self.language_button.setIcon(QIcon("images/icon.png"))
        self.language_button.clicked.connect(self.cycle_language)
        sidebar.addWidget(self.language_button)

        lang_name, _ = self.languages[self.current_language_index]
        self.language_button.setText(lang_name)

        # Кнопки бічної панелі
        self.theme_btn = self.create_sidebar_button("", "cil-lightbulb.png", self.toggle_theme)
        self.add_btn = self.create_sidebar_button("", "cil-plus.png", self.add_lesson)
        self.export_schedule = self.create_sidebar_button("", "cil-level-up.png", self.export_to_csv)
        self.import_schedule = self.create_sidebar_button("", "cil-level-down.png", self.import_from_csv)
        self.settings_btn = self.create_sidebar_button("", "cil-settings.png", self.open_settings)

        for btn in [self.theme_btn, self.add_btn, self.export_schedule, self.import_schedule, self.settings_btn]:
            sidebar.addWidget(btn)

        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFixedWidth(200)
        sidebar_frame.setFrameShape(QFrame.Shape.StyledPanel)

        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.schedule_view)

        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(right_frame)
        main_layout.setStretch(1, 1)

        self.update_theme_button_icon()
        self.update_ui_texts()

    def create_sidebar_button(self, text, icon_name, callback):
        btn = QToolButton()
        btn.setIcon(QIcon(f"images/icons/{icon_name}"))
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setObjectName("sidebarButton")
        btn.setFixedHeight(40)
        btn.clicked.connect(callback)
        return btn

    def load_language_index(self):
        saved_lang = load_language()
        for i, (_, code) in enumerate(self.languages):
            if code == saved_lang:
                return i
        return 0

    def cycle_language(self):
        self.current_language_index = (self.current_language_index + 1) % len(self.languages)
        _, lang_code = self.languages[self.current_language_index]
        set_language(lang_code)  # наприклад, змінюємо глобальну мову
        self.language_button.setText(_)  # оновлюємо текст кнопки
        self.update_ui_texts()  # оновлюємо всі елементи інтерфейсу

    def update_ui_texts(self):
        self.setWindowTitle(tr("app.title"))
        self.theme_btn.setText(tr("app.buttons.theme"))
        self.add_btn.setText(tr("app.buttons.add"))
        self.export_schedule.setText(tr("app.buttons.export_csv"))
        self.import_schedule.setText(tr("app.buttons.import_csv"))
        self.settings_btn.setText(tr("app.buttons.settings"))

    def load_lessons(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons ORDER BY day, start_time")  # Add sorting
        rows = cursor.fetchall()
        conn.close()

        lessons = [Lesson(*row) for row in rows]
        self.schedule_view.set_lessons(lessons)

    def add_lesson(self):
        dialog = LessonDialog(parent=self)
        if dialog.exec() == LessonDialog.DialogCode.Accepted:
            lesson = dialog.get_data()
            conn = sqlite3.connect('data/schedule.db')
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO lessons (day, subject, start_time, end_time, type, room)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (lesson.day, lesson.subject, lesson.start_time, lesson.end_time, lesson.type, lesson.room))
            conn.commit()
            conn.close()
            self.load_lessons()

    def edit_lesson(self):
        # Placeholder for actual lesson selection logic
        print("Edit lesson not implemented fully")

    def delete_lesson(self):
        # Placeholder for actual lesson selection logic
        print("Delete lesson not implemented fully")

    def export_schedule(self):
        pass

    def import_schedule(self):
        pass

    def export_to_csv(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons")
        rows = cursor.fetchall()
        conn.close()

        lessons = [Lesson(*row) for row in rows]
        export_to_csv(lessons, self)

    def export_to_json(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons")
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
        cursor.execute("DELETE FROM lessons")
        for lesson in lessons:
            cursor.execute("""
                    INSERT INTO lessons (day, subject, start_time, end_time, type, room)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (lesson.day, lesson.subject, lesson.start_time, lesson.end_time, lesson.type, lesson.room))
        conn.commit()
        conn.close()
        self.load_lessons()

    def update_theme_button_icon(self):
        current_theme = load_theme()
        icon_path = "images/icons/cil-moon.png" if current_theme == "dark_theme" else "images/icons/cil-lightbulb.png"
        self.theme_btn.setIcon(QIcon(icon_path))

    def load_current_theme(self):
        current_theme = load_theme()
        try:
            with open(f"styles/{current_theme}.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Theme load error:", e)

    def toggle_theme(self):
        current = load_theme()
        new_theme = "light_theme" if current == "dark_theme" else "dark_theme"
        save_theme(new_theme)
        self.load_current_theme()
        self.update_theme_button_icon()

    def open_settings(self):
        dialog = SettingsDialog(parent=self)
        dialog.exec()

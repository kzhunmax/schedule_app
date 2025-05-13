import os
import sqlite3
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolButton
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from database import DB_PATH
from models import Lesson
from notification import Notification
from ui.export_dialog import ExportDialog
from ui.import_dialog import ImportDialog
from ui.lesson_dialog import LessonDialog
from settings import save_theme, load_theme, load_language, load_notifications
from ui.settings_dialog import SettingsDialog
from ui.schedule_view import ScheduleWidget
from language import set_language, tr, load_translations


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app.title"))
        self.setGeometry(100, 50, 1280, 720)
        self.setMinimumSize(1280, 720)
        self.load_current_theme()
        self.setWindowIcon(QIcon("images/icon.png"))

        self.notification = Notification(self)
        self.notification.hide()
        self.icon_buttons = []
        load_translations()

        # Порядок мов і їх коди
        self.languages = [("      English", "en"), ("      Українська", "ukr"), ("      Polska", "pl")]
        self.current_language_index = self.load_language_index()

        self.init_ui()
        self.load_lessons()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.schedule_widget = ScheduleWidget()

        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(0)


        # Кнопки бічної панелі
        self.language_button = self.create_sidebar_button("", "globe.png", self.cycle_language)
        self.add_btn = self.create_sidebar_button("", "plus.png", self.add_lesson)
        self.export_schedule = self.create_sidebar_button("", "export.png", self.open_export_dialog)
        self.import_schedule = self.create_sidebar_button("", "import.png", self.open_import_dialog)
        self.settings_btn = self.create_sidebar_button("", "settings.png", self.open_settings)
        self.theme_btn = self.create_sidebar_button("", "moon.png", self.toggle_theme)

        for btn in [self.language_button, self.add_btn, self.export_schedule, self.import_schedule, self.settings_btn, self.theme_btn]:
            sidebar.addWidget(btn)
            self.icon_buttons.append(btn)

        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFrameShape(QFrame.Shape.NoFrame)

        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(self.schedule_widget)

        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(right_frame)
        main_layout.setStretch(1, 1)

        self.update_ui_texts()
        self.update_all_button_icons()
        self.update_language_button_text()

    def update_all_button_icons(self):
        current_theme = load_theme()

        for btn in self.icon_buttons:
            if not hasattr(btn, "icon_name"):
                continue

            icon_base = btn.icon_name

            # Special case for theme toggle button
            suffix = "-light" if current_theme == "light_theme" else "-dark"
            icon_name = f"{icon_base}{suffix}.png"

            icon_path = f"images/icons/{icon_name}"

            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            else:
                # Fallback to default icon without suffix
                fallback_icon_path = f"images/icons/{icon_base}.png"
                if os.path.exists(fallback_icon_path):
                    btn.setIcon(QIcon(fallback_icon_path))

    @staticmethod
    def create_sidebar_button(text, icon_name, callback):
        btn = QToolButton()
        btn.setIcon(QIcon(f"images/icons/{icon_name}"))
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setObjectName("sidebarButton")
        btn.clicked.connect(callback)
        btn.icon_name = icon_name.split('.')[0]
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
        set_language(lang_code)
        self.update_language_button_text()
        self.update_ui_texts()
        self.schedule_widget.refresh_translation()

    def update_language_button_text(self):
        lang_name, _ = self.languages[self.current_language_index]
        self.language_button.setText(lang_name)

    def update_ui_texts(self):
        self.setWindowTitle(tr("app.title"))
        self.add_btn.setText(tr("app.buttons.add"))
        self.export_schedule.setText(tr("app.buttons.export_csv"))
        self.import_schedule.setText(tr("app.buttons.import_csv"))
        self.settings_btn.setText(tr("app.buttons.settings"))
        if load_theme() == "light_theme":
            self.theme_btn.setText(tr("app.buttons.light_theme"))
        else:
            self.theme_btn.setText(tr("app.buttons.dark_theme"))

    def load_lessons(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lessons ORDER BY day, start_time")
        rows = cursor.fetchall()
        conn.close()

        lessons = [Lesson(*row) for row in rows]
        self.schedule_widget.set_lessons(lessons)

    def add_lesson(self):
        dialog = LessonDialog(parent=self)
        if dialog.exec() == LessonDialog.DialogCode.Accepted:
            lesson = dialog.get_data()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO lessons (day, subject, start_time, end_time, type, room)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (lesson.day, lesson.subject, lesson.start_time, lesson.end_time, lesson.type, lesson.room))
            conn.commit()
            conn.close()
            self.load_lessons()

    def edit_lesson(self):
        pass

    def delete_lesson(self):
        pass

    def bulk_insert_lessons(self, lessons):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lessons")
                for lesson in lessons:
                    cursor.execute("""
                        INSERT INTO lessons (id, day, subject, start_time, end_time, type, room, color)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lesson.id,
                        lesson.day,
                        lesson.subject,
                        lesson.start_time,
                        lesson.end_time,
                        lesson.type,
                        lesson.room,
                        lesson.color
                    ))
                conn.commit()
                self.load_lessons()
        except Exception:
            self.parent.show_notification(tr("app.import.file_corrupted"), success=False)


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
        self.update_ui_texts()
        self.update_all_button_icons()

    def open_settings(self):
        dialog = SettingsDialog(parent=self)
        dialog.exec()

    def set_new_language(self, lang_code):
        set_language(lang_code)

        for i, (_, code) in enumerate(self.languages):
            if code == lang_code:
                self.current_language_index = i
                break

        self.update_language_button_text()
        self.update_ui_texts()
        self.update_all_button_icons()
        self.schedule_widget.refresh_translation()

    def open_export_dialog(self):
        dialog = ExportDialog(self)
        dialog.exec()

    def open_import_dialog(self):
        dialog = ImportDialog(self)
        dialog.exec()

    def show_notification(self, message, success=False, duration=3000):
        if not load_notifications():
            return
        self.notification.show_message(message, success, duration)
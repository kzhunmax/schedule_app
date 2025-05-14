"""
Головне вікно додатку для управління розкладом занять.

Містить інтерфейс для перегляду, додавання, редагування та експорту/імпорту уроків.
Також надає функціонал зміни теми, мови та сповіщень.
"""

import os
import sqlite3
from typing import List, Tuple
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolButton
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from src.database import DB_PATH
from src.models import Lesson
from src.notification import Notification
from src.ui.export_dialog import ExportDialog
from src.ui.import_dialog import ImportDialog
from src.ui.lesson_dialog import LessonDialog
from src.settings import save_theme, load_theme, load_language, load_notifications
from src.ui.settings_dialog import SettingsDialog
from src.ui.schedule_view import ScheduleWidget
from src.language import set_language, tr, load_translations
from src.signals import app_signals


class MainWindow(QMainWindow):
    """Головне вікно додатку для управління розкладом."""

    def __init__(self) -> None:
        """Ініціалізує головне вікно додатку."""
        super().__init__()
        self._setup_window_properties()
        self.notification = Notification(self)
        self.notification.hide()
        self.icon_buttons = []
        load_translations()

        # Connect signals for other files
        app_signals.show_notification.connect(self._show_notification)
        app_signals.load_current_theme.connect(self._load_current_theme)
        app_signals.update_all_button_icons.connect(self._update_all_button_icons)
        app_signals.set_new_language.connect(self._set_new_language)
        app_signals.lessons_imported.connect(self._bulk_insert_lessons)

        self.languages = self._initialize_languages()
        self.current_language_index = self._load_language_index()

        self._init_ui()
        self._load_lessons()

    def _setup_window_properties(self) -> None:
        """Налаштовує основні властивості вікна."""
        self.setWindowTitle(tr("app.title"))
        self.setGeometry(100, 50, 1280, 720)
        self.setMinimumSize(1280, 720)
        self._load_current_theme()
        self.setWindowIcon(QIcon("src/images/icon.png"))

    @staticmethod
    def _initialize_languages() -> List[Tuple[str, str]]:
        """Ініціалізує список доступних мов.

        Returns:
            List[Tuple[str, str]]: Список кортежів (назва мови, код мови).
        """
        return [
            ("      English", "en"),
            ("      Українська", "ukr"),
            ("      Polska", "pl")
        ]

    def _init_ui(self) -> None:
        """Ініціалізує інтерфейс користувача."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.schedule_widget = ScheduleWidget()

        sidebar = self._create_sidebar()
        right_frame = self._create_right_frame()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(right_frame)
        main_layout.setStretch(1, 1)

        self._update_ui_texts()
        self._update_all_button_icons()
        self._update_language_button_text()

    def _create_sidebar(self) -> QFrame:
        """Створює бічну панель з кнопками."""
        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(0)

        # Створюємо кнопки і зберігаємо їх як атрибути
        self.language_button = self._create_sidebar_button("", "globe.png", self._cycle_language)
        self.add_btn = self._create_sidebar_button("", "plus.png", self._add_lesson)
        self.export_schedule = self._create_sidebar_button("", "export.png", self._open_export_dialog)
        self.import_schedule = self._create_sidebar_button("", "import.png", self._open_import_dialog)
        self.settings_btn = self._create_sidebar_button("", "settings.png", self._open_settings)
        self.theme_btn = self._create_sidebar_button("", "moon.png", self._toggle_theme)

        # Додаємо всі кнопки до бічної панелі
        buttons = [
            self.language_button,
            self.add_btn,
            self.export_schedule,
            self.import_schedule,
            self.settings_btn,
            self.theme_btn
        ]

        for btn in buttons:
            sidebar.addWidget(btn)
            self.icon_buttons.append(btn)

        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFrameShape(QFrame.Shape.NoFrame)
        return sidebar_frame

    def _create_right_frame(self) -> QFrame:
        """Створює праву частину інтерфейсу з розкладом.

        Returns:
            QFrame: Готова права частина інтерфейсу.
        """
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(self.schedule_widget)
        return right_frame

    @staticmethod
    def _create_sidebar_button(text: str, icon_name: str, callback) -> QToolButton:
        """Створює кнопку для бічної панелі.

        Args:
            text (str): Текст кнопки.
            icon_name (str): Назва іконки.
            callback: Функція, яка викликається при натисканні.

        Returns:
            QToolButton: Готова кнопка.
        """
        btn = QToolButton()
        btn.setIcon(QIcon(f"src/images/icons/{icon_name}"))
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setObjectName("sidebarButton")
        btn.clicked.connect(callback)
        btn.icon_name = icon_name.split('.')[0]
        return btn

    def _load_language_index(self) -> int:
        """Завантажує індекс поточної мови.

        Returns:
            int: Індекс мови у списку languages.
        """
        saved_lang = load_language()
        for i, (_, code) in enumerate(self.languages):
            if code == saved_lang:
                return i
        return 0

    def _cycle_language(self) -> None:
        """Змінює мову інтерфейсу на наступну у списку."""
        self.current_language_index = (self.current_language_index + 1) % len(self.languages)
        _, lang_code = self.languages[self.current_language_index]
        set_language(lang_code)
        self._update_language_button_text()
        self._update_ui_texts()
        self.schedule_widget.refresh_translation()

    def _update_language_button_text(self) -> None:
        """Оновлює текст кнопки зміни мови."""
        lang_name, _ = self.languages[self.current_language_index]
        self.language_button.setText(lang_name)

    def _update_ui_texts(self) -> None:
        """Оновлює всі тексти інтерфейсу відповідно до поточної мови."""
        self.setWindowTitle(tr("app.title"))
        self.add_btn.setText(tr("app.buttons.add"))
        self.export_schedule.setText(tr("app.buttons.export_csv"))
        self.import_schedule.setText(tr("app.buttons.import_csv"))
        self.settings_btn.setText(tr("app.buttons.settings"))
        theme_text = tr("app.buttons.light_theme") if load_theme() == "light_theme" else tr("app.buttons.dark_theme")
        self.theme_btn.setText(theme_text)

    def _load_lessons(self) -> None:
        """Завантажує уроки з бази даних та відображає їх у розкладі."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM lessons ORDER BY day, start_time")
                lessons = [Lesson(*row) for row in cursor.fetchall()]
                self.schedule_widget.set_lessons(lessons)
        except sqlite3.Error:
            self._show_notification(tr("app.database.error"), False)

    def _add_lesson(self) -> None:
        """Відкриває діалогове вікно для додавання нового уроку."""
        dialog = LessonDialog(parent=self)
        if dialog.exec() == LessonDialog.DialogCode.Accepted:
            lesson = dialog.get_data()
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO lessons (day, subject, start_time, end_time, type, room, color)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lesson.day, lesson.subject, lesson.start_time,
                        lesson.end_time, lesson.type, lesson.room, lesson.color
                    ))
                    conn.commit()
                    self._load_lessons()
                    self._show_notification(tr("app.lesson.added"), True)
            except sqlite3.Error:
                self._show_notification(tr("app.database.error"), False)

    def _bulk_insert_lessons(self, lessons: list) -> None:
        """Додає список уроків до бази даних.

        Args:
            lessons (list): Список уроків для додавання.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lessons")
                for lesson in lessons:
                    cursor.execute("""
                        INSERT INTO lessons (id, day, subject, start_time, end_time, type, room, color)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lesson.id, lesson.day, lesson.subject,
                        lesson.start_time, lesson.end_time,
                        lesson.type, lesson.room, lesson.color
                    ))
                conn.commit()
                self._load_lessons()
                self._show_notification(tr("app.import.success"), True)
        except Exception as e:
            print(f"Main window error: {e}")
            self._show_notification(tr("app.import.file_corrupted"), False)

    def _load_current_theme(self) -> None:
        """Завантажує поточну тему інтерфейсу."""
        current_theme = load_theme()
        try:
            with open(f"src/styles/{current_theme}.qss", "r") as f:
                self.setStyleSheet(f.read())
        except IOError as e:
            print(f"Theme load error: {e}")

    def _toggle_theme(self) -> None:
        """Змінює тему інтерфейсу на протилежну."""
        current = load_theme()
        new_theme = "light_theme" if current == "dark_theme" else "dark_theme"
        save_theme(new_theme)
        self._load_current_theme()
        self._update_ui_texts()
        self._update_all_button_icons()

    def _update_all_button_icons(self) -> None:
        """Оновлює іконки всіх кнопок відповідно до поточної теми."""
        current_theme = load_theme()
        suffix = "-light" if current_theme == "light_theme" else "-dark"

        for btn in self.icon_buttons:
            if not hasattr(btn, "icon_name"):
                continue

            icon_name = f"{btn.icon_name}{suffix}.png"
            icon_path = f"src/images/icons/{icon_name}"

            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            else:
                fallback_icon_path = f"src/images/icons/{btn.icon_name}.png"
                if os.path.exists(fallback_icon_path):
                    btn.setIcon(QIcon(fallback_icon_path))

    def _open_settings(self) -> None:
        """Відкриває діалогове вікно налаштувань."""
        dialog = SettingsDialog(parent=self)
        dialog.exec()

    def _set_new_language(self, lang_code: str) -> None:
        """Встановлює нову мову інтерфейсу.

        Args:
            lang_code (str): Код мови (наприклад, 'en', 'ukr').
        """
        set_language(lang_code)
        for i, (_, code) in enumerate(self.languages):
            if code == lang_code:
                self.current_language_index = i
                break
        self._update_language_button_text()
        self._update_ui_texts()
        self._update_all_button_icons()
        self.schedule_widget.refresh_translation()

    def _open_export_dialog(self) -> None:
        """Відкриває діалогове вікно експорту."""
        dialog = ExportDialog(self)
        dialog.exec()

    def _open_import_dialog(self) -> None:
        """Відкриває діалогове вікно імпорту."""
        dialog = ImportDialog(self)
        dialog.exec()

    def _show_notification(self, message: str, success: bool = False, duration: int = 3000) -> None:
        """Показує сповіщення.

        Args:
            message (str): Текст сповіщення.
            success (bool): Чи є сповіщення про успіх.
            duration (int): Тривалість показу в мілісекундах.
        """
        if load_notifications():
            self.notification.show_message(message, success, duration)

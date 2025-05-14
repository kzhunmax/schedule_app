"""
Діалогове вікно для експорту даних у файли CSV/JSON.

Підтримує:
- Експорт у формат CSV
- Експорт у формат JSON
- Вибір місця збереження файлу
- Повідомлення про результат операції
"""

import sqlite3
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton

from src.signals import app_signals
from src.language import tr
from src.utils import export_to_csv, export_to_json
from src.database import DB_PATH
from src.models import Lesson


class ExportDialog(QDialog):
    """Діалогове вікно експорту даних."""

    MIN_WIDTH = 300
    BTN_SPACING = 10

    def __init__(self, parent=None):
        """Ініціалізація діалогового вікна.

        Args:
            parent: Батьківський віджет
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Ініціалізація інтерфейсу користувача."""
        self.setWindowTitle(tr("app.export.title"))
        self.setMinimumWidth(self.MIN_WIDTH)

        layout = QVBoxLayout()
        layout.setSpacing(self.BTN_SPACING)

        self.csv_btn = QPushButton(tr("app.export.csv"))
        self.json_btn = QPushButton(tr("app.export.json"))

        self.csv_btn.clicked.connect(self._export_as_csv)
        self.json_btn.clicked.connect(self._export_as_json)

        layout.addWidget(self.csv_btn)
        layout.addWidget(self.json_btn)

        self.setLayout(layout)

    def _export_as_csv(self) -> None:
        """Експортує дані у формат CSV."""
        lessons = self._get_lessons_from_db()
        if not lessons:
            self._show_error(tr("app.export.no_data"))
            return

        result = export_to_csv(lessons, self)
        self._handle_export_result(result, "csv")

    def _export_as_json(self) -> None:
        """Експортує дані у формат JSON."""
        lessons = self._get_lessons_from_db()
        if not lessons:
            self._show_error(tr("app.export.no_data"))
            return

        result = export_to_json(lessons, self)
        self._handle_export_result(result, "json")

    @staticmethod
    def _get_lessons_from_db() -> list[Lesson]:
        """Отримує уроки з бази даних.

        Returns:
            Список об'єктів Lesson
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM lessons")
                return [Lesson(*row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def _handle_export_result(self, result: bool, format_type: str) -> None:
        """Обробляє результат експорту.

        Args:
            result: Результат операції експорту
            format_type: Тип формату ('csv' або 'json')
        """
        if result is None:  # Користувач скасував операцію
            self.reject()
            return

        key = f"{format_type}_success" if result else f"{format_type}_failed"
        self._show_notification(tr(f"app.export.{key}"), result)
        self.accept() if result else self.reject()

    def _show_notification(self, message: str, success: bool) -> None:
        """Показує повідомлення про результат операції.

        Args:
            message: Текст повідомлення
            success: Чи успішна операція
        """
        if self.parent():
            app_signals.show_notification.emit(message, success)

    def _show_error(self, message: str) -> None:
        """Показує повідомлення про помилку.

        Args:
            message: Текст повідомлення
        """
        self._show_notification(message, False)
        self.reject()
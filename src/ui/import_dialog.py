"""
Діалогове вікно для імпорту даних з файлів CSV/JSON.

Підтримує:
- Вибір файлу через діалогове вікно
- Drag-and-drop файлів
- Валідацію формату файлу
- Імпорт уроків у базу даних
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from src.language import tr
from src.utils import import_from_csv, import_from_json
from src.signals import app_signals


class ImportDialog(QDialog):
    """Діалогове вікно імпорту даних."""

    MIN_WIDTH = 400
    MIN_HEIGHT = 300
    FILE_FILTERS = "CSV Files (*.csv);;JSON Files (*.json)"

    def __init__(self, parent=None):
        """Ініціалізація діалогового вікна.

        Args:
            parent: Батьківський віджет
        """
        super().__init__(parent)
        self.parent = parent
        self._init_ui()

    def _init_ui(self) -> None:
        """Ініціалізація інтерфейсу користувача."""
        self.setWindowTitle(tr("app.import.title"))
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setAcceptDrops(True)

        layout = QVBoxLayout()
        self.label = QLabel(tr("app.import.instructions"))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")
        layout.addWidget(self.label)

        self.setLayout(layout)

    def mousePressEvent(self, event) -> None:
        """Обробка click мишею для відкриття файлу."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._open_file_dialog()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Обробка події перетягування файлу у вікно."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Обробка події скидання файлу."""
        urls = event.mimeData().urls()
        if urls:
            self._handle_file(urls[0].toLocalFile())

    def _open_file_dialog(self) -> None:
        """Відкриває діалогове вікно вибору файлу."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("app.import.select_file"),
            "",
            self.FILE_FILTERS
        )
        if file_path:
            self._handle_file(file_path)

    def _handle_file(self, file_path: str) -> None:
        """Обробляє вибраний файл для імпорту.

        Args:
            file_path: Шлях до файлу для імпорту
        """
        try:
            if file_path.endswith(".csv"):
                self._import_csv(file_path)
            elif file_path.endswith(".json"):
                self._import_json(file_path)
            else:
                self._show_error(tr("app.import.unsupported_format"))

        except Exception as e:
            print(f"Import dialog error: {e}")
            self._show_error(tr("app.import.file_corrupted"))

    def _import_csv(self, file_path: str) -> None:
        """Імпортує дані з CSV файлу.

        Args:
            file_path: Шлях до CSV файлу
        """
        lessons = import_from_csv(file_path)
        if not lessons:
            self._show_error(tr("app.import.csv_failed"))
            return

        app_signals.lessons_imported.emit(lessons)
        self._show_success(tr("app.import.csv_success"))

    def _import_json(self, file_path: str) -> None:
        """Імпортує дані з JSON файлу.

        Args:
            file_path: Шлях до JSON файлу
        """
        lessons = import_from_json(file_path)
        if not lessons:
            self._show_error(tr("app.import.json_failed"))
            return

        app_signals.lessons_imported.emit(lessons)
        self._show_success(tr("app.import.json_success"))

    def _show_success(self, message: str) -> None:
        """Показує повідомлення про успішний імпорт.

        Args:
            message: Текст повідомлення
        """
        self.label.setText(message)
        app_signals.show_notification.emit(message, True)
        self.accept()

    def _show_error(self, message: str) -> None:
        """Показує повідомлення про помилку імпорту.

        Args:
            message: Текст повідомлення
        """
        self.label.setText(message)
        app_signals.show_notification.emit(message, False)
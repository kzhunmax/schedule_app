"""
Діалогове вікно для вибору часу.

Надає інтерфейс для вибору години та хвилини
з можливістю збереження або скасування.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)

from src.language import tr


class TimePickerDialog(QDialog):
    """Діалогове вікно вибору часу."""

    DIALOG_WIDTH = 200
    DIALOG_HEIGHT = 100
    MARGINS = (10, 5, 10, 10)
    SPACING = 5

    def __init__(self, current_time: str = "09:00", parent=None):
        """
        Ініціалізація діалогового вікна.

        Args:
            current_time: Поточний час у форматі HH:MM
            parent: Батьківський віджет
        """
        super().__init__(parent)
        self.time = current_time
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Налаштовує інтерфейс користувача."""
        self.setWindowTitle(tr("app.time_dialog.title"))
        self.setFixedSize(self.DIALOG_WIDTH, self.DIALOG_HEIGHT)

        layout = QVBoxLayout(self)
        layout.setSpacing(self.SPACING)
        layout.setContentsMargins(*self.MARGINS)

        self._setup_time_controls(layout)
        self._setup_action_buttons(layout)

    def _setup_time_controls(self, layout: QVBoxLayout) -> None:
        """Налаштовує елементи вибору часу."""
        time_layout = QHBoxLayout()

        self.hour_combo = QComboBox()
        self.minute_combo = QComboBox()
        self._populate_time_combos()

        colon_label = QLabel(":")
        colon_label.setFixedSize(30, 30)
        colon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)

        time_layout.addWidget(self.hour_combo)
        time_layout.addWidget(colon_label)
        time_layout.addWidget(self.minute_combo)
        layout.addLayout(time_layout)

    def _populate_time_combos(self) -> None:
        """Заповнює комбобокси з годинами та хвилинами."""
        for h in range(0, 24):
            self.hour_combo.addItem(f"{h:02d}")

        for m in range(0, 60, 5):
            self.minute_combo.addItem(f"{m:02d}")

        if ":" in self.time:
            hour, minute = self.time.split(":")
            self.hour_combo.setCurrentText(hour.zfill(2))
            self.minute_combo.setCurrentText(minute.zfill(2))

    def _setup_action_buttons(self, layout: QVBoxLayout) -> None:
        """Налаштовує кнопки дій."""
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton(tr("app.time_dialog.save"))
        self.cancel_btn = QPushButton(tr("app.time_dialog.cancel"))

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_time(self) -> str:
        """Повертає вибраний час.

        Returns:
            Рядок часу у форматі HH:MM
        """
        return f"{self.hour_combo.currentText()}:{self.minute_combo.currentText()}"

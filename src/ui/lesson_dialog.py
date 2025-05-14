"""
Діалогове вікно для створення уроку.

Містить форму для введення всіх необхідних даних про урок:
- День тижня
- Назва предмету
- Час початку та закінчення
- Тип заняття (онлайн/офлайн)
- Аудиторія
- Колір для візуалізації
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QComboBox, QFrame, QButtonGroup
)
from src.models import Lesson
from src.language import tr
from src.ui.time_picker_dialog import TimePickerDialog
from src.signals import app_signals

class LessonDialog(QDialog):
    """Діалогове вікно для роботи з уроками."""

    # Константи класу
    COLORS = ["#00a7e5", "#14142b", "#e40173", "#6308f7", "#ff7f08", "#44d6df", "#b1cb49"]
    DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    MIN_DIALOG_WIDTH = 400
    MIN_DIALOG_HEIGHT = 650
    start_time_input: QLineEdit
    end_time_input: QLineEdit

    def __init__(self, lesson: Lesson = None, parent=None):
        """Ініціалізація діалогового вікна.

        Args:
            lesson: Існуючий урок для редагування (опціонально)
            parent: Батьківський віджет
        """
        super().__init__(parent)
        self.lesson = lesson or Lesson()
        self.selected_color = self.lesson.color or self.COLORS[0]

        self._init_ui()
        self._setup_connections()

    def _init_ui(self) -> None:
        """Ініціалізація інтерфейсу користувача."""
        self.setWindowTitle(tr("app.lesson_dialog.add_title"))
        self.setMinimumSize(self.MIN_DIALOG_WIDTH, self.MIN_DIALOG_HEIGHT)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 10, 20, 20)
        self.setLayout(main_layout)

        # Основні елементи форми
        self._init_day_selector(main_layout)
        self._init_subject_input(main_layout)
        self._init_time_inputs(main_layout)
        self._init_type_selector(main_layout)
        self._init_room_input(main_layout)
        self._init_color_picker(main_layout)
        self._init_action_buttons(main_layout)

    def _init_day_selector(self, layout: QVBoxLayout) -> None:
        """Ініціалізує вибір дня тижня."""
        self.day_combo = QComboBox()
        self.day_combo.addItems([tr(f"app.days.{day}") for day in self.DAYS])

        if self.lesson.day:
            day_key = self.lesson.day.lower()
            if day_key in self.DAYS:
                self.day_combo.setCurrentText(tr(f"app.days.{day_key}"))

        layout.addWidget(QLabel(tr("app.lesson_dialog.label_day")))
        layout.addWidget(self.day_combo)

    def _init_subject_input(self, layout: QVBoxLayout) -> None:
        """Ініціалізує поле вводу назви предмету."""
        self.subject_input = QLineEdit(self.lesson.subject)
        self.subject_input.setPlaceholderText(tr("app.lesson_dialog.subject_placeholder"))

        layout.addWidget(QLabel(tr("app.lesson_dialog.label_subject")))
        layout.addWidget(self.subject_input)

    def _init_time_inputs(self, layout: QVBoxLayout) -> None:
        """Ініціалізує поля для часу початку та закінчення."""
        # Початковий час
        self._init_time_input(
            layout,
            "app.lesson_dialog.label_start_time",
            "start_time_input",
            self.lesson.start_time,
            self.pick_start_time
        )

        # Час закінчення
        self._init_time_input(
            layout,
            "app.lesson_dialog.label_end_time",
            "end_time_input",
            self.lesson.end_time,
            self.pick_end_time
        )

    def _init_time_input(self, layout: QVBoxLayout, label_key: str,
                         input_name: str, initial_value: str,
                         picker_slot) -> None:
        """Створює поле для вводу часу з кнопкою вибору.

        Args:
            layout: Layout для додавання елементів
            label_key: Ключ перекладу для підпису
            input_name: Назва атрибуту для поля вводу
            initial_value: Початкове значення
            picker_slot: Функція-обробник вибору часу
        """
        time_input = QLineEdit(initial_value)
        time_input.setPlaceholderText(tr("app.lesson_dialog.time_placeholder"))
        setattr(self, input_name, time_input)

        pick_btn = QPushButton("...")
        pick_btn.setFixedSize(30, 30)
        pick_btn.clicked.connect(picker_slot)

        if "start" in label_key.lower():
            self.pick_start_time_btn = pick_btn
        elif "end" in label_key.lower():
            self.pick_end_time_btn = pick_btn

        time_layout = QHBoxLayout()
        time_layout.addWidget(time_input)
        time_layout.addWidget(pick_btn)

        layout.addWidget(QLabel(tr(label_key)))
        layout.addLayout(time_layout)

    def _init_type_selector(self, layout: QVBoxLayout) -> None:
        """Ініціалізує вибір типу заняття (онлайн/офлайн)."""
        self.online_btn = self._create_type_button("app.lesson_dialog.type_online")
        self.offline_btn = self._create_type_button("app.lesson_dialog.type_offline")

        self.option_group = QButtonGroup(self)
        self.option_group.addButton(self.online_btn)
        self.option_group.addButton(self.offline_btn)
        self.option_group.setExclusive(True)

        # Встановлення початкового стану
        if self.lesson.type == "Offline":
            self.offline_btn.setChecked(True)
        else:
            self.online_btn.setChecked(True)

        type_group = QFrame()
        type_layout = QHBoxLayout()
        type_layout.addWidget(self.online_btn)
        type_layout.addWidget(self.offline_btn)
        type_group.setLayout(type_layout)

        layout.addWidget(QLabel(tr("app.lesson_dialog.label_type")))
        layout.addWidget(type_group)

    @staticmethod
    def _create_type_button(text_key: str) -> QPushButton:
        """Створює кнопку для вибору типу заняття."""
        btn = QPushButton(tr(text_key))
        btn.setObjectName("optionButton")
        btn.setCheckable(True)
        return btn

    def _init_room_input(self, layout: QVBoxLayout) -> None:
        """Ініціалізує поле вводу аудиторії."""
        self.room_input = QLineEdit(self.lesson.room)
        self.room_input.setPlaceholderText(tr("app.lesson_dialog.room_placeholder"))

        layout.addWidget(QLabel(tr("app.lesson_dialog.label_room")))
        layout.addWidget(self.room_input)

    def _init_color_picker(self, layout: QVBoxLayout) -> None:
        """Ініціалізує вибір кольору."""
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_color")))

        self.color_button_group = QButtonGroup(self)
        self.color_button_group.setExclusive(True)

        color_layout = QHBoxLayout()
        for color in self.COLORS:
            btn = self._create_color_button(color)
            self.color_button_group.addButton(btn)
            color_layout.addWidget(btn)

        layout.addLayout(color_layout)
        self._update_color_buttons()

    def _create_color_button(self, color: str) -> QPushButton:
        """Створює кнопку вибору кольору."""
        btn = QPushButton()
        btn.setFixedSize(30, 30)
        btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 15px;
                background-color: rgba({self.hex_to_rgba(color, 0.2)});
                border: 2px solid {color};
            }}
            QPushButton:checked {{
                background-color: {color};
            }}
        """)
        btn.setCheckable(True)
        btn.setToolTip(color)
        return btn

    def _init_action_buttons(self, layout: QVBoxLayout) -> None:
        """Ініціалізує кнопки дій (зберегти/скасувати)."""
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton(tr("app.lesson_dialog.save"))
        self.cancel_btn = QPushButton(tr("app.lesson_dialog.cancel"))

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def _setup_connections(self) -> None:
        """Налаштовує підключення сигналів."""
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _update_color_buttons(self) -> None:
        """Оновлює стан кнопок вибору кольору."""
        for button in self.color_button_group.buttons():
            if button.toolTip() == self.lesson.color:
                button.setChecked(True)
                self.selected_color = button.toolTip()
                break
        else:
            self.color_button_group.buttons()[0].setChecked(True)

    @staticmethod
    def hex_to_rgba(hex_color: str, opacity: float = 1.0) -> str:
        """Конвертує HEX-колір у RGBA-рядок.

        Args:
            hex_color: Колір у форматі HEX
            opacity: Прозорість (0.0-1.0)

        Returns:
            Рядок у форматі "R, G, B, A"
        """
        hex_color = hex_color.lstrip('#')
        return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, {opacity}"

    def pick_start_time(self) -> None:
        """Відкриває діалог вибору часу початку."""
        self._pick_time(self.start_time_input)

    def pick_end_time(self) -> None:
        """Відкриває діалог вибору часу закінчення."""
        self._pick_time(self.end_time_input)

    def _pick_time(self, target_input: QLineEdit) -> None:
        """Спільний метод для вибору часу.

        Args:
            target_input: Поле вводу, куди записати результат
        """
        dialog = TimePickerDialog(target_input.text(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            target_input.setText(dialog.get_time())

    def validate_and_accept(self) -> None:
        """Валідує дані перед закриттям діалогу."""
        if not self._validate_inputs():
            return

        self.accept()

    def _validate_inputs(self) -> bool:
        """Валідація введених даних.

        Returns:
            True, якщо дані валідні, False - якщо ні
        """
        subject = self.subject_input.text().strip()
        if not subject:
            self._show_error(tr("app.lesson_dialog.error_empty_subject"))
            return False

        start_time = self.normalize_time(self.start_time_input.text().strip())
        end_time = self.normalize_time(self.end_time_input.text().strip())

        if not all([self._validate_time(t) for t in [start_time, end_time]]):
            return False

        if not self._validate_time_range(start_time, end_time):
            return False

        return True

    def _validate_time(self, time_str: str) -> bool:
        """Валідує формат часу."""
        if not time_str:
            self._show_error(tr("app.lesson_dialog.error_time_required"))
            return False

        if not self.validate_time_format(time_str):
            self._show_error(tr("app.lesson_dialog.error_invalid_time_format"))
            return False

        return True

    def _validate_time_range(self, start_time: str, end_time: str) -> bool:
        """Валідує часовий проміжок."""
        if start_time == end_time:
            self._show_error(tr("app.lesson_dialog.error_same_times"))
            return False

        if self.time_to_minutes(end_time) <= self.time_to_minutes(start_time):
            self._show_error(tr("app.lesson_dialog.error_end_before_start"))
            return False

        return True

    def _show_error(self, message: str) -> None:
        """Відображає повідомлення про помилку."""
        if self.parent():
            app_signals.show_notification.emit(message, False)

    @staticmethod
    def normalize_time(time_str: str) -> str:
        """Нормалізує рядок часу до формату HH:MM.

        Args:
            time_str: Рядок часу для нормалізації

        Returns:
            Нормалізований рядок часу
        """
        if not time_str or ':' not in time_str:
            return time_str

        hours, minutes = time_str.split(':')
        return f"{hours.zfill(2)}:{minutes.zfill(2)}"

    @staticmethod
    def time_to_minutes(time_str: str) -> int:
        """Конвертує час у хвилини.

        Args:
            time_str: Рядок часу у форматі HH:MM

        Returns:
            Кількість хвилин з початку доби
        """
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Перевіряє коректність формату часу.

        Args:
            time_str: Рядок часу для перевірки

        Returns:
            True, якщо формат валідний, False - якщо ні
        """
        try:
            if time_str.count(':') != 1:
                return False

            hours, minutes = time_str.split(':')
            if len(hours) != 2 or len(minutes) != 2:
                return False

            hours_int = int(hours)
            minutes_int = int(minutes)
            return 0 <= hours_int <= 23 and 0 <= minutes_int <= 59
        except ValueError:
            return False

    def get_data(self) -> Lesson:
        """Повертає дані уроку з форми.

        Returns:
            Об'єкт Lesson з даними з форми
        """
        selected_button = self.color_button_group.checkedButton()
        self.selected_color = selected_button.toolTip() if selected_button else self.COLORS[0]

        lesson_type = "Offline" if self.offline_btn.isChecked() else "Online"

        return Lesson(
            lesson_id=self.lesson.id,
            day=self.day_combo.currentText(),
            subject=self.subject_input.text().strip(),
            start_time=self.start_time_input.text().strip(),
            end_time=self.end_time_input.text().strip(),
            lesson_type=lesson_type,
            room=self.room_input.text().strip(),
            color=self.selected_color
        )

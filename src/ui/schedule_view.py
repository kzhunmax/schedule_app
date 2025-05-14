"""
Віджет для відображення розкладу занять у вигляді сітки.

Містить:
- Фон у вигляді сітки з годинами та днями тижня
- Блоки уроків з інформацією про предмет та аудиторію
- Підтримку різних мов інтерфейсу
- Можливість оновлення даних
"""
from typing import Any

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QScrollArea,
    QGridLayout, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from src.language import tr
from src.signals import app_signals


class GridBackground(QWidget):
    """Віджет для відображення фонової сітки розкладу."""

    def __init__(self, hours: list, days: list,
                 time_slot_height: int = 40,
                 day_header_width: int = 80,
                 parent=None):
        """
        Ініціалізація сітки.

        Args:
            hours: Список годин для відображення
            days: Список днів тижня
            time_slot_height: Висота одного часового проміжку
            day_header_width: Ширина заголовка з годинами
            parent: Батьківський віджет
        """
        super().__init__(parent)
        self.hours = hours
        self.days = days
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self._setup_initial_size()

    def _setup_initial_size(self) -> None:
        """Встановлює початковий розмір віджета."""
        min_width = self.day_header_width + len(self.days) * 150
        min_height = len(self.hours) * self.time_slot_height
        self.setMinimumSize(min_width, min_height)

    def paintEvent(self, event) -> None:
        """Малює сітку розкладу."""
        painter = QPainter(self)
        painter.setPen(QColor("#3a3a3a"))

        width = self.width()
        height = self.height()
        day_width = (width - self.day_header_width) // len(self.days)

        # Горизонтальні лінії (години)
        for i in range(len(self.hours) + 1):
            y = i * self.time_slot_height
            painter.drawLine(0, y, width, y)

        # Вертикальні лінії (дні)
        for i in range(len(self.days) + 1):
            x = self.day_header_width + i * day_width
            painter.drawLine(x, 0, x, height)


class ScheduleBlock(QFrame):
    """Блок для відображення одного уроку в розкладі."""

    def __init__(self, lesson):
        """
        Ініціалізація блоку уроку.

        Args:
            lesson: Об'єкт уроку для відображення
        """
        super().__init__()
        self.lesson = lesson
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Налаштовує інтерфейс блоку уроку."""
        self.setFixedHeight(40)
        color = self.lesson.color if self.lesson.color else "#3a3a3a"
        self._apply_styles(color)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(0)

        subject_label = QLabel(self.lesson.subject)
        room_text = self._format_room_text()
        room_label = QLabel(room_text)

        subject_label.setStyleSheet("font-weight: bold;")
        room_label.setStyleSheet("font-size: 12px;")

        layout.addWidget(subject_label)
        layout.addWidget(room_label)
        self.setLayout(layout)

    def _apply_styles(self, color: str) -> None:
        """Застосовує CSS стилі до блоку."""
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 4px;
            margin: 2px;
            padding: 5px;
        """)

    def _format_room_text(self) -> str:
        """Форматує текст про аудиторію."""
        room = self.lesson.room if self.lesson.room else tr("app.schedule.room_not_specified")
        return f"{tr('app.schedule.room_label')} {room}"


class ScheduleView(QScrollArea):
    """Основний віджет для відображення розкладу."""

    HOURS = [f"{hour:02d}:00" for hour in range(0, 24)]
    DAY_TRANSLATIONS = {
        'en': ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        'uk': ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"],
        'pl': ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]
    }

    def __init__(self, time_slot_height: int = 60,
                 day_header_width: int = 80,
                 min_day_width: int = 150):
        """
        Ініціалізація віджета розкладу.

        Args:
            time_slot_height: Висота одного часового проміжку
            day_header_width: Ширина заголовка з годинами
            min_day_width: Мінімальна ширина колонки дня
        """
        super().__init__()
        app_signals.render_lessons.connect(self._render_lessons)
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self.min_day_width = min_day_width
        self.lesson_blocks = []
        self.lessons = []
        self._setup_scroll_area()
        self._init_content_widget()
        self._setup_time_labels()

    @property
    def days(self) -> list:
        """Повертає список днів тижня у поточній мові."""
        return [
            tr("app.days.monday"),
            tr("app.days.tuesday"),
            tr("app.days.wednesday"),
            tr("app.days.thursday"),
            tr("app.days.friday"),
            tr("app.days.saturday"),
            tr("app.days.sunday")
        ]

    def _setup_scroll_area(self) -> None:
        """Налаштовує область прокрутки."""
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWidgetResizable(True)

    def _init_content_widget(self) -> None:
        """Ініціалізує вміст області прокрутки."""
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setWidget(self.content_widget)
        self._update_grid_size()

    def _update_grid_size(self) -> None:
        """Оновлює розмір сітки."""
        min_width = self.day_header_width + len(self.days) * self.min_day_width
        min_height = len(self.HOURS) * self.time_slot_height
        self.content_widget.setMinimumSize(min_width, min_height)

    def _setup_time_labels(self) -> None:
        """Додає мітки з годинами до сітки."""
        for row, time in enumerate(self.HOURS):
            label = QLabel(time)
            label.setFixedWidth(self.day_header_width)
            label.setFixedHeight(self.time_slot_height)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                color: #bbb;
                font-size: 12px;
                border-right: 1px solid #3a3a3a;
            """)
            self.grid_layout.addWidget(label, row, 0)

        self._add_background_grid()

    def _add_background_grid(self) -> None:
        """Додає фонову сітку."""
        self.background = GridBackground(
            self.HOURS,
            self.days,
            time_slot_height=self.time_slot_height,
            day_header_width=self.day_header_width
        )
        self.grid_layout.addWidget(
            self.background,
            0, 1,
            len(self.HOURS),
            len(self.days)
        )

    def set_lessons(self, lessons: list) -> None:
        """Встановлює уроки для відображення.

        Args:
            lessons: Список уроків
        """
        self.lessons = lessons
        self._render_lessons()

    def _render_lessons(self) -> None:
        """Відображає уроки на сітці."""
        self._clear_existing_blocks()
        self._create_day_mapping()

        for lesson in self.lessons:
            self._add_lesson_block(lesson)

    def _clear_existing_blocks(self) -> None:
        """Видаляє існуючі блоки уроків."""
        for block in self.lesson_blocks:
            block.setParent(None)
        self.lesson_blocks.clear()

    def _create_day_mapping(self) -> dict:
        """Створює мапу для швидкого пошуку днів.

        Returns:
            Словник зіставлень назв днів до їх індексів
        """
        reverse_mapping = {}
        for lang, days in self.DAY_TRANSLATIONS.items():
            for idx, day in enumerate(days):
                normalized_day = day.lower().strip()
                if normalized_day not in reverse_mapping:
                    reverse_mapping[normalized_day] = idx
        return reverse_mapping

    def _add_lesson_block(self, lesson) -> None:
        """Додає блок уроку на сітку.

        Args:
            lesson: Об'єкт уроку для додавання
        """
        try:
            day_index = self._get_day_index(lesson.day)
            if day_index is None:
                return

            row_index = self._get_time_row_index(lesson.start_time)
            if row_index is None:
                return

            block = self._create_lesson_block(lesson)
            self.grid_layout.addWidget(block, row_index, day_index + 1)
            self.lesson_blocks.append(block)
        except (ValueError, AttributeError):
            return

    def _get_day_index(self, day_name: str) -> Any | None:
        """Повертає індекс дня за його назвою.

        Args:
            day_name: Назва дня

        Returns:
            Індекс дня або None, якщо не знайдено
        """
        if not day_name:
            return None

        day_mapping = self._create_day_mapping()
        return day_mapping.get(day_name.lower().strip())

    def _get_time_row_index(self, time_str: str) -> int | None:
        """Повертає рядок сітки за часом.

        Args:
            time_str: Час у форматі HH:MM

        Returns:
            Індекс рядка або None, якщо не знайдено
        """
        if not time_str or ":" not in time_str:
            return None

        hour = time_str.split(":")[0].zfill(2) + ":00"
        try:
            return self.HOURS.index(hour)
        except ValueError:
            return None

    def _create_lesson_block(self, lesson) -> ScheduleBlock:
        """Створює блок уроку.

        Args:
            lesson: Об'єкт уроку

        Returns:
            Налаштований блок ScheduleBlock
        """
        block = ScheduleBlock(lesson)
        block.setFixedWidth(self.min_day_width - 10)

        try:
            start_h, start_m = map(int, lesson.start_time.split(':'))
            end_h, end_m = map(int, lesson.end_time.split(':'))
            duration = (end_h - start_h) + (end_m - start_m) / 60
            block.setFixedHeight(max(self.time_slot_height, int(duration * self.time_slot_height)))
        except (ValueError, AttributeError):
            block.setFixedHeight(self.time_slot_height)

        return block


class ScheduleWidget(QWidget):
    """Композитний віджет, що містить заголовки днів та розклад."""

    def __init__(self):
        """Ініціалізація віджета розкладу."""
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Налаштовує інтерфейс віджета."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.schedule_view = ScheduleView()
        self.day_width = self.schedule_view.min_day_width

        self._setup_header()
        layout.addWidget(self.header_frame)
        layout.addWidget(self.schedule_view)

    def _setup_header(self) -> None:
        """Налаштовує заголовок з днями тижня."""
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(self.schedule_view.time_slot_height)
        self.header_frame.setStyleSheet("""
            background-color: #2b2b2b;
            border-bottom: 1px solid #3a3a3a;
        """)

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(self.schedule_view.day_header_width, 0, 0, 0)
        header_layout.setSpacing(0)

        for day in self.schedule_view.days:
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedWidth(self.day_width)
            label.setStyleSheet("""
                font-weight: bold;
                font-size: 14px;
                color: white;
            """)
            header_layout.addWidget(label)

    def set_lessons(self, lessons: list) -> None:
        """Встановлює уроки для відображення.

        Args:
            lessons: Список уроків
        """
        self.schedule_view.set_lessons(lessons)

    def refresh_translation(self) -> None:
        """Оновлює переклад при зміні мови."""
        # Оновлюємо заголовки днів
        for i, day in enumerate(self.schedule_view.days):
            label = self.header_frame.layout().itemAt(i).widget()
            if isinstance(label, QLabel):
                label.setText(day)

        # Оновлюємо блоки уроків
        app_signals.render_lessons.emit()

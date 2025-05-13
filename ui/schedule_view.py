from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QScrollArea, QGridLayout,
    QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor

from language import tr


class GridBackground(QWidget):
    def __init__(self, hours, days, time_slot_height=40, day_header_width=80, parent=None):
        super().__init__(parent)
        self.hours = hours
        self.days = days
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width

        min_width = self.day_header_width + len(self.days) * 150
        min_height = len(self.hours) * self.time_slot_height
        self.setMinimumSize(min_width, min_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor("#3a3a3a"))

        width = self.width()
        height = self.height()

        day_width = (width - self.day_header_width) // len(self.days)

        # Horizontal lines
        for i in range(len(self.hours) + 1):
            y = i * self.time_slot_height
            painter.drawLine(0, y, width, y)

        # Vertical lines
        for i in range(len(self.days) + 1):
            x = self.day_header_width + i * day_width
            painter.drawLine(x, 0, x, height)


class ScheduleBlock(QFrame):
    def __init__(self, lesson):
        super().__init__()
        self.lesson = lesson
        self.setFixedHeight(40)
        color = lesson.color if lesson.color else "#3a3a3a"

        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 4px;
            margin: 2px;
            padding: 5px;
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(0)

        subject_label = QLabel(f"{lesson.subject}")
        room_text = f"{tr('app.schedule.room_label')} {lesson.room if lesson.room else tr('app.schedule.room_not_specified')}"
        room_label = QLabel(room_text)

        subject_label.setStyleSheet("font-weight: bold;")
        room_label.setStyleSheet("font-size: 12px;")

        layout.addWidget(subject_label)
        layout.addWidget(room_label)
        self.setLayout(layout)


class ScheduleView(QScrollArea):
    HOURS = [f"{hour:02d}:00" for hour in range(0, 24)]

    @property
    def DAYS(self):
        return [
            tr("app.days.monday"),
            tr("app.days.tuesday"),
            tr("app.days.wednesday"),
            tr("app.days.thursday"),
            tr("app.days.friday"),
            tr("app.days.saturday"),
            tr("app.days.sunday")
        ]

    def __init__(self, time_slot_height=60, day_header_width=80, min_day_width=150):
        super().__init__()
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self.min_day_width = min_day_width

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.setWidget(self.content_widget)
        self.lesson_blocks = []
        self.lessons = []

        self.update_grid_size()
        self._setup_time_labels()

    def _setup_time_labels(self):
        for row, time in enumerate(self.HOURS):
            label = QLabel(time)
            label.setFixedWidth(self.day_header_width)
            label.setFixedHeight(self.time_slot_height)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #bbb; font-size: 12px; border-right: 1px solid #3a3a3a;")
            self.grid_layout.addWidget(label, row, 0)

        self.background = GridBackground(
            self.HOURS,
            self.DAYS,
            time_slot_height=self.time_slot_height,
            day_header_width=self.day_header_width
        )
        self.grid_layout.addWidget(self.background, 0, 1, len(self.HOURS), len(self.DAYS))

    def update_grid_size(self):
        min_width = self.day_header_width + len(self.DAYS) * self.min_day_width
        min_height = len(self.HOURS) * self.time_slot_height
        self.content_widget.setMinimumSize(min_width, min_height)

    def set_lessons(self, lessons):
        self.lessons = lessons
        self._render()

    def _render(self):
        for block in self.lesson_blocks:
            block.setParent(None)
        self.lesson_blocks.clear()

        day_width = self.min_day_width

        # Створюємо словники для всіх підтримуваних мов
        day_translations = {
            'en': ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            'uk': ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"],
            'pl': ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]
        }

        # Створюємо обернений словник для швидкого пошуку
        reverse_day_mapping = {}
        for lang, days in day_translations.items():
            for idx, day in enumerate(days):
                # Приводимо до нижнього регістру для уніфікованого порівняння
                normalized_day = day.lower()
                if normalized_day not in reverse_day_mapping:
                    reverse_day_mapping[normalized_day] = idx

        for lesson in self.lessons:
            try:
                # Нормалізуємо назву дня з уроку
                lesson_day = lesson.day.lower().strip()

                # Знаходимо індекс дня за допомогою оберненого словника
                day_index = reverse_day_mapping.get(lesson_day)
                if day_index is None:
                    continue  # Пропускаємо, якщо день не розпізнано

                col_index = day_index + 1  # +1 тому що перша колонка - це час

                # Решта логіки залишається незмінною
                start_hour = lesson.start_time.split(':')[0].zfill(2) + ":00"
                if start_hour not in self.HOURS:
                    continue

                row_index = self.HOURS.index(start_hour)

                start_h, start_m = map(int, lesson.start_time.split(':'))
                end_h, end_m = map(int, lesson.end_time.split(':'))
                duration = (end_h - start_h) + (end_m - start_m) / 60
                block_height = max(self.time_slot_height, int(duration * self.time_slot_height))

                block_frame = ScheduleBlock(lesson)
                block_frame.setFixedWidth(day_width - 10)
                block_frame.setFixedHeight(block_height)
                self.grid_layout.addWidget(block_frame, row_index, col_index)
                self.lesson_blocks.append(block_frame)
            except ValueError:
                continue


class ScheduleWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.schedule_view = ScheduleView()
        self.day_width = self.schedule_view.min_day_width

        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(self.schedule_view.time_slot_height)
        self.header_frame.setStyleSheet("background-color: #2b2b2b; border-bottom: 1px solid #3a3a3a;")

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(self.schedule_view.day_header_width, 0, 0, 0)
        header_layout.setSpacing(0)

        # Використовуємо переклад для заголовків днів
        for day in self.schedule_view.DAYS:
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedWidth(self.day_width)
            label.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
            header_layout.addWidget(label)


        layout.addWidget(self.header_frame)
        layout.addWidget(self.schedule_view)

    def set_lessons(self, lessons):
        self.schedule_view.set_lessons(lessons)

    def refresh_translation(self):
        """Оновлює переклад при зміні мови"""
        # Оновлюємо заголовки днів
        for i, day in enumerate(self.schedule_view.DAYS):
            self.header_frame.layout().itemAt(i).widget().setText(day)

        # Оновлюємо блоки уроків
        self.schedule_view._render()
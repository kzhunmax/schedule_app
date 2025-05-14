from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QScrollArea,
    QGridLayout, QWidget, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from src.language import tr
from src.signals import app_signals


class GridBackground(QWidget):
    def __init__(self, hours: list, days: list,
                 time_slot_height: int = 60,
                 day_header_width: int = 100,
                 parent=None):
        super().__init__(parent)
        self.hours = hours
        self.days = days
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self._setup_initial_size()

    def _setup_initial_size(self) -> None:
        min_width = len(self.days) * 200  # 200px per day column
        min_height = len(self.hours) * self.time_slot_height
        self.setMinimumSize(min_width, min_height)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setPen(QColor("#3a3a3a"))
        width = self.width()
        height = self.height()
        day_width = width // len(self.days) if len(self.days) > 0 else 0

        # Horizontal lines (hours)
        for i in range(len(self.hours) + 1):
            y = i * self.time_slot_height
            painter.drawLine(0, y, width, y)

        # Vertical lines (days)
        for i in range(len(self.days) + 1):
            x = i * day_width
            painter.drawLine(x, 0, x, height)


class ScheduleBlock(QFrame):
    def __init__(self, lesson):
        super().__init__()
        self.lesson = lesson
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(60)
        self._apply_styles()

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(4)

        subject_label = QLabel(self.lesson.subject)
        type_text = self._format_type_text()
        room_text = self._format_room_text()

        type_label = QLabel(type_text)
        room_label = QLabel(room_text)

        subject_label.setStyleSheet("font-weight: bold; font-size: 14px; background-color: transparent;")
        type_label.setStyleSheet("font-size: 12px; background-color: transparent;")
        room_label.setStyleSheet("font-size: 12px; background-color: transparent;")

        layout.addWidget(subject_label)
        layout.addWidget(type_label)
        layout.addWidget(room_label)
        self.setLayout(layout)

    def _apply_styles(self) -> None:
        color = self.lesson.color if hasattr(self.lesson, 'color') and self.lesson.color else "#3a3a3a"
        self.setStyleSheet(f"""
            ScheduleBlock {{
                background-color: {color};
                border-radius: 6px;
                margin: 4px;
                padding: 8px;
                color: black;
            }}
        """)

    def _format_type_text(self) -> str:
        if hasattr(self.lesson, 'type') and self.lesson.type:
            return f"{tr('app.schedule.type_label')} {self.lesson.type}"
        return ""

    def _format_room_text(self) -> str:
        room = self.lesson.room if hasattr(self.lesson, 'room') and self.lesson.room else tr(
            "app.schedule.room_not_specified")
        return f"{tr('app.schedule.room_label')} {room}"

class ScrollSyncManager:
    def __init__(self, main_scroll, time_scroll=None, header_scroll=None):
        self.main_scroll = main_scroll
        if time_scroll:
            main_scroll.verticalScrollBar().valueChanged.connect(time_scroll.verticalScrollBar().setValue)
            time_scroll.verticalScrollBar().valueChanged.connect(main_scroll.verticalScrollBar().setValue)
        if header_scroll:
            main_scroll.horizontalScrollBar().valueChanged.connect(header_scroll.horizontalScrollBar().setValue)
            header_scroll.horizontalScrollBar().valueChanged.connect(main_scroll.horizontalScrollBar().setValue)

class TimeColumn(QWidget):
    def __init__(self, hours, time_slot_height=60, day_header_width=100):
        super().__init__()
        self.hours = hours
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self.setFixedWidth(day_header_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor("#ffffff"))

        # Draw right border
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        # Draw horizontal lines to match grid and add time labels
        for i in range(len(self.hours)):
            y = i * self.time_slot_height
            # Draw text (time label)
            painter.drawText(0, y + self.time_slot_height // 2, self.width(), self.time_slot_height,
                             Qt.AlignmentFlag.AlignCenter, self.hours[i])

class ScheduleView(QWidget):
    HOURS = [f"{hour:02d}:00" for hour in range(0, 24)]
    DAY_TRANSLATIONS = {
        'en': ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        'uk': ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"],
        'pl': ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]
    }

    def __init__(self, time_slot_height=80, day_header_width=100, min_day_width=200):
        super().__init__()
        app_signals.render_lessons.connect(self._render_lessons)
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self.min_day_width = min_day_width
        self.lesson_blocks = []
        self.lessons = []

        self._setup_ui()

    @property
    def days(self) -> list:
        return [
            tr("app.days.monday"),
            tr("app.days.tuesday"),
            tr("app.days.wednesday"),
            tr("app.days.thursday"),
            tr("app.days.friday"),
            tr("app.days.saturday"),
            tr("app.days.sunday")
        ]

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Time column
        self.time_column = TimeColumn(self.HOURS, self.time_slot_height, self.day_header_width)
        self.time_scroll_area = QScrollArea()
        self.time_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.time_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.time_scroll_area.setWidgetResizable(True)
        self.time_scroll_area.setFixedWidth(self.day_header_width)
        self.time_scroll_area.setWidget(self.time_column)
        main_layout.addWidget(self.time_scroll_area)

        # Main scroll area for grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        # Add background grid
        self.background = GridBackground(
            self.HOURS,
            self.days,
            time_slot_height=self.time_slot_height,
            day_header_width=0
        )
        self.grid_layout.addWidget(
            self.background,
            0, 0,
            len(self.HOURS),
            len(self.days),
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        self._update_grid_size()

    def set_header_scroll_area(self, header_scroll):
        self.scroll_sync = ScrollSyncManager(
            main_scroll=self.scroll_area,
            time_scroll=self.time_scroll_area,
            header_scroll=header_scroll
        )

    def _update_grid_size(self):
        min_width = len(self.days) * self.min_day_width
        min_height = len(self.HOURS) * self.time_slot_height
        self.content_widget.setMinimumSize(min_width, min_height)

    def set_lessons(self, lessons):
        self.lessons = lessons
        self._render_lessons()

    def _render_lessons(self):
        self._clear_existing_blocks()
        self._update_background()  # New method call to update background size and redraw
        day_mapping = self._create_day_mapping()
        for lesson in self.lessons:
            try:
                day_index = day_mapping.get(lesson.day.lower().strip())
                if day_index is None:
                    continue
                row_index = self._get_time_row_index(lesson.start_time)
                if row_index is None:
                    continue
                block = self._create_lesson_block(lesson)
                self.grid_layout.addWidget(block, row_index, day_index)
                self.lesson_blocks.append(block)
            except (ValueError, AttributeError):
                continue

    def _update_background(self):
        # Remove old background
        self.background.setParent(None)
        # Create new one with updated dimensions
        self.background = GridBackground(
            self.HOURS,
            self.days,
            time_slot_height=self.time_slot_height,
            day_header_width=0
        )
        self.grid_layout.addWidget(
            self.background,
            0, 0,
            len(self.HOURS),
            len(self.days),
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

    def _clear_existing_blocks(self):
        for block in self.lesson_blocks:
            block.setParent(None)
        self.lesson_blocks.clear()

    def _create_day_mapping(self):
        reverse_mapping = {}
        for lang, days in self.DAY_TRANSLATIONS.items():
            for idx, day in enumerate(days):
                normalized_day = day.lower().strip()
                if normalized_day not in reverse_mapping:
                    reverse_mapping[normalized_day] = idx
        return reverse_mapping

    def _get_time_row_index(self, time_str):
        if not time_str or ":" not in time_str:
            return None

        hour = time_str.split(":")[0].zfill(2) + ":00"
        try:
            return self.HOURS.index(hour)
        except ValueError:
            return None

    def _create_lesson_block(self, lesson):
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
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header_scroll_area = QScrollArea()
        self.header_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.header_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.header_scroll_area.setWidgetResizable(True)
        self.header_scroll_area.setFixedHeight(80)

        self.header_frame = QWidget()
        self.header_frame.setStyleSheet("""
            background-color: #2b2b2b;
            border-bottom: 1px solid #3a3a3a;
        """)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        for day in self.days:
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedWidth(200)
            label.setStyleSheet("""
                font-weight: bold;
                font-size: 16px;
                color: white;
            """)
            header_layout.addWidget(label)

        self.header_scroll_area.setWidget(self.header_frame)
        layout.addWidget(self.header_scroll_area)

        # Schedule view
        self.schedule_view = ScheduleView()
        self.schedule_view.set_header_scroll_area(self.header_scroll_area)
        layout.addWidget(self.schedule_view)

    @property
    def days(self):
        return [
            tr("app.days.monday"),
            tr("app.days.tuesday"),
            tr("app.days.wednesday"),
            tr("app.days.thursday"),
            tr("app.days.friday"),
            tr("app.days.saturday"),
            tr("app.days.sunday")
        ]

    def set_lessons(self, lessons):
        self.schedule_view.set_lessons(lessons)

    def refresh_translation(self):
        # Update day headers
        for i, day in enumerate(self.days):
            label = self.header_frame.layout().itemAt(i).widget()
            if isinstance(label, QLabel):
                label.setText(day)

        app_signals.render_lessons.emit()
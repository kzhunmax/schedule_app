from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QScrollArea,
    QGridLayout, QWidget, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.language import tr
from src.signals import app_signals
from src.ui.lesson_dialog import LessonDialog

class GridBackground(QWidget):
    def __init__(self, time_slots: list, days: list,
                 time_slot_height: int = 20,  # Adjusted for 5-minute slots
                 day_header_width: int = 100,
                 parent=None):
        super().__init__(parent)
        self.time_slots = time_slots
        self.days = days
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self._setup_initial_size()

    def _setup_initial_size(self) -> None:
        min_width = len(self.days) * 200
        min_height = len(self.time_slots) * self.time_slot_height
        self.setMinimumSize(min_width, min_height)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setPen(QColor("#3a3a3a"))
        width = self.width()
        height = self.height()
        day_width = width // len(self.days) if len(self.days) > 0 else 0

        # Horizontal lines (only for full hours)
        for i, time_slot in enumerate(self.time_slots):
            if time_slot.endswith(":00"):  # Draw lines only for full hours
                y = i * self.time_slot_height
                painter.drawLine(0, y, width, y)

        # Vertical lines (days)
        for i in range(len(self.days) + 1):
            x = i * day_width
            painter.drawLine(x, 0, x, height)

class TimeColumn(QWidget):
    def __init__(self, time_slots, time_slot_height=20, day_header_width=100):  # Adjusted height
        super().__init__()
        self.time_slots = time_slots
        self.time_slot_height = time_slot_height
        self.day_header_width = day_header_width
        self.setFixedWidth(day_header_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(len(time_slots) * time_slot_height)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw right border with gray color
        painter.setPen(QColor("#3a3a3a"))  # Сіра лінія
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        # Draw time labels with white color
        painter.setPen(QColor("#ffffff"))  # Білий текст
        for i, time_slot in enumerate(self.time_slots):
            if time_slot.endswith(":00"):  # Show labels only for full hours
                y = i * self.time_slot_height
                painter.drawText(0, y + self.time_slot_height // 2, self.width(), self.time_slot_height,
                                 Qt.AlignmentFlag.AlignCenter, time_slot)

class ScheduleView(QWidget):
    # Signal to request lesson edit
    lesson_edit_requested = pyqtSignal(object)

    # Create time slots for every 5 minutes from 01:00 to 23:55
    TIME_SLOTS = []
    for hour in range(0, 23):
        for minute in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
            TIME_SLOTS.append(f"{hour:02d}:{minute:02d}")

    DAY_TRANSLATIONS = {
        'en': ["monday", "tuesday", "wednesday", "thursday", "friday"],
        'uk': ["понеділок", "вівторок", "середа", "четвер", "п'ятниця"],
        'pl': ["poniedziałek", "wtorek", "środa", "czwartek", "piątek"]
    }

    def __init__(self, time_slot_height=20, day_header_width=100, min_day_width=210):  # Adjusted height
        super().__init__()
        app_signals.render_lessons.connect(self._render_lessons)
        app_signals.lesson_updated.connect(self._handle_lesson_updated)
        app_signals.lesson_deleted.connect(self._handle_lesson_deleted)
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
            tr("app.days.friday")
        ]

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Time column
        self.time_column = TimeColumn(self.TIME_SLOTS, self.time_slot_height, self.day_header_width)
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
            self.TIME_SLOTS,
            self.days,
            time_slot_height=self.time_slot_height,
            day_header_width=0
        )
        self.grid_layout.addWidget(
            self.background,
            0, 0,
            len(self.TIME_SLOTS),
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
        min_height = len(self.TIME_SLOTS) * self.time_slot_height
        self.content_widget.setMinimumSize(min_width, min_height)

    def set_lessons(self, lessons):
        self.lessons = lessons
        self._render_lessons()

    def _render_lessons(self):
        self._clear_existing_blocks()
        self._update_background()
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
                # Connect block click to edit handler
                block.lesson_clicked.connect(self._handle_lesson_block_clicked)
                # Span rows based on duration
                row_span = self._calculate_row_span(lesson.start_time, lesson.end_time)
                self.grid_layout.addWidget(block, row_index, day_index, row_span, 1)
                self.lesson_blocks.append(block)
            except (ValueError, AttributeError):
                continue

    def _update_background(self):
        self.background.setParent(None)
        self.background = GridBackground(
            self.TIME_SLOTS,
            self.days,
            time_slot_height=self.time_slot_height,
            day_header_width=0
        )
        self.grid_layout.addWidget(
            self.background,
            0, 0,
            len(self.TIME_SLOTS),
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

        try:
            hour, minute = map(int, time_str.split(":"))
            time_str_formatted = f"{hour:02d}:{minute:02d}"
            return self.TIME_SLOTS.index(time_str_formatted)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _calculate_row_span(start_time, end_time):
        try:
            start_h, start_m = map(int, start_time.split(':'))
            end_h, end_m = map(int, end_time.split(':'))
            start_total = start_h * 60 + start_m
            end_total = end_h * 60 + end_m
            duration_minutes = end_total - start_total
            row_span = max(1, duration_minutes // 5)
            return row_span
        except (ValueError, AttributeError):
            return 1

    def _create_lesson_block(self, lesson):
        block = ScheduleBlock(lesson)
        block.setFixedWidth(self.min_day_width - 10)

        try:
            row_span = self._calculate_row_span(lesson.start_time, lesson.end_time)
            min_height = row_span * self.time_slot_height
            block.setMinimumHeight(max(30, min_height))
            block.setMaximumHeight(min_height)
        except (ValueError, AttributeError):
            block.setMinimumHeight(30)

        return block

    def _handle_lesson_block_clicked(self, lesson):
        """Відкриває діалог редагування для вибраного уроку."""
        dialog = LessonDialog(lesson=lesson, edit_mode=True, parent=self)
        dialog.exec()

    def _handle_lesson_updated(self, lesson):
        """Оновлює урок у списку та перемальовує розклад."""
        for i, existing_lesson in enumerate(self.lessons):
            if existing_lesson.id == lesson.id:
                self.lessons[i] = lesson
                break
        else:
            self.lessons.append(lesson)
        self._render_lessons()

    def _handle_lesson_deleted(self, lesson_id):
        """Видаляє урок зі списку та перемальовує розклад."""
        self.lessons = [lesson for lesson in self.lessons if lesson.id != lesson_id]
        self._render_lessons()

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
        header_layout.setContentsMargins(100, 0, 100, 0)
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
            tr("app.days.friday")
        ]

    def set_lessons(self, lessons):
        self.schedule_view.set_lessons(lessons)

    def refresh_translation(self):
        for i, day in enumerate(self.days):
            label = self.header_frame.layout().itemAt(i).widget()
            if isinstance(label, QLabel):
                label.setText(day)

        app_signals.render_lessons.emit()

class ScrollSyncManager:
    def __init__(self, main_scroll, time_scroll=None, header_scroll=None):
        self.main_scroll = main_scroll
        if time_scroll:
            main_scroll.verticalScrollBar().valueChanged.connect(time_scroll.verticalScrollBar().setValue)
            time_scroll.verticalScrollBar().valueChanged.connect(main_scroll.verticalScrollBar().setValue)
            time_scroll.horizontalScrollBar().setEnabled(False)
        if header_scroll:
            main_scroll.horizontalScrollBar().valueChanged.connect(header_scroll.horizontalScrollBar().setValue)
            header_scroll.horizontalScrollBar().valueChanged.connect(main_scroll.horizontalScrollBar().setValue)

class ScheduleBlock(QFrame):
    # Signal emitted when the block is clicked
    lesson_clicked = pyqtSignal(object)

    def __init__(self, lesson):
        super().__init__()
        self.lesson = lesson
        self.setMouseTracking(True)  # Enable mouse tracking for click events
        self._setup_ui()

    def _setup_ui(self) -> None:
        self._apply_styles()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        subject_label = QLabel(self.lesson.subject)
        subject_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        subject_label.setWordWrap(True)

        time_text = self._format_time_text()
        time_label = QLabel(time_text)
        time_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.labels = {
            'subject': subject_label,
            'time': time_label
        }

        layout.addWidget(subject_label)
        layout.addWidget(time_label)

        self.block_layout = layout
        self.setLayout(layout)

    def mousePressEvent(self, event):
        """Обробляє клік на блоці уроку."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.lesson_clicked.emit(self.lesson)
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_content_visibility()

    def _update_content_visibility(self):
        required_height = 100

        if self.height() >= required_height:
            if 'type' not in self.labels:
                type_text = self._format_type_text()
                if type_text:
                    type_label = QLabel(type_text)
                    type_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                    self.labels['type'] = type_label
                    self.block_layout.insertWidget(2, type_label)

            if 'room' not in self.labels:
                room_text = self._format_room_text()
                if room_text:
                    room_label = QLabel(room_text)
                    room_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                    self.labels['room'] = room_label
                    self.block_layout.insertWidget(3, room_label)
        else:
            for key in ['type', 'room']:
                if key in self.labels:
                    self.labels[key].hide()
                    self.block_layout.removeWidget(self.labels[key])
                    self.labels[key].deleteLater()
                    del self.labels[key]

        self._apply_text_styles()

    def _apply_styles(self) -> None:
        hex_color = self.lesson.color if hasattr(self.lesson, 'color') and self.lesson.color else "#3a3a3a"
        rgb_color = tuple(int(hex_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
        rgba_background = f"rgba({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, 0.1)"

        self.setStyleSheet(f"""
            ScheduleBlock {{
                background-color: {rgba_background};
                border: 2px solid {hex_color};
                border-radius: 4px;
                margin: 2px;
            }}
            ScheduleBlock:hover {{
                background-color: {rgba_background.replace('0.1', '0.2')};
            }}
        """)

    def _apply_text_styles(self):
        hex_color = self.lesson.color if hasattr(self.lesson, 'color') and self.lesson.color else "#3a3a3a"
        base_font_size = max(8, min(14, self.height() // 5))

        for label in self.labels.values():
            if isinstance(label, QLabel):
                font_size = base_font_size
                if label is self.labels.get('subject'):
                    font_size = min(16, base_font_size + 2)

                label.setStyleSheet(f"""
                    QLabel {{
                        font-size: {font_size}px;
                        color: {hex_color};
                        background-color: transparent;
                        margin: 0;
                        padding: 0;
                    }}
                """)
                if label is self.labels.get('subject'):
                    label.setStyleSheet(label.styleSheet() + "font-weight: bold;")

    def _format_time_text(self) -> str:
        start_time = self.lesson.start_time if hasattr(self.lesson, 'start_time') and self.lesson.start_time else ""
        end_time = self.lesson.end_time if hasattr(self.lesson, 'end_time') and self.lesson.end_time else ""
        if start_time and end_time:
            return f"{start_time} - {end_time}"
        return ""

    def _format_type_text(self) -> str:
        if hasattr(self.lesson, 'type') and self.lesson.type:
            return self.lesson.type
        return ""

    def _format_room_text(self) -> str:
        room = self.lesson.room if hasattr(self.lesson, 'room') and self.lesson.room else ""
        return room
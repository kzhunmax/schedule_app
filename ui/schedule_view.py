from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
                             QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from models import Lesson


class ScheduleBlock(QFrame):
    COLOR_MAP = {
        "Lecture": "#007acc",
        "Seminar": "#28a745",
        "Lab": "#e83e8c",
        "Online": "#6f42c1",
        "Offline": "#fd7e14",
        "Default": "#6c757d"
    }

    def __init__(self, lesson: Lesson):
        super().__init__()
        self.lesson = lesson
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        title = QLabel(f"{self.lesson.subject}")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        time_range = f"{self.lesson.start_time} - {self.lesson.end_time}"
        subtitle = QLabel(f"{time_range} | {self.lesson.type} | Room {self.lesson.room}")
        subtitle.setFont(QFont("Segoe UI", 9))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.setLayout(layout)

        # Set background color
        bg_color = self.COLOR_MAP.get(self.lesson.type, self.COLOR_MAP["Default"])
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                color: white;
                border-radius: 10px;
                padding: 5px;
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)

        # Height based on duration
        duration_minutes = self._estimate_duration(self.lesson.start_time, self.lesson.end_time)
        height = max(60, min(200, duration_minutes))  # More reasonable size range
        self.setFixedHeight(height)

    def _estimate_duration(self, start_time, end_time):
        try:
            h1, m1 = map(int, start_time.strip().split(":"))
            h2, m2 = map(int, end_time.strip().split(":"))
            return (h2 - h1) * 60 + (m2 - m1)
        except Exception:
            return 60


class ScheduleView(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Add a placeholder when empty
        self.placeholder = QLabel("No lessons scheduled")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: gray; font-size: 16px;")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(15, 15, 15, 15)

        # Add placeholder initially
        self.content_layout.addWidget(self.placeholder)
        self.content_widget.setLayout(self.content_layout)
        self.setWidget(self.content_widget)

        self.lessons = []

    def set_lessons(self, lessons):
        # Sort lessons by start_time
        self.lessons = sorted(lessons, key=lambda x: x.start_time)
        self._render()

    def _render(self):
        # Clear current layout
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not self.lessons:
            self.content_layout.addWidget(self.placeholder)
        else:
            for lesson in self.lessons:
                block = ScheduleBlock(lesson)
                self.content_layout.addWidget(block)
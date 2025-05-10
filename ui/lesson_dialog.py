from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QHBoxLayout
)
from models import Lesson


class LessonDialog(QDialog):
    def __init__(self, lesson=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Lesson")
        self.lesson = lesson or Lesson()

        layout = QVBoxLayout()

        # Day of the week
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        if self.lesson.day:
            self.day_combo.setCurrentText(self.lesson.day)

        # Subject
        self.subject_input = QLineEdit(self.lesson.subject)

        # Start time
        self.start_time_input = QLineEdit(self.lesson.start_time)
        self.start_time_input.setPlaceholderText("e.g. 09:00")

        # End time
        self.end_time_input = QLineEdit(self.lesson.end_time)
        self.end_time_input.setPlaceholderText("e.g. 10:30")

        # Type (online/offline)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Online", "Offline"])
        if self.lesson.type in ["Online", "Offline"]:
            self.type_combo.setCurrentText(self.lesson.type)
        else:
            self.type_combo.setCurrentIndex(0)

        # Room
        self.room_input = QLineEdit(self.lesson.room)

        # Layout widgets
        layout.addWidget(QLabel("Day:"))
        layout.addWidget(self.day_combo)
        layout.addWidget(QLabel("Subject:"))
        layout.addWidget(self.subject_input)
        layout.addWidget(QLabel("Start Time:"))
        layout.addWidget(self.start_time_input)
        layout.addWidget(QLabel("End Time:"))
        layout.addWidget(self.end_time_input)
        layout.addWidget(QLabel("Type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Room:"))
        layout.addWidget(self.room_input)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        return Lesson(
            day=self.day_combo.currentText(),
            subject=self.subject_input.text(),
            start_time=self.start_time_input.text(),
            end_time=self.end_time_input.text(),
            lesson_type=self.type_combo.currentText(),
            room=self.room_input.text()
        )

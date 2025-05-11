from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

from language import tr


class TimePickerDialog(QDialog):
    def __init__(self, current_time="09:00", parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("app.time_dialog.title"))
        self.time = current_time

        layout = QVBoxLayout(self)
        time_layout = QHBoxLayout()

        self.setFixedSize(200, 100)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 5, 10, 10)

        # Години та хвилини
        self.hour_combo = QComboBox()
        self.minute_combo = QComboBox()

        for h in range(0, 24):
            self.hour_combo.addItem(f"{h:02d}")
        for m in range(0, 60, 5):
            self.minute_combo.addItem(f"{m:02d}")

        if ":" in current_time:
            hour, minute = current_time.split(":")
            self.hour_combo.setCurrentText(hour.zfill(2))
            self.minute_combo.setCurrentText(minute.zfill(2))

        colon_label = QLabel(":")
        colon_label.setFixedSize(30, 30)
        colon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        time_layout.addWidget(self.hour_combo)
        time_layout.addWidget(colon_label)
        time_layout.addWidget(self.minute_combo)

        layout.addLayout(time_layout)

        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton(tr("app.time_dialog.save"))
        self.cancel_btn = QPushButton(tr("app.time_dialog.cancel"))

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_time(self):
        hour = self.hour_combo.currentText()
        minute = self.minute_combo.currentText()
        return f"{hour}:{minute}"
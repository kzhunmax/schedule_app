from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QComboBox, QFrame, QButtonGroup, QMessageBox
)
from models import Lesson
from language import tr
from ui.time_picker_dialog import TimePickerDialog


class LessonDialog(QDialog):
    COLORS = ["#00a7e5", "#14142b", "#e40173", "#6308f7", "#ff7f08", "#44d6df", "#b1cb49"]

    def __init__(self, lesson=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("app.lesson_dialog.title"))
        self.lesson = lesson or Lesson()
        self.setMinimumSize(400, 650)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 10, 20, 20)

        # Day of the week
        self.day_combo = QComboBox()
        self.day_combo.addItems([
            tr("app.days.monday"),
            tr("app.days.tuesday"),
            tr("app.days.wednesday"),
            tr("app.days.thursday"),
            tr("app.days.friday")
        ])
        if self.lesson.day:
            self.day_combo.setCurrentText(tr(f"app.days.{self.lesson.day.lower()}"))

        # Subject - no restrictions on language
        self.subject_input = QLineEdit(self.lesson.subject)

        # Type: Online / Offline (кнопки з вибором)
        self.online_btn = QPushButton(tr("app.lesson_dialog.type_online"))
        self.offline_btn = QPushButton(tr("app.lesson_dialog.type_offline"))

        for btn in [self.online_btn, self.offline_btn]:
            btn.setObjectName("optionButton")
            btn.setCheckable(True)

        # --- Додаємо групу для ексклюзивного вибору ---
        self.type_button_group = QFrame()
        self.type_button_group_layout = QHBoxLayout()

        # Створюємо групу кнопок
        self.option_group = QButtonGroup(self)
        self.option_group.addButton(self.online_btn)
        self.option_group.addButton(self.offline_btn)
        self.option_group.setExclusive(True)

        if self.lesson.type == "Online":
            self.online_btn.setChecked(True)
        elif self.lesson.type == "Offline":
            self.offline_btn.setChecked(True)
        else:
            self.online_btn.setChecked(True)

        # Додаємо кнопки в layout
        self.type_button_group_layout.addWidget(self.online_btn)
        self.type_button_group_layout.addWidget(self.offline_btn)
        self.type_button_group.setLayout(self.type_button_group_layout)

        # Room
        self.room_input = QLineEdit(self.lesson.room)

        # Start time
        self.start_time_input = QLineEdit(self.lesson.start_time)
        self.pick_start_time_btn = QPushButton("...")
        self.start_time_input.setPlaceholderText(tr("app.lesson_dialog.time_placeholder"))
        self.pick_start_time_btn.setFixedSize(30, 30)
        self.pick_start_time_btn.clicked.connect(self.pick_start_time)

        # End time
        self.end_time_input = QLineEdit(self.lesson.end_time)
        self.pick_end_time_btn = QPushButton("...")
        self.end_time_input.setPlaceholderText(tr("app.lesson_dialog.time_placeholder"))
        self.pick_end_time_btn.setFixedSize(30, 30)
        self.pick_end_time_btn.clicked.connect(self.pick_end_time)

        # Layout widgets
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_day")))
        layout.addWidget(self.day_combo)
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_subject")))
        layout.addWidget(self.subject_input)
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_start_time")))
        start_time_layout = QHBoxLayout()
        start_time_layout.addWidget(self.start_time_input)
        start_time_layout.addWidget(self.pick_start_time_btn)
        layout.addLayout(start_time_layout)
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_end_time")))
        end_time_layout = QHBoxLayout()
        end_time_layout.addWidget(self.end_time_input)
        end_time_layout.addWidget(self.pick_end_time_btn)
        layout.addLayout(end_time_layout)
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_type")))
        layout.addWidget(self.type_button_group)
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_room")))
        layout.addWidget(self.room_input)

        # --- Вибір кольору ---
        layout.addWidget(QLabel(tr("app.lesson_dialog.label_color")))

        self.color_button_group = QButtonGroup(self)
        self.color_button_group.setExclusive(True)

        color_layout = QHBoxLayout()
        for color in self.COLORS:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    width: 30px;
                    height: 30px;
                    border-radius: 15px;
                    background-color: rgba({self.hex_to_rgba(color, opacity=0.2)});
                    border: 2px solid {color};
                }}
                QPushButton:checked {{
                    background-color: {color};
                }}
            """)
            btn.setCheckable(True)
            btn.setToolTip(color)
            self.color_button_group.addButton(btn)
            color_layout.addWidget(btn)

        layout.addLayout(color_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(tr("app.lesson_dialog.save"))
        cancel_btn = QPushButton(tr("app.lesson_dialog.cancel"))
        save_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.update_color_buttons()

    @staticmethod
    def hex_to_rgba(hex_color, opacity=1.0):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}, {opacity}"

    def pick_start_time(self):
        dialog = TimePickerDialog(self.start_time_input.text(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.start_time_input.setText(dialog.get_time())

    def pick_end_time(self):
        dialog = TimePickerDialog(self.end_time_input.text(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.end_time_input.setText(dialog.get_time())

    def update_color_buttons(self):
        for button in self.color_button_group.buttons():
            if button.toolTip() == self.lesson.color:
                button.setChecked(True)
                break
        else:
            self.color_button_group.buttons()[0].setChecked(True)

    def validate_and_accept(self):
        """Validate inputs before accepting the dialog"""
        # Отримуємо та нормалізуємо час
        start_time = self.normalize_time(self.start_time_input.text().strip())
        end_time = self.normalize_time(self.end_time_input.text().strip())

        subject = self.subject_input.text().strip()

        # Оновлюємо поля вводу з нормалізованим часом
        self.start_time_input.setText(start_time)
        self.end_time_input.setText(end_time)

        # Перевірка на пусте поле предмету
        if not subject:
            self.parent().show_notification(tr("app.lesson_dialog.error_empty_subject"))
            return

        # Check if times are empty
        if not start_time or not end_time:
            self.parent().show_notification(tr("app.lesson_dialog.error_time_required"))
            return

        # Validate time formats
        if not self.validate_time_format(start_time):
            self.parent().show_notification(tr("app.lesson_dialog.error_invalid_start_time"))
            return

        if not self.validate_time_format(end_time):
            self.parent().show_notification(tr("app.lesson_dialog.error_invalid_end_time"))
            return

        # Check if start time equals end time
        if start_time == end_time:
            self.parent().show_notification(tr("app.lesson_dialog.error_same_times"))
            return

        # Check if end time is before start time
        if self.time_to_minutes(end_time) <= self.time_to_minutes(start_time):
            self.parent().show_notification(tr("app.lesson_dialog.error_end_before_start"))
            return

        # If all validations pass, accept the dialog
        self.accept()

    def normalize_time(self, time_str):
        """Додає ведучі нулі до часу (9:00 -> 09:00)"""
        if not time_str or ':' not in time_str:
            return time_str

        hours, minutes = time_str.split(':')
        return f"{hours.zfill(2)}:{minutes.zfill(2)}"

    def time_to_minutes(self, time_str):
        """Конвертує час у форматі HH:MM у кількість хвилин"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def validate_time_format(self, time_str):
        """Validate time format (HH:MM)"""
        if not time_str:
            return False

        # Перевіряємо чи є рівно одна двокрапка
        if time_str.count(':') != 1:
            return False

        hours, minutes = time_str.split(':')

        # Перевіряємо чи є ведучий нуль для годин < 10
        if len(hours) < 2 or (hours[0] == '0' and len(hours) > 2):
            return False

        # Перевіряємо чи є ведучий нуль для хвилин < 10
        if len(minutes) != 2:
            return False

        try:
            hours_int = int(hours)
            minutes_int = int(minutes)
            return 0 <= hours_int <= 23 and 0 <= minutes_int <= 59
        except ValueError:
            return False

    def get_data(self):
        selected_button = self.color_button_group.checkedButton()
        self.selected_color = selected_button.toolTip() if selected_button else "#00a7e5"

        selected_type = self.option_group.checkedButton()
        lesson_type = "Online" if selected_type == self.online_btn else "Offline"

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
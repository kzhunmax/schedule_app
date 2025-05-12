from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer, QPropertyAnimation
from PyQt6.QtCore import Qt


class Notification(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # --- Сповіщення всередині ---
        self.content = QLabel()
        self.content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content.setWordWrap(True)
        self.content.setStyleSheet("""
            background-color: #2c2c2c;
            color: white;
            font-family: "Segoe UI";
            font-size: 14px;
            border-radius: 8px;
            padding: 10px 15px;
        """)
        self.content.setFixedWidth(300)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content)
        self.setLayout(layout)

        # --- Налаштування анімації ---
        self.anim_duration = 300
        self.show_duration = 3000
        self.parent_widget = parent

        self.animation_in = None
        self.animation_out = None

    def show_message(self, message, success=False, duration=3000):
        # Оновлюємо колір фону
        bg_color = "#2ecc71" if success else "#e74c3c"
        self.content.setStyleSheet(f"""
            background-color: {bg_color};
            color: white;
            font-family: 'Segoe UI';
            font-size: 14px;
            border-radius: 8px;
            padding: 10px 15px;
        """)

        self.content.setText(message)
        self.content.adjustSize()

        new_height = self.content.sizeHint().height() + 20
        self.setFixedHeight(new_height)
        self.resize(self.width(), new_height)

        self.setup_position()

        # --- Анімація появи ---
        from PyQt6.QtCore import QPropertyAnimation

        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        self.animation_in = QPropertyAnimation(self, b"windowOpacity")
        self.animation_in.setDuration(self.anim_duration)
        self.animation_in.setStartValue(0.0)
        self.animation_in.setEndValue(1.0)

        # --- Анімація зникнення ---
        self.animation_out = QPropertyAnimation(self, b"windowOpacity")
        self.animation_out.setDuration(self.anim_duration)
        self.animation_out.setStartValue(1.0)
        self.animation_out.setEndValue(0.0)
        self.animation_out.finished.connect(self.hide)

        self.animation_in.start()
        QTimer.singleShot(duration, lambda: self.animation_out.start())

    def setup_position(self):
        if self.parent_widget:
            x = self.parent_widget.x() + (self.parent_widget.width() - self.width()) // 2
            y = self.parent_widget.y() + 20
            self.move(x, y)

    def hide(self):
        if self.animation_in and self.animation_in.state() == QPropertyAnimation.State.Running:
            self.animation_in.stop()
        super().hide()
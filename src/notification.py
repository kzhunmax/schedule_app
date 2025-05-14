from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import QTimer, QPropertyAnimation, Qt


class Notification(QWidget):
    """
    Віджет для показу короткочасних сповіщень.

    Attributes:
        parent_widget (QWidget): Батьківський віджет для позиціонування.
        anim_duration (int): Тривалість анімації появи/зникнення (у мс).
        show_duration (int): Тривалість показу повідомлення (у мс).
    """

    def __init__(self, parent=None):
        """Ініціалізація віджета сповіщення.

        Args:
            parent (QWidget): Батьківський віджет для прив'язки.
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # --- Налаштування контенту ---
        self.content = QLabel()
        self.content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content.setWordWrap(True)
        self.content.setStyleSheet(self._default_stylesheet())

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content)
        self.setLayout(layout)

        # --- Анімація ---
        self.anim_duration = 300
        self.show_duration = 3000
        self.parent_widget = parent

        self.animation_in = None
        self.animation_out = None

    @staticmethod
    def _default_stylesheet() -> str:
        """Повертає стиль за замовчуванням."""
        return """
            background-color: #2c2c2c;
            color: white;
            font-family: 'Segoe UI';
            font-size: 14px;
            border-radius: 8px;
            padding: 10px 15px;
        """

    def show_message(self, message: str, success: bool = False, duration: int = 3000) -> None:
        """
        Показує сповіщення з можливістю налаштування кольору та тривалості.

        Args:
            message (str): Текст сповіщення.
            success (bool): Якщо True — зелений фон, інакше червоний.
            duration (int): Тривалість показу в мілісекундах.
        """
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

        self.adjustSize()
        QApplication.processEvents()

        self.setup_position()
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        # Анімація появи
        self.animation_in = QPropertyAnimation(self, b"windowOpacity")
        self.animation_in.setDuration(self.anim_duration)
        self.animation_in.setStartValue(0.0)
        self.animation_in.setEndValue(1.0)

        # Анімація зникнення
        self.animation_out = QPropertyAnimation(self, b"windowOpacity")
        self.animation_out.setDuration(self.anim_duration)
        self.animation_out.setStartValue(1.0)
        self.animation_out.setEndValue(0.0)
        self.animation_out.finished.connect(self.hide)

        self.animation_in.start()
        QTimer.singleShot(duration, lambda: self.animation_out.start())

    def setup_position(self) -> None:
        """Налаштовує позицію сповіщення відносно батька."""
        if self.parent_widget:
            x = self.parent_widget.x() + (self.parent_widget.width() - self.width()) // 2
            y = self.parent_widget.y() + 20
            self.move(x, y)

    def hide(self) -> None:
        """Зупиняє анімацію приховання."""
        if self.animation_in and self.animation_in.state() == QPropertyAnimation.State.Running:
            self.animation_in.stop()
        super().hide()
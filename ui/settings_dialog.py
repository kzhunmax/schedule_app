from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QStackedWidget, QListWidget,
    QListWidgetItem, QWidget, QCheckBox
)
from PyQt6.QtGui import QIcon
from settings import save_theme, load_theme, save_language, load_language, save_notifications, load_notifications


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon("images/icons/cil-settings.png"))
        self.setMinimumSize(600, 400)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left panel
        nav_list = QListWidget()
        nav_list.setFixedWidth(150)
        nav_list.addItem(QListWidgetItem("Theme"))
        nav_list.addItem(QListWidgetItem("Language"))
        nav_list.addItem(QListWidgetItem("Notifications"))

        # Контент вкладок
        self.pages = QStackedWidget()

        # 1. Вкладка Тема
        page1 = QWidget()
        page1_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        if load_theme() == "light_theme":
            self.theme_combo.setCurrentText("Light")
        else:
            self.theme_combo.setCurrentText("Dark")
        self.theme_combo.currentIndexChanged.connect(self.save_current_theme)
        page1_layout.addWidget(QLabel("Choose theme:"))
        page1_layout.addWidget(self.theme_combo)
        page1.setLayout(page1_layout)

        # 2. Вкладка Мова
        page2 = QWidget()
        page2_layout = QVBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Українська", "English"])
        if load_language() == "uk":
            self.lang_combo.setCurrentText("Українська")
        else:
            self.lang_combo.setCurrentText("English")
        self.lang_combo.currentIndexChanged.connect(self.save_current_language)
        page2_layout.addWidget(QLabel("Choose language:"))
        page2_layout.addWidget(self.lang_combo)
        page2.setLayout(page2_layout)

        # 3. Вкладка Сповіщення
        page3 = QWidget()
        page3_layout = QVBoxLayout()
        self.notifications_checkbox = QCheckBox("Enable notifications")
        self.notifications_checkbox.setChecked(load_notifications())
        self.notifications_checkbox.toggled.connect(self.save_notification_state)
        page3_layout.addWidget(self.notifications_checkbox)
        page3.setLayout(page3_layout)

        # Додавання сторінок
        self.pages.addWidget(page1)
        self.pages.addWidget(page2)
        self.pages.addWidget(page3)

        # Підключення перемикання сторінок
        nav_list.currentRowChanged.connect(self.pages.setCurrentIndex)

        # Кнопки
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        # Комбінований інтерфейс
        layout.addWidget(nav_list)
        layout.addWidget(self.pages, stretch=1)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def save_current_theme(self):
        selected = self.theme_combo.currentText()
        new_theme = "dark_theme" if selected == "Dark" else "light_theme"
        save_theme(new_theme)
        self.parent.load_current_theme()
        self.parent.update_theme_button_icon()

    def save_current_language(self):
        selected = self.lang_combo.currentText()
        lang_code = "uk" if selected == "Українська" else "en"
        save_language(lang_code)

    @staticmethod
    def save_notification_state(state):
        save_notifications(state)
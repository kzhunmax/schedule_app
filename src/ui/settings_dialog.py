"""
Діалогове вікно налаштувань додатку.

Містить налаштування:
- Теми інтерфейсу (світла/темна)
- Мови інтерфейсу (англійська, українська, польська)
- Режиму відображення розкладу (день/тиждень)
- Сповіщень (включити/виключити)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QButtonGroup, QFrame
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.language import tr
from src.signals import app_signals
from src.settings import (
    save_language, save_view_mode,
    save_notifications, save_theme,
    load_notifications, load_language,
    load_view_mode, load_theme
)


class SettingsDialog(QDialog):
    """Клас діалогового вікна налаштувань."""

    # Константи класу
    MIN_WIDTH = 400
    MIN_HEIGHT = 450
    ICON_PATH = "src/images/icons/settings-dark.png"
    LANGUAGES = {
        "en": "English",
        "ukr": "Українська",
        "pl": "Polski"
    }

    def __init__(self, parent=None):
        """Ініціалізація діалогового вікна.

        Args:
            parent: Батьківський віджет
        """
        super().__init__(parent)
        self.parent = parent
        self._init_ui()

    def _init_ui(self) -> None:
        """Ініціалізація інтерфейсу користувача."""
        self.setWindowTitle(tr("app.settings.title"))
        self.setWindowIcon(QIcon(self.ICON_PATH))
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 10, 20, 20)
        self.setLayout(layout)

        # Додаємо секції налаштувань
        self._init_theme_section(layout)
        self._init_view_mode_section(layout)
        self._init_language_section(layout)
        self._init_notifications_section(layout)
        self._init_action_buttons(layout)

    def _init_theme_section(self, layout: QVBoxLayout) -> None:
        """Ініціалізує секцію вибору теми."""
        layout.addWidget(self._create_section_label(tr("app.settings.theme")))

        self.theme_dark_btn = self._create_option_button(tr("app.settings.dark"))
        self.theme_light_btn = self._create_option_button(tr("app.settings.light"))

        self.theme_group = self._create_button_group(
            [self.theme_dark_btn, self.theme_light_btn],
            "dark_theme" if load_theme() != "light_theme" else "light_theme"
        )

        theme_layout = QHBoxLayout()
        theme_layout.addWidget(self.theme_dark_btn)
        theme_layout.addWidget(self.theme_light_btn)
        layout.addLayout(theme_layout)

    def _init_view_mode_section(self, layout: QVBoxLayout) -> None:
        """Ініціалізує секцію вибору режиму перегляду."""
        layout.addWidget(self._create_section_label(tr("app.settings.view_mode")))

        self.view_daily_btn = self._create_option_button(tr("app.settings.daily"))
        self.view_weekly_btn = self._create_option_button(tr("app.settings.weekly"))

        current_view = load_view_mode()
        self.view_group = self._create_button_group(
            [self.view_daily_btn, self.view_weekly_btn],
            "weekly" if current_view == "weekly" else "daily"
        )

        view_layout = QHBoxLayout()
        view_layout.addWidget(self.view_daily_btn)
        view_layout.addWidget(self.view_weekly_btn)
        layout.addLayout(view_layout)

    def _init_language_section(self, layout: QVBoxLayout) -> None:
        """Ініціалізує секцію вибору мови."""
        layout.addWidget(self._create_section_label(tr("app.settings.language")))

        self.lang_btns = {}
        for code, name in self.LANGUAGES.items():
            self.lang_btns[code] = self._create_option_button(name)

        current_lang = load_language()
        self.lang_group = self._create_button_group(
            list(self.lang_btns.values()),
            current_lang if current_lang in self.LANGUAGES else "en"
        )

        lang_layout = QHBoxLayout()
        for btn in self.lang_btns.values():
            lang_layout.addWidget(btn)
        layout.addLayout(lang_layout)

    def _init_notifications_section(self, layout: QVBoxLayout) -> None:
        """Ініціалізує секцію налаштувань сповіщень."""
        layout.addWidget(self._create_section_label(tr("app.settings.notifications")))

        self.notif_yes_btn = self._create_option_button(tr("app.settings.yes"))
        self.notif_no_btn = self._create_option_button(tr("app.settings.no"))

        self.notif_group = self._create_button_group(
            [self.notif_yes_btn, self.notif_no_btn],
            "yes" if load_notifications() else "no"
        )

        notif_layout = QHBoxLayout()
        notif_layout.addWidget(self.notif_yes_btn)
        notif_layout.addWidget(self.notif_no_btn)
        layout.addLayout(notif_layout)

    def _init_action_buttons(self, layout: QVBoxLayout) -> None:
        """Ініціалізує кнопки дій."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = QPushButton(tr("app.settings.save"))
        self.cancel_btn = QPushButton(tr("app.settings.cancel"))

        self.save_btn.clicked.connect(self._handle_save)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    @staticmethod
    def _create_section_label(text: str) -> QLabel:
        """Створює заголовок секції.

        Args:
            text: Текст заголовка

        Returns:
            Віджет QLabel з оформленим текстом
        """
        label = QLabel(f"<b>{text}</b>")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return label

    @staticmethod
    def _create_option_button(text: str) -> QPushButton:
        """Створює кнопку вибору опції.

        Args:
            text: Текст кнопки

        Returns:
            Налаштований віджет QPushButton
        """
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setObjectName("optionButton")
        return btn

    def _create_button_group(self, buttons: list, active_value: str) -> QButtonGroup:
        """Створює групу кнопок з вибором однієї опції.

        Args:
            buttons: Список кнопок
            active_value: Значення активної кнопки (напр., "dark_theme", "en", "weekly", "yes")
        """
        group = QButtonGroup(self)

        for btn in buttons:
            group.addButton(btn)

            # Визначаємо, чи відповідає кнопка active_value
            btn_value = self._get_button_value(btn.text())
            if btn_value == active_value:
                btn.setChecked(True)

        group.setExclusive(True)
        return group

    def _get_button_value(self, button_text: str) -> str:
        """Повертає значення кнопки, яке можна порівняти з active_value."""
        # Для теми (кнопки "Dark" / "Light" → "dark_theme" / "light_theme")
        if button_text in [tr("app.settings.dark"), tr("app.settings.light")]:
            return "dark_theme" if button_text == tr("app.settings.dark") else "light_theme"

        # Для мови (кнопки "English", "Українська", "Polski" → "en", "ukr", "pl")
        for code, name in self.LANGUAGES.items():
            if button_text == name:
                return code

        # Для режиму перегляду ("Day" / "Week" → "daily" / "weekly")
        if button_text == tr("app.settings.daily"):
            return "daily"
        elif button_text == tr("app.settings.weekly"):
            return "weekly"

        # Для сповіщень ("Yes" / "No" → "yes" / "no")
        if button_text == tr("app.settings.yes"):
            return "yes"
        elif button_text == tr("app.settings.no"):
            return "no"

        return ""

    def _handle_save(self) -> None:
        """Обробляє збереження налаштувань."""
        self._save_settings()
        app_signals.show_notification.emit(tr("app.settings.saved"), True)
        super().accept()

    def _save_settings(self) -> None:
        """Зберігає всі налаштування."""
        self._save_theme()
        self._save_language()
        self._save_view_mode()
        self._save_notifications()

    def _save_theme(self) -> None:
        """Зберігає вибрану тему."""
        theme = "light_theme" if self.theme_light_btn.isChecked() else "dark_theme"
        save_theme(theme)
        app_signals.load_current_theme.emit()
        app_signals.update_all_button_icons.emit()

    def _save_language(self) -> None:
        """Зберігає вибрану мову."""
        lang_code = next(
            (code for code, btn in self.lang_btns.items() if btn.isChecked()),
            "en"
        )
        old_lang = load_language()
        if lang_code != old_lang:
            save_language(lang_code)
            app_signals.set_new_language.emit(lang_code)

    def _save_view_mode(self) -> None:
        """Зберігає вибраний режим перегляду."""
        view_mode = "weekly" if self.view_weekly_btn.isChecked() else "daily"
        save_view_mode(view_mode)

    def _save_notifications(self) -> None:
        """Зберігає налаштування сповіщень."""
        state = self.notif_yes_btn.isChecked()
        save_notifications(state)

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QButtonGroup, QFrame
)
from PyQt6.QtGui import QIcon

from language import tr
from settings import save_language, save_view_mode, save_notifications, save_theme, load_notifications, load_language, \
    load_view_mode, load_theme


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("app.settings.title"))
        self.setWindowIcon(QIcon("images/icons/settings-dark.png"))
        self.setMinimumSize(400, 450)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Theme Setting ---
        layout.addWidget(QLabel("<b>" + tr("app.settings.theme") + "</b>"))

        theme_btn_layout = QHBoxLayout()
        self.theme_dark_btn = QPushButton("Dark")
        self.theme_light_btn = QPushButton("Light")
        self.theme_dark_btn.setCheckable(True)
        self.theme_light_btn.setCheckable(True)
        self.theme_dark_btn.setObjectName("optionButton")
        self.theme_light_btn.setObjectName("optionButton")

        self.theme_group = QButtonGroup()
        self.theme_group.addButton(self.theme_dark_btn)
        self.theme_group.addButton(self.theme_light_btn)
        self.theme_group.setExclusive(True)

        if load_theme() == "light_theme":
            self.theme_light_btn.setChecked(True)
        else:
            self.theme_dark_btn.setChecked(True)

        theme_btn_layout.addWidget(self.theme_dark_btn)
        theme_btn_layout.addWidget(self.theme_light_btn)
        layout.addLayout(theme_btn_layout)

        # --- Schedule View Mode ---
        layout.addWidget(QLabel("<b>" + tr("app.settings.view_mode") + "</b>"))

        view_btn_layout = QHBoxLayout()
        self.view_daily_btn = QPushButton(tr("app.settings.daily"))
        self.view_weekly_btn = QPushButton(tr("app.settings.weekly"))
        for btn in [self.view_daily_btn, self.view_weekly_btn]:
            btn.setCheckable(True)
            btn.setObjectName("optionButton")

        self.view_group = QButtonGroup()
        self.view_group.addButton(self.view_daily_btn)
        self.view_group.addButton(self.view_weekly_btn)
        self.view_group.setExclusive(True)

        current_view = load_view_mode()
        if current_view == "weekly":
            self.view_weekly_btn.setChecked(True)
        else:
            self.view_daily_btn.setChecked(True)

        view_btn_layout.addWidget(self.view_daily_btn)
        view_btn_layout.addWidget(self.view_weekly_btn)
        layout.addLayout(view_btn_layout)

        # --- Language Setting ---
        layout.addWidget(QLabel("<b>" + tr("app.settings.language") + "</b>"))

        lang_btn_layout = QHBoxLayout()
        self.lang_ukr_btn = QPushButton("Українська")
        self.lang_en_btn = QPushButton("English")
        self.lang_pl_btn = QPushButton("Polski")
        self.lang_ukr_btn.setCheckable(True)
        self.lang_en_btn.setCheckable(True)
        self.lang_pl_btn.setCheckable(True)
        self.lang_ukr_btn.setObjectName("optionButton")
        self.lang_en_btn.setObjectName("optionButton")
        self.lang_pl_btn.setObjectName("optionButton")

        self.lang_group = QButtonGroup()
        self.lang_group.addButton(self.lang_ukr_btn)
        self.lang_group.addButton(self.lang_en_btn)
        self.lang_group.addButton(self.lang_pl_btn)
        self.lang_group.setExclusive(True)

        current_lang = load_language()
        if current_lang == "ukr":
            self.lang_ukr_btn.setChecked(True)
        elif current_lang == "pl":
            self.lang_pl_btn.setChecked(True)
        else:
            self.lang_en_btn.setChecked(True)

        lang_btn_layout.addWidget(self.lang_en_btn)
        lang_btn_layout.addWidget(self.lang_ukr_btn)
        lang_btn_layout.addWidget(self.lang_pl_btn)
        layout.addLayout(lang_btn_layout)

        # --- Notifications Setting ---
        layout.addWidget(QLabel("<b>" + tr("app.settings.notifications") + "</b>"))

        notif_btn_layout = QHBoxLayout()
        self.notif_yes_btn = QPushButton(tr("app.settings.yes"))
        self.notif_no_btn = QPushButton(tr("app.settings.no"))
        for btn in [self.notif_yes_btn, self.notif_no_btn]:
            btn.setCheckable(True)
            btn.setObjectName("optionButton")

        self.notif_group = QButtonGroup()
        self.notif_group.addButton(self.notif_yes_btn)
        self.notif_group.addButton(self.notif_no_btn)
        self.notif_group.setExclusive(True)

        if load_notifications():
            self.notif_yes_btn.setChecked(True)
        else:
            self.notif_no_btn.setChecked(True)

        notif_btn_layout.addWidget(self.notif_yes_btn)
        notif_btn_layout.addWidget(self.notif_no_btn)
        layout.addLayout(notif_btn_layout)

        # --- Divider Line ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(tr("app.settings.save"))
        cancel_btn = QPushButton(tr("app.settings.cancel"))
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def accept(self):
        self.save_settings()
        super().accept()

    def save_settings(self):
        # Save theme
        selected_theme = "dark_theme" if self.theme_dark_btn.isChecked() else "light_theme"
        save_theme(selected_theme)
        self.parent.load_current_theme()
        self.parent.update_all_button_icons()

        # Save language
        if self.lang_ukr_btn.isChecked():
            lang_code = "ukr"
        elif self.lang_pl_btn.isChecked():
            lang_code = "pl"
        else:
            lang_code = "en"

        old_lang = load_language()
        if lang_code != old_lang:
            save_language(lang_code)
            self.parent.set_new_language(lang_code)

        # Save view mode
        view_mode = "daily" if self.view_daily_btn.isChecked() else "weekly"
        save_view_mode(view_mode)

        # Save notifications
        state = self.notif_yes_btn.isChecked()
        save_notifications(state)
from PyQt6.QtCore import QSettings

SETTINGS = QSettings("MyUniversity", "SchedulePlanner")

def save_theme(theme_name):
    SETTINGS.setValue("app_theme", theme_name)

def load_theme():
    return SETTINGS.value("app_theme", "dark_theme")

def save_language(lang_code):
    SETTINGS.setValue("language", lang_code)

def load_language():
    return SETTINGS.value("language", "en")

def save_notifications(enabled):
    SETTINGS.setValue("notifications", enabled)

def load_notifications():
    return SETTINGS.value("notifications", True, type=bool)


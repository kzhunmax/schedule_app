from PyQt6.QtCore import QSettings

Settings = QSettings("MyUniversity", "SchedulePlanner")

def save_theme(theme_name):
    Settings.setValue("app_theme", theme_name)

def load_theme():
    return Settings.value("app_theme", "dark_theme")
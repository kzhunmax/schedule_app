from PyQt6.QtCore import pyqtSignal, QObject


class AppSignals(QObject):
    show_notification = pyqtSignal(str, bool)
    load_current_theme = pyqtSignal()
    update_all_button_icons = pyqtSignal()
    set_new_language = pyqtSignal(str)
    lessons_imported = pyqtSignal(list)
    render_lessons = pyqtSignal()


app_signals = AppSignals()

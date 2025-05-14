from PyQt6.QtCore import QSettings

# Глобальні налаштування
SETTINGS = QSettings("MyUniversity", "SchedulePlanner")


def save_theme(theme_name: str) -> None:
    """Зберігає тему інтерфейсу.

    Args:
        theme_name (str): Назва теми (наприклад 'dark_theme').
    """
    SETTINGS.setValue("app_theme", theme_name)


def load_theme() -> str:
    """Повертає збережену тему.

    Returns:
        str: Назва теми або 'dark_theme' за замовчуванням.
    """
    return str(SETTINGS.value("app_theme", "dark_theme"))


def save_language(lang_code: str) -> None:
    """Зберігає вирану користувачем мову.

    Args:
        lang_code (str): Код мови (наприклад 'en', 'ukr').
    """
    SETTINGS.setValue("language", lang_code)


def load_language() -> str:
    """Повертає збережений код мови.

    Returns:
        str: Код мови або 'en' за замовчуванням.
    """
    return str(SETTINGS.value("language", "en"))


def save_notifications(enabled: bool) -> None:
    """Зберігає стан сповіщень.

    Args:
        enabled (bool): True, якщо сповіщення увімкнені.
    """
    SETTINGS.setValue("notifications", enabled)


def load_notifications() -> bool:
    """Перевіряє, чи увімкнені сповіщення.

    Returns:
        bool: Стан сповіщень.
    """
    return bool(SETTINGS.value("notifications", True, type=bool))


def save_view_mode(mode: str) -> None:
    """Зберігає режим відображення розкладу.

    Args:
        mode (str): Режим ('daily', 'weekly' тощо).
    """
    SETTINGS.setValue("view_mode", mode)


def load_view_mode() -> str:
    """Повертає збережений режим відображення.

    Returns:
        str: Режим відображення.
    """
    return str(SETTINGS.value("view_mode", "daily"))

import json
from src.settings import load_language, save_language

_translations = {}


def load_translations() -> None:
    """Завантажує мовні файли відповідно до поточної мови."""
    global _translations
    lang_code = load_language()
    lang_file = f"src/locales/{lang_code}.json"

    try:
        with open(lang_file, "r", encoding="utf-8") as file:
            _translations = json.load(file)
    except FileNotFoundError:
        # Якщо файл не знайдено, завантажується англійська мова за замовчуванням
        with open("src/locales/en.json", "r", encoding="utf-8") as file:
            _translations = json.load(file)


def tr(key: str) -> str:
    """Повертає переклад за ключем.

    Args:
        key (str): Ключ перекладу (наприклад 'app.lesson_dialog.title').

    Returns:
        str: Перекладений текст або ключ, якщо переклад не знайдено.
    """
    keys = key.split(".")
    result = _translations
    for k in keys:
        if not isinstance(result, dict):
            break
        result = result.get(k, {})
    return result if isinstance(result, str) else key


def set_language(lang_code: str) -> None:
    """Встановлює нову мову і оновлює переклади.

    Args:
        lang_code (str): Код мови (наприклад 'en', 'ukr').
    """
    save_language(lang_code)
    load_translations()

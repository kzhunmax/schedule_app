import json
from settings import load_language

_translations = {}

def load_translations():
    global _translations
    lang_code = load_language()  # returns 'en', 'ukr', 'pl'
    lang_file = f"locales/{lang_code}.json"

    try:
        with open(lang_file, "r", encoding="utf-8") as f:
            _translations = json.load(f)
    except FileNotFoundError:
        with open("locales/en.json", "r", encoding="utf-8") as f:
            _translations = json.load(f)

def tr(key):
    keys = key.split(".")
    result = _translations
    for k in keys:
        result = result.get(k, {})
    return result if isinstance(result, str) else key

def set_language(lang_code):
    from settings import save_language
    save_language(lang_code)
    load_translations()
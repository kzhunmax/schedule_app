import csv
import json
from typing import List, Optional
from PyQt6.QtWidgets import QFileDialog
from src.models import Lesson

REQUIRED_FIELDS = {
    'ID': str,
    'Day': str,
    'Subject': str,
    'Start_time': str,
    'End_time': str,
}


def export_to_csv(lessons: List[Lesson], parent=None) -> Optional[bool]:
    """
    Експортує список уроків у CSV файл.

    Args:
        lessons (List[Lesson]): Список уроків для експорту.
        parent (QWidget): Батьківський віджет для діалогу.

    Returns:
        Optional[bool]: True — якщо успішно, False — якщо сталася помилка, None — скасовано.
    """
    file_path, _ = QFileDialog.getSaveFileName(parent, "Save CSV", "", "CSV Files (*.csv)")
    if not file_path:
        return None

    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Day", "Subject", "Start_time", "End_time", "Type", "Room", "Color"])
            for lesson in lessons:
                writer.writerow([
                    lesson.id,
                    lesson.day,
                    lesson.subject,
                    lesson.start_time,
                    lesson.end_time,
                    lesson.type,
                    lesson.room,
                    lesson.color
                ])
        return True
    except Exception as e:
        print("CSV Export Error:", e)
        return False


def export_to_json(lessons: list, parent=None) -> Optional[bool]:
    """
    Експортує список уроків у JSON файл.

    Args:
        lessons (list): Список уроків для експорту.
        parent (QWidget): Батьківський віджет для діалогу.

    Returns:
        Optional[bool]: True — якщо успішно, False — якщо сталася помилка, None — скасовано.
    """
    file_path, _ = QFileDialog.getSaveFileName(parent, "Save JSON", "", "JSON Files (*.json)")
    if not file_path:
        return None

    try:
        data = [lesson.to_dict() for lesson in lessons]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print("JSON Export Error:", e)
        return False


def _validate_lesson_fields(row: dict) -> bool:
    """Перевіряє, чи всі обов'язкові поля присутні та не є порожніми."""
    for field, field_type in REQUIRED_FIELDS.items():
        value = row.get(field)
        if not isinstance(value, field_type) or not value:
            return False
    return True


def import_from_csv(file_path: str) -> List[Lesson]:
    """
    Імпортує уроки з CSV файлу.

    Args:
        file_path (str): Шлях до CSV файлу.

    Returns:
        List[Lesson]: Список уроків або порожній список у разі помилки.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Перевірка заголовків
            missing_headers = [h for h in REQUIRED_FIELDS if h not in reader.fieldnames]
            if missing_headers:
                print("CSV Import Error: Missing required headers", missing_headers)
                return []

            lessons = []
            seen_ids = set()

            for row in reader:
                lesson_id = row.get("ID")

                # Перевірка на пусті/відсутні обов'язкові поля
                if not _validate_lesson_fields(row):
                    print("CSV Import Error: Invalid or missing fields")
                    return []

                # Перевірка дублікатів ID
                if lesson_id in seen_ids:
                    print(f"CSV Import Error: Duplicate ID found - {lesson_id}")
                    return []
                seen_ids.add(lesson_id)

                lessons.append(Lesson(
                    lesson_id=lesson_id,
                    day=row['Day'],
                    subject=row['Subject'],
                    start_time=row['Start_time'],
                    end_time=row['End_time'],
                    lesson_type=row.get('Type', ''),
                    room=row.get('Room', ''),
                    color=row.get('Color', '')
                ))

            return lessons

    except Exception as e:
        print("CSV Import Error:", e)
        return []


def import_from_json(file_path: str) -> List[Lesson]:
    """
    Імпортує уроки з JSON файлу.

    Args:
        file_path (str): Шлях до JSON файлу.

    Returns:
        List[Lesson]: Список уроків або порожній список у разі помилки.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("JSON Import Error: Data is not a list")
            return []

        lessons = []
        seen_ids = set()

        for item in data:
            lesson_id = item.get("ID")

            # Перевірка обов'язкових полів
            if not _validate_lesson_fields(item):
                print("JSON Import Error: Invalid or missing fields")
                return []

            # Перевірка дублікатів ID
            if lesson_id in seen_ids:
                print(f"JSON Import Error: Duplicate ID found - {lesson_id}")
                return []
            seen_ids.add(lesson_id)

            lessons.append(Lesson.from_dict(item))

        return lessons

    except Exception as e:
        print("JSON Import Error:", e)
        return []

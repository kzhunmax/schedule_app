import csv
import json
from PyQt6.QtWidgets import QFileDialog
from models import Lesson


def export_to_csv(lessons, parent=None):
    file_path, _ = QFileDialog.getSaveFileName(parent, "Save CSV", "", "CSV Files (*.csv)")
    if not file_path:
        return

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Day", "Subject", "Time", "Type", "Room"])
        for lesson in lessons:
            writer.writerow([lesson.id, lesson.day, lesson.subject, lesson.time, lesson.type, lesson.room])


def export_to_json(lessons, parent=None):
    file_path, _ = QFileDialog.getSaveFileName(parent, "Save JSON", "", "JSON Files (*.json)")
    if not file_path:
        return

    data = [lesson.to_dict() for lesson in lessons]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def import_from_csv(parent=None):
    file_path, _ = QFileDialog.getOpenFileName(parent, "Choose CSV", "", "CSV Files (*.csv)")
    if not file_path:
        return []

    lessons = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lessons.append(Lesson(
                lesson_id=row.get("ID"),
                day=row.get("Day"),
                subject=row.get("Subject"),
                time=row.get("Time"),
                lesson_type=row.get("Type"),
                room=row.get("Room")
            ))
    return lessons


def import_from_json(parent=None):
    file_path, _ = QFileDialog.getOpenFileName(parent, "Choose JSON", "", "JSON Files (*.json)")
    if not file_path:
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [Lesson.from_dict(item) for item in data]
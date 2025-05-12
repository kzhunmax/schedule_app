import csv
import json
from PyQt6.QtWidgets import QFileDialog
from models import Lesson


def export_to_csv(lessons, parent=None):
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

def export_to_json(lessons, parent=None):
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


def import_from_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            lessons = []
            for row in reader:
                lesson = Lesson(
                    lesson_id=row.get("ID"),
                    day=row.get('Day', ''),
                    subject=row.get('Subject', ''),
                    start_time=row.get('Start_time', ''),
                    end_time=row.get('End_time', ''),
                    lesson_type=row.get('Type', ''),
                    room=row.get('Room', ''),
                    color=row.get('Color', '')
                )
                lessons.append(lesson)
            return lessons
    except Exception as e:
        print("CSV Import Error:", e)
        return []


def import_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Lesson.from_dict(item) for item in data]
    except Exception as e:
        print("JSON Import Error:", e)
        return []
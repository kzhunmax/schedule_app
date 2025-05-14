from typing import Dict, Any


class Lesson:
    """Модель уроку.

    Attributes:
        id (int | None): Унікальний ідентифікатор уроку.
        day (str): День тижня.
        subject (str): Назва предмету.
        start_time (str): Час початку у форматі HH:MM.
        end_time (str): Час закінчення у форматі HH:MM.
        type (str): Тип заняття ('Online', 'Offline').
        room (str): Аудиторія.
        color (str): Колір для візуалізації.
    """

    def __init__(
        self,
        lesson_id: int | None = None,
        day: str = "",
        subject: str = "",
        start_time: str = "",
        end_time: str = "",
        lesson_type: str = "",
        room: str = "",
        color: str = ""
    ):
        self.id = lesson_id
        self.day = day
        self.subject = subject
        self.start_time = start_time
        self.end_time = end_time
        self.type = lesson_type
        self.room = room
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        """Перетворює урок у словник.

        Returns:
            dict: Дані уроку.
        """
        return {
            "id": self.id,
            "day": self.day,
            "subject": self.subject,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "type": self.type,
            "room": self.room,
            "color": self.color
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Lesson":
        """Створює об'єкт уроку зі словника.

        Args:
            data (dict): Дані уроку.

        Returns:
            Lesson: Екземпляр класу Lesson.
        """
        return Lesson(
            lesson_id=data.get("id"),
            day=data.get("day", ""),
            subject=data.get("subject", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            lesson_type=data.get("type", ""),
            room=data.get("room", ""),
            color=data.get("color", "")
        )

class Lesson:
    def __init__(self, lesson_id=None, day="", subject="", time="", lesson_type="", room=""):
        self.id = lesson_id
        self.day = day
        self.subject = subject
        self.time = time
        self.type = lesson_type
        self.room = room

    def to_dict(self):
        return {
            "id": self.id,
            "day": self.day,
            "subject": self.subject,
            "time": self.time,
            "type": self.type,
            "room": self.room
        }

    @staticmethod
    def from_dict(data):
        return Lesson(**data)
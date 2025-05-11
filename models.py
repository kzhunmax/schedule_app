class Lesson:
    def __init__(self, lesson_id=None, day="", subject="", start_time="", end_time="", lesson_type="", room="", color=""):
        self.id = lesson_id
        self.day = day
        self.subject = subject
        self.start_time = start_time
        self.end_time = end_time
        self.type = lesson_type
        self.room = room
        self.color = color or "#00a7e5"

    def to_dict(self):
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
    def from_dict(data):
        return Lesson(
            lesson_id=data.get("id"),
            day=data.get("day", ""),
            subject=data.get("subject", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            lesson_type=data.get("type", ""),
            room=data.get("room", ""),
            color = data.get("color")
        )
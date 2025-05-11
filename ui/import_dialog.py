from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from language import tr
from utils import import_from_csv, import_from_json

class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("app.import.title"))
        self.setMinimumSize(400, 300)
        self.setAcceptDrops(True)
        self.parent = parent

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel(tr("app.import.instructions"))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(".csv"):
                lessons = import_from_csv(file_path)
                self.parent.bulk_insert_lessons(lessons)
                self.accept()
            elif file_path.endswith(".json"):
                lessons = import_from_json(file_path)
                self.parent.bulk_insert_lessons(lessons)
                self.accept()
            else:
                self.label.setText(tr("app.import.unsupported_format"))
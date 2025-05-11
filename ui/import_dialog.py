from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select File",
                "",
                "CSV Files (*.csv);;JSON Files (*.json)"
            )
            if file_path:
                self.handle_file(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.handle_file(file_path)

    def handle_file(self, file_path):
        if file_path.endswith(".csv"):
            lessons = import_from_csv(file_path)
            if lessons:
                self.parent.bulk_insert_lessons(lessons)
                self.accept()
            else:
                self.label.setText(tr("app.import.csv_failed"))
        elif file_path.endswith(".json"):
            lessons = import_from_json(file_path)
            if lessons:
                self.parent.bulk_insert_lessons(lessons)
                self.accept()
            else:
                self.label.setText(tr("app.import.json_failed"))
        else:
            self.label.setText(tr("app.import.unsupported_format"))
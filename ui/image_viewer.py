# ui/image_viewer.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from core.image_editor import ImageEditor

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.editor = ImageEditor()
        self.current_path = None

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel("Aquí se mostrará la imagen")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; background: #fafafa;")

        # Que el visor crezca todo lo posible
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setMinimumSize(400, 300)

        layout.addWidget(self.preview_label, stretch=1)
        self.setLayout(layout)

    def set_image(self, path: str):
        self.current_path = path
        self.refresh()

    def rotate(self, angle: int):
        if not self.current_path:
            return
        self.editor.rotate(self.current_path, angle)
        self.refresh()

    def refresh(self):
        if not self.current_path:
            self.preview_label.clear()
            self.preview_label.setText("Aquí se mostrará la imagen")
            return
        pixmap = self.editor.render_for_label(self.current_path, self.preview_label.size())
        self.preview_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reescalar la imagen al tamaño actual del label
        self.refresh()

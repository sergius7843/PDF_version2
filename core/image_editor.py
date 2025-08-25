# core/image_editor.py (Actualizado)
from PyQt6.QtGui import QPixmap, QTransform, QImage
from PyQt6.QtCore import QSize, Qt

class ImageEditor:
    def __init__(self):
        self.rotations = {}  # {path: grados}
        self.edited_images = {}  # {path: QImage editada (post-recorte/filtro)}

    def rotation_for(self, path: str) -> int:
        return self.rotations.get(path, 0)

    def rotate(self, path: str, angle: int) -> int:
        new_angle = (self.rotation_for(path) + angle) % 360
        self.rotations[path] = new_angle
        return new_angle

    def set_edited(self, path: str, img: QImage):
        if not img.isNull():
            self.edited_images[path] = img

    def get_current_image(self, path: str) -> QImage:
        """Devuelve la imagen base (original o editada) con rotación aplicada."""
        if path in self.edited_images:
            base = self.edited_images[path]
        else:
            base = QImage(path)
        if base.isNull():
            return QImage()
        angle = self.rotation_for(path)
        if angle:
            transform = QTransform().rotate(angle)
            base = base.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        return base

    def render_for_label(self, path: str, target_size: QSize) -> QPixmap:
        img = self.get_current_image(path)
        if img.isNull():
            return QPixmap()
        pm = QPixmap.fromImage(img)
        return pm.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
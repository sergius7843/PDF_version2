# core/image_editor.py
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import QSize, Qt

class ImageEditor:
    def __init__(self):
        # Rotación acumulada por ruta
        self.rotations = {}  # {path: grados}

    def rotation_for(self, path: str) -> int:
        return self.rotations.get(path, 0)

    def rotate(self, path: str, angle: int) -> int:
        """Acumula rotación en memoria (no guarda en disco). Devuelve el nuevo ángulo."""
        new_angle = (self.rotation_for(path) + angle) % 360
        self.rotations[path] = new_angle
        return new_angle

    def render_for_label(self, path: str, target_size: QSize) -> QPixmap:
        """
        Devuelve un QPixmap listo para pintar en el QLabel del visor,
        aplicando rotación y escalado con suavizado.
        """
        pm = QPixmap(path)
        if pm.isNull():
            return QPixmap()

        angle = self.rotation_for(path)
        if angle:
            transform = QTransform().rotate(angle)
            pm = pm.transformed(transform, Qt.TransformationMode.SmoothTransformation)

        # IMPORTANTE: usar enums de PyQt6, no enteros
        return pm.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

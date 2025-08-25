# ui/crop_editor.py (Nuevo archivo)
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QPen, QColor, QCursor
from PyQt6.QtCore import Qt, QPointF
from core.image_processor import manual_crop_document


class CropEditor(QDialog):
    def __init__(self, image: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recorte Manual")
        self.setModal(True)
        self.resize(800, 600)

        self.image_item = QGraphicsPixmapItem(image)
        self.scene = QGraphicsScene()
        self.scene.addItem(self.image_item)

        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setInteractive(True)
        self.view.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        # Puntos iniciales (esquinas de la imagen)
        w, h = image.width(), image.height()
        self.points = [
            QPointF(0, 0),           # TL
            QPointF(w - 1, 0),       # TR
            QPointF(w - 1, h - 1),   # BR
            QPointF(0, h - 1)        # BL
        ]
        self.point_items = []
        self.selected_point = None

        for p in self.points:
            ellipse = QGraphicsEllipseItem(-5, -5, 10, 10)
            ellipse.setPos(p)
            ellipse.setPen(QPen(QColor("red"), 2))
            ellipse.setBrush(QColor("red"))
            ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
            ellipse.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.scene.addItem(ellipse)
            self.point_items.append(ellipse)

        # Eventos
        self.view.mousePressEvent = self.mouse_press
        self.view.mouseMoveEvent = self.mouse_move
        self.view.mouseReleaseEvent = self.mouse_release

        apply_btn = QPushButton("Aplicar Recorte")
        apply_btn.clicked.connect(self.apply_crop)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.view)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Ajustar vista a imagen
        self.view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)

    def mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.view.mapToScene(event.pos())
            for i, item in enumerate(self.point_items):
                if item.contains(pos - item.pos()):
                    self.selected_point = i
                    return
        super(QGraphicsView, self.view).mousePressEvent(event)

    def mouse_move(self, event):
        if self.selected_point is not None:
            pos = self.view.mapToScene(event.pos())
            # Limitar al bounding de la imagen
            pos.setX(max(0, min(self.image_item.pixmap().width() - 1, pos.x())))
            pos.setY(max(0, min(self.image_item.pixmap().height() - 1, pos.y())))
            self.point_items[self.selected_point].setPos(pos)
        super(QGraphicsView, self.view).mouseMoveEvent(event)

    def mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected_point = None
        super(QGraphicsView, self.view).mouseReleaseEvent(event)

    def apply_crop(self):
        # Obtener puntos actualizados
        self.points = [item.pos() for item in self.point_items]
        # Ordenar si es necesario (asumimos usuario mantiene orden aproximado)
        self.accept()

    def get_points(self) -> list[tuple[float, float]]:
        return [(p.x(), p.y()) for p in self.points]
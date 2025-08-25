# ui/rename_panel.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton
from PyQt6.QtCore import pyqtSignal

class RenamePanel(QWidget):
    rename_signal = pyqtSignal(str)   # Emite el nuevo nombre (Enter)
    prev_signal = pyqtSignal()        # Click en Anterior
    next_signal = pyqtSignal()        # Click en Siguiente
    rotate_left_signal = pyqtSignal()
    rotate_right_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(6)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Escribe un nombre y presiona Enter…")
        self.input.returnPressed.connect(self.on_enter)

        # Botones compactos (tool buttons) para no quitar altura al visor
        self.prev_btn = QToolButton()
        self.prev_btn.setText("Anterior")
        self.prev_btn.clicked.connect(self.prev_signal.emit)

        self.next_btn = QToolButton()
        self.next_btn.setText("Siguiente")
        self.next_btn.clicked.connect(self.next_signal.emit)

        self.rot_left_btn = QToolButton()
        self.rot_left_btn.setText("⟲")
        self.rot_left_btn.setToolTip("Girar izquierda (Ctrl+←)")
        self.rot_left_btn.clicked.connect(self.rotate_left_signal.emit)

        self.rot_right_btn = QToolButton()
        self.rot_right_btn.setText("⟳")
        self.rot_right_btn.setToolTip("Girar derecha (Ctrl+→)")
        self.rot_right_btn.clicked.connect(self.rotate_right_signal.emit)

        # Orden: rotaciones | anterior | input | siguiente
        row.addWidget(self.rot_left_btn)
        row.addWidget(self.rot_right_btn)
        row.addWidget(self.prev_btn)
        row.addWidget(self.input, stretch=1)
        row.addWidget(self.next_btn)

        self.setLayout(row)

        # Limitar alto para no “comerse” la previsualización
        self.setMaximumHeight(48)

    def set_name(self, text: str):
        self.input.setText(text)
        self.input.selectAll()
        self.input.setFocus()

    def on_enter(self):
        self.rename_signal.emit(self.input.text().strip())
        # Auto-avanzar al siguiente
        self.next_signal.emit()

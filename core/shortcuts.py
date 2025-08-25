# core/shortcuts.py
from PyQt6.QtGui import QShortcut, QKeySequence

def setup_shortcuts(window, rotate_left_cb, rotate_right_cb):
    """Configura atajos de teclado para rotación en la ventana."""
    s_left = QShortcut(QKeySequence("Ctrl+Left"), window)
    s_right = QShortcut(QKeySequence("Ctrl+Right"), window)
    s_left.activated.connect(rotate_left_cb)
    s_right.activated.connect(rotate_right_cb)
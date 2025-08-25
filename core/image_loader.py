# core/image_loader.py
import os
from PyQt6.QtWidgets import QFileDialog

IMG_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")

class ImageLoader:
    def __init__(self):
        self.images = []   # rutas absolutas en orden de carga
        self.names = {}    # {ruta: nombre en memoria}

    def open_dialog(self, parent):
        paths, _ = QFileDialog.getOpenFileNames(
            parent, "Seleccionar imágenes", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp)"
        )
        self._add_paths(paths)
        return paths

    def add_dropped_paths(self, paths):
        self._add_paths(paths)

    def _add_paths(self, paths):
        for p in paths:
            if not p:
                continue
            if not p.lower().endswith(IMG_EXTS):
                continue
            if p not in self.images:
                self.images.append(p)
                self.names[p] = os.path.basename(p)

    def get_name(self, path):
        return self.names.get(path, os.path.basename(path))

    def set_name(self, path, new_name):
        if not new_name:
            return
        self.names[path] = new_name

    def remove_path(self, path):
        if path in self.images:
            self.images.remove(path)
            self.names.pop(path, None)
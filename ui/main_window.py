# iu/main_window.py
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QSplitter, QFileDialog, QMessageBox, QListWidgetItem, QApplication, QProgressDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from ui.image_viewer import ImageViewer
from ui.rename_panel import RenamePanel
from core.image_loader import ImageLoader, IMG_EXTS
from core.shortcuts import setup_shortcuts
from core.pdf_exporter import PDFExporter
from core.group_handler import GroupHandler
from core.image_processor import auto_crop_document


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Documentos - Fase 4")
        self.setGeometry(100, 100, 1200, 700)

        # --- Core ---
        self.loader = ImageLoader()
        self.group_handler = GroupHandler()  # Nuevo: Maneja grupos
        self.pdf_exporter = PDFExporter()
        self.viewer = ImageViewer()

        # --- Widgets UI ---
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Multi-select para agrupar
        self.viewer = ImageViewer()
        self.rename_panel = RenamePanel()

        # Botones
        load_button = QPushButton("Abrir imágenes")
        load_button.clicked.connect(self.load_images)

        self.create_group_btn = QPushButton("Crear Grupo")
        self.create_group_btn.clicked.connect(self.create_group)

        self.ungroup_btn = QPushButton("Desagrupar")
        self.ungroup_btn.clicked.connect(self.ungroup_current)

        self.export_current_btn = QPushButton("Exportar actual a PDF")
        self.export_current_btn.clicked.connect(self.export_current_to_pdf)

        self.export_all_btn = QPushButton("Exportar todos a PDFs")
        self.export_all_btn.clicked.connect(self.export_all_to_pdfs)

        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.clicked.connect(self.delete_current)

        # Panel izquierdo
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.list_widget)
        left_layout.addWidget(load_button)
        left_layout.addWidget(self.create_group_btn)
        left_layout.addWidget(self.ungroup_btn)
        left_layout.addWidget(self.export_current_btn)
        left_layout.addWidget(self.export_all_btn)
        left_layout.addWidget(self.delete_btn)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Panel derecho
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.viewer, stretch=1)
        right_layout.addWidget(self.rename_panel, stretch=0)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Panel derecho: agregar botones de edición antes de rename_panel
        edit_layout = QHBoxLayout()
        edit_layout.setContentsMargins(0, 4, 0, 4)
        edit_layout.setSpacing(6)

        self.auto_crop_btn = QPushButton("Recorte Automático")
        self.auto_crop_btn.clicked.connect(self.auto_crop_current)
        edit_layout.addWidget(self.auto_crop_btn)

        # Placeholder para más botones en futuras subfases
        edit_layout.addStretch()

        right_layout.addLayout(edit_layout)
        right_layout.addWidget(self.viewer, stretch=1)
        right_layout.addWidget(self.rename_panel, stretch=0)

        # Splitter
        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        container = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.addWidget(splitter)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Conexiones
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.rename_panel.rename_signal.connect(self.on_rename)
        self.rename_panel.prev_signal.connect(self.show_previous)
        self.rename_panel.next_signal.connect(self.show_next)
        self.rename_panel.rotate_left_signal.connect(lambda: self.viewer.rotate(-90))
        self.rename_panel.rotate_right_signal.connect(lambda: self.viewer.rotate(90))

        setup_shortcuts(
            self,
            rotate_left_cb=lambda: self.viewer.rotate(-90),
            rotate_right_cb=lambda: self.viewer.rotate(90),
        )

        self.setAcceptDrops(True)

    # Carga y selección
    def load_images(self):
        paths = self.loader.open_dialog(self)
        self._append_list_items(paths)
        if paths and self.list_widget.currentRow() == -1:
            self.list_widget.setCurrentRow(0)
            self._show_index(0)

    def _append_list_items(self, paths):
        for p in paths:
            name = self.loader.get_name(p)
            item = QListWidgetItem(name)
            item.setToolTip(p)
            item.setData(Qt.ItemDataRole.UserRole, {'type': 'single', 'path': p})  # Marcar como single
            self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        index = self.list_widget.row(item)
        self._show_index(index)

    def _show_index(self, index: int):
        if 0 <= index < self.list_widget.count():
            item = self.list_widget.item(index)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data['type'] == 'single':
                path = data['path']
                self.viewer.set_image(path)
                self.rename_panel.set_name(self.loader.get_name(path))
            elif data['type'] == 'group':
                group = data['group']
                first_path = group['paths'][0] if group['paths'] else None
                if first_path:
                    self.viewer.set_image(first_path)
                self.rename_panel.set_name(self.group_handler.get_group_name(group))
            self.list_widget.setCurrentRow(index)

    # Renombrado
    def on_rename(self, new_name: str):
        idx = self.list_widget.currentRow()
        if idx < 0 or idx >= self.list_widget.count():
            return
        item = self.list_widget.item(idx)
        data = item.data(Qt.ItemDataRole.UserRole)
        if data['type'] == 'single':
            path = data['path']
            self.loader.set_name(path, new_name)
            item.setText(new_name)
        elif data['type'] == 'group':
            group = data['group']
            self.group_handler.set_group_name(group, new_name)
            item.setText(f"Grupo: {new_name} [{len(group['paths'])} imgs]")

    # Navegación
    def show_previous(self):
        idx = self.list_widget.currentRow()
        if idx > 0:
            self._show_index(idx - 1)

    def show_next(self):
        idx = self.list_widget.currentRow()
        if idx < len(self.loader.images) - 1:
            self._show_index(idx + 1)

    # Keyboard navigation
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Right:
            self.show_next()
        elif key == Qt.Key.Key_Left:
            self.show_previous()
        else:
            super().keyPressEvent(event)

    # Drag & Drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p and p.lower().endswith(IMG_EXTS):
                paths.append(p)
        if not paths:
            return
        self.loader.add_dropped_paths(paths)
        self._append_list_items(paths)
        if self.list_widget.currentRow() == -1:
            self.list_widget.setCurrentRow(0)
            self._show_index(0)

    # Exportación Individual
    def export_current_to_pdf(self):
            idx = self.list_widget.currentRow()
            if idx < 0:
                QMessageBox.warning(self, "Sin selección", "No hay nada seleccionado.")
                return

            item = self.list_widget.item(idx)
            data = item.data(Qt.ItemDataRole.UserRole)
            name = item.text().split("[")[0].strip() if '[' in item.text() else item.text()  # Limpio para grupos

            default_filename = f"{name}.pdf" if name else "documento.pdf"

            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("PDF Files (*.pdf)")
            file_dialog.setDefaultSuffix("pdf")
            file_dialog.setWindowTitle("Guardar como PDF")
            file_dialog.selectFile(default_filename)

            if file_dialog.exec():
                save_path = file_dialog.selectedFiles()[0]
                try:
                    if data['type'] == 'single':
                        path = data['path']
                        image = self.viewer.editor.get_current_image(path)
                        self.pdf_exporter.export_image_to_pdf(image, save_path)
                    elif data['type'] == 'group':
                        group = data['group']
                        paths = group['paths']
                        images = [self.viewer.editor.get_current_image(p) for p in paths]
                        self.pdf_exporter.export_images_to_pdf(images, save_path)
                    QMessageBox.information(self, "Éxito", f"PDF guardado en:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")

    # Exportación en Lote
    def export_all_to_pdfs(self):
        total_items = len(self.loader.images) + len(self.group_handler.groups)
        if total_items == 0:
            QMessageBox.warning(self, "Sin ítems", "No hay imágenes o grupos cargados.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para exportar PDFs")
        if not output_dir:
            return

        progress = QProgressDialog("Exportando PDFs...", "Cancelar", 0, total_items, self)
        progress.setWindowTitle("Exportando")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        errors = []
        count = 0

        # Export sueltas
        for path in self.loader.images[:]:  # Copia para evitar mod
            if progress.wasCanceled():
                break
            progress.setValue(count)
            progress.setLabelText(f"Exportando {count+1}/{total_items} (suelta)")
            QApplication.processEvents()

            name = self.loader.get_name(path)
            if not name:
                name = f"documento_{count + 1}"
            save_path = os.path.join(output_dir, f"{name}.pdf")
            try:
                image = self.viewer.editor.get_current_image(path)
                self.pdf_exporter.export_image_to_pdf(image, save_path)
            except Exception as e:
                errors.append(f"{name}: {e}")
            count += 1

        # Export grupos
        for group in self.group_handler.groups:
            if progress.wasCanceled():
                break
            progress.setValue(count)
            progress.setLabelText(f"Exportando {count+1}/{total_items} (grupo)")
            QApplication.processEvents()

            name = self.group_handler.get_group_name(group)
            if not name:
                name = f"grupo_{count + 1}"
            save_path = os.path.join(output_dir, f"{name}.pdf")
            try:
                paths = group['paths']
                images = [self.viewer.editor.get_current_image(p) for p in paths]
                self.pdf_exporter.export_images_to_pdf(images, save_path)
            except Exception as e:
                errors.append(f"{name}: {e}")
            count += 1

        progress.setValue(total_items)

        if errors:
            error_msg = "Algunos PDFs fallaron:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... y {len(errors) - 10} más"
            QMessageBox.warning(self, "Advertencia", error_msg)
        else:
            QMessageBox.information(self, "Éxito", f"Todos exportados a:\n{output_dir}")

    # Crear Grupo
    def create_group(self):
        selected_items = self.list_widget.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(self, "Selección", "Selecciona al menos 2 imágenes para agrupar.")
            return

        paths = []
        indices_to_remove = []
        for item in selected_items:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data['type'] != 'single':
                continue  # Solo agrupar sueltas
            paths.append(data['path'])
            indices_to_remove.append(self.list_widget.row(item))

        if not paths:
            return

        # Crear grupo
        group_name = f"Grupo_{len(self.group_handler.groups) + 1}"
        group = self.group_handler.create_group(paths, group_name)

        # Agregar item para grupo
        group_item = QListWidgetItem(f"Grupo: {group_name} [{len(paths)} imgs]")
        group_item.setToolTip("\n".join(paths))  # Tooltip con paths
        group_item.setData(Qt.ItemDataRole.UserRole, {'type': 'group', 'group': group})
        group_item.setBackground(QBrush(group['color']))  # Color para diferenciar
        self.list_widget.addItem(group_item)

        # Remover sueltas seleccionadas (en reversa para indices)
        for idx in sorted(indices_to_remove, reverse=True):
            path = self.list_widget.item(idx).data(Qt.ItemDataRole.UserRole)['path']
            self.loader.remove_path(path)
            self.list_widget.takeItem(idx)

        # Seleccionar el nuevo grupo
        self.list_widget.setCurrentItem(group_item)
        self._show_index(self.list_widget.row(group_item))


    # Desagrupar
    def ungroup_current(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return
        item = self.list_widget.item(idx)
        data = item.data(Qt.ItemDataRole.UserRole)
        if data['type'] != 'group':
            QMessageBox.warning(self, "Selección", "Selecciona un grupo para desagrupar.")
            return

        reply = QMessageBox.question(self, "Confirmar", "¿Desagrupar y devolver imágenes sueltas?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        group = data['group']
        paths = group['paths']
        self.group_handler.remove_group(group)
        self.list_widget.takeItem(idx)

        # Agregar de vuelta como sueltas
        self.loader._add_paths(paths)  # Re-agregar a loader
        self._append_list_items(paths)  # Re-agregar a lista

        if self.list_widget.count() > 0:
            self._show_index(0)

    # Eliminar Imagen
    def delete_current(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return

        item = self.list_widget.item(idx)
        data = item.data(Qt.ItemDataRole.UserRole)
        msg = "esta imagen" if data['type'] == 'single' else "este grupo (y sus imágenes)"

        reply = QMessageBox.question(self, "Confirmar eliminación", f"¿Eliminar {msg}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        if data['type'] == 'single':
            path = data['path']
            self.loader.remove_path(path)
        elif data['type'] == 'group':
            self.group_handler.remove_group(data['group'])

        self.list_widget.takeItem(idx)

        if self.list_widget.count() > 0:
            new_idx = min(idx, self.list_widget.count() - 1)
            self._show_index(new_idx)
        else:
            self.viewer.set_image(None)
            self.rename_panel.set_name("")

    def auto_crop_current(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return
        item = self.list_widget.item(idx)
        data = item.data(Qt.ItemDataRole.UserRole)
        if data['type'] != 'single':
            QMessageBox.warning(self, "Selección", "El recorte automático solo funciona en imágenes individuales.")
            return

        path = data['path']
        try:
            current_img = self.viewer.editor.get_current_image(path)
            cropped = auto_crop_document(current_img)
            if cropped is None:
                QMessageBox.information(self, "Información", "No se detectó un documento para recortar automáticamente.")
                return
            self.viewer.editor.set_edited(path, cropped)
            self.viewer.editor.rotations[path] = 0  # Resetear rotación (ya "horneada" en la editada)
            self.viewer.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo en recorte automático: {str(e)}")

    
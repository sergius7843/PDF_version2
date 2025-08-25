# core/pdf_exporter.py

import tempfile
import os
from PyQt6.QtGui import QImage, QTransform
from PyQt6.QtCore import Qt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class PDFExporter:
    def __init__(self):
        pass

    def export_image_to_pdf(self, image_path: str, save_path: str, rotation_angle: int = 0):
        """
        Convierte una imagen en un PDF sin bordes blancos, aplicando rotación.
        Usa archivos temporales para compatibilidad con ReportLab.
        """
        image = QImage(image_path)

        if image.isNull():
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")

        # Aplicar rotación si es necesario
        if rotation_angle != 0:
            transform = QTransform().rotate(rotation_angle)
            image = image.transformed(transform, Qt.TransformationMode.SmoothTransformation)

        # Crear archivo temporal para la imagen procesada
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Guardar imagen procesada en archivo temporal
        if not image.save(temp_path, "PNG"):
            os.unlink(temp_path)
            raise ValueError("No se pudo guardar la imagen temporal")

        try:
            # Obtener dimensiones después de rotación
            img_width = image.width()
            img_height = image.height()

            # Crear PDF del mismo tamaño que la imagen
            c = canvas.Canvas(save_path, pagesize=(img_width, img_height))
            c.drawImage(temp_path, 0, 0, width=img_width, height=img_height)
            c.showPage()
            c.save()
        finally:
            # Siempre eliminar el archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        return save_path
    
    def export_images_to_pdf(self, image_paths: list[str], rotation_angles: list[int], save_path: str):
        """
        Crea un PDF multi-página de varias imágenes, aplicando rotaciones individuales.
        Usa A4 como pagesize, scaling imágenes para fit sin bordes extras.
        """
        if not image_paths:
            raise ValueError("No hay imágenes para exportar")

        c = canvas.Canvas(save_path, pagesize=A4)
        pdf_width, pdf_height = A4

        temp_paths = []
        try:
            for path, angle in zip(image_paths, rotation_angles):
                image = QImage(path)
                if image.isNull():
                    continue  # Skip inválidas

                if angle != 0:
                    transform = QTransform().rotate(angle)
                    image = image.transformed(transform, Qt.TransformationMode.SmoothTransformation)

                # Temp file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                if not image.save(temp_path, "PNG"):
                    continue
                temp_paths.append(temp_path)

                # Draw scaled to fit A4 sin bordes (aspect ratio keep)
                img_width = image.width()
                img_height = image.height()
                scale = min(pdf_width / img_width, pdf_height / img_height)
                draw_width = img_width * scale
                draw_height = img_height * scale
                x = (pdf_width - draw_width) / 2
                y = (pdf_height - draw_height) / 2
                c.drawImage(temp_path, x, y, width=draw_width, height=draw_height)
                c.showPage()

            c.save()
        finally:
            for tp in temp_paths:
                if os.path.exists(tp):
                    os.unlink(tp)

        return save_path
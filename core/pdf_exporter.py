# core/pdf_exporter.py (Actualizado)
import tempfile
import os
from PyQt6.QtGui import QImage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class PDFExporter:
    def __init__(self):
        pass

    def export_image_to_pdf(self, image: QImage, save_path: str):
        """
        Convierte una QImage (ya procesada) en un PDF sin bordes blancos.
        Usa archivos temporales para compatibilidad con ReportLab.
        """
        if image.isNull():
            raise ValueError("Imagen inválida")

        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        # Guardar imagen en temporal
        if not image.save(temp_path, "PNG"):
            os.unlink(temp_path)
            raise ValueError("No se pudo guardar la imagen temporal")

        try:
            # PDF del tamaño exacto de la imagen
            img_width = image.width()
            img_height = image.height()
            c = canvas.Canvas(save_path, pagesize=(img_width, img_height))
            c.drawImage(temp_path, 0, 0, width=img_width, height=img_height)
            c.showPage()
            c.save()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        return save_path

    def export_images_to_pdf(self, images: list[QImage], save_path: str):
        """
        Crea un PDF multi-página de varias QImages, escalando a A4 sin bordes extras.
        """
        if not images:
            raise ValueError("No hay imágenes para exportar")

        c = canvas.Canvas(save_path, pagesize=A4)
        pdf_width, pdf_height = A4

        temp_paths = []
        try:
            for image in images:
                if image.isNull():
                    continue

                # Temporal
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                if not image.save(temp_path, "PNG"):
                    continue
                temp_paths.append(temp_path)

                # Escalar a A4 manteniendo aspect ratio
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
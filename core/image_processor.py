# core/image_processor.py (Actualizado)
import cv2
import numpy as np
from PyQt6.QtGui import QImage

def qimage_to_cv2(qimg: QImage) -> np.ndarray:
    """Convierte QImage a imagen OpenCV (BGR)."""
    qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
    width = qimg.width()
    height = qimg.height()
    ptr = qimg.bits()
    ptr.setsize(height * width * 3)
    arr = np.frombuffer(ptr, np.uint8).reshape(height, width, 3)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def cv2_to_qimage(cv_img: np.ndarray) -> QImage:
    """Convierte imagen OpenCV (BGR o grayscale) a QImage."""
    if len(cv_img.shape) == 2:  # Grayscale
        height, width = cv_img.shape
        bytes_per_line = width
        return QImage(cv_img.tobytes(), width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
    else:  # BGR
        height, width, _ = cv_img.shape
        bytes_per_line = 3 * width
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return QImage(cv_img.tobytes(), width, height, bytes_per_line, QImage.Format.Format_RGB888)

def auto_crop_document(qimg: QImage) -> QImage | None:
    """
    Realiza recorte automático detectando el documento (rectángulo).
    Devuelve la imagen recortada y enderezada si se detecta, None si no.
    Versión mejorada con umbrales automáticos y fallback.
    """
    cv_img = qimage_to_cv2(qimg)
    orig = cv_img.copy()
    height, width = cv_img.shape[:2]

    # Redimensionar para procesamiento (máx altura 800px para balance)
    ratio = height / 800.0 if height > 800 else 1.0
    cv_img_resized = cv2.resize(cv_img, (int(width / ratio), int(height / ratio)))

    def detect_contours(gray):
        # Blur suave
        gray = cv2.GaussianBlur(gray, (3, 3), 0)  # Kernel más pequeño para preservar bordes

        # Umbrales automáticos para Canny (basado en mediana)
        sigma = 0.33
        v = np.median(gray)
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(gray, lower, upper)

        # Dilatar para conectar bordes rotos
        kernel = np.ones((3, 3), np.uint8)
        edged = cv2.dilate(edged, kernel, iterations=1)

        # Encontrar contornos
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # EXTERNAL para contornos externos
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]  # Top 15 para más candidatos

        screen_cnt = None
        min_area = (gray.shape[0] * gray.shape[1]) * 0.05  # Mínimo 5% del área para ignorar ruido
        for c in contours:
            if cv2.contourArea(c) < min_area:
                continue
            peri = cv2.arcLength(c, True)
            epsilon = 0.015 * peri  # Más flexible (0.015 en lugar de 0.02)
            approx = cv2.approxPolyDP(c, epsilon, True)
            if len(approx) == 4 and cv2.isContourConvex(approx):  # Chequear convexidad para documentos reales
                screen_cnt = approx
                break

        return screen_cnt

    # Primer intento: Grayscale estándar
    gray = cv2.cvtColor(cv_img_resized, cv2.COLOR_BGR2GRAY)
    screen_cnt = detect_contours(gray)

    # Fallback: Si no detecta, usar adaptive thresholding para mejor contraste
    if screen_cnt is None:
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        screen_cnt = detect_contours(thresh)

    if screen_cnt is None:
        # Debug: Guardar edged para inspección (comenta después de probar)
        # cv2.imwrite('debug_edged.png', edged)
        return None

    # Ordenar puntos
    def order_points(pts: np.ndarray) -> np.ndarray:
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # TL
        rect[2] = pts[np.argmax(s)]  # BR
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # TR
        rect[3] = pts[np.argmax(diff)]  # BL
        return rect

    # Escalar de vuelta
    pts = screen_cnt.reshape(4, 2) * ratio
    rect = order_points(pts)

    (tl, tr, br, bl) = rect

    # Dimensiones
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    # Destino
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    # Warp
    m = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(orig, m, (max_width, max_height))

    return cv2_to_qimage(warped)
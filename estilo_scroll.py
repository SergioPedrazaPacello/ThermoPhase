"""
estilo_scroll.py — Barras de desplazamiento de estilo retro (Windows 95/98/2000)
para todo el programa: botones con flechas, relieve biselado y riel tramado,
pero delgadas (12 px en lugar de 16-17 px).

Las flechas y la trama se dibujan al iniciar con QPainter y se guardan como
PNG en una carpeta temporal (así funciona igual en el .exe, sin archivos
adicionales).  Uso:  estilo_scroll.instalar(app)
"""
import os
import tempfile

from PyQt6.QtGui import QImage, QPainter, QColor, QPolygon
from PyQt6.QtCore import QPoint, Qt, QObject, QEvent
from PyQt6.QtWidgets import QScrollBar

ANCHO = 12                      # grosor de la barra (px)
CARA = "#D4D4D4"                # cara de botones y del cursor
LUZ = "#FFFFFF"                 # bisel claro (arriba / izquierda)
MEDIA = "#A0A0A0"               # bisel interior oscuro
SOMBRA = "#404040"              # bisel oscuro (abajo / derecha)


def _png(nombre, ancho, alto, pintar):
    carpeta = os.path.join(tempfile.gettempdir(), "thermophase_qss")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre)
    img = QImage(ancho, alto, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    pintar(p)
    p.end()
    img.save(ruta, "PNG")
    return ruta.replace("\\", "/")


def _flecha(direccion, color):
    # Triángulo macizo de 7×4 (o 4×7) px, como el de Windows clásico.
    def pintar(p):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        if direccion == 'arriba':
            pts = [QPoint(3, 0), QPoint(7, 4), QPoint(-1, 4)]
        elif direccion == 'abajo':
            pts = [QPoint(-1, 0), QPoint(7, 0), QPoint(3, 4)]
        elif direccion == 'izquierda':
            pts = [QPoint(0, 3), QPoint(4, -1), QPoint(4, 7)]
        else:
            pts = [QPoint(0, -1), QPoint(0, 7), QPoint(4, 3)]
        p.drawPolygon(QPolygon(pts))
    w, h = (7, 4) if direccion in ('arriba', 'abajo') else (4, 7)
    return w, h, pintar


def _trama():
    # Riel tramado 2×2 (blanco / gris claro), el típico de Windows clásico.
    def pintar(p):
        p.fillRect(0, 0, 2, 2, QColor("#F0F0F0"))
        p.fillRect(0, 0, 1, 1, QColor(CARA))
        p.fillRect(1, 1, 1, 1, QColor(CARA))
    return pintar


def qss():
    img = {}
    for d in ('arriba', 'abajo', 'izquierda', 'derecha'):
        for estado, color in (('', '#000000'), ('_off', '#9A9A9A')):
            w, h, f = _flecha(d, color)
            img[d + estado] = (_png(f"flecha_{d}{estado}.png", w, h, f), w, h)
    trama = _png("trama.png", 2, 2, _trama())
    a = ANCHO
    relieve = (f"background:{CARA}; border-style:solid; border-width:1px;"
               f" border-top-color:{LUZ}; border-left-color:{LUZ};"
               f" border-bottom-color:{SOMBRA}; border-right-color:{SOMBRA};")
    hundido = (f"background:{CARA}; border-style:solid; border-width:1px;"
               f" border-color:{MEDIA};")

    def flecha(sel, clave):
        ruta, w, h = img[clave]
        return f"{sel} {{ image:url({ruta}); width:{w}px; height:{h}px; }}\n"

    return (
        f"QScrollBar:vertical {{ background:url({trama}); width:{a}px; margin:{a}px 0 {a}px 0; border:none; }}\n"
        f"QScrollBar:horizontal {{ background:url({trama}); height:{a}px; margin:0 {a}px 0 {a}px; border:none; }}\n"
        f"QScrollBar::handle:vertical {{ {relieve} min-height:20px; }}\n"
        f"QScrollBar::handle:horizontal {{ {relieve} min-width:20px; }}\n"
        f"QScrollBar::sub-line:vertical {{ {relieve} height:{a-2}px; subcontrol-position:top; subcontrol-origin:margin; }}\n"
        f"QScrollBar::add-line:vertical {{ {relieve} height:{a-2}px; subcontrol-position:bottom; subcontrol-origin:margin; }}\n"
        f"QScrollBar::sub-line:horizontal {{ {relieve} width:{a-2}px; subcontrol-position:left; subcontrol-origin:margin; }}\n"
        f"QScrollBar::add-line:horizontal {{ {relieve} width:{a-2}px; subcontrol-position:right; subcontrol-origin:margin; }}\n"
        f"QScrollBar::sub-line:pressed, QScrollBar::add-line:pressed {{ {hundido} }}\n"
        f"QScrollBar::add-page, QScrollBar::sub-page {{ background:none; }}\n"
        f"QScrollBar::add-page:pressed, QScrollBar::sub-page:pressed {{ background:#404040; }}\n"
        + flecha("QScrollBar::up-arrow:vertical", 'arriba')
        + flecha("QScrollBar::down-arrow:vertical", 'abajo')
        + flecha("QScrollBar::left-arrow:horizontal", 'izquierda')
        + flecha("QScrollBar::right-arrow:horizontal", 'derecha')
        + flecha("QScrollBar::up-arrow:vertical:disabled", 'arriba_off')
        + flecha("QScrollBar::down-arrow:vertical:disabled", 'abajo_off')
        + flecha("QScrollBar::left-arrow:horizontal:disabled", 'izquierda_off')
        + flecha("QScrollBar::right-arrow:horizontal:disabled", 'derecha_off')
    )


class _Filtro(QObject):
    """Aplica el estilo directamente a cada QScrollBar al mostrarse: así
    gana a las hojas de estilo «background:...» sin selector que algunas
    ventanas ponen en sus contenedores (y que, si no, pintarían el riel)."""

    def __init__(self, hoja):
        super().__init__()
        self._hoja = hoja

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Type.Show and isinstance(obj, QScrollBar) \
                and not obj.property("_tp_retro"):
            obj.setProperty("_tp_retro", True)
            obj.setStyleSheet(self._hoja)
        return False


_FILTRO = None


def instalar(app):
    global _FILTRO
    try:
        # Solo por barra (filtro de eventos), NUNCA con app.setStyleSheet: una
        # hoja de estilo global hace que Qt use QStyleSheetStyle en TODOS los
        # widgets y en Windows cambia métricas (alto mínimo de filas, botones,
        # combos), lo que desajustaba el alto de las ventanas al quitar
        # componentes y hacía aparecer barras en Parámetros de la EOS.
        hoja = qss()
        _FILTRO = _Filtro(hoja)
        app.installEventFilter(_FILTRO)
    except Exception:
        pass

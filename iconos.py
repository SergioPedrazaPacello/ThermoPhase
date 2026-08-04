"""
iconos.py — Fabrica de iconos vectoriales para ThermoPhase.

Todos los iconos se DIBUJAN en tiempo de ejecucion con QPainter sobre un
QPixmap transparente. No se necesita ningun archivo .png/.svg externo, lo
que simplifica el empaquetado con PyInstaller (nada que agregar a --add-data).

Uso:
    from iconos import icono
    boton.setIcon(icono("guardar"))          # QIcon 32x32 por defecto
    arbol_item.setIcon(0, icono("envolvente", 16))

Paleta "office": azules corporativos con acentos que respetan las
convenciones cromaticas de ThermoPhase (rojo oxido para la envolvente,
azul profundo para liquido, verde para ejecutar, rojo para detener).
"""
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QBrush, QIcon, QPolygonF, QPainterPath,
    QFont, QLinearGradient, QImage, qGray, qAlpha, qRgba
)
from PyQt6.QtCore import Qt, QPointF, QRectF

# ── Paleta monocromatica ─────────────────────────────────────
# Todo el conjunto de iconos se dibuja con una unica tinta gris oscura para
# las lineas y grises claros / blanco para los rellenos, en linea con la
# estetica retro monocromatica de ThermoPhase. Ademas, un desaturado final
# (ver _desaturar) fuerza escala de grises aunque algun icono use un color
# puntual embebido en su funcion de dibujo.
NEGRO     = QColor("#303030")   # tinta principal (lineas)
GRIS      = QColor("#5A5A5A")   # gris medio
GRIS_CLR  = QColor("#B8B8B8")   # gris claro (rellenos suaves)
BLANCO    = QColor("#FFFFFF")
PAPEL     = QColor("#F4F4F4")
# Alias de compatibilidad: los iconos siguen nombrando estos colores, pero
# todos apuntan ahora a la escala de grises.
AZUL      = QColor("#8A8A8A")
AZUL_OSC  = QColor("#3A3A3A")
AZUL_CLR  = QColor("#C4C4C4")
ROJO_OX   = QColor("#4A4A4A")
ROJO      = QColor("#565656")
VERDE     = QColor("#4A4A4A")
AMBAR     = QColor("#777777")


# ── Infraestructura ──────────────────────────────────────────
def _nuevo(tam):
    """Crea (pixmap transparente, painter listo)."""
    pm = QPixmap(tam, tam)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    # Trabajamos en un lienzo virtual 32x32 y escalamos al tamano pedido.
    p.scale(tam / 32.0, tam / 32.0)
    return pm, p


def _pen(color, w=1.8, cap=Qt.PenCapStyle.RoundCap,
         join=Qt.PenJoinStyle.RoundJoin):
    pen = QPen(color, w)
    pen.setCapStyle(cap)
    pen.setJoinStyle(join)
    return pen


def _poly(pts):
    return QPolygonF([QPointF(x, y) for x, y in pts])


# ── Bloques reutilizables ────────────────────────────────────
def _documento(p, borde=GRIS, relleno=PAPEL, esquina=True):
    """Hoja de papel con esquina doblada (base de los iconos de archivo)."""
    path = QPainterPath()
    path.moveTo(7, 3)
    path.lineTo(19, 3)
    path.lineTo(25, 9)
    path.lineTo(25, 29)
    path.lineTo(7, 29)
    path.closeSubpath()
    p.setPen(_pen(borde, 1.6))
    p.setBrush(QBrush(relleno))
    p.drawPath(path)
    if esquina:
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolyline(_poly([(19, 3), (19, 9), (25, 9)]))


def _lineas_texto(p, color=GRIS_CLR, x0=10, x1=22, ys=(14, 18, 22)):
    p.setPen(_pen(color, 1.4))
    for y in ys:
        p.drawLine(QPointF(x0, y), QPointF(x1, y))


# ── Iconos: ARCHIVO ──────────────────────────────────────────
def _nuevo_doc(p):
    _documento(p, relleno=BLANCO)
    _lineas_texto(p)


def _abrir(p):
    # Carpeta abierta
    p.setPen(_pen(QColor("#B8860B"), 1.4))
    p.setBrush(QBrush(QColor("#F4C453")))
    p.drawPolygon(_poly([(4, 9), (13, 9), (16, 12), (27, 12), (27, 25), (4, 25)]))
    p.setBrush(QBrush(QColor("#FCE29A")))
    p.drawPolygon(_poly([(7, 14), (28, 14), (25, 25), (4, 25)]))


def _guardar(p):
    # Diskette
    p.setPen(_pen(AZUL_OSC, 1.4))
    p.setBrush(QBrush(AZUL))
    path = QPainterPath()
    path.moveTo(5, 5); path.lineTo(23, 5); path.lineTo(27, 9)
    path.lineTo(27, 27); path.lineTo(5, 27); path.closeSubpath()
    p.drawPath(path)
    # Etiqueta blanca inferior
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(BLANCO))
    p.drawRect(QRectF(9, 17, 14, 10))
    # Obturador superior
    p.setBrush(QBrush(QColor("#EAF0FB")))
    p.drawRect(QRectF(11, 6, 9, 7))
    p.setBrush(QBrush(AZUL_OSC))
    p.drawRect(QRectF(17, 7, 2.5, 5))


def _guardar_como(p):
    _guardar(p)
    # Lapiz sobre el diskette
    p.setPen(_pen(VERDE, 1.6))
    p.setBrush(QBrush(VERDE))
    p.drawPolygon(_poly([(20, 24), (28, 16), (30, 18), (22, 26)]))
    p.setBrush(QBrush(QColor("#FFF2CC")))
    p.drawPolygon(_poly([(20, 24), (22, 26), (19, 27)]))


def _imprimir(p):
    p.setPen(_pen(GRIS, 1.4))
    p.setBrush(QBrush(BLANCO))
    p.drawRect(QRectF(9, 4, 14, 8))          # hoja superior
    p.setBrush(QBrush(QColor("#C9D4E4")))
    p.drawRoundedRect(QRectF(5, 12, 22, 10), 2, 2)  # cuerpo
    p.setBrush(QBrush(BLANCO))
    p.drawRect(QRectF(9, 19, 14, 9))          # hoja salida
    p.setPen(_pen(GRIS_CLR, 1.2))
    p.drawLine(QPointF(11, 23), QPointF(21, 23))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL))
    p.drawEllipse(QRectF(22, 14, 2.4, 2.4))


# ── Iconos: EDICION ──────────────────────────────────────────
def _cortar(p):
    # Tijeras
    p.setPen(_pen(GRIS, 1.8))
    p.drawLine(QPointF(11, 12), QPointF(27, 24))
    p.drawLine(QPointF(11, 20), QPointF(27, 8))
    p.setBrush(QBrush(BLANCO))
    p.drawEllipse(QRectF(5, 9, 7, 7))
    p.drawEllipse(QRectF(5, 17, 7, 7))


def _copiar(p):
    p.setPen(_pen(GRIS, 1.4))
    p.setBrush(QBrush(QColor("#E8EEF7")))
    p.drawRect(QRectF(6, 6, 14, 17))          # hoja trasera
    p.setBrush(QBrush(BLANCO))
    p.drawRect(QRectF(12, 11, 14, 17))         # hoja delantera
    _lineas_texto(p, x0=15, x1=23, ys=(16, 20, 24))


def _pegar(p):
    # Portapapeles
    p.setPen(_pen(QColor("#7A5C33"), 1.4))
    p.setBrush(QBrush(QColor("#C79A5B")))
    p.drawRoundedRect(QRectF(6, 6, 20, 24), 2, 2)
    p.setBrush(QBrush(QColor("#EFE0C6")))
    p.drawRect(QRectF(10, 9, 12, 3))
    p.setBrush(QBrush(BLANCO))
    p.drawRect(QRectF(9, 14, 14, 14))          # hoja pegada
    _lineas_texto(p, x0=11, x1=21, ys=(18, 22, 26))


def _deshacer(p):
    p.setPen(_pen(AZUL, 2.4))
    path = QPainterPath()
    path.moveTo(24, 22)
    path.arcTo(QRectF(7, 8, 18, 18), -20, -150)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(path)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL))
    p.drawPolygon(_poly([(6, 9), (14, 8), (10, 16)]))


def _rehacer(p):
    p.setPen(_pen(AZUL, 2.4))
    path = QPainterPath()
    path.moveTo(8, 22)
    path.arcTo(QRectF(7, 8, 18, 18), 200, 150)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(path)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL))
    p.drawPolygon(_poly([(26, 9), (18, 8), (22, 16)]))


# ── Iconos: CALCULOS ─────────────────────────────────────────
def _fraccion_masica(p):
    # Balanza / porcentaje de masa
    p.setPen(_pen(GRIS, 1.8))
    p.drawLine(QPointF(16, 5), QPointF(16, 27))
    p.drawLine(QPointF(7, 9), QPointF(25, 9))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(BLANCO))
    p.setPen(_pen(AZUL, 1.4))
    p.drawPolygon(_poly([(4, 9), (10, 9), (7, 18)]))   # platillo izq
    p.drawPolygon(_poly([(22, 9), (28, 9), (25, 18)])) # platillo der
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(GRIS))
    p.drawRect(QRectF(12, 27, 8, 2.5))


def _normalizar(p):
    # Sigma con flechas de igualacion
    p.setPen(_pen(AZUL_OSC, 2.0))
    p.drawPolyline(_poly([(21, 7), (9, 7), (16, 16), (9, 25), (21, 25)]))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(VERDE))
    p.drawEllipse(QRectF(22, 13, 6, 6))


def _ejecutar(p):
    # Triangulo play verde
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(VERDE))
    p.drawPolygon(_poly([(9, 6), (26, 16), (9, 26)]))


def _detener(p):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(GRIS_CLR))
    p.drawRoundedRect(QRectF(8, 8, 16, 16), 2.5, 2.5)


# ── Iconos: UNIDADES ─────────────────────────────────────────
def _sistema(p):
    # Regla / unidades
    p.setPen(_pen(AZUL_OSC, 1.4))
    p.setBrush(QBrush(QColor("#DCE7F7")))
    p.save(); p.translate(16, 16); p.rotate(-30); p.translate(-16, -16)
    p.drawRect(QRectF(4, 12, 24, 8))
    p.setPen(_pen(AZUL_OSC, 1.1))
    for i, x in enumerate(range(7, 28, 4)):
        h = 5 if i % 2 == 0 else 3
        p.drawLine(QPointF(x, 12), QPointF(x, 12 + h))
    p.restore()


def _conversor(p):
    # Dos flechas circulares de intercambio
    p.setPen(_pen(AZUL, 2.2))
    p.drawLine(QPointF(7, 12), QPointF(23, 12))
    p.drawLine(QPointF(9, 20), QPointF(25, 20))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(AZUL))
    p.drawPolygon(_poly([(23, 8), (28, 12), (23, 16)]))
    p.setBrush(QBrush(AZUL_OSC))
    p.drawPolygon(_poly([(9, 16), (4, 20), (9, 24)]))


# ── Iconos: DATOS ────────────────────────────────────────────
def _cilindro(p, color, borde):
    p.setPen(_pen(borde, 1.4))
    p.setBrush(QBrush(color))
    p.drawRect(QRectF(7, 8, 18, 16))
    p.drawEllipse(QRectF(7, 21, 18, 6))
    p.setBrush(QBrush(color.lighter(115)))
    p.drawEllipse(QRectF(7, 5, 18, 6))


def _componentes(p):
    # Molecula: atomo central rojo con enlaces a atomos azul/verde.
    p.setPen(_pen(QColor("#707070"), 2.2))
    p.drawLine(QPointF(16, 16), QPointF(9, 9))
    p.drawLine(QPointF(16, 16), QPointF(23, 9))
    p.drawLine(QPointF(16, 16), QPointF(16, 25))
    p.setPen(_pen(QColor("#2A4A70"), 0.8)); p.setBrush(QBrush(QColor("#6E97C6")))
    p.drawEllipse(QRectF(5.5, 5.5, 7, 7))
    p.drawEllipse(QRectF(19.5, 5.5, 7, 7))
    p.setPen(_pen(QColor("#3B6D11"), 0.8)); p.setBrush(QBrush(QColor("#8CBF6C")))
    p.drawEllipse(QRectF(12.5, 21.5, 7, 7))
    p.setPen(_pen(QColor("#7A1F1F"), 0.8)); p.setBrush(QBrush(QColor("#C0392B")))
    p.drawEllipse(QRectF(11.5, 11.5, 9, 9))


def _fluidos(p):
    # Matraz Erlenmeyer con liquido ambar UNIFORME.
    OUT = QColor("#4A4A4A"); OIL = QColor("#D9A441")
    flask = QPainterPath()
    flask.moveTo(13, 4); flask.lineTo(19, 4)
    flask.lineTo(19, 12); flask.lineTo(26, 25)
    flask.cubicTo(27, 27.5, 25.5, 29, 23, 29)
    flask.lineTo(9, 29)
    flask.cubicTo(6.5, 29, 5, 27.5, 6, 25)
    flask.lineTo(13, 12); flask.closeSubpath()
    p.setPen(_pen(OUT, 1.5)); p.setBrush(QBrush(QColor("#FFFFFF")))
    p.drawPath(flask)
    p.setClipPath(flask)
    liq = QPainterPath()
    liq.moveTo(8.7, 21); liq.lineTo(23.3, 21)
    liq.lineTo(26, 25); liq.cubicTo(27, 27.5, 25.5, 29, 23, 29)
    liq.lineTo(9, 29); liq.cubicTo(6.5, 29, 5, 27.5, 6, 25); liq.closeSubpath()
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(OIL))
    p.drawPath(liq)
    p.setClipping(False)
    p.setPen(_pen(OUT, 1.5)); p.drawLine(QPointF(13, 4), QPointF(19, 4))


def _mezclas(p):
    # Matraz con contenido
    p.setPen(_pen(GRIS, 1.4))
    path = QPainterPath()
    path.moveTo(13, 5); path.lineTo(13, 13); path.lineTo(7, 26)
    path.cubicTo(6, 28, 8, 29, 10, 29)
    path.lineTo(22, 29)
    path.cubicTo(24, 29, 26, 28, 25, 26)
    path.lineTo(19, 13); path.lineTo(19, 5)
    p.setBrush(QBrush(BLANCO)); p.drawPath(path)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#6FBF8A")))
    liq = QPainterPath()
    liq.moveTo(11, 22); liq.lineTo(21, 22)
    liq.lineTo(23, 26)
    liq.cubicTo(24, 28, 22, 29, 20, 29)
    liq.lineTo(12, 29)
    liq.cubicTo(10, 29, 8, 28, 9, 26)
    liq.closeSubpath()
    p.drawPath(liq)
    p.setPen(_pen(GRIS, 1.6)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawLine(QPointF(12, 5), QPointF(20, 5))


# ── Iconos: HERRAMIENTAS ─────────────────────────────────────
def _tablas(p):
    p.setPen(_pen(AZUL_OSC, 1.4))
    p.setBrush(QBrush(BLANCO))
    p.drawRect(QRectF(5, 6, 22, 20))
    p.setBrush(QBrush(AZUL))
    p.drawRect(QRectF(5, 6, 22, 5))
    p.setPen(_pen(AZUL_CLR, 1.0))
    for y in (11, 16, 21):
        p.drawLine(QPointF(5, y), QPointF(27, y))
    for x in (12, 20):
        p.drawLine(QPointF(x, 6), QPointF(x, 26))


def _calculadora(p):
    p.setPen(_pen(GRIS, 1.4))
    p.setBrush(QBrush(QColor("#3A4657")))
    p.drawRoundedRect(QRectF(7, 4, 18, 24), 2.5, 2.5)
    p.setBrush(QBrush(QColor("#9FE0B0")))
    p.drawRect(QRectF(10, 7, 12, 5))          # pantalla
    p.setBrush(QBrush(QColor("#D8DEE8")))     # botones
    for r in range(3):
        for c in range(3):
            p.drawRect(QRectF(10 + c * 4, 15 + r * 4, 2.6, 2.6))


def _graficas(p):
    p.setPen(_pen(GRIS, 1.6))
    p.drawLine(QPointF(6, 4), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(28, 27))
    p.setPen(_pen(ROJO_OX, 2.2)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPolyline(_poly([(8, 22), (13, 15), (18, 19), (26, 8)]))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL))
    for x, y in [(13, 15), (18, 19), (26, 8)]:
        p.drawEllipse(QRectF(x - 1.6, y - 1.6, 3.2, 3.2))


# ── Iconos: PREFERENCIAS ─────────────────────────────────────
def _engranaje(p, color=GRIS, cx=16, cy=16, r=8):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(color))
    import math
    path = QPainterPath()
    n = 8
    for i in range(n * 2):
        ang = math.pi * i / n
        rr = r + 3 if i % 2 == 0 else r
        x = cx + rr * math.cos(ang); y = cy + rr * math.sin(ang)
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    path.closeSubpath()
    p.drawPath(path)
    p.setBrush(QBrush(BLANCO))
    p.drawEllipse(QRectF(cx - 3.5, cy - 3.5, 7, 7))


def _opciones(p):
    _engranaje(p, AZUL)


def _configuracion(p):
    _engranaje(p, GRIS, cx=13, cy=13, r=6.5)
    _engranaje(p, AZUL, cx=22, cy=21, r=5)


# ── Iconos: AYUDA ────────────────────────────────────────────
def _ayuda(p):
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL))
    p.drawEllipse(QRectF(4, 4, 24, 24))
    p.setBrush(QBrush(BLANCO))
    f = QFont("Arial", 16, QFont.Weight.Bold)
    p.setFont(f); p.setPen(_pen(BLANCO, 1))
    p.drawText(QRectF(4, 2, 24, 26), Qt.AlignmentFlag.AlignCenter, "?")


def _acerca(p):
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL_OSC))
    p.drawEllipse(QRectF(4, 4, 24, 24))
    p.setBrush(QBrush(BLANCO))
    f = QFont("Georgia", 15, QFont.Weight.Bold)
    p.setFont(f); p.setPen(_pen(BLANCO, 1))
    p.drawText(QRectF(4, 3, 24, 26), Qt.AlignmentFlag.AlignCenter, "i")


# ── Iconos: NAVEGADOR (pestanas) ─────────────────────────────
def _equilibrio(p):
    # Separador flash (tambor horizontal): gas azul arriba, liquido ambar
    # UNIFORME abajo, con salida de vapor (arriba) y de liquido (abajo).
    OIL = QColor("#D9A441"); GAS = QColor("#AFCDE8"); OUT = QColor("#4A4A4A")
    drum = QRectF(4, 10, 24, 13)
    path = QPainterPath(); path.addRoundedRect(drum, 6, 6)
    p.setClipPath(path)
    p.fillRect(QRectF(4, 10, 24, 6.5), GAS)
    p.fillRect(QRectF(4, 16.5, 24, 6.5), OIL)
    p.setClipping(False)
    p.setPen(_pen(OUT, 1.6)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(drum, 6, 6)
    p.setPen(_pen(OUT, 0.9)); p.drawLine(QPointF(6, 16.5), QPointF(26, 16.5))
    p.setPen(_pen(QColor("#1F5FA8"), 1.6))
    p.drawLine(QPointF(23, 10), QPointF(23, 4))
    p.drawPolyline(_poly([(21, 6), (23, 4), (25, 6)]))
    p.setPen(_pen(QColor("#B87A1C"), 1.6))
    p.drawLine(QPointF(9, 23), QPointF(9, 29))
    p.drawPolyline(_poly([(7, 27), (9, 29), (11, 27)]))


def _envolvente(p):
    # Envolvente de fases con la forma clasica (lazo tipo domo inclinado):
    # rama de burbuja (rojo) y rama de rocio (azul) que se unen en el critico.
    p.setPen(_pen(QColor("#8A8A8A"), 1.3))
    p.drawLine(QPointF(6, 4), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(28, 27))
    bub = QPainterPath(); bub.moveTo(9, 25)
    bub.cubicTo(8, 12, 16, 6, 21, 10)          # rama de burbuja
    p.setPen(_pen(QColor("#C0392B"), 2.2)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(bub)
    dew = QPainterPath(); dew.moveTo(21, 10)
    dew.cubicTo(27, 14, 22, 24, 12, 25)        # rama de rocio
    p.setPen(_pen(QColor("#1F5FA8"), 2.2))
    p.drawPath(dew)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#333333")))
    p.drawEllipse(QRectF(19.35, 8.35, 3.3, 3.3))   # punto critico


def _saturacion(p):
    # Misma envolvente clasica, destacando los puntos de saturacion (burbuja
    # y rocio) unidos por una isobara.
    p.setPen(_pen(QColor("#8A8A8A"), 1.3))
    p.drawLine(QPointF(6, 4), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(28, 27))
    env = QPainterPath(); env.moveTo(9, 25)
    env.cubicTo(8, 12, 16, 6, 21, 10)
    env.cubicTo(27, 14, 22, 24, 12, 25)
    p.setPen(_pen(QColor("#B8860B"), 2.0)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(env)
    yb = 16.7
    p.setPen(_pen(QColor("#9A9A9A"), 1.0, cap=Qt.PenCapStyle.FlatCap))
    p.drawLine(QPointF(9.8, yb), QPointF(23.3, yb))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor("#C0392B"))); p.drawEllipse(QRectF(8.2, yb - 1.6, 3.2, 3.2))
    p.setBrush(QBrush(QColor("#1F5FA8"))); p.drawEllipse(QRectF(21.7, yb - 1.6, 3.2, 3.2))


def _propiedades(p):
    # Grafico de barras sobre ejes (como el icono anterior), en color.
    p.setPen(_pen(QColor("#8A8A8A"), 1.4))
    p.drawLine(QPointF(6, 4), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(28, 27))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor("#1F5FA8"))); p.drawRect(QRectF(9, 18, 4, 9))
    p.setBrush(QBrush(QColor("#2E8B57"))); p.drawRect(QRectF(15, 13, 4, 14))
    p.setBrush(QBrush(QColor("#C0392B"))); p.drawRect(QRectF(21, 9, 4, 18))


def _parametros(p):
    # Matriz kij tipo hoja de calculo: cabecera azul y celda resaltada verde.
    OUT = QColor("#666666")
    p.setPen(_pen(OUT, 1.4)); p.setBrush(QBrush(QColor("#FFFFFF")))
    p.drawRect(QRectF(5, 6, 22, 20))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#6E97C6")))
    p.drawRect(QRectF(5, 6, 22, 5))
    p.setBrush(QBrush(QColor("#EDEDE4"))); p.drawRect(QRectF(5, 11, 6, 15))
    p.setBrush(QBrush(QColor("#B7D8A8"))); p.drawRect(QRectF(11, 16, 6, 5))
    p.setPen(_pen(QColor("#C8C8C8"), 1.0))
    for i in range(1, 4):
        p.drawLine(QPointF(5 + 6 * i, 6), QPointF(5 + 6 * i, 26))
    for j in range(1, 4):
        p.drawLine(QPointF(5, 6 + 5 * j), QPointF(27, 6 + 5 * j))
    p.setPen(_pen(OUT, 1.4)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRect(QRectF(5, 6, 22, 20))


def _corriente(p):
    # Flama de gas (poder calorifico / GPM / BOE)
    path = QPainterPath()
    path.moveTo(16, 3)
    path.cubicTo(23, 10, 24, 15, 20, 20)
    path.cubicTo(22, 15, 18, 13, 18, 9)
    path.cubicTo(15, 13, 9, 15, 11, 22)
    path.cubicTo(8, 18, 8, 24, 12, 27)
    path.cubicTo(16, 30, 24, 28, 24, 20)
    path.cubicTo(24, 14, 20, 10, 16, 3)
    grad = QLinearGradient(16, 3, 16, 29)
    grad.setColorAt(0.0, AMBAR)
    grad.setColorAt(1.0, ROJO)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(grad))
    p.drawPath(path)
    # Nucleo azul
    inner = QPainterPath()
    inner.moveTo(15, 17)
    inner.cubicTo(19, 20, 19, 25, 15, 27)
    inner.cubicTo(12, 25, 12, 20, 15, 17)
    p.setBrush(QBrush(QColor("#EAF3FF"))); p.drawPath(inner)


# ── Iconos de la barra de herramientas (selectores globales) ─────────
def _eos(p):
    # Isoterma en diagrama P-V (construccion de Van der Waals): de mayor a
    # menor volumen -> rama gaseosa suave, meseta bifasica horizontal y rama
    # liquida empinada. Solo la isoterma (sin campana).
    p.setPen(_pen(QColor("#8A8A8A"), 1.4))
    p.drawLine(QPointF(6, 4), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(29, 27))
    iso = QPainterPath()
    iso.moveTo(10, 6)
    iso.cubicTo(10.6, 10, 11.2, 14, 12, 17)   # rama liquida empinada
    iso.lineTo(21, 17)                          # meseta bifasica horizontal
    iso.cubicTo(23.5, 17.6, 25.5, 21, 28, 23)  # rama gaseosa suave
    p.setPen(_pen(QColor("#C0392B"), 2.3)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(iso)


def _densidad(p):
    # Probeta con liquido (azul, buen contraste) y un hidrometro con peso rojo.
    OUT = QColor("#4A4A4A")
    cil = QPainterPath()
    cil.moveTo(11, 5); cil.lineTo(11, 22)
    cil.quadTo(11, 26, 16, 26); cil.quadTo(21, 26, 21, 22); cil.lineTo(21, 5)
    p.setPen(_pen(OUT, 1.6)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(cil)
    liq = QPainterPath()
    liq.moveTo(12, 13.5); liq.lineTo(12, 22)
    liq.quadTo(12, 24.6, 16, 24.6); liq.quadTo(20, 24.6, 20, 22); liq.lineTo(20, 13.5)
    liq.closeSubpath()
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#5A86BE")))
    p.drawPath(liq)
    p.setPen(_pen(QColor("#333333"), 1.0)); p.setBrush(QBrush(QColor("#FDFDFD")))
    p.drawRoundedRect(QRectF(14.6, 6.5, 2.8, 12.5), 1.2, 1.2)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#C0392B")))
    p.drawEllipse(QRectF(13.4, 18, 5.2, 5.2))


def _unidades(p):
    # Manometro / dial de medicion (buen contraste: gris + aguja roja).
    import math
    cx, cy, r = 16.0, 17.0, 10.5
    p.setPen(_pen(QColor("#4A4A4A"), 1.6)); p.setBrush(QBrush(QColor("#FDFDFD")))
    p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
    p.setPen(_pen(QColor("#4A4A4A"), 1.0))
    for ang in (180, 135, 90, 45, 0):
        rad = math.radians(ang)
        ox, oy = cx + r * math.cos(rad), cy - r * math.sin(rad)
        ix, iy = cx + (r - 2.4) * math.cos(rad), cy - (r - 2.4) * math.sin(rad)
        p.drawLine(QPointF(ox, oy), QPointF(ix, iy))
    p.setPen(_pen(QColor("#C0392B"), 1.9))
    p.drawLine(QPointF(cx, cy), QPointF(cx + 5.5, cy - 5.8))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#333333")))
    p.drawEllipse(QRectF(cx - 1.7, cy - 1.7, 3.4, 3.4))


# ── Registro nombre -> funcion de dibujo ─────────────────────
_REGISTRO = {
    # archivo
    "nuevo": _nuevo_doc, "abrir": _abrir, "guardar": _guardar,
    "guardar_como": _guardar_como, "imprimir": _imprimir,
    # edicion
    "cortar": _cortar, "copiar": _copiar, "pegar": _pegar,
    "deshacer": _deshacer, "rehacer": _rehacer,
    # calculos
    "fraccion_masica": _fraccion_masica, "normalizar": _normalizar,
    "ejecutar": _ejecutar, "detener": _detener,
    # unidades
    "sistema": _sistema, "conversor": _conversor,
    # datos
    "componentes": _componentes, "fluidos": _fluidos, "mezclas": _mezclas,
    # herramientas
    "tablas": _tablas, "calculadora": _calculadora, "graficas": _graficas,
    # preferencias
    "opciones": _opciones, "configuracion": _configuracion,
    # ayuda
    "ayuda": _ayuda, "acerca": _acerca,
    # navegador / pestanas
    "equilibrio": _equilibrio, "envolvente": _envolvente,
    "saturacion": _saturacion, "propiedades": _propiedades,
    "parametros": _parametros, "corriente": _corriente,
    # barra de herramientas
    "eos": _eos, "densidad": _densidad, "unidades": _unidades,
}

# Cache: (nombre, tam) -> QIcon
_CACHE = {}


def _desaturar(pm):
    """Convierte un QPixmap a escala de grises conservando el canal alfa.
    Garantiza el resultado monocromatico aunque un icono use algun color
    puntual embebido en su funcion de dibujo."""
    img = pm.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    for y in range(img.height()):
        for x in range(img.width()):
            px = img.pixel(x, y)
            a = qAlpha(px)
            if a == 0:
                continue
            g = qGray(px)
            img.setPixel(x, y, qRgba(g, g, g, a))
    return QPixmap.fromImage(img)


def icono(nombre, tam=32):
    """Devuelve un QIcon con el glifo pedido, escalado a `tam` px.

    Si el nombre no existe, devuelve un QIcon vacio (no falla), de modo que
    un boton sin icono definido simplemente muestra su texto.
    """
    clave = (nombre, tam)
    if clave in _CACHE:
        return _CACHE[clave]
    fn = _REGISTRO.get(nombre)
    if fn is None:
        ic = QIcon()
        _CACHE[clave] = ic
        return ic
    pm, p = _nuevo(tam)
    try:
        fn(p)
    finally:
        p.end()
    ic = QIcon(pm)
    _CACHE[clave] = ic
    return ic


def pixmap(nombre, tam=32):
    """Igual que icono() pero devuelve el QPixmap (util para QLabel)."""
    fn = _REGISTRO.get(nombre)
    pm, p = _nuevo(tam)
    if fn is not None:
        try:
            fn(p)
        finally:
            p.end()
    else:
        p.end()
    return pm

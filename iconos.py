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
    QFont, QLinearGradient
)
from PyQt6.QtCore import Qt, QPointF, QRectF

# ── Paleta office ────────────────────────────────────────────
AZUL      = QColor("#2D6CDF")   # azul office primario
AZUL_OSC  = QColor("#1A4FA8")   # azul profundo (liquido)
AZUL_CLR  = QColor("#7FA9E8")
GRIS      = QColor("#6E6E6E")
GRIS_CLR  = QColor("#B8B8B8")
ROJO_OX   = QColor("#A83218")   # rojo oxido (envolvente / vapor)
ROJO      = QColor("#D0392B")   # rojo detener
VERDE      = QColor("#2E9E4F")  # verde ejecutar
AMBAR     = QColor("#E0902F")   # ambar (gas / flama)
BLANCO    = QColor("#FFFFFF")
NEGRO     = QColor("#303030")
PAPEL     = QColor("#FCFCFC")


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
    _cilindro(p, QColor("#CBB2E0"), QColor("#7A4FA0"))
    p.setPen(_pen(QColor("#7A4FA0"), 1.2))
    p.drawArc(QRectF(7, 11, 18, 6), 0, -180 * 16)
    p.drawArc(QRectF(7, 16, 18, 6), 0, -180 * 16)


def _fluidos(p):
    # Gota
    path = QPainterPath()
    path.moveTo(16, 5)
    path.cubicTo(24, 15, 25, 20, 16, 27)
    path.cubicTo(7, 20, 8, 15, 16, 5)
    p.setPen(_pen(AZUL_OSC, 1.4))
    grad = QLinearGradient(16, 5, 16, 27)
    grad.setColorAt(0, AZUL_CLR); grad.setColorAt(1, AZUL_OSC)
    p.setBrush(QBrush(grad))
    p.drawPath(path)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(BLANCO))
    p.drawEllipse(QRectF(12, 16, 3, 4))


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
    # Gota partida vapor/liquido
    path = QPainterPath()
    path.moveTo(16, 5)
    path.cubicTo(24, 15, 25, 20, 16, 27)
    path.cubicTo(7, 20, 8, 15, 16, 5)
    p.setPen(_pen(GRIS, 1.4))
    p.setBrush(QBrush(QColor("#EAF0FB")))
    p.drawPath(path)
    p.setClipPath(path)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL_OSC))
    p.drawRect(QRectF(16, 4, 12, 26))          # mitad liquida
    p.setClipping(False)
    p.setPen(_pen(GRIS, 1.0))
    p.drawLine(QPointF(16, 6), QPointF(16, 26))


def _envolvente(p):
    # Curva envolvente P-T con punto critico
    p.setPen(_pen(GRIS, 1.4))
    p.drawLine(QPointF(6, 4), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(28, 27))
    path = QPainterPath()
    path.moveTo(9, 25)
    path.cubicTo(8, 12, 16, 6, 21, 10)         # rama burbuja
    path.cubicTo(27, 14, 22, 24, 12, 25)       # rama rocio
    p.setPen(_pen(ROJO_OX, 2.2)); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(path)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL))
    p.drawEllipse(QRectF(19.5, 8.5, 3.4, 3.4))  # punto critico


def _saturacion(p):
    # Marcador X sobre curva
    p.setPen(_pen(GRIS, 1.4))
    p.drawLine(QPointF(5, 26), QPointF(27, 26))
    p.setPen(_pen(AZUL_CLR, 1.8))
    p.drawArc(QRectF(6, 6, 20, 30), 20 * 16, 140 * 16)
    p.setPen(_pen(ROJO, 2.4))
    p.drawLine(QPointF(12, 10), QPointF(20, 18))
    p.drawLine(QPointF(20, 10), QPointF(12, 18))


def _propiedades(p):
    # H-S: barras + curva
    p.setPen(_pen(GRIS, 1.4))
    p.drawLine(QPointF(6, 4), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(28, 27))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(AZUL))
    p.drawRect(QRectF(9, 18, 4, 9))
    p.setBrush(QBrush(AZUL_CLR)); p.drawRect(QRectF(15, 13, 4, 14))
    p.setBrush(QBrush(ROJO_OX)); p.drawRect(QRectF(21, 9, 4, 18))


def _parametros(p):
    # Matriz kij (rejilla)
    p.setPen(_pen(AZUL_OSC, 1.4))
    p.setBrush(QBrush(BLANCO))
    p.drawRect(QRectF(6, 6, 20, 20))
    p.setPen(_pen(AZUL_CLR, 1.0))
    for i in range(1, 4):
        p.drawLine(QPointF(6 + i * 5, 6), QPointF(6 + i * 5, 26))
        p.drawLine(QPointF(6, 6 + i * 5), QPointF(26, 6 + i * 5))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor("#D8E4F5")))
    for k in range(4):
        p.drawRect(QRectF(6 + k * 5, 6 + k * 5, 5, 5))   # diagonal


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
}

# Cache: (nombre, tam) -> QIcon
_CACHE = {}


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

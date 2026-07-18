"""
ribbon.py — Barra de herramientas clasica (Win95) y panel Navegador lateral.

Estetica retro monocromatica: gris #C0C0C0, biseles 3D (luz arriba-izquierda,
sombra abajo-derecha), Arial Narrow. La antigua "cinta" office se sustituyo
por una barra de herramientas delgada de iconos pequenos, mas fiel al estilo
clasico de Windows.

API publica (sin cambios para el resto del programa):
    construir_ribbon(acciones) -> (QWidget barra, dict de botones)
    NavigatorPanel  — panel lateral con arbol de Calculos y Datos.
"""
from PyQt6.QtWidgets import (
    QWidget, QToolButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QScrollArea, QTreeWidget, QTreeWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from iconos import icono

# ── Paleta clasica Win95 (monocromatica) ─────────────────────
FUENTE_UI  = "Arial Narrow"
CARA       = "#C0C0C0"   # gris de cara de control
LUZ        = "#FFFFFF"   # highlight (borde superior-izq)
LUZ2       = "#DFDFDF"
SOMBRA     = "#808080"   # sombra (borde inferior-der)
SOMBRA_OSC = "#404040"
BORDE      = "#808080"
TXT        = "#000000"
SEL_BG     = "#000080"   # azul de seleccion clasico
SEL_TXT    = "#FFFFFF"
HDR_TXT    = "#000000"

# Barra de herramientas: (clave, texto/tooltip, icono). Los None son
# separadores de grupo (linea vertical grabada).
_TOOLBAR = [
    ("nuevo",        "Nuevo",             "nuevo"),
    ("abrir",        "Abrir",             "abrir"),
    ("guardar",      "Guardar",           "guardar"),
    ("guardar_como", "Guardar como",      "guardar_como"),
    ("imprimir",     "Imprimir",          "imprimir"),
    (None, None, None),
    ("deshacer",     "Deshacer",          "deshacer"),
    ("rehacer",      "Rehacer",           "rehacer"),
    ("copiar",       "Copiar",            "copiar"),
    ("pegar",        "Pegar",             "pegar"),
    (None, None, None),
    ("fraccion",     "Fracción másica",   "fraccion_masica"),
    ("normalizar",   "Normalizar",        "normalizar"),
    ("ejecutar",     "Realizar cálculo",  "ejecutar"),
    ("detener",      "Detener",           "detener"),
    (None, None, None),
    ("componentes",  "Componentes",       "componentes"),
    ("fluidos",      "Fluidos",           "fluidos"),
    (None, None, None),
    ("acerca",       "Acerca de",         "acerca"),
]

# Items del arbol "Cálculos": (clave, texto). La clave abre la subventana MDI.
NAV_CALCULOS = [
    ("equilibrio",  "Equilibrio de fases"),
    ("envolvente",  "Envolvente de fases"),
    ("saturacion",  "Puntos de saturación"),
    ("propiedades", "Propiedades termodinámicas"),
    ("corriente",   "Propiedades de la corriente"),
    ("parametros",  "Parámetros de la ecuación de estado"),
]

# Accesos del arbol "Datos": (icono, texto, clave)
NAV_DATOS = [
    ("componentes", "Componentes", "componentes"),
    ("fluidos",     "Fluidos",     "fluidos"),
]


# ── Botones y separadores estilo Win95 ───────────────────────
_BTN_QSS = (
    f'QToolButton {{ border:1px solid transparent; background:transparent;'
    f' padding:1px; }}'
    f'QToolButton:hover {{ background:{CARA};'
    f' border-top:1px solid {LUZ}; border-left:1px solid {LUZ};'
    f' border-right:1px solid {SOMBRA_OSC}; border-bottom:1px solid {SOMBRA_OSC}; }}'
    f'QToolButton:pressed, QToolButton:checked {{ background:{CARA};'
    f' border-top:1px solid {SOMBRA_OSC}; border-left:1px solid {SOMBRA_OSC};'
    f' border-right:1px solid {LUZ}; border-bottom:1px solid {LUZ}; }}'
    f'QToolButton:disabled {{ }}'
)


class SepVertical(QWidget):
    """Separador vertical grabado (sombra + luz), estilo clasico."""
    def __init__(self, alto=22, parent=None):
        super().__init__(parent)
        self.setFixedSize(6, alto)

    def paintEvent(self, e):
        from PyQt6.QtGui import QPainter, QColor
        p = QPainter(self)
        x = 2; h = self.height()
        p.setPen(QColor(SOMBRA))
        p.drawLine(x, 2, x, h - 3)
        p.setPen(QColor(LUZ))
        p.drawLine(x + 1, 2, x + 1, h - 3)
        p.end()


class ToolBtn(QToolButton):
    def __init__(self, texto, nombre_icono, parent=None):
        super().__init__(parent)
        self.setToolTip(texto)
        self.setIcon(icono(nombre_icono, 20))
        self.setIconSize(QSize(20, 20))
        self.setFixedSize(QSize(26, 26))
        self.setStyleSheet(_BTN_QSS)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


def construir_ribbon(acciones=None):
    """Barra de herramientas clasica. Devuelve (barra, {clave: ToolBtn})."""
    acciones = acciones or {}
    barra = QFrame()
    barra.setFixedHeight(32)
    # Cara gris con una linea de luz arriba y sombra abajo (barra elevada).
    barra.setStyleSheet(
        f'QFrame {{ background:{CARA};'
        f' border-top:1px solid {LUZ};'
        f' border-bottom:1px solid {SOMBRA}; }}')
    lay = QHBoxLayout(barra)
    lay.setContentsMargins(4, 2, 4, 2)
    lay.setSpacing(1)
    lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    botones = {}
    for clave, texto, ic in _TOOLBAR:
        if clave is None:
            lay.addWidget(SepVertical(22))
            continue
        b = ToolBtn(texto, ic)
        fn = acciones.get(clave)
        if fn is not None:
            b.clicked.connect(fn)
        botones[clave] = b
        lay.addWidget(b)
    lay.addStretch()
    return barra, botones


# ══════════════════════════════════════════════════════════════
# Panel Navegador lateral (docked, estilo clasico)
# ══════════════════════════════════════════════════════════════
def _seccion(texto):
    """Cabecera de seccion: etiqueta en negrita + linea grabada debajo."""
    cont = QWidget()
    v = QVBoxLayout(cont)
    v.setContentsMargins(0, 4, 0, 1)
    v.setSpacing(1)
    lbl = QLabel(texto)
    lbl.setStyleSheet(
        f'background:transparent; color:{HDR_TXT};'
        f' font-family:"{FUENTE_UI}"; font-size:10pt; font-weight:bold;')
    v.addWidget(lbl)
    linea = QFrame()
    linea.setFixedHeight(2)
    linea.setStyleSheet(
        f'background:{CARA}; border-top:1px solid {SOMBRA};'
        f' border-bottom:1px solid {LUZ};')
    v.addWidget(linea)
    return cont


def _tree_base():
    t = QTreeWidget()
    t.setHeaderHidden(True)
    t.setIndentation(14)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    # Borde hundido (inset) clasico alrededor del arbol.
    t.setStyleSheet(
        f'QTreeWidget {{ background:#FFFFFF; color:{TXT};'
        f' font-family:"{FUENTE_UI}"; font-size:10pt; outline:0;'
        f' border-top:1px solid {SOMBRA}; border-left:1px solid {SOMBRA};'
        f' border-right:1px solid {LUZ}; border-bottom:1px solid {LUZ}; }}'
        f'QTreeWidget::item {{ height:22px; padding-left:2px; }}'
        f'QTreeWidget::item:selected {{ background:{SEL_BG}; color:{SEL_TXT}; }}'
        f'QTreeWidget::item:hover {{ background:#D8D8E8; }}')
    return t


class NavigatorPanel(QWidget):
    """Panel lateral izquierdo (docked) con barra de titulo 'Navegador' y X,
    arbol de Calculos (abre subventanas) y accesos a Datos."""

    calculo_pedido = pyqtSignal(str)   # clave del calculo a abrir
    dato_pedido    = pyqtSignal(str)   # clave de dato (componentes, fluidos)
    cerrar_pedido  = pyqtSignal()      # X de la barra de titulo del panel

    ANCHO = 244

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(self.ANCHO)
        self.setStyleSheet(f'background:{CARA};')
        self._leaf_por_clave = {}
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(2, 2, 2, 2)
        outer.setSpacing(2)

        # ── Barra de titulo del panel (docked) ───────────────
        cap = QFrame()
        cap.setFixedHeight(20)
        cap.setStyleSheet(
            f'QFrame {{ background:{CARA};'
            f' border-top:1px solid {LUZ}; border-left:1px solid {LUZ};'
            f' border-right:1px solid {SOMBRA}; border-bottom:1px solid {SOMBRA}; }}')
        hc = QHBoxLayout(cap)
        hc.setContentsMargins(5, 0, 2, 0); hc.setSpacing(0)
        tit = QLabel("Navegador")
        tit.setStyleSheet(
            f'background:transparent; color:{TXT};'
            f' font-family:"{FUENTE_UI}"; font-size:10pt; font-weight:bold;')
        hc.addWidget(tit); hc.addStretch()
        x = QToolButton()
        x.setText("✕")
        x.setFixedSize(16, 16)
        x.setStyleSheet(
            f'QToolButton {{ background:{CARA}; color:{TXT};'
            f' font-family:"{FUENTE_UI}"; font-size:8pt;'
            f' border-top:1px solid {LUZ}; border-left:1px solid {LUZ};'
            f' border-right:1px solid {SOMBRA_OSC}; border-bottom:1px solid {SOMBRA_OSC}; }}'
            f'QToolButton:pressed {{'
            f' border-top:1px solid {SOMBRA_OSC}; border-left:1px solid {SOMBRA_OSC};'
            f' border-right:1px solid {LUZ}; border-bottom:1px solid {LUZ}; }}')
        x.setCursor(Qt.CursorShape.PointingHandCursor)
        x.clicked.connect(self.cerrar_pedido.emit)
        hc.addWidget(x)
        outer.addWidget(cap)

        # Contenido (con scroll para alturas pequenas)
        cont = QWidget()
        cont.setStyleSheet(f'background:{CARA};')
        v = QVBoxLayout(cont)
        v.setContentsMargins(4, 2, 4, 4)
        v.setSpacing(2)

        # ── Cálculos ─────────────────────────────────────────
        v.addWidget(_seccion("Cálculos"))
        self.tree_calc = _tree_base()
        self.tree_calc.setRootIsDecorated(True)
        raiz = QTreeWidgetItem(["Cálculos"])
        raiz.setFlags(raiz.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        f = raiz.font(0); f.setBold(True); raiz.setFont(0, f)
        self.tree_calc.addTopLevelItem(raiz)
        for clave, texto in NAV_CALCULOS:
            it = QTreeWidgetItem([texto])
            it.setIcon(0, icono(clave, 16))
            it.setData(0, Qt.ItemDataRole.UserRole, clave)
            raiz.addChild(it)
            self._leaf_por_clave[clave] = it
        raiz.setExpanded(True)
        self.tree_calc.itemClicked.connect(self._on_calc_click)
        self.tree_calc.setFixedHeight(24 + 22 * (len(NAV_CALCULOS) + 1))
        v.addWidget(self.tree_calc)

        # ── Datos ────────────────────────────────────────────
        v.addWidget(_seccion("Datos"))
        self.tree_datos = _tree_base()
        self.tree_datos.setRootIsDecorated(False)
        for nombre_ic, texto, clave in NAV_DATOS:
            it = QTreeWidgetItem([texto])
            it.setIcon(0, icono(nombre_ic, 16))
            it.setData(0, Qt.ItemDataRole.UserRole, clave)
            self.tree_datos.addTopLevelItem(it)
        self.tree_datos.itemClicked.connect(self._on_dato_click)
        self.tree_datos.setFixedHeight(24 + 22 * len(NAV_DATOS))
        v.addWidget(self.tree_datos)

        v.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(cont)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f'QScrollArea {{ background:{CARA}; border:none; }}')
        outer.addWidget(scroll, 1)

    # ── Slots ────────────────────────────────────────────────
    def _on_calc_click(self, item, col):
        clave = item.data(0, Qt.ItemDataRole.UserRole)
        if clave:
            self.calculo_pedido.emit(str(clave))

    def _on_dato_click(self, item, col):
        clave = item.data(0, Qt.ItemDataRole.UserRole)
        if clave:
            self.dato_pedido.emit(str(clave))

    def sincronizar(self, clave):
        it = self._leaf_por_clave.get(clave)
        self.tree_calc.blockSignals(True)
        if it is not None:
            self.tree_calc.setCurrentItem(it)
        else:
            self.tree_calc.clearSelection()
        self.tree_calc.blockSignals(False)

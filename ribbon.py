"""
ribbon.py — Barra de selectores globales y panel Navegador lateral (retro).

La barra superior ya no tiene botones de iconos: contiene tres listas
desplegables globales (Ecuacion de estado, Metodo de densidad y Metodo de
envolvente) cuya seleccion se propaga a la ventana correspondiente. El
navegador conserva el arbol de Calculos y los accesos de Datos.

Estetica: monocromatica, grises claros, sin relieve 3D en los controles,
Arial Narrow.

API publica:
    construir_ribbon() -> (QWidget barra, dict de QComboBox {eos,densidad,envolvente})
    NavigatorPanel
"""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QFrame,
    QScrollArea, QTreeWidget, QTreeWidgetItem, QAbstractItemView, QListView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette, QColor

from iconos import icono

# ── Paleta clasica clara (monocromatica) ─────────────────────
FUENTE_UI  = "Arial Narrow"
CARA       = "#D4D4D4"   # gris de cara (mas claro que antes)
LUZ        = "#FFFFFF"
SOMBRA     = "#A8A8A8"
SOMBRA_OSC = "#8A8A8A"
BORDE      = "#A8A8A8"
TXT        = "#000000"
SEL_BG     = "#DCDCDC"
SEL_TXT    = "#000000"
HDR_TXT    = "#000000"

# ── Selectores globales de la barra: (clave, etiqueta, items) ─
_SELECTORES = [
    ("eos",        "Ecuación de estado:", ["Peng-Robinson", "SRK"]),
    ("densidad",   "Densidad:",           ["COSTALD", "EOS"]),
    ("envolvente", "Método envolvente:",  ["Ziervogel-Poling", "Michelsen"]),
]

# Items del arbol "Cálculos": (clave, texto). La clave abre la subventana MDI.
NAV_CALCULOS = [
    ("equilibrio",  "Equilibrio de fases"),
    ("envolvente",  "Envolvente de fases"),
    ("saturacion",  "Puntos de saturación"),
    ("propiedades", "Propiedades termodinámicas"),
    ("parametros",  "Parámetros de la ecuación de estado"),
]

# Accesos del arbol "Datos": (icono, texto, clave)
NAV_DATOS = [
    ("componentes", "Componentes", "componentes"),
    ("fluidos",     "Fluidos",     "fluidos"),
]

# Estilo plano (sin relieve) de las listas desplegables de la barra.
_COMBO_QSS = (
    f'QComboBox {{ background:#FFFFFF; color:{TXT};'
    f' border:1px solid {BORDE}; padding:1px 4px;'
    f' font-family:"{FUENTE_UI}"; font-size:10pt; min-height:20px; }}'
    f'QComboBox:hover {{ border:1px solid {SOMBRA_OSC}; }}'
    f'QComboBox::drop-down {{ border:none; width:16px; }}'
    f'QComboBox QAbstractItemView {{ background:#FFFFFF; color:{TXT};'
    f' border:1px solid {BORDE}; outline:0;'
    f' selection-background-color:{SEL_BG}; selection-color:{SEL_TXT}; }}'
)


def construir_ribbon(acciones=None):
    """Barra superior de selectores globales.

    Devuelve (barra, {clave: QComboBox}) con claves 'eos', 'densidad' y
    'envolvente'. El parametro `acciones` se mantiene por compatibilidad
    pero ya no se usa (la barra no tiene botones)."""
    barra = QFrame()
    barra.setFixedHeight(34)
    barra.setStyleSheet(
        f'QFrame {{ background:{CARA}; border-bottom:1px solid {SOMBRA}; }}')
    lay = QHBoxLayout(barra)
    lay.setContentsMargins(8, 3, 8, 3)
    lay.setSpacing(6)
    lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def _lbl(txt):
        l = QLabel(txt)
        l.setStyleSheet(
            f'background:transparent; color:{TXT};'
            f' font-family:"{FUENTE_UI}"; font-size:10pt;')
        return l

    combos = {}
    for i, (clave, etiqueta, items) in enumerate(_SELECTORES):
        lay.addWidget(_lbl(etiqueta))
        cmb = QComboBox()
        cmb.addItems(items)
        vista = QListView()
        # Forzar el color de resaltado de la LISTA a gris (el QListView usa la
        # paleta, no el QSS, para el highlight de la seleccion).
        pal = vista.palette()
        pal.setColor(QPalette.ColorRole.Highlight, QColor("#DCDCDC"))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        vista.setPalette(pal)
        vista.setStyleSheet(
            'QListView { background:#FFFFFF; color:#000000; outline:0; }'
            'QListView::item:selected { background:#DCDCDC; color:#000000; }'
            'QListView::item:hover { background:#ECECEC; color:#000000; }')
        cmb.setView(vista)
        cmb.setStyleSheet(_COMBO_QSS)
        cmb.setFixedWidth(148)
        cmb.setCursor(Qt.CursorShape.PointingHandCursor)
        combos[clave] = cmb
        lay.addWidget(cmb)
        if i < len(_SELECTORES) - 1:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setStyleSheet(f'color:{SOMBRA}; background:{SOMBRA};')
            sep.setFixedWidth(1)
            lay.addSpacing(4); lay.addWidget(sep); lay.addSpacing(4)
    lay.addStretch()
    return barra, combos


# ══════════════════════════════════════════════════════════════
# Panel Navegador lateral (docked, estilo clasico)
# ══════════════════════════════════════════════════════════════
def _seccion(texto):
    cont = QWidget()
    v = QVBoxLayout(cont)
    v.setContentsMargins(0, 4, 0, 1)
    v.setSpacing(1)
    lbl = QLabel(texto)
    lbl.setStyleSheet(
        f'background:transparent; color:{HDR_TXT};'
        f' font-family:"{FUENTE_UI}"; font-size:10pt;')
    v.addWidget(lbl)
    linea = QFrame()
    linea.setFixedHeight(1)
    linea.setStyleSheet('background:#C4C4C4; border:none;')
    v.addWidget(linea)
    return cont


def _tree_base():
    t = QTreeWidget()
    t.setHeaderHidden(True)
    t.setIndentation(14)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setStyleSheet(
        f'QTreeWidget {{ background:#FFFFFF; color:{TXT};'
        f' font-family:"{FUENTE_UI}"; font-size:10pt; outline:0;'
        f' border:1px solid #7F7F7F; }}'
        f'QTreeWidget::item {{ height:22px; padding-left:2px; }}'
        f'QTreeWidget::item:selected {{ background:#DCDCDC; color:{TXT}; }}'
        f'QTreeWidget::item:hover {{ background:#EDEDED; }}')
    return t


class NavigatorPanel(QWidget):
    """Panel lateral con barra de titulo 'Navegador' + X, arbol de Calculos
    (abre subventanas) y accesos a Datos."""

    calculo_pedido = pyqtSignal(str)
    dato_pedido    = pyqtSignal(str)
    cerrar_pedido  = pyqtSignal()

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

        # Barra de titulo del panel (plana, sin relieve ni boton X)
        cap = QFrame()
        cap.setFixedHeight(20)
        cap.setStyleSheet(
            f'QFrame {{ background:{CARA}; border:none;'
            f' border-bottom:1px solid #C4C4C4; }}')
        hc = QHBoxLayout(cap)
        hc.setContentsMargins(5, 0, 2, 0); hc.setSpacing(0)
        tit = QLabel("Navegador")
        tit.setStyleSheet(
            f'background:transparent; color:{TXT};'
            f' font-family:"{FUENTE_UI}"; font-size:10pt;')
        hc.addWidget(tit); hc.addStretch()
        outer.addWidget(cap)

        cont = QWidget()
        cont.setStyleSheet(f'background:{CARA};')
        v = QVBoxLayout(cont)
        v.setContentsMargins(4, 2, 4, 4)
        v.setSpacing(2)

        # Cálculos
        v.addWidget(_seccion("Cálculos"))
        self.tree_calc = _tree_base()
        self.tree_calc.setRootIsDecorated(True)
        raiz = QTreeWidgetItem(["Cálculos"])
        raiz.setFlags(raiz.flags() & ~Qt.ItemFlag.ItemIsSelectable)
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

        # Datos
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

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
try:
    from eos import NOMBRES as _NOMBRES_COMP
except Exception:
    _NOMBRES_COMP = []

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
    ("eos",        "Ecuación de estado:", ["Peng-Robinson (HYSYS)", "SRK (HYSYS)",
                                           "Peng-Robinson (PVTsim)", "SRK (PVTsim)"]),
    ("densidad",   "Densidad:",           ["COSTALD", "EOS"]),
    ("volumen",    "Corrección de volumen:", ["Ninguna", "Peneloux"]),
    ("envolvente", "Método envolvente:",  ["Ziervogel-Poling", "Michelsen"]),
    ("unidades",   "Sistema de unidades:", ["Field", "SI"]),
]

# Items del arbol "Cálculos": (clave, texto). La clave abre la subventana MDI.
NAV_CALCULOS = [
    ("equilibrio",  "Equilibrio de fases"),
    ("envolvente",  "Envolvente de fases"),
    ("saturacion",  "Puntos de saturación"),
    ("propiedades", "Análisis de sensibilidad"),
    ("parametros",  "Parámetros de la ecuación de estado"),
]

# Accesos del arbol "Datos": (icono, texto, clave)
NAV_DATOS = [
    ("componentes", "Componentes", "componentes"),
    ("fluidos",     "Fluidos",     "fluidos"),
]

# Funcionalidades que cuelgan de cada fluido en el arbol (nombres abreviados).
FUNC_FLUIDO = [
    ("equilibrio",  "Equilibrio"),
    ("envolvente",  "Envolvente"),
    ("saturacion",  "Saturación"),
    ("propiedades", "Sensibilidad"),
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


class BarraSelectores(QFrame):
    """Barra superior de selectores. Cuando la ventana se achica y no entran
    todos, oculta los selectores de MENOR prioridad (los de la derecha) uno a
    uno —el primero en desaparecer es 'Sistema de unidades'— y los vuelve a
    mostrar al agrandar. Nunca se solapan ni aparece barra de desplazamiento."""
    def __init__(self, grupos):
        super().__init__()
        self._grupos = grupos          # en orden de aparicion (izq->der)
        self.setFixedHeight(34)
        self.setStyleSheet(
            f'QFrame#barraSel {{ background:{CARA};'
            f' border-bottom:1px solid {SOMBRA}; }}')
        self.setObjectName('barraSel')
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 3, 8, 3)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        for g in grupos:
            lay.addWidget(g)
        lay.addStretch()
        # Boton de Documentacion tecnica: SIEMPRE visible, a la derecha
        # (no forma parte de los grupos que se ocultan al achicar).
        from PyQt6.QtWidgets import QToolButton
        from PyQt6.QtCore import QSize
        from iconos import icono
        self.btn_doc = QToolButton()
        self.btn_doc.setIcon(icono("documentacion", 22))
        self.btn_doc.setIconSize(QSize(22, 22))
        self.btn_doc.setToolTip("Documentación técnica")
        self.btn_doc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_doc.setStyleSheet(
            'QToolButton { border:none; background:transparent; padding:3px; }'
            'QToolButton:hover { background:#DCDCDC; border-radius:4px; }')
        lay.addWidget(self.btn_doc)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._reflow()

    def showEvent(self, e):
        super().showEvent(e)
        self._reflow()

    def _reflow(self):
        # Reservamos ~34 px a la derecha para el boton de documentacion.
        avail = self.width() - 18 - 34
        used = 0
        ocultar = False
        for g in self._grupos:
            w = g.sizeHint().width()
            if (not ocultar) and (used + w <= avail):
                g.setVisible(True)
                used += w
            else:
                ocultar = True
                g.setVisible(False)


def construir_ribbon(acciones=None):
    """Barra superior de selectores globales.

    Devuelve (barra, {clave: QComboBox}). La barra oculta progresivamente los
    selectores de la derecha cuando la ventana se hace angosta (empezando por
    'Sistema de unidades') y los restaura al agrandarla."""
    from PyQt6.QtWidgets import QSizePolicy, QWidget
    from PyQt6.QtCore import QSize
    from iconos import icono

    def _lbl(txt):
        l = QLabel(txt)
        l.setStyleSheet(
            f'background:transparent; color:{TXT};'
            f' font-family:"{FUENTE_UI}"; font-size:10pt;')
        l.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        return l

    _ICONO = {"eos": "eos", "densidad": "densidad",
              "volumen": "volumen",
              "envolvente": "envolvente", "unidades": "unidades"}
    combos = {}
    grupos = []
    for i, (clave, etiqueta, items) in enumerate(_SELECTORES):
        grupo = QWidget()
        grupo.setStyleSheet('background:transparent;')
        gl = QHBoxLayout(grupo)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(6)
        gl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # Separador a la izquierda (excepto el primero)
        if i > 0:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setStyleSheet(f'color:{SOMBRA}; background:{SOMBRA};')
            sep.setFixedWidth(1)
            gl.addSpacing(4); gl.addWidget(sep); gl.addSpacing(6)
        # Icono
        nombre_ic = _ICONO.get(clave)
        if nombre_ic:
            ic_lbl = QLabel()
            ic_lbl.setPixmap(icono(nombre_ic, 18).pixmap(QSize(18, 18)))
            ic_lbl.setStyleSheet('background:transparent;')
            ic_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
            gl.addWidget(ic_lbl)
            gl.addSpacing(1)
        gl.addWidget(_lbl(etiqueta))
        cmb = QComboBox()
        cmb.addItems(items)
        vista = QListView()
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
        gl.addWidget(cmb)
        grupo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        grupos.append(grupo)

    barra = BarraSelectores(grupos)
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
    fluido_calc_pedido = pyqtSignal(str, str)   # (nombre_fluido, clave_calculo)
    componente_pedido = pyqtSignal(str)         # nombre del componente
    gestor_comp_pedido = pyqtSignal()           # doble clic en "Componentes"
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

        # Datos (Componentes + Fluidos como arbol expandible)
        v.addWidget(_seccion("Datos"))
        self.tree_datos = _tree_base()
        self.tree_datos.setRootIsDecorated(True)
        # Componentes (nodo expandible: muestra los 13 componentes)
        self._nodo_comp = QTreeWidgetItem(["Componentes"])
        self._nodo_comp.setIcon(0, icono("componentes", 16))
        self._nodo_comp.setData(0, Qt.ItemDataRole.UserRole, "componentes")
        self.tree_datos.addTopLevelItem(self._nodo_comp)
        self._comp_items = []      # hojas de componente en orden canonico
        for nombre in _NOMBRES_COMP:
            txt = nombre.rstrip(':')
            hijo = QTreeWidgetItem([txt])
            # Por defecto todos los componentes estan activos -> verde suave.
            hijo.setIcon(0, icono("componente_hex_activo", 16))
            hijo.setData(0, Qt.ItemDataRole.UserRole, ('comp', txt))
            self._nodo_comp.addChild(hijo)
            self._comp_items.append(hijo)
        self._nodo_comp.setExpanded(False)
        # Fluidos (nodo raiz expandible; sus hijos son los fluidos)
        self._nodo_fluidos = QTreeWidgetItem(["Fluidos"])
        self._nodo_fluidos.setIcon(0, icono("fluidos", 16))
        self._nodo_fluidos.setData(0, Qt.ItemDataRole.UserRole, "fluidos")
        self.tree_datos.addTopLevelItem(self._nodo_fluidos)
        self._nodo_fluidos.setExpanded(True)
        self.tree_datos.itemClicked.connect(self._on_dato_click)
        self.tree_datos.itemDoubleClicked.connect(self._on_dato_double_click)
        self.tree_datos.itemExpanded.connect(lambda *_: self._ajustar_alto_datos())
        self.tree_datos.itemCollapsed.connect(lambda *_: self._ajustar_alto_datos())
        v.addWidget(self.tree_datos)
        self._ajustar_alto_datos()

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
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple) and data and data[0] == 'calc':
            # Hoja de funcionalidad de un fluido: (‘calc’, nombre, clave)
            self.fluido_calc_pedido.emit(data[1], data[2])
        elif isinstance(data, tuple) and data and data[0] == 'comp':
            # Nombre de componente: abrir su ventana de propiedades.
            self.componente_pedido.emit(data[1])
        elif data == 'componentes':
            # Expandir/colapsar para mostrar los 13 componentes.
            item.setExpanded(not item.isExpanded())
        elif isinstance(data, str):
            self.dato_pedido.emit(data)
        else:
            # Nodo de fluido: alternar expandido/colapsado
            item.setExpanded(not item.isExpanded())

    def _on_dato_double_click(self, item, col):
        """Doble clic en el nodo 'Componentes' → abre el gestor de
        componentes (ventana de dos listas para sacar/añadir compuestos).
        El clic simple sigue expandiendo/colapsando el árbol de componentes."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data == 'componentes':
            self.gestor_comp_pedido.emit()

    def set_componentes_activos(self, activos):
        """Recolorea el icono de cada componente: verde suave si esta activo
        (forma parte del fluido) o el hexagono azulado por defecto si esta
        quitado. `activos` es la lista de indices canonicos activos."""
        act = set(activos)
        for i, it in enumerate(getattr(self, '_comp_items', [])):
            nombre = "componente_hex_activo" if i in act else "componente_hex"
            it.setIcon(0, icono(nombre, 16))

    def set_fluidos(self, nombres):
        """Reconstruye el arbol de fluidos: cada fluido con sus 4
        funcionalidades (equilibrio, envolvente, saturacion, propiedades)."""
        nodo = self._nodo_fluidos
        nodo.takeChildren()
        for nombre in nombres:
            fl = QTreeWidgetItem([nombre])
            fl.setData(0, Qt.ItemDataRole.UserRole, ('fluido', nombre))
            nodo.addChild(fl)
            for clave, texto in FUNC_FLUIDO:
                hoja = QTreeWidgetItem([texto])
                hoja.setIcon(0, icono(clave, 16))
                hoja.setData(0, Qt.ItemDataRole.UserRole, ('calc', nombre, clave))
                fl.addChild(hoja)
            fl.setExpanded(True)
        nodo.setExpanded(True)
        self._ajustar_alto_datos()

    def _ajustar_alto_datos(self):
        """Ajusta la altura del arbol de Datos a las filas visibles."""
        def contar(item):
            n = 1
            if item.isExpanded():
                for i in range(item.childCount()):
                    n += contar(item.child(i))
            return n
        total = 0
        for i in range(self.tree_datos.topLevelItemCount()):
            total += contar(self.tree_datos.topLevelItem(i))
        self.tree_datos.setFixedHeight(24 + 22 * max(total, 1))

    def sincronizar(self, clave):
        it = self._leaf_por_clave.get(clave)
        self.tree_calc.blockSignals(True)
        if it is not None:
            self.tree_calc.setCurrentItem(it)
        else:
            self.tree_calc.clearSelection()
        self.tree_calc.blockSignals(False)

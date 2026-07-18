"""
ribbon.py — Cinta de opciones (ribbon) y panel Navegador lateral.

Provee el "chrome" de estilo office que envuelve las pestanas de contenido
fijo de ThermoPhase. Todo el cromo usa una fuente moderna (Segoe UI) para
contrastar con el contenido retro (Arial Narrow) de las pestanas.

Componentes:
    RibbonButton   — boton grande (icono arriba, texto abajo) o pequeno.
    RibbonGroup    — grupo titulado de botones con separador vertical.
    construir_ribbon(acciones) -> (QScrollArea, dict de botones)
    NavigatorPanel — panel lateral con arbol de Calculos, Datos,
                     Herramientas e Informacion de la base de datos.
"""
from PyQt6.QtWidgets import (
    QWidget, QToolButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QScrollArea, QSizePolicy, QTreeWidget, QTreeWidgetItem, QGridLayout,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont

from iconos import icono

# ── Paleta / tipografia del cromo office ─────────────────────
FUENTE_UI = "Segoe UI"
BANDA     = "#F3F4F6"   # fondo de la cinta
BORDE     = "#C6CBD3"
SEPAR     = "#D5D9E0"
HOVER     = "#DCE7F7"
PRESION   = "#C4D6F2"
TITULO    = "#6B7280"   # texto de titulo de grupo
TXT       = "#26303A"
HDR_BG    = "#E4E8EF"   # cabecera de seccion del navegador
HDR_TXT   = "#33404E"
SEL_BG    = "#CCE0FA"

# Estructura de la cinta: (titulo_grupo, [(clave, texto, icono, grande), ...])
_ESPEC_RIBBON = [
    ("Archivo", [
        ("nuevo",        "Nuevo",            "nuevo",          True),
        ("abrir",        "Abrir",            "abrir",          True),
        ("guardar",      "Guardar",          "guardar",        True),
        ("guardar_como", "Guardar\ncomo",    "guardar_como",   True),
        ("imprimir",     "Imprimir",         "imprimir",       True),
    ]),
    ("Edición", [
        ("deshacer",     "Deshacer",         "deshacer",       True),
        ("rehacer",      "Rehacer",          "rehacer",        True),
        ("cortar",       "Cortar",           "cortar",         True),
        ("copiar",       "Copiar",           "copiar",         True),
        ("pegar",        "Pegar",            "pegar",          True),
    ]),
    ("Cálculos", [
        ("fraccion",     "Fracción\nmásica", "fraccion_masica", True),
        ("normalizar",   "Normalizar",       "normalizar",     True),
        ("ejecutar",     "Realizar\ncálculo","ejecutar",       True),
        ("detener",      "Detener",          "detener",        True),
    ]),
    ("Unidades", [
        ("sistema",      "Sistema",          "sistema",        True),
        ("conversor",    "Conversor",        "conversor",      True),
    ]),
    ("Datos", [
        ("componentes",  "Componentes",      "componentes",    True),
        ("fluidos",      "Fluidos",          "fluidos",        True),
        ("mezclas",      "Mezclas",          "mezclas",        True),
    ]),
    ("Herramientas", [
        ("tablas",       "Tablas",           "tablas",         True),
        ("calculadora",  "Calculadora",      "calculadora",    True),
        ("graficas",     "Gráficas",         "graficas",       True),
    ]),
    ("Preferencias", [
        ("opciones",     "Opciones",         "opciones",       True),
        ("configuracion","Configuración",    "configuracion",  True),
    ]),
    ("Ayuda", [
        ("ayuda",        "Ayuda",            "ayuda",          True),
        ("acerca",       "Acerca de",        "acerca",         True),
    ]),
]

# Items del arbol "Cálculos" del navegador -> indice de pestana central
NAV_CALCULOS = [
    ("equilibrio",  "Equilibrio de fases",                0),
    ("envolvente",  "Envolvente de fases",                1),
    ("saturacion",  "Puntos de saturación",               2),
    ("propiedades", "Propiedades termodinámicas",         3),
    ("corriente",   "Propiedades de la corriente",        4),
    ("parametros",  "Parámetros de la ecuación de estado", 5),
]


def _btn_style(grande):
    """QSS office plano con resalte al pasar el mouse."""
    return (
        f'QToolButton {{ border:1px solid transparent; border-radius:3px;'
        f' background:transparent; color:{TXT};'
        f' font-family:"{FUENTE_UI}"; font-size:{8 if grande else 8}pt;'
        f' padding:{2 if grande else 1}px; }}'
        f'QToolButton:hover {{ background:{HOVER}; border:1px solid {BORDE}; }}'
        f'QToolButton:pressed {{ background:{PRESION}; }}'
        f'QToolButton:checked {{ background:{PRESION}; border:1px solid #8FB4E8; }}'
        f'QToolButton:disabled {{ color:#9AA1AB; }}'
    )


class RibbonButton(QToolButton):
    """Boton de cinta: grande (icono arriba / texto abajo) o pequeno."""
    def __init__(self, texto, nombre_icono, grande=True, parent=None):
        super().__init__(parent)
        self.setText(texto)
        self.setIcon(icono(nombre_icono, 32 if grande else 18))
        self.setStyleSheet(_btn_style(grande))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon if grande
            else Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        if grande:
            self.setIconSize(QSize(30, 30))
            self.setFixedSize(QSize(64, 66))
        else:
            self.setIconSize(QSize(18, 18))
            self.setFixedHeight(22)


class RibbonGroup(QFrame):
    """Grupo titulado de botones con separador vertical a la derecha."""
    def __init__(self, titulo, parent=None):
        super().__init__(parent)
        self._v = QVBoxLayout(self)
        self._v.setContentsMargins(4, 3, 0, 2)
        self._v.setSpacing(1)

        fila = QWidget()
        self._h = QHBoxLayout(fila)
        self._h.setContentsMargins(0, 0, 0, 0)
        self._h.setSpacing(1)
        self._h.setAlignment(Qt.AlignmentFlag.AlignLeft
                             | Qt.AlignmentFlag.AlignVCenter)
        self._v.addWidget(fila, 1)

        # Linea separadora + titulo del grupo
        lbl = QLabel(titulo)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f'color:{TITULO}; font-family:"{FUENTE_UI}"; font-size:7.5pt;'
            f' border-top:1px solid {SEPAR}; padding-top:1px;')
        self._v.addWidget(lbl)

    def add(self, boton):
        self._h.addWidget(boton, alignment=Qt.AlignmentFlag.AlignVCenter)


def construir_ribbon(acciones=None):
    """Construye la cinta completa.

    Parametros
    ----------
    acciones : dict {clave: callable}
        Mapa opcional de clave de boton -> funcion a ejecutar al hacer clic.

    Devuelve
    --------
    (scroll, botones)
        scroll  : QScrollArea que contiene la cinta (scroll horizontal si el
                  ancho de la ventana es menor que el de la cinta).
        botones : dict {clave: RibbonButton} para habilitar/deshabilitar o
                  marcar como checkable desde fuera.
    """
    acciones = acciones or {}
    barra = QWidget()
    barra.setStyleSheet(f'background:{BANDA};')
    lay = QHBoxLayout(barra)
    lay.setContentsMargins(6, 4, 6, 2)
    lay.setSpacing(0)
    lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

    botones = {}
    for i, (titulo, items) in enumerate(_ESPEC_RIBBON):
        grupo = RibbonGroup(titulo)
        for clave, texto, ic, grande in items:
            b = RibbonButton(texto, ic, grande)
            fn = acciones.get(clave)
            if fn is not None:
                b.clicked.connect(fn)
            botones[clave] = b
            grupo.add(b)
        lay.addWidget(grupo)
        # Separador vertical entre grupos
        if i < len(_ESPEC_RIBBON) - 1:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setStyleSheet(f'color:{SEPAR}; background:{SEPAR};')
            sep.setFixedWidth(1)
            lay.addWidget(sep)
    lay.addStretch()

    scroll = QScrollArea()
    scroll.setWidget(barra)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setFixedHeight(94)
    scroll.setStyleSheet(
        f'QScrollArea {{ background:{BANDA}; border-bottom:1px solid {BORDE}; }}')
    return scroll, botones


# ══════════════════════════════════════════════════════════════
# Panel Navegador lateral
# ══════════════════════════════════════════════════════════════
def _cabecera(texto):
    lbl = QLabel("  " + texto)
    lbl.setFixedHeight(22)
    lbl.setStyleSheet(
        f'background:{HDR_BG}; color:{HDR_TXT};'
        f' font-family:"{FUENTE_UI}"; font-size:9pt; font-weight:bold;'
        f' border:1px solid {BORDE};')
    return lbl


def _tree_base():
    t = QTreeWidget()
    t.setHeaderHidden(True)
    t.setIndentation(14)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setStyleSheet(
        f'QTreeWidget {{ background:#FFFFFF; border:1px solid {BORDE};'
        f' font-family:"{FUENTE_UI}"; font-size:9pt; color:{TXT};'
        f' outline:0; }}'
        f'QTreeWidget::item {{ height:22px; padding-left:2px; }}'
        f'QTreeWidget::item:selected {{ background:{SEL_BG}; color:{TXT}; }}'
        f'QTreeWidget::item:hover {{ background:{HOVER}; }}')
    return t


class NavigatorPanel(QWidget):
    """Panel lateral izquierdo de ancho fijo con arbol de Calculos,
    accesos a Datos / Herramientas e Informacion de la base de datos."""

    pestana_pedida = pyqtSignal(int)   # indice de pestana solicitado
    dato_pedido    = pyqtSignal(str)   # clave de accion (componentes, tablas...)

    ANCHO = 258

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(self.ANCHO)
        self.setStyleSheet(f'background:#FBFBFC;')
        self._leaf_por_indice = {}
        self._build()

    def _build(self):
        cont = QWidget()
        v = QVBoxLayout(cont)
        v.setContentsMargins(6, 6, 6, 6)
        v.setSpacing(6)

        # ── Navegador (Cálculos) ─────────────────────────────
        v.addWidget(_cabecera("Navegador"))
        self.tree_calc = _tree_base()
        raiz = QTreeWidgetItem(["Cálculos"])
        raiz.setIcon(0, icono("guardar", 16))
        raiz.setFlags(raiz.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        f = raiz.font(0); f.setBold(True); raiz.setFont(0, f)
        self.tree_calc.addTopLevelItem(raiz)
        for nombre_ic, texto, idx in NAV_CALCULOS:
            it = QTreeWidgetItem([texto])
            it.setIcon(0, icono(nombre_ic, 16))
            it.setData(0, Qt.ItemDataRole.UserRole, idx)
            raiz.addChild(it)
            self._leaf_por_indice[idx] = it
        raiz.setExpanded(True)
        self.tree_calc.itemClicked.connect(self._on_calc_click)
        self.tree_calc.setFixedHeight(24 + 22 * (len(NAV_CALCULOS) + 1))
        v.addWidget(self.tree_calc)

        # ── Datos ────────────────────────────────────────────
        v.addWidget(_cabecera("Datos"))
        self.tree_datos = _tree_base()
        self.tree_datos.setRootIsDecorated(False)
        for nombre_ic, texto, clave in [
            ("componentes", "Componentes", "componentes"),
            ("fluidos",     "Fluidos",     "fluidos"),
            ("mezclas",     "Mezclas",     "mezclas"),
        ]:
            it = QTreeWidgetItem([texto])
            it.setIcon(0, icono(nombre_ic, 16))
            it.setData(0, Qt.ItemDataRole.UserRole, clave)
            self.tree_datos.addTopLevelItem(it)
        self.tree_datos.itemClicked.connect(self._on_dato_click)
        self.tree_datos.setFixedHeight(24 + 22 * 3)
        v.addWidget(self.tree_datos)

        # ── Herramientas ─────────────────────────────────────
        v.addWidget(_cabecera("Herramientas"))
        self.tree_herr = _tree_base()
        self.tree_herr.setRootIsDecorated(False)
        for nombre_ic, texto, clave in [
            ("conversor",   "Conversor de unidades", "conversor"),
            ("tablas",      "Tablas",                "tablas"),
            ("calculadora", "Calculadora",           "calculadora"),
        ]:
            it = QTreeWidgetItem([texto])
            it.setIcon(0, icono(nombre_ic, 16))
            it.setData(0, Qt.ItemDataRole.UserRole, clave)
            self.tree_herr.addTopLevelItem(it)
        self.tree_herr.itemClicked.connect(self._on_dato_click)
        self.tree_herr.setFixedHeight(24 + 22 * 3)
        v.addWidget(self.tree_herr)

        # ── Informacion de la base de datos ──────────────────
        v.addWidget(_cabecera("Información de la base de datos"))
        info = QFrame()
        info.setStyleSheet(
            f'QFrame {{ background:#FFFFFF; border:1px solid {BORDE}; }}')
        g = QGridLayout(info)
        g.setContentsMargins(8, 6, 8, 6)
        g.setHorizontalSpacing(6)
        g.setVerticalSpacing(4)

        def _et(txt, bold=False):
            l = QLabel(txt)
            peso = "bold" if bold else "normal"
            l.setStyleSheet(
                f'background:transparent; color:{TXT};'
                f' font-family:"{FUENTE_UI}"; font-size:9pt;'
                f' font-weight:{peso};')
            return l

        self.lbl_archivo = _et("Sin título.tpsim")
        self.lbl_ruta    = _et("—")
        self.lbl_ruta.setWordWrap(True)
        self.lbl_estado  = _et("Listo")
        self.lbl_ncomp   = _et("0")
        filas = [("Archivo:", self.lbl_archivo), ("Ruta:", self.lbl_ruta),
                 ("Estado:", self.lbl_estado), ("Componentes:", self.lbl_ncomp)]
        for r, (k, w) in enumerate(filas):
            g.addWidget(_et(k, bold=True), r, 0,
                        alignment=Qt.AlignmentFlag.AlignTop
                                  | Qt.AlignmentFlag.AlignLeft)
            g.addWidget(w, r, 1)
        g.setColumnStretch(1, 1)
        v.addWidget(info)

        v.addStretch()

        # Scroll para que el panel funcione en ventanas de poca altura
        scroll = QScrollArea(self)
        scroll.setWidget(cont)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ── Slots ────────────────────────────────────────────────
    def _on_calc_click(self, item, col):
        idx = item.data(0, Qt.ItemDataRole.UserRole)
        if idx is not None:
            self.pestana_pedida.emit(int(idx))

    def _on_dato_click(self, item, col):
        clave = item.data(0, Qt.ItemDataRole.UserRole)
        if clave:
            self.dato_pedido.emit(str(clave))

    def sincronizar(self, indice):
        """Resalta el item del arbol que corresponde a la pestana activa."""
        it = self._leaf_por_indice.get(indice)
        if it is not None:
            self.tree_calc.blockSignals(True)
            self.tree_calc.setCurrentItem(it)
            self.tree_calc.blockSignals(False)

    def set_info(self, archivo="Sin título.tpsim", ruta="—",
                 estado="Listo", n_comp=0):
        self.lbl_archivo.setText(archivo)
        self.lbl_ruta.setText(ruta)
        self.lbl_estado.setText(estado)
        self.lbl_ncomp.setText(str(n_comp))

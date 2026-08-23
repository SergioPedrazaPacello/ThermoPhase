"""
Peng-Robinson EOS — Equilibrio de Fases
v12: Estructura multi-widget. Títulos como QLabel, datos como QTableWidget pequeños.
     Esto elimina el conflicto de QSS y permite colorear celda por celda.
"""
import sys, os, copy
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTabBar, QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QDoubleSpinBox, QGridLayout, QFrame, QHeaderView,
    QCheckBox, QMessageBox, QStatusBar, QAbstractItemView, QScrollArea, QComboBox,
    QAbstractSpinBox, QMenuBar, QFileDialog, QSplitter,
    QMdiArea, QMdiSubWindow, QListWidget, QInputDialog
)
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QEvent
from PyQt6.QtGui import QColor, QBrush, QFont, QIcon, QAction, QKeySequence

from eos import (
    COMPONENTES, NOMBRES, PM, TC, PC, OMEGA, KIJ_DEFAULT, NC,
    calcular, R_GAS, set_eos as _set_eos, get_eos as _get_eos
)
import eos as _eng
from pestana_envolvente import TabEnvolvente
from pestana_saturacion import TabSaturacion
from pestana_propiedades import TabPropiedades
import dialogos as dialogos
from rutas import ruta_recurso
from ribbon import construir_ribbon, NavigatorPanel
import iconos
import edicion
import idioma as _i18n
kij_user = copy.deepcopy(KIJ_DEFAULT)
kij_fuente = 'PR'         # EOS-fuente activa de los kij globales (PR/SRK/PR_PVT/SRK_PVT)

# Las 4 ecuaciones de estado, en el orden de los combos.
EOS_ITEMS = ["Peng-Robinson (HYSYS)", "SRK (HYSYS)",
             "Peng-Robinson (PVTsim)", "SRK (PVTsim)"]
EOS_CODES = ['PR', 'SRK', 'PR_PVT', 'SRK_PVT']

def _eos_code(idx):
    return EOS_CODES[idx] if 0 <= idx < len(EOS_CODES) else 'PR'

def _eos_idx(code):
    return EOS_CODES.index(code) if code in EOS_CODES else 0

def _eos_nombre(code):
    return {'PR': "Peng-Robinson (HYSYS)", 'SRK': "SRK (HYSYS)",
            'PR_PVT': "Peng-Robinson (PVTsim)",
            'SRK_PVT': "SRK (PVTsim)"}.get(code, "Peng-Robinson (HYSYS)")

# ── Paleta ────────────────────────────────────────────────────
WHITE    = "#FFFFFF"
GRAY_TIT = "#A8A8A8"   # plomo oscuro para títulos / cabeceras
GRAY_LBL = "#D0D0D0"   # plomo medio para etiquetas
GRAY_RES = "#E8E8E8"   # plomo claro para celdas de resultado (vacías)
BORDER   = "#888888"
TEXT     = "#000000"
TEXT_DIM = "#555555"
TEXT_RES = "#000080"   # azul oscuro para resultados
FONT_F   = "Arial Narrow"
FS       = 10

# ── Estilo retro de las listas desplegables (QComboBox) ───────
# Para cambiar de modelo: comenta el COMBO_STYLE activo y
# descomenta el que quieras. Los 4 modelos usan la misma paleta.
#
# Modelo 1 — Windows 95 clásico  (ACTIVO, recomendado)
COMBO_STYLE = (
    f'QComboBox {{ background:{WHITE}; border:2px inset {BORDER};'
    f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
    f'QComboBox:on {{ border:2px inset #555555; }}'
    f'QAbstractItemView {{ background:{WHITE}; border:1px solid #000000;'
    f' color:{TEXT}; selection-background-color:#DCDCDC; selection-color:#000000;'
    f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
    f'QAbstractItemView::item {{ min-height:18px; padding:1px 6px; }}'
)

def _aplicar_estilo_combo(combo):
    """Aplica el estilo retro (Modelo 1) al combo y a su lista emergente.
    Usa Fusion por-widget para que el QSS se respete en Windows, fuerza que
    la lista se despliegue hacia ABAJO (no centrada en la opción actual) y
    conserva la flecha ▼ (la dibuja Fusion, por eso no se estiliza ::drop-down)."""
    from PyQt6.QtWidgets import QListView, QStyleFactory, QProxyStyle, QStyle
    class _DesplegarAbajo(QProxyStyle):
        def styleHint(self, hint, option=None, widget=None, returnData=None):
            if hint == QStyle.StyleHint.SH_ComboBox_Popup:
                return 0
            return super().styleHint(hint, option, widget, returnData)
    combo._proxy = _DesplegarAbajo(QStyleFactory.create("Fusion"))
    combo.setStyle(combo._proxy)
    combo.setView(QListView())
    combo._vstyle = QStyleFactory.create("Fusion")
    combo.view().setStyle(combo._vstyle)
    combo.view().setUniformItemSizes(True)   # todas las filas con la misma altura
    # Forzar resaltado gris (la vista usa la paleta para el highlight).
    from PyQt6.QtGui import QPalette, QColor
    _pal = combo.view().palette()
    _pal.setColor(QPalette.ColorRole.Highlight, QColor("#DCDCDC"))
    _pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    combo.view().setPalette(_pal)
    combo.setStyleSheet(COMBO_STYLE)
    combo.view().setStyleSheet(COMBO_STYLE)
# Modelo 2 — Plomo IBM / monocromo
# COMBO_STYLE = (
#     f'QComboBox {{ background:{GRAY_RES}; border:1px solid {TEXT_DIM};'
#     f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
#     f'QComboBox::drop-down {{ subcontrol-origin:padding; subcontrol-position:top right;'
#     f' width:18px; background:{GRAY_LBL}; border-left:1px solid {TEXT_DIM}; }}'
#     f'QAbstractItemView {{ background:{GRAY_RES}; border:1px solid {TEXT_DIM};'
#     f' color:{TEXT}; selection-background-color:#555555; selection-color:#FFFFFF;'
#     f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
#     f'QAbstractItemView::item {{ min-height:18px; padding:1px 4px; }}'
# )
# Modelo 3 — Acento naranja (logo)
# COMBO_STYLE = (
#     f'QComboBox {{ background:{WHITE}; border:2px inset {BORDER};'
#     f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
#     f'QComboBox::drop-down {{ subcontrol-origin:padding; subcontrol-position:top right;'
#     f' width:18px; background:#C8C8C8; border-left:2px solid #C0392B; }}'
#     f'QAbstractItemView {{ background:{WHITE}; border:1px solid #C0392B;'
#     f' color:{TEXT}; selection-background-color:#C0392B; selection-color:#FFFFFF;'
#     f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
#     f'QAbstractItemView::item {{ min-height:18px; padding:1px 4px; }}'
# )
# Modelo 4 — Terminal ámbar CRT
# COMBO_STYLE = (
#     f'QComboBox {{ background:#1A1A1A; border:2px inset #555555;'
#     f' color:#FFB000; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
#     f'QComboBox::drop-down {{ subcontrol-origin:padding; subcontrol-position:top right;'
#     f' width:18px; background:#2A2A2A; border-left:1px solid #FFB000; }}'
#     f'QAbstractItemView {{ background:#1A1A1A; border:1px solid #FFB000;'
#     f' color:#FFB000; selection-background-color:#3A2A00; selection-color:#FFD700;'
#     f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
#     f'QAbstractItemView::item {{ min-height:18px; padding:1px 4px; }}'
# )

# ── Helpers de color ─────────────────────────────────────────
def _brush(hex_color):
    return QBrush(QColor(hex_color), Qt.BrushStyle.SolidPattern)

def cell(text, bg=WHITE, color=TEXT,
         align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter,
         editable=False):
    """Crea un QTableWidgetItem con color de fondo explícito."""
    it = QTableWidgetItem(str(text))
    it.setTextAlignment(align)
    it.setBackground(_brush(bg))
    it.setForeground(_brush(color))
    if not editable:
        it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return it

def title_label(text):
    """Barra de título oscura."""
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    lbl.setFixedHeight(22)
    lbl.setStyleSheet(
        f'background:{GRAY_TIT}; color:{TEXT}; '
        f'font-family:"{FONT_F}"; font-size:{FS}pt; '
        f'padding:0px 6px; border:1px solid {BORDER};'
    )
    return lbl

def section_label(text, left=False):
    """Barra de sección (plomo medio)."""
    lbl = QLabel(text)
    align = (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
             if left else Qt.AlignmentFlag.AlignCenter)
    lbl.setAlignment(align)
    lbl.setFixedHeight(22)
    lbl.setStyleSheet(
        f'background:{GRAY_LBL}; color:{TEXT}; '
        f'font-family:"{FONT_F}"; font-size:{FS}pt; '
        f'padding:0px 8px; border:1px solid {BORDER};'
    )
    return lbl

def make_table(rows, cols, row_h=22):
    """Tabla sin cabeceras, sin scroll, tamaño fijo."""
    t = QTableWidget(rows, cols)
    t.horizontalHeader().hide()
    t.verticalHeader().hide()
    t.setShowGrid(True)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setStyleSheet(
        f'QTableWidget {{ border:1px solid {BORDER}; '
        f'font-family:"{FONT_F}"; font-size:{FS}pt; gridline-color:{BORDER}; }}'
        f'QTableWidget::item {{ padding:2px 6px; }}'
    )
    for r in range(rows):
        t.setRowHeight(r, row_h)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return t

def fix_table_size(t):
    """Ajusta el tamaño de la tabla a su contenido, ignorando filas y
    columnas ocultas (para soportar componentes deshabilitados)."""
    w = sum(t.columnWidth(c) for c in range(t.columnCount())
            if not t.isColumnHidden(c)) + 2
    h = sum(t.rowHeight(r) for r in range(t.rowCount())
            if not t.isRowHidden(r)) + 2
    t.setFixedSize(w, h)

# ── Dimensiones ──────────────────────────────────────────────
W_LBL  = 255   # columna de etiqueta
W_VAL  = 140   # columna de valor (Vapor o Líquido)
W_COMP = 290   # columna nombre de componente
ROW_H  = 22

# Propiedades del resumen de resultados (selector). Orden canonico:
# (key, etiqueta_base, unidad_mag_o_None, decimales, tiene_valor_de_mezcla)
PROP_RESUMEN = [
    ('frac_molar',  'Fase fraccion [molar]',      None,   4, False),
    ('frac_masica', 'Fase fraccion [masica]',     None,   4, False),
    ('sg',          'Gravedad especifica',         None,   4, False),
    ('densidad',    'Densidad masica',             'dens', 4, True),
    ('z',           'Factor de compresibilidad',   None,   4, False),
    ('pm',          'Peso molecular',              None,   4, True),
    ('entalpia',    'Entalpia molar',              'H',    2, True),
    ('entropia',    'Entropia molar',              'S',    4, True),
    ('viscosidad',  'Viscosidad',                  'visc', 5, False),
]
PROP_DEFAULT = ['frac_molar', 'frac_masica', 'sg', 'densidad', 'z', 'pm']
_PROP_DEF = {d[0]: d for d in PROP_RESUMEN}

# ── Worker ────────────────────────────────────────────────────
class Worker(QThread):
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)
    def __init__(self, z, T, P, kij, metodo_densidad='EOS'):
        super().__init__()
        self.z=z; self.T=T; self.P=P; self.kij=kij
        self.metodo_densidad=metodo_densidad
    def run(self):
        try:    self.done.emit(calcular(self.z, self.T, self.P, self.kij,
                                        metodo_densidad=self.metodo_densidad))
        except Exception as e: self.error.emit(str(e))

# ══════════════════════════════════════════════════════════════
# Tab 1 — Equilibrio de Fases
# ══════════════════════════════════════════════════════════════
class TabEquilibrio(QWidget):
    # Señal emitida cuando el usuario cambia la EOS en el selector.
    # El valor emitido es 'PR' o 'SRK'. La ventana principal se
    # encarga de propagar el cambio al motor y al resto de pestañas.
    eos_changed = pyqtSignal(str)

    def __init__(self, kij_get=None):
        super().__init__()
        self.worker      = None
        self.last_result = None
        self._kij_get    = kij_get   # None -> kij global; callable -> kij propio
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.setSpacing(0)

        # Centrar todo al ancho de la tabla
        hc = QHBoxLayout()
        hc.setContentsMargins(0,0,0,0)
        hc.addStretch()

        # Ancho total = W_COMP + 3*W_VAL
        TW = W_COMP + 3*W_VAL   # 290 + 420 = 710

        box = QWidget()
        box.setFixedWidth(TW)
        root = QVBoxLayout(box)
        root.setContentsMargins(0, 8, 0, 8)
        root.setSpacing(4)

        # ── ENCABEZADO (parte alta de la ventana) ─────────────
        root.addWidget(title_label("ThermoPhase — Equilibrio de Fases"))

        # ── Fila entradas P/T + checkbox + botón ─────────────
        top = QHBoxLayout()
        top.setSpacing(10)

        pin = QFrame()
        pin.setStyleSheet(f'border:1px solid {BORDER};')
        gl = QGridLayout(pin)
        gl.setContentsMargins(6,4,6,4); gl.setSpacing(4)

        def inp_lbl(txt):
            l = QLabel(txt)
            l.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            l.setStyleSheet(
                f'background:{GRAY_LBL};border:1px solid {BORDER};'
                f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
            l.setFixedHeight(22)
            return l

        self.lbl_P_in = inp_lbl("Presion (psi):")
        gl.addWidget(self.lbl_P_in, 0, 0)
        self.sp_P = QDoubleSpinBox()
        self.sp_P.setRange(0,15000); self.sp_P.setDecimals(2)
        self.sp_P.setSpecialValueText(" "); self.sp_P.setValue(0)
        self.sp_P.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_P.setFixedHeight(22); self.sp_P.setFixedWidth(110)
        self.sp_P.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gl.addWidget(self.sp_P, 0, 1)

        self.lbl_Tabs_in = inp_lbl("Temperatura (°R):")
        gl.addWidget(self.lbl_Tabs_in, 1, 0)
        self.sp_T = QDoubleSpinBox()
        self.sp_T.setRange(0.0, 9999.99)
        self.sp_T.setDecimals(2)
        self.sp_T.setSpecialValueText(" "); self.sp_T.setValue(0)
        self.sp_T.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_T.setFixedHeight(22); self.sp_T.setFixedWidth(110)
        gl.addWidget(self.sp_T, 1, 1)

        self.lbl_Trel_in = inp_lbl("Temperatura (°F):")
        gl.addWidget(self.lbl_Trel_in, 2, 0)
        self.sp_F = QDoubleSpinBox()
        self.sp_F.setRange(-459.67, 9540.32)
        self.sp_F.setDecimals(2)
        self.sp_F.setSpecialValueText(" "); self.sp_F.setValue(-459.67)
        self.sp_F.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_F.setFixedHeight(22); self.sp_F.setFixedWidth(110)
        gl.addWidget(self.sp_F, 2, 1)

        # Sincronización bidireccional °R ↔ °F
        # El campo activo (donde se escribe) queda blanco; el otro queda gris
        self._sync_lock = False
        ACTIVO = WHITE
        INACTIVO = "#B8B8B8"   # plomo más oscuro
        def _style_T(activo):
            self.sp_T.setStyleSheet(
                f'QDoubleSpinBox {{ background:{ACTIVO if activo else INACTIVO};'
                f'border:1px solid {BORDER};'
                f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        def _style_F(activo):
            self.sp_F.setStyleSheet(
                f'QDoubleSpinBox {{ background:{ACTIVO if activo else INACTIVO};'
                f'border:1px solid {BORDER};'
                f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        self._style_T = _style_T; self._style_F = _style_F
        _style_T(True); _style_F(False)

        def _off():
            import unidades as _u
            return _u.offset_abs_rel()
        def _on_T_changed(v):
            if self._sync_lock: return
            self._sync_lock = True
            off = _off()
            if v <= 0:
                self.sp_F.setValue(-off)      # vacío
            else:
                self.sp_F.setValue(v - off)
            _style_T(True); _style_F(False)
            self._sync_lock = False
        def _on_F_changed(v):
            if self._sync_lock: return
            self._sync_lock = True
            off = _off()
            if v <= -off:
                self.sp_T.setValue(0)         # vacío
            else:
                self.sp_T.setValue(v + off)
            _style_F(True); _style_T(False)
            self._sync_lock = False
        self.sp_T.valueChanged.connect(_on_T_changed)
        self.sp_F.valueChanged.connect(_on_F_changed)


        top.addWidget(pin,
            alignment=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        top.addStretch()

        # Panel derecho: QVBoxLayout con stretch arriba/abajo para centrar botones,
        # selector densidad al fondo alineado a la derecha
        rp = QVBoxLayout(); rp.setSpacing(0); rp.setContentsMargins(0,0,0,0)

        rp.addStretch(2)   # empuja bloque botones+selector hacia el centro

        # Fila de botones (alineados a la derecha)
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        btn_row.addStretch()

        # Botón toggle que alterna entre Fraccion molar / masica
        self.btn_frac = QPushButton("Fraccion masica")
        self.btn_frac.setCheckable(True)
        self.btn_frac.setFixedWidth(120)
        self.btn_frac.setStyleSheet(
            f'background:{GRAY_LBL};border:2px outset {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
        self.btn_frac.clicked.connect(self._on_chk)
        btn_row.addWidget(self.btn_frac, alignment=Qt.AlignmentFlag.AlignVCenter)

        btn_n = QPushButton("Normalizar")
        btn_n.setFixedWidth(100)
        btn_n.setStyleSheet(
            f'background:{GRAY_LBL};border:2px outset {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
        btn_n.clicked.connect(self.normalizar)
        btn_row.addWidget(btn_n, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.btn = QPushButton("Realizar Calculo")
        self.btn.setFixedWidth(130)
        self.btn.setStyleSheet(
            f'background:{GRAY_LBL};border:2px outset {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
        self.btn.clicked.connect(self.calcular)
        btn_row.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        rp.addLayout(btn_row)

        rp.addSpacing(6)   # pequeño espacio entre botones y selector

        # Fila selector densidad + corrección de volumen (misma fila para no
        # aumentar la altura del panel).  Etiqueta + combo, alineados a la
        # derecha, con el mismo estilo que las demás filas.
        dens_row = QHBoxLayout(); dens_row.setSpacing(4)
        dens_row.addStretch()
        lbl_dens = QLabel("Densidad:")
        lbl_dens.setFixedHeight(22); lbl_dens.setFixedWidth(72)
        lbl_dens.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        lbl_dens.setStyleSheet(
            f'background:{GRAY_LBL};border:1px solid {BORDER};'
            f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
        dens_row.addWidget(lbl_dens, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.cmb_dens = QComboBox()
        self.cmb_dens.addItems(["COSTALD", "EOS"])
        self.cmb_dens.setFixedHeight(22); self.cmb_dens.setFixedWidth(110)
        _aplicar_estilo_combo(self.cmb_dens)
        dens_row.addWidget(self.cmb_dens, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Corrección de volumen a la derecha de densidad, en la misma fila.
        dens_row.addSpacing(10)
        lbl_vol = QLabel("Corrección de volumen:")
        lbl_vol.setFixedHeight(22)
        lbl_vol.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        lbl_vol.setStyleSheet(
            f'background:{GRAY_LBL};border:1px solid {BORDER};'
            f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
        dens_row.addWidget(lbl_vol, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.cmb_vol = QComboBox()
        self.cmb_vol.addItems(["Ninguna", "Peneloux"])
        self.cmb_vol.setFixedHeight(22); self.cmb_vol.setFixedWidth(110)
        _aplicar_estilo_combo(self.cmb_vol)
        dens_row.addWidget(self.cmb_vol, alignment=Qt.AlignmentFlag.AlignVCenter)
        rp.addLayout(dens_row)
        # Switch local: Peneloux fuerza densidad a EOS y la bloquea.
        self.cmb_vol.currentIndexChanged.connect(self._on_vol_local)

        rp.addSpacing(4)

        # Fila selector Ecuación de estado (misma estetica que Densidad).
        eos_row = QHBoxLayout(); eos_row.setSpacing(4)
        eos_row.addStretch()
        lbl_eos = QLabel("Ecuacion:")
        lbl_eos.setFixedHeight(22); lbl_eos.setFixedWidth(72)
        lbl_eos.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        lbl_eos.setStyleSheet(
            f'background:{GRAY_LBL};border:1px solid {BORDER};'
            f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
        eos_row.addWidget(lbl_eos, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.cmb_eos = QComboBox()
        self.cmb_eos.addItems(EOS_ITEMS)
        self.cmb_eos.setFixedHeight(22); self.cmb_eos.setFixedWidth(190)
        _aplicar_estilo_combo(self.cmb_eos)
        # Emitir señal cuando el usuario cambia la EOS
        self.cmb_eos.currentIndexChanged.connect(self._on_eos_changed)
        eos_row.addWidget(self.cmb_eos, alignment=Qt.AlignmentFlag.AlignVCenter)
        rp.addLayout(eos_row)

        rp.addStretch(2)   # equilibra el bloque hacia el centro

        top.addLayout(rp)
        root.addLayout(top)

        # ── BLOQUE RESUMEN ────────────────────────────────────
        # Título de sección + botón para elegir qué propiedades mostrar
        res_hdr_row = QHBoxLayout()
        res_hdr_row.setContentsMargins(0, 0, 0, 0); res_hdr_row.setSpacing(6)
        res_hdr_row.addWidget(section_label("Resumen de los calculos:", left=True), 1)
        self.btn_props = QPushButton("Propiedades")
        self.btn_props.setFixedHeight(22); self.btn_props.setFixedWidth(120)
        self.btn_props.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_props.setStyleSheet(
            f'QPushButton {{ background:{GRAY_LBL}; border:1px solid {BORDER};'
            f' font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 8px; }}'
            f'QPushButton:hover {{ background:#DCDCDC; }}')
        self.btn_props.clicked.connect(self._abrir_selector_props)
        res_hdr_row.addWidget(self.btn_props, 0)
        root.addLayout(res_hdr_row)

        # Cabecera de columnas del resumen (plomo medio)
        # Anchos del resumen = mismos que composicion para alinear columnas
        WR0 = W_COMP        # 290 — etiqueta
        WR1 = 100           # Mezcla
        WR2 = W_VAL         # Vapor  (140)
        WR3 = W_VAL         # Liquida(140)
        # Total = 290+100+140+140 = 670 — coincide con W_COMP+3*W_VAL si W_VAL=126.6
        # Ajustamos W_VAL para que todo sume igual:
        # W_COMP + 3*W_VAL = WR0+WR1+WR2+WR3 → 290+3*W_VAL = 290+100+2*W_VAL → W_VAL=100
        # Mejor: fijamos total = W_COMP+W_VAL*3 y distribuimos:
        # WR0=W_COMP, WR1+WR2+WR3 = W_VAL*3 → WR1=W_VAL-40, WR2=WR3=(W_VAL*3-(W_VAL-40))/2
        WR1 = W_VAL   # misma anchura que Vapor y Liquida
        WR2 = W_VAL
        WR3 = W_VAL
        hdr_res = make_table(1, 4)
        hdr_res.setColumnWidth(0, W_COMP)
        hdr_res.setColumnWidth(1, WR1)
        hdr_res.setColumnWidth(2, WR2)
        hdr_res.setColumnWidth(3, WR3)
        hdr_res.setItem(0,0, cell("", bg=GRAY_LBL))
        hdr_res.setItem(0,1, cell("Mezcla", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))
        hdr_res.setItem(0,2, cell("Fase Vapor", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))
        hdr_res.setItem(0,3, cell("Fase Liquida", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))
        fix_table_size(hdr_res)
        root.addWidget(hdr_res)

        # Tabla de datos del resumen
        # Filas: ff_mol, ff_mas, grav, dens, Z, PM
        # Tabla resumen: 4 columnas
        # col0=etiqueta, col1=mezcla(solo dens y PM), col2=Fase Vapor, col3=Fase Liquida
        # Para filas sin mezcla: col1 queda plomo/vacía, col2 y col3 tienen los valores
        self.tbl_res = make_table(6, 4)
        self.tbl_res.setColumnWidth(0, W_COMP)
        self.tbl_res.setColumnWidth(1, W_VAL)
        self.tbl_res.setColumnWidth(2, W_VAL)
        self.tbl_res.setColumnWidth(3, W_VAL)

        # Propiedades seleccionadas (por defecto, las 6 clásicas)
        self._props_sel = list(PROP_DEFAULT)
        self._rebuild_resumen()      # arma filas/etiquetas iniciales
        root.addWidget(self.tbl_res)

        # ── BLOQUE COMPOSICIÓN ────────────────────────────────
        root.addWidget(section_label("Composicion de las fases:", left=True))

        # Cabecera de composición (2 niveles)
        hdr_comp = make_table(2, 4)
        hdr_comp.setRowHeight(0, ROW_H)
        hdr_comp.setRowHeight(1, ROW_H)
        hdr_comp.setColumnWidth(0, W_COMP)
        for c in [1,2,3]: hdr_comp.setColumnWidth(c, W_VAL)

        hdr_comp.setItem(0,0, cell("Componente", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))
        hdr_comp.setItem(0,1, cell("Composicion General", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))
        hdr_comp.setItem(0,2, cell("Fase Vapor", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))
        hdr_comp.setItem(0,3, cell("Fase Liquida", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))

        hdr_comp.setItem(1,0, cell("", bg=GRAY_LBL))
        self.hdr_comp_gen  = cell("Fraccion Molar", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter)
        self.hdr_comp_vap  = cell("Fraccion molar", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter)
        self.hdr_comp_liq  = cell("Fraccion molar", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter)
        hdr_comp.setItem(1,1, self.hdr_comp_gen)
        hdr_comp.setItem(1,2, self.hdr_comp_vap)
        hdr_comp.setItem(1,3, self.hdr_comp_liq)
        fix_table_size(hdr_comp)
        root.addWidget(hdr_comp)

        # Tabla de componentes
        self.tbl_comp = make_table(NC+1, 4)
        self.tbl_comp.setColumnWidth(0, W_COMP)
        for c in [1,2,3]: self.tbl_comp.setColumnWidth(c, W_VAL)

        for i in range(NC):
            self.tbl_comp.setItem(i, 0, cell(
                NOMBRES[i], bg=GRAY_LBL,
                align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
            self.tbl_comp.setItem(i, 1, cell("", bg=WHITE, editable=True))
            self.tbl_comp.setItem(i, 2, cell("", bg=GRAY_RES, color=TEXT_RES))
            self.tbl_comp.setItem(i, 3, cell("", bg=GRAY_RES, color=TEXT_RES))

        # Fila de sumatorias dentro de tbl_comp (fila NC)
        self.tbl_comp.setItem(NC, 0, cell("Sumatorias:", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
        self.tbl_comp.setItem(NC, 1, cell("", bg=WHITE))
        self.tbl_comp.setItem(NC, 2, cell("", bg=GRAY_RES))
        self.tbl_comp.setItem(NC, 3, cell("", bg=GRAY_RES))
        self.sum_row = NC  # índice de la fila sumatoria dentro de tbl_comp
        fix_table_size(self.tbl_comp)
        self.tbl_comp.itemChanged.connect(self._on_item_changed)
        root.addWidget(self.tbl_comp)



        hc.addWidget(box)
        hc.addStretch()
        outer.addLayout(hc)

    # ── Helpers de entrada ───────────────────────────────────
    def get_T(self):
        """Temperatura en °R (interno del motor), convertida desde el campo
        absoluto (°R en Field, K en SI/Metric)."""
        import unidades as _u
        return _u.R_desde_abs(self.sp_T.value())

    def get_P(self):
        """Presión en psia (interno), convertida desde la unidad mostrada."""
        import unidades as _u
        try:
            val = float(self.sp_P.text().replace(',', '.'))
        except ValueError:
            val = 200.0
        if val <= 0:
            val = _u.p_desde_psia(200.0)
        return _u.p_a_psia(val)

    def aplicar_unidades(self, old):
        """Reconfigura entradas, etiquetas y resultados al sistema activo.
        `old` es el sistema anterior (para convertir los valores actuales)."""
        import unidades as _u
        # 1) Valores internos actuales (con el sistema anterior)
        try:
            P_int = _u.p_a_psia(float(self.sp_P.text().replace(',', '.')), old)
        except Exception:
            P_int = None
        Tabs_old = self.sp_T.value()
        T_int_R = _u.R_desde_abs(Tabs_old, old) if Tabs_old > 0 else None
        # 2) Etiquetas de entrada con la unidad nueva
        self.lbl_P_in.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
        self.lbl_Tabs_in.setText(f"{_i18n.t('Temperatura')} ({_u.u_abs()}):")
        self.lbl_Trel_in.setText(f"{_i18n.t('Temperatura')} ({_u.u('T')}):")
        # 3) Valores convertidos al sistema nuevo (sin disparar recursión)
        self._sync_lock = True
        if P_int is not None and P_int > 0:
            self.sp_P.setValue(_u.p_desde_psia(P_int))
        if T_int_R is not None:
            self.sp_T.setValue(_u.abs_desde_R(T_int_R))
            self.sp_F.setValue(_u.t_desde_R(T_int_R))
        self._sync_lock = False
        # 4) Reconstruir el resumen con las unidades nuevas (etiquetas + valores)
        if getattr(self, 'last_result', None) is not None:
            self._render(self.last_result)
        else:
            self._rebuild_resumen()

    # ── Handlers ─────────────────────────────────────────────
    def _on_eos_changed(self, idx):
        """Emite la señal para que MainWindow propague el cambio de EOS."""
        self.eos_changed.emit(_eos_code(idx))

    # ── Guardar / restaurar estado (usado por Archivo > Guardar/Abrir) ──
    def get_estado(self):
        """Devuelve dict con inputs y resultado calculado (si existe).
        T_R y P_psi se guardan SIEMPRE en unidades internas (°R, psia),
        independientemente del sistema de unidades mostrado."""
        Tabs = self.sp_T.value()
        import unidades as _u
        return {
            'entrada': {
                'composicion': self.get_z(),
                'T_R':         float(_u.R_desde_abs(Tabs)) if Tabs > 0 else 0.0,
                'P_psi':       float(self.get_P()),
                'densidad':    self.cmb_dens.currentText(),
                'correccion_volumen': self.cmb_vol.currentText(),
                'eos':         _eos_code(self.cmb_eos.currentIndex()),
                'modo_masico': self.btn_frac.isChecked(),
            },
            'resultado': self.last_result,   # dict o None
        }

    def set_estado(self, datos):
        """Restaura inputs y resultado. La EOS se maneja aparte por
        MainWindow (via señal eos_changed) para propagar a todas las tabs."""
        e = datos.get('entrada', {}) or {}
        # Composicion
        z = e.get('composicion') or [0.0]*NC
        self.tbl_comp.blockSignals(True)
        for i in range(NC):
            self.tbl_comp.item(i, 1).setText(f"{z[i] if i<len(z) else 0.0:.4f}")
        self.tbl_comp.blockSignals(False)
        self._upd_suma()
        # T y P se guardan en internas (°R, psia); convertir al sistema activo.
        import unidades as _u
        T = float(e.get('T_R', 0.0) or 0.0)          # °R interno
        self.sp_T.setValue(_u.abs_desde_R(T) if T > 0 else 0)
        P = float(e.get('P_psi', 0.0) or 0.0)        # psia interno
        self.sp_P.setValue(_u.p_desde_psia(P) if P > 0 else 0)
        # Densidad
        d = e.get('densidad', 'COSTALD')
        idx = self.cmb_dens.findText(d)
        if idx >= 0:
            self.cmb_dens.setCurrentIndex(idx)
        # Corrección de volumen (restaurar y aplicar switch)
        cv = e.get('correccion_volumen', 'Ninguna')
        iv = self.cmb_vol.findText(cv)
        if iv >= 0:
            self.cmb_vol.setCurrentIndex(iv)
        # EOS (silencioso — MainWindow ya la habra aplicado antes)
        eos_code = e.get('eos', 'PR')
        self.cmb_eos.blockSignals(True)
        self.cmb_eos.setCurrentIndex(_eos_idx(eos_code))
        self.cmb_eos.blockSignals(False)
        # Modo masico / molar
        masico = bool(e.get('modo_masico', False))
        self.btn_frac.setChecked(masico)
        self._on_chk()  # ajusta cabeceras
        # Resultado
        r = datos.get('resultado')
        if r:
            self.last_result = r
            self._render(r)

    def _on_chk(self):
        masa = self.btn_frac.isChecked()
        # El botón muestra el modo OPUESTO (la acción que realizará al hacer clic)
        self.btn_frac.setText("Fraccion molar" if masa else "Fraccion masica")
        # Col 1 (Composicion General) SIEMPRE "Fraccion Molar"
        self.hdr_comp_vap.setText(
            "Fraccion masica" if masa else "Fraccion molar")
        self.hdr_comp_liq.setText(
            "Fraccion masica" if masa else "Fraccion molar")
        if self.last_result:
            self._render(self.last_result)

    def _on_item_changed(self, item):
        if item.column() != 1: return
        if item.row() == self.sum_row: return  # no procesar fila sumatorias
        self._upd_suma()

    def aplicar_componentes_activos(self, activos):
        """Muestra solo las filas de los componentes activos y ajusta el
        tamaño de la tabla.  Los inactivos se ocultan y su fracción se pone
        a 0 para que el motor los ignore."""
        activos_set = set(activos)
        self.tbl_comp.blockSignals(True)
        for i in range(NC):
            oculto = i not in activos_set
            self.tbl_comp.setRowHidden(i, oculto)
            if oculto:
                self.tbl_comp.item(i, 1).setText("0.0000")
        self.tbl_comp.blockSignals(False)
        fix_table_size(self.tbl_comp)
        self._upd_suma()

    def get_z(self):
        z = []
        for i in range(NC):
            try: z.append(float(self.tbl_comp.item(i,1).text()))
            except: z.append(0.0)
        return z

    def set_z(self, z):
        """Carga una composicion (lista de NC fracciones) en la tabla."""
        self.tbl_comp.blockSignals(True)
        for i in range(NC):
            self.tbl_comp.item(i, 1).setText(f"{z[i] if i < len(z) else 0.0:.4f}")
        self.tbl_comp.blockSignals(False)
        self._upd_suma()

    def _upd_suma(self):
        s = sum(self.get_z())
        self.tbl_comp.blockSignals(True)
        self.tbl_comp.item(self.sum_row,1).setText(f"{s:.4f}")
        self.tbl_comp.blockSignals(False)

    def normalizar(self):
        z = self.get_z(); s = sum(z)
        if s <= 0: return
        self.tbl_comp.blockSignals(True)
        for i in range(NC):
            self.tbl_comp.item(i,1).setText(f"{z[i]/s:.4f}")
        self.tbl_comp.blockSignals(False)
        self._upd_suma()  # actualiza fila sumatorias

    def _on_vol_local(self, idx):
        """Switch local de corrección de volumen de esta ventana de
        equilibrio.  Peneloux corrige la densidad de la EOS, por lo que es
        incompatible con COSTALD: al activarlo se fuerza la densidad a EOS y
        se bloquea el selector; al volver a Ninguna se rehabilita."""
        es_peneloux = (self.cmb_vol.currentText() == 'Peneloux')
        if es_peneloux:
            self._densidad_previa_local = self.cmb_dens.currentText()
            iEOS = self.cmb_dens.findText('EOS')
            if iEOS >= 0:
                self.cmb_dens.setCurrentIndex(iEOS)
            self.cmb_dens.setEnabled(False)
        else:
            self.cmb_dens.setEnabled(True)
            prev = getattr(self, '_densidad_previa_local', 'COSTALD')
            iPrev = self.cmb_dens.findText(prev)
            if iPrev >= 0:
                self.cmb_dens.setCurrentIndex(iPrev)

    def calcular(self):
        z = self.get_z()
        if self.get_P() <= 0 or self.get_T() <= 0:
            dialogos.advertencia(self,
                "Ingrese la presion y la temperatura.")
            return
        if abs(sum(z)-1.0) > 1e-3:
            dialogos.advertencia(self,
                "La suma de fracciones debe ser 1.0")
            return
        self.btn.setEnabled(False); self.btn.setText(_i18n.t("Calculando..."))
        # Cada ventana de Equilibrio usa la EOS de su propio combo.
        eos_code = _eos_code(self.cmb_eos.currentIndex())
        _set_eos(eos_code)
        kij = self._kij_get() if self._kij_get is not None else kij_user
        # Contexto para calcular entalpia/entropia al recibir el resultado.
        self._hs_ctx = (list(z), self.get_T(), self.get_P(), kij, eos_code)
        # Método de densidad efectivo.  Cada ventana de equilibrio tiene su
        # propio selector de corrección de volumen: si está en Peneloux,
        # prevalece sobre el selector de densidad (bloqueado en EOS); si no,
        # se usa el método de densidad elegido (COSTALD o EOS).
        if self.cmb_vol.currentText() == 'Peneloux':
            metodo_dens = 'Peneloux'
        else:
            metodo_dens = self.cmb_dens.currentText()
        self._metodo_densidad_actual = metodo_dens
        self.worker = Worker(z, self.get_T(), self.get_P(), kij,
                             metodo_densidad=metodo_dens)
        self.worker.done.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_error(self, msg):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Realizar Calculo"))
        dialogos.error(self, msg)

    def _on_result(self, r):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Realizar Calculo"))
        # Entalpia y entropia (para el selector de propiedades)
        try:
            import entalpia_entropia_gen as _hs
            z, T_R, P, kij, eos = self._hs_ctx
            o = _hs.calcular_HS(z, T_R, P, r, eos=eos, kij=kij)
            for k in ('H_stream', 'S_stream', 'H_vapor', 'S_vapor',
                      'H_liquido', 'S_liquido'):
                r[k] = o.get(k)
        except Exception:
            pass
        self.last_result = r
        self._render(r)

    def _paint_res(self, row, col, txt):
        it = self.tbl_res.item(row, col)
        if it is None:
            it = cell("", bg=GRAY_RES); self.tbl_res.setItem(row, col, it)
        it.setText(txt)
        if txt:
            it.setBackground(_brush(WHITE)); it.setForeground(_brush(TEXT_RES))
        else:
            it.setBackground(_brush(GRAY_RES)); it.setForeground(_brush(TEXT))

    def _rebuild_resumen(self, valores=None):
        """(Re)construye la tabla de resumen mostrando solo las propiedades
        seleccionadas, en el orden canonico. `valores` es un dict
        key -> (mezcla, vapor, liquido) con textos ya formateados; si es None
        solo arma las etiquetas (sin valores)."""
        import unidades as _u, idioma as _i18n
        sel = [d for d in PROP_RESUMEN if d[0] in self._props_sel]
        self.tbl_res.setRowCount(len(sel))
        for i, (key, base, mag, fmt, has_mix) in enumerate(sel):
            self.tbl_res.setRowHeight(i, ROW_H)   # mismo alto que las demas
            unidad = f" [{_u.u(mag)}]" if mag else ""
            etq = f"{_i18n.t(base)}{unidad}:"
            self.tbl_res.setItem(i, 0, cell(etq, bg=GRAY_LBL))
            if valores is not None and key in valores:
                mix, vap, liq = valores[key]
            else:
                mix = vap = liq = ""
            self._paint_res(i, 1, mix if has_mix else "")
            self._paint_res(i, 2, vap)
            self._paint_res(i, 3, liq)
        fix_table_size(self.tbl_res)

    def _abrir_selector_props(self):
        """Ventana de selección de propiedades con dos listas: disponibles
        (izquierda) y seleccionadas (derecha), con botones para mover entre
        ellas.  Se mantiene la premisa de exactamente 6 propiedades en el
        resumen del equilibrio."""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                     QListWidget, QListWidgetItem, QPushButton,
                                     QLabel)
        import idioma as _i18n, unidades as _u
        MAX = len(PROP_DEFAULT)   # número exacto de propiedades a mostrar (6)

        def etiqueta(key):
            base = _PROP_DEF[key][1]; mag = _PROP_DEF[key][2]
            unidad = f" [{_u.u(mag)}]" if mag else ""
            return f"{_i18n.t(base)}{unidad}"

        dlg = QDialog(self)
        dlg.setWindowTitle(_i18n.t("Propiedades a mostrar"))
        dlg.setStyleSheet('QDialog { background:#e0e0e0; }')
        root = QVBoxLayout(dlg)
        root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)

        info = QLabel(_i18n.t(
            "Seleccione las propiedades a mostrar en el resumen:"))
        info.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                           f'color:{TEXT};background:transparent;')
        root.addWidget(info)

        list_qss = (f'QListWidget {{ background:{WHITE}; border:1px solid {BORDER};'
                    f' font-family:"{FONT_F}"; font-size:{FS}pt; }}'
                    f'QListWidget::item {{ height:22px; padding-left:4px; }}'
                    f'QListWidget::item:selected {{ background:#DCDCDC;'
                    f' color:{TEXT}; }}')
        btn_qss = (f'background:{GRAY_LBL};border:2px outset {BORDER};'
                   f'font-family:"{FONT_F}";font-size:{FS}pt;')

        cols = QHBoxLayout(); cols.setSpacing(12)

        # Columna izquierda: disponibles
        col_izq = QVBoxLayout(); col_izq.setSpacing(3)
        lbl_disp = QLabel(_i18n.t("Disponibles"))
        lbl_disp.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                               f'color:{TEXT};background:transparent;')
        col_izq.addWidget(lbl_disp)
        lista_disp = QListWidget(); lista_disp.setStyleSheet(list_qss)
        lista_disp.setFixedSize(240, 240)
        col_izq.addWidget(lista_disp)
        cols.addLayout(col_izq)

        # Columna derecha: seleccionadas
        col_der = QVBoxLayout(); col_der.setSpacing(3)
        lbl_sel = QLabel(_i18n.t("Seleccionadas"))
        lbl_sel.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                              f'color:{TEXT};background:transparent;')
        col_der.addWidget(lbl_sel)
        lista_sel = QListWidget(); lista_sel.setStyleSheet(list_qss)
        lista_sel.setFixedSize(240, 240)
        col_der.addWidget(lista_sel)
        cols.addLayout(col_der)

        root.addLayout(cols)

        def add_item(lista, key):
            it = QListWidgetItem(etiqueta(key))
            it.setData(Qt.ItemDataRole.UserRole, key)
            lista.addItem(it)
        for key in self._props_sel:
            add_item(lista_sel, key)
        for key, *_ in PROP_RESUMEN:
            if key not in self._props_sel:
                add_item(lista_disp, key)

        # Fila única inferior: contador a la izquierda; botones Agregar,
        # Quitar, OK y Cancel a la derecha, todos a la misma altura.
        fila = QHBoxLayout(); fila.setSpacing(8)
        contador = QLabel()
        contador.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                               f'color:{TEXT};background:transparent;')
        fila.addWidget(contador)
        fila.addStretch()

        btn_add = QPushButton(_i18n.t("Agregar"))
        btn_rem = QPushButton(_i18n.t("Quitar"))
        btn_ok  = QPushButton(_i18n.t("Aceptar"))
        btn_cancel = QPushButton(_i18n.t("Cancelar"))
        for b in (btn_add, btn_rem, btn_ok, btn_cancel):
            b.setFixedHeight(26); b.setMinimumWidth(84)
            b.setStyleSheet(btn_qss)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            fila.addWidget(b)
        root.addLayout(fila)

        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)

        def _actualizar():
            n = lista_sel.count()
            contador.setText(_i18n.t("Seleccionadas: ") + f"{n} / {MAX}")
            btn_ok.setEnabled(n == MAX)
            btn_add.setEnabled(n < MAX and lista_disp.count() > 0)
            btn_rem.setEnabled(lista_sel.count() > 0)

        def _mover(origen, destino):
            it = origen.currentItem()
            if it is None:
                return
            key = it.data(Qt.ItemDataRole.UserRole)
            origen.takeItem(origen.row(it))
            add_item(destino, key)
            _actualizar()

        def _agregar():
            if lista_sel.count() < MAX:
                _mover(lista_disp, lista_sel)
        def _quitar():
            _mover(lista_sel, lista_disp)

        btn_add.clicked.connect(_agregar)
        btn_rem.clicked.connect(_quitar)
        lista_disp.itemDoubleClicked.connect(lambda _: _agregar())
        lista_sel.itemDoubleClicked.connect(lambda _: _quitar())
        _actualizar()

        dlg.adjustSize(); dlg.setFixedSize(dlg.sizeHint())

        if dlg.exec():
            nuevos = [lista_sel.item(i).data(Qt.ItemDataRole.UserRole)
                      for i in range(lista_sel.count())]
            if not nuevos:
                nuevos = list(PROP_DEFAULT)
            self._props_sel = nuevos
            if getattr(self, 'last_result', None) is not None:
                self._render(self.last_result)
            else:
                self._rebuild_resumen()

    def _render(self, r):
        masa = self.btn_frac.isChecked()
        V=r["V"]; L=r["L"]
        ZV=r.get("ZV"); ZL=r.get("ZL")
        x=r["x"]; y=r["y"]
        PM_v=r.get("PM_v"); PM_l=r.get("PM_l"); PM_z=r.get("PM_z")
        rho_v=r.get("rho_v"); rho_l=r.get("rho_l")
        sg_v=r.get("sg_v"); sg_l=r.get("sg_l")
        Vm=r["Vm"]; Lm=r["Lm"]
        modo=r["modo"]
        # Densidad al sistema de unidades activo (MW y Z no cambian)
        import unidades as _u
        rho_v = _u.dens_desde(rho_v) if rho_v else rho_v
        rho_l = _u.dens_desde(rho_l) if rho_l else rho_l

        rho_z = None
        if rho_v and rho_l:
            inv = (Vm/rho_v if rho_v>0 else 0)+(Lm/rho_l if rho_l>0 else 0)
            if inv>0: rho_z = 1.0/inv
        elif rho_l: rho_z = rho_l
        elif rho_v: rho_z = rho_v

        def f(v, d=4):
            return f"{v:.{d}f}" if v is not None else ""

        def paint(item, txt):
            item.setText(txt)
            if txt:
                item.setBackground(_brush(WHITE))
                item.setForeground(_brush(TEXT_RES))
            else:
                item.setBackground(_brush(GRAY_RES))
                item.setForeground(_brush(TEXT))

        # ── Resumen: construir segun las propiedades seleccionadas ──
        Hs = _u.H_desde(r.get('H_stream')) if r.get('H_stream') is not None else None
        Hv = _u.H_desde(r.get('H_vapor'))  if r.get('H_vapor')  is not None else None
        Hl = _u.H_desde(r.get('H_liquido'))if r.get('H_liquido')is not None else None
        Ss = _u.S_desde(r.get('S_stream')) if r.get('S_stream') is not None else None
        Sv = _u.S_desde(r.get('S_vapor'))  if r.get('S_vapor')  is not None else None
        Sl = _u.S_desde(r.get('S_liquido'))if r.get('S_liquido')is not None else None
        vap_ok = V > 1e-9
        liq_ok = L > 1e-9
        def cv(val, ok, d=4):
            return f(val, d) if (val is not None and ok) else ""
        mu_v = r.get('mu_v'); mu_l = r.get('mu_l')   # viscosidad (cP)
        valores = {
            'frac_molar':  ("",          cv(V, vap_ok),  cv(L, liq_ok)),
            'frac_masica': ("",          cv(Vm, vap_ok), cv(Lm, liq_ok)),
            'sg':          ("",          cv(sg_v, vap_ok),cv(sg_l, liq_ok)),
            'densidad':    (f(rho_z),    cv(rho_v, vap_ok),cv(rho_l, liq_ok)),
            'z':           ("",          cv(ZV, vap_ok), cv(ZL, liq_ok)),
            'pm':          (f(PM_z),     cv(PM_v, vap_ok),cv(PM_l, liq_ok)),
            'entalpia':    (f(Hs, 2),    cv(Hv, vap_ok, 2),cv(Hl, liq_ok, 2)),
            'entropia':    (f(Ss),       cv(Sv, vap_ok), cv(Sl, liq_ok)),
            'viscosidad':  ("",          cv(mu_v, vap_ok, 5),cv(mu_l, liq_ok, 5)),
        }
        self._rebuild_resumen(valores)

        # ── Composiciones ─────────────────────────────────────
        sy = sx = 0
        self.tbl_comp.blockSignals(True)
        for i in range(NC):
            yi = y[i] if i < len(y) else 0
            xi = x[i] if i < len(x) else 0
            if masa:
                yi_s = yi*PM[i]/PM_v if (PM_v and PM_v>0) else 0
                xi_s = xi*PM[i]/PM_l if (PM_l and PM_l>0) else 0
            else:
                yi_s, xi_s = yi, xi
            sy += yi_s; sx += xi_s
            tv = f"{yi_s:.4f}" if V>0 else ""
            tl = f"{xi_s:.4f}" if L>0 else ""
            it2 = self.tbl_comp.item(i,2)
            it3 = self.tbl_comp.item(i,3)
            it2.setText(tv); it2.setBackground(_brush(WHITE if tv else GRAY_RES))
            it3.setText(tl); it3.setBackground(_brush(WHITE if tl else GRAY_RES))
        self.tbl_comp.blockSignals(False)

        ts2 = f"{sy:.4f}" if V>0 else ""
        ts3 = f"{sx:.4f}" if L>0 else ""
        self.tbl_comp.item(self.sum_row,2).setText(ts2)
        self.tbl_comp.item(self.sum_row,3).setText(ts3)
        self.tbl_comp.item(self.sum_row,2).setBackground(_brush(WHITE if ts2 else GRAY_RES))
        self.tbl_comp.item(self.sum_row,3).setBackground(_brush(WHITE if ts3 else GRAY_RES))


# ══════════════════════════════════════════════════════════════
# Tab 2 — Parámetros EOS
# ══════════════════════════════════════════════════════════════
class TabParametros(QWidget):
    def __init__(self, objetivo=None):
        # objetivo=None -> edita el kij global; objetivo=dict fluido -> edita
        # el kij independiente de ese fluido (objetivo['kij']).
        super().__init__()
        self._objetivo = objetivo
        self._WK = 65
        self._build()

    def _kij(self):
        """Matriz kij que edita esta tabla (global o la del fluido)."""
        if self._objetivo is not None:
            return self._objetivo['kij']
        return kij_user

    def _fuente(self):
        """EOS-fuente de los kij ('PR'/'SRK'/'PR_PVT'/'SRK_PVT')."""
        global kij_fuente
        if self._objetivo is not None:
            return self._objetivo.get('kij_fuente', self._objetivo.get('eos', 'PR'))
        return kij_fuente

    def _on_fuente(self, idx):
        """Cambia la fuente de kij (una de las 4 EOS) y recarga la matriz."""
        global kij_user, kij_fuente
        code = _eos_code(idx)
        nueva = _eng.kij_base(code)
        if self._objetivo is not None:
            self._objetivo['kij_fuente'] = code
            self._objetivo['kij'] = nueva
        else:
            kij_fuente = code
            kij_user = nueva
        self.refrescar_tabla()

    def _eos_ctx(self):
        """EOS del contexto (para las propiedades criticas): global o fluido."""
        if self._objetivo is not None:
            return self._objetivo.get('eos', 'PR')
        return _eng.get_eos()

    def _llenar_criticas(self):
        """Rellena la tabla de propiedades criticas segun la EOS del contexto
        (HYSYS o PVTsim), convertidas al sistema de unidades activo."""
        import unidades as _u
        TCa, PCa, OMa, PMa = _eng.crit_props(self._eos_ctx())
        for i in range(NC):
            r = i + 1
            self.tbl_p.setItem(r, 0, cell(NOMBRES[i], bg=GRAY_LBL,
                align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
            tc = _u.abs_desde_R(TCa[i])       # °R -> °R/K
            pc = _u.p_desde_psia(PCa[i])      # psi -> psi/kPa
            for c, v in enumerate([f"{tc:.4f}", f"{pc:.4f}",
                                   f"{OMa[i]:.8f}", f"{PMa[i]}"]):
                self.tbl_p.setItem(r, c+1, cell(v, bg=WHITE, color=TEXT_RES))
        # Cabeceras de Tc y Pc con la unidad activa
        self.tbl_p.setItem(0, 1, cell(
            f"{_i18n.t('Temperatura Critica')} ({_u.u_abs()})", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))
        self.tbl_p.setItem(0, 2, cell(
            f"{_i18n.t('Presion Critica')} ({_u.u('P')})", bg=GRAY_LBL,
            align=Qt.AlignmentFlag.AlignCenter))

    def aplicar_unidades(self, old=None):
        """Reconvierte las propiedades criticas (Tc, Pc) al sistema activo."""
        self._llenar_criticas()

    def _sync_desde_objetivo(self):
        """Refresca kij, propiedades criticas y el desplegable de fuente
        cuando cambia la EOS (global o del fluido)."""
        self.refrescar_tabla()
        self._llenar_criticas()
        if hasattr(self, 'cmb_fuente'):
            self.cmb_fuente.blockSignals(True)
            self.cmb_fuente.setCurrentIndex(_eos_idx(self._fuente()))
            self.cmb_fuente.blockSignals(False)

    def tam_ideal(self):
        """Tamaño (ancho, alto) que hace entrar todo el contenido justo, sin
        scrollbars ni espacio sobrante.  El alto depende del número de
        componentes activos (filas visibles)."""
        WK = self._WK
        n_act = getattr(self, '_n_activos', NC)
        ancho_tabla = (n_act + 1) * WK + 2   # columnas kij visibles + borde
        margen_lat = 13
        ancho = ancho_tabla + 2*margen_lat
        h_tbl = (n_act+1)*ROW_H + 2   # cabecera + filas activas + borde
        alto = 8 + 22 + 3 + h_tbl + 3 + 22 + 3 + h_tbl + 3 + 30
        return (ancho, alto)

    def aplicar_componentes_activos(self, activos):
        """Oculta filas y columnas de los componentes inactivos en ambas
        tablas (propiedades críticas y coeficientes kij) y reajusta tamaños.
        En tbl_p el componente i está en la fila i+1; en tbl_k está en la
        fila i+1 y la columna i+1 (fila/col 0 son cabeceras)."""
        activos_set = set(activos)
        self._n_activos = len(activos_set)
        # Tabla de propiedades críticas: ocultar filas de datos inactivas
        for i in range(NC):
            self.tbl_p.setRowHidden(i+1, i not in activos_set)
        # Tabla kij: ocultar filas y columnas inactivas
        for i in range(NC):
            oculto = i not in activos_set
            self.tbl_k.setRowHidden(i+1, oculto)
            self.tbl_k.setColumnHidden(i+1, oculto)
        # Reajustar alturas y anchos de ambas tablas contando solo lo visible
        n = self._n_activos
        self.tbl_p.setFixedHeight((n+1)*ROW_H + 2)
        self.tbl_k.setFixedHeight((n+1)*ROW_H + 2)
        # Ancho de la tabla kij = (activos + 1) columnas
        WK = self._WK
        self.tbl_k.setFixedWidth((n+1)*WK + 2)
        # La tabla de propiedades mantiene su ancho de columnas fijas (WP)
        # porque sus columnas no son por componente.

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(13,4,13,4)
        outer.setSpacing(3)
        self.setStyleSheet(f'background:{GRAY_LBL};')

        WP = [250, 170, 165, 155, 170]   # suma 910 = ancho de la tabla kij
        WK = 65

        # ─── Tabla propiedades críticas (título+cabecera+datos en una sola tabla) ─
        outer.addWidget(title_label("Propiedades criticas y factor acentrico"))

        self.tbl_p = QTableWidget(NC+1, 5)  # fila 0=cabecera, filas 1..NC=datos
        self.tbl_p.horizontalHeader().hide()
        self.tbl_p.verticalHeader().hide()
        self.tbl_p.setShowGrid(True)
        self.tbl_p.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_p.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;gridline-color:{BORDER};}}'
            f'QTableWidget::item {{ padding:2px 6px; }}')
        for c,w in enumerate(WP): self.tbl_p.setColumnWidth(c,w)
        for r in range(NC+1): self.tbl_p.setRowHeight(r, ROW_H)

        # Fila 0: cabecera (se desplaza con scroll)
        for c,h in enumerate(["Componente","Temperatura Critica (°R)",
                               "Presion Critica (psi)","Factor acentrico",
                               "Peso Molecular (lb/lb-mol)"]):
            self.tbl_p.setItem(0,c, cell(h, bg=GRAY_LBL,
                align=Qt.AlignmentFlag.AlignCenter))

        # Filas 1..NC: datos (segun la EOS del contexto)
        self._llenar_criticas()

        self.tbl_p.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_p.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_p.setFixedHeight((NC+1)*ROW_H + 2)   # filas + borde (1 px por lado)
        self.tbl_p.setFixedWidth(sum(WP) + 2)   # columnas + borde (1 px por lado)
        outer.addWidget(self.tbl_p, alignment=Qt.AlignmentFlag.AlignHCenter)

        # ─── Tabla kij (cabecera+datos en una sola tabla) ─────
        outer.addWidget(title_label("Coeficientes de interaccion binaria"))

        self.tbl_k = QTableWidget(NC+1, NC+1)  # fila 0=cabecera
        self.tbl_k.horizontalHeader().hide()
        self.tbl_k.verticalHeader().hide()
        self.tbl_k.setShowGrid(True)
        self.tbl_k.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;gridline-color:{BORDER};}}'
            f'QTableWidget::item {{ padding:2px 4px; }}')
        self.tbl_k.setColumnWidth(0, WK)
        for c in range(1,NC+1): self.tbl_k.setColumnWidth(c, WK)
        for r in range(NC+1): self.tbl_k.setRowHeight(r, ROW_H)

        # Fila 0: cabecera (se desplaza con scroll)
        self.tbl_k.setItem(0,0, cell("", bg=GRAY_LBL))
        for j,comp in enumerate(COMPONENTES):
            self.tbl_k.setItem(0,j+1, cell(comp, bg=GRAY_LBL,
                align=Qt.AlignmentFlag.AlignCenter))

        # Filas 1..NC: datos
        for i in range(NC):
            r = i+1
            self.tbl_k.setItem(r,0, cell(COMPONENTES[i], bg=GRAY_LBL,
                align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
            for j in range(NC):
                v = self._kij()[i][j]
                if i == j:
                    it = cell(f"{v:.5f}", bg=GRAY_LBL,
                        color=TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter)
                    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    it = cell(f"{v:.5f}", bg=WHITE, color=TEXT_RES,
                        align=Qt.AlignmentFlag.AlignCenter, editable=True)
                self.tbl_k.setItem(r,j+1, it)

        self.tbl_k.itemChanged.connect(self._on_kij)
        self.tbl_k.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_k.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_k.setFixedHeight(310)
        self.tbl_k.setFixedWidth((NC+1)*WK + 2)   # columnas + borde
        outer.addWidget(self.tbl_k, alignment=Qt.AlignmentFlag.AlignHCenter)

        bot = QHBoxLayout()
        lf = QLabel("Fuente de los coeficientes de iteracion binaria:")
        lf.setStyleSheet(
            f'color:{TEXT};font-size:{FS}pt;font-family:"{FONT_F}";'
            f'background:transparent;')
        bot.addWidget(lf)
        self.cmb_fuente = QComboBox()
        self.cmb_fuente.addItems(EOS_ITEMS)
        _aplicar_estilo_combo(self.cmb_fuente)
        self.cmb_fuente.setFixedWidth(190)
        self.cmb_fuente.setCurrentIndex(_eos_idx(self._fuente()))
        self.cmb_fuente.currentIndexChanged.connect(self._on_fuente)
        bot.addWidget(self.cmb_fuente)
        bot.addStretch()
        btn_r = QPushButton("Restaurar valores originales")
        btn_r.setFixedWidth(220)
        btn_r.setStyleSheet(
            f'background:{GRAY_LBL};border:2px outset {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
        btn_r.clicked.connect(self._reset)
        bot.addWidget(btn_r)
        outer.addLayout(bot)

    def _on_kij(self, item):
        r = item.row(); c = item.column()
        if r < 1 or c < 1: return   # fila 0 = cabecera
        i = r-1; j = c-1
        if i == j: return
        try:
            v = float(item.text())
            m = self._kij()
            m[i][j] = v
            m[j][i] = v
            self.tbl_k.blockSignals(True)
            sym = self.tbl_k.item(j+1, i+1)  # +1 por fila de cabecera
            if sym: sym.setText(f"{v:.5f}")
            item.setBackground(_brush(WHITE))
            item.setForeground(_brush(TEXT_RES))
            self.tbl_k.blockSignals(False)
        except: pass

    def refrescar_tabla(self):
        """Refresca la tabla visible desde la matriz kij correspondiente
        (global o la del fluido). Sin diálogo."""
        m = self._kij()
        self.tbl_k.blockSignals(True)
        for i in range(NC):
            for j in range(NC):
                it = self.tbl_k.item(i+1, j+1)  # +1 por fila de cabecera
                if it and i != j:
                    it.setText(f"{m[i][j]:.5f}")
        self.tbl_k.blockSignals(False)

    def _reset(self):
        # Restaura al default de la EOS-fuente seleccionada.
        nuevo = _eng.kij_base(self._fuente())
        if self._objetivo is not None:
            self._objetivo['kij'] = nuevo
        else:
            global kij_user
            kij_user = nuevo
        self.refrescar_tabla()
        dialogos.info(self, "Coeficientes restaurados.")



# ══════════════════════════════════════════════════════════════
# Pantalla de Carga (Splash Screen)
# ══════════════════════════════════════════════════════════════
class SplashScreen(QWidget):
    """Pantalla de carga mostrada mientras ThermoPhase inicia."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(340, 269)
        self._img = None
        # Cargar imagen splash
        _sp = ruta_recurso('splash.png')
        if os.path.exists(_sp):
            from PyQt6.QtGui import QPixmap
            self._img = QPixmap(_sp)
        # Centrar en pantalla
        from PyQt6.QtWidgets import QApplication
        sg = QApplication.primaryScreen().geometry()
        self.move((sg.width()-340)//2, (sg.height()-269)//2)

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QColor, QPen, QFont
        from PyQt6.QtCore import Qt as _Qt
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._img:
            p.drawPixmap(0, 0, self._img)
        else:
            # Fallback: rectángulo oscuro con texto
            p.setBrush(QColor(20,10,5))
            p.setPen(_Qt.PenStyle.NoPen)
            p.drawRoundedRect(0,0,420,260,16,16)
            p.setPen(QColor(240,144,48))
            fnt = QFont("Arial Narrow", 28, QFont.Weight.Bold)
            p.setFont(fnt)
            p.drawText(50,80,320,60, _Qt.AlignmentFlag.AlignCenter, "ThermoPhase")
            p.setPen(QColor(200,160,120))
            fnt2 = QFont("Arial Narrow", 11)
            p.setFont(fnt2)
            p.drawText(50,140,320,40, _Qt.AlignmentFlag.AlignCenter,
                       "Software de Equilibrio de Fases")
        p.end()

# ══════════════════════════════════════════════════════════════
class ScrollableTabBar(QTabBar):
    """
    QTabBar sin flechas visibles pero con el mecanismo interno de scroll
    activo. Al hacer clic en una pestaña que quedo parcialmente cortada por
    el borde de la barra, se fuerza el scroll para dejarla visible. Ademas
    se agrega soporte para la rueda del mouse sobre la barra de pestañas.
    """
    def mousePressEvent(self, e):
        idx = self.tabAt(e.pos())
        if idx >= 0:
            r  = self.tabRect(idx)
            br = self.rect()
            if r.left() < br.left() or r.right() > br.right():
                # Pestaña parcialmente oculta: la seleccionamos primero para
                # que Qt haga scroll interno y quede visible por completo.
                self.setCurrentIndex(idx)
                e.accept()
                return
        super().mousePressEvent(e)

    def wheelEvent(self, e):
        # Un tick de rueda = una pestaña arriba o abajo.
        step = -1 if e.angleDelta().y() > 0 else 1
        new_idx = max(0, min(self.count() - 1, self.currentIndex() + step))
        if new_idx != self.currentIndex():
            self.setCurrentIndex(new_idx)
        e.accept()


class PdfWorker(QThread):
    """Genera el PDF en segundo plano para no congelar la interfaz."""
    done = pyqtSignal(bool, str)

    def __init__(self, estado, path):
        super().__init__()
        self.estado = estado
        self.path   = path

    def run(self):
        try:
            from reporte_pdf import generar_pdf
            ok, msg = generar_pdf(self.estado, self.path)
            self.done.emit(ok, msg)
        except Exception as ex:
            import traceback
            self.done.emit(False, f"Error inesperado:\n{ex}\n{traceback.format_exc()}")


class TabFluidos(QWidget):
    """Gestor de fluidos: guarda varias composiciones (cromatografias) con
    nombre, permite editarlas, cargarlas en la composicion principal y abrir
    calculos independientes por fluido para compararlos entre si."""

    def __init__(self, fluidos, get_z_actual, cargar_en_principal, abrir_calc,
                 on_change=None, on_comp_change=None):
        super().__init__()
        self.fluidos = fluidos                 # lista compartida de dicts
        self._get_z_actual = get_z_actual
        self._cargar_principal = cargar_en_principal
        self._abrir_calc = abrir_calc
        self._on_change = on_change
        self._on_comp_change = on_comp_change
        self._idx = -1
        self._build()
        self._refrescar_lista()

    def _build(self):
        BTN = (f'background:{GRAY_LBL};border:2px outset {BORDER};'
               f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;'
               f'padding:1px 8px;')
        box = QWidget(); box.setFixedWidth(712)
        box.setStyleSheet('background:#ECECEC;')
        root = QVBoxLayout(box)
        root.setContentsMargins(0, 8, 0, 8); root.setSpacing(6)
        root.addWidget(title_label("ThermoPhase — Fluidos"))

        fila = QHBoxLayout(); fila.setSpacing(10)

        # Izquierda: lista de fluidos + gestion
        izq = QVBoxLayout(); izq.setSpacing(4)
        izq.addWidget(section_label("Fluidos guardados", left=True))
        self.lista = QListWidget(); self.lista.setFixedWidth(250)
        self.lista.setStyleSheet(
            f'QListWidget {{ background:{WHITE}; border:1px solid {BORDER};'
            f' font-family:"{FONT_F}"; font-size:{FS}pt; outline:0; }}'
            f'QListWidget::item {{ height:22px; padding-left:4px; }}'
            f'QListWidget::item:selected {{ background:#DCDCDC; color:{TEXT}; }}')
        self.lista.currentRowChanged.connect(self._on_sel)
        izq.addWidget(self.lista)
        g1 = QGridLayout(); g1.setSpacing(4)
        for k, (txt, fn) in enumerate([("Nuevo", self._nuevo),
                                       ("Capturar actual", self._capturar),
                                       ("Renombrar", self._renombrar),
                                       ("Eliminar", self._eliminar)]):
            b = QPushButton(txt); b.setStyleSheet(BTN); b.clicked.connect(fn)
            g1.addWidget(b, k // 2, k % 2)
        izq.addLayout(g1)
        izq.addStretch()
        fila.addLayout(izq)

        # Derecha: composicion del fluido seleccionado
        der = QVBoxLayout(); der.setSpacing(4)
        der.addWidget(section_label("Composicion del fluido (fraccion molar)", left=True))
        self.tbl = make_table(NC + 1, 2)
        self.tbl.setColumnWidth(0, W_COMP); self.tbl.setColumnWidth(1, W_VAL)
        for i in range(NC):
            self.tbl.setItem(i, 0, cell(NOMBRES[i], bg=GRAY_LBL))
            self.tbl.setItem(i, 1, cell("", bg=WHITE, editable=True))
        self.tbl.setItem(NC, 0, cell("Sumatorias:", bg=GRAY_LBL))
        self.tbl.setItem(NC, 1, cell("", bg=WHITE))
        fix_table_size(self.tbl)
        self.tbl.itemChanged.connect(self._on_edit)
        der.addWidget(self.tbl, alignment=Qt.AlignmentFlag.AlignLeft)
        g2 = QHBoxLayout(); g2.setSpacing(4)
        for txt, fn in [("Normalizar", self._normalizar),
                        ("Cargar en composicion principal", self._cargar)]:
            b = QPushButton(txt); b.setStyleSheet(BTN); b.clicked.connect(fn)
            g2.addWidget(b)
        g2.addStretch()
        der.addLayout(g2); der.addStretch()
        fila.addLayout(der)
        root.addLayout(fila)

        root.addWidget(section_label(
            "Abrir calculo del fluido seleccionado (ventana independiente):", left=True))
        g3 = QHBoxLayout(); g3.setSpacing(4)
        for txt, clave in [("Equilibrio de fases", "equilibrio"),
                           ("Envolvente de fases", "envolvente"),
                           ("Puntos de saturación", "saturacion"),
                           ("Propiedades termodinámicas", "propiedades"),
                           ("Parámetros EOS", "parametros")]:
            b = QPushButton(txt); b.setStyleSheet(BTN)
            b.clicked.connect(lambda _=False, c=clave: self._abrir(c))
            g3.addWidget(b)
        g3.addStretch()
        root.addLayout(g3)
        root.addStretch()

        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        hc = QHBoxLayout(); hc.addStretch(); hc.addWidget(box); hc.addStretch()
        outer.addLayout(hc)

    # ── Lista / seleccion ────────────────────────────────────
    def _refrescar_lista(self):
        self.lista.blockSignals(True)
        self.lista.clear()
        for f in self.fluidos:
            self.lista.addItem(f['nombre'])
        self.lista.blockSignals(False)
        if self.fluidos:
            r = min(max(self._idx, 0), len(self.fluidos) - 1)
            self.lista.setCurrentRow(r); self._on_sel(r)
        else:
            self._idx = -1; self._mostrar_z([0.0] * NC)
        if self._on_change:
            self._on_change()

    def _on_sel(self, row):
        self._idx = row
        if 0 <= row < len(self.fluidos):
            self._mostrar_z(self.fluidos[row]['z'])

    def _mostrar_z(self, z):
        self.tbl.blockSignals(True)
        for i in range(NC):
            self.tbl.item(i, 1).setText(f"{z[i] if i < len(z) else 0.0:.4f}")
        self.tbl.blockSignals(False)
        self._upd_suma()

    def _leer_z(self):
        z = []
        for i in range(NC):
            try: z.append(float(self.tbl.item(i, 1).text()))
            except: z.append(0.0)
        return z

    def _upd_suma(self):
        s = sum(self._leer_z())
        self.tbl.blockSignals(True)
        self.tbl.item(NC, 1).setText(f"{s:.4f}")
        self.tbl.blockSignals(False)

    def _on_edit(self, item):
        if item.column() != 1 or item.row() >= NC:
            return
        self._upd_suma()
        if 0 <= self._idx < len(self.fluidos):
            self.fluidos[self._idx]['z'] = self._leer_z()
            if self._on_comp_change:
                self._on_comp_change(self.fluidos[self._idx])

    # ── Acciones de gestion ──────────────────────────────────
    def _nombre_nuevo(self, base=None):
        if base is None: base = _i18n.t("Fluido")
        existentes = {f['nombre'] for f in self.fluidos}
        i = 1
        while f"{base} {i}" in existentes:
            i += 1
        return f"{base} {i}"

    def _nuevo(self):
        self.fluidos.append({'nombre': self._nombre_nuevo(), 'z': [0.0] * NC,
                             'eos': 'PR', 'kij': copy.deepcopy(KIJ_DEFAULT),
                             'kij_fuente': 'PR'})
        self._idx = len(self.fluidos) - 1
        self._refrescar_lista()

    def _capturar(self):
        z = list(self._get_z_actual())
        self.fluidos.append({'nombre': self._nombre_nuevo(_i18n.t("Cromatografia")),
                             'z': z, 'eos': 'PR',
                             'kij': copy.deepcopy(KIJ_DEFAULT),
                             'kij_fuente': 'PR'})
        self._idx = len(self.fluidos) - 1
        self._refrescar_lista()

    def _renombrar(self):
        if not (0 <= self._idx < len(self.fluidos)):
            return
        actual = self.fluidos[self._idx]['nombre']
        nuevo, ok = QInputDialog.getText(self, "Renombrar fluido", "Nombre:", text=actual)
        if ok and nuevo.strip():
            self.fluidos[self._idx]['nombre'] = nuevo.strip()
            self._refrescar_lista()

    def _eliminar(self):
        if not (0 <= self._idx < len(self.fluidos)):
            return
        del self.fluidos[self._idx]
        self._idx = min(self._idx, len(self.fluidos) - 1)
        self._refrescar_lista()

    def _normalizar(self):
        z = self._leer_z(); s = sum(z)
        if s <= 0:
            return
        self._mostrar_z([v / s for v in z])
        if 0 <= self._idx < len(self.fluidos):
            self.fluidos[self._idx]['z'] = self._leer_z()

    def _cargar(self):
        if 0 <= self._idx < len(self.fluidos):
            self._cargar_principal(list(self.fluidos[self._idx]['z']))
            dialogos.info(self, _i18n.t(
                "Fluido «%s» cargado en la composicion principal.")
                % self.fluidos[self._idx]['nombre'])

    def _abrir(self, clave):
        if not (0 <= self._idx < len(self.fluidos)):
            dialogos.advertencia(self, "Selecciona un fluido primero.")
            return
        self._abrir_calc(clave, self.fluidos[self._idx])

    def refrescar(self):
        self._idx = 0 if self.fluidos else -1
        self._refrescar_lista()


class _Ventana(QWidget):
    """Ventana de funcionalidad como ventana top-level de Windows: usa el
    marco/barra de titulo NATIVO del sistema (icono + minimizar/maximizar/
    cerrar), igual que la ventana principal, y puede moverse libremente por
    la pantalla. Al cerrarse se OCULTA (no se destruye) para conservar su
    contenido y estado al reabrirla desde el navegador."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window)

    def closeEvent(self, ev):
        ev.ignore()
        self.hide()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThermoPhase")
        # Ventana redimensionable / maximizable. El contenido de cada pestaña
        # sigue siendo de tamaño fijo (se envuelve en un QScrollArea), pero la
        # ventana ya puede maximizarse, minimizarse y ajustarse libremente.
        self.setMinimumSize(920, 620)
        self.resize(1300, 840)
        self.current_path = None        # ruta del .tpsim actual (None = sin guardar)
        self.fluidos = []               # lista de fluidos guardados (gestor Fluidos)
        # Componentes activos del fluido: conjunto de índices (0..NC-1).
        # Inicialmente todos activos.  Los inactivos se ocultan en las tablas
        # y su fracción molar se fuerza a 0 (el motor los ignora).
        self.componentes_activos = list(range(NC))
        self._build()
        # Gestor de edicion (copiar/pegar/deshacer/rehacer sobre celdas).
        self.gestor_edicion = edicion.GestorEdicion()
        self.gestor_edicion.registrar(self.tab_eq.tbl_comp)
        self.gestor_edicion.registrar(self.tab_par.tbl_k)
        self._construir_menu()
        self._actualizar_titulo()

    def _construir_menu(self):
        """Barra de menu clasica (Win95): Archivo, Editar, Ver, Herramientas,
        Exportar, Ventana, Ayuda."""
        CARA = "#D4D4D4"
        menubar = self.menuBar()
        menubar.setStyleSheet(
            f'QMenuBar {{ background:{CARA}; color:#000000;'
            f'  font-family:"{FONT_F}"; font-size:{FS}pt;'
            f'  border-bottom:1px solid #7F7F7F; }}'
            f'QMenuBar::item {{ padding:3px 9px; background:transparent; }}'
            f'QMenuBar::item:selected {{ background:#DCDCDC; color:#000000; }}'
            f'QMenuBar::item:pressed {{ background:#DCDCDC; color:#000000; }}'
            f'QMenu {{ background:{CARA}; color:#000000;'
            f'  border:1px solid #7F7F7F;'
            f'  font-family:"{FONT_F}"; font-size:{FS}pt; }}'
            f'QMenu::item {{ padding:3px 24px 3px 20px; }}'
            f'QMenu::item:selected {{ background:#DCDCDC; color:#000000; }}'
            f'QMenu::item:disabled {{ color:#909090; }}'
            f'QMenu::separator {{ height:1px; margin:3px 4px;'
            f'  background:#BFBFBF; }}')

        def _act(texto, slot, atajo=None):
            a = QAction(texto, self)
            if atajo is not None:
                a.setShortcut(atajo)
            a.triggered.connect(slot)
            return a

        # ── Archivo ──────────────────────────────────────────
        m_arch = menubar.addMenu("&Archivo")
        m_arch.addAction(_act("&Nuevo", self._menu_nuevo,
                              QKeySequence.StandardKey.New))
        m_arch.addAction(_act("&Abrir...", self._menu_abrir,
                              QKeySequence.StandardKey.Open))
        m_arch.addSeparator()
        m_arch.addAction(_act("&Guardar", self._menu_guardar,
                              QKeySequence.StandardKey.Save))
        m_arch.addAction(_act("Guardar &como...", self._menu_guardar_como,
                              QKeySequence.StandardKey.SaveAs))
        m_arch.addSeparator()
        m_arch.addAction(_act("&Imprimir / Exportar a PDF...",
                              self._menu_exportar_pdf))
        m_arch.addSeparator()
        m_arch.addAction(_act("&Salir", self.close,
                              QKeySequence.StandardKey.Quit))

        # ── Editar ───────────────────────────────────────────
        m_edit = menubar.addMenu("&Editar")
        m_edit.addAction(_act("&Deshacer", self.gestor_edicion.deshacer,
                              QKeySequence.StandardKey.Undo))
        m_edit.addAction(_act("&Rehacer", self.gestor_edicion.rehacer,
                              QKeySequence.StandardKey.Redo))
        m_edit.addSeparator()
        m_edit.addAction(_act("&Copiar", self.gestor_edicion.copiar,
                              QKeySequence.StandardKey.Copy))
        m_edit.addAction(_act("&Pegar", self.gestor_edicion.pegar,
                              QKeySequence.StandardKey.Paste))

        # ── Ver ──────────────────────────────────────────────
        m_ver = menubar.addMenu("&Ver")
        self._act_nav = QAction("&Navegador", self, checkable=True)
        self._act_nav.setChecked(True)
        self._act_nav.toggled.connect(self._toggle_nav)
        m_ver.addAction(self._act_nav)
        self._act_tb = QAction("Barra de &herramientas", self, checkable=True)
        self._act_tb.setChecked(True)
        self._act_tb.toggled.connect(
            lambda on: self.ribbon.setVisible(on))
        m_ver.addAction(self._act_tb)
        # La X del panel navegador desmarca la opcion de Ver.
        if hasattr(self, 'nav'):
            self.nav.cerrar_pedido.connect(
                lambda: self._act_nav.setChecked(False))

        # ── Herramientas ─────────────────────────────────────
        m_herr = menubar.addMenu("&Herramientas")
        m_herr.addAction(_act("&Asociar archivos .tpsim con este programa",
                              self._menu_asociar))
        m_herr.addAction(_act("&Quitar asociacion de archivos .tpsim",
                              self._menu_desasociar))

        # ── Exportar ─────────────────────────────────────────
        m_exp = menubar.addMenu("&Exportar")
        m_exp.addAction(_act("Exportar resultados a &PDF...",
                             self._menu_exportar_pdf))

        # ── Ventana (gestion del area MDI) ───────────────────
        m_win = menubar.addMenu("Ve&ntana")
        m_win.addAction(_act("&Cascada", lambda: self._cascada()))
        m_win.addAction(_act("&Mosaico", self._mosaico))
        m_win.addSeparator()
        m_win.addAction(_act("Cerrar &todas", self._cerrar_todas))

        # ── Idioma ───────────────────────────────────────────
        import idioma as _i18n
        m_idi = menubar.addMenu("&Idioma")
        self._act_es = QAction("Español", self, checkable=True)
        self._act_en = QAction("Inglés", self, checkable=True)
        self._act_es.setChecked(_i18n.get_idioma() == 'ES')
        self._act_en.setChecked(_i18n.get_idioma() == 'EN')
        self._act_es.triggered.connect(lambda: self._cambiar_idioma('ES'))
        self._act_en.triggered.connect(lambda: self._cambiar_idioma('EN'))
        m_idi.addAction(self._act_es)
        m_idi.addAction(self._act_en)

        # ── Ayuda ────────────────────────────────────────────
        m_ayuda = menubar.addMenu("A&yuda")
        m_ayuda.addAction(_act("&Documentación técnica", self._abrir_documentacion))
        m_ayuda.addSeparator()
        m_ayuda.addAction(_act("&Acerca de ThermoPhase...", self._menu_acerca))

    def _toggle_nav(self, on):
        if hasattr(self, 'nav'):
            self.nav.setVisible(on)

    def _cambiar_idioma(self, lang):
        """Cambia el idioma de TODA la interfaz (principal + subventanas)."""
        import idioma as _i18n
        _i18n.set_idioma(lang)
        self._act_es.setChecked(lang == 'ES')
        self._act_en.setChecked(lang == 'EN')
        # Ventana principal (menus, navegador, barra, status)
        _i18n.retraducir(self)
        # Tooltip del boton de documentacion de la barra
        if hasattr(self.ribbon, 'btn_doc'):
            self.ribbon.btn_doc.setToolTip(_i18n.t("Documentación técnica"))
        # Pestaña principal de equilibrio: reconstruir etiquetas con unidad
        if hasattr(self, 'tab_eq') and hasattr(self.tab_eq, 'aplicar_unidades'):
            import unidades as _u0
            _i18n.retraducir(self.tab_eq)   # traduce etiquetas y combos propios
            try: self.tab_eq.aplicar_unidades(_u0.sistema())
            except Exception: pass
        # Pestaña principal de envolvente: reconstruir etiquetas (incluidas
        # cricondentérmica y cricondenbárica) y re-trazar en el nuevo idioma.
        if hasattr(self, 'tab_env'):
            import unidades as _u0
            _i18n.retraducir(self.tab_env)
            if hasattr(self.tab_env, 'retraducir_grafico'):
                try: self.tab_env.retraducir_grafico()
                except Exception: pass
            if hasattr(self.tab_env, 'aplicar_unidades'):
                try: self.tab_env.aplicar_unidades(_u0.sistema())
                except Exception: pass
        if hasattr(self, 'ribbon'):
            _i18n.retraducir(self.ribbon)
        if hasattr(self, 'nav'):
            _i18n.retraducir(self.nav)
        # Todas las subventanas de funcionalidad (abiertas u ocultas)
        import unidades as _u
        _sis = _u.sistema()
        for sw in self._subventanas.values():
            _i18n.retraducir(sw)
            # Gráficos (envolvente, etc.): re-trazar en el idioma activo
            w = getattr(sw, '_widget', None)
            if w is not None and hasattr(w, 'retraducir_grafico'):
                try: w.retraducir_grafico()
                except Exception: pass
            # Reconstruir etiquetas con unidad en el nuevo idioma (sin
            # convertir valores: old = sistema actual).
            if w is not None and hasattr(w, 'aplicar_unidades'):
                try: w.aplicar_unidades(_sis)
                except Exception: pass
            es_tit = sw.property("_i18n_es_title")
            if es_tit is None:
                es_tit = _i18n._TRAD_INV.get(sw.windowTitle(), sw.windowTitle())
                sw.setProperty("_i18n_es_title", es_tit)
            # Titulos con sufijo " - Nombre" (por fluido): traducir solo la parte
            base = es_tit.split(" - ")[0]
            resto = es_tit[len(base):]
            sw.setWindowTitle(_i18n._traducir_texto(base) + resto)
        # Pie de pagina EOS y status
        self._refrescar_pies()
        self._lbl_info.setText(f"{_eos_nombre(self._eos_main_code())} EOS")
        # Ventana de documentacion tecnica (barra, arbol, pie)
        sw_doc = self._subventanas.get('documentacion')
        if sw_doc is not None:
            if hasattr(sw_doc._widget, 'retraducir'):
                sw_doc._widget.retraducir()
            if hasattr(sw_doc, '_pie'):
                sw_doc._pie.setText(f"  {_i18n.t('Documentación técnica')}")
            sw_doc.setWindowTitle(_i18n.t('Documentación técnica'))

    # ── Exportacion a PDF ────────────────────────────────────
    def _menu_exportar_pdf(self):
        """Genera un PDF con los resultados del calculo flash (Equilibrio
        de fases). Si no se ha ejecutado el flash, no exporta."""
        estado = self._recopilar_estado()
        res_eq = (estado.get('tabs', {})
                        .get('equilibrio', {})
                        .get('resultado'))
        if not res_eq:
            dialogos.advertencia(self,
                "No hay resultados del calculo flash para exportar.\n"
                "Ejecute el calculo en la pestaña de Equilibrio de fases.")
            return

        eos = estado.get('eos_activa', 'PR')
        base = (os.path.splitext(os.path.basename(self.current_path))[0]
                if self.current_path else f"{_i18n.t('reporte')}_{eos.lower()}")
        path, _ = QFileDialog.getSaveFileName(
            self, _i18n.t("Exportar resultados a PDF"), base + ".pdf",
            "PDF (*.pdf);;" + _i18n.t("Todos los archivos (*.*)"))
        if not path:
            return
        if not path.lower().endswith('.pdf'):
            path += '.pdf'

        self._sb.showMessage("  " + _i18n.t("Generando PDF..."), 0)
        self._pdf_worker = PdfWorker(estado, path)
        self._pdf_worker.done.connect(self._on_pdf_done)
        self._pdf_worker.start()

    def _on_pdf_done(self, ok, msg):
        self._sb.clearMessage()
        if ok:
            dialogos.info(self, msg)
        else:
            dialogos.error(self, msg)

    def _menu_asociar(self):
        try:
            import asociar_extension as rx
            ok, msg = rx.registrar()
            if ok:
                dialogos.info(self, "Asociacion registrada correctamente.")
            else:
                dialogos.advertencia(self, msg)
        except Exception as ex:
            dialogos.error(self, f"No se pudo completar la operacion:\n{ex}")

    def _menu_desasociar(self):
        try:
            import asociar_extension as rx
            ok, msg = rx.desregistrar()
            if ok:
                dialogos.info(self, "Asociacion eliminada correctamente.")
            else:
                dialogos.advertencia(self, msg)
        except Exception as ex:
            dialogos.error(self, f"No se pudo completar la operacion:\n{ex}")

    def _actualizar_titulo(self):
        """Muestra el nombre del archivo (sin extension) en el titulo."""
        if self.current_path:
            nombre = os.path.splitext(os.path.basename(self.current_path))[0]
            self.setWindowTitle(f"ThermoPhase — {nombre}")
        else:
            self.setWindowTitle("ThermoPhase")

    # ── Recopilar y aplicar estado global (todas las pestañas + globales) ──
    def _recopilar_estado(self):
        """Junta el estado completo del programa en un dict serializable."""
        import eos as _eng
        # Estados de las funcionalidades por fluido (envolvente, saturacion,
        # propiedades, equilibrio) que se hayan abierto/calculado.
        fluido_estados = {}
        for clave, sw in self._subventanas.items():
            if '@' not in clave:
                continue
            tipo, nombre = clave.split('@', 1)
            w = getattr(sw, '_widget', None)
            if w is not None and hasattr(w, 'get_estado'):
                try:
                    fluido_estados.setdefault(nombre, {})[tipo] = w.get_estado()
                except Exception:
                    pass
        return {
            'kij_user':   copy.deepcopy(kij_user),
            'kij_fuente': kij_fuente,
            'eos_activa': _eng.get_eos(),
            'fluidos':    copy.deepcopy(self.fluidos),
            'fluido_estados': fluido_estados,
            'tabs': {
                'equilibrio':  self.tab_eq.get_estado(),
                'envolvente':  self.tab_env.get_estado(),
                'saturacion':  self.tab_sat.get_estado(),
                'propiedades': self.tab_prop.get_estado(),
            },
        }

    def _aplicar_estado(self, doc):
        """Restaura el estado completo desde un dict (leído de .tpsim).
        El orden es importante: primero EOS y kij (afectan al resto),
        despues cada pestaña."""
        global kij_user, kij_fuente
        import eos as _eng
        kij_fuente = doc.get('kij_fuente', 'PR')

        # 1. EOS activa (sin disparar señal para no resetear kij_user)
        eos = doc.get('eos_activa', 'PR')
        if eos not in EOS_CODES:
            eos = 'PR'
        _eng.set_eos(eos)
        # Reflejar en el combo sin re-emitir la señal
        self.tab_eq.cmb_eos.blockSignals(True)
        self.tab_eq.cmb_eos.setCurrentIndex(_eos_idx(eos))
        self.tab_eq.cmb_eos.blockSignals(False)

        # 2. Matriz kij_user (mantiene la que el usuario habia editado)
        kij = doc.get('kij_user')
        if kij:
            try:
                kij_user = [[float(v) for v in fila] for fila in kij]
            except Exception:
                kij_user = _eng.kij_base(eos)
        # Refrescar tabla de parametros (kij + criticas)
        if hasattr(self, 'tab_par'):
            self.tab_par._sync_desde_objetivo()

        # 3. Cada pestaña restaura inputs + resultados
        tabs = doc.get('tabs', {})
        if 'equilibrio' in tabs:
            self.tab_eq.set_estado(tabs['equilibrio'])
        if 'envolvente' in tabs:
            self.tab_env.set_estado(tabs['envolvente'])
        if 'saturacion' in tabs:
            self.tab_sat.set_estado(tabs['saturacion'])
        if 'propiedades' in tabs:
            self.tab_prop.set_estado(tabs['propiedades'])

        # 3b. Fluidos guardados
        self._cerrar_ventanas_fluido()
        self.fluidos.clear()
        for f in (doc.get('fluidos') or []):
            try:
                fl = {'nombre': str(f.get('nombre', 'Fluido')),
                      'z': [float(v) for v in f.get('z', [])],
                      'eos': (f.get('eos') if f.get('eos') in EOS_CODES else 'PR'),
                      'kij_fuente': f.get('kij_fuente', f.get('eos', 'PR'))}
                kij = f.get('kij')
                fl['kij'] = ([[float(v) for v in fila] for fila in kij]
                             if kij else copy.deepcopy(KIJ_DEFAULT))
                self.fluidos.append(fl)
            except Exception:
                pass
        if hasattr(self, '_tab_fluidos'):
            self._tab_fluidos.refrescar()
        self._sync_nav_fluidos()
        # Estados de funcionalidades por fluido: se aplican al abrir cada una.
        self._fluido_estados_pend = doc.get('fluido_estados') or {}

        # 4. Label permanente del status bar
        nombre = "Soave-Redlich-Kwong" if eos == 'SRK' else "Peng-Robinson"
        self._lbl_info.setText(f"{nombre} EOS")

        # 5. Navegador

    # ── Slots del menu ─────────────────────────────────────────────
    def _menu_nuevo(self):
        """Reinicia el estado: composicion vacia, PR, kij por defecto de PR."""
        global kij_user
        import eos as _eng
        _eng.set_eos('PR')
        kij_user = copy.deepcopy(_eng.KIJ_DEFAULT_PR)
        # Reset pestañas
        self.tab_eq.set_estado({'entrada': {
            'composicion': [0.0]*NC, 'T_R': 0.0, 'P_psi': 0.0,
            'densidad': 'COSTALD', 'eos': 'Peng-Robinson', 'modo_masico': False,
        }, 'resultado': None})
        self.tab_env.set_estado({'entrada': {}, 'resultado': None})
        self.tab_sat.set_estado({'entrada': {}, 'resultado': None})
        self.tab_prop.set_estado({'entrada': {'T_R':0.0,'P_psi':0.0},'resultado':None})
        if hasattr(self, 'tab_par'):
            self.tab_par.refrescar_tabla()
        self._cerrar_ventanas_fluido()
        self.fluidos.clear()
        self._fluido_estados_pend = {}
        if hasattr(self, '_tab_fluidos'):
            self._tab_fluidos.refrescar()
        self._sync_nav_fluidos()
        self.current_path = None
        self._actualizar_titulo()
        self._lbl_info.setText("Peng-Robinson EOS")

    def _cerrar_ventanas_fluido(self):
        """Cierra y elimina las ventanas ligadas a fluidos (claves con '@')."""
        for clave in [k for k in self._subventanas if '@' in k]:
            sw = self._subventanas.pop(clave)
            try:
                sw.hide(); sw.deleteLater()
            except Exception:
                pass

    def _menu_abrir(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir simulacion ThermoPhase", "",
            "Simulaciones ThermoPhase (*.tpsim);;Todos los archivos (*.*)")
        if not path:
            return
        try:
            import simulacion as sio
            doc = sio.cargar(path)
            self._aplicar_estado(doc)
            self.current_path = path
            self._actualizar_titulo()
        except Exception as ex:
            dialogos.error(self, f"No se pudo abrir el archivo:\n\n{ex}")

    def _menu_guardar(self):
        if not self.current_path:
            return self._menu_guardar_como()
        self._guardar_a(self.current_path)

    def _menu_guardar_como(self):
        sugerido = self.current_path or "simulacion.tpsim"
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar simulacion ThermoPhase", sugerido,
            "Simulaciones ThermoPhase (*.tpsim);;Todos los archivos (*.*)")
        if not path:
            return
        if not path.lower().endswith('.tpsim'):
            path += '.tpsim'
        self._guardar_a(path)
        self.current_path = path
        self._actualizar_titulo()

    def _guardar_a(self, path):
        try:
            import simulacion as sio
            estado = self._recopilar_estado()
            sio.guardar(path, estado)
            self._sb.showMessage(
                f"  Simulacion guardada: {os.path.basename(path)}", 4000)
        except Exception as ex:
            dialogos.error(self, f"No se pudo guardar el archivo:\n\n{ex}")

    def _build(self):
        # ── Widgets de cada calculo (tamaño / colores identicos) ──
        self.tab_eq   = TabEquilibrio()
        self.tab_env  = TabEnvolvente(get_z=self._getz_main,
                                      get_kij=lambda: kij_user,
                                      get_metodo_densidad=self._metodo_densidad_main)
        self.tab_sat  = TabSaturacion(get_z=self._getz_main,
                                      get_kij=lambda: kij_user)
        self.tab_prop = TabPropiedades(get_z=self._getz_main,
                                       get_kij=lambda: kij_user)
        self.tab_par  = TabParametros()

        # Definicion de cada calculo: clave -> (widget, titulo, icono)
        self._defs_calc = {
            'equilibrio':  (self.tab_eq,   "Equilibrio de fases",                 "equilibrio"),
            'envolvente':  (self.tab_env,  "Envolvente de fases",                 "envolvente"),
            'saturacion':  (self.tab_sat,  "Puntos de saturación",                "saturacion"),
            'propiedades': (self.tab_prop, "Propiedades termodinámicas",          "propiedades"),
            'parametros':  (self.tab_par,  "Parámetros de la ecuación de estado", "parametros"),
        }
        self._subventanas = {}     # clave -> QMdiSubWindow

        # ── Barra superior de selectores globales ────────────
        self.ribbon, self.selectores = construir_ribbon()
        self._cablear_selectores()

        # ── Panel Navegador lateral ──────────────────────────
        self.nav = NavigatorPanel()
        self.nav.calculo_pedido.connect(self._abrir_calculo)
        self.nav.dato_pedido.connect(self._accion_nav)
        self.nav.fluido_calc_pedido.connect(self._abrir_calc_fluido_por_nombre)
        self.nav.componente_pedido.connect(self._abrir_componente)
        self.nav.gestor_comp_pedido.connect(self._abrir_gestor_componentes)

        # ── Area de simulacion (MDI) ─────────────────────────
        # Cada calculo se abre como una subventana con barra de titulo nativa
        # (icono + cerrar), tamaño fijo, que no puede salir del area; se
        # pueden tener varias abiertas a la vez.
        # Las ventanas de funcionalidad son ahora ventanas top-level nativas
        # de Windows (ver _Ventana), no subventanas MDI. El area central queda
        # como un panel neutro; las ventanas flotan por encima y pueden
        # moverse libremente por la pantalla.
        self.area = QWidget()
        self.area.setStyleSheet('background:#FFFFFF;')

        # Logo de ThermoPhase para el icono de cada ventana.
        _logo_path = ruta_recurso('thermophase.ico')
        self._logo = (QIcon(_logo_path) if os.path.exists(_logo_path)
                      else iconos.icono('equilibrio', 16))

        # ── Ensamblado central ───────────────────────────────
        cw = QWidget(); self.setCentralWidget(cw)
        cw.setStyleSheet('background:#D4D4D4;')
        v = QVBoxLayout(cw)
        v.setContentsMargins(0, 0, 0, 0); v.setSpacing(0)
        v.addWidget(self.ribbon)

        # Divisor gris oscuro #7F7F7F entre el navegador y el area.
        split = QSplitter(Qt.Orientation.Horizontal)
        split.setStyleSheet(
            'QSplitter { background:#D4D4D4; }'
            'QSplitter::handle { background:#7F7F7F; }')
        split.addWidget(self.nav)
        split.addWidget(self.area)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        split.setSizes([NavigatorPanel.ANCHO, 1100])
        split.setHandleWidth(2)
        v.addWidget(split, 1)

        # ── Barra de estado (plana, sutil) ───────────────────
        sb = QStatusBar()
        sb.setSizeGripEnabled(False)
        sb.setStyleSheet(
            f'QStatusBar {{ background:#D4D4D4; font-family:"{FONT_F}";'
            f' font-size:9pt; border-top:1px solid #C4C4C4; }}'
            f'QStatusBar::item {{ border:none; }}')
        def _panel(txt, ancho=None):
            l = QLabel(txt)
            if ancho:
                l.setFixedWidth(ancho)
            l.setStyleSheet(
                f'QLabel {{ background:transparent; color:{TEXT};'
                f' font-family:"{FONT_F}"; font-size:9pt; padding:1px 8px; }}')
            return l
        self._lbl_estado = _panel("Listo")
        sb.addWidget(self._lbl_estado, 1)
        self._lbl_info = _panel("Peng-Robinson EOS")
        sb.addPermanentWidget(self._lbl_info, 0)
        self.setStatusBar(sb)
        self._sb = sb

        # Cablear cambio de EOS desde el calculo de Equilibrio.
        self.tab_eq.eos_changed.connect(self._on_eos_changed)

        # Al iniciar NO se abre ninguna subventana: el area queda vacia.

    # ── Selectores globales de la barra superior ─────────────
    def _cablear_selectores(self):
        """Enlaza los tres desplegables globales con el desplegable
        correspondiente de cada ventana (en ambos sentidos)."""
        # EOS: barra -> equilibrio.cmb_eos (dispara eos_changed y propaga)
        cmb = self.selectores['eos']
        idx = self.tab_eq.cmb_eos.currentIndex()
        cmb.setCurrentIndex(idx if idx >= 0 else 0)
        cmb.currentIndexChanged.connect(
            lambda i: self.tab_eq.cmb_eos.setCurrentIndex(i))
        # Reflejar de vuelta cuando cambie en la ventana.
        self.tab_eq.cmb_eos.currentIndexChanged.connect(
            lambda i: self._sync_combo(cmb, i))

        # Densidad: barra <-> equilibrio.cmb_dens
        cmbd = self.selectores['densidad']
        idx = self.tab_eq.cmb_dens.currentIndex()
        cmbd.setCurrentIndex(idx if idx >= 0 else 0)
        cmbd.currentIndexChanged.connect(
            lambda i: self.tab_eq.cmb_dens.setCurrentIndex(i))
        self.tab_eq.cmb_dens.currentIndexChanged.connect(
            lambda i: self._sync_combo(cmbd, i))

        # ── Corrección de volumen (Peneloux) ─────────────────
        # Selector global que solo afecta a la composición principal.
        # Switch: al elegir Peneloux se fuerza la densidad a EOS y se
        # bloquea el selector de densidad (Peneloux corrige la densidad de
        # la ecuación de estado, no COSTALD); al volver a Ninguna se
        # rehabilita el selector de densidad.
        # ── Corrección de volumen (Peneloux) ─────────────────
        # La barra solo gobierna la composición principal: se sincroniza en
        # ambos sentidos con el selector cmb_vol del equilibrio principal,
        # igual que EOS y densidad.  Los fluidos usan su propio cmb_vol.
        cmbv = self.selectores.get('volumen')
        if cmbv is not None and hasattr(self.tab_eq, 'cmb_vol'):
            idx = self.tab_eq.cmb_vol.currentIndex()
            cmbv.setCurrentIndex(idx if idx >= 0 else 0)
            cmbv.currentIndexChanged.connect(
                lambda i: self.tab_eq.cmb_vol.setCurrentIndex(i))
            self.tab_eq.cmb_vol.currentIndexChanged.connect(
                lambda i: self._sync_combo(cmbv, i))
            # Cuando la barra cambia la corrección de volumen, el switch del
            # selector de densidad de la barra debe reflejar el del equilibrio.
            cmbv.currentIndexChanged.connect(self._on_correccion_volumen)

        # Envolvente: barra <-> envolvente.cmb_metodo
        cmbe = self.selectores['envolvente']
        if hasattr(self.tab_env, 'cmb_metodo'):
            idx = self.tab_env.cmb_metodo.currentIndex()
            cmbe.setCurrentIndex(idx if idx >= 0 else 0)
            cmbe.currentIndexChanged.connect(
                lambda i: self.tab_env.cmb_metodo.setCurrentIndex(i))
            self.tab_env.cmb_metodo.currentIndexChanged.connect(
                lambda i: self._sync_combo(cmbe, i))

        # ── Sistema de unidades ──────────────────────────────
        cmbu = self.selectores.get('unidades')
        if cmbu is not None:
            cmbu.currentIndexChanged.connect(self._on_unidades)
        # Boton de documentacion tecnica de la barra
        if hasattr(self.ribbon, 'btn_doc'):
            self.ribbon.btn_doc.clicked.connect(self._abrir_documentacion)

    def _on_correccion_volumen(self, idx):
        """Switch de la corrección de volumen en la barra (composición
        principal).  Mantiene el selector de densidad de la barra coherente
        con el switch: Peneloux fuerza densidad a EOS y la bloquea; Ninguna
        la rehabilita.  La sincronización del valor con el equilibrio
        principal la realiza el cableado de _cablear_selectores."""
        cmbd = self.selectores.get('densidad')
        es_peneloux = (idx == 1)
        self._correccion_volumen = 'Peneloux' if es_peneloux else 'Ninguna'
        if cmbd is not None:
            if es_peneloux:
                self._densidad_previa = cmbd.currentText()
                iEOS = cmbd.findText('EOS')
                if iEOS >= 0:
                    self._sync_combo(cmbd, iEOS)
                cmbd.setEnabled(False)
            else:
                cmbd.setEnabled(True)
                prev = getattr(self, '_densidad_previa', 'COSTALD')
                iPrev = cmbd.findText(prev)
                if iPrev >= 0:
                    self._sync_combo(cmbd, iPrev)

    def correccion_volumen_activa(self):
        """Devuelve 'Peneloux' o 'Ninguna' — corrección de volumen global
        vigente para la composición principal."""
        return getattr(self, '_correccion_volumen', 'Ninguna')

    def _on_unidades(self, idx):
        """Cambia el sistema de unidades de TODA la interfaz. El motor sigue
        en unidades internas FIELD; solo cambia la entrada y el despliegue."""
        import unidades as _u
        old = _u.sistema()
        nuevo = _u.SISTEMAS[idx] if 0 <= idx < len(_u.SISTEMAS) else 'FIELD'
        if nuevo == old:
            return
        _u.set_sistema(nuevo)
        # Reconfigurar todas las vistas de calculo: la pestaña principal de
        # equilibrio y cada subventana abierta (calculos y fluidos).
        vistas = []
        if hasattr(self, 'tab_eq'):
            vistas.append(self.tab_eq)
        for sw in self._subventanas.values():
            w = getattr(sw, '_widget', None)
            if w is not None:
                vistas.append(w)
        hechos = set()
        for w in vistas:
            if id(w) in hechos:
                continue
            hechos.add(id(w))
            if hasattr(w, 'aplicar_unidades'):
                try: w.aplicar_unidades(old)
                except Exception: pass
        self._refrescar_pies()

    @staticmethod
    def _sync_combo(cmb, i):
        """Actualiza un combo evitando reentradas de señal."""
        if cmb.currentIndex() != i and 0 <= i < cmb.count():
            cmb.blockSignals(True)
            cmb.setCurrentIndex(i)
            cmb.blockSignals(False)

    # ── EOS principal / por fluido y pies de pagina ──────────
    @staticmethod
    def _nombre_eos(code):
        return {'PR': "Peng-Robinson (HYSYS)", 'SRK': "SRK (HYSYS)",
                'PR_PVT': "Peng-Robinson (PVTsim)",
                'SRK_PVT': "SRK (PVTsim)"}.get(code, "Peng-Robinson (HYSYS)")

    def _eos_main_code(self):
        return _eos_code(self.tab_eq.cmb_eos.currentIndex())

    def _getz_main(self):
        """get_z para las ventanas NO asignadas a un fluido: fija la EOS
        principal (la de la barra / Equilibrio principal) antes de leer z."""
        _set_eos(self._eos_main_code())
        return self.tab_eq.get_z()

    def _metodo_densidad_main(self):
        """Método de densidad efectivo de la composición principal, para el
        mapa de densidad de la envolvente principal.  Refleja el selector de
        corrección de volumen (Peneloux) y el de densidad (COSTALD/EOS) del
        equilibrio principal."""
        if self.tab_eq.cmb_vol.currentText() == 'Peneloux':
            return 'Peneloux'
        return self.tab_eq.cmb_dens.currentText()

    def _refrescar_pies(self):
        """Actualiza el pie (EOS) de cada ventana abierta."""
        for w in self._subventanas.values():
            prov = getattr(w, '_eos_prov', None)
            pie = getattr(w, '_pie', None)
            if prov is not None and pie is not None:
                pie.setText(f"  {self._nombre_eos(prov())} EOS")

    # ── Gestion de ventanas de funcionalidad (top-level) ─────
    def _montar_subventana(self, clave, widget, titulo, tam=None,
                           eos_provider=None, redimensionable=False,
                           pie_texto=None):
        """Envuelve un widget en una ventana top-level nativa de Windows
        (marco del sistema) y la registra. `tam` da un tamaño propio;
        `eos_provider` agrega un pie con la EOS; `redimensionable` permite
        maximizar/redimensionar (por defecto las ventanas son de tamaño fijo)."""
        cont = QWidget()
        cont.setAutoFillBackground(True)
        cont.setStyleSheet('background:#E6E6E6;')
        lc = QVBoxLayout(cont)
        lc.setContentsMargins(0, 0, 0, 0); lc.setSpacing(0)
        lc.addWidget(widget)
        sc = QScrollArea()
        sc.setWidget(cont)
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.Shape.NoFrame)
        sc.setStyleSheet('QScrollArea { background:#E6E6E6; border:none; }')
        sc.viewport().setStyleSheet('background:#E6E6E6;')

        win = _Ventana(self)
        win.setWindowTitle(titulo)
        win.setWindowIcon(self._logo)
        lay = QVBoxLayout(win)
        lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)
        lay.addWidget(sc, 1)

        # Pie de pagina con la EOS que ocupa esta ventana.
        alto_pie = 0
        if pie_texto is not None:
            pie = QLabel(f"  {pie_texto}")
            pie.setFixedHeight(20)
            pie.setStyleSheet(
                f'QLabel {{ background:#D4D4D4; color:{TEXT};'
                f' font-family:"{FONT_F}"; font-size:9pt; padding:1px 6px;'
                f' border-top:1px solid #B4B4B4; }}')
            lay.addWidget(pie)
            win._pie = pie
            win._pie_fijo = True
            alto_pie = 20
        elif eos_provider is not None:
            pie = QLabel(f"  {self._nombre_eos(eos_provider())} EOS")
            pie.setFixedHeight(20)
            pie.setStyleSheet(
                f'QLabel {{ background:#D4D4D4; color:{TEXT};'
                f' font-family:"{FONT_F}"; font-size:9pt; padding:1px 6px;'
                f' border-top:1px solid #B4B4B4; }}')
            lay.addWidget(pie)
            win._pie = pie
            win._eos_prov = eos_provider
            alto_pie = 20

        win._clave = clave
        win._widget = widget
        # Tamaño FIJO (solo la ventana principal se puede redimensionar). Los
        # calculos comparten el tamaño de "Equilibrio de fases", un pelin mas
        # ancho que su contenido; Fluidos recibe su propio `tam`.
        if tam is None:
            if not hasattr(self, '_tam_sub'):
                h = self.tab_eq.sizeHint()
                self._tam_sub = (h.width() + 26, h.height() + 12)
            tam = self._tam_sub
        if redimensionable:
            win.resize(tam[0], tam[1] + alto_pie)
            win.setMinimumSize(480, 360)
        else:
            win.setFixedSize(tam[0], tam[1] + alto_pie)
        self._subventanas[clave] = win
        # La ventana nace en el idioma activo: si es ingles, traducir ya
        # (antes solo se traducia al alternar idioma).
        win.setProperty("_i18n_es_title", titulo)
        if _i18n.get_idioma() == 'EN':
            _i18n.retraducir(win)
            base = titulo.split(" - ")[0]; resto = titulo[len(base):]
            win.setWindowTitle(_i18n._traducir_texto(base) + resto)
            # Traducir el grafico del widget si lo soporta
            w = getattr(win, '_widget', None)
            if w is not None and hasattr(w, 'retraducir_grafico'):
                try: w.retraducir_grafico()
                except Exception: pass
        # La ventana nace en el sistema de unidades activo
        import unidades as _u
        if _u.sistema() != 'FIELD':
            w = getattr(win, '_widget', None)
            if w is not None and hasattr(w, 'aplicar_unidades'):
                try: w.aplicar_unidades('FIELD')
                except Exception: pass
        return win

    def _mostrar_subventana(self, win):
        if not win.isVisible():
            self._cascada(win)
        win.showNormal()
        win.raise_()
        win.activateWindow()

    def _tam_calculo(self, clave, widget):
        """Tamaño fijo para la ventana de cada cálculo."""
        if clave in ('parametros', 'saturacion') and hasattr(widget, 'tam_ideal'):
            return widget.tam_ideal()
        return None   # el resto usa el tamaño estandar (igual que Equilibrio)

    def _abrir_calculo(self, clave):
        """Abre (o activa) la ventana del calculo pedido."""
        if clave not in self._defs_calc:
            return
        sw = self._subventanas.get(clave)
        if sw is None:
            widget, titulo, ic = self._defs_calc[clave]
            prov = self._eos_main_code
            tam = self._tam_calculo(clave, widget)
            sw = self._montar_subventana(clave, widget, titulo, tam=tam,
                                         eos_provider=prov)
        self._mostrar_subventana(sw)

    def _abrir_gestor_componentes(self):
        """Abre (o activa) el gestor de componentes del fluido: ventana de
        dos listas (disponibles / seleccionados) para sacar y añadir
        compuestos.  Por ahora es solo la interfaz, sin efecto sobre los
        cálculos."""
        import componentes_ui as _cui
        clave = 'gestor_componentes'
        sw = self._subventanas.get(clave)
        if sw is None:
            widget = _cui.VentanaGestorComponentes(
                seleccionados=self.componentes_activos,
                on_cambio=self.aplicar_componentes_activos)
            tam = widget.tam_ideal()
            sw = self._montar_subventana(
                clave, widget, _i18n.t("Componentes del fluido"), tam=tam)
        self._mostrar_subventana(sw)

    def aplicar_componentes_activos(self, activos):
        """Aplica el conjunto de componentes activos a todas las pestañas:
        oculta las filas/columnas de los inactivos y reajusta el tamaño de
        cada subventana para que no queden huecos ni scrollbars."""
        self.componentes_activos = sorted(activos)
        if hasattr(self, 'tab_eq') and hasattr(self.tab_eq, 'aplicar_componentes_activos'):
            self.tab_eq.aplicar_componentes_activos(self.componentes_activos)
        if hasattr(self, 'tab_sat') and hasattr(self.tab_sat, 'aplicar_componentes_activos'):
            self.tab_sat.aplicar_componentes_activos(self.componentes_activos)
        if hasattr(self, 'tab_par') and hasattr(self.tab_par, 'aplicar_componentes_activos'):
            self.tab_par.aplicar_componentes_activos(self.componentes_activos)
        mapa = {'saturacion': 'tab_sat', 'parametros': 'tab_par'}
        for clave_sub, attr in mapa.items():
            sw = self._subventanas.get(clave_sub)
            widget = getattr(self, attr, None)
            if sw is not None and widget is not None:
                tam = self._tam_calculo(clave_sub, widget)
                if tam:
                    sw.setFixedSize(tam[0], tam[1] + 20)
                    widget.setFixedSize(tam[0], tam[1])

    def _abrir_componente(self, nombre):
        """Abre (o activa) la ventana de propiedades de un componente puro.
        `nombre` es el texto mostrado en el árbol (nombre completo sin ':')."""
        import componentes_ui as _cui
        # Resolver el índice del componente por su nombre mostrado
        idx = None
        for i, nom in enumerate(NOMBRES):
            if nom.rstrip(':') == nombre:
                idx = i
                break
        if idx is None:
            return
        clave = f'componente@{idx}'
        sw = self._subventanas.get(clave)
        if sw is None:
            widget = _cui.VentanaPropComponente(idx)
            titulo = NOMBRES[idx].rstrip(':')
            tam = widget.tam_ideal()
            sw = self._montar_subventana(clave, widget, titulo, tam=tam)
        self._mostrar_subventana(sw)

    def _abrir_fluidos(self):
        """Abre (o activa) el gestor de Fluidos."""
        sw = self._subventanas.get('fluidos')
        if sw is None:
            widget = TabFluidos(
                fluidos=self.fluidos,
                get_z_actual=self.tab_eq.get_z,
                cargar_en_principal=self._cargar_fluido_principal,
                abrir_calc=self._abrir_calculo_fluido,
                on_change=self._sync_nav_fluidos,
                on_comp_change=lambda f: self._sync_fluido_z(f, 'fluidos'))
            self._tab_fluidos = widget
            h = widget.sizeHint()
            sw = self._montar_subventana('fluidos', widget, "Fluidos",
                                         tam=(h.width() + 24, h.height() + 16))
        self._mostrar_subventana(sw)

    def _cargar_fluido_principal(self, z):
        """Carga la composicion de un fluido en la pestaña de Equilibrio."""
        self.tab_eq.set_z(z)
        self._abrir_calculo('equilibrio')

    def _sync_nav_fluidos(self):
        """Actualiza el arbol de fluidos del navegador. Si el idioma activo es
        ingles, retraduce el arbol para que los nombres de las funcionalidades
        del nuevo fluido salgan en ingles de inmediato."""
        if hasattr(self, 'nav'):
            self.nav.set_fluidos([f['nombre'] for f in self.fluidos])
            if _i18n.get_idioma() == 'EN':
                _i18n.retraducir(self.nav)

    def _abrir_calc_fluido_por_nombre(self, nombre, clave):
        """Abre un calculo de fluido desde el arbol del navegador."""
        for f in self.fluidos:
            if f['nombre'] == nombre:
                self._abrir_calculo_fluido(clave, f)
                return

    def _abrir_calculo_fluido(self, clave, fluido):
        """Abre un calculo ligado a un fluido concreto, en su propia ventana,
        para poder comparar varios fluidos entre si."""
        etiquetas = {
            'equilibrio':  "Equilibrio",
            'envolvente':  "Envolvente",
            'saturacion':  "Saturacion",
            'propiedades': "Propiedades",
            'parametros':  "Parametros",
        }
        if clave not in etiquetas:
            return
        fluido.setdefault('eos', 'PR')
        fluido.setdefault('kij', copy.deepcopy(KIJ_DEFAULT))
        fluido.setdefault('kij_fuente', fluido.get('eos', 'PR'))
        subclave = f"{clave}@{fluido['nombre']}"
        sw = self._subventanas.get(subclave)
        if sw is None:
            widget = self._crear_widget_fluido(clave, fluido)
            if widget is None:
                return
            # Restaurar estado guardado (al abrir un archivo) si existe.
            pend = getattr(self, '_fluido_estados_pend', {}).get(
                fluido['nombre'], {})
            if clave in pend and hasattr(widget, 'set_estado'):
                try:
                    widget.set_estado(pend[clave])
                except Exception:
                    pass
            titulo = f"{etiquetas[clave]} - {fluido['nombre']}"
            # Pie con la EOS del fluido.
            prov = (lambda f=fluido: f.get('eos', 'PR'))
            tam = self._tam_calculo(clave, widget)
            sw = self._montar_subventana(subclave, widget, titulo,
                                         tam=tam, eos_provider=prov)
        self._mostrar_subventana(sw)

    def _getz_fluido(self, fluido):
        """get_z para las ventanas de un fluido: fija la EOS del fluido antes
        de leer su composicion (asi su envolvente/saturacion la respetan)."""
        _set_eos(fluido.get('eos', 'PR'))
        return list(fluido['z'])

    def _crear_widget_fluido(self, clave, fluido):
        """Construye el widget de calculo ligado a la composicion y kij del
        fluido."""
        gz = lambda f=fluido: self._getz_fluido(f)
        gk = lambda f=fluido: f['kij']
        def gm(f=fluido):
            # Método de densidad del fluido para su mapa: lee de la ventana
            # de equilibrio del fluido si está abierta (fuente de verdad de
            # sus selectores), con Peneloux prevaleciendo sobre densidad.
            sub = self._subventanas.get(f"equilibrio@{f['nombre']}")
            w = getattr(sub, '_widget', None) if sub is not None else None
            if w is not None and hasattr(w, 'cmb_vol'):
                if w.cmb_vol.currentText() == 'Peneloux':
                    return 'Peneloux'
                return w.cmb_dens.currentText()
            return f.get('densidad', 'COSTALD')
        if clave == 'envolvente':
            return TabEnvolvente(get_z=gz, get_kij=gk, get_metodo_densidad=gm)
        if clave == 'saturacion':
            return TabSaturacion(get_z=gz, get_kij=gk)
        if clave == 'propiedades':
            return TabPropiedades(get_z=gz, get_kij=gk)
        if clave == 'parametros':
            # Parametros (kij / criticos) INDEPENDIENTES del fluido.
            return TabParametros(objetivo=fluido)
        if clave == 'equilibrio':
            # Equilibrio propio del fluido: su combo EOS define la EOS del
            # fluido y usa el kij del fluido. Su composicion queda LIGADA al
            # fluido (edicion bidireccional con el gestor de Fluidos).
            w = TabEquilibrio(kij_get=gk)
            w.set_z(fluido['z'])
            w.cmb_eos.blockSignals(True)
            w.cmb_eos.setCurrentIndex(_eos_idx(fluido.get('eos', 'PR')))
            w.cmb_eos.blockSignals(False)
            w.cmb_dens.setCurrentIndex(self.tab_eq.cmb_dens.currentIndex())
            w.eos_changed.connect(
                lambda *_a, f=fluido, ww=w: self._on_fluido_eos(f, ww))
            w.tbl_comp.itemChanged.connect(
                lambda _it, f=fluido, ww=w: self._on_eq_fluido_comp(f, ww))
            return w
        return None

    def _on_eq_fluido_comp(self, fluido, w):
        """La composicion editada en el Equilibrio del fluido pasa al fluido
        y se refleja en el gestor (y viceversa)."""
        if getattr(self, '_sync_z_lock', False):
            return
        fluido['z'] = w.get_z()
        self._sync_fluido_z(fluido, 'equilibrio')

    def _sync_fluido_z(self, fluido, origen):
        """Sincroniza la composicion del fluido entre el gestor de Fluidos y
        la ventana de Equilibrio del fluido (bidireccional, sin bucles)."""
        if getattr(self, '_sync_z_lock', False):
            return
        self._sync_z_lock = True
        try:
            if origen != 'equilibrio':
                sw = self._subventanas.get(f"equilibrio@{fluido['nombre']}")
                if sw is not None:
                    for ww in sw.findChildren(TabEquilibrio):
                        ww.set_z(fluido['z'])
            if origen != 'fluidos':
                tf = getattr(self, '_tab_fluidos', None)
                if (tf is not None and 0 <= tf._idx < len(self.fluidos)
                        and self.fluidos[tf._idx] is fluido):
                    tf._mostrar_z(fluido['z'])
        finally:
            self._sync_z_lock = False

    def _on_fluido_eos(self, fluido, w):
        """La EOS del combo de la ventana de Equilibrio del fluido pasa a ser
        la EOS del fluido; su kij y fuente se reinician al default de esa EOS
        y se refrescan los pies y la ventana de Parametros del fluido."""
        fluido['eos'] = _eos_code(w.cmb_eos.currentIndex())
        # El kij sigue a la EOS: se carga la matriz por defecto de esa EOS.
        fluido['kij_fuente'] = fluido['eos']
        fluido['kij'] = _eng.kij_base(fluido['eos'])
        par = self._subventanas.get(f"parametros@{fluido['nombre']}")
        if par is not None:
            for tp in par.findChildren(TabParametros):
                tp._sync_desde_objetivo()
        self._refrescar_pies()

    def _cascada(self, sw=None):
        """Coloca las ventanas en cascada partiendo cerca de la ventana
        principal. Si se pasa `sw`, solo posiciona esa (al abrirla)."""
        origen = self.frameGeometry().topLeft()
        x0, y0 = origen.x() + 130, origen.y() + 120
        if sw is not None:
            n = sum(1 for w in self._subventanas.values() if w.isVisible())
            off = 30 * (n % 8)
            sw.move(x0 + off, y0 + off)
            return
        i = 0
        for w in self._subventanas.values():
            if w.isVisible():
                off = 30 * (i % 8)
                w.move(x0 + off, y0 + off)
                w.raise_()
                i += 1

    def _mosaico(self):
        """Distribuye en mosaico las ventanas visibles sobre la pantalla."""
        vis = [w for w in self._subventanas.values() if w.isVisible()]
        if not vis:
            return
        scr = self.screen().availableGeometry() if self.screen() else self.geometry()
        import math
        cols = math.ceil(math.sqrt(len(vis)))
        filas = math.ceil(len(vis) / cols)
        aw = scr.width() // cols
        ah = scr.height() // filas
        for k, w in enumerate(vis):
            r, c = divmod(k, cols)
            w.showNormal()
            w.resize(max(aw - 8, 400), max(ah - 8, 320))
            w.move(scr.x() + c * aw + 4, scr.y() + r * ah + 4)
            w.raise_()

    def _cerrar_todas(self):
        """Cierra (oculta) todas las ventanas abiertas."""
        for sw in self._subventanas.values():
            sw.hide()

    def _placeholder(self, nombre):
        dialogos.info(self,
            f"La función «{nombre}» todavía no está implementada.\n"
            "(Interfaz preliminar.)")

    def _accion_nav(self, clave):
        if clave == 'fluidos':
            self._abrir_fluidos()
            return
        nombres = {'componentes': "Componentes"}
        self._placeholder(nombres.get(clave, clave))

    def _abrir_documentacion(self):
        """Abre (o trae al frente) la ventana de Documentación técnica."""
        clave = 'documentacion'
        if clave in self._subventanas:
            sw = self._subventanas[clave]
            sw.show(); sw.raise_(); sw.activateWindow()
            return
        from documentacion import DocTecnica
        widget = DocTecnica()
        self._montar_subventana(clave, widget, _i18n.t("Documentación técnica"),
                                tam=(900, 640), redimensionable=True,
                                pie_texto=_i18n.t("Documentación técnica"))

    def _menu_acerca(self):
        dialogos.info(self,
            "ThermoPhase 1.0\n\n"
            "Software de equilibrio de fases y propiedades termodinamicas "
            "para mezclas de hidrocarburos (13 componentes).\n"
            "Ecuaciones de estado: Peng-Robinson y Soave-Redlich-Kwong.")


    def _on_eos_changed(self, eos):
        """Propaga el cambio de ecuación de estado a todo el sistema:
           - Cambia la EOS activa del motor (una de las 4).
           - El kij sigue a la EOS: kij_user se recarga con la matriz por
             defecto de esa EOS (PR HYSYS, SRK HYSYS, PR PVTsim, SRK PVTsim).
           - Refresca la pestaña Parametros (kij + propiedades criticas).
           - Actualiza el status bar y los pies.
        La Envolvente/Saturacion leen kij_user y el engine usa la EOS activa,
        asi que la siguen automaticamente."""
        global kij_user, kij_fuente
        import eos as _eng
        _eng.set_eos(eos)
        kij_fuente = eos
        kij_user = _eng.kij_base(eos)
        if hasattr(self, 'tab_par'):
            self.tab_par._sync_desde_objetivo()
        self._lbl_info.setText(f"{_eos_nombre(eos)} EOS")
        self._refrescar_pies()

def main():
    """Arranca la aplicacion. Llamado desde main.py en la raiz."""
    import time as _time
    app = QApplication(sys.argv)
    # Fuente global Arial Narrow (todo el cromo retro la hereda).
    _f = QFont("Arial Narrow", 9)
    app.setFont(_f)
    # Icono global de la aplicacion
    _ico2 = ruta_recurso('thermophase.ico')
    if os.path.exists(_ico2):
        app.setWindowIcon(QIcon(_ico2))
    # Splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    _t_ini = _time.time()
    # Cargar ventana principal
    win = MainWindow()
    # Mantener el splash visible al menos 2 segundos en total
    _espera = 2.0 - (_time.time() - _t_ini)
    if _espera > 0:
        _time.sleep(_espera)
    splash.close()
    win.showMaximized()
    # Si el programa fue invocado con un .tpsim como argumento (por ejemplo
    # al hacer doble clic sobre el archivo en Windows Explorer), abrirlo
    # automaticamente despues de mostrar la ventana.
    _archivo_cli = None
    for _arg in sys.argv[1:]:
        if _arg.lower().endswith('.tpsim') and os.path.exists(_arg):
            _archivo_cli = _arg
            break
    if _archivo_cli:
        try:
            import simulacion as _sio
            _doc = _sio.cargar(_archivo_cli)
            win._aplicar_estado(_doc)
            win.current_path = _archivo_cli
            win._actualizar_titulo()
        except Exception as _ex:
            import dialogos as _dlg
            _dlg.error(win, f"No se pudo abrir el archivo pasado como argumento:\n\n{_ex}")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

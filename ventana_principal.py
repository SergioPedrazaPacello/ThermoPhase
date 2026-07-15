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
    QAbstractSpinBox, QMenuBar, QFileDialog
)
import matplotlib
matplotlib.use('QtAgg')
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QFont, QIcon, QAction, QKeySequence

from eos import (
    COMPONENTES, NOMBRES, PM, TC, PC, OMEGA, KIJ_DEFAULT, NC,
    calcular, R_GAS
)
from pestana_envolvente import TabEnvolvente
from pestana_saturacion import TabSaturacion
from pestana_propiedades import TabPropiedades
import dialogos as dialogos
from rutas import ruta_recurso
kij_user = copy.deepcopy(KIJ_DEFAULT)

# ── Paleta ────────────────────────────────────────────────────
WHITE    = "#FFFFFF"
GRAY_TIT = "#A8A8A8"   # plomo oscuro para títulos / cabeceras
GRAY_LBL = "#D0D0D0"   # plomo medio para encabezados de tabla y barras
GRAY_CEL = "#D0D0D0"   # celdas de etiqueta (por ahora, igual al encabezado)
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
    f' color:{TEXT}; selection-background-color:#000080; selection-color:#FFFFFF;'
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
    """Tabla sin cabeceras, sin scroll, tamaño fijo.

    Grilla interna DESACTIVADA: solo se dibuja el borde externo de la
    tabla (el 'border' del QTableWidget). Las lineas entre celdas se
    quitan con setShowGrid(False).

    IMPORTANTE: no estilizar 'QTableWidget::item' con border/background en
    la hoja de estilos. En cuanto se hace, Qt deja de respetar el
    setBackground() de cada QTableWidgetItem y pinta todas las celdas de
    blanco. El color de fondo por celda se controla SOLO desde
    cell(..., bg=...).
    """
    t = QTableWidget(rows, cols)
    t.horizontalHeader().hide()
    t.verticalHeader().hide()
    t.setShowGrid(False)                       # sin grilla interna
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setStyleSheet(
        f'QTableWidget {{ border:1px solid {BORDER}; '
        f'font-family:"{FONT_F}"; font-size:{FS}pt; }}'
        f'QTableWidget::item {{ padding:2px 6px; }}'
    )
    for r in range(rows):
        t.setRowHeight(r, row_h)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return t

def fix_table_size(t):
    """Ajusta el tamaño de la tabla a su contenido.

    Se suman 4 px (no 2) por dimension: 2 px del marco de la tabla
    (border:1px a cada lado) MAS 2 px para que la ultima linea de la
    grilla —la del borde derecho de la ultima columna y la del borde
    inferior de la ultima fila— tenga espacio y no quede recortada.
    Sin esos 2 px extra, las celdas del borde se ven "sin margen".
    """
    w = sum(t.columnWidth(c) for c in range(t.columnCount())) + 4
    h = sum(t.rowHeight(r) for r in range(t.rowCount())) + 4
    t.setFixedSize(w, h)

# ── Dimensiones ──────────────────────────────────────────────
W_LBL  = 255   # columna de etiqueta
W_VAL  = 140   # columna de valor (Vapor o Líquido)
W_COMP = 290   # columna nombre de componente
ROW_H  = 22

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

    def __init__(self):
        super().__init__()
        self.worker      = None
        self.last_result = None
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

        gl.addWidget(inp_lbl("Presion (psi):"), 0, 0)
        self.sp_P = QDoubleSpinBox()
        self.sp_P.setRange(0,15000); self.sp_P.setDecimals(2)
        self.sp_P.setSpecialValueText(" "); self.sp_P.setValue(0)
        self.sp_P.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_P.setFixedHeight(22); self.sp_P.setFixedWidth(110)
        self.sp_P.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gl.addWidget(self.sp_P, 0, 1)

        gl.addWidget(inp_lbl("Temperatura (°R):"), 1, 0)
        self.sp_T = QDoubleSpinBox()
        self.sp_T.setRange(0.0, 9999.99)
        self.sp_T.setDecimals(2)
        self.sp_T.setSpecialValueText(" "); self.sp_T.setValue(0)
        self.sp_T.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_T.setFixedHeight(22); self.sp_T.setFixedWidth(110)
        gl.addWidget(self.sp_T, 1, 1)

        gl.addWidget(inp_lbl("Temperatura (°F):"), 2, 0)
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

        def _on_T_changed(v):
            if self._sync_lock: return
            self._sync_lock = True
            if v <= 0:
                self.sp_F.setValue(-459.67)   # vacío
            else:
                self.sp_F.setValue(v - 459.67)
            _style_T(True); _style_F(False)
            self._sync_lock = False
        def _on_F_changed(v):
            if self._sync_lock: return
            self._sync_lock = True
            if v <= -459.67:
                self.sp_T.setValue(0)         # vacío
            else:
                self.sp_T.setValue(v + 459.67)
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

        # Fila de botones
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)

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

        # Fila selector densidad — etiqueta igual a inp_lbl + combobox, alineados a derecha
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
        rp.addLayout(dens_row)

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
        self.cmb_eos.addItems(["Peng-Robinson", "SRK"])
        self.cmb_eos.setFixedHeight(22); self.cmb_eos.setFixedWidth(110)
        _aplicar_estilo_combo(self.cmb_eos)
        # Emitir señal cuando el usuario cambia la EOS
        self.cmb_eos.currentIndexChanged.connect(self._on_eos_changed)
        eos_row.addWidget(self.cmb_eos, alignment=Qt.AlignmentFlag.AlignVCenter)
        rp.addLayout(eos_row)

        rp.addStretch(2)   # equilibra el bloque hacia el centro

        top.addLayout(rp)
        root.addLayout(top)

        # ── TÍTULO principal ──────────────────────────────────
        root.addWidget(title_label("ThermoPhase — Equilibrio de Fases"))

        # ── HELPER LOCAL: frame con borde que envuelve tablas ─
        # Cada "grupo" (columna de datos) = QFrame con border + VBox de tablas sin border.
        # Los QTableWidget internos tienen border:none para que el frame sea el unico borde.
        # Asi se logra borde externo por columna sin grilla interna.
        def _tbl_sin_borde(rows, col_w, row_h=ROW_H):
            t = QTableWidget(rows, 1)
            t.horizontalHeader().hide(); t.verticalHeader().hide()
            t.setShowGrid(False)
            t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            t.setColumnWidth(0, col_w)
            t.setFixedWidth(col_w)
            for r in range(rows): t.setRowHeight(r, row_h)
            t.setFixedHeight(rows * row_h)
            t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            t.setStyleSheet(
                f'QTableWidget {{ border:none; '
                f'font-family:"{FONT_F}"; font-size:{FS}pt; }}'
                f'QTableWidget::item {{ padding:2px 6px; }}')
            return t

        def _frame_col(col_w, total_rows):
            """Frame con borde gris que contiene N filas de tablas."""
            fr = QFrame()
            fr.setStyleSheet(f'QFrame {{ border:1px solid {BORDER}; }}')
            fr.setFixedWidth(col_w + 2)
            lay = QVBoxLayout(fr)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(0)
            return fr, lay

        # ── BLOQUE RESUMEN ────────────────────────────────────
        root.addWidget(section_label("Resumen de los calculos:", left=True))

        # Anchos de columna identicos a antes
        W0 = W_COMP   # 290 etiquetas
        W1 = W_VAL    # 140 Mezcla
        W2 = W_VAL    # 140 Fase Vapor
        W3 = W_VAL    # 140 Fase Liquida

        # Filas: 1 hdr + 6 datos = 7 por grupo
        HDR_ROWS_R = 1
        DAT_ROWS_R = 6

        # Grupo 0 — etiquetas
        fr0_r, lay0_r = _frame_col(W0, HDR_ROWS_R + DAT_ROWS_R)
        hdr_r0 = _tbl_sin_borde(HDR_ROWS_R, W0)
        hdr_r0.setItem(0, 0, cell("", bg=GRAY_LBL))
        lay0_r.addWidget(hdr_r0)
        # tabla de datos col0 (etiquetas)
        self.tbl_res = QTableWidget(DAT_ROWS_R, 4)   # conservamos como objeto de 4 col
        # NOTA: se mantiene como QTableWidget de 4 columnas internamente para que
        # todo el codigo de _render() funcione sin cambios. Lo que cambia es que
        # VISUALMENTE solo mostramos la col 0 aqui; las otras 3 estan en sus frames.
        # ALTERNATIVA mas simple: usamos 4 tablas de 1 col y las referenciamos.
        # Por claridad y para NO tocar _render(), usamos tablas de 1 col separadas
        # y creamos alias self.tbl_res como objeto contenedor de celdas.
        # Reemplazamos por el enfoque de 4 sub-tablas con un objeto proxy:
        lay0_r.addWidget(_tbl_sin_borde(0, W0))  # placeholder
        fr0_r.setFixedHeight((HDR_ROWS_R + DAT_ROWS_R) * ROW_H + 2)

        # --- Enfoque definitivo: 4 sub-tablas de 1 columna, alias en self ---
        # Eliminar lo anterior y rehacer limpio:
        del hdr_r0, lay0_r, fr0_r

        res_labels = [
            "Fase fraccion [molar]:",
            "Fase fraccion [masica]:",
            "Gravedad especifica:",
            "Densidad masica [lb/ft3]:",
            "Factor de compresibilidad:",
            "Peso molecular:",
        ]
        self.res_has_mix = {3, 5}

        # Cada grupo: 1 fila hdr + 6 filas datos = 7 filas
        R_TOTAL = 1 + DAT_ROWS_R

        def _grupo_res(col_w, hdr_txt, hdr_bg=GRAY_LBL):
            fr, lay = _frame_col(col_w, R_TOTAL)
            t = _tbl_sin_borde(R_TOTAL, col_w)
            t.setItem(0, 0, cell(hdr_txt, bg=hdr_bg,
                                 align=Qt.AlignmentFlag.AlignCenter))
            fr.setFixedHeight(R_TOTAL * ROW_H + 2)
            lay.addWidget(t)
            return fr, t

        fr_r0, t_r0 = _grupo_res(W0, "")
        fr_r1, t_r1 = _grupo_res(W1, "Mezcla")
        fr_r2, t_r2 = _grupo_res(W2, "Fase Vapor")
        fr_r3, t_r3 = _grupo_res(W3, "Fase Liquida")

        # Rellenar filas de datos
        for i, lbl in enumerate(res_labels):
            r = i + 1  # fila 0 = hdr
            t_r0.setItem(r, 0, cell(lbl, bg=GRAY_CEL,
                align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
            t_r1.setItem(r, 0, cell("", bg=GRAY_RES))
            t_r2.setItem(r, 0, cell("", bg=GRAY_RES))
            t_r3.setItem(r, 0, cell("", bg=GRAY_RES))

        # Objeto proxy self.tbl_res: QTableWidget de 4 cols para compatibilidad
        # con _render(). Las sub-tablas son los objetos reales de display.
        self.tbl_res   = None   # se asigna abajo como objeto de acceso
        self._tr0, self._tr1, self._tr2, self._tr3 = t_r0, t_r1, t_r2, t_r3
        self._tr_offset = 1    # offset de fila (fila 0 = hdr)

        hbox_res = QHBoxLayout()
        hbox_res.setSpacing(3)
        hbox_res.setContentsMargins(0, 0, 0, 0)
        for fr in (fr_r0, fr_r1, fr_r2, fr_r3):
            hbox_res.addWidget(fr)
        hbox_res.addStretch()
        root.addLayout(hbox_res)

        # ── BLOQUE COMPOSICIÓN ────────────────────────────────
        root.addWidget(section_label("Composicion de las fases:", left=True))

        # Cada grupo: 2 filas hdr + (NC+1) filas datos
        HDR_ROWS_C = 2
        DAT_ROWS_C = NC + 1
        C_TOTAL    = HDR_ROWS_C + DAT_ROWS_C

        def _grupo_comp(col_w, hdr0, hdr1, hdr1_ref=None):
            fr, lay = _frame_col(col_w, C_TOTAL)
            t = _tbl_sin_borde(C_TOTAL, col_w)
            t.setRowHeight(0, ROW_H); t.setRowHeight(1, ROW_H)
            it0 = cell(hdr0, bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter)
            it1 = cell(hdr1, bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter)
            t.setItem(0, 0, it0)
            t.setItem(1, 0, it1)
            fr.setFixedHeight(C_TOTAL * ROW_H + 2)
            lay.addWidget(t)
            return fr, t, it1

        fr_c0, t_c0, _     = _grupo_comp(W0, "Componente",          "")
        fr_c1, t_c1, hdr1_c1 = _grupo_comp(W1, "Composicion General", "Fraccion Molar")
        fr_c2, t_c2, hdr1_c2 = _grupo_comp(W2, "Fase Vapor",          "Fraccion molar")
        fr_c3, t_c3, hdr1_c3 = _grupo_comp(W3, "Fase Liquida",        "Fraccion molar")

        # Guardamos refs a las celdas de sub-encabezado (para modo masico)
        self.hdr_comp_gen = hdr1_c1
        self.hdr_comp_vap = hdr1_c2
        self.hdr_comp_liq = hdr1_c3

        # Rellenar filas de componentes
        for i in range(NC):
            r = HDR_ROWS_C + i
            t_c0.setItem(r, 0, cell(
                NOMBRES[i], bg=GRAY_CEL,
                align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
            t_c1.setItem(r, 0, cell("", bg=WHITE, editable=True))
            t_c2.setItem(r, 0, cell("", bg=GRAY_RES, color=TEXT_RES))
            t_c3.setItem(r, 0, cell("", bg=GRAY_RES, color=TEXT_RES))

        # Fila sumatorias (ultima fila = HDR_ROWS_C + NC)
        r_sum = HDR_ROWS_C + NC
        t_c0.setItem(r_sum, 0, cell("Sumatorias:", bg=GRAY_CEL,
            align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
        t_c1.setItem(r_sum, 0, cell("", bg=WHITE))
        t_c2.setItem(r_sum, 0, cell("", bg=GRAY_RES))
        t_c3.setItem(r_sum, 0, cell("", bg=GRAY_RES))

        self.sum_row   = r_sum        # fila sumatoria en las sub-tablas de comp
        self._tc0, self._tc1, self._tc2, self._tc3 = t_c0, t_c1, t_c2, t_c3
        self._tc_offset = HDR_ROWS_C  # offset: filas 0,1 = hdrs

        # self.tbl_comp sigue siendo el objeto de edicion de composicion:
        # para eso apuntamos la tabla de composicion general (col1)
        self.tbl_comp = t_c1
        self.tbl_comp.itemChanged.connect(self._on_item_changed)

        hbox_comp = QHBoxLayout()
        hbox_comp.setSpacing(3)
        hbox_comp.setContentsMargins(0, 0, 0, 0)
        for fr in (fr_c0, fr_c1, fr_c2, fr_c3):
            hbox_comp.addWidget(fr)
        hbox_comp.addStretch()
        root.addLayout(hbox_comp)



        hc.addWidget(box)
        hc.addStretch()
        outer.addLayout(hc)

    # ── Helpers de entrada ───────────────────────────────────
    def get_T(self):
        """Lee la temperatura del QDoubleSpinBox."""
        return self.sp_T.value()

    def get_P(self):
        """Lee la presión del QLineEdit de forma segura."""
        try:
            val = float(self.sp_P.text().replace(',', '.'))
            return val if val > 0 else 200.0
        except ValueError:
            return 200.0

    # ── Handlers ─────────────────────────────────────────────
    def _on_eos_changed(self, idx):
        """Emite la señal para que MainWindow propague el cambio de EOS."""
        eos = 'SRK' if idx == 1 else 'PR'
        self.eos_changed.emit(eos)

    # ── Guardar / restaurar estado (usado por Archivo > Guardar/Abrir) ──
    def get_estado(self):
        """Devuelve dict con inputs y resultado calculado (si existe)."""
        # Leemos los valores crudos de los spinboxes (sp_T ya esta en °R,
        # sp_P en psi). NO usamos get_T/get_P que tienen fallbacks de 200.
        return {
            'entrada': {
                'composicion': self.get_z(),
                'T_R':         float(self.sp_T.value()),
                'P_psi':       float(self.sp_P.value()),
                'densidad':    self.cmb_dens.currentText(),
                'eos':         self.cmb_eos.currentText(),
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
            self.tbl_comp.item(i+self._tc_offset, 0).setText(f"{z[i] if i<len(z) else 0.0:.4f}")
        self.tbl_comp.blockSignals(False)
        self._upd_suma()
        # T (en °R directo, el sp_T ya esta en °R). Al setear sp_T, el
        # slot _on_T_changed sincroniza automaticamente sp_F.
        T = float(e.get('T_R', 0.0) or 0.0)
        self.sp_T.setValue(T if T > 0 else 0)
        # P (psi directo)
        P = float(e.get('P_psi', 0.0) or 0.0)
        self.sp_P.setValue(P if P > 0 else 0)
        # Densidad
        d = e.get('densidad', 'COSTALD')
        idx = self.cmb_dens.findText(d)
        if idx >= 0:
            self.cmb_dens.setCurrentIndex(idx)
        # EOS (silencioso — MainWindow ya la habra aplicado antes)
        eos_txt = e.get('eos', 'Peng-Robinson')
        idx = self.cmb_eos.findText(eos_txt)
        if idx >= 0:
            self.cmb_eos.blockSignals(True)
            self.cmb_eos.setCurrentIndex(idx)
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

    def get_z(self):
        z = []
        for i in range(NC):
            try: z.append(float(self.tbl_comp.item(i+self._tc_offset,0).text()))
            except: z.append(0.0)
        return z

    def _upd_suma(self):
        s = sum(self.get_z())
        self.tbl_comp.blockSignals(True)
        self.tbl_comp.item(self.sum_row,0).setText(f"{s:.4f}")
        self.tbl_comp.blockSignals(False)

    def normalizar(self):
        z = self.get_z(); s = sum(z)
        if s <= 0: return
        self.tbl_comp.blockSignals(True)
        for i in range(NC):
            self.tbl_comp.item(i+self._tc_offset,0).setText(f"{z[i]/s:.4f}")
        self.tbl_comp.blockSignals(False)
        self._upd_suma()  # actualiza fila sumatorias

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
        self.btn.setEnabled(False); self.btn.setText("Calculando...")
        self.worker = Worker(z, self.get_T(), self.get_P(), kij_user,
                             metodo_densidad=self.cmb_dens.currentText())
        self.worker.done.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_error(self, msg):
        self.btn.setEnabled(True); self.btn.setText("Realizar Calculo")
        dialogos.error(self, msg)

    def _on_result(self, r):
        self.btn.setEnabled(True); self.btn.setText("Realizar Calculo")
        self.last_result = r
        self._render(r)

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

        # Resumen — 6 filas × 3 cols (etiqueta, vapor, liquida)
        # col 0 = etiqueta (plomo siempre)
        # col 1 = Fase Vapor  → blanco si tiene valor
        # col 2 = Fase Liquida→ blanco si tiene valor
        #
        # Filas dens (3) y PM (5) también usan col0 para valor de mezcla
        data = [None]*6
        if modo == "liquido_unico":
            data[0] = ("", f(V) if V>0 else "", f(L) if L>0 else "")
            data[1] = ("", f(Vm) if V>0 else "", f(Lm) if L>0 else "")
            data[2] = ("", "", f(sg_l))
            data[3] = (f(rho_z), "", f(rho_l))
            data[4] = ("", "", f(ZL))
            data[5] = (f(PM_z), "", f(PM_l))
        elif modo == "vapor_unico":
            data[0] = ("", f(V) if V>0 else "", "")
            data[1] = ("", f(Vm) if V>0 else "", "")
            data[2] = ("", f(sg_v), "")
            data[3] = (f(rho_z), f(rho_v), "")
            data[4] = ("", f(ZV), "")
            data[5] = (f(PM_z), f(PM_v), "")
        else:
            data[0] = ("", f(V), f(L))
            data[1] = ("", f(Vm), f(Lm))
            data[2] = ("", f(sg_v), f(sg_l))
            data[3] = (f(rho_z), f(rho_v), f(rho_l))
            data[4] = ("", f(ZV), f(ZL))
            data[5] = (f(PM_z), f(PM_v), f(PM_l))

        for i, (mix, vap, liq) in enumerate(data):
            # col0=etiqueta (plomo fijo), col1=mezcla, col2=vapor, col3=liquida
            if i in self.res_has_mix:
                paint(self._tr1.item(i+self._tr_offset,0), mix)
            else:
                self._tr1.item(i+self._tr_offset,0).setText("")
                self._tr1.item(i+self._tr_offset,0).setBackground(_brush(GRAY_RES))
            paint(self._tr2.item(i+self._tr_offset,0), vap)
            paint(self._tr3.item(i+self._tr_offset,0), liq)

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
            it2 = self._tc2.item(i+self._tc_offset,0)
            it3 = self._tc3.item(i+self._tc_offset,0)
            it2.setText(tv); it2.setBackground(_brush(WHITE if tv else GRAY_RES))
            it3.setText(tl); it3.setBackground(_brush(WHITE if tl else GRAY_RES))
        self.tbl_comp.blockSignals(False)

        ts2 = f"{sy:.4f}" if V>0 else ""
        ts3 = f"{sx:.4f}" if L>0 else ""
        self._tc2.item(self.sum_row,0).setText(ts2)
        self._tc3.item(self.sum_row,0).setText(ts3)
        self._tc2.item(self.sum_row,0).setBackground(_brush(WHITE if ts2 else GRAY_RES))
        self._tc3.item(self.sum_row,0).setBackground(_brush(WHITE if ts3 else GRAY_RES))


# ══════════════════════════════════════════════════════════════
# Tab 2 — Parámetros EOS
# ══════════════════════════════════════════════════════════════
class TabParametros(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(4,4,4,4)
        outer.setSpacing(3)
        self.setStyleSheet(f'background:{GRAY_LBL};')

        WP = [200,160,150,145,165]
        WK = 65

        # ─── Tabla propiedades críticas (título+cabecera+datos en una sola tabla) ─
        outer.addWidget(title_label("Propiedades criticas y factor acentrico"))

        self.tbl_p = QTableWidget(NC+1, 5)  # fila 0=cabecera, filas 1..NC=datos
        self.tbl_p.horizontalHeader().hide()
        self.tbl_p.verticalHeader().hide()
        self.tbl_p.setShowGrid(False)
        self.tbl_p.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_p.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;}}'
            f'QTableWidget::item {{ padding:2px 6px; }}')
        for c,w in enumerate(WP): self.tbl_p.setColumnWidth(c,w)
        for r in range(NC+1): self.tbl_p.setRowHeight(r, ROW_H)

        # Fila 0: cabecera (se desplaza con scroll)
        for c,h in enumerate(["Componente","Temperatura Critica (°R)",
                               "Presion Critica (psi)","Factor acentrico",
                               "Peso Molecular (lb/lb-mol)"]):
            self.tbl_p.setItem(0,c, cell(h, bg=GRAY_LBL,
                align=Qt.AlignmentFlag.AlignCenter))

        # Filas 1..NC: datos
        for i in range(NC):
            r = i+1
            self.tbl_p.setItem(r,0, cell(NOMBRES[i], bg=GRAY_LBL,
                align=Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
            for c,v in enumerate([f"{TC[i]:.4f}",f"{PC[i]:.4f}",
                                   f"{OMEGA[i]:.8f}",f"{PM[i]}"]):
                self.tbl_p.setItem(r,c+1, cell(v, bg=WHITE, color=TEXT_RES))

        self.tbl_p.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_p.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_p.setFixedHeight(309)
        outer.addWidget(self.tbl_p)  # altura fija 310px

        # ─── Tabla kij (cabecera+datos en una sola tabla) ─────
        outer.addWidget(title_label("Coeficientes de interaccion binaria"))

        self.tbl_k = QTableWidget(NC+1, NC+1)  # fila 0=cabecera
        self.tbl_k.horizontalHeader().hide()
        self.tbl_k.verticalHeader().hide()
        self.tbl_k.setShowGrid(False)
        self.tbl_k.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;}}'
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
                v = kij_user[i][j]
                if i == j:
                    it = cell(f"{v:.5f}", bg=GRAY_LBL,
                        color=TEXT_DIM, align=Qt.AlignmentFlag.AlignCenter)
                    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    it = cell(f"{v:.5f}", bg=WHITE, color=TEXT_RES,
                        align=Qt.AlignmentFlag.AlignCenter, editable=True)
                self.tbl_k.setItem(r,j+1, it)

        self.tbl_k.itemChanged.connect(self._on_kij)
        self.tbl_k.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_k.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tbl_k.setFixedHeight(310)
        outer.addWidget(self.tbl_k)  # altura fija 316px

        bot = QHBoxLayout()
        note = QLabel("Doble clic para editar un coeficiente "
                      "(la celda simetrica se actualiza automaticamente)")
        note.setStyleSheet(
            f'color:{TEXT_DIM};font-size:9pt;font-family:"{FONT_F}";'
            f'background:transparent;')
        bot.addWidget(note)
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
            kij_user[i][j] = v
            kij_user[j][i] = v
            self.tbl_k.blockSignals(True)
            sym = self.tbl_k.item(j+1, i+1)  # +1 por fila de cabecera
            if sym: sym.setText(f"{v:.5f}")
            item.setBackground(_brush(WHITE))
            item.setForeground(_brush(TEXT_RES))
            self.tbl_k.blockSignals(False)
        except: pass

    def refrescar_tabla(self):
        """Refresca la tabla visible desde la variable global kij_user
        (sin diálogo). La usa MainWindow cuando cambia la EOS activa."""
        self.tbl_k.blockSignals(True)
        for i in range(NC):
            for j in range(NC):
                it = self.tbl_k.item(i+1, j+1)  # +1 por fila de cabecera
                if it and i != j:
                    it.setText(f"{kij_user[i][j]:.5f}")
        self.tbl_k.blockSignals(False)

    def _reset(self):
        # Restaura al default de la EOS activa (PR o SRK).
        global kij_user
        import eos as _eng
        base = _eng.KIJ_DEFAULT_SRK if _eng.get_eos() == 'SRK' else _eng.KIJ_DEFAULT_PR
        kij_user = copy.deepcopy(base)
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
                       "Calculadora de Equilibrio de Fases")
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ThermoPhase")
        TW = W_COMP + 3*W_VAL + 30   # ancho total + márgenes
        TH = 830                      # +25 para acomodar la barra de menu
        self.setFixedSize(TW, TH)
        self.current_path = None        # ruta del .tpsim actual (None = sin guardar)
        self._build()
        self._construir_menu()
        self._actualizar_titulo()

    def _construir_menu(self):
        """Barra de menu superior con acciones de archivo. Estilo Win95
        para armonizar con el resto de la aplicacion."""
        menubar = self.menuBar()
        menubar.setStyleSheet(
            f'QMenuBar {{ background:{GRAY_LBL}; '
            f'  font-family:"{FONT_F}"; font-size:{FS}pt; '
            f'  border-bottom:1px solid {BORDER}; }} '
            f'QMenuBar::item {{ padding:3px 10px; background:transparent; }} '
            f'QMenuBar::item:selected {{ background:#000080; color:#FFFFFF; }} '
            f'QMenu {{ background:{WHITE}; color:{TEXT}; '
            f'  border:1px solid {BORDER}; '
            f'  font-family:"{FONT_F}"; font-size:{FS}pt; }} '
            f'QMenu::item {{ padding:3px 22px 3px 20px; }} '
            f'QMenu::item:selected {{ background:#000080; color:#FFFFFF; }} '
            f'QMenu::separator {{ height:1px; background:{BORDER}; '
            f'  margin:2px 4px; }}')

        m_arch = menubar.addMenu("&Archivo")

        act_new = QAction("&Nuevo", self)
        act_new.setShortcut(QKeySequence.StandardKey.New)
        act_new.triggered.connect(self._menu_nuevo)
        m_arch.addAction(act_new)

        act_open = QAction("&Abrir...", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self._menu_abrir)
        m_arch.addAction(act_open)

        m_arch.addSeparator()

        act_save = QAction("&Guardar", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self._menu_guardar)
        m_arch.addAction(act_save)

        act_save_as = QAction("Guardar &como...", self)
        act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        act_save_as.triggered.connect(self._menu_guardar_como)
        m_arch.addAction(act_save_as)

        m_arch.addSeparator()

        act_exit = QAction("&Salir", self)
        act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)
        m_arch.addAction(act_exit)

        # ── Menu Herramientas ────────────────────────────────
        m_herr = menubar.addMenu("&Herramientas")

        act_reg = QAction("&Asociar archivos .tpsim con este programa", self)
        act_reg.triggered.connect(self._menu_asociar)
        m_herr.addAction(act_reg)

        act_desr = QAction("&Quitar asociacion de archivos .tpsim", self)
        act_desr.triggered.connect(self._menu_desasociar)
        m_herr.addAction(act_desr)

        # ── Menu Exportar ────────────────────────────────────
        m_exp = menubar.addMenu("&Exportar")

        act_pdf = QAction("Exportar resultados a &PDF", self)
        act_pdf.triggered.connect(self._menu_exportar_pdf)
        m_exp.addAction(act_pdf)

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
                if self.current_path else f"reporte_{eos.lower()}")
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar resultados a PDF", base + ".pdf",
            "PDF (*.pdf);;Todos los archivos (*.*)")
        if not path:
            return
        if not path.lower().endswith('.pdf'):
            path += '.pdf'

        self._sb.showMessage("  Generando PDF...", 0)
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
        return {
            'kij_user':   copy.deepcopy(kij_user),
            'eos_activa': _eng.get_eos(),
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
        global kij_user
        import eos as _eng

        # 1. EOS activa (sin disparar señal para no resetear kij_user)
        eos = doc.get('eos_activa', 'PR')
        _eng.set_eos(eos)
        # Reflejar en el combo sin re-emitir la señal
        idx = 1 if eos == 'SRK' else 0
        self.tab_eq.cmb_eos.blockSignals(True)
        self.tab_eq.cmb_eos.setCurrentIndex(idx)
        self.tab_eq.cmb_eos.blockSignals(False)

        # 2. Matriz kij_user (mantiene la que el usuario habia editado)
        kij = doc.get('kij_user')
        if kij:
            try:
                kij_user = [[float(v) for v in fila] for fila in kij]
            except Exception:
                base = _eng.KIJ_DEFAULT_SRK if eos == 'SRK' else _eng.KIJ_DEFAULT_PR
                kij_user = copy.deepcopy(base)
        # Refrescar tabla de parametros
        if hasattr(self, 'tab_par'):
            self.tab_par.refrescar_tabla()

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

        # 4. Label permanente del status bar
        nombre = "Soave-Redlich-Kwong" if eos == 'SRK' else "Peng-Robinson"
        self._lbl_info.setText(
            f"  {nombre} EOS  |  "
            f"R = {R_GAS} psi·ft³/(lb-mol·°R)  |  13 componentes")

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
        self.current_path = None
        self._actualizar_titulo()
        self._lbl_info.setText(
            f"  Peng-Robinson EOS  |  "
            f"R = {R_GAS} psi·ft³/(lb-mol·°R)  |  13 componentes")

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
        cw = QWidget(); self.setCentralWidget(cw)
        lay = QVBoxLayout(cw)
        lay.setContentsMargins(4,4,4,2); lay.setSpacing(2)

        tabs = QTabWidget()
        # Reemplaza la barra por defecto con una que hace scroll al hacer
        # clic en pestañas cortadas y responde a la rueda del mouse.
        tabs.setTabBar(ScrollableTabBar())
        # Se mantiene el mecanismo interno de scroll (necesario para que
        # setCurrentIndex desplace la barra) pero se ocultan las flechas
        # con QSS (QToolButton width:0).
        tabs.setUsesScrollButtons(True)
        tabs.tabBar().setUsesScrollButtons(True)
        tabs.setStyleSheet(
            f'QTabWidget::pane {{border:1px solid {BORDER};}}'
            f'QTabBar::tab {{background:{GRAY_LBL};color:{TEXT};'
            f'padding:4px 14px;border:1px solid {BORDER};border-bottom:none;'
            f'margin-right:1px;font-family:"{FONT_F}";font-size:{FS}pt;}}'
            f'QTabBar::tab:selected {{background:{WHITE};'
            f'border-bottom:1px solid {WHITE};}}'
            f'QTabBar::scroller {{width:0px;}}'
            f'QTabBar QToolButton {{width:0px;height:0px;padding:0px;'
            f'margin:0px;border:none;image:none;}}'
        )
        self.tab_eq  = TabEquilibrio()
        self.tab_env = TabEnvolvente(
            get_z=self.tab_eq.get_z,
            get_kij=lambda: kij_user
        )
        self.tab_sat = TabSaturacion(
            get_z=self.tab_eq.get_z,
            get_kij=lambda: kij_user
        )
        self.tab_prop = TabPropiedades(
            get_z=self.tab_eq.get_z,
            get_kij=lambda: kij_user
        )
        self.tab_par = TabParametros()
        tabs.addTab(self.tab_eq,   "Equilibrio de fases")
        tabs.addTab(self.tab_env,  "Envolvente de fases")
        tabs.addTab(self.tab_sat,  "Puntos de saturacion")
        tabs.addTab(self.tab_prop, "Propiedades termodinamicas")
        tabs.addTab(self.tab_par,  "Parametros de la ecuacion de estado")
        lay.addWidget(tabs)

        sb = QStatusBar()
        sb.setStyleSheet(
            f'background:{GRAY_LBL};font-family:"{FONT_F}";font-size:9pt;'
            f'border-top:1px solid {BORDER};'
            f'QStatusBar::item {{ border:none; }}')
        # Widget permanente para el mensaje de EOS/R/componentes. Se usa
        # addPermanentWidget (no addWidget) para que NO se oculte cuando
        # Qt muestra los tooltips temporales del hover del menu Archivo.
        self._lbl_info = QLabel(
            f"  Peng-Robinson EOS  |  "
            f"R = {R_GAS} psi·ft³/(lb-mol·°R)  |  13 componentes")
        self._lbl_info.setStyleSheet(
            f'background:transparent;color:{TEXT};'
            f'font-family:"{FONT_F}";font-size:9pt;padding:0px 4px;')
        sb.addPermanentWidget(self._lbl_info, 1)
        self.setStatusBar(sb)
        self._sb = sb

        # Cablear cambio de EOS desde la pestaña Equilibrio.
        self.tab_eq.eos_changed.connect(self._on_eos_changed)

    def _on_eos_changed(self, eos):
        """Propaga el cambio de ecuación de estado a todo el sistema:
           - Cambia la EOS activa del motor nucleo.eos.
           - Reinicia kij_user a la matriz por defecto de la EOS elegida
             (PR: matriz HYSYS; SRK: ceros hasta que se carguen valores).
           - Refresca la tabla en la pestaña Parametros.
           - Actualiza el mensaje del status bar.
        Las pestañas Envolvente / Saturacion leen kij_user via callback y
        el engine expone despachadores que ya usan la EOS activa, así que
        no requieren tocarse. La pestaña Propiedades queda en PR (blindada
        en pestana_propiedades.py) hasta nueva calibracion contra HYSYS-SRK.
        """
        global kij_user
        import eos as _eng
        _eng.set_eos(eos)
        base = _eng.KIJ_DEFAULT_SRK if eos == 'SRK' else _eng.KIJ_DEFAULT_PR
        kij_user = copy.deepcopy(base)
        # Refrescar tabla de kij en la pestaña Parametros
        if hasattr(self, 'tab_par'):
            self.tab_par.refrescar_tabla()
        # Actualizar el label permanente del status bar
        nombre = "Soave-Redlich-Kwong" if eos == 'SRK' else "Peng-Robinson"
        self._lbl_info.setText(
            f"  {nombre} EOS  |  "
            f"R = {R_GAS} psi·ft³/(lb-mol·°R)  |  13 componentes")

def main():
    """Arranca la aplicacion. Llamado desde main.py en la raiz."""
    import time as _time
    app = QApplication(sys.argv)
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
    win.show()
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

"""
Pestaña Puntos de Saturación para ThermoPhase.
Calcula T de rocío, T de burbuja, P de rocío, P de burbuja.
Mismo estilo (Arial Narrow) que el resto del programa.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QGridLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSizePolicy, QAbstractSpinBox, QStyledItemDelegate
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QPen

from eos import NOMBRES, NC
import dialogos as dialogos
import idioma as _i18n
import eos as _eng
import unidades as _u
WHITE="#FFFFFF"; GRAY_TIT="#A8A8A8"; GRAY_HDR="#C8C8C8"; GRAY_LBL="#D0D0D0"
GRAY_RES="#E8E8E8"; BORDER="#888888"; TEXT="#000000"; TEXT_DIM="#555555"
# Gris más claro (sin llegar al blanco) para las celdas vacías ANTES de
# calcular: contrasta con el fondo de la ventana y evita la saturación de
# grises. Tras un cálculo, las celdas usan GRAY_RES/WHITE como siempre.
GRAY_EMPTY="#F6F6F6"


class GridDelegate(QStyledItemDelegate):
    """Rejilla PLANA de 1px (borde derecho e inferior de cada celda) que
    respeta el color de fondo por celda. Reemplaza al gridline nativo (que a
    DPI fraccional se ve biselado) sin pisar los setBackground como sí lo hace
    un borde por CSS."""
    def __init__(self, color=BORDER, parent=None):
        super().__init__(parent)
        self._pen = QPen(QColor(color)); self._pen.setWidth(1); self._pen.setCosmetic(True)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        painter.save(); painter.setPen(self._pen); r = option.rect
        painter.drawLine(r.right(), r.top(), r.right(), r.bottom())
        painter.drawLine(r.left(), r.bottom(), r.right(), r.bottom())
        painter.restore()
TEXT_RES="#000080"; FONT_F="Arial Narrow"; FS=10
ROW_H = 22

# ── Catalogo de propiedades por fase del punto de saturacion ─────
# Son las MISMAS propiedades que ofrece el resumen de Equilibrio de fases
# (mas la viscosidad, ya calculada por la misma correlacion LBC validada).
# Cada entrada: (key, etiqueta_base, magnitud_unidad|None, decimales,
#                key_vapor, key_liquido, conversor|None)
_PROP_SAT = [
    ('pm',         'Peso molecular',            None,   4, 'PM_v',  'PM_l',  None),
    ('z',          'Factor de compresibilidad', None,   4, 'ZV',    'ZL',    None),
    ('densidad',   'Densidad masica',           'dens', 4, 'rho_v', 'rho_l', 'dens'),
    ('sg',         'Gravedad especifica',       None,   4, 'sg_v',  'sg_l',  None),
    ('entalpia',   'Entalpia molar',            'H',    2, 'H_v',   'H_l',   'H'),
    ('entropia',   'Entropia molar',            'S',    4, 'S_v',   'S_l',   'S'),
    ('viscosidad', 'Viscosidad',                'visc', 5, 'mu_v',  'mu_l',  None),
    # Poder calorífico (GPSA-87). Se calcula desde la composición de cada fase
    # (marcador 'PCAL:<clave>'); no proviene del dict 'props'.
    ('hhv_mas',    'HHV masico [BTU/lb]',       None,   1, 'PCAL:hhv_mas', 'PCAL:hhv_mas', None),
    ('lhv_mas',    'LHV masico [BTU/lb]',       None,   1, 'PCAL:lhv_mas', 'PCAL:lhv_mas', None),
    ('hhv_vol',    'HHV volumetrico [BTU/pie3]',None,   1, 'PCAL:hhv_vol', 'PCAL:hhv_vol', None),
    ('lhv_vol',    'LHV volumetrico [BTU/pie3]',None,   1, 'PCAL:lhv_vol', 'PCAL:lhv_vol', None),
    # GPM C3+ solo en fase vapor (marcador GPM:vapor); líquido vacío.
    ('gpm',        'GPM C3+ [gal/1000pie3]',    None,   4, 'GPM:v', 'GPM:none', None),
]
_PROP_SAT_DEF = {d[0]: d for d in _PROP_SAT}
# Seleccion por defecto = las 6 propiedades que la pestaña muestra hoy.
_PROP_SAT_DEFAULT = ['pm', 'z', 'densidad', 'sg', 'entalpia', 'entropia']
# Tope de propiedades a mostrar: se pueden colocar TODAS las del catalogo
# (minimo 1). La ventana se ajusta sola al numero elegido.
PROP_SAT_MAX = len(_PROP_SAT)


def _conv_prop(clave_conv, val):
    """Convierte un valor de propiedad al sistema de unidades activo segun el
    conversor indicado en el catalogo. cP (viscosidad) es universal: sin
    conversion."""
    if val is None or clave_conv is None:
        return val
    if clave_conv == 'dens':
        return _u.dens_desde(val)
    if clave_conv == 'H':
        return _u.H_desde(val)
    if clave_conv == 'S':
        return _u.S_desde(val)
    return val

# ── Estilo retro de las listas desplegables (QComboBox) ───────
# Cambia de modelo comentando el activo y descomentando otro.
# Modelo 1 — Windows 95 clásico  (ACTIVO)
COMBO_STYLE = (
    f'QComboBox {{ background:{WHITE}; border:2px inset {BORDER};'
    f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
    f'QComboBox:on {{ border:2px inset #555555; }}'
    f'QAbstractItemView {{ background:{WHITE}; border:1px solid #000000;'
    f' color:{TEXT}; selection-background-color:#DCDCDC; selection-color:#000000;'
    f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
    f'QAbstractItemView::item {{ min-height:22px; padding:1px 6px; }}'
)

def _aplicar_estilo_combo(combo):
    """Aplica el estilo retro (Modelo 1) al combo y a su lista emergente.
    Usa Fusion por-widget para que el QSS se respete en Windows, fuerza que
    la lista se despliegue hacia ABAJO (no centrada en la opcion actual) y
    conserva la flecha (la dibuja Fusion, por eso no se estiliza ::drop-down)."""
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

BTN_STYLE=(f'background:{GRAY_LBL};border:2px outset {BORDER};'
           f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
LBL_TIT=(f'background:{GRAY_TIT};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_SEC=(f'background:{GRAY_LBL};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_RES=(f'background:{GRAY_LBL};border:1px solid {BORDER};color:{TEXT_RES};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px 6px;')


# ── Worker para cálculo en segundo plano ──────────────────────
class SatWorker(QThread):
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)
    def __init__(self, tipo, valor, z, kij, eos=None):
        super().__init__()
        self.tipo=tipo; self.valor=valor; self.z=z; self.kij=kij; self.eos=eos
    def run(self):
        try:
            import eos as _eng
            if self.eos:
                _eng.set_eos(self.eos)      # los puntos de saturacion obedecen la EOS elegida
            from envolvente import punto_saturacion
            res = punto_saturacion(self.tipo, self.valor, self.z, self.kij)
            self.done.emit(res if res else {})
        except Exception as e:
            self.error.emit(str(e))


class TabSaturacion(QWidget):
    # Mapeo desplegable → (tipo_calc, unidad_entrada, etiqueta_entrada, unidad_result)
    TIPOS = {
        "Temperatura de Rocío":   ('T_rocio',   'P', 'Presion (psi):',      'T'),
        "Temperatura de Burbuja": ('T_burbuja', 'P', 'Presion (psi):',      'T'),
        "Presion de Rocío":       ('P_rocio',   'T', 'Temperatura (°R):',   'P'),
        "Presion de Burbuja":     ('P_burbuja', 'T', 'Temperatura (°R):',   'P'),
    }

    def __init__(self, get_z, get_kij):
        super().__init__()
        self.get_z=get_z; self.get_kij=get_kij
        self.worker=None
        self.last_result=None
        self._res_unit=None
        self._tipo_txt=None
        self._build()

    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root=QVBoxLayout(self)
        root.setContentsMargins(13,9,13,5); root.setSpacing(3)

        # Título
        title=QLabel("ThermoPhase — Puntos de Saturación")
        title.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_TIT)
        root.addWidget(title)

        # ── Panel de entrada ──────────────────────────────────
        in_box=QFrame()
        in_box.setStyleSheet('background:transparent;border:none;')
        gl=QGridLayout(in_box); gl.setContentsMargins(6,4,6,4); gl.setSpacing(4)

        def lbl(txt, res=False):
            l=QLabel(txt)
            if res:
                # Celda de RESULTADO: fondo blanco
                l.setStyleSheet(
                    f'background:{WHITE};border:1px solid {BORDER};'
                    f'color:{TEXT_RES};padding:2px 6px;'
                    f'font-family:"{FONT_F}";font-size:{FS}pt;')
            else:
                # Etiqueta: mismo gris que los encabezados de la pestaña de
                # Equilibrio de Fases (GRAY_LBL) para estandarizar el aspecto.
                l.setStyleSheet(
                    f'background:{GRAY_LBL};border:1px solid {BORDER};'
                    f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
            l.setFixedHeight(24)
            return l

        # Selector de tipo de cálculo
        gl.addWidget(lbl("Calcular:"), 0, 0)
        self.cmb_tipo=QComboBox()
        self.cmb_tipo.addItems(list(self.TIPOS.keys()))
        self.cmb_tipo.setFixedHeight(24)
        _aplicar_estilo_combo(self.cmb_tipo)
        self.cmb_tipo.currentTextChanged.connect(self._on_tipo_change)
        gl.addWidget(self.cmb_tipo, 0, 1)

        # Etiqueta + campo de condición (P o T)
        self.lbl_cond=lbl("Presion (psi):")
        self.lbl_cond.setFixedWidth(130)
        gl.addWidget(self.lbl_cond, 1, 0)
        self.sp_cond=QDoubleSpinBox()
        self.sp_cond.setRange(0.0, 15000.0); self.sp_cond.setDecimals(2)
        self.sp_cond.setSpecialValueText(" ")   # muestra vacío en el mínimo
        self.sp_cond.setValue(0.0)              # inicia vacío
        self.sp_cond.setFixedHeight(24)
        # Sin flechas de incremento/decremento
        self.sp_cond.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_cond.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gl.addWidget(self.sp_cond, 1, 1)

        # Botón calcular
        self.btn=QPushButton("Calcular punto de saturacion")
        self.btn.setStyleSheet(BTN_STYLE); self.btn.setFixedHeight(24)
        self.btn.clicked.connect(self.calcular)
        gl.addWidget(self.btn, 2, 0, 1, 2)

        gl.setColumnStretch(0,0); gl.setColumnStretch(1,1)

        # ── Panel de resultados (a la derecha de la entrada) ──
        res_outer=QVBoxLayout(); res_outer.setSpacing(3)
        res_title=QLabel("Resultado:")
        res_title.setStyleSheet(LBL_SEC); res_title.setFixedHeight(20)
        res_outer.addWidget(res_title)

        res_box=QFrame()
        res_box.setStyleSheet('background:transparent;border:none;')
        rl=QGridLayout(res_box); rl.setContentsMargins(6,3,6,3); rl.setSpacing(3)

        self.lbl_res_label=lbl("Temperatura de rocio (°F):")
        rl.addWidget(self.lbl_res_label, 0, 0)
        self.lbl_res_val=lbl("", res=True)
        self.lbl_res_val.setFixedWidth(120)
        self.lbl_res_val.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.lbl_res_val, 0, 1)

        self.lbl_res2_label=lbl("Equivalente (°R / psi):")
        rl.addWidget(self.lbl_res2_label, 1, 0)
        self.lbl_res2_val=lbl("", res=True)
        self.lbl_res2_val.setFixedWidth(120)
        self.lbl_res2_val.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.lbl_res2_val, 1, 1)

        self.lbl_estado=QLabel("")
        self.lbl_estado.setStyleSheet(
            f'color:{TEXT_DIM};font-family:"{FONT_F}";font-size:9pt;background:transparent;')
        rl.addWidget(self.lbl_estado, 2, 0, 1, 2)

        # Etiqueta estira para llenar, valor fijo a la derecha → sin huecos
        rl.setColumnStretch(0,1); rl.setColumnStretch(1,0)
        res_outer.addWidget(res_box)

        # Layout horizontal: entrada (izq) + resultado (der), repartido 50/50
        top_row=QHBoxLayout(); top_row.setSpacing(10)
        top_row.setContentsMargins(0,0,0,0)
        in_wrap=QVBoxLayout(); in_wrap.setSpacing(3)
        in_title=QLabel("Datos de entrada:")
        in_title.setStyleSheet(LBL_SEC); in_title.setFixedHeight(20)
        in_wrap.addWidget(in_title)
        in_wrap.addWidget(in_box)
        top_row.addLayout(in_wrap, 1)      # entrada ocupa mitad
        top_row.addLayout(res_outer, 1)    # resultado ocupa mitad
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Envolver en un contenedor con política vertical Maximum para que el
        # layout NO reserve más alto que el contenido (evita ~20 px de hueco
        # muerto entre este panel y "Composicion de las fases en equilibrio").
        top_wrap=QWidget(); top_wrap.setLayout(top_row)
        top_wrap.setStyleSheet('background:transparent;')
        top_wrap.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        root.addWidget(top_wrap)

        # ── Tabla de composiciones de las fases ───────────────
        comp_title=QLabel("Composicion de las fases en equilibrio:")
        comp_title.setStyleSheet(LBL_SEC); comp_title.setFixedHeight(22)
        root.addWidget(comp_title)

        # 5 columnas (col 4 = Fase Acuosa) y NC+2 filas (fila del agua en el
        # indice NC, Sumatorias en NC+1). Col 4 y la fila del agua quedan
        # OCULTAS por defecto: con agua inactiva la tabla se ve identica al
        # original (4 columnas, 13 HC + Sumatorias).
        self.tbl=QTableWidget(NC+2, 5)
        self.tbl.setHorizontalHeaderLabels(
            ["Componente","Mezcla","Fase Vapor","Fase Liquida","Fase Acuosa"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Rejilla PLANA de 1px dibujada con bordes CSS por celda (no el gridline
        # nativo de Windows, que se ve biselado/doble a ciertos DPI). Igual
        # aspecto que las tablas de Equilibrio de fases: borde superior/izquierdo
        # en la tabla y borde derecho/inferior en cada celda -> 1px sin duplicar.
        self.tbl.setShowGrid(False)
        self.tbl.setStyleSheet(
            f'QTableWidget {{ background:{WHITE};'
            f'border-top:1px solid {BORDER};border-left:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;}}'
            f'QTableWidget::item {{ padding:0px 6px; }}'
            f'QHeaderView::section {{ background:{GRAY_LBL};border:none;'
            f'border-right:1px solid {BORDER};border-bottom:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px; }}')
        self.tbl.setItemDelegate(GridDelegate(BORDER, self.tbl))
        hh=self.tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(1,120)
        self.tbl.setColumnWidth(2,120); self.tbl.setColumnWidth(3,120)
        self.tbl.setColumnWidth(4,120)
        self.tbl.verticalHeader().setDefaultSectionSize(22)
        self.tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Col 4 (Fase Acuosa) oculta hasta que el agua este activa.
        self.tbl.setColumnHidden(4, True)
        # Expandir horizontalmente para llenar el ancho del layout (la
        # columna 0 en Stretch absorbe el espacio sobrante).
        self.tbl.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Fixed)

        GRIS_NOMBRE = QColor(GRAY_LBL)    # mismo gris que los nombres de la
                                          # pestaña de Equilibrio de Fases
        GRIS_RES = QColor(GRAY_EMPTY)     # gris claro para celdas vacías
                                          # (estado inicial, sin cálculo)
        for i in range(NC):
            it=QTableWidgetItem(NOMBRES[i].rstrip(':'))
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS_NOMBRE))
            self.tbl.setItem(i,0,it)
            for c in (1,2,3,4):
                cell=QTableWidgetItem("")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cell.setBackground(QBrush(GRIS_RES))
                self.tbl.setItem(i,c,cell)
        # Fila del agua (indice NC): visible solo con agua activa.
        wit=QTableWidgetItem(_eng.componente_nombre(_eng.IDX_AGUA))
        wit.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        wit.setBackground(QBrush(GRIS_NOMBRE))
        self.tbl.setItem(NC,0,wit)
        for c in (1,2,3,4):
            cell=QTableWidgetItem("")
            cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            cell.setBackground(QBrush(GRIS_RES))
            self.tbl.setItem(NC,c,cell)
        self.tbl.setRowHidden(NC, True)
        # Fila sumatorias (ahora en el indice NC+1)
        sit=QTableWidgetItem("Sumatorias:")
        sit.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        sit.setBackground(QBrush(GRIS_NOMBRE))
        self.tbl.setItem(NC+1,0,sit)
        for c in (1,2,3,4):
            cell=QTableWidgetItem("")
            cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            cell.setBackground(QBrush(GRIS_RES))
            self.tbl.setItem(NC+1,c,cell)

        root.addWidget(self.tbl)

        # ── Panel de propiedades del punto de saturación ──────
        # Cabecera: titulo + boton para elegir que propiedades mostrar
        # (mismo comportamiento que el resumen de Equilibrio de fases).
        prop_hdr = QHBoxLayout()
        prop_hdr.setContentsMargins(0, 0, 0, 0); prop_hdr.setSpacing(6)
        prop_title=QLabel("Propiedades del punto de saturacion:")
        prop_title.setStyleSheet(LBL_SEC); prop_title.setFixedHeight(22)
        prop_hdr.addWidget(prop_title, 1)
        self.btn_props = QPushButton("Propiedades")
        # Misma altura que los encabezados de sección de Equilibrio de fases
        # (section_label = 22 px) y que el título contiguo.
        self.btn_props.setFixedHeight(22); self.btn_props.setFixedWidth(120)
        self.btn_props.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_props.setStyleSheet(
            f'QPushButton {{ background:{GRAY_LBL}; border:1px solid {BORDER};'
            f' font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 8px; }}'
            f'QPushButton:hover {{ background:#DCDCDC; }}')
        self.btn_props.clicked.connect(self._abrir_selector_props)
        prop_hdr.addWidget(self.btn_props, 0)
        root.addLayout(prop_hdr)

        self.tbl_prop=QTableWidget(0, 5)
        self.tbl_prop.setHorizontalHeaderLabels(
            ["Propiedad","Mezcla","Fase Vapor","Fase Liquida","Fase Acuosa"])
        self.tbl_prop.verticalHeader().setVisible(False)
        self.tbl_prop.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_prop.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_prop.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tbl_prop.setShowGrid(False)
        self.tbl_prop.setStyleSheet(
            f'QTableWidget {{ background:{WHITE};'
            f'border-top:1px solid {BORDER};border-left:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;}}'
            f'QTableWidget::item {{ padding:0px 6px; }}'
            f'QHeaderView::section {{ background:{GRAY_LBL};border:none;'
            f'border-right:1px solid {BORDER};border-bottom:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px; }}')
        self.tbl_prop.setItemDelegate(GridDelegate(BORDER, self.tbl_prop))
        hp=self.tbl_prop.horizontalHeader()
        hp.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hp.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hp.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hp.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hp.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tbl_prop.setColumnWidth(1,120)
        self.tbl_prop.setColumnWidth(2,120); self.tbl_prop.setColumnWidth(3,120)
        self.tbl_prop.setColumnWidth(4,120)
        self.tbl_prop.verticalHeader().setDefaultSectionSize(22)
        self.tbl_prop.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_prop.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Col 4 (Fase Acuosa) oculta hasta que el agua este activa.
        self.tbl_prop.setColumnHidden(4, True)
        self.tbl_prop.setSizePolicy(QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Fixed)

        # Propiedades seleccionadas (por defecto, las 6 que mostraba la pestaña)
        self._props_sel = list(_PROP_SAT_DEFAULT)
        # Callback (lo fija la ventana principal) para redimensionar la ventana
        # cuando cambia el numero de propiedades mostradas.
        self._on_props_resize = None
        self._rebuild_prop_table()
        root.addWidget(self.tbl_prop)

    def showEvent(self, event):
        super().showEvent(event)
        self._fit_table_heights()

    def aplicar_componentes(self, activos):
        """Oculta las filas de los componentes no activos en la tabla de
        composicion de fases y reajusta su alto. Cambio puramente estetico
        (la composicion se lee del fluido principal via get_z, que ya
        devuelve 0 para los componentes ocultos)."""
        act = set(activos)
        for i in range(NC):
            self.tbl.setRowHidden(i, i not in act)
        # Agua (idx 13): muestra/oculta la fila del agua (indice NC) y la
        # columna de Fase Acuosa (col 4) en ambas tablas. La fila de
        # Sumatorias (indice NC+1) nunca se oculta.
        agua_on = _eng.IDX_AGUA in act
        self.tbl.setRowHidden(NC, not agua_on)
        self.tbl.setColumnHidden(4, not agua_on)
        self.tbl_prop.setColumnHidden(4, not agua_on)
        self._fit_table_heights()

    def _rebuild_prop_table(self):
        """(Re)construye la tabla de propiedades mostrando solo las
        seleccionadas, en el orden del catalogo. Solo arma etiquetas y celdas
        vacias; los valores los rellena _render."""
        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        GRIS = QColor(GRAY_LBL); GRIS_RES = QColor(GRAY_EMPTY)
        self.tbl_prop.setRowCount(len(sel))
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            self.tbl_prop.setRowHeight(r, ROW_H)
            unidad = f" [{_u.u(mag)}]" if mag else ""
            it = QTableWidgetItem(f"{_i18n.t(base)}{unidad}:")
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS))
            self.tbl_prop.setItem(r, 0, it)
            for c in (1, 2, 3, 4):
                cc = QTableWidgetItem("")
                cc.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cc.setBackground(QBrush(GRIS_RES))
                self.tbl_prop.setItem(r, c, cc)
        self._fit_table_heights()

    def _abrir_selector_props(self):
        """Ventana de seleccion de propiedades (dos listas: disponibles /
        seleccionadas). Se puede mostrar entre 1 y PROP_SAT_MAX propiedades,
        de las MISMAS que ofrece el equilibrio de fases, para no
        desconfigurar la ventana."""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                     QListWidget, QListWidgetItem, QPushButton,
                                     QLabel)
        MIN, MAX = 1, PROP_SAT_MAX

        def etiqueta(key):
            base = _PROP_SAT_DEF[key][1]; mag = _PROP_SAT_DEF[key][2]
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
        col_izq = QVBoxLayout(); col_izq.setSpacing(3)
        lbl_disp = QLabel(_i18n.t("Disponibles"))
        lbl_disp.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                               f'color:{TEXT};background:transparent;')
        col_izq.addWidget(lbl_disp)
        lista_disp = QListWidget(); lista_disp.setStyleSheet(list_qss)
        lista_disp.setFixedSize(240, 240)
        col_izq.addWidget(lista_disp)
        cols.addLayout(col_izq)

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
        for key, *_ in _PROP_SAT:
            if key not in self._props_sel:
                add_item(lista_disp, key)

        fila = QHBoxLayout(); fila.setSpacing(8)
        contador = QLabel()
        contador.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                               f'color:{TEXT};background:transparent;')
        fila.addWidget(contador); fila.addStretch()
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
            btn_ok.setEnabled(MIN <= n <= MAX)
            btn_add.setEnabled(n < MAX and lista_disp.count() > 0)
            btn_rem.setEnabled(n > MIN)

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
            if lista_sel.count() > MIN:
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
                nuevos = list(_PROP_SAT_DEFAULT)
            # Mantener el orden canonico del catalogo.
            self._props_sel = [k for k, *_ in _PROP_SAT if k in nuevos]
            self._rebuild_prop_table()
            if getattr(self, 'last_result', None) is not None:
                self._render(self.last_result)
            # Avisar a la ventana principal para reajustar el alto.
            if self._on_props_resize is not None:
                self._on_props_resize(self, len(self._props_sel))

    def _fit_table_heights(self):
        """Ajusta la altura de cada tabla a la suma real de sus filas,
        para mostrar todas sin scrollbar (robusto ante DPI/versión Windows)."""
        for tbl, nrows in [(self.tbl, NC+2),
                           (self.tbl_prop, self.tbl_prop.rowCount())]:
            h = tbl.horizontalHeader().height()
            for r in range(nrows):
                h += tbl.rowHeight(r)
            h += 2*tbl.frameWidth()   # solo el borde; el scroll está siempre OFF
            tbl.setFixedHeight(h)

    def _tipo_es(self):
        """Clave ESPAÑOL del tipo seleccionado (robusto a la traduccion)."""
        try:
            import idioma
            idx = self.cmb_tipo.currentIndex()
            es = self.cmb_tipo.property(f"_i18n_es_{idx}")
            if es and es in self.TIPOS:
                return es
            txt = self.cmb_tipo.currentText()
            es2 = idioma._TRAD_INV.get(txt, txt)
            return es2 if es2 in self.TIPOS else txt
        except Exception:
            return self.cmb_tipo.currentText()

    def _actualizar_labels_resultado(self):
        """Fija las etiquetas de resultado segun el tipo y las unidades activas
        (funciona aunque todavia no se haya calculado)."""
        tipo, unidad, etiqueta, res_unit = self.TIPOS[self._tipo_es()]
        tipo_txt = self.cmb_tipo.currentText()
        if res_unit == 'T':
            self.lbl_res_label.setText(f"{tipo_txt} ({_u.u('T')}):")
            self.lbl_res2_label.setText(f"{_i18n.t('Equivalente')} ({_u.u_abs()}):")
        else:
            self.lbl_res_label.setText(f"{tipo_txt} ({_u.u('P')}):")
            self.lbl_res2_label.setText(f"{_i18n.t('Temperatura')} ({_u.u('T')}):")

    def _on_tipo_change(self, txt):
        tipo, unidad, etiqueta, _ = self.TIPOS[self._tipo_es()]
        if unidad=='P':
            self.lbl_cond.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
            self.sp_cond.setRange(0.0, 999999.0)
        else:
            self.lbl_cond.setText(f"{_i18n.t('Temperatura')} ({_u.u_abs()}):")
            self.sp_cond.setRange(0.0, 9999.0)
        self._actualizar_labels_resultado()
        # No forzar valor — dejar lo que el usuario haya puesto o vacío

    def calcular(self):
        z=self.get_z()
        if abs(sum(z)-1.0)>1e-3:
            dialogos.advertencia(self,
                "La suma de fracciones debe ser 1.0")
            return
        kij=self.get_kij()
        tipo, unidad, etiqueta, res_unit = self.TIPOS[self._tipo_es()]
        valor=self.sp_cond.value()
        if valor <= 0.0:
            dialogos.advertencia(self,
                "Ingrese un valor de presion o temperatura.")
            return
        # Convertir al interno del motor: P->psia, T->°R
        valor = _u.p_a_psia(valor) if unidad=='P' else _u.R_desde_abs(valor)

        self.btn.setEnabled(False); self.btn.setText(_i18n.t("Calculando..."))
        self.lbl_estado.setText("")
        self._res_unit=res_unit; self._tipo_txt=self.cmb_tipo.currentText()
        eos_ctx = _eng.get_eos()          # EOS activa (ya fijada por get_z)
        self.worker=SatWorker(tipo, valor, z, kij, eos_ctx)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def aplicar_unidades(self, old):
        """Convierte el valor de entrada, actualiza etiquetas y re-muestra el
        resultado en el sistema de unidades activo."""
        tipo, unidad, etiqueta, res_unit = self.TIPOS[self._tipo_es()]
        v = self.sp_cond.value()
        if v > 0:
            if unidad == 'P':
                v_int = _u.p_a_psia(v, old); self.sp_cond.setValue(_u.p_desde_psia(v_int))
            else:
                v_int = _u.R_desde_abs(v, old); self.sp_cond.setValue(_u.abs_desde_R(v_int))
        # Etiqueta de condicion
        if unidad == 'P':
            self.lbl_cond.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
        else:
            self.lbl_cond.setText(f"{_i18n.t('Temperatura')} ({_u.u_abs()}):")
        # Etiquetas de la tabla de propiedades con la unidad activa
        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            it = self.tbl_prop.item(r, 0)
            if it is not None:
                unidad = f" [{_u.u(mag)}]" if mag else ""
                it.setText(f"{_i18n.t(base)}{unidad}:")
        # Etiquetas de resultado (aunque no haya calculo aun)
        self._actualizar_labels_resultado()
        # Re-render del ultimo resultado (internos °R/psia)
        if getattr(self, 'last_result', None) is not None:
            self._render(self.last_result)

    def _on_error(self, msg):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular punto de saturacion"))
        dialogos.error(self, msg)

    def _on_done(self, res):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular punto de saturacion"))
        if not res or not res.get('exito'):
            self.lbl_res_val.setText(""); self.lbl_res2_val.setText("")
            self.last_result = None
            dialogos.advertencia(self, _i18n.t("No se encontro punto de saturacion"))
            return
        self.last_result = res
        self._render(res)

    def _render(self, res):
        """Muestra el resultado en pantalla. Se llama tanto desde el worker
        (calculo nuevo) como desde set_estado (carga desde archivo)."""

        T=res['T']; P=res['P']   # internos: °R, psia
        self._tipo_txt=self.cmb_tipo.currentText()   # nombre actual (traducido)
        if self._res_unit=='T':
            self.lbl_res_label.setText(f"{self._tipo_txt} ({_u.u('T')}):")
            self.lbl_res_val.setText(f"{_u.t_desde_R(T):.2f}")
            self.lbl_res2_label.setText(f"{_i18n.t('Equivalente')} ({_u.u_abs()}):")
            self.lbl_res2_val.setText(f"{_u.abs_desde_R(T):.2f}")
        else:
            self.lbl_res_label.setText(f"{self._tipo_txt} ({_u.u('P')}):")
            self.lbl_res_val.setText(f"{_u.p_desde_psia(P):.2f}")
            self.lbl_res2_label.setText(f"{_i18n.t('Temperatura')} ({_u.u('T')}):")
            self.lbl_res2_val.setText(f"{_u.t_desde_R(T):.2f}")

        # ── Composición: Mezcla (col1) | Vapor (col2) | Líquido (col3) ──
        x=res.get('x',[0]*NC); y=res.get('y',[0]*NC)
        z=res.get('z') or self.get_z()
        sx=sum(x); sy=sum(y); sz=sum(z)
        WHT=QColor(WHITE)
        for i in range(NC):
            self.tbl.item(i,1).setText(f"{z[i]:.4f}")
            self.tbl.item(i,2).setText(f"{y[i]:.4f}")
            self.tbl.item(i,3).setText(f"{x[i]:.4f}")
            for c in (1,2,3):
                self.tbl.item(i,c).setBackground(QBrush(WHT))
                self.tbl.item(i,c).setForeground(QBrush(QColor(TEXT_RES)))
        # Fila Sumatorias (indice NC+1)
        self.tbl.item(NC+1,1).setText(f"{sz:.4f}")
        self.tbl.item(NC+1,2).setText(f"{sy:.4f}")
        self.tbl.item(NC+1,3).setText(f"{sx:.4f}")
        for c in (1,2,3):
            self.tbl.item(NC+1,c).setBackground(QBrush(WHT))

        # ── Fase Acuosa (col 4): flash trifásico en el punto (T,P) ──
        # Solo cuando el agua está activa. Si el flash falla o beta_W≈0, se
        # deja la columna vacía. NO altera las columnas Mezcla/Vapor/Líquido.
        self._render_acuosa(T, P)

        # ── Propiedades: Mezcla | Vapor | Líquido ──
        p=res.get('props',{})
        import poder_calorifico as _pc
        import eos as _eng
        _pc_v = _pc.poder_calorifico_fase(y, p.get('PM_v'))
        _pc_l = _pc.poder_calorifico_fase(x, p.get('PM_l'))
        _pc_z = _pc.poder_calorifico_fase(z, None) if sz > 0 else {}
        _gpm_v = _pc.gpm_c3(y)
        _gpm_z = _pc.gpm_c3(z) if sz > 0 else None
        # Peso molecular de la mezcla desde la composición global.
        _pm_z = sum(z[i]*_eng.PM[i] for i in range(NC)) if sz > 0 else None
        # En un punto de saturación una fase es incipiente (fracción → 0), así
        # que la mezcla coincide con la fase saturada. Densidad/SG/Z de mezcla =
        # los de esa fase (rocío → vapor; burbuja → líquido).
        tipo = self._tipo_es()
        es_rocio = 'rocio' in tipo.lower() or 'rocío' in tipo.lower()
        _rho_z = p.get('rho_v') if es_rocio else p.get('rho_l')
        _sg_z  = p.get('sg_v')  if es_rocio else p.get('sg_l')
        _z_z   = p.get('ZV')    if es_rocio else p.get('ZL')

        def _valor_prop(kf, phase_pc, gpm_val):
            if isinstance(kf, str) and kf.startswith('PCAL:'):
                return phase_pc.get(kf.split(':', 1)[1])
            if isinstance(kf, str) and kf.startswith('GPM:'):
                return gpm_val if kf == 'GPM:v' else None
            return _conv_prop(conv, p.get(kf))

        def _valor_mezcla(key, conv):
            if key == 'pm':        return _conv_prop(conv, _pm_z)
            if key == 'densidad':  return _conv_prop(conv, _rho_z)
            if key == 'sg':        return _sg_z
            if key == 'z':         return _z_z
            if key in ('hhv_mas','lhv_mas','hhv_vol','lhv_vol'):
                return _pc_z.get(key)
            if key == 'gpm':       return _gpm_z
            return None   # entalpía, entropía, viscosidad: sin valor de mezcla

        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            unidad = f" [{_u.u(mag)}]" if mag else ""
            it_lbl = self.tbl_prop.item(r, 0)
            if it_lbl is not None:
                it_lbl.setText(f"{_i18n.t(base)}{unidad}:")
            vz = _valor_mezcla(key, conv)
            vv = _valor_prop(kv, _pc_v, _gpm_v)
            vl = _valor_prop(kl, _pc_l, None)
            fmt = f"{{:.{dec}f}}"
            for c, vw in ((1, vz), (2, vv), (3, vl)):
                cell = self.tbl_prop.item(r, c)
                if vw is not None:
                    cell.setText(fmt.format(vw))
                    cell.setForeground(QBrush(QColor(TEXT_RES)))
                    cell.setBackground(QBrush(WHT))
                else:
                    cell.setText("")
                    cell.setBackground(QBrush(QColor(GRAY_RES)))

    def _limpiar_acuosa(self):
        """Vacía la columna de Fase Acuosa (col 4) en ambas tablas."""
        GR = QColor(GRAY_RES)
        for r in range(self.tbl.rowCount()):
            it = self.tbl.item(r, 4)
            if it is not None:
                it.setText(""); it.setBackground(QBrush(GR))
        for r in range(self.tbl_prop.rowCount()):
            it = self.tbl_prop.item(r, 4)
            if it is not None:
                it.setText(""); it.setBackground(QBrush(GR))

    def _render_acuosa(self, T_R, P_psia):
        """Corre el flash trifásico en el punto (T_R,P_psia) y llena la columna
        de Fase Acuosa (col 4) de composición y propiedades. Reproduce el
        formato/decimales de _render_trifasico de ventana_principal.py. Si el
        agua está inactiva, el flash falla o beta_W≈0, deja la columna vacía."""
        # Solo si el agua está activa (col 4 visible / fila del agua visible).
        if self.tbl.isColumnHidden(4):
            return
        z14 = self.get_z()
        if len(z14) <= _eng.IDX_AGUA or z14[_eng.IDX_AGUA] <= 1e-12:
            self._limpiar_acuosa(); return
        if not (T_R and P_psia and T_R > 0 and P_psia > 0):
            self._limpiar_acuosa(); return
        try:
            import flash_agua as _fa, numpy as _np, propiedades_agua as _pa
            eos_nombre = _eng.get_eos()
            z = _np.array(z14, dtype=float); z = z / z.sum()
            rt = _fa.flash_trifasico(z, T_R, P_psia, eos=eos_nombre, metodo='hv')
            bW = rt.get('beta_W', 0.0)
            if not bW or bW <= 1e-9:
                self._limpiar_acuosa(); return
            props = _pa.propiedades_fases(rt, T_R, P_psia, eos_nombre,
                                          metodo_densidad='COSTALD')
            pW = props.get('W', {}) or {}
        except Exception:
            self._limpiar_acuosa(); return

        WHT = QColor(WHITE); GR = QColor(GRAY_RES)
        w = rt.get('w')
        # ── Composición acuosa por componente (col 4), incl. fila agua (NC) ──
        sw = 0.0
        for i in range(NC + 1):   # 0..NC-1 HC, NC = agua
            it = self.tbl.item(i, 4)
            if it is None:
                continue
            val = float(w[i]) if (w is not None and i < len(w)) else None
            if val is not None:
                it.setText(f"{val:.4f}")
                it.setBackground(QBrush(WHT)); it.setForeground(QBrush(QColor(TEXT_RES)))
                sw += val
            else:
                it.setText(""); it.setBackground(QBrush(GR))
        # Sumatoria (fila NC+1)
        it_s = self.tbl.item(NC + 1, 4)
        if it_s is not None:
            it_s.setText(f"{sw:.4f}"); it_s.setBackground(QBrush(WHT))

        # ── Propiedades de la fase acuosa (col 4 de tbl_prop) ──
        # Mapa clave del catálogo -> valor de la fase acuosa (con conversión de
        # unidades igual que _render_trifasico). Las propiedades sin definición
        # para el agua (poder calorífico, GPM) quedan en blanco.
        _mapa = {
            'pm':        pW.get('PM'),
            'z':         pW.get('Z'),
            'densidad':  _u.dens_desde(pW.get('rho')) if pW.get('rho') is not None else None,
            'sg':        pW.get('sg'),
            'entalpia':  _u.H_desde(pW.get('H')) if pW.get('H') is not None else None,
            'entropia':  _u.S_desde(pW.get('S')) if pW.get('S') is not None else None,
            'viscosidad':pW.get('mu'),
        }
        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            cell = self.tbl_prop.item(r, 4)
            if cell is None:
                continue
            vw = _mapa.get(key)
            if vw is not None:
                cell.setText(f"{{:.{dec}f}}".format(vw))
                cell.setForeground(QBrush(QColor(TEXT_RES)))
                cell.setBackground(QBrush(WHT))
            else:
                cell.setText(""); cell.setBackground(QBrush(GR))

    # ── Guardar / restaurar estado ────────────────────────────
    def get_estado(self):
        """Devuelve inputs + resultado calculado (si existe)."""
        return {
            'entrada': {
                'tipo':  self._tipo_es(),
                'valor': float(self.sp_cond.value()),
            },
            'props': list(self._props_sel),
            'resultado': self.last_result,   # dict o None
        }

    def set_estado(self, datos):
        """Restaura inputs y re-renderiza el resultado sin recalcular."""
        e = datos.get('entrada', {}) or {}
        tipo = e.get('tipo', '')
        idx = self.cmb_tipo.findText(tipo)
        if idx < 0 and tipo in self.TIPOS:
            idx = list(self.TIPOS.keys()).index(tipo)
        if idx >= 0:
            self.cmb_tipo.setCurrentIndex(idx)
        try:
            self.sp_cond.setValue(float(e.get('valor', 0.0)))
        except (TypeError, ValueError):
            self.sp_cond.setValue(0.0)
        # Restaurar la seleccion de propiedades (si viene guardada).
        props = datos.get('props')
        if props:
            sel = [k for k, *_ in _PROP_SAT if k in props][:PROP_SAT_MAX]
            if sel and sel != self._props_sel:
                self._props_sel = sel
                self._rebuild_prop_table()
                if self._on_props_resize is not None:
                    self._on_props_resize(self, len(self._props_sel))
        # Renderizar resultado si estaba
        r = datos.get('resultado')
        if not r:
            return
        self.last_result = r
        # Reconstruir _res_unit y _tipo_txt (necesarios para _render)
        if tipo in self.TIPOS:
            _, _, _, self._res_unit = self.TIPOS[tipo]
            self._tipo_txt = tipo
        self._render(r)

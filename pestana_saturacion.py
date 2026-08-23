"""
Pestaña Puntos de Saturación para ThermoPhase.
Calcula T de rocío, T de burbuja, P de rocío, P de burbuja.
Mismo estilo (Arial Narrow) que el resto del programa.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QGridLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSizePolicy, QAbstractSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from eos import NOMBRES, NC
import dialogos as dialogos
import idioma as _i18n
import eos as _eng
import unidades as _u
WHITE="#FFFFFF"; GRAY_TIT="#A8A8A8"; GRAY_HDR="#C8C8C8"; GRAY_LBL="#D0D0D0"
GRAY_RES="#E8E8E8"; BORDER="#888888"; TEXT="#000000"; TEXT_DIM="#555555"
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
                # Etiqueta: fondo gris un poco mas oscuro que el panel para
                # diferenciarla del fondo
                l.setStyleSheet(
                    f'background:#C2C2C2;border:1px solid {BORDER};'
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
        in_wrap=QVBoxLayout(); in_wrap.setSpacing(3)
        in_title=QLabel("Datos de entrada:")
        in_title.setStyleSheet(LBL_SEC); in_title.setFixedHeight(20)
        in_wrap.addWidget(in_title)
        in_wrap.addWidget(in_box)
        top_row.addLayout(in_wrap, 1)      # entrada ocupa mitad
        top_row.addLayout(res_outer, 1)    # resultado ocupa mitad
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.addLayout(top_row)

        # ── Tabla de composiciones de las fases ───────────────
        comp_title=QLabel("Composicion de las fases en equilibrio:")
        comp_title.setStyleSheet(LBL_SEC); comp_title.setFixedHeight(20)
        root.addWidget(comp_title)

        self.tbl=QTableWidget(NC+1, 3)
        self.tbl.setHorizontalHeaderLabels(["Componente","Fase Vapor","Fase Liquida"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tbl.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;gridline-color:{BORDER};}}'
            f'QHeaderView::section {{ background:{GRAY_HDR};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px; }}')
        hh=self.tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(1,130); self.tbl.setColumnWidth(2,130)
        self.tbl.verticalHeader().setDefaultSectionSize(22)
        self.tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Expandir horizontalmente para llenar el ancho del layout (la
        # columna 0 en Stretch absorbe el espacio sobrante).
        self.tbl.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Fixed)

        GRIS_NOMBRE = QColor("#E8E8E8")   # gris claro para nombres
        BLANCO = QColor(WHITE)
        for i in range(NC):
            it=QTableWidgetItem(NOMBRES[i].rstrip(':'))
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS_NOMBRE))
            self.tbl.setItem(i,0,it)
            for c in (1,2):
                cell=QTableWidgetItem("")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cell.setBackground(QBrush(BLANCO))
                self.tbl.setItem(i,c,cell)
        # Fila sumatorias
        sit=QTableWidgetItem("Sumatorias:")
        sit.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        sit.setBackground(QBrush(GRIS_NOMBRE))
        self.tbl.setItem(NC,0,sit)
        for c in (1,2):
            cell=QTableWidgetItem("")
            cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            cell.setBackground(QBrush(BLANCO))
            self.tbl.setItem(NC,c,cell)

        root.addWidget(self.tbl)

        # ── Panel de propiedades del punto de saturación ──────
        # Cabecera: titulo + boton para elegir que propiedades mostrar
        # (mismo comportamiento que el resumen de Equilibrio de fases).
        prop_hdr = QHBoxLayout()
        prop_hdr.setContentsMargins(0, 0, 0, 0); prop_hdr.setSpacing(6)
        prop_title=QLabel("Propiedades del punto de saturacion:")
        prop_title.setStyleSheet(LBL_SEC); prop_title.setFixedHeight(20)
        prop_hdr.addWidget(prop_title, 1)
        self.btn_props = QPushButton("Propiedades")
        self.btn_props.setFixedHeight(22); self.btn_props.setFixedWidth(120)
        self.btn_props.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_props.setStyleSheet(
            f'QPushButton {{ background:{GRAY_LBL}; border:1px solid {BORDER};'
            f' font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 8px; }}'
            f'QPushButton:hover {{ background:#DCDCDC; }}')
        self.btn_props.clicked.connect(self._abrir_selector_props)
        prop_hdr.addWidget(self.btn_props, 0)
        root.addLayout(prop_hdr)

        self.tbl_prop=QTableWidget(0, 3)
        self.tbl_prop.setHorizontalHeaderLabels(
            ["Propiedad","Fase Vapor","Fase Liquida"])
        self.tbl_prop.verticalHeader().setVisible(False)
        self.tbl_prop.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_prop.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_prop.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tbl_prop.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;gridline-color:{BORDER};}}'
            f'QHeaderView::section {{ background:{GRAY_HDR};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px; }}')
        hp=self.tbl_prop.horizontalHeader()
        hp.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hp.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hp.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tbl_prop.setColumnWidth(1,130); self.tbl_prop.setColumnWidth(2,130)
        self.tbl_prop.verticalHeader().setDefaultSectionSize(22)
        self.tbl_prop.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_prop.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        # La fila de Sumatorias (indice NC) nunca se oculta.
        self._fit_table_heights()

    def _rebuild_prop_table(self):
        """(Re)construye la tabla de propiedades mostrando solo las
        seleccionadas, en el orden del catalogo. Solo arma etiquetas y celdas
        vacias; los valores los rellena _render."""
        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        GRIS = QColor(GRAY_RES); BLANCO_P = QColor(WHITE)
        self.tbl_prop.setRowCount(len(sel))
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            self.tbl_prop.setRowHeight(r, ROW_H)
            unidad = f" [{_u.u(mag)}]" if mag else ""
            it = QTableWidgetItem(f"{_i18n.t(base)}{unidad}:")
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS))
            self.tbl_prop.setItem(r, 0, it)
            for c in (1, 2):
                cc = QTableWidgetItem("")
                cc.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cc.setBackground(QBrush(BLANCO_P))
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
        for tbl, nrows in [(self.tbl, NC+1),
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
            self.lbl_estado.setText(_i18n.t("No se encontro punto de saturacion"))
            self.lbl_res_val.setText(""); self.lbl_res2_val.setText("")
            self.last_result = None
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

        self.lbl_estado.setText(_i18n.t("Convergencia exitosa."))

        # Llenar tabla de composiciones
        x=res.get('x',[0]*NC); y=res.get('y',[0]*NC)
        sx=sum(x); sy=sum(y)
        for i in range(NC):
            self.tbl.item(i,1).setText(f"{y[i]:.4f}")
            self.tbl.item(i,2).setText(f"{x[i]:.4f}")
            self.tbl.item(i,1).setBackground(QBrush(QColor(WHITE)))
            self.tbl.item(i,2).setBackground(QBrush(QColor(WHITE)))
            self.tbl.item(i,1).setForeground(QBrush(QColor(TEXT_RES)))
            self.tbl.item(i,2).setForeground(QBrush(QColor(TEXT_RES)))
        self.tbl.item(NC,1).setText(f"{sy:.4f}")
        self.tbl.item(NC,2).setText(f"{sx:.4f}")

        # Llenar panel de propiedades (solo las seleccionadas, en orden)
        p=res.get('props',{})
        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            unidad = f" [{_u.u(mag)}]" if mag else ""
            it_lbl = self.tbl_prop.item(r, 0)
            if it_lbl is not None:
                it_lbl.setText(f"{_i18n.t(base)}{unidad}:")
            vv = _conv_prop(conv, p.get(kv))
            vl = _conv_prop(conv, p.get(kl))
            fmt = f"{{:.{dec}f}}"
            self.tbl_prop.item(r,1).setText(fmt.format(vv) if vv is not None else "")
            self.tbl_prop.item(r,2).setText(fmt.format(vl) if vl is not None else "")
            self.tbl_prop.item(r,1).setForeground(QBrush(QColor(TEXT_RES)))
            self.tbl_prop.item(r,2).setForeground(QBrush(QColor(TEXT_RES)))

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

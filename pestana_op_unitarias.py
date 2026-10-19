"""
pestana_op_unitarias.py — Operaciones unitarias (estilo PVTsim).

Ventana de ingreso de datos: tipo de operación (compresor, expansor,
enfriador, calentador, bomba, válvula o separador), condiciones de entrada
(flujo, temperatura, presión), especificación de salida según la operación,
modelo (EOS, densidad, corrección de volumen) y la cromatografía.  El cálculo
corre con la ventana abierta; solo si hay resultado se abre la ventana de
resultados.

Ventana de resultados: resumen entrada/salida y resultados de la operación
(trabajo, capacidad, head, X/Y de Schultz, …), propiedades de las fases y
composiciones de las fases, como las hojas de salida de PVTsim.
"""
from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QLabel, QPushButton, QLineEdit,
                             QComboBox, QRadioButton, QButtonGroup,
                             QTableWidget, QTableWidgetItem, QStackedWidget,
                             QFrame, QAbstractItemView, QFileDialog,
                             QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEventLoop, QTimer
from PyQt6.QtGui import QBrush, QColor

import idioma as _i18n
import unidades as _u
import dialogos
import op_unitarias as ou
from eos import NC, NOMBRES, PM as PM_COMP, componente_etiqueta

WHITE = "#FFFFFF"; GRAY_TIT = "#A8A8A8"; GRAY_LBL = "#D0D0D0"
GRAY_RES = "#E8E8E8"; GRAY_EMPTY = "#F6F6F6"
BORDER = "#888888"; TEXT = "#000000"; TEXT_RES = "#000080"; SEL_BG = "#DCDCDC"
FONT_F = "Arial Narrow"; FS = 10; ROW_H = 22
AVISO = "#8B0000"

_UR_VAL = Qt.ItemDataRole.UserRole + 10
_UR_TXT = Qt.ItemDataRole.UserRole + 11

LB_KG = 0.45359237
# Unidades de la hoja de composición (iguales para todas las operaciones)
UNID_COMP = [('xm', "Fracción molar"), ('pm', "Porcentaje molar"),
             ('xw', "Fracción másica"), ('pw', "Porcentaje másico"),
             ('nm', "Flujo molar"), ('nw', "Flujo másico")]
W_CAMPO = 232        # ancho común de campos y listas de la ventana de ingreso


# ── Unidades propias del módulo ─────────────────────────────────────────
def _field():
    return _u.sistema() == 'FIELD'


def u_mol():  return 'lbmol/h' if _field() else 'kgmol/h'
def u_mas():  return 'lb/h' if _field() else 'kg/h'
def u_vol():  return 'ft³/h' if _field() else 'm³/h'
def u_pot():  return 'hp' if _field() else 'kW'
def u_head(): return 'ft' if _field() else 'm'


def u_calor():
    return {'FIELD': 'Btu/h', 'SI': 'kW'}.get(_u.sistema(), 'kcal/h')


def mol_desde(n):  return n if _field() else n*LB_KG
def mas_desde(m):  return m if _field() else m*LB_KG
def vol_desde(v):  return v if _field() else v*0.028316846592
def head_desde(h): return h if _field() else h*0.3048
def head_a(v):     return v if _field() else v/0.3048


def pot_desde(q):
    return q/ou.BTUH_HP if _field() else q/ou.BTUH_KW


def pot_a(v):
    return v*ou.BTUH_HP if _field() else v*ou.BTUH_KW


def calor_desde(q):
    s = _u.sistema()
    if s == 'FIELD':
        return q
    if s == 'SI':
        return q/ou.BTUH_KW
    return q*0.251995761


def dT_desde(dTF):  return _u.dt_desde_F(dTF)
def dT_a(v):        return v if _field() else v*1.8
def dP_desde(dP):   return _u.p_desde_psia(dP)
def dP_a(v):        return _u.p_a_psia(v)


# Unidades de flujo de entrada → lbmol/h
FLUJOS = ['lbmol/h', 'kgmol/h', 'lb/h', 'kg/h', 'MMscfd', 'Sm³/d']
SM3_KMOL = 23.6446          # Sm³/kmol a 15 °C y 101.325 kPa (gas ideal)


def flujo_a_lbmolh(v, unidad, PM):
    if unidad == 'lbmol/h':
        return v
    if unidad == 'kgmol/h':
        return v/LB_KG
    if unidad == 'lb/h':
        return v/PM
    if unidad == 'kg/h':
        return v/LB_KG/PM
    if unidad == 'Sm³/d':
        return v/24.0/SM3_KMOL/LB_KG
    return v*1.0e6/ou.SCF_LBMOL/24.0          # MMscfd


def u_std():
    return 'MMscfd' if _field() else 'Sm³/d'


def std_desde(n):
    """Caudal de gas estándar de n lbmol/h: MMscfd (60 °F, 14.696 psia) o
    Sm³/d (15 °C, 101.325 kPa), ambos como gas ideal."""
    if _field():
        return n*ou.SCF_LBMOL*24.0/1.0e6
    return n*LB_KG*SM3_KMOL*24.0


# ── Especificaciones de salida por operación (como PVTsim) ──────────────
# (código, texto, [(clave, etiqueta, magnitud, defecto)]).  Magnitudes:
# 'P' presión, 'dP' diferencia de presión, 'T' temperatura, 'dT' diferencia
# de temperatura, 'eta' eficiencia, 'pot' potencia, 'head' head.
_ETA = ('eta', "Eficiencia isentrópica", 'eta', "1.000")
SPECS = {
    ('compresor', 'clasico'): [
        ('dP_eta', "Incremento de presión", [('dP', "Incremento de presión", 'dP', ""), _ETA]),
        ('P_eta', "Presión de salida", [('P2', "Presión de salida", 'P', ""), _ETA]),
    ],
    ('compresor', 'pace'): [
        ('P_eta', "Presión de salida y eficiencia",
         [('P2', "Presión de salida", 'P', ""), ('eta', "Eficiencia", 'eta', "1.000")]),
        ('W_eta', "Trabajo del compresor y eficiencia",
         [('W', "Trabajo del compresor", 'pot', ""), ('eta', "Eficiencia", 'eta', "1.000")]),
        ('H_eta', "Head y eficiencia",
         [('head', "Head", 'head', ""), ('eta', "Eficiencia", 'eta', "1.000")]),
        ('P_T', "Presión y temperatura de salida",
         [('P2', "Presión de salida", 'P', ""), ('T2', "Temperatura de salida", 'T', "")]),
    ],
    ('expansor', None): [
        ('dP_eta', "Caída de presión", [('dP', "Caída de presión", 'dP', ""), _ETA]),
        ('P_eta', "Presión de salida", [('P2', "Presión de salida", 'P', ""), _ETA]),
    ],
    ('enfriador', None): [
        ('dT_dP', "Disminución de temperatura",
         [('dT', "Disminución de temperatura", 'dT', ""), ('dPc', "Caída de presión", 'dP', "0")]),
        ('T_dP', "Temperatura de salida",
         [('T2', "Temperatura de salida", 'T', ""), ('dPc', "Caída de presión", 'dP', "0")]),
    ],
    ('calentador', None): [
        ('dT_dP', "Aumento de temperatura",
         [('dT', "Aumento de temperatura", 'dT', ""), ('dPc', "Caída de presión", 'dP', "0")]),
        ('T_dP', "Temperatura de salida",
         [('T2', "Temperatura de salida", 'T', ""), ('dPc', "Caída de presión", 'dP', "0")]),
    ],
    ('bomba', None): [
        ('dP_eta', "Incremento de presión",
         [('dP', "Incremento de presión", 'dP', ""), ('eta', "Eficiencia", 'eta', "1.000")]),
        ('P_eta', "Presión de salida",
         [('P2', "Presión de salida", 'P', ""), ('eta', "Eficiencia", 'eta', "1.000")]),
    ],
    ('valvula', None): [
        ('dP', "Caída de presión", [('dP', "Caída de presión", 'dP', "")]),
        ('P', "Presión de salida", [('P2', "Presión de salida", 'P', "")]),
    ],
    ('separador', None): [],
}


def _unidad_mag(mag):
    if mag in ('P', 'dP'):
        return _u.u('P')
    if mag in ('T', 'dT'):
        return _u.u('T')
    if mag == 'pot':
        return u_pot()
    if mag == 'head':
        return u_head()
    return ""


def _a_float(t):
    try:
        return float(str(t).strip().replace(',', '.'))
    except Exception:
        return None


# ── Celdas y estilos ────────────────────────────────────────────────────
def _cell(text, bg=WHITE, color=TEXT, align=None, editable=False):
    it = QTableWidgetItem(str(text))
    it.setTextAlignment(align or (Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter))
    it.setBackground(QBrush(QColor(bg)))
    it.setForeground(QBrush(QColor(color)))
    if not editable:
        it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return it


def _set_comp(item, v):
    v = float(v); t = f"{v:.4f}"
    item.setData(_UR_VAL, v); item.setText(t); item.setData(_UR_TXT, t)


def _get_comp(item):
    if item is None:
        return 0.0
    t = item.text(); v = item.data(_UR_VAL)
    if v is not None and item.data(_UR_TXT) == t:
        return float(v)
    return _a_float(t) or 0.0


def _titulo(text):
    l = QLabel(text)
    l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    l.setFixedHeight(22)
    l.setStyleSheet(f'background:{GRAY_TIT}; color:{TEXT}; font-family:"{FONT_F}";'
                    f' font-size:{FS}pt; padding:0px 6px; border:1px solid {BORDER};')
    return l


def _seccion(text):
    l = QLabel(text)
    l.setFixedHeight(22)
    l.setStyleSheet(f'background:{GRAY_LBL}; color:{TEXT}; font-family:"{FONT_F}";'
                    f' font-size:{FS}pt; padding:0px 6px; border:1px solid {BORDER};')
    return l


TXT_QSS = f'font-family:"{FONT_F}";font-size:{FS}pt;color:{TEXT};background:transparent;'
LBL_QSS = (f'background:{GRAY_LBL};border:1px solid {BORDER};'
           f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
ED_QSS = (f'QLineEdit {{ background:{WHITE};border:1px solid {BORDER};'
          f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 4px; }}'
          f'QLineEdit:disabled {{ background:{GRAY_EMPTY}; color:#808080; }}')
BTN_QSS = (f'QPushButton {{ background:{GRAY_LBL};border:2px outset {BORDER};'
           f'font-family:"{FONT_F}";font-size:{FS}pt; padding:0px 8px; }}'
           f'QPushButton:checked {{ border:2px inset {BORDER}; background:#C4C4C4; }}'
           f'QPushButton:disabled {{ color:#808080; }}')
RADIO_QSS = (f'QRadioButton {{ font-family:"{FONT_F}"; font-size:{FS}pt;'
             f' color:{TEXT}; background:transparent; spacing:6px; }}')
# Rejilla plana de 1 px dibujada por el delegado (la rejilla nativa se ve
# gruesa a DPI fraccional): la tabla solo aporta el borde superior/izquierdo.
TBL_QSS = (f'QTableWidget {{ background:{WHITE};'
           f' border-top:1px solid {BORDER}; border-left:1px solid {BORDER};'
           f' font-family:"{FONT_F}"; font-size:{FS}pt;'
           f' selection-background-color:{SEL_BG}; selection-color:{TEXT}; }}'
           f'QTableWidget::item {{ padding:2px 6px; }}')


def _tabla(filas, cols):
    t = QTableWidget(filas, cols)
    t.horizontalHeader().hide(); t.verticalHeader().hide()
    t.setShowGrid(False); t.setStyleSheet(TBL_QSS)
    from pestana_saturacion import GridDelegate
    t.setItemDelegate(GridDelegate(BORDER, t))
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    t.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
    return t


def _ajustar(t):
    w = sum(t.columnWidth(c) for c in range(t.columnCount())) + 1
    h = sum(t.rowHeight(r) for r in range(t.rowCount())) + 1
    t.setFixedSize(w, h)


def _fmt(v, dec):
    if v is None:
        return ""
    try:
        return f"{float(v):.{dec}f}"
    except Exception:
        return str(v)


# ════════════════════════════════════════════════════════════════════════
# Hilo de cálculo
# ════════════════════════════════════════════════════════════════════════
class OUWorker(QThread):
    done = pyqtSignal(dict)
    error = pyqtSignal(str)
    aviso = pyqtSignal(str)

    def __init__(self, spec):
        super().__init__()
        self.spec = spec

    def run(self):
        import flash_ph as _fph
        try:
            self.done.emit(ou.ejecutar(self.spec))
        except (ou.SinSolucionOU, _fph.SinSolucion) as ex:
            self.aviso.emit(str(ex))
        except Exception as ex:
            self.error.emit(str(ex))


# ════════════════════════════════════════════════════════════════════════
# Ventana de ingreso de datos
# ════════════════════════════════════════════════════════════════════════
class DialogoOU(QDialog):
    """fuentes: [(clave, nombre)] de composiciones que se pueden cargar;
    datos_fuente(clave) → (nombre, z, kij, eos, metodo); activos: índices de
    los componentes activos (incluida el agua, índice NC, si está activa);
    previo: datos del último cálculo (para reabrir con ellos); h: helpers
    de la ventana principal (estilo de combos, EOS, registro de edición)."""

    def __init__(self, parent, fuentes, datos_fuente, activos, previo, h):
        super().__init__(parent)
        self.fuentes = fuentes; self.datos_fuente = datos_fuente
        self.act = [i for i in sorted(set(activos)) if i <= NC]
        self.h = h
        self.resultado = None; self.entrada = None
        self.setWindowTitle(_i18n.t("Operaciones unitarias"))
        self.setStyleSheet('QDialog { background:#e0e0e0; }')
        root = QVBoxLayout(self); root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)
        root.addWidget(_titulo(_i18n.t("ThermoPhase — Ingreso de datos")))
        cols = QHBoxLayout(); cols.setSpacing(16)

        # ── Columna izquierda: operación, entrada, salida y modelo ──────
        c1 = QVBoxLayout(); c1.setSpacing(4)
        gop = QGridLayout(); gop.setSpacing(4)
        self.cmb_op = QComboBox(); self.cmb_op.setFixedSize(W_CAMPO, 22)
        h['estilo_combo'](self.cmb_op)
        for op in ou.OPERACIONES:
            self.cmb_op.addItem(_i18n.t(ou.NOMBRES[op]), op)
        gop.addWidget(self._etq("Operación unitaria:"), 0, 0); gop.addWidget(self.cmb_op, 0, 1)
        c1.addLayout(gop)

        c1.addSpacing(4)
        c1.addWidget(self._lbl_txt("Entrada:"))
        ge = QGridLayout(); ge.setSpacing(4)
        self.ed_flujo = self._campo(W_CAMPO - 80)
        self.cmb_flujo = QComboBox(); self.cmb_flujo.setFixedSize(76, 22)
        h['estilo_combo'](self.cmb_flujo); self.cmb_flujo.addItems(FLUJOS)
        fl = QHBoxLayout(); fl.setSpacing(4); fl.addWidget(self.ed_flujo); fl.addWidget(self.cmb_flujo)
        ge.addWidget(self._etq("Flujo:"), 0, 0); ge.addLayout(fl, 0, 1)
        self.lbl_T1 = self._etq("Temperatura:"); self.ed_T1 = self._campo(W_CAMPO - 80)
        self.cmb_T = QComboBox(); self.cmb_T.setFixedSize(76, 22)
        h['estilo_combo'](self.cmb_T); self.cmb_T.addItems([_u.u('T'), _u.u_abs()])
        self._T_abs = False
        self.cmb_T.currentIndexChanged.connect(self._on_unidad_T)
        ft = QHBoxLayout(); ft.setSpacing(4); ft.addWidget(self.ed_T1); ft.addWidget(self.cmb_T)
        self.lbl_P1 = self._etq(""); self.ed_P1 = self._campo()
        ge.addWidget(self.lbl_T1, 1, 0); ge.addLayout(ft, 1, 1)
        ge.addWidget(self.lbl_P1, 2, 0); ge.addWidget(self.ed_P1, 2, 1)
        self.w_metodo = QComboBox(); self.w_metodo.setFixedSize(W_CAMPO, 22)
        h['estilo_combo'](self.w_metodo)
        self.w_metodo.addItem(_i18n.t("Clásico"), 'clasico')
        self.w_metodo.addItem(_i18n.t("Politrópico"), 'pace')
        self.lbl_met = self._etq("Cálculo del compresor:")
        ge.addWidget(self.lbl_met, 3, 0); ge.addWidget(self.w_metodo, 3, 1)
        c1.addLayout(ge)

        c1.addSpacing(4)
        self.lbl_sal = self._lbl_txt("Salida:")
        c1.addWidget(self.lbl_sal)
        gs = QGridLayout(); gs.setSpacing(4)
        self.cmb_spec = QComboBox(); self.cmb_spec.setFixedSize(W_CAMPO, 22)
        h['estilo_combo'](self.cmb_spec)
        self.lbl_spec = self._etq("Especificación:")
        gs.addWidget(self.lbl_spec, 0, 0); gs.addWidget(self.cmb_spec, 0, 1)
        self.lbl_x = [self._etq(""), self._etq("")]
        self.ed_x = [self._campo(), self._campo()]
        self.cmb_Tx = []
        for k in range(2):
            c = QComboBox(); c.setFixedSize(76, 22); h['estilo_combo'](c)
            c.addItems([_u.u('T'), _u.u_abs()]); c.hide()
            c.currentIndexChanged.connect(self._on_unidad_T)
            self.cmb_Tx.append(c)
            fx = QHBoxLayout(); fx.setSpacing(4); fx.addWidget(self.ed_x[k]); fx.addWidget(c)
            fx.addStretch(1)
            gs.addWidget(self.lbl_x[k], k + 1, 0); gs.addLayout(fx, k + 1, 1)
        self.lbl_sep = QLabel(_i18n.t(
            "El separador se simula como un flash PT a las condiciones de entrada."))
        self.lbl_sep.setStyleSheet(TXT_QSS); self.lbl_sep.setWordWrap(True)
        gs.addWidget(self.lbl_sep, 3, 0, 1, 2)
        c1.addLayout(gs)

        c1.addSpacing(4)
        c1.addWidget(self._lbl_txt("Modelo:"))
        gm = QGridLayout(); gm.setSpacing(4)
        self.c_eos = self._combo(h['eos_items'], 0)
        self.c_dens = self._combo(["COSTALD", "EOS"], 0)
        self.c_vol = self._combo(["Ninguna", "Peneloux"], 0)
        gm.addWidget(self._etq("Ecuación de estado:"), 0, 0); gm.addWidget(self.c_eos, 0, 1)
        gm.addWidget(self._etq("Densidad:"), 1, 0); gm.addWidget(self.c_dens, 1, 1)
        gm.addWidget(self._etq("Corrección de volumen:"), 2, 0); gm.addWidget(self.c_vol, 2, 1)
        self._dens_prev = "COSTALD"
        self.c_vol.currentIndexChanged.connect(self._on_vol)
        c1.addLayout(gm)
        c1.addStretch(1)
        cols.addLayout(c1)

        # ── Columna derecha: cromatografía ─────────────────────────────
        c2 = QVBoxLayout(); c2.setSpacing(4)
        fc = QHBoxLayout(); fc.setSpacing(6)
        fc.addWidget(self._lbl_txt("Cromatografía:")); fc.addStretch()
        fc.addWidget(self._lbl_txt("Cargar de:"))
        self.cmb_fuente = QComboBox(); self.cmb_fuente.setFixedSize(170, 22)
        h['estilo_combo'](self.cmb_fuente)
        self.cmb_fuente.addItem("", None)
        for k, nom in fuentes:
            self.cmb_fuente.addItem(nom, k)
        fc.addWidget(self.cmb_fuente)
        c2.addLayout(fc)
        tc = self.tc = _tabla(len(self.act) + 2, 2)
        tc.setColumnWidth(0, 210); tc.setColumnWidth(1, 110)
        tc.setItem(0, 0, _cell(_i18n.t("Componente"), bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        tc.setItem(0, 1, _cell(_i18n.t("Composición"), bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        for r, i in enumerate(self.act, 1):
            nom = NOMBRES[i] if i < NC else componente_etiqueta(NC)
            tc.setItem(r, 0, _cell(_i18n.t(nom), bg=GRAY_LBL))
            tc.setItem(r, 1, _cell("", editable=True))
        self.rs = len(self.act) + 1
        tc.setItem(self.rs, 0, _cell(_i18n.t("Sumatorias:"), bg=GRAY_LBL))
        tc.setItem(self.rs, 1, _cell("", bg=GRAY_EMPTY, color=TEXT_RES))
        for r in range(self.rs + 1):
            tc.setRowHeight(r, ROW_H)
        _ajustar(tc)
        c2.addWidget(tc, 0, Qt.AlignmentFlag.AlignRight)
        c2.addStretch(1)
        cols.addLayout(c2)
        root.addLayout(cols)
        try:
            h['registrar'](tc)
        except Exception:
            pass
        tc.itemChanged.connect(self._on_cambio)

        # ── Botones ─────────────────────────────────────────────────────
        fila = QHBoxLayout(); fila.setSpacing(8)
        self.b_norm = QPushButton(_i18n.t("Normalizar"))
        self.b_ok = QPushButton(_i18n.t("Calcular")); self.b_can = QPushButton(_i18n.t("Cancelar"))
        for b in (self.b_norm, self.b_ok, self.b_can):
            b.setFixedHeight(26); b.setMinimumWidth(84); b.setStyleSheet(BTN_QSS)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        fila.addWidget(self.b_norm); fila.addStretch(); fila.addWidget(self.b_ok); fila.addWidget(self.b_can)
        root.addLayout(fila)
        self.b_norm.clicked.connect(self._normalizar)
        self.b_can.clicked.connect(self.reject)
        self.b_ok.clicked.connect(self._calcular)

        # ── Señales y valores iniciales ─────────────────────────────────
        self.cmb_op.currentIndexChanged.connect(lambda _i: self._on_op())
        self.w_metodo.currentIndexChanged.connect(lambda _i: self._on_op())
        self.cmb_spec.currentIndexChanged.connect(lambda _i: self._on_spec())
        self.cmb_fuente.activated.connect(lambda _i: self._cargar_fuente(self.cmb_fuente.currentData()))
        self._valores = {}          # valores escritos por clave de campo
        self._aplicar_previo(previo)
        self.adjustSize(); self.setFixedSize(self.sizeHint())
        self._tam_fijo = self.size()

    # ── helpers de construcción ─────────────────────────────────────────
    def _lbl_txt(self, t):
        l = QLabel(_i18n.t(t)); l.setStyleSheet(TXT_QSS); return l

    def _etq(self, t):
        l = QLabel(_i18n.t(t) if t else ""); l.setStyleSheet(LBL_QSS); l.setFixedHeight(22)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        l.setMinimumWidth(170)
        return l

    def _campo(self, w=None):
        w = W_CAMPO if w is None else w
        e = QLineEdit(); e.setStyleSheet(ED_QSS); e.setFixedSize(w, 22)
        e.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return e

    def _combo(self, items, idx):
        c = QComboBox(); c.setFixedSize(W_CAMPO, 22); self.h['estilo_combo'](c)
        c.addItems([_i18n.t(x) for x in items]); c.setCurrentIndex(max(0, idx))
        return c

    def _on_vol(self, i):
        if i == 1:
            if self.c_dens.isEnabled():
                self._dens_prev = self.c_dens.currentText()
            self.c_dens.setCurrentIndex(1); self.c_dens.setEnabled(False)
        else:
            self.c_dens.setEnabled(True)
            self.c_dens.setCurrentIndex(0 if self._dens_prev == "COSTALD" else 1)

    # ── operación y especificaciones ────────────────────────────────────
    def op(self):
        return self.cmb_op.currentData() or 'compresor'

    def metodo(self):
        return self.w_metodo.currentData() or 'clasico'

    def _specs(self):
        op = self.op()
        return SPECS[(op, self.metodo() if op == 'compresor' else None)]

    def _guardar_campos(self):
        sp = getattr(self, '_spec_act', None)
        if sp is None:
            return
        for k, (key, *_r) in enumerate(sp[2]):
            self._valores[key] = self.ed_x[k].text()

    def _on_op(self):
        self._guardar_campos()
        op = self.op()
        es_comp = op == 'compresor'
        self.lbl_met.setVisible(es_comp); self.w_metodo.setVisible(es_comp)
        specs = self._specs()
        prev = self.cmb_spec.currentData()
        self.cmb_spec.blockSignals(True); self.cmb_spec.clear()
        for cod, txt, _f in specs:
            self.cmb_spec.addItem(_i18n.t(txt), cod)
        codigos = [s[0] for s in specs]
        if prev in codigos:
            self.cmb_spec.setCurrentIndex(codigos.index(prev))
        self.cmb_spec.blockSignals(False)
        sep = op == 'separador'
        self.lbl_spec.setVisible(not sep); self.cmb_spec.setVisible(not sep)
        self.lbl_sep.setVisible(sep)
        self._spec_act = None
        self._on_spec()

    # ── temperatura absoluta o relativa ──────────────────────────────────
    def _T_a_R(self, v, absoluta=None):
        absoluta = self._T_abs if absoluta is None else absoluta
        return _u.R_desde_abs(v) if absoluta else _u.t_a_R(v)

    def _R_a_T(self, R, absoluta=None):
        absoluta = self._T_abs if absoluta is None else absoluta
        return _u.abs_desde_R(R) if absoluta else _u.t_desde_R(R)

    def _on_unidad_T(self, i):
        """Cambia la unidad de todas las temperaturas de la ventana (entrada
        y salida) y convierte los valores ya escritos."""
        viejo = self._T_abs; nuevo = (i == 1)
        # todas las listas de temperatura muestran la misma unidad
        for c in [self.cmb_T] + list(getattr(self, 'cmb_Tx', [])):
            if c.currentIndex() != i:
                c.blockSignals(True); c.setCurrentIndex(i); c.blockSignals(False)
        if viejo == nuevo:
            return
        self._guardar_campos()
        def conv(txt):
            v = _a_float(txt)
            if v is None:
                return txt
            return f"{self._R_a_T(self._T_a_R(v, viejo), nuevo):.2f}"
        self.ed_T1.setText(conv(self.ed_T1.text()))
        if 'T2' in self._valores:
            self._valores['T2'] = conv(self._valores['T2'])
        self._T_abs = nuevo
        self._spec_act = None
        self._on_spec()

    def _on_spec(self):
        self._guardar_campos()
        specs = self._specs()
        idx = self.cmb_spec.currentIndex()
        sp = specs[idx] if 0 <= idx < len(specs) else None
        self._spec_act = sp
        campos = sp[2] if sp else []
        for k in range(2):
            vis = k < len(campos)
            self.lbl_x[k].setVisible(vis); self.ed_x[k].setVisible(vis)
            es_T = vis and campos[k][2] == 'T'
            self.cmb_Tx[k].setVisible(es_T)
            self.ed_x[k].setFixedWidth(W_CAMPO - 80 if es_T else W_CAMPO)
            if vis:
                key, etq, mag, defecto = campos[k]
                un = "" if mag == 'T' else _unidad_mag(mag)
                self.ed_x[k].setText(self._valores.get(key, defecto))
                self.lbl_x[k].setText(f"{_i18n.t(etq)}" + (f" ({un}):" if un else ":"))
        # La ventana conserva su ANCHO al mostrar u ocultar la lista de unidad
        # de temperatura, pero su ALTO se ajusta a las filas visibles de la
        # operación elegida (sin huecos ni traslapes).
        if getattr(self, '_tam_fijo', None) is not None:
            lay = self.layout()
            lay.invalidate(); lay.activate()
            w = self._tam_fijo.width()
            alto = lay.totalHeightForWidth(w) if lay.hasHeightForWidth() else lay.sizeHint().height()
            self.setFixedSize(w, max(alto, lay.totalMinimumSize().height()))

    # ── composición ─────────────────────────────────────────────────────
    def _crudo(self):
        z = [0.0]*(NC + 1)
        for r, i in enumerate(self.act, 1):
            z[i] = _get_comp(self.tc.item(r, 1))
        return z

    def _upd_suma(self):
        self.tc.blockSignals(True)
        self.tc.item(self.rs, 1).setText(f"{sum(self._crudo()):.4f}")
        self.tc.blockSignals(False)

    def _on_cambio(self, it):
        if it.column() != 1 or it.row() in (0, self.rs):
            return
        v = _a_float(it.text())
        self.tc.blockSignals(True)
        if v is not None and it.data(_UR_TXT) != it.text():
            _set_comp(it, v)
        self.tc.blockSignals(False)
        self._upd_suma()

    def _set_z(self, z):
        self.tc.blockSignals(True)
        for r, i in enumerate(self.act, 1):
            v = z[i] if i < len(z) else 0.0
            it = self.tc.item(r, 1)
            if v:
                _set_comp(it, v)
            else:
                it.setText(""); it.setData(_UR_VAL, None)
        self.tc.blockSignals(False)
        self._upd_suma()

    def _normalizar(self):
        z = self._crudo(); s = sum(z)
        if s <= 0:
            return
        base = 100.0 if abs(s - 100.0) < abs(s - 1.0) else 1.0
        self._set_z([v/s*base for v in z])

    def _cargar_fuente(self, clave):
        if clave is None:
            return
        d = self.datos_fuente(clave)
        if d is None:
            return
        nombre, z, kij, eos_c, met = d
        self._set_z(z)
        self.c_eos.setCurrentIndex(self.h['eos_idx'](eos_c))
        if met == 'Peneloux':
            self.c_vol.setCurrentIndex(1)
        else:
            self.c_vol.setCurrentIndex(0)
            self.c_dens.setCurrentIndex(0 if met == 'COSTALD' else 1)
        self._kij_fuente = (eos_c, kij)

    # ── valores iniciales ───────────────────────────────────────────────
    def _aplicar_previo(self, p):
        self.lbl_P1.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
        self._kij_fuente = None
        if not p:
            self.cmb_op.setCurrentIndex(0)
            self.ed_flujo.setText("100")
            self.cmb_flujo.setCurrentText(u_mol())
            if self.fuentes:
                self.cmb_fuente.setCurrentIndex(1)
                self._cargar_fuente(self.fuentes[0][0])
            self._on_op()
            return
        self.cmb_op.blockSignals(True); self.w_metodo.blockSignals(True)
        ops = list(ou.OPERACIONES)
        self.cmb_op.setCurrentIndex(ops.index(p['op']) if p.get('op') in ops else 0)
        self.w_metodo.setCurrentIndex(1 if p.get('metodo') == 'pace' else 0)
        self.cmb_op.blockSignals(False); self.w_metodo.blockSignals(False)
        self.ed_flujo.setText(p.get('flujo_txt', "100"))
        self.cmb_flujo.setCurrentText(p.get('flujo_u', u_mol()))
        for c in [self.cmb_T] + self.cmb_Tx:
            c.blockSignals(True); c.setCurrentIndex(1 if p.get('T_abs') else 0)
            c.blockSignals(False)
        self._T_abs = bool(p.get('T_abs'))
        T1, P1 = p.get('T1'), p.get('P1')
        if T1:
            self.ed_T1.setText(f"{self._R_a_T(T1):.2f}")
        if P1:
            self.ed_P1.setText(f"{_u.p_desde_psia(P1):.2f}")
        self._valores = dict(p.get('valores') or {})
        self.c_eos.setCurrentIndex(p.get('i_eos', 0))
        self.c_vol.setCurrentIndex(p.get('i_vol', 0))
        if p.get('i_vol', 0) == 0:
            self.c_dens.setCurrentIndex(p.get('i_dens', 0))
        self._kij_fuente = p.get('kij_fuente')
        self._set_z(p.get('z_crudo') or [])
        self._on_op()
        specs = [s[0] for s in self._specs()]
        if p.get('spec') in specs:
            self.cmb_spec.setCurrentIndex(specs.index(p['spec']))

    # ── cálculo ─────────────────────────────────────────────────────────
    def _leer(self):
        """Valida y arma la especificación del motor; None si hay error."""
        adv = lambda m: (dialogos.advertencia(self, _i18n.t(m)), None)[1]
        op = self.op()
        zc = self._crudo(); s = sum(zc)
        if s <= 1e-12 or sum(zc[:NC]) <= 1e-12:
            return adv("Ingrese la cromatografía de la corriente.")
        if abs(s - 1.0) > 1e-3 and abs(s - 100.0) > 1e-1:
            return adv("La composicion debe sumar 1 (fraccion molar) o 100 (porcentaje molar)")
        z = [v/s for v in zc]
        vf = _a_float(self.ed_flujo.text())
        vT = _a_float(self.ed_T1.text()); vP = _a_float(self.ed_P1.text())
        if vf is None or vf <= 0:
            return adv("Ingrese un flujo mayor que cero.")
        if vT is None or vP is None:
            return adv("Ingrese la presion y la temperatura.")
        T1 = self._T_a_R(vT); P1 = _u.p_a_psia(vP)
        if T1 <= 0 or P1 <= 0:
            return adv("La presión y la temperatura absoluta deben ser mayores que cero.")
        import eos as _e
        PMz = sum(z[i]*PM_COMP[i] for i in range(NC)) + z[NC]*_e.prop_agua("PM")
        n = flujo_a_lbmolh(vf, self.cmb_flujo.currentText(), PMz)
        eos_c = self.h['eos_code'](self.c_eos.currentIndex())
        met = 'Peneloux' if self.c_vol.currentIndex() == 1 else self.c_dens.currentText()
        kf = self._kij_fuente
        kij = kf[1] if (kf and kf[0] == eos_c) else self.h['kij_base'](eos_c)
        ctx = dict(kij=kij, eos=eos_c, metodo=met, agua=bool(z[NC] > 1e-12))
        spec = dict(op=op, z=z, ctx=ctx, n=n, T1=T1, P1=P1)
        vals = {}
        sp = self._spec_act
        if sp is not None:
            for k, (key, etq, mag, _d) in enumerate(sp[2]):
                v = _a_float(self.ed_x[k].text())
                if v is None:
                    return adv("Complete los datos de salida.")
                vals[key] = v
        cod = sp[0] if sp else None
        if op == 'compresor':
            spec['metodo'] = self.metodo(); spec['salida'] = cod
        if 'eta' in vals:
            if not (0.0 < vals['eta'] <= 1.0):
                return adv("La eficiencia debe ser mayor que 0 y menor o igual a 1.")
            spec['eta'] = vals['eta']
        if 'dP' in vals:
            spec['P2'] = P1 + dP_a(vals['dP']) if op in ('compresor', 'bomba') else P1 - dP_a(vals['dP'])
        if 'P2' in vals:
            spec['P2'] = _u.p_a_psia(vals['P2'])
        if 'dT' in vals:
            spec['T2'] = T1 + dT_a(vals['dT']) if op == 'calentador' else T1 - dT_a(vals['dT'])
        if 'T2' in vals:
            spec['T2'] = self._T_a_R(vals['T2'])
        if 'dPc' in vals:
            spec['dP'] = dP_a(vals['dPc'])
        if 'W' in vals:
            spec['trabajo'] = pot_a(vals['W'])
        if 'head' in vals:
            spec['head'] = head_a(vals['head'])
        if spec.get('P2') is not None and spec['P2'] <= 0:
            return adv("La presión de salida debe ser mayor que cero.")
        self._guardar_campos()
        self.entrada = dict(op=op, metodo=self.metodo(), spec=cod,
                            flujo_txt=self.ed_flujo.text(), flujo_u=self.cmb_flujo.currentText(),
                            T1=T1, P1=P1, valores=dict(self._valores), T_abs=self._T_abs,
                            i_eos=self.c_eos.currentIndex(), i_vol=self.c_vol.currentIndex(),
                            i_dens=self.c_dens.currentIndex(), kij_fuente=self._kij_fuente,
                            z_crudo=zc, eos_nombre=self.c_eos.currentText(), metodo_dens=met)
        return spec

    def _calcular(self):
        spec = self._leer()
        if spec is None:
            return
        txt = self.b_ok.text()
        for b in (self.b_ok, self.b_can, self.b_norm):
            b.setEnabled(False)
        self.b_ok.setText(_i18n.t("Calculando..."))
        out = {}
        w = OUWorker(spec)
        lazo = QEventLoop()
        w.done.connect(lambda r: out.update(r=r))
        w.aviso.connect(lambda m: out.update(aviso=m))
        w.error.connect(lambda m: out.update(error=m))
        w.finished.connect(lazo.quit)
        w.start()
        lazo.exec()
        for b in (self.b_ok, self.b_can, self.b_norm):
            b.setEnabled(True)
        self.b_ok.setText(txt)
        if 'r' in out:
            self.resultado = out['r']
            self.accept()
        elif 'aviso' in out:
            dialogos.advertencia(self, _i18n.t(out['aviso']))
        else:
            dialogos.error(self, _i18n.t(out.get('error', "Error")))

    def reject(self):
        if not self.b_can.isEnabled():
            return                      # cálculo en curso
        super().reject()


# ════════════════════════════════════════════════════════════════════════
# Ventana de resultados
# ════════════════════════════════════════════════════════════════════════
class TabOperacionUnitaria(QWidget):
    def __init__(self, on_nuevo=None):
        super().__init__()
        self.on_nuevo = on_nuevo
        self.res = None; self.entrada = None
        self.setObjectName('ouTab')
        self.setStyleSheet(f'QWidget#ouTab {{ background:{GRAY_LBL}; }}')
        root = QVBoxLayout(self); root.setContentsMargins(13, 9, 13, 8); root.setSpacing(6)
        root.addWidget(_titulo("ThermoPhase — Operaciones unitarias"))

        # Barra: operación + botones de hoja (como PVTsim) + nuevo / exportar
        self.lbl_op = _seccion("")
        root.addWidget(self.lbl_op)
        bar = QHBoxLayout(); bar.setSpacing(6)
        self._bar = bar
        self.on_tamano = None
        self.W = 706          # ancho útil común de las tres hojas (set_ancho)
        lv = QLabel(_i18n.t("Mostrar:")); lv.setStyleSheet(TXT_QSS); bar.addWidget(lv)
        self.cmb_hoja = QComboBox(); self.cmb_hoja.setFixedSize(170, 22)
        for txt in ("Resultados", "Propiedades", "Composición"):
            self.cmb_hoja.addItem(_i18n.t(txt))
        self.cmb_hoja.currentIndexChanged.connect(self._hoja)
        bar.addWidget(self.cmb_hoja)
        bar.addStretch(1)
        self.btn_nuevo = QPushButton(_i18n.t("Nuevo cálculo"))
        self.btn_csv = QPushButton(_i18n.t("Exportar CSV"))
        for b in (self.btn_nuevo, self.btn_csv):
            b.setFixedHeight(24); b.setStyleSheet(BTN_QSS)
            b.setCursor(Qt.CursorShape.PointingHandCursor); bar.addWidget(b)
        self.btn_nuevo.clicked.connect(lambda: self.on_nuevo and self.on_nuevo())
        self.btn_csv.clicked.connect(self.exportar_csv)
        root.addLayout(bar)

        self.pila = QStackedWidget()
        root.addWidget(self.pila, 1)
        # Hoja 1: resultados — corrientes a la izquierda y resultados de la
        # operación a la derecha; advertencias debajo.
        p1 = QWidget(); v1 = QVBoxLayout(p1); v1.setContentsMargins(0, 0, 0, 0); v1.setSpacing(4)
        self.lbl_corr = _seccion(_i18n.t("Corrientes")); v1.addWidget(self.lbl_corr)
        self.tbl_corr = _tabla(1, 1); v1.addWidget(self.tbl_corr)
        v1.addSpacing(4)
        self.lbl_res_op = _seccion(""); v1.addWidget(self.lbl_res_op)
        self.tbl_op = _tabla(1, 1); v1.addWidget(self.tbl_op)
        self.lbl_aviso = QLabel(""); self.lbl_aviso.setWordWrap(True)
        self.lbl_aviso.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                                     f'color:{AVISO};background:transparent;')
        v1.addWidget(self.lbl_aviso)
        self.pila.addWidget(p1)
        # Hoja 2: propiedades de las fases (entrada y salida en una tabla)
        p2 = QWidget(); v2 = QVBoxLayout(p2); v2.setContentsMargins(0, 0, 0, 0); v2.setSpacing(4)
        v2.addWidget(_seccion(_i18n.t("Propiedades de las fases")))
        self.tbl_prop = _tabla(1, 1); v2.addWidget(self.tbl_prop)
        self.pila.addWidget(p2)
        # Hoja 3: composiciones de las fases (entrada y salida en una tabla)
        p3 = QWidget(); v3 = QVBoxLayout(p3); v3.setContentsMargins(0, 0, 0, 0); v3.setSpacing(4)
        f3 = QHBoxLayout(); f3.setSpacing(6)
        self.lbl_comp = _seccion(_i18n.t("Composición de las fases")); f3.addWidget(self.lbl_comp, 1)
        l3 = QLabel(_i18n.t("Unidades:")); l3.setStyleSheet(TXT_QSS); f3.addWidget(l3)
        self.cmb_ucomp = QComboBox(); self.cmb_ucomp.setFixedSize(170, 22)
        for k, txt in UNID_COMP:
            self.cmb_ucomp.addItem(_i18n.t(txt), k)
        self.cmb_ucomp.currentIndexChanged.connect(lambda _i: (self._render_comp(),
                                                               self._ajustar_ventana()))
        f3.addWidget(self.cmb_ucomp)
        v3.addLayout(f3)
        self.tbl_comp = _tabla(1, 1); v3.addWidget(self.tbl_comp)
        self.pila.addWidget(p3)
        self._hoja(0)

    def set_estilo_combo(self, fn):
        fn(self.cmb_ucomp); fn(self.cmb_hoja)

    def set_ancho(self, ancho_ventana):
        """Ancho fijo de la ventana (el de Equilibrio de fases): las tablas
        de las tres hojas se reparten ese mismo ancho."""
        m = self.layout().contentsMargins()
        self.W = int(ancho_ventana) - m.left() - m.right() - 2
        if self.res is not None:
            self._render(); self._ajustar_ventana()

    def _repartir(self, t, col0):
        """Columna 0 de ancho col0 y el resto del ancho W repartido por igual."""
        n = t.columnCount() - 1
        if n <= 0:
            return
        t.setColumnWidth(0, col0)
        resto = self.W - 1 - col0
        base = resto // n
        for c in range(1, n + 1):
            t.setColumnWidth(c, base + (resto - base*n if c == n else 0))

    def _hoja(self, i):
        self.pila.setCurrentIndex(i)
        if self.cmb_hoja.currentIndex() != i:
            self.cmb_hoja.blockSignals(True); self.cmb_hoja.setCurrentIndex(i)
            self.cmb_hoja.blockSignals(False)
        self._ajustar_ventana()

    def _ajustar_ventana(self):
        """Cada hoja con su propio tamaño: las hojas ocultas no cuentan para
        el tamaño de la pila y la ventana se ajusta a la hoja visible."""
        from PyQt6.QtWidgets import QSizePolicy as _SP
        for k in range(self.pila.count()):
            pg = self.pila.widget(k)
            if k == self.pila.currentIndex():
                pg.setSizePolicy(_SP.Policy.Preferred, _SP.Policy.Preferred)
            else:
                pg.setSizePolicy(_SP.Policy.Ignored, _SP.Policy.Ignored)
            pg.layout().activate()
        self.pila.updateGeometry()
        self.layout().activate()
        if self.on_tamano is not None:
            sz = self.sizeHint()
            m = self.layout().contentsMargins()
            self.on_tamano(self.W + 2 + m.left() + m.right(), sz.height() + 2)

    # ── datos ───────────────────────────────────────────────────────────
    def mostrar(self, res, entrada):
        self.res = res; self.entrada = entrada
        self._render()
        self._ajustar_ventana()

    def _corrientes(self):
        """[(grupo, subtítulo, estado o None, flujo molar lbmol/h)].  En el
        separador: alimentación (global) y salidas N°1 vapor, N°2 líquido y
        N°3 acuosa (con agua); una salida sin fase queda vacía."""
        r = self.res; n = r['n']
        if r['op'] == 'separador':
            e = r['entrada']
            out = [(_i18n.t("Alimentación"), _i18n.t("Global"), e, n)]
            for k, nom, sal in self._salidas_sep():
                f = e['fases'].get(k)
                sub = None
                if f:
                    sub = dict(T=e['T'], P=e['P'], H=f['H'], S=f['S'], PM=f['PM'],
                               rho=f['rho'], V=(f['PM']/f['rho'] if f['rho'] else None),
                               z=f['comp'], fases={k: dict(f, beta=1.0, beta_m=1.0)})
                out.append((sal, nom, sub, n*f['beta'] if f else 0.0))
            return out
        return [(_i18n.t("Entrada"), None, r['entrada'], n),
                (_i18n.t("Salida"), None, r['salida'], n)]

    def _salidas_sep(self):
        s_ = [('V', _i18n.t("Vapor"), _i18n.t("Salida N°1")),
              ('L', _i18n.t("Líquido"), _i18n.t("Salida N°2"))]
        if self._con_agua():
            s_.append(('W', _i18n.t("Acuosa"), _i18n.t("Salida N°3")))
        return s_

    @staticmethod
    def _agrupar(cols):
        """[(grupo, sub)] consecutivos → [(grupo, [subs])]."""
        g = []
        for grp, sub in cols:
            if g and g[-1][0] == grp:
                g[-1][1].append(sub)
            else:
                g.append((grp, [sub]))
        return g

    def _render(self):
        if self.res is None:
            return
        r = self.res
        met = {'pace': " — " + _i18n.t("Politrópico"), 'clasico': " — " + _i18n.t("Clásico")}.get(
            r['datos'].get('metodo'), "")
        self.lbl_op.setText(f"{_i18n.t(ou.NOMBRES[r['op']])}{met}")
        corr = self._corrientes()
        # Solo condiciones y flujos: las propiedades van en su propia hoja.
        filas = [("Presión", _u.u('P')), ("Temperatura", _u.u('T')),
                 ("Flujo molar", u_mol()), ("Flujo másico", u_mas()),
                 ("Flujo volumétrico estándar", u_std()),
                 ("Flujo volumétrico (a P y T)", u_vol())]
        t = self.tbl_corr
        dos = any(sub is not None for _g, sub, _e, _n in corr)   # separador
        h0 = 2 if dos else 1
        t.clearSpans(); t.clear()
        t.setRowCount(len(filas) + h0); t.setColumnCount(len(corr) + 1)
        if dos:
            self._encabezado(t, self._agrupar([(g, sb) for g, sb, _e, _n in corr]), 80, 230, "")
        else:
            t.setItem(0, 0, _cell("", bg=GRAY_LBL))
            for c, (tit, _sb, _e, _n) in enumerate(corr, 1):
                t.setItem(0, c, _cell(tit, bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        self._repartir(t, 230)
        for c, (tit, _sb, e, nn) in enumerate(corr, 1):
            if e is None:
                for k in range(len(filas)):
                    t.setItem(k + h0, c, _cell("", bg=GRAY_RES))
                continue
            vals = [_fmt(_u.p_desde_psia(e['P']), 2), _fmt(_u.t_desde_R(e['T']), 2),
                    _fmt(mol_desde(nn), 4), _fmt(mas_desde(nn*e['PM']), 2),
                    _fmt(std_desde(nn), 4 if _field() else 1),
                    _fmt(vol_desde(nn*e['V']) if e['V'] else None, 2)]
            for k, v in enumerate(vals):
                t.setItem(k + h0, c, _cell(v, color=TEXT_RES))
        for k, (base, un) in enumerate(filas, h0):
            t.setItem(k, 0, _cell(f"{_i18n.t(base)}" + (f" [{un}]:" if un else ":"), bg=GRAY_LBL))
        for k in range(t.rowCount()):
            t.setRowHeight(k, ROW_H)
        _ajustar(t)

        # Resultados de la operación
        filas_op = self._filas_operacion()
        self.lbl_res_op.setText(_i18n.t("Resultados de la operación") if filas_op else "")
        self.lbl_res_op.setVisible(bool(filas_op)); self.tbl_op.setVisible(bool(filas_op))
        t = self.tbl_op
        # dos pares etiqueta/valor por fila, repartidos en el ancho común
        nf = (len(filas_op) + 1)//2
        t.clear(); t.setRowCount(nf); t.setColumnCount(4)
        wv = 100; we = (self.W - 1 - 2*wv)//2
        for c, w_ in enumerate((we, wv, self.W - 1 - 2*wv - we, wv)):
            t.setColumnWidth(c, w_)
        for k in range(nf*2):
            fi, c = k % nf, 2*(k // nf)
            if k < len(filas_op):
                base, un, v = filas_op[k]
                t.setItem(fi, c, _cell(f"{_i18n.t(base)}" + (f" [{un}]:" if un else ":"), bg=GRAY_LBL))
                t.setItem(fi, c + 1, _cell(v, color=TEXT_RES))
            else:
                t.setItem(fi, c, _cell("", bg=GRAY_LBL)); t.setItem(fi, c + 1, _cell("", bg=GRAY_RES))
        for fi in range(nf):
            t.setRowHeight(fi, ROW_H)
        _ajustar(t)
        av = [_i18n.t("Advertencia:") + " " + _i18n.t(a) for a in r.get('avisos') or []]
        self.lbl_aviso.setText("\n".join(av)); self.lbl_aviso.setVisible(bool(av))
        self._render_prop(); self._render_comp()

    def _filas_operacion(self):
        r = self.res; d = r['datos']; op = r['op']
        e1 = r['entrada']; e2 = r['salida']
        H = lambda v: _fmt(_u.H_desde(v) if v is not None else None, 2)
        filas = []
        dT = lambda: _fmt(dT_desde(e2['T'] - e1['T']), 2)
        if op in ('compresor', 'expansor', 'bomba'):
            rel = "Relación de compresión" if op != 'expansor' else "Relación de expansión"
            filas.append((rel, "", _fmt(d.get('relacion'), 4)))
            if op == 'compresor' and d.get('metodo') == 'pace':
                filas.append(("Eficiencia politrópica", "", _fmt(d.get('eta'), 4)))
            elif op == 'bomba':
                pass
            else:
                filas.append(("Eficiencia isentrópica", "", _fmt(d.get('eta'), 4)))
            if op != 'bomba' and d.get('T2s') is not None:
                filas.append(("Temperatura de salida isentrópica", _u.u('T'),
                              _fmt(_u.t_desde_R(d['T2s']), 2)))
                filas.append(("Cambio de entalpía isentrópico", _u.u('H'), H(d.get('dHs'))))
            filas.append(("Cambio de entalpía", _u.u('H'), H(d.get('dH'))))
            filas.append(("Cambio de temperatura", _u.u('T'), dT()))
            nombre = {'compresor': "Trabajo del compresor", 'expansor': "Trabajo del expansor",
                      'bomba': "Trabajo de la bomba"}[op]
            filas.append((nombre, u_pot(), _fmt(pot_desde(d['trabajo']), 3)))
            if op == 'compresor' and d.get('metodo') == 'pace':
                filas.append(("Head", u_head(), _fmt(head_desde(d['head']), 1)))
                for k, nom in (('Xmin', "X mínimo"), ('Xmax', "X máximo"),
                               ('Ymin', "Y mínimo"), ('Ymax', "Y máximo")):
                    filas.append((nom, "", _fmt(d.get(k), 4)))
        elif op in ('enfriador', 'calentador'):
            filas.append(("Cambio de temperatura", _u.u('T'), dT()))
            filas.append(("Caída de presión", _u.u('P'), _fmt(dP_desde(d.get('dP', 0.0)), 2)))
            filas.append(("Cambio de entalpía", _u.u('H'), H(d.get('dH'))))
            nombre = "Capacidad de enfriamiento" if op == 'enfriador' else "Capacidad de calentamiento"
            filas.append((nombre, u_calor(), _fmt(calor_desde(d['calor']), 2)))
        elif op == 'valvula':
            filas.append(("Caída de presión", _u.u('P'), _fmt(dP_desde(d['dP']), 2)))
            filas.append(("Cambio de temperatura", _u.u('T'), dT()))
        return filas

    def _estados(self):
        """[(título, estado)] de las corrientes de las hojas de propiedades y
        composición: entrada y salida (o la alimentación del separador)."""
        r = self.res
        if r['op'] == 'separador' or r.get('salida') is None:
            return [(_i18n.t("Alimentación"), r['entrada'])]
        return [(_i18n.t("Entrada"), r['entrada']), (_i18n.t("Salida"), r['salida'])]

    def _con_agua(self):
        e = self.res['entrada']; z = e.get('z') or []
        return (len(z) > NC and z[NC] > 0) or any(
            'W' in x['fases'] for x in (self.res['entrada'], self.res.get('salida')) if x)

    def _fases(self, e=None):
        """Siempre las mismas columnas (vapor, líquido y, con agua, fase
        acuosa), haya o no esa fase; las ausentes se sombrean."""
        fs = [('V', _i18n.t("Vapor")), ('L', _i18n.t("Líquido"))]
        if self._con_agua():
            fs.append(('W', _i18n.t("Acuosa")))
        return fs

    def _encabezado(self, t, grupos, w_col, col0, tit0):
        """Dos filas de encabezado: el nombre de cada corriente sobre sus
        columnas y el de cada fase debajo.  grupos = [(título, [subtítulos])];
        un título None ocupa las dos filas (columna sin corriente)."""
        t.setItem(0, 0, _cell(tit0, bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        t.setItem(1, 0, _cell("", bg=GRAY_LBL))
        t.setSpan(0, 0, 2, 1)
        t.setColumnWidth(0, col0)
        c = 1
        for tit, subs in grupos:
            if tit is None:
                t.setItem(0, c, _cell(subs[0], bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
                t.setItem(1, c, _cell("", bg=GRAY_LBL))
                t.setSpan(0, c, 2, 1); t.setColumnWidth(c, w_col); c += 1
                continue
            t.setItem(0, c, _cell(tit, bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
            for j in range(1, len(subs)):
                t.setItem(0, c + j, _cell("", bg=GRAY_LBL))
            if len(subs) > 1:
                t.setSpan(0, c, 1, len(subs))
            for j, sub in enumerate(subs):
                t.setItem(1, c + j, _cell(sub, bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
                t.setColumnWidth(c + j, w_col)
            c += len(subs)

    def _render_prop(self):
        if self.res is None:
            return
        t = self.tbl_prop
        filas = [("Fracción molar", "", lambda f: f['beta'], 6, None),
                 ("Fracción másica", "", lambda f: f.get('beta_m'), 6, None),
                 ("Peso molecular", "", lambda f: f['PM'], 4, None),
                 ("Densidad", _u.u('dens'), lambda f: f['rho'], 4, _u.dens_desde),
                 ("Factor de compresibilidad", "", lambda f: f['Z'], 5, None),
                 ("Entalpía molar", _u.u('H'), lambda f: f['H'], 2, _u.H_desde),
                 ("Entropía molar", _u.u('S'), lambda f: f['S'], 4, _u.S_desde),
                 ("Viscosidad", _u.u('visc'), lambda f: f['mu'], 5, None)]
        cols = []          # (estado, clave de fase)
        grupos = []
        if self.res['op'] == 'separador':
            e = self.res['entrada']
            cols = [(e, 'Z')] + [(e, k) for k, _n, _s in self._salidas_sep()]
            grupos = [(_i18n.t("Alimentación"), [_i18n.t("Global")])] + \
                     [(s_, [nm]) for _k, nm, s_ in self._salidas_sep()]
        else:
            for tit, e in self._estados():
                fs = [('Z', _i18n.t("Global"))] + self._fases(e)
                grupos.append((tit, [n for _k, n in fs]))
                cols += [(e, k) for k, _n in fs]
        t.clearSpans(); t.clear()
        t.setRowCount(len(filas) + 2); t.setColumnCount(len(cols) + 1)
        self._encabezado(t, grupos, 80, 190, "")
        self._repartir(t, 190)
        for c, (e, k) in enumerate(cols, 1):
            f = (dict(beta=1.0, beta_m=1.0, PM=e['PM'], rho=e['rho'], Z=None,
                      H=e['H'], S=e['S'], mu=None) if k == 'Z' else e['fases'].get(k))
            for r, (base, un, get, dec, conv) in enumerate(filas, 2):
                try:
                    v = get(f) if f is not None else None
                    v = conv(v) if (conv and v is not None) else v
                except Exception:
                    v = None
                t.setItem(r, c, _cell(_fmt(v, dec), color=TEXT_RES,
                                      bg=WHITE if v is not None else GRAY_RES))
        for r, (base, un, *_x) in enumerate(filas, 2):
            t.setItem(r, 0, _cell(f"{_i18n.t(base)}" + (f" [{un}]:" if un else ":"), bg=GRAY_LBL))
        for r in range(t.rowCount()):
            t.setRowHeight(r, ROW_H)
        _ajustar(t)

    def _render_comp(self):
        if self.res is None:
            return
        t = self.tbl_comp
        est = self._estados()
        n = self.res['n']
        z = est[0][1].get('z') or []
        con_agua = self._con_agua()
        idx = list(range(NC + 1 if con_agua else NC))
        unid = self.cmb_ucomp.currentData() or 'xm'
        un = {'nm': u_mol(), 'nw': u_mas()}.get(unid)
        self.lbl_comp.setText(_i18n.t("Composición de las fases") + (f" [{un}]" if un else ""))
        import eos as _e
        M = list(PM_COMP) + [_e.prop_agua('PM')]

        def convertir(comp, flujo):
            """comp: fracciones molares (lista NC+1); flujo: lbmol/h de la fase."""
            x = [(comp[i] if i < len(comp) else 0.0) for i in range(NC + 1)]
            if unid in ('xw', 'pw'):
                m = [x[i]*M[i] for i in range(NC + 1)]; sm = sum(m) or 1.0
                v = [mi/sm for mi in m]
                return [vi*100 for vi in v] if unid == 'pw' else v
            if unid == 'pm':
                return [xi*100 for xi in x]
            if unid == 'nm':
                return [mol_desde(flujo*xi) for xi in x]
            if unid == 'nw':
                return [mas_desde(flujo*x[i]*M[i]) for i in range(NC + 1)]
            return x

        cols = [convertir(z, n)]
        if self.res['op'] == 'separador':
            # alimentación (global) y cada salida con su fase
            e = est[0][1]
            grupos = [(_i18n.t("Alimentación"), [_i18n.t("Global")])]
            for k, nm, s_ in self._salidas_sep():
                grupos.append((s_, [nm]))
                f = e['fases'].get(k)
                cols.append(convertir(f['comp'], n*f['beta']) if f else None)
        else:
            grupos = [(None, [_i18n.t("Global")])]
            for tit, e in est:
                fs = self._fases(e)
                grupos.append((tit, [nm for _k, nm in fs]))
                for k, _nm in fs:
                    f = e['fases'].get(k)
                    cols.append(convertir(f['comp'], n*f['beta']) if f else None)
        t.clearSpans(); t.clear()
        t.setRowCount(len(idx) + 3); t.setColumnCount(len(cols) + 1)
        self._encabezado(t, grupos, 80, 210, _i18n.t("Componente"))
        self._repartir(t, 210)
        dec = 4 if unid in ('xm', 'xw', 'pm', 'pw', 'nm') else 2
        for c, comp in enumerate(cols, 1):
            for r, i in enumerate(idx, 2):
                if comp is None:
                    t.setItem(r, c, _cell("", bg=GRAY_RES))
                    continue
                d = 6 if (i == NC and unid in ('xm', 'xw')) else dec
                t.setItem(r, c, _cell(f"{comp[i]:.{d}f}", color=TEXT_RES))
            if comp is None:
                t.setItem(len(idx) + 2, c, _cell("", bg=GRAY_RES))
            else:
                tot = sum(comp[i] for i in idx)
                t.setItem(len(idx) + 2, c, _cell(f"{tot:.{dec}f}", color=TEXT_RES))
        for r, i in enumerate(idx, 2):
            nom = NOMBRES[i] if i < NC else componente_etiqueta(NC)
            t.setItem(r, 0, _cell(_i18n.t(nom), bg=GRAY_LBL))
        t.setItem(len(idx) + 2, 0, _cell(_i18n.t("Sumatorias:"), bg=GRAY_LBL))
        for r in range(t.rowCount()):
            t.setRowHeight(r, ROW_H)
        _ajustar(t)

    # ── unidades / idioma ───────────────────────────────────────────────
    def aplicar_unidades(self, old=None):
        self._render()

    def retraducir_grafico(self):
        self._render()

    def exportar_csv(self):
        if self.res is None:
            return
        path, _f = QFileDialog.getSaveFileName(self, _i18n.t("Exportar CSV"),
                                               "operacion_unitaria.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.lbl_op.text().replace('\n', ' ') + "\n")
                for t in (self.tbl_corr, self.tbl_op, self.tbl_prop, self.tbl_comp):
                    for r in range(t.rowCount()):
                        fila = [(t.item(r, c).text() if t.item(r, c) else "")
                                for c in range(t.columnCount())]
                        f.write(";".join(fila) + "\n")
                    f.write("\n")
                for a in self.res.get('avisos') or []:
                    f.write(_i18n.t("Advertencia:") + " " + _i18n.t(a) + "\n")
            dialogos.info(self, f"{_i18n.t('CSV guardado:')}\n{path}")
        except Exception as ex:
            dialogos.error(self, str(ex))

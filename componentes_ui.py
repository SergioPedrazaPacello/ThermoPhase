# -*- coding: utf-8 -*-
"""
Ventanas relacionadas con los componentes puros:

  VentanaPropComponente : muestra todas las propiedades de un componente
                          (críticas HYSYS, críticas PVTsim, COSTALD, etc.)
                          en una ventana con el estilo del selector de
                          propiedades del equilibrio.

  VentanaGestorComponentes : ventana de dos listas (disponibles /
                          seleccionados) para escoger qué componentes
                          entran en un fluido.  Por ahora no ejecuta
                          ninguna acción sobre el motor; solo la interfaz.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

import numpy as np
import eos as _eng
import idioma as _i18n

# ── Paleta (coherente con ventana_principal) ────────────────────
WHITE    = "#FFFFFF"
GRAY_TIT = "#A8A8A8"
GRAY_LBL = "#D0D0D0"
GRAY_RES = "#E8E8E8"
BORDER   = "#888888"
TEXT     = "#000000"
TEXT_DIM = "#555555"
TEXT_RES = "#000080"
FONT_F   = "Arial Narrow"
FS       = 10


# ════════════════════════════════════════════════════════════════
#  Definición de las propiedades a mostrar por componente
# ════════════════════════════════════════════════════════════════
# Cada entrada: (etiqueta, nombre_array_en_eos, magnitud, decimales)
#   magnitud: None (adimensional), 'T_abs' (°R/K), 'P' (psia/kPa/bar),
#             'V_mol_cm3' (cm³/mol → se mantiene), 'V_mol_ft3' (ft³/lbmol),
#             'PM' (lb/lbmol), 'NBP' (°R/K temperatura absoluta)
# Los valores se guardan internamente en unidades de campo y se convierten
# a la unidad del sistema activo al mostrarlos.

import unidades as _u

# ── Valores por componente (unidades internas de campo) ─────────────────
# Cada propiedad se obtiene con una función getter(i) → valor (o None si no
# aplica).  Así el agua (índice 13), cuyos datos viven fuera de los arreglos de
# 13 componentes, se trata igual que el resto.

_J_A_BTU = 0.2388459              # J/(mol·K) → BTU/(lbmol·°F)
_T60_K = (60.0 + 459.67)/1.8      # 60 °F en K


def _es_agua(i):
    return i == getattr(_eng, 'IDX_AGUA', 13)


def _hysys_agua():
    import flash_agua as _fa
    return _fa


def _g_nbp(i):
    return _eng.AGUA_NBP if _es_agua(i) else _eng.NBP[i]


def _g_formador(i):
    """Estructuras de hidrato en las que el componente entra como huésped
    (constantes de Langmuir de la base de datos de PVTsim)."""
    if _es_agua(i):
        return "Anfitrión (red del hidrato)"
    import hidratos as _h
    nombre = [k for k, v in _h._IDX.items() if v == i]
    if not nombre:
        return "No"
    nom = nombre[0]
    est = []
    par = _h._AB_DB_PR.get(nom)
    if par is not None:
        if any(p is not None for p in par[0:2]):
            est.append('sI')
        if any(p is not None for p in par[2:4]):
            est.append('sII')
    if any(nom in _h._AB_H_PR[c] for c in ('small', 'large')):
        est.append('sH')
    return ", ".join(est) if est else "No"


# HYSYS
def _g_tc_h(i):  return _hysys_agua().AGUA_TC if _es_agua(i) else _eng.TC[i]
def _g_pc_h(i):  return _hysys_agua().AGUA_PC if _es_agua(i) else _eng.PC[i]
def _g_w_pr(i):  return _hysys_agua().AGUA_OMEGA if _es_agua(i) else _eng.OMEGA[i]
def _g_w_srk(i): return _hysys_agua().AGUA_OMEGA_SRK if _es_agua(i) else _eng.OMEGA_SRK[i]
def _g_pm_h(i):  return _hysys_agua().AGUA_PM if _es_agua(i) else _eng.PM[i]
def _g_vc_h(i):  return 55.9 if _es_agua(i) else _eng.VC[i]


def _g_vstar(i):
    if _es_agua(i):
        import propiedades_agua as _pa
        return _pa.AGUA_VSTAR
    return _eng.VSTAR_COSTALD[i]


def _g_pen(i, srk):
    """Traslado de volumen de Peneloux c' [ft³/lbmol] de PVTsim (base de datos
    CPenPR/CPenSRK; correlación de PVTsim si el componente no lo tiene)."""
    return _eng.c_peneloux_i(i, 'SRK_PVT' if srk else 'PR_PVT')


def _cp60(coefs):
    if coefs is None:
        return None
    c1, c2, c3, c4 = coefs[:4]
    T = _T60_K
    return (c1 + c2*T + c3*T**2 + c4*T**3)*_J_A_BTU


def _g_cp_h(i):
    if _es_agua(i):
        import propiedades_agua as _pa
        return _cp60(_pa.CP_REID_AGUA)
    import entalpia_entropia_gen as _hs
    return _cp60(_hs._cp_coefs(i, 'PR'))


# PVTsim
def _g_tc_p(i):  return _eng.AGUA_TC if _es_agua(i) else _eng.TC_PVT[i]
def _g_pc_p(i):  return _eng.AGUA_PC if _es_agua(i) else _eng.PC_PVT[i]
def _g_w_p(i):   return _eng.AGUA_OMEGA if _es_agua(i) else _eng.OMEGA_PVT[i]
def _g_pm_p(i):  return _eng.AGUA_PM if _es_agua(i) else _eng.PM_PVT[i]
def _g_vc_p(i):  return _eng.AGUA_VC_PVT if _es_agua(i) else _eng.VC_PVT[i]


def _g_cp_p(i):
    if _es_agua(i):
        import propiedades_agua as _pa
        return _cp60(_pa._cp_agua('PR_PVT'))
    import entalpia_entropia_gen as _hs
    return _cp60(_hs._cp_coefs(i, 'PR_PVT'))


# Cada entrada: (etiqueta, getter | 'nombre' | 'simbolo', magnitud, decimales)
#   magnitud: None, 'T_abs', 'P', 'PM', 'Vc' (cm³/mol), 'Vstar' (ft³/lbmol),
#             'Vpen' (ft³/lbmol), 'Cp' (unidad de entropía), 'texto'
_GRUPOS_PROP = [
    ("Propiedades generales", [
        ("Nombre",                          'nombre',   None,    None),
        ("Símbolo",                         'simbolo',  None,    None),
        ("Punto de ebullición normal",      _g_nbp,     "T_abs", 2),
        ("Formador de hidrato (estructuras)", _g_formador, "texto", None),
    ]),
    ("Parámetros de HYSYS (EOS PR y SRK de HYSYS)", [
        ("Temperatura crítica",             _g_tc_h,    "T_abs", 4),
        ("Presión crítica",                 _g_pc_h,    "P",     4),
        ("Factor acéntrico (PR)",           _g_w_pr,    None,    6),
        ("Factor acéntrico (SRK)",          _g_w_srk,   None,    6),
        ("Peso molecular",                  _g_pm_h,    "PM",    4),
        ("Volumen crítico (viscosidad LBC)", _g_vc_h,   "Vc",    2),
        ("Volumen característico V* (COSTALD)", _g_vstar, "Vstar", 6),
        ("Cp de gas ideal a 60 °F",         _g_cp_h,    "Cp",    4),
    ]),
    ("Parámetros de PVTsim (EOS PR y SRK de PVTsim)", [
        ("Temperatura crítica",             _g_tc_p,    "T_abs", 4),
        ("Presión crítica",                 _g_pc_p,    "P",     4),
        ("Factor acéntrico",                _g_w_p,     None,    6),
        ("Peso molecular",                  _g_pm_p,    "PM",    4),
        ("Volumen crítico (viscosidad LBC)", _g_vc_p,   "Vc",    2),
        ("Traslado de volumen de Peneloux (PR)",  lambda i: _g_pen(i, False), "Vpen", 6),
        ("Traslado de volumen de Peneloux (SRK)", lambda i: _g_pen(i, True),  "Vpen", 6),
        ("Cp de gas ideal a 60 °F",         _g_cp_p,    "Cp",    4),
    ]),
]


def _unidad_prop(magnitud):
    """Etiqueta de unidad de una propiedad según el sistema activo."""
    if magnitud in (None, 'texto'):
        return ""
    if magnitud == 'T_abs':
        return _u.u_abs()                 # °R o K
    if magnitud == 'P':
        return _u.u('P')                  # psia, kPa o bar
    if magnitud == 'PM':
        return 'lb/lbmol' if _u.sistema() == 'FIELD' else 'kg/kgmol'
    if magnitud == 'Vc':
        return 'cm³/mol'                  # volumen crítico se mantiene
    if magnitud in ('Vstar', 'Vpen'):
        return _u.u('V')
    if magnitud == 'Cp':
        return _u.u('S')
    return ""


def _valor_convertido(idx, getter, magnitud, decimales):
    """Valor de una propiedad convertido al sistema activo, formateado."""
    if getter is None:
        return ""
    try:
        val = getter(idx)
    except Exception:
        val = None
    if val is None:
        return ""
    if magnitud == 'texto':
        return _i18n.t(str(val))
    if magnitud == 'T_abs':
        val = _u.abs_desde_R(val)
    elif magnitud == 'P':
        val = _u.p_desde_psia(val)
    elif magnitud in ('Vstar', 'Vpen'):
        val = _u.V_desde(val)
    elif magnitud == 'Cp':
        val = _u.S_desde(val)
    if decimales is None:
        return str(val)
    return f"{val:.{decimales}f}"


class VentanaPropComponente(QWidget):
    """Ventana del componente puro: nombre y símbolo, y los parámetros Tc, Pc,
    ω y PM de las cuatro EOS (PR y SRK de HYSYS y de PVTsim).  Los valores son
    EDITABLES: al cambiarlos se recalculan los parámetros de la EOS en todo el
    programa (como los kij).  «Restaurar valores originales» vuelve a la base
    de datos.  Estilo de tablas igual al de Equilibrio de fases."""

    # (clave en eos, etiqueta, magnitud, decimales)
    _PROPS = [
        ('TC',    "Temperatura crítica", 'T_abs', 4),
        ('PC',    "Presión crítica",     'P',     4),
        ('PM',    "Peso molecular",      'PM',    4),
        ('OMEGA', "Factor acéntrico",    None,    6),
    ]
    # (título del grupo, [(código EOS, cabecera de columna), ...])
    _GRUPOS = [
        ("Parámetros de HYSYS",  [('PR', "Peng-Robinson"), ('SRK', "SRK")]),
        ("Parámetros de PVTsim", [('PR_PVT', "Peng-Robinson"), ('SRK_PVT', "SRK")]),
    ]
    W_ET, W_VAL = 236, 128

    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        self._tablas = []        # [(tabla, [codigos EOS])]
        self._build()
        _eng.escuchar_props(self._oyente)

    # ── estilo compartido con ventana_principal ─────────────────
    @staticmethod
    def _vp():
        import ventana_principal as _vp
        return _vp

    def _titulo(self, texto):
        lbl = QLabel(_i18n.t(texto))
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl.setFixedHeight(22)
        lbl.setStyleSheet(
            f'background:{GRAY_TIT}; color:{TEXT}; font-family:"{FONT_F}";'
            f' font-size:{FS}pt; padding:0px 6px; border:1px solid {BORDER};')
        lbl.setFixedWidth(self._ancho)
        return lbl

    def _tabla(self, filas, cols):
        vp = self._vp()
        t = QTableWidget(filas, cols)
        t.horizontalHeader().hide(); t.verticalHeader().hide()
        t.setShowGrid(False)
        t.setStyleSheet(
            f'QTableWidget {{ background:{WHITE};'
            f'border-top:1px solid {BORDER};border-left:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;'
            f'selection-background-color:{vp.SEL_BG};selection-color:{TEXT};}}'
            f'QTableWidget::item {{ padding:2px 6px; }}')
        t.setItemDelegate(vp.GridDelegate(BORDER, t))
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.setColumnWidth(0, self.W_ET)
        for c in range(1, cols):
            t.setColumnWidth(c, self.W_VAL if cols > 2 else 2*self.W_VAL)
        for r in range(filas):
            t.setRowHeight(r, vp.ROW_H)
        t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        t.setFixedWidth(self._ancho)
        return t

    @staticmethod
    def _fija(it):
        it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsSelectable
                    & ~Qt.ItemFlag.ItemIsEditable)
        return it

    def _ajustar_alto(self, t):
        alto = sum(t.rowHeight(r) for r in range(t.rowCount())) + 2
        t.setFixedHeight(alto)

    def _build(self):
        vp = self._vp()
        self._ancho = self.W_ET + 2*self.W_VAL + 2
        self.setStyleSheet('background:#E6E6E6;')   # fondo como Equilibrio de fases
        root = QVBoxLayout(self)
        root.setContentsMargins(13, 6, 13, 8); root.setSpacing(3)
        DER = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        CEN = Qt.AlignmentFlag.AlignCenter

        # ── Propiedades generales ──
        root.addWidget(self._titulo("Propiedades generales"),
                       alignment=Qt.AlignmentFlag.AlignHCenter)
        tg = self._tabla(2, 2)
        tg.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tg.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        tg.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        nombre = _eng.componente_etiqueta(self.idx).rstrip(":")
        for r, (et, val) in enumerate([("Nombre", _i18n.t(nombre)),
                                       ("Símbolo", _eng.componente_nombre(self.idx))]):
            tg.setItem(r, 0, vp.cell(_i18n.t(et), bg=GRAY_LBL, align=DER))
            tg.setItem(r, 1, vp.cell(val, bg=WHITE, color=TEXT_RES, align=CEN))
        self._ajustar_alto(tg)
        root.addWidget(tg, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._tg = tg

        # ── HYSYS y PVTsim ──
        for titulo, cols in self._GRUPOS:
            root.addSpacing(3)
            root.addWidget(self._titulo(titulo), alignment=Qt.AlignmentFlag.AlignHCenter)
            t = self._tabla(1 + len(self._PROPS), 1 + len(cols))
            t.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked
                              | QAbstractItemView.EditTrigger.EditKeyPressed
                              | QAbstractItemView.EditTrigger.AnyKeyPressed)
            t.setItem(0, 0, self._fija(vp.cell(_i18n.t("Propiedad"), bg=GRAY_LBL, align=CEN)))
            for c, (_cod, cab) in enumerate(cols):
                t.setItem(0, c+1, self._fija(vp.cell(cab, bg=GRAY_LBL, align=CEN)))
            self._ajustar_alto(t)
            t.itemChanged.connect(lambda it, t=t, cols=cols: self._on_editar(t, cols, it))
            root.addWidget(t, alignment=Qt.AlignmentFlag.AlignHCenter)
            self._tablas.append((t, [c for c, _ in cols]))
        self._llenar()

        # ── Botón restaurar ──
        root.addSpacing(5)
        fila = QHBoxLayout(); fila.setContentsMargins(0, 0, 0, 0)
        fila.addStretch()
        self.btn_reset = QPushButton(_i18n.t("Restaurar valores originales"))
        self.btn_reset.setFixedWidth(220)
        self.btn_reset.setStyleSheet(
            f'background:{GRAY_LBL};border:2px outset {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset)
        fila.addWidget(self.btn_reset)
        root.addLayout(fila)
        root.addStretch()

    # ── datos ────────────────────────────────────────────────────
    def _texto(self, eos, clave, magnitud, dec):
        v = _eng.get_prop_componente(eos, clave, self.idx)
        if magnitud == 'T_abs':
            v = _u.abs_desde_R(v)
        elif magnitud == 'P':
            v = _u.p_desde_psia(v)
        return f"{v:.{dec}f}"

    def _llenar(self):
        vp = self._vp()
        DER = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        CEN = Qt.AlignmentFlag.AlignCenter
        for t, cods in self._tablas:
            t.blockSignals(True)
            for r, (clave, et, mag, dec) in enumerate(self._PROPS, start=1):
                un = _unidad_prop(mag)
                txt = _i18n.t(et) + (f" [{un}]" if un else "")
                t.setItem(r, 0, self._fija(vp.cell(txt, bg=GRAY_LBL, align=DER)))
                for c, eos in enumerate(cods, start=1):
                    it = vp.cell(self._texto(eos, clave, mag, dec), bg=WHITE,
                                 color=TEXT_RES, align=CEN, editable=True)
                    it.setData(Qt.ItemDataRole.UserRole, (eos, clave))
                    if _eng.prop_modificada(eos, clave, self.idx):
                        it.setToolTip(_i18n.t("Valor modificado. Original: ")
                                      + self._texto_orig(eos, clave, mag, dec))
                    t.setItem(r, c, it)
            t.setCurrentItem(None)
            t.blockSignals(False)
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setEnabled(_eng.componente_modificado(self.idx))

    def _texto_orig(self, eos, clave, magnitud, dec):
        v = _eng.get_prop_original(eos, clave, self.idx)
        if magnitud == 'T_abs':
            v = _u.abs_desde_R(v)
        elif magnitud == 'P':
            v = _u.p_desde_psia(v)
        return f"{v:.{dec}f}"

    def _on_editar(self, t, cols, item):
        dato = item.data(Qt.ItemDataRole.UserRole)
        if not dato:
            return
        eos, clave = dato
        from numeros import a_float
        v = a_float(item.text())
        ok = v is not None and np.isfinite(v)
        if ok:
            if clave == 'TC':
                v = _u.R_desde_abs(v); ok = v > 0
            elif clave == 'PC':
                v = _u.p_a_psia(v); ok = v > 0
            elif clave == 'PM':
                ok = v > 0
            elif clave == 'OMEGA':
                ok = -1.0 < v < 5.0
        if ok:
            _eng.set_prop_componente(eos, clave, self.idx, v)   # avisa a los oyentes
        else:
            self._llenar()                                        # valor inválido: revertir
        if hasattr(self, 'btn_reset'):
            self.btn_reset.setEnabled(_eng.componente_modificado(self.idx))

    def _reset(self):
        _eng.restablecer_componente(self.idx)
        try:
            import dialogos
            dialogos.info(self, _i18n.t("Valores originales restaurados."))
        except Exception:
            pass

    def _oyente(self):
        try:
            self._llenar()
            self.btn_reset.setEnabled(_eng.componente_modificado(self.idx))
        except RuntimeError:
            # La ventana se cerró (objeto Qt destruido): dejar de escuchar.
            try: _eng._OYENTES_PROPS.remove(self._oyente)
            except ValueError: pass

    def aplicar_unidades(self, old=None):
        self._llenar()

    def tam_ideal(self):
        """Tamaño (ancho, alto) ajustado al contenido."""
        sh = self.sizeHint()
        return (max(sh.width(), self._ancho + 26), sh.height())


class VentanaGestorComponentes(QWidget):
    """Gestor de componentes de un fluido: dos listas (disponibles /
    seleccionados) con botones Agregar y Quitar.  Por ahora solo interfaz;
    no modifica el motor."""

    def __init__(self, seleccionados=None, on_cambio=None):
        super().__init__()
        # Por defecto, los 13 HC están seleccionados y el AGUA (índice 13) NO.
        # El total de componentes disponibles es NC+1 (13 HC + agua opcional).
        if seleccionados is None:
            seleccionados = list(range(_eng.NC))   # sin agua
        self._sel = list(seleccionados)
        self._on_cambio = on_cambio    # callback(lista_indices) al cambiar
        self._build()

    # Total de componentes disponibles en el gestor (13 HC + agua).
    _N_TOTAL = property(lambda self: _eng.NC + 1)

    def _indices_seleccionados(self):
        """Índices de componentes actualmente en la lista de seleccionados,
        en el orden canónico del motor."""
        idxs = []
        for r in range(self.lista_sel.count()):
            idxs.append(self.lista_sel.item(r).data(Qt.ItemDataRole.UserRole))
        return sorted(idxs)

    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)

        info = QLabel(_i18n.t("Seleccione los componentes del fluido:"))
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
        self.lista_disp = QListWidget(); self.lista_disp.setStyleSheet(list_qss)
        self.lista_disp.setFixedSize(250, 310)
        col_izq.addWidget(self.lista_disp)
        cols.addLayout(col_izq)

        col_der = QVBoxLayout(); col_der.setSpacing(3)
        lbl_sel = QLabel(_i18n.t("Seleccionados"))
        lbl_sel.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                              f'color:{TEXT};background:transparent;')
        col_der.addWidget(lbl_sel)
        self.lista_sel = QListWidget(); self.lista_sel.setStyleSheet(list_qss)
        self.lista_sel.setFixedSize(250, 310)
        col_der.addWidget(self.lista_sel)
        cols.addLayout(col_der)

        root.addLayout(cols)

        # Poblar listas (13 HC + agua opcional en índice 13)
        for i in self._sel:
            self._add_item(self.lista_sel, i)
        for i in range(_eng.NC + 1):
            if i not in self._sel:
                self._add_item(self.lista_disp, i)

        # Fila de botones
        fila = QHBoxLayout(); fila.setSpacing(8)
        self.contador = QLabel()
        self.contador.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                                    f'color:{TEXT};background:transparent;')
        fila.addWidget(self.contador)
        fila.addStretch()
        self.btn_add = QPushButton(_i18n.t("Agregar"))
        self.btn_rem = QPushButton(_i18n.t("Quitar"))
        for b in (self.btn_add, self.btn_rem):
            b.setFixedHeight(26); b.setMinimumWidth(90)
            b.setStyleSheet(btn_qss)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            fila.addWidget(b)
        root.addLayout(fila)
        root.addStretch()

        self.btn_add.clicked.connect(self._agregar)
        self.btn_rem.clicked.connect(self._quitar)
        self.lista_disp.itemDoubleClicked.connect(lambda _: self._agregar())
        self.lista_sel.itemDoubleClicked.connect(lambda _: self._quitar())
        self._actualizar()

    def _add_item(self, lista, idx):
        nombre = _eng.componente_etiqueta(idx).rstrip(':')
        it = QListWidgetItem(nombre)
        it.setData(Qt.ItemDataRole.UserRole, idx)
        # Insertar en orden canónico (por índice de componente)
        pos = lista.count()
        for r in range(lista.count()):
            if lista.item(r).data(Qt.ItemDataRole.UserRole) > idx:
                pos = r; break
        lista.insertItem(pos, it)

    def _actualizar(self):
        n = self.lista_sel.count()
        self.contador.setText(_i18n.t("Seleccionados: ") + f"{n} / {_eng.NC + 1}")
        self.btn_add.setEnabled(self.lista_disp.count() > 0)
        # No permitir quitar el último componente (siempre al menos 1)
        self.btn_rem.setEnabled(self.lista_sel.count() > 1)

    def _mover(self, origen, destino):
        it = origen.currentItem()
        if it is None:
            return
        # No permitir vaciar la lista de seleccionados
        if origen is self.lista_sel and self.lista_sel.count() <= 1:
            return
        idx = it.data(Qt.ItemDataRole.UserRole)
        origen.takeItem(origen.row(it))
        self._add_item(destino, idx)
        self._actualizar()
        if self._on_cambio is not None:
            self._on_cambio(self._indices_seleccionados())

    def _agregar(self):
        self._mover(self.lista_disp, self.lista_sel)

    def _quitar(self):
        self._mover(self.lista_sel, self.lista_disp)

    def tam_ideal(self):
        """Tamaño (ancho, alto) ajustado exactamente al contenido, medido
        con el sizeHint real del widget para evitar scrollbars o huecos."""
        sh = self.sizeHint()
        return (sh.width(), sh.height())


def _qcolor(hexstr):
    from PyQt6.QtGui import QColor
    return QColor(hexstr)

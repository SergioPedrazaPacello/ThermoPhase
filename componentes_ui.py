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
    """Traslado de volumen de Peneloux [ft³/lbmol] (misma fórmula del motor)."""
    tc, pc, w = _g_tc_h(i), _g_pc_h(i), _g_w_pr(i)
    z_ra = 0.29056 - 0.08775*w
    rtp = _eng.R_GAS*tc/pc
    return 0.40768*rtp*(0.29441 - z_ra) if srk else 0.50033*rtp*(0.25969 - z_ra)


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
        ("Traslado de volumen de Peneloux (PR)",  lambda i: _g_pen(i, False), "Vpen", 6),
        ("Traslado de volumen de Peneloux (SRK)", lambda i: _g_pen(i, True),  "Vpen", 6),
        ("Cp de gas ideal a 60 °F",         _g_cp_h,    "Cp",    4),
    ]),
    ("Parámetros de PVTsim (EOS PR y SRK de PVTsim)", [
        ("Temperatura crítica",             _g_tc_p,    "T_abs", 4),
        ("Presión crítica",                 _g_pc_p,    "P",     4),
        ("Factor acéntrico",                _g_w_p,     None,    6),
        ("Peso molecular",                  _g_pm_p,    "PM",    4),
        ("Volumen crítico (viscosidad LBC)", _g_vc_p,   "Vc",    2),
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
    """Ventana de solo lectura con todas las propiedades de un componente.
    El estilo replica el selector de propiedades del equilibrio."""

    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        self._build()

    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root = QVBoxLayout(self)
        root.setContentsMargins(13, 9, 13, 9); root.setSpacing(3)

        # Título con el nombre del componente
        nombre = _eng.componente_etiqueta(self.idx).rstrip(":")
        title = QLabel(f"ThermoPhase — {nombre}")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22)
        title.setStyleSheet(
            f'background:{GRAY_TIT};color:{TEXT};padding:2px 8px;'
            f'font-family:"{FONT_F}";font-size:{FS}pt;')
        root.addWidget(title)

        # Filas: cabecera de grupo + una fila por propiedad
        # Columna 0 = "Nombre de la propiedad [unidad]", Columna 1 = valor
        filas = []   # ('grupo', texto) | ('prop', etiqueta_con_unidad, valor)
        for grupo, props in _GRUPOS_PROP:
            filas.append(('grupo', grupo))
            for etiqueta, arr, magnitud, dec in props:
                unidad = _unidad_prop(magnitud)
                et_full = _i18n.t(etiqueta)
                if unidad:
                    et_full = f"{et_full} [{unidad}]"
                if arr == 'nombre':
                    valor = _eng.componente_etiqueta(self.idx).rstrip(":")
                elif arr == 'simbolo':
                    valor = _eng.componente_nombre(self.idx)
                else:
                    valor = _valor_convertido(self.idx, arr, magnitud, dec)
                filas.append(('prop', et_full, valor))

        tbl = QTableWidget(len(filas), 2)
        tbl.horizontalHeader().hide()
        tbl.verticalHeader().hide()
        tbl.setShowGrid(True)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tbl.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;gridline-color:{BORDER};}}'
            f'QTableWidget::item {{ padding:2px 6px; }}')
        # Dos columnas: etiqueta+unidad (ancha) | valor
        W_ET, W_VAL = 320, 150
        tbl.setColumnWidth(0, W_ET)
        tbl.setColumnWidth(1, W_VAL)
        hh = tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)

        ROW_H = 24
        for r, fila in enumerate(filas):
            tbl.setRowHeight(r, ROW_H)
            if fila[0] == 'grupo':
                it = QTableWidgetItem(_i18n.t(fila[1]))
                it.setBackground(_qcolor(GRAY_LBL))
                it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                tbl.setItem(r, 0, it)
                tbl.setSpan(r, 0, 1, 2)
            else:
                _, etiqueta, valor = fila
                it_et = QTableWidgetItem(etiqueta)
                it_et.setBackground(_qcolor(GRAY_RES))
                it_et.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                tbl.setItem(r, 0, it_et)
                it_val = QTableWidgetItem(valor)
                it_val.setBackground(_qcolor(WHITE))
                it_val.setForeground(_qcolor(TEXT_RES))
                it_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tbl.setItem(r, 1, it_val)

        alto_tabla = ROW_H * len(filas) + 2
        tbl.setFixedHeight(alto_tabla)
        tbl.setFixedWidth(W_ET + W_VAL + 2)
        tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(tbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addStretch()

        self._tbl = tbl
        self._alto_tabla = alto_tabla
        self._ancho_tabla = W_ET + W_VAL + 2

    def tam_ideal(self):
        """Tamaño (ancho, alto) ajustado al contenido."""
        ancho = self._ancho_tabla + 2*13
        alto = 22 + 3 + self._alto_tabla + 9 + 9 + 4
        return (ancho, alto)


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

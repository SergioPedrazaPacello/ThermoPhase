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

_GRUPOS_PROP = [
    # Propiedades genéricas, comunes a ambos modelos
    ("Propiedades en conjunto", [
        ("Nombre",                  None,           None,   None),
        ("Símbolo",                 None,           None,   None),
        ("Peso molecular",          "PM",           "PM",   4),
        ("Punto de ebullición normal", "NBP",       "T_abs", 2),
        ("Volumen crítico",         "VC",           "Vc",   2),
    ]),
    # Todo lo recopilado de HYSYS (incluye COSTALD, que es el método de
    # densidad de líquido del paquete HYSYS)
    ("Propiedades recopiladas de HYSYS", [
        ("Temperatura crítica",     "TC",           "T_abs", 4),
        ("Presión crítica",         "PC",           "P",    4),
        ("Factor acéntrico (PR)",   "OMEGA",        None,   6),
        ("Factor acéntrico (SRK)",  "OMEGA_SRK",    None,   6),
        ("Volumen característico V* (COSTALD)", "VSTAR_COSTALD", "Vstar", 6),
    ]),
    # Todo lo recopilado de PVTsim
    ("Propiedades recopiladas de PVTsim", [
        ("Temperatura crítica",     "TC_PVT",       "T_abs", 4),
        ("Presión crítica",         "PC_PVT",       "P",    4),
        ("Factor acéntrico",        "OMEGA_PVT",    None,   6),
        ("Peso molecular",          "PM_PVT",       "PM",   4),
    ]),
]


def _unidad_prop(magnitud):
    """Etiqueta de unidad de una propiedad según el sistema activo."""
    if magnitud is None:
        return ""
    if magnitud == 'T_abs':
        return _u.u_abs()                 # °R o K
    if magnitud == 'P':
        return _u.u('P')                  # psia, kPa o bar
    if magnitud == 'PM':
        return _u.u('dens') and 'lb/lbmol' if _u.sistema() == 'FIELD' else 'kg/kgmol'
    if magnitud == 'Vc':
        return 'cm³/mol'                  # volumen crítico se mantiene
    if magnitud == 'Vstar':
        return 'ft³/lbmol' if _u.sistema() == 'FIELD' else 'm³/kgmol'
    return ""


def _valor_convertido(idx, nombre_array, magnitud, decimales):
    """Valor de una propiedad convertido al sistema activo, formateado."""
    if nombre_array is None:
        return ""
    arr = getattr(_eng, nombre_array, None)
    if arr is None or idx >= len(arr):
        return ""
    val = arr[idx]
    # Conversión según magnitud
    if magnitud == 'T_abs':
        val = _u.abs_desde_R(val)
    elif magnitud == 'P':
        val = _u.p_desde_psia(val)
    elif magnitud == 'PM':
        val = val if _u.sistema() == 'FIELD' else val   # lb/lbmol = kg/kgmol num.
    elif magnitud == 'Vstar':
        val = val if _u.sistema() == 'FIELD' else _u.V_desde(val)
    # 'Vc' y None no se convierten
    if decimales is None:
        return str(val)
    return f"{val:.{decimales}f}"


def _valor_prop(idx, nombre_array, decimales):
    """Compatibilidad: valor sin conversión (solo para casos None)."""
    if nombre_array is None:
        return ""
    arr = getattr(_eng, nombre_array, None)
    if arr is None or idx >= len(arr):
        return ""
    val = arr[idx]
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
        nombre = _eng.NOMBRES[self.idx].rstrip(':')
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
                if etiqueta == "Nombre":
                    valor = _eng.NOMBRES[self.idx].rstrip(':')
                elif etiqueta == "Símbolo":
                    valor = _eng.COMPONENTES[self.idx]
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
                it.setBackground(_qcolor(GRAY_TIT))
                it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                tbl.setItem(r, 0, it)
                tbl.setSpan(r, 0, 1, 2)
            else:
                _, etiqueta, valor = fila
                it_et = QTableWidgetItem(etiqueta)
                it_et.setBackground(_qcolor(GRAY_LBL))
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

    def __init__(self, seleccionados=None):
        super().__init__()
        # Por defecto, todos los componentes están seleccionados
        if seleccionados is None:
            seleccionados = list(range(_eng.NC))
        self._sel = list(seleccionados)
        self._build()

    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)

        title = QLabel(_i18n.t("ThermoPhase — Componentes del fluido"))
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22)
        title.setStyleSheet(
            f'background:{GRAY_TIT};color:{TEXT};padding:2px 8px;'
            f'font-family:"{FONT_F}";font-size:{FS}pt;')
        root.addWidget(title)

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

        # Poblar listas
        for i in self._sel:
            self._add_item(self.lista_sel, i)
        for i in range(_eng.NC):
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
        nombre = _eng.NOMBRES[idx].rstrip(':')
        it = QListWidgetItem(nombre)
        it.setData(Qt.ItemDataRole.UserRole, idx)
        lista.addItem(it)

    def _actualizar(self):
        n = self.lista_sel.count()
        self.contador.setText(_i18n.t("Seleccionados: ") + f"{n} / {_eng.NC}")
        self.btn_add.setEnabled(self.lista_disp.count() > 0)
        self.btn_rem.setEnabled(self.lista_sel.count() > 0)

    def _mover(self, origen, destino):
        it = origen.currentItem()
        if it is None:
            return
        idx = it.data(Qt.ItemDataRole.UserRole)
        origen.takeItem(origen.row(it))
        self._add_item(destino, idx)
        self._actualizar()

    def _agregar(self):
        self._mover(self.lista_disp, self.lista_sel)

    def _quitar(self):
        self._mover(self.lista_sel, self.lista_disp)

    def tam_ideal(self):
        return (250*2 + 12 + 2*14, 22 + 3 + 20 + 310 + 40 + 24 + 12)


def _qcolor(hexstr):
    from PyQt6.QtGui import QColor
    return QColor(hexstr)

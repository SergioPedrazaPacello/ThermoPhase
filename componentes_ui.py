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
# Cada entrada: (etiqueta, nombre_array_en_eos, unidad, decimales)
# El grupo indica el bloque (cabecera) bajo el que se muestra.

_GRUPOS_PROP = [
    ("Identificación", [
        ("Nombre",                 None,             "",        None),
        ("Símbolo",                None,             "",        None),
        ("Peso molecular",         "PM",             "lb/lbmol", 4),
        ("Punto de ebullición normal", "NBP",        "°R",       2),
        ("Volumen crítico",        "VC",             "cm³/mol",  2),
    ]),
    ("Propiedades críticas (HYSYS)", [
        ("Temperatura crítica",    "TC",             "°R",       4),
        ("Presión crítica",        "PC",             "psia",     4),
        ("Factor acéntrico (PR)",  "OMEGA",          "",         6),
        ("Factor acéntrico (SRK)", "OMEGA_SRK",      "",         6),
    ]),
    ("Propiedades críticas (PVTsim)", [
        ("Temperatura crítica",    "TC_PVT",         "°R",       4),
        ("Presión crítica",        "PC_PVT",         "psia",     4),
        ("Factor acéntrico",       "OMEGA_PVT",      "",         6),
        ("Peso molecular",         "PM_PVT",         "lb/lbmol", 4),
    ]),
    ("Densidad de líquido (COSTALD)", [
        ("Volumen característico V*", "VSTAR_COSTALD", "ft³/lbmol", 6),
    ]),
]


def _valor_prop(idx, nombre_array, decimales):
    """Devuelve el texto formateado del valor de una propiedad para el
    componente idx.  Si el array no existe devuelve cadena vacía."""
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
            f'font-family:"{FONT_F}";font-size:{FS}pt;font-weight:bold;')
        root.addWidget(title)

        # Construir la tabla de propiedades: filas de grupo (cabecera) +
        # filas de propiedad (etiqueta | valor | unidad)
        filas = []   # (tipo, ...) tipo='grupo' o 'prop'
        for grupo, props in _GRUPOS_PROP:
            filas.append(('grupo', grupo))
            for etiqueta, arr, unidad, dec in props:
                if etiqueta == "Nombre":
                    valor = _eng.NOMBRES[self.idx].rstrip(':')
                elif etiqueta == "Símbolo":
                    valor = _eng.COMPONENTES[self.idx]
                else:
                    valor = _valor_prop(self.idx, arr, dec)
                filas.append(('prop', etiqueta, valor, unidad))

        tbl = QTableWidget(len(filas), 3)
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
        # Anchos: etiqueta ancha, valor medio, unidad angosta
        W_ET, W_VAL, W_UN = 250, 150, 110
        tbl.setColumnWidth(0, W_ET)
        tbl.setColumnWidth(1, W_VAL)
        tbl.setColumnWidth(2, W_UN)
        hh = tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)

        ROW_H = 24
        for r, fila in enumerate(filas):
            tbl.setRowHeight(r, ROW_H)
            if fila[0] == 'grupo':
                # Fila de grupo: una celda combinada visualmente (gris título)
                it = QTableWidgetItem(_i18n.t(fila[1]))
                it.setBackground(_qcolor(GRAY_TIT))
                it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                f = it.font(); f.setBold(True); it.setFont(f)
                tbl.setItem(r, 0, it)
                tbl.setSpan(r, 0, 1, 3)
            else:
                _, etiqueta, valor, unidad = fila
                it_et = QTableWidgetItem(_i18n.t(etiqueta))
                it_et.setBackground(_qcolor(GRAY_LBL))
                it_et.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                tbl.setItem(r, 0, it_et)
                it_val = QTableWidgetItem(valor)
                it_val.setBackground(_qcolor(WHITE))
                it_val.setForeground(_qcolor(TEXT_RES))
                it_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tbl.setItem(r, 1, it_val)
                it_un = QTableWidgetItem(unidad)
                it_un.setBackground(_qcolor(GRAY_RES))
                it_un.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tbl.setItem(r, 2, it_un)

        # Altura fija ajustada al contenido; ancho fijo = suma de columnas
        alto_tabla = ROW_H * len(filas) + 2
        tbl.setFixedHeight(alto_tabla)
        tbl.setFixedWidth(W_ET + W_VAL + W_UN + 2)
        tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(tbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addStretch()

        self._tbl = tbl
        self._alto_tabla = alto_tabla

    def tam_ideal(self):
        """Tamaño (ancho, alto) ajustado al contenido."""
        ancho = (250 + 150 + 110 + 2) + 2*13
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
            f'font-family:"{FONT_F}";font-size:{FS}pt;font-weight:bold;')
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
        self.lista_disp.setFixedSize(250, 260)
        col_izq.addWidget(self.lista_disp)
        cols.addLayout(col_izq)

        col_der = QVBoxLayout(); col_der.setSpacing(3)
        lbl_sel = QLabel(_i18n.t("Seleccionados"))
        lbl_sel.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                              f'color:{TEXT};background:transparent;')
        col_der.addWidget(lbl_sel)
        self.lista_sel = QListWidget(); self.lista_sel.setStyleSheet(list_qss)
        self.lista_sel.setFixedSize(250, 260)
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
        return (250*2 + 12 + 2*14, 22 + 3 + 20 + 260 + 40 + 24 + 12)


def _qcolor(hexstr):
    from PyQt6.QtGui import QColor
    return QColor(hexstr)

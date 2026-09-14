# -*- coding: utf-8 -*-
"""
Pestaña Formación de Hidratos para ThermoPhase.

Calcula la temperatura o la presión de formación de hidrato para la
composición del fluido principal (modelo PVTsim/Munck, ver `hidratos`).
En cada punto muestra el flash (composición de fases) y las propiedades de
ese punto, con el mismo aspecto que la pestaña de Puntos de Saturación.

Incluye un botón para agregar/quitar la curva de formación de hidratos sobre
la envolvente de fases (en verde, marcador triangular).
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

# Reutilizar estilos, helpers y catálogo de propiedades de la pestaña de
# saturación para mantener un aspecto idéntico y no duplicar código.
from pestana_saturacion import (
    WHITE, GRAY_TIT, GRAY_LBL, GRAY_RES, BORDER, TEXT, TEXT_DIM, TEXT_RES,
    FONT_F, FS, ROW_H, GridDelegate,
    BTN_STYLE, LBL_TIT, LBL_SEC,
    _aplicar_estilo_combo, _conv_prop,
    _PROP_SAT, _PROP_SAT_DEF, _PROP_SAT_DEFAULT, PROP_SAT_MAX,
)


class HidratoWorker(QThread):
    """Calcula un punto de la curva de hidratos + el flash en ese punto."""
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, modo, valor, z, kij, eos_nombre=None):
        super().__init__()
        self.modo = modo; self.valor = valor
        self.z = z; self.kij = kij; self.eos_nombre = eos_nombre

    def run(self):
        try:
            import eos as _eng2
            if self.eos_nombre:
                _eng2.set_eos(self.eos_nombre)
            import hidratos as _hid
            pt = _hid.punto_hidrato(self.z, self.modo, self.valor,
                                    self.kij, self.eos_nombre)
            if pt is None:
                self.done.emit({})
                return
            # Flash en el punto de hidrato: composición de fases HC.
            flash = _eng2.calcular(self.z, pt['T_R'], pt['P_psia'], self.kij)
            # Propiedades completas (H, S, PM, densidad, Z, SG, viscosidad) por
            # la misma ruta que la pestaña de saturación.
            from envolvente import propiedades_punto
            x = flash.get('x', list(self.z)); y = flash.get('y', list(self.z))
            props = propiedades_punto(pt['T_R'], pt['P_psia'], x, y, self.kij)
            pt['flash'] = flash
            pt['props'] = props
            self.done.emit(pt)
        except Exception as e:
            self.error.emit(str(e))


class TabHidratos(QWidget):
    # desplegable → (modo_calc, unidad_entrada, etiqueta_entrada, unidad_result)
    #   modo 'T' → se da P, se resuelve T   |  modo 'P' → se da T, se resuelve P
    TIPOS = {
        "Temperatura de Hidrato": ('T', 'P', 'Presion (psi):',    'T'),
        "Presion de Hidrato":     ('P', 'T', 'Temperatura (°R):', 'P'),
    }

    def __init__(self, get_z, get_kij, get_envolvente=None, get_eos_nombre=None):
        super().__init__()
        self.get_z = get_z; self.get_kij = get_kij
        # Callback que devuelve la instancia de TabEnvolvente (para trazar la
        # curva sobre ella).  Y el nombre de la EOS activa.
        self.get_envolvente = get_envolvente
        self.get_eos_nombre = get_eos_nombre
        self.worker = None
        self.last_result = None
        self._res_unit = None
        self._tipo_txt = None
        self._props_sel = list(_PROP_SAT_DEFAULT)
        self._on_props_resize = None
        self._curva_on = False
        self._build()

    # ══════════════════════════════════════════════════════════
    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root = QVBoxLayout(self)
        root.setContentsMargins(13, 9, 13, 5); root.setSpacing(3)

        title = QLabel("ThermoPhase — Formación de Hidratos")
        title.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_TIT)
        root.addWidget(title)

        # ── Panel de entrada ──────────────────────────────────
        in_box = QFrame()
        in_box.setStyleSheet('background:transparent;border:none;')
        gl = QGridLayout(in_box); gl.setContentsMargins(6,4,6,4); gl.setSpacing(4)

        def lbl(txt, res=False):
            l = QLabel(txt)
            if res:
                l.setStyleSheet(
                    f'background:{WHITE};border:1px solid {BORDER};'
                    f'color:{TEXT_RES};padding:2px 6px;'
                    f'font-family:"{FONT_F}";font-size:{FS}pt;')
            else:
                l.setStyleSheet(
                    f'background:{GRAY_LBL};border:1px solid {BORDER};'
                    f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
            l.setFixedHeight(24)
            return l

        # Selector de tipo de cálculo
        gl.addWidget(lbl("Calcular:"), 0, 0)
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(list(self.TIPOS.keys()))
        self.cmb_tipo.setFixedHeight(24)
        _aplicar_estilo_combo(self.cmb_tipo)
        self.cmb_tipo.currentTextChanged.connect(self._on_tipo_change)
        gl.addWidget(self.cmb_tipo, 0, 1)

        # Etiqueta + campo de condición (P o T)
        self.lbl_cond = lbl("Presion (psi):")
        self.lbl_cond.setFixedWidth(130)
        gl.addWidget(self.lbl_cond, 1, 0)
        self.sp_cond = QDoubleSpinBox()
        self.sp_cond.setRange(0.0, 15000.0); self.sp_cond.setDecimals(2)
        self.sp_cond.setSpecialValueText(" "); self.sp_cond.setValue(0.0)
        self.sp_cond.setFixedHeight(24)
        self.sp_cond.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_cond.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gl.addWidget(self.sp_cond, 1, 1)

        # Botón calcular
        self.btn = QPushButton("Calcular formacion de hidrato")
        self.btn.setStyleSheet(BTN_STYLE); self.btn.setFixedHeight(24)
        self.btn.clicked.connect(self.calcular)
        gl.addWidget(self.btn, 2, 0, 1, 2)

        gl.setColumnStretch(0,0); gl.setColumnStretch(1,1)

        # ── Panel de resultados ───────────────────────────────
        res_outer = QVBoxLayout(); res_outer.setSpacing(3)
        res_title = QLabel("Resultado:")
        res_title.setStyleSheet(LBL_SEC); res_title.setFixedHeight(20)
        res_outer.addWidget(res_title)

        res_box = QFrame()
        res_box.setStyleSheet('background:transparent;border:none;')
        rl = QGridLayout(res_box); rl.setContentsMargins(6,3,6,3); rl.setSpacing(3)

        self.lbl_res_label = lbl("Temperatura de hidrato (°F):")
        rl.addWidget(self.lbl_res_label, 0, 0)
        self.lbl_res_val = lbl("", res=True); self.lbl_res_val.setFixedWidth(120)
        self.lbl_res_val.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.lbl_res_val, 0, 1)

        self.lbl_res2_label = lbl("Equivalente (°R / psi):")
        rl.addWidget(self.lbl_res2_label, 1, 0)
        self.lbl_res2_val = lbl("", res=True); self.lbl_res2_val.setFixedWidth(120)
        self.lbl_res2_val.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.lbl_res2_val, 1, 1)

        # Fila 2 (a la altura del botón "Calcular" del panel izquierdo): botón
        # para agregar/quitar la curva de hidratos sobre la envolvente. Ocupa
        # el hueco que en Puntos de saturación queda libre (donde esa pestaña
        # muestra el mensaje de convergencia), de modo que esta pestaña
        # mantiene EXACTAMENTE la misma altura.
        self.btn_curva = QPushButton("Agregar curva de formacion de hidrato")
        self.btn_curva.setStyleSheet(BTN_STYLE); self.btn_curva.setFixedHeight(24)
        self.btn_curva.clicked.connect(self._toggle_curva)
        rl.addWidget(self.btn_curva, 2, 0, 1, 2)

        # El estado (convergencia / estructura) NO se muestra como texto suelto
        # como en saturación: el resultado ya deja claro el punto calculado y la
        # estructura se anexa al valor. Se conserva el atributo para no romper
        # las llamadas existentes, pero oculto y sin reservar espacio.
        self.lbl_estado = QLabel("")
        self.lbl_estado.setVisible(False)

        rl.setColumnStretch(0,1); rl.setColumnStretch(1,0)
        res_outer.addWidget(res_box)

        # Layout horizontal entrada + resultado
        top_row = QHBoxLayout(); top_row.setSpacing(10); top_row.setContentsMargins(0,0,0,0)
        in_wrap = QVBoxLayout(); in_wrap.setSpacing(3)
        in_title = QLabel("Datos de entrada:")
        in_title.setStyleSheet(LBL_SEC); in_title.setFixedHeight(20)
        in_wrap.addWidget(in_title)
        in_wrap.addWidget(in_box)
        top_row.addLayout(in_wrap, 1)
        top_row.addLayout(res_outer, 1)
        root.addLayout(top_row)

        # ── Tabla de composición de fases (flash) ─────────────
        comp_title = QLabel("Composicion de las fases en equilibrio:")
        comp_title.setStyleSheet(LBL_SEC); comp_title.setFixedHeight(22)
        root.addWidget(comp_title)

        self.tbl = QTableWidget(NC+1, 4)
        self.tbl.setHorizontalHeaderLabels(
            ["Componente","Mezcla","Fase Vapor","Fase Liquida"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        hh = self.tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(1,120)
        self.tbl.setColumnWidth(2,120); self.tbl.setColumnWidth(3,120)
        self.tbl.verticalHeader().setDefaultSectionSize(22)
        self.tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        GRIS_NOMBRE = QColor(GRAY_LBL); GRIS_RES = QColor(GRAY_RES)
        for i in range(NC):
            it = QTableWidgetItem(NOMBRES[i].rstrip(':'))
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS_NOMBRE))
            self.tbl.setItem(i,0,it)
            for c in (1,2,3):
                cell = QTableWidgetItem("")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cell.setBackground(QBrush(GRIS_RES))
                self.tbl.setItem(i,c,cell)
        sit = QTableWidgetItem("Sumatorias:")
        sit.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        sit.setBackground(QBrush(GRIS_NOMBRE))
        self.tbl.setItem(NC,0,sit)
        for c in (1,2,3):
            cell = QTableWidgetItem("")
            cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            cell.setBackground(QBrush(GRIS_RES))
            self.tbl.setItem(NC,c,cell)
        root.addWidget(self.tbl)

        # ── Tabla de propiedades del punto ────────────────────
        prop_hdr = QHBoxLayout(); prop_hdr.setContentsMargins(0,0,0,0); prop_hdr.setSpacing(6)
        prop_title = QLabel("Propiedades del punto de hidrato:")
        prop_title.setStyleSheet(LBL_SEC); prop_title.setFixedHeight(22)
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

        self.tbl_prop = QTableWidget(0, 4)
        self.tbl_prop.setHorizontalHeaderLabels(
            ["Propiedad","Mezcla","Fase Vapor","Fase Liquida"])
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
        hp = self.tbl_prop.horizontalHeader()
        hp.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hp.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hp.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hp.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tbl_prop.setColumnWidth(1,120)
        self.tbl_prop.setColumnWidth(2,120); self.tbl_prop.setColumnWidth(3,120)
        self.tbl_prop.verticalHeader().setDefaultSectionSize(ROW_H)
        self.tbl_prop.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_prop.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_prop.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._rebuild_prop_table()
        root.addWidget(self.tbl_prop)

    # ══════════════════════════════════════════════════════════
    def showEvent(self, event):
        super().showEvent(event)
        self._fit_table_heights()

    def _fit_table_heights(self):
        for tbl, nrows in [(self.tbl, NC+1),
                           (self.tbl_prop, self.tbl_prop.rowCount())]:
            h = tbl.horizontalHeader().height()
            for r in range(nrows):
                h += tbl.rowHeight(r)
            h += 2*tbl.frameWidth()
            tbl.setFixedHeight(h)

    def aplicar_componentes(self, activos):
        act = set(activos)
        for i in range(NC):
            self.tbl.setRowHidden(i, i not in act)
        self._fit_table_heights()

    def _rebuild_prop_table(self):
        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        GRIS_NOMBRE = QColor(GRAY_LBL)   # nombre de propiedad (col 0)
        GRIS_VACIA  = QColor(GRAY_RES)   # celda de valor vacía (col 1 y 2)
        self.tbl_prop.setRowCount(len(sel))
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            self.tbl_prop.setRowHeight(r, ROW_H)
            unidad = f" [{_u.u(mag)}]" if mag else ""
            it = QTableWidgetItem(f"{_i18n.t(base)}{unidad}:")
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS_NOMBRE))
            self.tbl_prop.setItem(r, 0, it)
            for c in (1, 2, 3):
                cc = QTableWidgetItem("")
                cc.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cc.setBackground(QBrush(GRIS_VACIA))
                self.tbl_prop.setItem(r, c, cc)
        self._fit_table_heights()

    def _abrir_selector_props(self):
        # Reutiliza el mismo diálogo que la pestaña de saturación.
        from pestana_saturacion import TabSaturacion
        TabSaturacion._abrir_selector_props(self)

    # ══════════════════════════════════════════════════════════
    def _on_tipo_change(self, txt):
        modo, u_in, lbl_in, u_res = self.TIPOS.get(
            self._tipo_es_de(txt), ('T','P','Presion (psi):','T'))
        if u_in == 'P':
            self.lbl_cond.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
        else:
            self.lbl_cond.setText(f"{_i18n.t('Temperatura')} ({_u.u_abs()}):")
        self.sp_cond.setValue(0.0)

    def _tipo_es_de(self, txt):
        """Clave española del tipo dado el texto mostrado (traducible)."""
        try:
            inv = _i18n._TRAD_INV.get(txt, txt)
        except Exception:
            inv = txt
        return inv if inv in self.TIPOS else list(self.TIPOS.keys())[
            max(0, self.cmb_tipo.currentIndex())]

    def _tipo_es(self):
        return self._tipo_es_de(self.cmb_tipo.currentText())

    # ══════════════════════════════════════════════════════════
    def calcular(self):
        z = self.get_z()
        if abs(sum(z)-1.0) > 1e-3:
            dialogos.advertencia(self, "La suma de fracciones debe ser 1.0")
            return
        tipo_es = self._tipo_es()
        modo, u_in, lbl_in, u_res = self.TIPOS[tipo_es]
        val_ui = self.sp_cond.value()
        if val_ui <= 0.0:
            dialogos.advertencia(self, "Ingrese un valor de entrada válido.")
            return
        # Convertir el valor de entrada (en unidades de la UI) a internas.
        if u_in == 'P':
            valor = _u.p_a_psia(val_ui)
        else:
            valor = _u.R_desde_abs(val_ui)
        self._res_unit = u_res
        kij = self.get_kij()
        eos_nombre = self._eos_nombre()
        self.btn.setEnabled(False); self.btn.setText(_i18n.t("Calculando..."))
        self.worker = HidratoWorker(modo, valor, list(z), kij, eos_nombre)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _eos_nombre(self):
        if callable(self.get_eos_nombre):
            try:
                return self.get_eos_nombre()
            except Exception:
                pass
        return _eng.get_eos()

    def _on_error(self, msg):
        self.btn.setEnabled(True)
        self.btn.setText(_i18n.t("Calcular formacion de hidrato"))
        dialogos.error(self, msg)

    def _on_done(self, res):
        self.btn.setEnabled(True)
        self.btn.setText(_i18n.t("Calcular formacion de hidrato"))
        if not res:
            self.lbl_res_val.setText(""); self.lbl_res2_val.setText("")
            self.last_result = None
            dialogos.advertencia(self, _i18n.t(
                "No se encontró punto de formación de hidrato en el rango."))
            return
        self.last_result = res
        self._render(res)

    # ══════════════════════════════════════════════════════════
    def aplicar_unidades(self, old):
        """Convierte el valor de entrada, actualiza etiquetas y re-muestra el
        resultado en el sistema de unidades activo."""
        modo, u_in, lbl_in, u_res = self.TIPOS[self._tipo_es()]
        v = self.sp_cond.value()
        if v > 0:
            if u_in == 'P':
                v_int = _u.p_a_psia(v, old); self.sp_cond.setValue(_u.p_desde_psia(v_int))
            else:
                v_int = _u.R_desde_abs(v, old); self.sp_cond.setValue(_u.abs_desde_R(v_int))
        if u_in == 'P':
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
        if getattr(self, 'last_result', None) is not None:
            self._render(self.last_result)

    # ══════════════════════════════════════════════════════════
    def _render(self, res):
        self.last_result = res
        T = res['T_R']; P = res['P_psia']
        self._tipo_txt = self.cmb_tipo.currentText()
        if self._res_unit == 'T':
            self.lbl_res_label.setText(f"{_i18n.t('Temperatura de Hidrato')} ({_u.u('T')}):")
            self.lbl_res_val.setText(f"{_u.t_desde_R(T):.2f}")
            self.lbl_res2_label.setText(f"{_i18n.t('Equivalente')} ({_u.u_abs()}):")
            self.lbl_res2_val.setText(f"{_u.abs_desde_R(T):.2f}")
        else:
            self.lbl_res_label.setText(f"{_i18n.t('Presion de Hidrato')} ({_u.u('P')}):")
            self.lbl_res_val.setText(f"{_u.p_desde_psia(P):.2f}")
            self.lbl_res2_label.setText(f"{_i18n.t('Temperatura')} ({_u.u('T')}):")
            self.lbl_res2_val.setText(f"{_u.t_desde_R(T):.2f}")

        # ── Composición: Mezcla (col1) | Vapor (col2) | Líquido (col3) ──
        flash = res.get('flash', {}) or {}
        x = flash.get('x', [0]*NC); y = flash.get('y', [0]*NC)
        z = flash.get('z') or self.get_z()
        V = flash.get('V', None)
        hay_vap = (V is None) or (V > 1e-9)
        hay_liq = (V is None) or (V < 1.0 - 1e-9)
        sx = sum(x); sy = sum(y); sz = sum(z)
        VAC = QColor(GRAY_RES)   # celda sombreada (fase ausente / sin valor)
        BLN = QColor(WHITE)

        def _set(cell, txt, ok):
            if ok:
                cell.setText(txt); cell.setBackground(QBrush(BLN))
                cell.setForeground(QBrush(QColor(TEXT_RES)))
            else:
                cell.setText(""); cell.setBackground(QBrush(VAC))

        for i in range(NC):
            _set(self.tbl.item(i,1), f"{z[i]:.4f}", sz > 0)
            _set(self.tbl.item(i,2), f"{y[i]:.4f}", hay_vap)
            _set(self.tbl.item(i,3), f"{x[i]:.4f}", hay_liq)
        _set(self.tbl.item(NC,1), f"{sz:.4f}", sz > 0)
        _set(self.tbl.item(NC,2), f"{sy:.4f}", hay_vap)
        _set(self.tbl.item(NC,3), f"{sx:.4f}", hay_liq)

        # ── Propiedades: Mezcla | Vapor | Líquido ──
        import math as _math
        import eos as _eng
        p = res.get('props', {}) or {}
        import poder_calorifico as _pc
        _pc_v = _pc.poder_calorifico_fase(y, p.get('PM_v')) if hay_vap else {}
        _pc_l = _pc.poder_calorifico_fase(x, p.get('PM_l')) if hay_liq else {}
        _pc_z = _pc.poder_calorifico_fase(z, None) if sz > 0 else {}
        _gpm_v = _pc.gpm_c3(y) if hay_vap else None
        _gpm_z = _pc.gpm_c3(z) if sz > 0 else None
        _pm_z = sum(z[i]*_eng.PM[i] for i in range(NC)) if sz > 0 else None
        # Densidad de mezcla por regla de volúmenes de las fases presentes.
        _rho_z = None
        rho_v = p.get('rho_v'); rho_l = p.get('rho_l')
        Vm = flash.get('Vm'); Lm = flash.get('Lm')
        if hay_vap and hay_liq and rho_v and rho_l and Vm is not None and Lm is not None:
            inv = (Vm/rho_v if rho_v>0 else 0)+(Lm/rho_l if rho_l>0 else 0)
            if inv>0: _rho_z = 1.0/inv
        elif hay_liq and rho_l:
            _rho_z = rho_l
        elif hay_vap and rho_v:
            _rho_z = rho_v

        def _es_valido(v):
            return v is not None and not (isinstance(v, float)
                                          and (_math.isnan(v) or _math.isinf(v)))

        def _valor_prop(kf, phase_pc, conv, gpm_val, existe):
            if not existe:
                return None
            if isinstance(kf, str) and kf.startswith('PCAL:'):
                v = phase_pc.get(kf.split(':', 1)[1])
            elif isinstance(kf, str) and kf.startswith('GPM:'):
                v = gpm_val if kf == 'GPM:v' else None
            else:
                v = _conv_prop(conv, p.get(kf))
            return v if _es_valido(v) else None

        def _valor_mezcla(key, conv):
            if sz <= 0:
                return None
            if key == 'pm':        return _conv_prop(conv, _pm_z)
            if key == 'densidad':  return _conv_prop(conv, _rho_z) if _rho_z else None
            if key in ('hhv_mas','lhv_mas','hhv_vol','lhv_vol'):
                v = _pc_z.get(key); return v if _es_valido(v) else None
            if key == 'gpm':       return _gpm_z if _es_valido(_gpm_z) else None
            return None   # z, sg, entalpía, entropía, viscosidad: sin mezcla

        sel = [d for d in _PROP_SAT if d[0] in self._props_sel]
        for r, (key, base, mag, dec, kv, kl, conv) in enumerate(sel):
            unidad = f" [{_u.u(mag)}]" if mag else ""
            it_lbl = self.tbl_prop.item(r, 0)
            if it_lbl is not None:
                it_lbl.setText(f"{_i18n.t(base)}{unidad}:")
            vz = _valor_mezcla(key, conv)
            vv = _valor_prop(kv, _pc_v, conv, _gpm_v, hay_vap)
            vl = _valor_prop(kl, _pc_l, conv, None, hay_liq)
            fmt = f"{{:.{dec}f}}"
            for c, vw in ((1, vz), (2, vv), (3, vl)):
                cell = self.tbl_prop.item(r, c)
                if vw is not None:
                    cell.setText(fmt.format(vw))
                    cell.setForeground(QBrush(QColor(TEXT_RES)))
                    cell.setBackground(QBrush(BLN))
                else:
                    cell.setText("")
                    cell.setBackground(QBrush(VAC))

    # ══════════════════════════════════════════════════════════
    # Curva de hidratos sobre la envolvente
    # ══════════════════════════════════════════════════════════
    def _toggle_curva(self):
        env = self.get_envolvente() if callable(self.get_envolvente) else None
        if env is None:
            dialogos.advertencia(self,
                "Abra la ventana de Envolvente de fases para trazar la curva.")
            return
        self._curva_on = not self._curva_on
        env._get_eos_nombre = self._eos_nombre
        env.set_hidratos_activo(self._curva_on)
        self._actualizar_btn_curva()

    def _actualizar_btn_curva(self):
        if self._curva_on:
            self.btn_curva.setText(_i18n.t("Quitar curva de formacion de hidrato"))
        else:
            self.btn_curva.setText(_i18n.t("Agregar curva de formacion de hidrato"))

    # ══════════════════════════════════════════════════════════
    def get_estado(self):
        return {
            'entrada': {
                'tipo': self._tipo_es(),
                'valor': self.sp_cond.value(),
                'props': list(self._props_sel),
                'curva_on': self._curva_on,
            },
            'resultado': self.last_result,
        }

    def set_estado(self, datos):
        e = datos.get('entrada', {}) or {}
        tipo = e.get('tipo')
        if tipo in self.TIPOS:
            idx = list(self.TIPOS.keys()).index(tipo)
            self.cmb_tipo.setCurrentIndex(idx)
        props = e.get('props')
        if props:
            self._props_sel = [k for k, *_ in _PROP_SAT if k in props][:PROP_SAT_MAX]
            self._rebuild_prop_table()
        val = e.get('valor')
        if val:
            self.sp_cond.setValue(float(val))
        self._curva_on = bool(e.get('curva_on', False))
        self._actualizar_btn_curva()
        res = datos.get('resultado')
        if res:
            modo = self.TIPOS[self._tipo_es()][0]
            self._res_unit = self.TIPOS[self._tipo_es()][3]
            self.last_result = res
            self._render(res)

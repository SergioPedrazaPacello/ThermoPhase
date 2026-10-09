"""
pestana_saturacion_agua.py — Contenido de agua de saturación.

Agrega a la corriente (composición principal o fluido) exactamente el agua que
admite a una presión y temperatura sin formar agua libre: la fase acuosa
queda incipiente.  Es la opción "Saturate w. water" de PVTsim.  El cálculo lo
hace contenido_agua.saturar_exacto con la EOS de la corriente (flash
multifásico con Huron-Vidal).

Si la composición de entrada ya trae agua, se toma sólo su parte de
hidrocarburos para saturar y el agua ingresada se compara con la de
saturación: corriente subsaturada (falta agua) o con agua libre (sobra).

La composición saturada puede cargarse en la composición principal, en el
fluido analizado o guardarse como un fluido nuevo; al cargarla se activa el
agua en todo el programa.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QHeaderView,
                             QSizePolicy, QAbstractSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from eos import NOMBRES, NC
from numeros import SpinNum as _SpinNum
import dialogos
import idioma as _i18n
import eos as _eng
import unidades as _u
from pestana_saturacion import (
    WHITE, GRAY_TIT, GRAY_LBL, GRAY_EMPTY, BORDER, TEXT, TEXT_RES,
    FONT_F, FS, ROW_H, GridDelegate, BTN_STYLE, LBL_TIT, LBL_SEC,
)

TOL_SAT = 1e-3        # |agua ingresada / agua de saturación − 1| para "saturada"


class SatAguaWorker(QThread):
    done = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, z, T_R, P, eos):
        super().__init__()
        self.z = z; self.T_R = T_R; self.P = P; self.eos = eos

    def run(self):
        try:
            import contenido_agua as _ca
            prev = _eng.get_eos()
            try:
                r = _ca.saturar_exacto(self.z, self.T_R, self.P, self.eos)
            finally:
                _eng.set_eos(prev)
            self.done.emit(r or {})
        except Exception as ex:
            self.error.emit(str(ex))


class TabSaturacionAgua(QWidget):
    """Ventana de Saturación con agua.  `get_z` da la composición (14 comp.),
    `get_eos` el código de la EOS de la corriente.  `on_cargar(z, destino)`
    con destino 'principal', 'fluido' o 'nuevo'."""

    def __init__(self, get_z, get_eos, on_cargar=None, es_fluido=False):
        super().__init__()
        self.get_z = get_z; self.get_eos = get_eos
        self.on_cargar = on_cargar; self.es_fluido = es_fluido
        self.worker = None
        self.last_result = None          # dict con entrada + resultado
        self._activos = list(range(NC))
        self._build()

    # ══════════════════════════════════════════════════════════
    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root = QVBoxLayout(self)
        root.setContentsMargins(13, 9, 13, 5); root.setSpacing(3)
        title = QLabel("ThermoPhase — Contenido de agua de saturación")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_TIT)
        root.addWidget(title)

        def lbl(txt, res=False, w=None):
            l = QLabel(txt)
            l.setStyleSheet(
                (f'background:{WHITE};color:{TEXT_RES};' if res else f'background:{GRAY_LBL};')
                + f'border:1px solid {BORDER};padding:2px 6px;'
                  f'font-family:"{FONT_F}";font-size:{FS}pt;')
            l.setFixedHeight(24)
            if res:
                l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if w:
                l.setFixedWidth(w)
            return l

        def spin(lo, hi):
            s = _SpinNum(); s.setRange(lo, hi); s.setDecimals(2)
            s.setSpecialValueText(" "); s.setValue(lo)
            s.setFixedHeight(24)
            s.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            s.setStyleSheet(f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
                            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
            return s

        # ── Entrada ──────────────────────────────────────────
        in_wrap = QVBoxLayout(); in_wrap.setSpacing(3)
        t_in = QLabel("Datos de entrada:"); t_in.setStyleSheet(LBL_SEC); t_in.setFixedHeight(20)
        in_wrap.addWidget(t_in)
        in_box = QFrame(); in_box.setStyleSheet('background:transparent;border:none;')
        gl = QGridLayout(in_box); gl.setContentsMargins(6, 4, 6, 4); gl.setSpacing(4)
        self.lbl_P = lbl(""); self.lbl_P.setFixedWidth(130)
        self.lbl_T = lbl(""); self.lbl_T.setFixedWidth(130)
        self.sp_P = spin(0.0, 999999.0)
        self.sp_T = spin(-999.0, 9999.0); self.sp_T.setSpecialValueText("")
        self.sp_T.setValue(-999.0)
        gl.addWidget(self.lbl_P, 0, 0); gl.addWidget(self.sp_P, 0, 1)
        gl.addWidget(self.lbl_T, 1, 0); gl.addWidget(self.sp_T, 1, 1)
        self.btn = QPushButton("Calcular contenido de agua")
        self.btn.setStyleSheet(BTN_STYLE); self.btn.setFixedHeight(24)
        self.btn.clicked.connect(self.calcular)
        gl.addWidget(self.btn, 2, 0, 1, 2)
        # Carga de la composición saturada, debajo del botón de cálculo:
        # en la corriente que se analiza (composición principal o fluido) o
        # como un fluido nuevo.
        self.btn_cargar = QPushButton("Cargar en la composición actual")
        self.btn_nuevo = QPushButton("Guardar como fluido nuevo")
        destino = 'fluido' if self.es_fluido else 'principal'
        for r_, (b_, dest) in enumerate(((self.btn_cargar, destino),
                                         (self.btn_nuevo, 'nuevo')), 3):
            b_.setStyleSheet(BTN_STYLE); b_.setFixedHeight(24); b_.setEnabled(False)
            b_.clicked.connect(lambda _=False, d=dest: self._cargar(d))
            gl.addWidget(b_, r_, 0, 1, 2)
        gl.setColumnStretch(1, 1)
        in_wrap.addWidget(in_box); in_wrap.addStretch()

        # ── Resultado (a la derecha) ─────────────────────────
        res_wrap = QVBoxLayout(); res_wrap.setSpacing(3)
        t_res = QLabel("Resultado:"); t_res.setStyleSheet(LBL_SEC); t_res.setFixedHeight(20)
        res_wrap.addWidget(t_res)
        res_box = QFrame(); res_box.setStyleSheet('background:transparent;border:none;')
        rl = QGridLayout(res_box); rl.setContentsMargins(6, 3, 6, 3); rl.setSpacing(3)
        self._res = {}
        filas = [('estado', "Estado de la corriente:"),
                 ('fases', "Fases de hidrocarburo:"),
                 ('sat', "Agua de saturación [porcentaje molar]:"),
                 ('ing', "Agua ingresada [porcentaje molar]:"),
                 ('dif', "Diferencia [porcentaje molar]:"),
                 ('cont', "Contenido de agua del gas saturado [lb/MMscf]:")]
        for r_, (k, txt) in enumerate(filas):
            a_ = lbl(txt); b_ = lbl("", res=True, w=120)
            rl.addWidget(a_, r_, 0); rl.addWidget(b_, r_, 1)
            self._res[k] = (a_, b_)
        rl.setColumnStretch(0, 1)
        res_wrap.addWidget(res_box); res_wrap.addStretch()

        top = QHBoxLayout(); top.setSpacing(10)
        top.addLayout(in_wrap, 1); top.addLayout(res_wrap, 1)
        root.addLayout(top)

        # ── Composición ─────────────────────────────────────
        t_c = QLabel("Composición de la corriente:"); t_c.setStyleSheet(LBL_SEC)
        t_c.setFixedHeight(22)
        root.addWidget(t_c)
        self.tbl = QTableWidget(NC + 2, 3)
        self.tbl.setHorizontalHeaderLabels(
            ["Componente", "Composición de entrada", "Composición saturada"])
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
        for c in (1, 2):
            hh.setSectionResizeMode(c, QHeaderView.ResizeMode.Fixed)
            self.tbl.setColumnWidth(c, 150)
        self.tbl.verticalHeader().setDefaultSectionSize(ROW_H)
        self.tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gris = QBrush(QColor(GRAY_LBL))
        for i in range(NC + 2):
            if i < NC:
                nom = NOMBRES[i].rstrip(':')
            elif i == NC:
                nom = _eng.componente_etiqueta(_eng.IDX_AGUA).rstrip(':')
            else:
                nom = "Sumatorias:"
            it = QTableWidgetItem(nom)
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(gris)
            self.tbl.setItem(i, 0, it)
            for c in (1, 2):
                v = QTableWidgetItem("")
                v.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                v.setBackground(QBrush(QColor(GRAY_EMPTY)))
                self.tbl.setItem(i, c, v)
        root.addWidget(self.tbl)

        root.addStretch()
        self._retitular()
        self._fit()

    # ══════════════════════════════════════════════════════════
    def _retitular(self):
        self.lbl_P.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
        self.lbl_T.setText(f"{_i18n.t('Temperatura')} ({_u.u('T')}):")

    def _fit(self):
        h = self.tbl.horizontalHeader().height() or 26
        for r in range(self.tbl.rowCount()):
            if not self.tbl.isRowHidden(r):
                h += self.tbl.rowHeight(r)
        self.tbl.setFixedHeight(h + 2*self.tbl.frameWidth())

    def showEvent(self, ev):
        super().showEvent(ev)
        self._fit()

    def aplicar_componentes(self, activos):
        """Muestra los hidrocarburos activos.  La fila del agua se ve siempre:
        es la que agrega la saturación."""
        self._activos = list(activos)
        act = set(activos)
        for i in range(NC):
            self.tbl.setRowHidden(i, i not in act)
        self._fit()

    def alto_ideal(self):
        self._fit()
        return self.sizeHint().height()

    # ══════════════════════════════════════════════════════════
    def set_condiciones(self, P_psia, T_R):
        self.sp_P.setValue(_u.p_desde_psia(P_psia))
        self.sp_T.setValue(_u.t_desde_R(T_R))

    def _leer(self):
        P = self.sp_P.value(); T = self.sp_T.value()
        if P <= 0 or self.sp_T.text().strip() == "":
            return None
        P = _u.p_a_psia(P); T_R = _u.t_a_F(T) + 459.67
        if P <= 0 or T_R <= 0:
            return None
        return P, T_R

    def calcular(self):
        if self.worker is not None and self.worker.isRunning():
            return
        pt = self._leer()
        if pt is None:
            dialogos.advertencia(self, _i18n.t("Ingrese la presion y la temperatura."))
            return
        z = list(self.get_z())
        z = z + [0.0]*(NC + 1 - len(z))
        if sum(z[:NC]) <= 1e-12:
            dialogos.advertencia(self, _i18n.t("La mezcla no contiene hidrocarburos."))
            return
        if abs(sum(z) - 1.0) > 1e-3:
            dialogos.advertencia(self, _i18n.t(
                "La composicion debe sumar 1 (fraccion molar) o 100 (porcentaje molar)"))
            return
        P, T_R = pt
        self._pend = {'z_in': [float(v) for v in z], 'P': P, 'T_R': T_R}
        self.btn.setEnabled(False); self.btn.setText(_i18n.t("Calculando..."))
        self.worker = SatAguaWorker(z, T_R, P, self.get_eos())
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _fin_boton(self):
        self.btn.setEnabled(True)
        self.btn.setText(_i18n.t("Calcular contenido de agua"))

    def _on_error(self, msg):
        self._fin_boton()
        dialogos.error(self, msg)

    def _on_done(self, res):
        self._fin_boton()
        if not res or not res.get('z_sat'):
            dialogos.advertencia(self, _i18n.t(
                "No se pudo saturar la corriente con agua a estas condiciones."))
            return
        r = dict(self._pend); r.update(res)
        self.last_result = r
        self._render()

    # ══════════════════════════════════════════════════════════
    def _render(self):
        r = self.last_result
        for c in (1, 2):
            for i in range(NC + 2):
                self.tbl.item(i, c).setText("")
        if not r:
            for k, (_a, b) in self._res.items():
                b.setText("")
            for b in (self.btn_cargar, self.btn_nuevo):
                b.setEnabled(False)
            return
        z_in = r['z_in']; z_sat = r['z_sat']
        for col, z in ((1, z_in), (2, z_sat)):
            for i in range(NC + 1):
                it = self.tbl.item(i, col)
                it.setText(f"{z[i]:.6f}" if i == NC else f"{z[i]:.4f}")
                it.setForeground(QBrush(QColor(TEXT if col == 1 else TEXT_RES)))
                it.setBackground(QBrush(QColor(WHITE)))
            s = self.tbl.item(NC + 1, col)
            s.setText(f"{sum(z[:NC + 1]):.4f}")
            s.setBackground(QBrush(QColor(WHITE)))
        w_in = z_in[NC]; w_sat = z_sat[NC]; r_sat = r['r_sat']
        r_in = w_in/(1.0 - w_in) if w_in < 1 else float('inf')
        if w_in <= 1e-12:
            estado = "Sin agua"
        elif abs(r_in/r_sat - 1.0) <= TOL_SAT:
            estado = "Saturada"
        elif r_in < r_sat:
            estado = "Subsaturada"
        else:
            estado = "Con agua libre"
        # diferencia en moles de agua por 100 moles de corriente de entrada:
        # + falta agua para saturar, − agua libre que sobra
        dif = (r_sat - r_in)*(1.0 - w_in)*100.0
        bV, bL = r.get('beta_V', 0.0), r.get('beta_L', 0.0)
        if bV > 1e-9 and bL > 1e-9:
            fases = "Vapor y líquido"
        elif bV > 1e-9:
            fases = "Vapor"
        else:
            fases = "Líquido"
        self._res['estado'][1].setText(_i18n.t(estado))
        self._res['sat'][1].setText(f"{w_sat*100:.5f}")
        self._res['ing'][1].setText(f"{w_in*100:.5f}")
        self._res['dif'][0].setText(_i18n.t(
            "Agua libre en exceso [porcentaje molar]:" if dif < 0 and w_in > 1e-12
            else "Agua faltante [porcentaje molar]:"))
        self._res['dif'][1].setText(f"{abs(dif):.5f}" if estado != "Saturada" else "0.00000")
        cont = r.get('cont_gas')
        self._res['cont'][1].setText("" if cont is None else f"{cont:.2f}")
        self._res['fases'][1].setText(_i18n.t(fases))
        for b in (self.btn_cargar, self.btn_nuevo):
            b.setEnabled(True)

    def _cargar(self, destino):
        if self.last_result and self.on_cargar:
            self.on_cargar(list(self.last_result['z_sat']), destino)

    # ══════════════════════════════════════════════════════════
    def aplicar_unidades(self, old=None):
        if old is not None:
            try:
                if self.sp_P.value() > 0:
                    self.sp_P.setValue(_u.p_desde_psia(_u.p_a_psia(self.sp_P.value(), old)))
                if self.sp_T.text().strip():
                    self.sp_T.setValue(_u.t_desde_F(_u.t_a_F(self.sp_T.value(), old)))
            except Exception:
                pass
        self._retitular()

    def retraducir_grafico(self):
        self._retitular()
        self.btn.setText(_i18n.t("Calcular contenido de agua"))
        self._render()

    def get_estado(self):
        pt = self._leer()
        return {'entrada': {'P_psi': pt[0] if pt else 0.0, 'T_R': pt[1] if pt else 0.0},
                'resultado': self.last_result}

    def set_estado(self, datos):
        e = (datos or {}).get('entrada', {}) or {}
        P = float(e.get('P_psi', 0.0) or 0.0); T = float(e.get('T_R', 0.0) or 0.0)
        if P > 0 and T > 0:
            self.set_condiciones(P, T)
        self.last_result = (datos or {}).get('resultado')
        self._render()

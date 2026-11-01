"""
pestana_orificio_serie.py — Serie de tiempo del medidor de orificio.

Ventana con la tabla de mediciones que cambian con el tiempo (presión
estática, presión diferencial y temperatura), que se pega desde Excel, y
la columna de caudal calculada fila por fila con los datos fijos de la
ventana del medidor (geometría, materiales, condiciones base, factor Z,
cromatografía).  La hora de cada fila sale de la hora de inicio y del
intervalo entre mediciones.  El caudal se grafica contra la hora y se
resumen el promedio, el mínimo, el máximo y el volumen acumulado.
"""
import datetime as _dt

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                             QPushButton, QComboBox, QLineEdit, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QDateTimeEdit,
                             QApplication, QFileDialog, QFrame, QProgressDialog)
from PyQt6.QtCore import Qt, QDateTime, QTime
from PyQt6.QtGui import QKeySequence, QBrush, QColor

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates

import idioma as _i18n
import dialogos
import aga3 as ag
import pestana_op_unitarias as po

INTERVALOS = [("s", 1.0), ("min", 60.0), ("h", 3600.0)]
# Volumen acumulado: unidad de caudal → (unidad de volumen, segundos por unidad de tiempo)
VOLUMEN = {"MMscfd": ("MMscf", 86400.0), "MCF/d": ("MCF", 86400.0), "scf/h": ("scf", 3600.0),
           "E3M3/d": ("E3M3", 86400.0), "Sm³/d": ("Sm³", 86400.0), "Sm³/h": ("Sm³", 3600.0),
           "kg/h": ("kg", 3600.0), "lb/h": ("lb", 3600.0)}
from pestana_propiedades import GRAY_PLOT_BG   # fondo de gráfico común
from pestana_propiedades import CURVA_LW      # grosor de curva común a los gráficos
FILAS_INI = 1


def _f(t):
    return po._a_float(t)


class _Tabla(QTableWidget):
    """Tabla que acepta pegar bloques copiados de Excel (Ctrl+V) y borrar
    la selección (Supr)."""

    def __init__(self, dueño):
        super().__init__(0, 5)
        self.dueño = dueño

    def keyPressEvent(self, ev):
        if ev.matches(QKeySequence.StandardKey.Paste):
            self.dueño.pegar()
            return
        if ev.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for it in self.selectedItems():
                if it.column() in (1, 2, 3):
                    it.setText("")
            return
        super().keyPressEvent(ev)


class VentanaSerie(QDialog):
    def __init__(self, orificio):
        super().__init__(orificio, Qt.WindowType.Window | Qt.WindowType.WindowTitleHint
                         | Qt.WindowType.WindowCloseButtonHint
                         | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.ori = orificio
        self.Q = []                 # (qm, Qb) por fila o None
        self.setWindowTitle(_i18n.t("Serie de tiempo — Medidor de orificio"))
        self.setStyleSheet('QDialog { background:#e0e0e0; }')
        root = QVBoxLayout(self); root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)
        root.addWidget(po._titulo("ThermoPhase — " + _i18n.t("Serie de tiempo")))
        cols = QHBoxLayout(); cols.setSpacing(12); root.addLayout(cols)

        # ── Izquierda: configuración y tabla ───────────────────────────
        c1 = QVBoxLayout(); c1.setSpacing(4)
        g = QGridLayout(); g.setSpacing(4)
        self.dt_ini = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_ini.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dt_ini.setCalendarPopup(True)
        hoy = QDateTime.currentDateTime(); hoy.setTime(QTime(0, 0))
        self.dt_ini.setDateTime(hoy)
        self.dt_ini.setFixedSize(150, 22); self.dt_ini.setStyleSheet(po.ED_QSS.replace('QLineEdit', 'QDateTimeEdit'))
        g.addWidget(self._etq("Hora de inicio:"), 0, 0); g.addWidget(self.dt_ini, 0, 1)
        self.e_int = QLineEdit("1"); self.e_int.setStyleSheet(po.ED_QSS); self.e_int.setFixedSize(70, 22)
        self.e_int.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.c_int = self._combo([n for n, _s in INTERVALOS], 76); self.c_int.setCurrentIndex(1)
        hi = QHBoxLayout(); hi.setSpacing(4); hi.addWidget(self.e_int); hi.addWidget(self.c_int); hi.addStretch(1)
        g.addWidget(self._etq("Intervalo de medición:"), 1, 0); g.addLayout(hi, 1, 1)
        import pestana_orificio as _por
        self.U_Q = _por.U_Q
        self.c_Qu = self._combo([n for n, _f in self.U_Q], 150)
        self.c_Qu.setCurrentIndex(self.ori.c_Qu.currentIndex())
        g.addWidget(self._etq("Unidad del caudal:"), 2, 0); g.addWidget(self.c_Qu, 2, 1)
        g.setColumnStretch(2, 1)
        c1.addLayout(g)

        t = self.tbl = _Tabla(self)
        t.verticalHeader().setDefaultSectionSize(20)
        hqss = (f'QHeaderView {{ background:{po.WHITE}; border:none; }}'
                f'QHeaderView::section {{ background:{po.GRAY_LBL}; color:#000000;'
                f' font-family:"{po.FONT_F}"; font-size:{po.FS}pt; font-weight:normal;'
                f' border:none; border-right:1px solid {po.BORDER};'
                f' border-bottom:1px solid {po.BORDER}; padding:2px 4px; }}')
        for hd in (t.horizontalHeader(), t.verticalHeader()):
            hd.setStyleSheet(hqss)
            hd.setHighlightSections(False)          # sin negrita al seleccionar
            f_ = hd.font(); f_.setBold(False); hd.setFont(f_)
        t.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setCornerButtonEnabled(False)
        # Rejilla plana de 1 px (como las demás tablas del programa)
        t.setShowGrid(False)
        from pestana_saturacion import GridDelegate
        t.setItemDelegate(GridDelegate(po.BORDER, t))
        t.setStyleSheet(f'QTableWidget {{ background:{po.WHITE}; font-family:"{po.FONT_F}";'
                        f' font-size:{po.FS}pt; border:none; border-top:1px solid {po.BORDER};'
                        f' border-left:1px solid {po.BORDER};'
                        f' selection-background-color:{po.SEL_BG}; selection-color:#000000; }}'
                        f'QTableCornerButton::section {{ background:{po.GRAY_LBL}; border:none;'
                        f' border-right:1px solid {po.BORDER}; border-bottom:1px solid {po.BORDER}; }}')
        t.setProperty('pegado_propio', True)     # Ctrl+V y Supr los maneja esta tabla
        t.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        for c, w in enumerate((118, 104, 104, 104, 112)):
            t.setColumnWidth(c, w)
        t.verticalHeader().setFixedWidth(42)
        t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        t.horizontalHeader().setStretchLastSection(True)   # la barra, si aparece, no corta columnas
        t.setFixedWidth(sum((118, 104, 104, 104, 112)) + 42 + 20)
        t.setFixedHeight(560)
        c1.addWidget(t, 1)
        fb = QHBoxLayout(); fb.setSpacing(6)
        self.b_pegar = QPushButton(_i18n.t("Pegar desde Excel"))
        self.b_limpiar = QPushButton(_i18n.t("Limpiar"))
        self.b_calc = QPushButton(_i18n.t("Calcular"))
        self.b_graf = QPushButton(_i18n.t("Graficar"))
        self.b_resumen = QPushButton(_i18n.t("Resumen"))
        self.b_csv = QPushButton(_i18n.t("Exportar CSV"))
        for b in (self.b_pegar, self.b_limpiar, self.b_calc, self.b_graf, self.b_resumen, self.b_csv):
            b.setFixedHeight(26); b.setStyleSheet(po.BTN_QSS)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        for b in (self.b_limpiar, self.b_calc, self.b_graf, self.b_resumen, self.b_csv):
            b.setFixedWidth(86)                 # mismo ancho (salvo «Pegar desde Excel»)
        fb.addWidget(self.b_pegar); fb.addStretch(1); fb.addWidget(self.b_limpiar)
        fb.addWidget(self.b_calc); fb.addWidget(self.b_graf); fb.addWidget(self.b_resumen)
        fb.addWidget(self.b_csv)
        c1.addLayout(fb)
        cols.addLayout(c1)
        self.v_graf = None; self.v_res = None

        self.b_pegar.clicked.connect(self.pegar)
        self.b_limpiar.clicked.connect(self.limpiar)
        self.b_calc.clicked.connect(self.calcular)
        self.b_csv.clicked.connect(self.exportar_csv)
        self.b_graf.clicked.connect(self.graficar)
        self.b_resumen.clicked.connect(self.resumen)
        self.c_Qu.currentIndexChanged.connect(lambda _i: self._render())
        self.dt_ini.dateTimeChanged.connect(lambda _d: self._render())
        self.e_int.textEdited.connect(lambda _t: self._render())
        self.c_int.currentIndexChanged.connect(lambda _i: self._render())
        t.itemChanged.connect(self._on_item)
        self._filas(FILAS_INI)
        self.actualizar_encabezados()
        self._render()
        self.adjustSize(); self.setFixedSize(self.sizeHint())     # tamaño fijo

    # ── helpers ─────────────────────────────────────────────────────────
    def _etq(self, t):
        l = QLabel(_i18n.t(t)); l.setStyleSheet(po.LBL_QSS); l.setFixedHeight(22)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        l.setMinimumWidth(160)
        return l

    def _combo(self, items, w):
        c = QComboBox(); c.setFixedSize(w, 22); self.ori.h['estilo_combo'](c)
        c.addItems([_i18n.t(x) for x in items])
        return c

    def actualizar_encabezados(self):
        """Encabezados con las unidades elegidas en la ventana del medidor."""
        o = self.ori
        self.tbl.setHorizontalHeaderLabels([
            _i18n.t("Hora"),
            f"{_i18n.t('P. estática')}\n[{o.f_P.nombre()}]",
            f"{_i18n.t('P. diferencial')}\n[{o.f_dP.nombre()}]",
            f"{_i18n.t('Temperatura')}\n[{o.f_T.nombre()}]",
            f"{_i18n.t('Caudal')}\n[{self.c_Qu.currentText()}]"])

    def _filas(self, n):
        t = self.tbl
        t.blockSignals(True)
        r0 = t.rowCount()
        t.setRowCount(max(n, r0))
        for r in range(r0, t.rowCount()):
            for c in range(5):
                it = QTableWidgetItem("")
                it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if c in (0, 4):
                    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    it.setBackground(QBrush(QColor(po.GRAY_EMPTY)))
                    it.setForeground(QBrush(QColor(po.TEXT_RES if c == 4 else '#000000')))
                t.setItem(r, c, it)
        t.blockSignals(False)

    def _on_item(self, it):
        # Al escribir en la última fila se habilita una fila nueva debajo
        if it.column() in (1, 2, 3) and it.text().strip() and it.row() == self.tbl.rowCount() - 1:
            self._filas(self.tbl.rowCount() + 1)
            self._render()
        if it.column() in (1, 2, 3) and self.Q:
            self.Q = []                     # datos cambiados: el caudal queda pendiente
            self._render()

    # ── pegado ──────────────────────────────────────────────────────────
    def pegar(self):
        txt = QApplication.clipboard().text()
        if not txt.strip():
            return
        lineas = [l for l in txt.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
        while lineas and not lineas[-1].strip():
            lineas.pop()
        t = self.tbl
        r0 = max(t.currentRow(), 0)
        c0 = t.currentColumn()
        c0 = c0 if c0 in (1, 2, 3) else 1
        self._filas(r0 + len(lineas) + 1)
        t.blockSignals(True)
        for k, l in enumerate(lineas):
            celdas = l.split('\t') if '\t' in l else l.split(';')
            for j, v in enumerate(celdas):
                c = c0 + j
                if c > 3:
                    break
                t.item(r0 + k, c).setText(v.strip())
        t.blockSignals(False)
        self.Q = []
        self._render()

    def limpiar(self):
        self.tbl.setRowCount(0)
        self._filas(FILAS_INI)
        self.Q = []
        self._render()

    # ── datos ───────────────────────────────────────────────────────────
    def _datos(self):
        """[(fila, P, dP, T)] de las filas con los tres valores."""
        t = self.tbl; out = []
        for r in range(t.rowCount()):
            v = [_f(t.item(r, c).text()) for c in (1, 2, 3)]
            if all(x is not None for x in v):
                out.append((r, *v))
        return out

    def _ultima_fila(self):
        t = self.tbl; u = -1
        for r in range(t.rowCount()):
            if any(t.item(r, c).text().strip() for c in (1, 2, 3)):
                u = r
        return u

    def _tiempos(self, n):
        v = _f(self.e_int.text())
        paso = (v if v and v > 0 else 1.0)*INTERVALOS[self.c_int.currentIndex()][1]
        t0 = self.dt_ini.dateTime().toPyDateTime()
        return [t0 + _dt.timedelta(seconds=paso*i) for i in range(n)], paso

    # ── cálculo ─────────────────────────────────────────────────────────
    def calcular(self):
        o = self.ori
        self.actualizar_encabezados()
        try:
            spec = o._leer(serie=True)
        except ValueError as ex:
            dialogos.advertencia(self, _i18n.t(str(ex)))
            return
        datos = self._datos()
        if not datos:
            dialogos.advertencia(self, _i18n.t("Pegue o escriba las mediciones en la tabla."))
            return
        uP, udP, uT = (o.f_P.u[o.f_P.c.currentIndex()], o.f_dP.u[o.f_dP.c.currentIndex()],
                       o.f_T.u[o.f_T.c.currentIndex()])
        gauge = o.f_P.nombre().endswith('g')
        Patm = o.f_Patm.si() if gauge else 0.0
        if gauge and Patm is None:
            dialogos.advertencia(self, _i18n.t("Ingrese la presión atmosférica."))
            return
        try:
            m = ag.Medidor(spec)
        except Exception as ex:
            dialogos.error(self, str(ex))
            return
        n = self._ultima_fila() + 1
        Q = [None]*n
        prog = None
        if len(datos) > 200 or spec['z_metodo'] == 'EOS':
            prog = QProgressDialog(_i18n.t("Calculando..."), _i18n.t("Cancelar"), 0, len(datos), self)
            prog.setWindowModality(Qt.WindowModality.WindowModal); prog.setMinimumDuration(300)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        errores = 0
        try:
            for k, (r, P, dP, T) in enumerate(datos):
                if prog is not None:
                    prog.setValue(k)
                    if prog.wasCanceled():
                        break
                Pa = uP[1](P) + Patm
                dPa = udP[1](dP)
                Tk = uT[1](T)
                if dPa <= 0:
                    Q[r] = (0.0, 0.0)           # sin diferencial: sin flujo
                    continue
                m.s['P_f'] = Pa; m.s['T_f'] = Tk; m.s['dP'] = dPa
                try:
                    q = m.evaluar(spec['d_ref'], dPa, 'aga3')
                    Q[r] = (q['qm'], q['Qb'])
                except Exception:
                    errores += 1
        finally:
            QApplication.restoreOverrideCursor()
            if prog is not None:
                prog.close()
        self.Q = Q
        self._render()
        if errores:
            dialogos.advertencia(self, f"{errores} " + _i18n.t("filas no tienen solución (revise la presión diferencial y la presión estática)."))

    # ── presentación ────────────────────────────────────────────────────
    def _valores(self):
        f = self.U_Q[self.c_Qu.currentIndex()][1]
        return [None if q is None else f(*q) for q in self.Q]

    def _render(self):
        self.actualizar_encabezados()
        t = self.tbl
        n = max(self._ultima_fila() + 1, len(self.Q))
        tiempos, paso = self._tiempos(max(n, 1))
        con_s = paso < 60.0
        fmt = "%d/%m %H:%M:%S" if con_s else "%d/%m/%Y %H:%M"
        vals = self._valores()
        t.blockSignals(True)
        for r in range(t.rowCount()):
            t.item(r, 0).setText(tiempos[r].strftime(fmt) if r < n else "")
            v = vals[r] if r < len(vals) else None
            t.item(r, 4).setText(f"{v:.6g}" if v is not None else "")
        t.blockSignals(False)
        if self.v_graf is not None and self.v_graf.isVisible():
            self.v_graf.dibujar()
        if self.v_res is not None and self.v_res.isVisible():
            self.v_res.llenar()

    def serie(self):
        """(tiempos, valores, paso, unidad) de las filas con caudal calculado."""
        n = max(self._ultima_fila() + 1, len(self.Q))
        tiempos, paso = self._tiempos(max(n, 1))
        vals = self._valores()
        pares = [(tiempos[i], v) for i, v in enumerate(vals) if v is not None and i < len(tiempos)]
        return [p[0] for p in pares], [p[1] for p in pares], paso, self.c_Qu.currentText()

    def estadisticas(self):
        _x, ys, paso, un = self.serie()
        if not ys:
            return []
        vu, seg = VOLUMEN.get(un, ("", 1.0))
        return [("Mediciones", f"{len(ys)}", ""),
                ("Promedio", f"{sum(ys)/len(ys):.6g}", un),
                ("Mínimo", f"{min(ys):.6g}", un),
                ("Máximo", f"{max(ys):.6g}", un),
                ("Volumen acumulado", f"{sum(ys)*paso/seg:.6g}", vu)]

    def _sin_datos(self):
        if not any(q is not None for q in self.Q):
            dialogos.advertencia(self, _i18n.t("Primero calcule el caudal de la serie."))
            return True
        return False

    def graficar(self):
        if self._sin_datos():
            return
        if self.v_graf is None:
            self.v_graf = VentanaGrafico(self)
        self.v_graf.dibujar()
        self.v_graf.show(); self.v_graf.raise_(); self.v_graf.activateWindow()

    def resumen(self):
        if self._sin_datos():
            return
        if self.v_res is None:
            self.v_res = VentanaResumen(self)
        self.v_res.llenar()
        self.v_res.show(); self.v_res.raise_(); self.v_res.activateWindow()

    def exportar_csv(self):
        if not self.Q:
            return
        path, _f2 = QFileDialog.getSaveFileName(self, _i18n.t("Exportar CSV"),
                                                "serie_orificio.csv", "CSV (*.csv)")
        if not path:
            return
        t = self.tbl
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(";".join(t.horizontalHeaderItem(c).text().replace('\n', ' ')
                                 for c in range(5)) + "\n")
                for r in range(self._ultima_fila() + 1):
                    f.write(";".join(t.item(r, c).text() for c in range(5)) + "\n")
                est = self.estadisticas()
                if est:
                    f.write("\n")
                    for nom, v, un in est:
                        f.write(f"{_i18n.t(nom)};{v};{un}\n")
            dialogos.info(self, f"{_i18n.t('CSV guardado:')}\n{path}")
        except Exception as ex:
            dialogos.error(self, str(ex))


class VentanaGrafico(QDialog):
    """Gráfico del caudal de la serie contra la hora."""

    def __init__(self, serie):
        super().__init__(serie, Qt.WindowType.Window)
        self.serie = serie
        self.setWindowTitle(_i18n.t("Caudal — Serie de tiempo"))
        self.setStyleSheet('QDialog { background:#e0e0e0; }')
        root = QVBoxLayout(self); root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)
        root.addWidget(po._titulo("ThermoPhase — " + _i18n.t("Caudal — Serie de tiempo")))
        caja = QFrame(); caja.setObjectName('cajaGraf')
        caja.setStyleSheet(f'QFrame#cajaGraf {{ background:{GRAY_PLOT_BG}; border:1px solid {po.BORDER}; }}')
        lc = QVBoxLayout(caja); lc.setContentsMargins(6, 6, 6, 6)
        self.fig = Figure(figsize=(1, 1)); self.fig.patch.set_facecolor(GRAY_PLOT_BG)
        self.canvas = FigureCanvas(self.fig); self.canvas.setMinimumSize(760, 460)
        import graficos_menu as _gm
        _gm.instalar(self.canvas, redibujar=self.dibujar)   # cuadrícula, guardar y copiar
        lc.addWidget(self.canvas)
        root.addWidget(caja, 1)

    def dibujar(self):
        xs, ys, paso, un = self.serie.serie()
        fig = self.fig; fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor('#FFFFFF'); ax.set_axisbelow(True)
        ax.tick_params(labelsize=8, colors='#000000', direction='in', top=True, right=True,
                       length=4, width=1.0)
        for sp in ax.spines.values():
            sp.set_edgecolor('#000000'); sp.set_linewidth(1.4)
        ax.grid(True, linestyle='-', linewidth=0.7, color=po.GRAY_LBL)
        ax.set_ylabel(f"{_i18n.t('Caudal')} [{un}]", fontsize=9)
        ax.set_xlabel(_i18n.t("Hora"), fontsize=9)
        if xs:
            ax.plot(xs, ys, color='#1F4E9A', linewidth=CURVA_LW)
            span = (xs[-1] - xs[0]).total_seconds() if len(xs) > 1 else 0
            if span > 86400:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
            elif paso < 60:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=10))
            for lb in ax.get_xticklabels():
                lb.set_rotation(30); lb.set_ha('right')
        fig.subplots_adjust(left=0.09, right=0.98, top=0.96, bottom=0.16)
        self.canvas.draw_idle()


class VentanaResumen(QDialog):
    """Resumen de la serie en forma de tabla."""

    def __init__(self, serie):
        super().__init__(serie, Qt.WindowType.Window)
        self.serie = serie
        self.setWindowTitle(_i18n.t("Resumen — Serie de tiempo"))
        self.setStyleSheet('QDialog { background:#e0e0e0; }')
        root = QVBoxLayout(self); root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)
        root.addWidget(po._titulo("ThermoPhase — " + _i18n.t("Resumen")))
        self.tbl = po._tabla(1, 3)
        self.tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        root.addWidget(self.tbl)
        root.addStretch(1)

    def llenar(self):
        est = self.serie.estadisticas()
        t = self.tbl
        t.clear(); t.setRowCount(len(est) + 1); t.setColumnCount(3)
        for c, h in enumerate((_i18n.t("Propiedad"), _i18n.t("Valor"), _i18n.t("Unidad"))):
            t.setItem(0, c, po._cell(h, bg=po.GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        for r, (nom, v, un) in enumerate(est, 1):
            t.setItem(r, 0, po._cell(_i18n.t(nom) + ":", bg=po.GRAY_LBL))
            t.setItem(r, 1, po._cell(v, color=po.TEXT_RES))
            t.setItem(r, 2, po._cell(un, align=Qt.AlignmentFlag.AlignCenter))
        for c, w in enumerate((170, 120, 80)):
            t.setColumnWidth(c, w)
        for r in range(t.rowCount()):
            t.setRowHeight(r, po.ROW_H)
        po._ajustar(t)
        self.adjustSize(); self.setFixedSize(self.sizeHint())

"""
pestana_multienvolvente.py — Comparación de varias envolventes de fases.

Traza en un mismo diagrama P-T las envolventes de la composición principal
y/o de los fluidos del gestor.  Cada fluido se calcula con su propia EOS y su
propio kij (los de la composición principal son los de la ventana principal)
y con el método de trazado elegido en la barra principal (Michelsen o
Ziervogel-Poling).  Con agua activa se usa, igual que en la envolvente
individual, el trazado de Lindeloff-Michelsen.

Panel derecho:
  • Puntos especiales del fluido elegido: punto crítico, cricondentérmica y
    cricondenbárica.
  • Resaltar: deja a pleno color el fluido elegido y vuelve translúcidos los
    demás ("Ninguno" = todos a pleno color).
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QSizePolicy, QProgressBar,
                             QGridLayout, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

import idioma as _i18n
import graf_opciones as _go
import unidades as _u
import dialogos
from pestana_envolvente import (EnvWorker, TabEnvolvente, _aplicar_estilo_combo,
                                Figure, FigureCanvas, ticker,
                                BTN_STYLE, LBL_HDR, LBL_SEC, LBL_RES, GRAY_RES,
                                GRAY_LBL, GRAY_PLOT_BG, BORDER, TEXT, FONT_F, FS)

# Un color por fluido (se repiten cíclicamente si hay más de 10)
COLORES = ['#c0392b', '#1a4fa8', '#27ae60', '#e67e22', '#8e44ad',
           '#16a085', '#b7950b', '#2c3e50', '#d35400', '#7f8c8d']
ALFA_TENUE = 0.12          # opacidad de los fluidos no resaltados


def _color(i):
    return COLORES[i % len(COLORES)]


class MultiEnvWorker(QThread):
    """Calcula las envolventes de varios fluidos, uno tras otro."""
    avance = pyqtSignal(int, int, str)          # i, n, nombre
    done = pyqtSignal(list)                      # [(nombre, res|None, error|None)]

    def __init__(self, trabajos, metodo, eos_restaurar):
        super().__init__()
        self.trabajos = trabajos                 # [dict(nombre, z, kij, eos)]
        self.metodo = metodo
        self.eos_restaurar = eos_restaurar

    def run(self):
        import eos as _eng
        out = []
        n = len(self.trabajos)
        for i, t in enumerate(self.trabajos):
            self.avance.emit(i, n, t['nombre'])
            res = {'r': None, 'e': None}
            try:
                _eng.set_eos(t['eos'])
                z_full = list(t['z'])
                z13 = z_full[:13]; s = sum(z13)
                z13 = [v/s for v in z13] if s > 0 else z13
                agua_on = len(z_full) > 13 and z_full[13] > 1e-12
                w = EnvWorker(z13, t['kij'], self.metodo, max_pts=10000,
                              z_full=z_full, eos_code=t['eos'], agua_on=agua_on)
                # se ejecuta en ESTE hilo: run() emite done/error de inmediato
                w.done.connect(lambda r, res=res: res.__setitem__('r', r),
                               Qt.ConnectionType.DirectConnection)
                w.error.connect(lambda m, res=res: res.__setitem__('e', m),
                                Qt.ConnectionType.DirectConnection)
                w.run()
            except Exception as ex:
                res['e'] = str(ex)
            out.append((t['nombre'], res['r'], res['e']))
        try:
            _eng.set_eos(self.eos_restaurar)
        except Exception:
            pass
        self.done.emit(out)


class TabMultiEnvolvente(QWidget):
    """Ventana de comparación de envolventes."""

    def __init__(self, get_metodo=None, on_reseleccionar=None, on_calcular=None):
        super().__init__()
        self.on_calcular = on_calcular
        self.get_metodo = get_metodo or (lambda: 'michelsen')
        self.on_reseleccionar = on_reseleccionar
        self.trabajos = []
        self.resultados = []            # [(nombre, res)] solo los calculados
        self.worker = None
        # estado del cursor de lectura (reutiliza el de la envolvente)
        self._hover_annot = None; self._cross_v = None; self._cross_h = None
        self._bg = None; self._cursor_on = False
        self._build()

    # Cursor de lectura: mismos métodos que la envolvente individual.
    set_cursor = TabEnvolvente.set_cursor
    _on_draw = TabEnvolvente._on_draw
    _on_hover = TabEnvolvente._on_hover

    def _build(self):
        self.setObjectName('multiEnvTab')
        self.setStyleSheet(f'QWidget#multiEnvTab {{ background:{GRAY_LBL}; }}')
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 10, 4, 4); root.setSpacing(3)
        title = QLabel("ThermoPhase — Comparación de envolventes")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_HDR)
        root.addWidget(title)

        content = QHBoxLayout()
        content.setContentsMargins(6, 4, 6, 4); content.setSpacing(8)
        self.left_box = QWidget()
        self.left_box.setStyleSheet(f'background:{GRAY_PLOT_BG};border:1px solid {BORDER};')
        self.left_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ll = QVBoxLayout(self.left_box); ll.setContentsMargins(6, 6, 6, 6)
        self.fig = Figure(figsize=(1, 1))
        self.fig.patch.set_facecolor(GRAY_PLOT_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_position([0.115, 0.085, 0.86, 0.895])
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet(f"background-color: {GRAY_PLOT_BG};")
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setVisible(False)
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
        self.canvas.mpl_connect('draw_event', self._on_draw)
        ll.addWidget(self.canvas)
        content.addWidget(self.left_box, stretch=1)

        right = QWidget(); right.setFixedWidth(210)
        vr = QVBoxLayout(right); vr.setContentsMargins(0, 0, 0, 0); vr.setSpacing(6)
        lbl_style = (f'font-family:"{FONT_F}";font-size:{FS}pt;'
                     f'color:{TEXT};background:transparent;')

        def sep():
            s = QFrame(); s.setFrameShape(QFrame.Shape.HLine)
            s.setFrameShadow(QFrame.Shadow.Sunken); s.setStyleSheet(f'color:{BORDER};')
            return s

        t1 = QLabel("Puntos especiales:"); t1.setStyleSheet(LBL_SEC); t1.setFixedHeight(22)
        vr.addWidget(t1)
        lf = QLabel("Fluido:"); lf.setStyleSheet(lbl_style); lf.setFixedHeight(16)
        vr.addWidget(lf)
        self.cmb_pts = QComboBox(); self.cmb_pts.setFixedHeight(24)
        _aplicar_estilo_combo(self.cmb_pts)
        self.cmb_pts.currentIndexChanged.connect(self._actualizar_puntos)
        vr.addWidget(self.cmb_pts)

        grid = QGridLayout(); grid.setSpacing(4); grid.setContentsMargins(0, 2, 0, 0)
        self.res_labels = {}; self.res_lbl_widgets = {}
        filas = [("T crítica", "Tc", "T"), ("P crítica", "Pc", "P"),
                 ("Cricondentérmica", "cric_T", "T"), ("Cricondenbárica", "cric_P", "P")]
        for r, (base, key, mag) in enumerate(filas):
            l = QLabel(f"{base} ({_u.u(mag)}):"); l.setStyleSheet(lbl_style)
            l.setWordWrap(True)
            l.setProperty("_mag", mag); l.setProperty("_base", base)
            grid.addWidget(l, r, 0); self.res_lbl_widgets[key] = l
            v = QLabel(""); v.setStyleSheet(LBL_RES.replace(GRAY_RES, '#F7F7F7'))
            v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(v, r, 1); self.res_labels[key] = v
        vr.addLayout(grid)

        vr.addWidget(sep())
        t2 = QLabel("Resaltar fluido:"); t2.setStyleSheet(LBL_SEC); t2.setFixedHeight(22)
        vr.addWidget(t2)
        self.cmb_res = QComboBox(); self.cmb_res.setFixedHeight(24)
        _aplicar_estilo_combo(self.cmb_res)
        self.cmb_res.currentIndexChanged.connect(lambda _i: self._plot())
        vr.addWidget(self.cmb_res)
        vr.addSpacing(4)
        # Recalcular con las composiciones actuales de los fluidos elegidos
        self.btn_calc = QPushButton("Calcular")
        self.btn_calc.setStyleSheet(BTN_STYLE); self.btn_calc.setFixedHeight(30)
        self.btn_calc.clicked.connect(lambda: self.on_calcular and self.on_calcular())
        vr.addWidget(self.btn_calc)

        self.prog = QProgressBar(); self.prog.setTextVisible(False)
        self.prog.setFixedHeight(18); self.prog.setVisible(False)
        self.prog.setStyleSheet(
            'QProgressBar { border:1px solid #888888; background:#E8E8E8; border-radius:0px; }'
            'QProgressBar::chunk { background:#2d7d2d; }')
        vr.addWidget(self.prog)
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet(f'font-family:"{FONT_F}";font-size:{FS-1}pt;'
                                      f'color:#555555;background:transparent;')
        self.lbl_estado.setWordWrap(True); self.lbl_estado.setVisible(False)
        vr.addWidget(self.lbl_estado)

        vr.addStretch()
        # Elegir otros fluidos (abajo, donde la envolvente tiene Exportar CSV)
        self.btn_sel = QPushButton("Seleccionar fluidos")
        self.btn_sel.setStyleSheet(BTN_STYLE)
        self.btn_sel.clicked.connect(lambda: self.on_reseleccionar and self.on_reseleccionar())
        vr.addWidget(self.btn_sel)
        content.addWidget(right)
        root.addLayout(content, stretch=1)

    # ── cálculo ─────────────────────────────────────────────────────────
    def calcular(self, trabajos, eos_restaurar):
        """trabajos: [dict(nombre, z(14), kij, eos)] ya validados."""
        if self.worker is not None and self.worker.isRunning():
            return
        self.trabajos = list(trabajos)
        self.resultados = []
        self.prog.setRange(0, len(trabajos)); self.prog.setValue(0)
        self.prog.setVisible(True); self.lbl_estado.setVisible(True)
        self.btn_sel.setEnabled(False); self.btn_calc.setEnabled(False)
        self.btn_calc.setText(_i18n.t("Calculando..."))
        self.worker = MultiEnvWorker(self.trabajos, self.get_metodo(), eos_restaurar)
        self.worker.avance.connect(self._on_avance)
        self.worker.done.connect(self._on_done)
        self.worker.start()

    def _on_avance(self, i, n, nombre):
        self.prog.setValue(i)
        self.lbl_estado.setText(_i18n.t("Calculando:") + f" {nombre} ({i + 1}/{n})")

    def _on_done(self, salida):
        self.prog.setVisible(False); self.btn_sel.setEnabled(True)
        self.btn_calc.setEnabled(True); self.btn_calc.setText(_i18n.t("Calcular"))
        self.lbl_estado.setText(""); self.lbl_estado.setVisible(False)
        fallidos = []
        self.resultados = []
        for nombre, res, err in salida:
            if res is not None and (res.get('burbuja') or res.get('rocio')
                                    or res.get('lm') or res.get('curva')):
                self.resultados.append((nombre, res))
            else:
                fallidos.append(nombre if not err else f"{nombre}: {err}")
        nombres = [n for n, _ in self.resultados]
        for cmb, extra in ((self.cmb_pts, None), (self.cmb_res, "Ninguno")):
            previo = cmb.currentText()          # se conserva al recalcular
            cmb.blockSignals(True); cmb.clear()
            if extra: cmb.addItem(_i18n.t(extra))
            cmb.addItems(nombres)
            i = cmb.findText(previo) if previo else -1
            cmb.setCurrentIndex(i if i >= 0 else 0)
            cmb.blockSignals(False)
        self.canvas.setVisible(bool(self.resultados))
        self._plot(); self._actualizar_puntos()
        if fallidos:
            dialogos.advertencia(self, _i18n.t(
                "No se pudo trazar la envolvente de:") + "\n\n• " + "\n• ".join(fallidos))

    # ── puntos especiales ───────────────────────────────────────────────
    def _actualizar_puntos(self, *_):
        for v in self.res_labels.values():
            v.setText("")
        i = self.cmb_pts.currentIndex()
        if not (0 <= i < len(self.resultados)):
            return
        res = self.resultados[i][1]
        fv = lambda v: f"{v:.1f}" if v is not None else ""
        crit = res.get('critico')
        if crit is not None:
            self.res_labels['Tc'].setText(fv(_u.t_desde_R(crit[1])))
            self.res_labels['Pc'].setText(fv(_u.p_desde_psia(crit[0])))
        pts = self._puntos_curvas(res)
        if res.get('puro'):
            self.res_labels['cric_T'].setText("-"); self.res_labels['cric_P'].setText("-")
        elif pts:
            self.res_labels['cric_T'].setText(fv(_u.t_desde_R(max(t for _, t in pts))))
            self.res_labels['cric_P'].setText(fv(_u.p_desde_psia(max(p for p, _ in pts))))

    @staticmethod
    def _segmentos(res):
        """Lista de tramos [(P,T)...] que forman la envolvente del fluido."""
        lm = res.get('lm')
        if lm is not None:
            return [pts for key in ('2-HC', '3-HC', '3-Aq', '2-Aq')
                    for pts in (lm.get(key) or []) if pts]
        if res.get('puro'):
            c = res.get('curva') or res.get('burbuja') or []
            return [c] if c else []
        return [s for s in (res.get('burbuja') or [], res.get('rocio') or []) if s]

    def _puntos_curvas(self, res):
        lm = res.get('lm')
        if lm is not None:   # cricondentérmica/bárica de la envolvente HC
            segs = [p for k in ('2-HC', '3-HC') for p in (lm.get(k) or [])]
            return [q for s in segs for q in s]
        return [q for s in self._segmentos(res) for q in s]

    # ── gráfico ─────────────────────────────────────────────────────────
    def _plot(self):
        ax = self.ax; ax.clear()
        self._hover_annot = None; self._cross_v = None; self._cross_h = None; self._bg = None
        ax.set_facecolor('#FFFFFF'); ax.set_axisbelow(True)
        ax.set_position([0.115, 0.085, 0.86, 0.895])
        sel = self.cmb_res.currentIndex() - 1          # -1 = ninguno
        for i, (nombre, res) in enumerate(self.resultados):
            col = _color(i)
            a = 1.0 if (sel < 0 or sel == i) else ALFA_TENUE
            z = 6 if sel == i else 2
            primero = True
            for seg in self._segmentos(res):
                T = [_u.t_desde_R(t) for _, t in seg]
                P = [_u.p_desde_psia(p) for p, _ in seg]
                _go.curva(ax, T, P, col, label=nombre if primero else None,
                          alpha=a, z_line=z, z_mark=z + 1, etiquetar=False)
                primero = False
            crit = res.get('critico')
            if crit is not None:
                ax.plot([_u.t_desde_R(crit[1])], [_u.p_desde_psia(crit[0])],
                        linestyle='none', marker='s', markersize=5, color=col,
                        markeredgecolor='#000000', markeredgewidth=0.6,
                        alpha=a, zorder=z + 2)
        ax.set_xlabel(f"{_i18n.t('Temperatura')} ({_u.u('T')})", fontsize=10, color=TEXT)
        ax.set_ylabel(f"{_i18n.t('Presion')} ({_u.u('P')})", fontsize=10, color=TEXT)
        ax.tick_params(labelsize=8, colors='#000000', direction='in',
                       top=True, right=True, length=4, width=1.0)
        for s in ax.spines.values():
            s.set_edgecolor('#000000'); s.set_linewidth(1.4)
        ax.grid(True, linestyle='-', linewidth=0.8, alpha=1.0, color=GRAY_LBL)
        if ax.get_legend_handles_labels()[0]:
            leg = ax.legend(fontsize=8, framealpha=1.0, fancybox=False,
                            edgecolor='#000000', facecolor=GRAY_PLOT_BG)
            leg.get_frame().set_linewidth(1.0)
            # la leyenda conserva el color pleno aunque la curva esté tenue
            for h in leg.legend_handles if hasattr(leg, 'legend_handles') else leg.legendHandles:
                try: h.set_alpha(1.0)
                except Exception: pass
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
        self.canvas.draw_idle()

    # ── unidades / idioma ───────────────────────────────────────────────
    def aplicar_unidades(self, old=None):
        for key, l in self.res_lbl_widgets.items():
            base = l.property("_base"); mag = l.property("_mag")
            l.setText(f"{_i18n.t(base)} ({_u.u(mag)}):")
        if self.cmb_res.count():
            self.cmb_res.setItemText(0, _i18n.t("Ninguno"))
        if self.resultados:
            self._plot(); self._actualizar_puntos()

    def retraducir_grafico(self):
        self.aplicar_unidades()

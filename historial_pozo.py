"""
historial_pozo.py — Historial de envolventes de un pozo.

Ventana de ingreso: EOS, método de la envolvente, composición + fecha de
muestreo de cada muestra y tabla con las muestras agregadas (se pueden quitar
o volver a cargar para corregirlas).  Al calcular se traza la envolvente de
cada muestra.

Ventana de resultados (tamaño fijo): envolventes superpuestas con color por
fecha y, a la derecha, la tendencia de la cricondentérmica, de la
cricondenbárica y de un componente (elegido con un selector) en el tiempo.
Botón «Vista 3D»: las envolventes en (temperatura, fecha, presión).
"""
import datetime as _dt

from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QLabel, QPushButton, QComboBox,
                             QDateEdit, QAbstractItemView, QSizePolicy,
                             QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate

import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

import idioma as _i18n
import unidades as _u
import dialogos
import graficos_menu as _gm
from eos import NC, NOMBRES, componente_etiqueta
from pestana_op_unitarias import (_titulo, _tabla, _cell, _ajustar, _set_comp,
                                  _get_comp, _a_float, TXT_QSS, LBL_QSS,
                                  BTN_QSS, WHITE, GRAY_LBL, GRAY_EMPTY,
                                  TEXT, TEXT_RES, ROW_H, FONT_F, FS, BORDER)

GRAY_PLOT_BG = "#DCDCDC"
# Mismo grosor de línea y tamaño de marcador que la Envolvente de fases y el
# Análisis de sensibilidad (graf_opciones.curva: lw=0.7, ms=3).
LW_2D = 0.7
MS_2D = 3
FMT_FECHA = "dd/MM/yyyy"
METODOS = [("Michelsen", 'michelsen'), ("Ziervogel-Poling", 'ziervogel')]
W_CAMPO = 232


def _fecha_txt(iso):
    try:
        return _dt.date.fromisoformat(iso).strftime("%d/%m/%Y")
    except Exception:
        return iso


def _nombre_comp(i):
    """Nombre completo del componente, p. ej. «Metano [C1]» (sin los dos
    puntos de las etiquetas de tabla)."""
    n = _i18n.t(NOMBRES[i]) if i < len(NOMBRES) else componente_etiqueta(i)
    return n.rstrip().rstrip(':')


GRUPOS = [("Pentanos y más pesados [C5+]", 7), ("Heptanos y más pesados [C7+]", 10)]


# ════════════════════════════════════════════════════════════════════════
# Cálculo
# ════════════════════════════════════════════════════════════════════════
def envolvente(z, kij, metodo):
    """Envolvente con el método pedido → (burbuja, rocío, crítico).  Puntos
    (P psia, T °R)."""
    if metodo == 'michelsen':
        try:
            from envolvente_michelsen import construir_envolvente
            r = construir_envolvente(z, kij, max_pts=10000)
            env = r.get('envolvente', []); crit = r.get('critico')
            if env:
                if crit is not None:
                    ic = min(range(len(env)), key=lambda i: (env[i][0]-crit[0])**2
                             + (env[i][1]-crit[1])**2)
                    return env[:ic+1], env[ic:], crit
                if r.get('sin_critico'):
                    return [], env, None
                return env, [], None
        except Exception:
            pass
    from envolvente import curva_envolvente
    r = curva_envolvente(z, kij)
    return r.get('burbuja', []), r.get('rocio', []), r.get('critico')


class HistWorker(QThread):
    progreso = pyqtSignal(int, int)
    done = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, muestras, eos_code, metodo, kij):
        super().__init__()
        self.muestras = muestras; self.eos_code = eos_code
        self.metodo = metodo; self.kij = kij

    def run(self):
        import eos as _eng
        try:
            _eng.set_eos(self.eos_code)
            res = []
            for k, m in enumerate(self.muestras):
                self.progreso.emit(k + 1, len(self.muestras))
                z = list(m['z'][:NC]); s = sum(z); z = [v/s for v in z]
                burb, rocio, crit = envolvente(z, self.kij, self.metodo)
                pts = list(burb) + list(rocio)
                if not pts:
                    raise RuntimeError(_i18n.t("No se pudo trazar la envolvente de la "
                                               "muestra del") + f" {_fecha_txt(m['fecha'])}.")
                ct = max(pts, key=lambda q: q[1])      # cricondentérmica
                cb = max(pts, key=lambda q: q[0])      # cricondenbárica
                res.append(dict(fecha=m['fecha'], z=z, burbuja=burb, rocio=rocio,
                                critico=crit, cricondenterma=ct, cricondenbara=cb))
            self.done.emit(res)
        except Exception as e:
            self.error.emit(str(e))


# ════════════════════════════════════════════════════════════════════════
# Ventana de ingreso
# ════════════════════════════════════════════════════════════════════════
class DialogoHistorial(QDialog):
    """h: helpers de la ventana principal (estilo_combo, eos_items, eos_code,
    eos_idx, kij_base).  fuentes/datos_fuente: para «Cargar de»."""

    def __init__(self, parent, fuentes, datos_fuente, activos, previo, h):
        super().__init__(parent)
        self.h = h; self.datos_fuente = datos_fuente
        self.act = [i for i in sorted(set(activos)) if i < NC]
        self.muestras = []            # [{fecha: 'yyyy-mm-dd', z: [NC]}], ordenadas
        self.resultado = None; self.entrada = None
        self.setWindowTitle(_i18n.t("Historial de pozo"))
        self.setStyleSheet('QDialog { background:#e0e0e0; }')
        root = QVBoxLayout(self); root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)
        root.addWidget(_titulo(_i18n.t("ThermoPhase — Historial de pozo")))

        # Modelo
        gm = QGridLayout(); gm.setSpacing(4)
        self.c_eos = QComboBox(); self.c_eos.setFixedSize(W_CAMPO, 22); h['estilo_combo'](self.c_eos)
        self.c_eos.addItems([_i18n.t(x) for x in h['eos_items']])
        self.c_met = QComboBox(); self.c_met.setFixedSize(W_CAMPO, 22); h['estilo_combo'](self.c_met)
        for txt, cod in METODOS:
            self.c_met.addItem(txt, cod)
        gm.addWidget(self._etq("Ecuación de estado:"), 0, 0); gm.addWidget(self.c_eos, 0, 1)
        gm.addWidget(self._etq("Método de la envolvente:"), 1, 0); gm.addWidget(self.c_met, 1, 1)
        fm = QHBoxLayout(); fm.addLayout(gm); fm.addStretch(1)
        # Calcular / Cancelar arriba a la derecha (con el avance debajo)
        vb = QVBoxLayout(); vb.setSpacing(4)
        fb0 = QHBoxLayout(); fb0.setSpacing(8); fb0.addStretch()
        self.b_ok = self._btn("Calcular"); self.b_can = self._btn("Cancelar")
        fb0.addWidget(self.b_ok); fb0.addWidget(self.b_can)
        vb.addLayout(fb0)
        fp = QHBoxLayout(); fp.setSpacing(6); fp.addStretch()
        self.lbl_prog = self._lbl(""); self.lbl_prog.setFixedHeight(18)
        fp.addWidget(self.lbl_prog)
        vb.addLayout(fp); vb.addStretch()
        fm.addLayout(vb)
        root.addLayout(fm)

        cols = QHBoxLayout(); cols.setSpacing(16)
        # ── Izquierda: nueva muestra ────────────────────────────────────
        c1 = QVBoxLayout(); c1.setSpacing(4)
        ff = QHBoxLayout(); ff.setSpacing(6)
        ff.addWidget(self._lbl("Muestra:")); ff.addStretch()
        ff.addWidget(self._lbl("Cargar de:"))
        self.cmb_fuente = QComboBox(); self.cmb_fuente.setFixedSize(150, 22)
        h['estilo_combo'](self.cmb_fuente)
        self.cmb_fuente.addItem("", None)
        for k, nom in fuentes:
            self.cmb_fuente.addItem(nom, k)
        ff.addWidget(self.cmb_fuente)
        c1.addLayout(ff)
        fd = QHBoxLayout(); fd.setSpacing(4)
        lf = self._etq("Fecha de muestreo:"); lf.setMinimumWidth(210); lf.setFixedWidth(210)
        self.ed_fecha = QDateEdit(QDate.currentDate()); self.ed_fecha.setCalendarPopup(True)
        self.ed_fecha.setDisplayFormat(FMT_FECHA); self.ed_fecha.setFixedSize(110, 22)
        self.ed_fecha.setStyleSheet(f'QDateEdit {{ background:{WHITE}; border:1px solid #888888;'
                                    f' font-family:"{FONT_F}"; font-size:{FS}pt; padding:0 4px; }}')
        fd.addWidget(lf); fd.addWidget(self.ed_fecha); fd.addStretch()
        c1.addLayout(fd)
        tc = self.tc = _tabla(len(self.act) + 2, 2)
        tc.setColumnWidth(0, 210); tc.setColumnWidth(1, 110)
        tc.setItem(0, 0, _cell(_i18n.t("Componente"), bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        tc.setItem(0, 1, _cell(_i18n.t("Composición"), bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        for r, i in enumerate(self.act, 1):
            tc.setItem(r, 0, _cell(_nombre_comp(i), bg=GRAY_LBL))
            tc.setItem(r, 1, _cell("", editable=True))
        self.rs = len(self.act) + 1
        tc.setItem(self.rs, 0, _cell(_i18n.t("Sumatorias:"), bg=GRAY_LBL))
        tc.setItem(self.rs, 1, _cell("", bg=GRAY_EMPTY, color=TEXT_RES))
        for r in range(self.rs + 1):
            tc.setRowHeight(r, ROW_H)
        _ajustar(tc)
        tc.itemChanged.connect(self._on_cambio)
        try:
            h['registrar'](tc)
        except Exception:
            pass
        c1.addWidget(tc)
        fb = QHBoxLayout(); fb.setSpacing(6)
        self.b_norm = self._btn("Normalizar"); self.b_add = self._btn("Agregar muestra")
        fb.addWidget(self.b_norm); fb.addStretch(); fb.addWidget(self.b_add)
        c1.addLayout(fb); c1.addStretch(1)
        cols.addLayout(c1)

        # ── Derecha: muestras agregadas ─────────────────────────────────
        c2 = QVBoxLayout(); c2.setSpacing(4)
        fl = QHBoxLayout(); fl.addWidget(self._lbl("Muestras agregadas:")); fl.addStretch()
        c2.addLayout(fl)
        self.tm = _tabla(len(self.act) + 2, 1)
        self.tm.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tm.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tm.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectColumns)
        self.tm.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tm.itemSelectionChanged.connect(self._on_sel_muestra)
        self.tm.setFixedSize(540, (len(self.act) + 2) * ROW_H + 2)
        c2.addWidget(self.tm)
        fq = QHBoxLayout(); fq.setSpacing(6)
        self.lbl_n = self._lbl("")
        self.b_quitar = self._btn("Quitar muestra")
        fq.addWidget(self.lbl_n); fq.addStretch(); fq.addWidget(self.b_quitar)
        c2.addLayout(fq)
        c2.addStretch(1)
        cols.addLayout(c2)
        root.addLayout(cols)


        self.b_norm.clicked.connect(self._normalizar)
        self.b_add.clicked.connect(self._agregar)
        self.b_quitar.clicked.connect(self._quitar)
        self.b_ok.clicked.connect(self._calcular)
        self.b_can.clicked.connect(self.reject)
        self.cmb_fuente.activated.connect(lambda _i: self._cargar_fuente(self.cmb_fuente.currentData()))
        self._worker = None
        self._aplicar_previo(previo)
        self._refrescar_tabla()
        self.adjustSize(); self.setFixedSize(self.sizeHint())
        self._listo = True

    # ── widgets ─────────────────────────────────────────────────────────
    def _lbl(self, t):
        l = QLabel(_i18n.t(t) if t else ""); l.setStyleSheet(TXT_QSS); return l

    def _etq(self, t):
        l = QLabel(_i18n.t(t)); l.setStyleSheet(LBL_QSS); l.setFixedHeight(22)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        l.setMinimumWidth(170)
        return l

    def _btn(self, t):
        b = QPushButton(_i18n.t(t)); b.setFixedHeight(26); b.setMinimumWidth(84)
        b.setStyleSheet(BTN_QSS); b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b

    # ── composición de entrada ──────────────────────────────────────────
    def _on_cambio(self, it):
        if it.column() != 1 or it.row() in (0, self.rs):
            return
        v = _a_float(it.text())
        self.tc.blockSignals(True)
        if v is not None:
            _set_comp(it, v)
        self.tc.blockSignals(False)
        self._upd_suma()

    def _crudo(self):
        return [_get_comp(self.tc.item(r, 1)) for r in range(1, self.rs)]

    def _upd_suma(self):
        self.tc.blockSignals(True)
        self.tc.item(self.rs, 1).setText(f"{sum(self._crudo()):.4f}")
        self.tc.blockSignals(False)

    def _set_z(self, z):
        self.tc.blockSignals(True)
        for r, i in enumerate(self.act, 1):
            v = z[i] if i < len(z) else 0.0
            _set_comp(self.tc.item(r, 1), v)
        self.tc.blockSignals(False)
        self._upd_suma()

    def _normalizar(self):
        z = self._crudo(); s = sum(z)
        if s <= 0:
            return
        base = 100.0 if abs(s - 100.0) < abs(s - 1.0) else 1.0
        zz = [0.0]*NC
        for r, i in enumerate(self.act):
            zz[i] = z[r]/s*base
        self._set_z(zz)

    def _cargar_fuente(self, clave):
        if clave is None:
            return
        d = self.datos_fuente(clave)
        if d is None:
            return
        _nombre, z, _kij, eos_c, _met = d
        self._set_z(z)
        self.c_eos.setCurrentIndex(self.h['eos_idx'](eos_c))

    # ── muestras ────────────────────────────────────────────────────────
    def _agregar(self):
        z = self._crudo(); s = sum(z)
        if s <= 0:
            dialogos.advertencia(self, _i18n.t("Ingrese la composición de la muestra."))
            return
        if not (abs(s - 1.0) < 0.01 or abs(s - 100.0) < 1.0):
            dialogos.advertencia(self, _i18n.t("La composicion debe sumar 1 (fraccion molar) "
                                               "o 100 (porcentaje molar)"))
            return
        zz = [0.0]*NC
        for r, i in enumerate(self.act):
            zz[i] = z[r]/s
        fecha = self.ed_fecha.date().toString("yyyy-MM-dd")
        self.muestras = [m for m in self.muestras if m['fecha'] != fecha]
        self.muestras.append(dict(fecha=fecha, z=zz))
        self.muestras.sort(key=lambda m: m['fecha'])
        self._refrescar_tabla()

    def _sel(self):
        cols = sorted({ix.column() for ix in self.tm.selectedIndexes()})
        c = cols[0] if cols else -1
        return c - 1 if c >= 1 else -1

    def _on_sel_muestra(self):
        k = self._sel()
        if 0 <= k < len(self.muestras):
            m = self.muestras[k]
            self.ed_fecha.setDate(QDate.fromString(m['fecha'], "yyyy-MM-dd"))
            self._set_z(m['z'])

    def _quitar(self):
        k = self._sel()
        if not (0 <= k < len(self.muestras)):
            dialogos.info(self, _i18n.t("Seleccione la muestra a quitar."))
            return
        del self.muestras[k]
        self._refrescar_tabla()

    def _refrescar_tabla(self):
        t = self.tm; n = len(self.muestras)
        t.blockSignals(True)
        t.clearContents(); t.setColumnCount(1 + n)
        t.setColumnWidth(0, 200)
        t.setItem(0, 0, _cell(_i18n.t("Componente"), bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        for r, i in enumerate(self.act, 1):
            t.setItem(r, 0, _cell(_nombre_comp(i), bg=GRAY_LBL))
        t.setItem(self.rs, 0, _cell(_i18n.t("Sumatorias:"), bg=GRAY_LBL))
        for c, m in enumerate(self.muestras, 1):
            t.setColumnWidth(c, 84)
            t.setItem(0, c, _cell(_fecha_txt(m['fecha']), bg=GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
            for r, i in enumerate(self.act, 1):
                t.setItem(r, c, _cell(f"{m['z'][i]:.4f}"))
            t.setItem(self.rs, c, _cell(f"{sum(m['z']):.4f}", bg=GRAY_EMPTY, color=TEXT_RES))
        for r in range(self.rs + 1):
            t.setRowHeight(r, ROW_H)
        t.blockSignals(False)
        self._ajustar_alto_tm()
        self.lbl_n.setText(_i18n.t("Muestras:") + f" {n}")
        self.b_ok.setEnabled(n >= 1)

    def _ajustar_alto_tm(self):
        """Alto justo de la tabla de muestras, con la altura REAL de las filas
        (en Windows la fila mínima puede ser mayor que ROW_H): sin hueco bajo
        «Sumatorias» y sin cortar filas.  Si las muestras no caben a lo ancho,
        se suma la barra horizontal."""
        t = self.tm
        marco = 2 * t.frameWidth()
        alto = sum(t.rowHeight(r) for r in range(t.rowCount())) + marco
        ancho = sum(t.columnWidth(c) for c in range(t.columnCount())) + marco
        if ancho > t.width():
            alto += t.horizontalScrollBar().sizeHint().height()
        if t.height() != alto:
            t.setFixedHeight(alto)
            if getattr(self, '_listo', False):
                self.setMinimumSize(0, 0); self.setMaximumSize(16777215, 16777215)
                self.layout().activate(); self.adjustSize()
                self.setFixedSize(self.sizeHint())

    def _aplicar_previo(self, p):
        if not p:
            return
        self.c_eos.setCurrentIndex(p.get('eos_idx', 0))
        self.c_met.setCurrentIndex(p.get('met_idx', 0))
        self.muestras = [dict(fecha=m['fecha'], z=list(m['z'])) for m in p.get('muestras', [])]

    # ── cálculo ─────────────────────────────────────────────────────────
    def _calcular(self):
        if not self.muestras or self._worker is not None:
            return
        eos_code = self.h['eos_code'](self.c_eos.currentIndex())
        self.entrada = dict(eos_idx=self.c_eos.currentIndex(), met_idx=self.c_met.currentIndex(),
                            eos=eos_code, eos_nombre=self.c_eos.currentText(),
                            metodo=self.c_met.currentData(),
                            muestras=[dict(fecha=m['fecha'], z=list(m['z'])) for m in self.muestras])
        for w in (self.b_ok, self.b_add, self.b_quitar, self.b_norm):
            w.setEnabled(False)
        self.lbl_prog.setText(_i18n.t("Calculando muestra") + f" 1 / {len(self.muestras)}…")
        self._worker = HistWorker(self.entrada['muestras'], eos_code,
                                  self.entrada['metodo'], self.h['kij_base'](eos_code))
        self._worker.progreso.connect(self._on_prog)
        self._worker.done.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_prog(self, k, n):
        self.lbl_prog.setText(_i18n.t("Calculando muestra") + f" {k} / {n}…")

    def _fin(self):
        self._worker.wait(); self._worker = None
        self.lbl_prog.setText("")
        for w in (self.b_ok, self.b_add, self.b_quitar, self.b_norm):
            w.setEnabled(True)

    def _on_done(self, res):
        self._fin()
        self.resultado = res
        self.accept()

    def _on_error(self, msg):
        self._fin()
        dialogos.advertencia(self, msg)

    def reject(self):
        if self._worker is not None:
            return
        super().reject()


# ════════════════════════════════════════════════════════════════════════
# Ventana de resultados
# ════════════════════════════════════════════════════════════════════════
def _estilo_ax(ax, chico=False):
    ax.set_facecolor('#FFFFFF'); ax.set_axisbelow(True)
    ax.tick_params(labelsize=7 if chico else 8, colors='#000000', direction='in',
                   top=True, right=True, length=3 if chico else 4, width=1.0)
    for s in ax.spines.values():
        s.set_edgecolor('#000000'); s.set_linewidth(1.2 if chico else 1.4)
    ax.grid(True, linestyle='-', linewidth=0.7, color=GRAY_LBL)


def _caja(widget, margen=6):
    """Recuadro como el de la Envolvente de fases: fondo del gráfico y borde
    gris, con un margen de 6 px alrededor del canvas."""
    f = QFrame(); f.setObjectName('cajaGraf')
    f.setStyleSheet(f'QFrame#cajaGraf {{ background:{GRAY_PLOT_BG}; border:1px solid {BORDER}; }}')
    l = QVBoxLayout(f); l.setContentsMargins(margen, margen, margen, margen); l.setSpacing(0)
    l.addWidget(widget)
    return f


def _barra_titulo(texto):
    """Barra de título «ThermoPhase — …» (mismo estilo que la Envolvente)."""
    t = QLabel(texto)
    t.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    t.setFixedHeight(22)
    t.setStyleSheet(f'background:#A8A8A8; color:{TEXT}; border:1px solid {BORDER};'
                    f' font-family:"{FONT_F}"; font-size:{FS}pt; padding:0px 6px;')
    return t


def estilo_3d(ax):
    """Formato común de los gráficos 3D: caras con gris tenue y contorno
    negro, cuadrícula mínima y líneas de ejes negras."""
    try:
        ax.set_facecolor(GRAY_PLOT_BG)
        for eje in (ax.xaxis, ax.yaxis, ax.zaxis):
            # (gris por defecto de matplotlib sobre el fondo, ya mezclado y
            # opaco, para que el contorno salga negro y no grisáceo)
            eje.set_pane_color((0.906, 0.906, 0.906, 1.0))
            eje.pane.set_edgecolor('#000000'); eje.pane.set_linewidth(1.0)
            eje.pane.set_closed(True)          # dibuja también el 4.º lado
            eje._axinfo['grid'].update(linewidth=0.3, color='#B0B0B0')
            eje.line.set_color('#000000'); eje.line.set_linewidth(1.0)
    except Exception:
        pass


def leyenda_3d(fig, ax, titulo):
    """Cuadro de leyendas como en la vista 2D, fijo a la figura."""
    h, l = ax.get_legend_handles_labels()
    if not h:
        return
    leg = fig.legend(h, l, title=titulo, fontsize=8, title_fontsize=8,
                     framealpha=1.0, fancybox=False, edgecolor='#000000',
                     facecolor=GRAY_PLOT_BG, loc='upper left',
                     bbox_to_anchor=(0.02, 0.98))
    leg.get_frame().set_linewidth(1.0)


class Ventana3DBase(QWidget):
    """Ventana 3D con barra de título y gráfico enmarcado; se gira con el
    ratón y es redimensionable.  Las subclases implementan _trazar(ax) y
    _titulos() -> (título de ventana, texto de la barra)."""

    def __init__(self, dueña=None):
        super().__init__(dueña)
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName('ventana3d')
        self.setStyleSheet(f'QWidget#ventana3d {{ background:{GRAY_LBL}; }}')
        lay = QVBoxLayout(self); lay.setContentsMargins(4, 10, 4, 4); lay.setSpacing(3)
        self.lbl_titulo = _barra_titulo("")
        lay.addWidget(self.lbl_titulo)
        self.fig = Figure(figsize=(1, 1)); self.fig.patch.set_facecolor(GRAY_PLOT_BG)
        self.canvas = FigureCanvas(self.fig)
        _gm.instalar(self.canvas)
        self.canvas.setStyleSheet(f'background-color:{GRAY_PLOT_BG};')
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        envol = QVBoxLayout(); envol.setContentsMargins(6, 4, 6, 4)
        envol.addWidget(_caja(self.canvas))
        lay.addLayout(envol, 1)
        self.setMinimumSize(560, 460); self.resize(940, 720)
        self.ax = None

    def _titulos(self):
        return "", ""

    def _trazar(self, ax):
        pass

    def retraducir(self, redibujar=True):
        tv, tb = self._titulos()
        self.setWindowTitle(tv); self.lbl_titulo.setText(tb)
        if redibujar and self.ax is not None:
            self.dibujar()

    def dibujar(self):
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
        vista = (self.ax.elev, self.ax.azim) if self.ax is not None else (22, -60)
        self.fig.clear()
        ax = self.ax = self.fig.add_subplot(111, projection='3d')
        self._trazar(ax)
        ax.tick_params(labelsize=7)
        ax.view_init(*vista)
        estilo_3d(ax)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.canvas.draw_idle()


class TabHistorial(QWidget):
    ANCHO, ALTO = 1180, 712
    W_ENV = 740                     # ancho del canvas de envolventes
    H_MINI = 186                    # alto de cada canvas de tendencia

    def __init__(self, on_nuevo=None, estilo_combo=None, dueña=None):
        super().__init__()
        self.on_nuevo = on_nuevo; self._estilo_combo = estilo_combo
        self._dueña = dueña
        self.res = []; self.entrada = {}; self._v3d = None
        self.setFixedSize(self.ANCHO, self.ALTO)
        # Fondo de la ventana como la Envolvente; cada gráfico en su recuadro.
        self.setObjectName('histTab')
        self.setAutoFillBackground(True)
        self.setStyleSheet(f'QWidget#histTab {{ background:{GRAY_LBL}; }}')
        root = QVBoxLayout(self); root.setContentsMargins(4, 10, 4, 4); root.setSpacing(3)
        self.lbl_titulo = _barra_titulo("ThermoPhase — " + _i18n.t("Historial de pozo"))
        root.addWidget(self.lbl_titulo)
        cont = QHBoxLayout(); cont.setContentsMargins(6, 4, 6, 4); cont.setSpacing(8)

        # ancho disponible para la columna derecha
        self.W_MINI = self.ANCHO - 8 - 12 - (self.W_ENV + 14) - 8 - 14
        alto_der = 3*(self.H_MINI + 14) + 22 + 26 + 4*4
        self.fig = Figure(figsize=(1, 1)); self.fig.patch.set_facecolor(GRAY_PLOT_BG)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        _gm.instalar(self.canvas)
        self.canvas.setStyleSheet(f'background-color:{GRAY_PLOT_BG};')
        h_env = alto_der - 14
        self.canvas.setFixedSize(self.W_ENV, h_env)
        self.fig.set_size_inches(self.W_ENV/self.fig.dpi, h_env/self.fig.dpi)
        try:
            self.fig.set_layout_engine('tight', pad=0.6)
        except Exception:
            pass
        cont.addWidget(_caja(self.canvas), 0, Qt.AlignmentFlag.AlignTop)

        der = QVBoxLayout(); der.setSpacing(4)
        self.f_ct, self.ax_ct, self.c_ct = self._mini(); der.addWidget(_caja(self.c_ct))
        self.f_cb, self.ax_cb, self.c_cb = self._mini(); der.addWidget(_caja(self.c_cb))
        fc = QHBoxLayout(); fc.setSpacing(6)
        l = QLabel(_i18n.t("Componente:")); l.setStyleSheet(TXT_QSS + 'background:transparent;')
        l.setFixedWidth(74)
        self.cmb_comp = QComboBox()
        self.cmb_comp.setFixedSize(self.W_MINI + 14 - 74 - 6, 22)
        if estilo_combo:
            estilo_combo(self.cmb_comp)
        fc.addWidget(l); fc.addWidget(self.cmb_comp)
        der.addLayout(fc)
        self.f_co, self.ax_co, self.c_co = self._mini(); der.addWidget(_caja(self.c_co))
        fb = QHBoxLayout(); fb.setSpacing(6); fb.addStretch()
        self.b_3d = QPushButton(_i18n.t("Mostrar vista 3D"))
        self.b_nuevo = QPushButton(_i18n.t("Modificar datos"))
        for b in (self.b_nuevo, self.b_3d):
            b.setFixedHeight(26); b.setMinimumWidth(110); b.setStyleSheet(BTN_QSS)
            b.setCursor(Qt.CursorShape.PointingHandCursor); fb.addWidget(b)
        der.addLayout(fb)
        der.addStretch(1)
        cont.addLayout(der)
        cont.addStretch(1)
        root.addLayout(cont)
        root.addStretch(1)
        self.cmb_comp.currentIndexChanged.connect(lambda _i: self._dibujar_comp())
        self.b_3d.clicked.connect(self.abrir_3d)
        self.b_nuevo.clicked.connect(lambda: self.on_nuevo and self.on_nuevo())

    def _mini(self):
        f = Figure(figsize=(1, 1)); f.patch.set_facecolor(GRAY_PLOT_BG)
        a = f.add_subplot(111); c = FigureCanvas(f)
        _gm.instalar(c)
        c.setStyleSheet(f'background-color:{GRAY_PLOT_BG};')
        w, h = self.W_MINI, self.H_MINI
        c.setFixedSize(w, h); f.set_size_inches(w/f.dpi, h/f.dpi)
        try:
            f.set_layout_engine('tight', pad=0.5)
        except Exception:
            pass
        return f, a, c

    # ── datos ───────────────────────────────────────────────────────────
    def mostrar(self, res, entrada):
        self.res = res or []; self.entrada = entrada or {}
        prev = self.cmb_comp.currentData()
        self.cmb_comp.blockSignals(True); self.cmb_comp.clear()
        usados = [i for i in range(NC) if any(r['z'][i] > 0 for r in self.res)]
        for i in usados:
            self.cmb_comp.addItem(_nombre_comp(i), f'c:{i}')
        for txt, i0 in GRUPOS:
            self.cmb_comp.addItem(_i18n.t(txt), f'g:{i0}')
        j = self.cmb_comp.findData(prev) if prev is not None else -1
        if j < 0:
            j = self.cmb_comp.findData('c:2')        # metano por defecto
        self.cmb_comp.setCurrentIndex(max(j, 0))
        self.cmb_comp.blockSignals(False)
        self.redibujar()

    def _colores(self):
        n = len(self.res)
        cmap = matplotlib.colormaps.get_cmap('viridis')
        return [cmap(0.0 if n == 1 else k/(n-1)*0.92) for k in range(n)]

    def _fechas(self):
        return [_dt.datetime.fromisoformat(r['fecha']) for r in self.res]

    def redibujar(self):
        self._dibujar_env(); self._dibujar_tendencias(); self._dibujar_comp()
        if self._v3d is not None:
            try:
                self._v3d.dibujar()
            except Exception:
                pass

    def _dibujar_env(self):
        ax = self.ax; ax.clear(); _estilo_ax(ax)
        for r, col in zip(self.res, self._colores()):
            pts = list(r['burbuja']) + list(r['rocio'])
            ax.plot([_u.t_desde_R(t) for _, t in pts], [_u.p_desde_psia(p) for p, _ in pts],
                    '-', color=col, lw=LW_2D, label=_fecha_txt(r['fecha']))
            if r['critico'] is not None:
                ax.plot([_u.t_desde_R(r['critico'][1])], [_u.p_desde_psia(r['critico'][0])],
                        '^', color=col, ms=MS_2D, mec='#000000', mew=0.3)
            p, t = r['cricondenterma']
            ax.plot([_u.t_desde_R(t)], [_u.p_desde_psia(p)], 's', color=col, ms=MS_2D,
                    mec='#000000', mew=0.3)
        ax.set_xlabel(f"{_i18n.t('Temperatura')} ({_u.u('T')})", fontsize=10)
        ax.set_ylabel(f"{_i18n.t('Presion')} ({_u.u('P')})", fontsize=10)
        if self.res:
            leg = ax.legend(title=_i18n.t("Fecha de muestreo"), fontsize=8, title_fontsize=8,
                            framealpha=1.0, fancybox=False, edgecolor='#000000',
                            facecolor=GRAY_PLOT_BG, loc='upper left')
            leg.get_frame().set_linewidth(1.0)
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
        self.canvas.draw_idle()

    def _tendencia(self, ax, canvas, ys, titulo, marcador, color):
        ax.clear(); _estilo_ax(ax, chico=True)
        f = self._fechas()
        ax.plot(f, ys, '-', color=color, lw=LW_2D, zorder=2)
        for x, y, c in zip(f, ys, self._colores()):
            ax.plot([x], [y], marcador, color=c, ms=MS_2D, mec='#000000', mew=0.3, zorder=3)
        ax.set_title(titulo, fontsize=9, loc='right')
        if len(f) == 1:
            ax.set_xlim(f[0] - _dt.timedelta(days=60), f[0] + _dt.timedelta(days=60))
        else:
            marg = (f[-1] - f[0]) * 0.05
            ax.set_xlim(f[0] - marg, f[-1] + marg)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        canvas.draw_idle()

    def _dibujar_tendencias(self):
        ct = [_u.t_desde_R(r['cricondenterma'][1]) for r in self.res]
        cb = [_u.p_desde_psia(r['cricondenbara'][0]) for r in self.res]
        self._tendencia(self.ax_ct, self.c_ct, ct,
                        f"{_i18n.t('Cricondentérmica')} ({_u.u('T')})", 's', '#555555')
        self._tendencia(self.ax_cb, self.c_cb, cb,
                        f"{_i18n.t('Cricondenbárica')} ({_u.u('P')})", 'o', '#555555')

    def _dibujar_comp(self):
        d = self.cmb_comp.currentData()
        if d is None or not self.res:
            return
        tipo, i = d.split(':'); i = int(i)
        if tipo == 'c':
            ys = [r['z'][i]*100 for r in self.res]
        else:
            ys = [sum(r['z'][i:NC])*100 for r in self.res]
        self._tendencia(self.ax_co, self.c_co, ys,
                        f"{self.cmb_comp.currentText()} (% {_i18n.t('molar')})", 'D', '#555555')

    # ── unidades / idioma ───────────────────────────────────────────────
    def aplicar_unidades(self, old=None):
        if self.res:
            self.redibujar()

    def retraducir_grafico(self):
        self.lbl_titulo.setText("ThermoPhase — " + _i18n.t("Historial de pozo"))
        if self._v3d is not None:
            try:
                self._v3d.retraducir()
            except Exception:
                pass
        if self.res:
            self.mostrar(self.res, self.entrada)

    # ── 3D ──────────────────────────────────────────────────────────────
    def abrir_3d(self):
        if not self.res:
            return
        if self._v3d is None:
            self._v3d = Ventana3D(self, self._dueña)
        self._v3d.dibujar()
        self._v3d.showNormal(); self._v3d.raise_(); self._v3d.activateWindow()


class Ventana3D(Ventana3DBase):
    """Envolventes en 3D (temperatura, fecha, presión)."""

    def __init__(self, tab, dueña=None):
        super().__init__(dueña)
        self._tab = tab
        self.retraducir(redibujar=False)

    def _titulos(self):
        return (_i18n.t("Historial de pozo") + " - " + _i18n.t("Vista 3D"),
                "ThermoPhase — " + _i18n.t("Historial de pozo") + ": " + _i18n.t("Vista 3D"))

    def closeEvent(self, ev):
        self._tab._v3d = None
        super().closeEvent(ev)

    def _trazar(self, ax):
        tab = self._tab
        f = tab._fechas(); fn = mdates.date2num(f)
        for r, x, col in zip(tab.res, fn, tab._colores()):
            pts = list(r['burbuja']) + list(r['rocio'])
            ax.plot([_u.t_desde_R(t) for _, t in pts], [x]*len(pts),
                    [_u.p_desde_psia(p) for p, _ in pts], color=col, lw=1.6,
                    label=_fecha_txt(r['fecha']))
        ax.set_xlabel(f"{_i18n.t('Temperatura')} ({_u.u('T')})", fontsize=9, labelpad=8)
        ax.set_ylabel(_i18n.t("Fecha de muestreo"), fontsize=9, labelpad=14)
        ax.set_zlabel(f"{_i18n.t('Presion')} ({_u.u('P')})", fontsize=9, labelpad=8)
        ax.set_yticks(fn); ax.set_yticklabels([x.strftime('%m/%Y') for x in f], fontsize=7)
        leyenda_3d(self.fig, ax, _i18n.t("Fecha de muestreo"))

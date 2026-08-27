"""
Pestaña de Análisis de Sensibilidad para ThermoPhase.

Barre una propiedad (Z de vapor/líquido, densidad de mezcla/líquido/vapor,
gravedad específica, peso molecular, viscosidad, entalpía y entropía) sobre
un rango de temperatura y presión, usando la composición global de la
pestaña de Equilibrio de fases.

Distribución y estética idénticas a la Envolvente de fases: gráfico a la
izquierda; a la derecha la propiedad, la variable del eje X y los rangos
(desde/hasta/N° puntos) de temperatura y presión.  Las curvas usan la misma
paleta y grosor que las líneas de isocalidad de la Envolvente.
"""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGridLayout, QFrame, QProgressBar, QSizePolicy, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from eos import NC
import idioma as _i18n
import unidades as _u
# Reutilizar el estilo EXACTO de combos de la Envolvente (Fusion + flecha).
from pestana_envolvente import _aplicar_estilo_combo, COMBO_STYLE

# ── Estilo (idéntico al de la Envolvente) ─────────────────────
WHITE="#FFFFFF"; GRAY_TIT="#A8A8A8"; GRAY_HDR="#C8C8C8"; GRAY_LBL="#D0D0D0"
GRAY_RES="#E8E8E8"; GRAY_PLOT_BG="#DCDCDC"; BORDER="#888888"
TEXT="#000000"; TEXT_DIM="#555555"; TEXT_RES="#000080"
FONT_F="Arial Narrow"; FS=10

BTN_STYLE=(f'background:{GRAY_HDR};border:2px outset {BORDER};'
           f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
LBL_HDR=(f'background:{GRAY_TIT};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_SEC=(f'background:{GRAY_LBL};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_STYLE=(f'font-family:"{FONT_F}";font-size:{FS}pt;'
           f'color:{TEXT};background:transparent;')
ED_STYLE=(f'QLineEdit {{ background:{WHITE};border:1px solid {BORDER};'
          f'color:{TEXT};font-family:"{FONT_F}";font-size:{FS}pt;'
          f'padding:1px 4px; }}')

# Paleta y grosor idénticos a las líneas de isocalidad de la Envolvente.
CURVA_COLORS = ['#c0392b','#e67e22','#27ae60','#2980b9','#8e44ad']
CURVA_LW = 0.7


def _rho_mezcla(r):
    """Densidad másica de la mezcla (global) = 1/(Vm/ρv + Lm/ρl)."""
    rho_v = r.get('rho_v'); rho_l = r.get('rho_l')
    Vm = r.get('Vm', 0.0) or 0.0; Lm = r.get('Lm', 0.0) or 0.0
    inv = (Vm/rho_v if rho_v else 0.0) + (Lm/rho_l if rho_l else 0.0)
    if inv > 0:
        return 1.0/inv
    if rho_l: return rho_l
    if rho_v: return rho_v
    return None


# Catálogo de propiedades:
#  (key, etiqueta técnica, magnitud_unidad|None, requiere_HS, extractor(r,h))
_PROPS_SENS = [
    ('ZV',       'Factor de compresibilidad (vapor)',   None,   False, lambda r,h: r.get('ZV')),
    ('ZL',       'Factor de compresibilidad (líquido)', None,   False, lambda r,h: r.get('ZL')),
    ('rho_z',    'Densidad másica (mezcla)',            'dens', False, lambda r,h: _rho_mezcla(r)),
    ('rho_l',    'Densidad másica (líquido)',           'dens', False, lambda r,h: r.get('rho_l')),
    ('rho_v',    'Densidad másica (vapor)',             'dens', False, lambda r,h: r.get('rho_v')),
    ('frac_v',   'Fracción de vapor (molar)',           None,   False, lambda r,h: r.get('V')),
    ('sg_l',     'Gravedad específica (líquido)',       None,   False, lambda r,h: r.get('sg_l')),
    ('sg_v',     'Gravedad específica (vapor)',         None,   False, lambda r,h: r.get('sg_v')),
    ('PM_l',     'Peso molecular (líquido)',            None,   False, lambda r,h: r.get('PM_l')),
    ('PM_v',     'Peso molecular (vapor)',              None,   False, lambda r,h: r.get('PM_v')),
    ('mu_l',     'Viscosidad (líquido)',                'visc', False, lambda r,h: r.get('mu_l')),
    ('mu_v',     'Viscosidad (vapor)',                  'visc', False, lambda r,h: r.get('mu_v')),
    ('H_stream', 'Entalpía molar (mezcla)',             'H',    True,  lambda r,h: (h or {}).get('H_stream')),
    ('S_stream', 'Entropía molar (mezcla)',             'S',    True,  lambda r,h: (h or {}).get('S_stream')),
]
_PROPS_BY_KEY = {d[0]: d for d in _PROPS_SENS}


def _conv_mag(mag, v):
    """Convierte al sistema activo según la magnitud (cP es universal)."""
    if v is None or mag is None:
        return v
    if mag == 'dens': return _u.dens_desde(v)
    if mag == 'H':    return _u.H_desde(v)
    if mag == 'S':    return _u.S_desde(v)
    return v


# ── Worker en segundo plano ───────────────────────────────────
class SensWorker(QThread):
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)
    progreso = pyqtSignal(int, int)

    def __init__(self, z, kij, eos, prop_key, eje_x, T_vals, P_vals):
        super().__init__()
        self.z=z; self.kij=kij; self.eos=eos
        self.prop_key=prop_key; self.eje_x=eje_x
        self.T_vals=T_vals; self.P_vals=P_vals   # °R y psia internos

    def run(self):
        try:
            import eos as eng
            eng.set_eos(self.eos)
            necesita_hs = _PROPS_BY_KEY[self.prop_key][3]
            extractor   = _PROPS_BY_KEY[self.prop_key][4]
            if necesita_hs:
                import entalpia_entropia_gen as hs

            # Si el eje X es T, cada curva es una isóbara (P fijo, barrido en
            # T); si es P, cada curva es una isoterma.
            if self.eje_x == 'T':
                x_int = self.T_vals; fam = self.P_vals; x_es_T = True
            else:
                x_int = self.P_vals; fam = self.T_vals; x_es_T = False

            total = max(len(x_int)*len(fam), 1); hecho = 0
            curvas = []
            for vf in fam:
                xs=[]; ys=[]
                for vx in x_int:
                    T = vx if x_es_T else vf
                    P = vf if x_es_T else vx
                    try:
                        rf = eng.calcular(self.z, float(T), float(P),
                                          kij=self.kij, metodo_densidad='COSTALD')
                        rh = hs.calcular_HS(self.z, float(T), float(P), rf,
                                            eos=self.eos, kij=self.kij) if necesita_hs else None
                        val = extractor(rf, rh)
                    except Exception:
                        val = None
                    xs.append(float(vx))
                    ys.append(val if val is not None else np.nan)
                    hecho += 1
                    if hecho % 5 == 0 or hecho == total:
                        self.progreso.emit(hecho, total)
                curvas.append((float(vf), xs, ys))
            self.done.emit({'prop_key': self.prop_key, 'eje_x': self.eje_x,
                            'curvas': curvas})
        except Exception as e:
            import traceback
            self.error.emit(f"{e}\n{traceback.format_exc()}")


class TabSensibilidad(QWidget):
    def __init__(self, get_z, get_kij):
        super().__init__()
        self.get_z=get_z; self.get_kij=get_kij
        self.worker=None
        self._last=None
        self._build()

    # ── Interfaz ──────────────────────────────────────────────
    def _build(self):
        self.setObjectName('sensTab')
        self.setStyleSheet(f'QWidget#sensTab {{ background:{GRAY_LBL}; }}')
        root=QVBoxLayout(self)
        root.setContentsMargins(4,10,4,4); root.setSpacing(3)

        title=QLabel("ThermoPhase — Análisis de Sensibilidad")
        title.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_HDR)
        root.addWidget(title)

        content=QHBoxLayout()
        content.setContentsMargins(6,4,6,4); content.setSpacing(8)

        # ── Izquierda: gráfico ──
        self.left_box=QWidget()
        self.left_box.setStyleSheet(
            f'background:{GRAY_PLOT_BG};border:1px solid {BORDER};')
        self.left_box.setSizePolicy(QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Expanding)
        left_lay=QVBoxLayout(self.left_box)
        left_lay.setContentsMargins(6,6,6,6); left_lay.setSpacing(0)
        self.fig=Figure(figsize=(1,1))
        self.fig.patch.set_facecolor(GRAY_PLOT_BG)
        self.ax=self.fig.add_subplot(111)
        self.ax.set_position([0.135, 0.11, 0.84, 0.86])
        self.canvas=FigureCanvas(self.fig)
        self.canvas.setStyleSheet(f"background-color: {GRAY_PLOT_BG};")
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                                  QSizePolicy.Policy.Expanding)
        self.canvas.setVisible(False)
        left_lay.addWidget(self.canvas)
        content.addWidget(self.left_box, stretch=1)

        # ── Derecha: panel de control (mismo ancho/espaciado que Envolvente) ──
        right=QWidget(); right.setFixedWidth(210)
        vr=QVBoxLayout(right); vr.setContentsMargins(0,0,0,0); vr.setSpacing(6)

        def sub(txt):
            l=QLabel(_i18n.t(txt)); l.setStyleSheet(LBL_STYLE)
            return l

        vr.addWidget(sub("Propiedad:"))
        self.cmb_prop=QComboBox(); self.cmb_prop.setFixedHeight(24)
        for key, lbl, *_ in _PROPS_SENS:
            self.cmb_prop.addItem(_i18n.t(lbl), key)
        _aplicar_estilo_combo(self.cmb_prop)
        vr.addWidget(self.cmb_prop)

        vr.addWidget(sub("Variable del eje X:"))
        self.cmb_eje=QComboBox(); self.cmb_eje.setFixedHeight(24)
        self.cmb_eje.addItem(_i18n.t("Temperatura"), 'T')
        self.cmb_eje.addItem(_i18n.t("Presion"), 'P')
        _aplicar_estilo_combo(self.cmb_eje)
        vr.addWidget(self.cmb_eje)

        sep=QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken); sep.setStyleSheet(f'color:{BORDER};')
        vr.addWidget(sep)

        # Rango de temperatura
        self.lbl_T=QLabel(); self.lbl_T.setStyleSheet(LBL_SEC); self.lbl_T.setFixedHeight(22)
        vr.addWidget(self.lbl_T)
        self.ed_T_ini, self.ed_T_fin, self.ed_T_n = self._fila_rango(vr)

        # Rango de presión
        self.lbl_P=QLabel(); self.lbl_P.setStyleSheet(LBL_SEC); self.lbl_P.setFixedHeight(22)
        vr.addWidget(self.lbl_P)
        self.ed_P_ini, self.ed_P_fin, self.ed_P_n = self._fila_rango(vr)

        self.btn=QPushButton(_i18n.t("Calcular"))
        self.btn.setStyleSheet(BTN_STYLE); self.btn.setFixedHeight(30)
        self.btn.clicked.connect(self.calcular)
        vr.addWidget(self.btn)

        self.prog=QProgressBar(); self.prog.setVisible(False)
        self.prog.setFixedHeight(16); self.prog.setTextVisible(False)
        self.prog.setStyleSheet(
            f'QProgressBar {{ border:1px solid #888888; background:#E8E8E8; }}'
            f'QProgressBar::chunk {{ background:#2d7d2d; }}')
        vr.addWidget(self.prog)

        vr.addStretch()
        content.addWidget(right, stretch=0)
        root.addLayout(content)
        self._retitular_rangos()

    def _fila_rango(self, parent_lay):
        """Fila con Desde / Hasta / N° puntos (celdas vacías por defecto)."""
        g=QGridLayout(); g.setContentsMargins(0,2,0,0)
        g.setHorizontalSpacing(4); g.setVerticalSpacing(4)
        def _lbl(t):
            l=QLabel(_i18n.t(t)); l.setStyleSheet(LBL_STYLE); return l
        def _ed():
            e=QLineEdit(); e.setStyleSheet(ED_STYLE); e.setFixedHeight(22); return e
        ed_ini=_ed(); ed_fin=_ed(); ed_n=_ed()
        g.addWidget(_lbl("Desde:"),    0,0); g.addWidget(ed_ini, 0,1)
        g.addWidget(_lbl("Hasta:"),    1,0); g.addWidget(ed_fin, 1,1)
        g.addWidget(_lbl("N° puntos:"),2,0); g.addWidget(ed_n,   2,1)
        g.setColumnStretch(1,1)
        w=QWidget(); w.setLayout(g); parent_lay.addWidget(w)
        return ed_ini, ed_fin, ed_n

    def _retitular_rangos(self):
        self.lbl_T.setText(f"{_i18n.t('Temperatura')} ({_u.u_abs()}):")
        self.lbl_P.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")

    # ── Cálculo ────────────────────────────────────────────────
    @staticmethod
    def _num(edit):
        t=edit.text().strip().replace(',', '.')
        if not t: return None
        try: return float(t)
        except ValueError: return None

    def calcular(self):
        import dialogos
        z=self.get_z(); s=sum(z)
        if s<=0:
            dialogos.advertencia(self, _i18n.t(
                "Composicion vacia. Ingrese la composicion en la "
                "pestaña de Equilibrio de fases."))
            return
        z=[zi/s for zi in z]

        Ti=self._num(self.ed_T_ini); Tf=self._num(self.ed_T_fin); nT=self._num(self.ed_T_n)
        Pi=self._num(self.ed_P_ini); Pf=self._num(self.ed_P_fin); nP=self._num(self.ed_P_n)
        if None in (Ti,Tf,nT,Pi,Pf,nP):
            dialogos.advertencia(self, _i18n.t(
                "Complete los campos de temperatura y presión (desde, hasta y N° puntos)."))
            return
        nT=int(round(nT)); nP=int(round(nP))
        if nT<2 or nP<1 or Ti<=0 or Tf<=0 or Pi<=0 or Pf<=0:
            dialogos.advertencia(self, _i18n.t(
                "Ingrese rangos positivos y N° de puntos válidos (T≥2, P≥1)."))
            return

        # A internos (°R, psia)
        Ti=_u.R_desde_abs(Ti); Tf=_u.R_desde_abs(Tf)
        Pi=_u.p_a_psia(Pi);     Pf=_u.p_a_psia(Pf)
        if Tf<Ti: Ti,Tf=Tf,Ti
        if Pf<Pi: Pi,Pf=Pf,Pi
        eje=self.cmb_eje.currentData()
        fam_n = nP if eje=='T' else nT
        if fam_n > 12:
            dialogos.advertencia(self, _i18n.t(
                "Demasiadas curvas (>12). Reduzca el N° de puntos de la "
                "variable que NO está en el eje X."))
            return
        T_vals=list(np.linspace(Ti,Tf,nT)); P_vals=list(np.linspace(Pi,Pf,nP))
        prop=self.cmb_prop.currentData()

        import eos as eng
        self.btn.setEnabled(False); self.btn.setText(_i18n.t("Calculando..."))
        self.prog.setRange(0,100); self.prog.setValue(0); self.prog.setVisible(True)
        self.worker=SensWorker(z, self.get_kij(), eng.get_eos(), prop, eje, T_vals, P_vals)
        self.worker.progreso.connect(self._on_prog)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_prog(self, hecho, total):
        self.prog.setValue(int(100*hecho/max(total,1)))

    def _on_done(self, res):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular"))
        self.prog.setVisible(False)
        self._last=res; self._plot(res)

    def _on_error(self, msg):
        import dialogos
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular"))
        self.prog.setVisible(False)
        dialogos.advertencia(self, _i18n.t("Error en el cálculo:")+f"\n{msg}")

    # ── Gráfico ────────────────────────────────────────────────
    def _plot(self, res):
        key=res['prop_key']; eje=res['eje_x']; curvas=res['curvas']
        d=_PROPS_BY_KEY[key]; etiqueta=_i18n.t(d[1]); mag=d[2]
        ax=self.ax; ax.clear()
        ax.set_facecolor('#FFFFFF'); ax.set_axisbelow(True)
        ax.set_position([0.135, 0.11, 0.84, 0.86])

        if eje=='T':
            x_label=f"{_i18n.t('Temperatura')} ({_u.u_abs()})"
            x_conv=lambda v: _u.abs_desde_R(v)
            fam_label=lambda vf: f"{_u.p_desde_psia(vf):.0f} {_u.u('P')}"
            leg_title=_i18n.t('Presion')
        else:
            x_label=f"{_i18n.t('Presion')} ({_u.u('P')})"
            x_conv=lambda v: _u.p_desde_psia(v)
            fam_label=lambda vf: f"{_u.abs_desde_R(vf):.0f} {_u.u_abs()}"
            leg_title=_i18n.t('Temperatura')
        y_unit=f" ({_u.u(mag)})" if mag else ""

        hay=False
        for i,(vf,xs,ys) in enumerate(curvas):
            xa=[x_conv(v) for v in xs]
            ya=[_conv_mag(mag, v) if not (isinstance(v,float) and np.isnan(v)) else np.nan
                for v in ys]
            if any(not (isinstance(v,float) and np.isnan(v)) for v in ya):
                hay=True
            ax.plot(xa, ya, '-', color=CURVA_COLORS[i % len(CURVA_COLORS)],
                    linewidth=CURVA_LW, label=fam_label(vf), zorder=3)

        ax.set_xlabel(x_label, fontsize=10, color=TEXT)
        ax.set_ylabel(f"{etiqueta}{y_unit}", fontsize=10, color=TEXT)
        ax.tick_params(labelsize=8, colors='#000000', direction='in',
                       top=True, right=True, length=4, width=1.0)
        for sp in ax.spines.values():
            sp.set_edgecolor('#000000'); sp.set_linewidth(1.4)
        ax.grid(True, linestyle='-', linewidth=0.8, alpha=1.0, color=GRAY_LBL)
        if hay:
            leg=ax.legend(fontsize=8, framealpha=1.0, fancybox=False,
                          edgecolor='#000000', facecolor=GRAY_PLOT_BG,
                          title=leg_title)
            leg.get_frame().set_linewidth(1.0)
            leg.get_title().set_fontsize(8)
        self.canvas.setVisible(True)
        self.canvas.draw_idle()

    # ── Unidades / idioma ─────────────────────────────────────
    def aplicar_unidades(self, old):
        # Convertir los valores presentes de 'old' al sistema activo.
        def _conv(edit, f_desde, f_a):
            v=self._num(edit)
            if v is None: return
            interno=f_desde(v, old)
            edit.blockSignals(True); edit.setText(f"{f_a(interno):.2f}"); edit.blockSignals(False)
        try:
            _conv(self.ed_T_ini, _u.R_desde_abs, _u.abs_desde_R)
            _conv(self.ed_T_fin, _u.R_desde_abs, _u.abs_desde_R)
            _conv(self.ed_P_ini, _u.p_a_psia,    _u.p_desde_psia)
            _conv(self.ed_P_fin, _u.p_a_psia,    _u.p_desde_psia)
        except Exception:
            pass
        self._retitular_rangos()
        if self._last is not None:
            self._plot(self._last)

    def retraducir_grafico(self):
        self._retitular_rangos()
        self.btn.setText(_i18n.t("Calcular"))
        prop_sel=self.cmb_prop.currentData(); eje_sel=self.cmb_eje.currentData()
        self.cmb_prop.blockSignals(True); self.cmb_prop.clear()
        for key,lbl,*_ in _PROPS_SENS:
            self.cmb_prop.addItem(_i18n.t(lbl), key)
        idx=self.cmb_prop.findData(prop_sel); self.cmb_prop.setCurrentIndex(max(0,idx))
        self.cmb_prop.blockSignals(False)
        self.cmb_eje.blockSignals(True); self.cmb_eje.clear()
        self.cmb_eje.addItem(_i18n.t("Temperatura"), 'T')
        self.cmb_eje.addItem(_i18n.t("Presion"), 'P')
        idx=self.cmb_eje.findData(eje_sel); self.cmb_eje.setCurrentIndex(max(0,idx))
        self.cmb_eje.blockSignals(False)
        if self._last is not None:
            self._plot(self._last)

    # ── Estado ────────────────────────────────────────────────
    def get_estado(self):
        return {
            'entrada': {
                'prop': self.cmb_prop.currentData(),
                'eje':  self.cmb_eje.currentData(),
                'T': [self.ed_T_ini.text(), self.ed_T_fin.text(), self.ed_T_n.text()],
                'P': [self.ed_P_ini.text(), self.ed_P_fin.text(), self.ed_P_n.text()],
            },
            'resultado': None,
        }

    def set_estado(self, datos):
        e=(datos or {}).get('entrada', {})
        try:
            idx=self.cmb_prop.findData(e.get('prop'))
            if idx>=0: self.cmb_prop.setCurrentIndex(idx)
            idx=self.cmb_eje.findData(e.get('eje'))
            if idx>=0: self.cmb_eje.setCurrentIndex(idx)
            if 'T' in e:
                self.ed_T_ini.setText(str(e['T'][0])); self.ed_T_fin.setText(str(e['T'][1]))
                self.ed_T_n.setText(str(e['T'][2]))
            if 'P' in e:
                self.ed_P_ini.setText(str(e['P'][0])); self.ed_P_fin.setText(str(e['P'][1]))
                self.ed_P_n.setText(str(e['P'][2]))
        except Exception:
            pass


# Alias de compatibilidad con el wiring existente.
TabPropiedades = TabSensibilidad

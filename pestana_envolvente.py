"""
Pestaña Envolvente de Fases para ThermoPhase.
Mismo estilo (Arial Narrow) que el resto del programa.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QProgressBar, QGridLayout, QLineEdit,
    QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

import numpy as np
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from matplotlib import font_manager

import mapa_densidad as rf
import dialogos as dialogos
# Colores (mismos que ventana_principal.py)
WHITE="#FFFFFF"; GRAY_TIT="#A8A8A8"; GRAY_HDR="#C8C8C8"; GRAY_LBL="#D0D0D0"; GRAY_RES="#E8E8E8"
GRAY_PLOT_BG="#DCDCDC"   # fondo del recuadro de trazado y de la caja de leyendas
BORDER="#888888"; TEXT="#000000"; TEXT_DIM="#555555"; TEXT_RES="#000080"
FONT_F="Arial Narrow"; FS=10

# ── Estilo retro de las listas desplegables (QComboBox) ───────
# Cambia de modelo comentando el activo y descomentando otro.
# Modelo 1 — Windows 95 clásico  (ACTIVO)
COMBO_STYLE = (
    f'QComboBox {{ background:{WHITE}; border:2px inset {BORDER};'
    f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
    f'QComboBox:on {{ border:2px inset #555555; }}'
    f'QAbstractItemView {{ background:{WHITE}; border:1px solid #000000;'
    f' color:{TEXT}; selection-background-color:#000080; selection-color:#FFFFFF;'
    f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
    f'QAbstractItemView::item {{ min-height:22px; padding:1px 6px; }}'
)

def _aplicar_estilo_combo(combo):
    """Aplica el estilo retro (Modelo 1) al combo y a su lista emergente.
    Usa Fusion por-widget para que el QSS se respete en Windows, fuerza que
    la lista se despliegue hacia ABAJO (no centrada en la opcion actual) y
    conserva la flecha (la dibuja Fusion, por eso no se estiliza ::drop-down)."""
    from PyQt6.QtWidgets import QListView, QStyleFactory, QProxyStyle, QStyle
    class _DesplegarAbajo(QProxyStyle):
        def styleHint(self, hint, option=None, widget=None, returnData=None):
            if hint == QStyle.StyleHint.SH_ComboBox_Popup:
                return 0
            return super().styleHint(hint, option, widget, returnData)
    combo._proxy = _DesplegarAbajo(QStyleFactory.create("Fusion"))
    combo.setStyle(combo._proxy)
    combo.setView(QListView())
    combo._vstyle = QStyleFactory.create("Fusion")
    combo.view().setStyle(combo._vstyle)
    combo.view().setUniformItemSizes(True)   # todas las filas con la misma altura
    combo.setStyleSheet(COMBO_STYLE)
    combo.view().setStyleSheet(COMBO_STYLE)
# Modelo 2 — Plomo IBM / monocromo
# COMBO_STYLE = (
#     f'QComboBox {{ background:{GRAY_RES}; border:1px solid {TEXT_DIM};'
#     f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
#     f'QComboBox::drop-down {{ subcontrol-origin:padding; subcontrol-position:top right;'
#     f' width:18px; background:{GRAY_LBL}; border-left:1px solid {TEXT_DIM}; }}'
#     f'QAbstractItemView {{ background:{GRAY_RES}; border:1px solid {TEXT_DIM};'
#     f' color:{TEXT}; selection-background-color:#555555; selection-color:#FFFFFF;'
#     f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
#     f'QAbstractItemView::item {{ min-height:18px; padding:1px 4px; }}'
# )
# Modelo 3 — Acento naranja (logo)
# COMBO_STYLE = (
#     f'QComboBox {{ background:{WHITE}; border:2px inset {BORDER};'
#     f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
#     f'QComboBox::drop-down {{ subcontrol-origin:padding; subcontrol-position:top right;'
#     f' width:18px; background:#C8C8C8; border-left:2px solid #C0392B; }}'
#     f'QAbstractItemView {{ background:{WHITE}; border:1px solid #C0392B;'
#     f' color:{TEXT}; selection-background-color:#C0392B; selection-color:#FFFFFF;'
#     f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
#     f'QAbstractItemView::item {{ min-height:18px; padding:1px 4px; }}'
# )
# Modelo 4 — Terminal ámbar CRT
# COMBO_STYLE = (
#     f'QComboBox {{ background:#1A1A1A; border:2px inset #555555;'
#     f' color:#FFB000; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
#     f'QComboBox::drop-down {{ subcontrol-origin:padding; subcontrol-position:top right;'
#     f' width:18px; background:#2A2A2A; border-left:1px solid #FFB000; }}'
#     f'QAbstractItemView {{ background:#1A1A1A; border:1px solid #FFB000;'
#     f' color:#FFB000; selection-background-color:#3A2A00; selection-color:#FFD700;'
#     f' outline:0; font-family:"{FONT_F}"; font-size:{FS}pt; }}'
#     f'QAbstractItemView::item {{ min-height:18px; padding:1px 4px; }}'
# )

# Configurar matplotlib para usar Arial Narrow
matplotlib.rcParams['font.family'] = ['Arial Narrow', 'Arial', 'sans-serif']

BTN_STYLE=(f'background:{GRAY_HDR};border:2px outset {BORDER};'
           f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
LBL_HDR=(f'background:{GRAY_TIT};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_SEC=(f'background:{GRAY_LBL};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_RES=(f'background:{GRAY_RES};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px 6px;color:{TEXT_RES};')


class EnvWorker(QThread):
    done=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, z, kij, metodo='ziervogel', max_pts=10000):
        super().__init__(); self.z=z; self.kij=kij; self.metodo=metodo
        self.max_pts=max_pts
    def run(self):
        try:
            from envolvente import curva_envolvente
            # curva_envolvente implementa toda la lógica de selección de método:
            #  - Detecta mezclas casi-azeotrópicas (CO2/C2, iC5/nC5, etc.)
            #  - Para esas mezclas: anula kij del par, prueba Ziervogel primero,
            #    luego Michelsen si Ziervogel no cierra (kij restaurados al salir)
            #  - Para mezclas normales: Ziervogel → Michelsen si no cierra
            # El parámetro self.metodo permite forzar Michelsen directamente
            # cuando la mezcla normal no cerró con Ziervogel; para mezclas
            # casi-azeotrópicas la selección se hace automáticamente.
            if self.metodo == 'michelsen':
                # Forzar Michelsen solo si la mezcla NO es casi-azeotrópica;
                # para casi-azeotrópicas la lógica de kij=0 + Ziervogel
                # ya está en curva_envolvente y no debe saltarse.
                import copy
                from eos import TC
                act = [i for i in range(len(self.z)) if self.z[i] > 1e-8]
                Tc_act = [TC[i] for i in act]
                casi_azeo = (len(act) >= 2 and
                             max(Tc_act) / max(min(Tc_act), 1.0) < 1.10)
                if casi_azeo:
                    # Dejar que curva_envolvente maneje la mezcla difícil
                    res = curva_envolvente(self.z, self.kij)
                else:
                    # Michelsen directo (comportamiento original)
                    from envolvente_michelsen import construir_envolvente
                    r = construir_envolvente(self.z, self.kij,
                                             max_pts=self.max_pts)
                    env = r.get('envolvente', [])
                    crit = r.get('critico')
                    if crit is not None and env:
                        ic = min(range(len(env)),
                                 key=lambda i: (env[i][0]-crit[0])**2
                                              +(env[i][1]-crit[1])**2)
                        burb = env[:ic+1]; rocio = env[ic:]
                    else:
                        burb = env; rocio = []
                    res = {'burbuja': burb, 'rocio': rocio,
                           'critico_burbuja': crit is not None,
                           'critico_rocio':   crit is not None,
                           'critico': crit}
            else:
                res = curva_envolvente(self.z, self.kij)
            self.done.emit(res)
        except Exception as e:
            self.error.emit(str(e))


class IsoWorker(QThread):
    """
    Calcula líneas de isocalidad (fracción de vapor constante). Si no se
    pasa una envolvente ya calculada (env_result=None), la calcula primero
    con Michelsen (las líneas de isocalidad sólo están implementadas con
    ese método) y la emite también para que la UI la dibuje.

    La UI (TabEnvolvente.calcular_isocalidad) siempre invoca con
    env_result=None: la envolvente se recalcula en cada click de "Calcular
    Isocalidad", porque la composición pudo cambiar desde el último cálculo
    de envolvente y una envolvente vieja ya no sería válida.
    """
    done=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, z, kij, calidades, env_result=None, max_pts=2000):
        super().__init__()
        self.z=z; self.kij=kij
        self.calidades=calidades   # {indice_celda: beta (0-1)}
        self.env_result=env_result
        self.max_pts=max_pts
    def run(self):
        try:
            from envolvente_michelsen import construir_envolvente, construir_isocalidad
            env=self.env_result
            if env is None:
                r=construir_envolvente(self.z, self.kij, max_pts=10000)
                ev=r.get('envolvente',[]); crit=r.get('critico')
                if crit is not None and ev:
                    ic=min(range(len(ev)),
                           key=lambda i:(ev[i][0]-crit[0])**2+(ev[i][1]-crit[1])**2)
                    burb=ev[:ic+1]; rocio=ev[ic:]
                else:
                    burb=ev; rocio=[]
                env={'burbuja':burb,'rocio':rocio,
                     'critico_burbuja':crit is not None,
                     'critico_rocio':crit is not None,'critico':crit}

            p_max=None
            crit=env.get('critico')
            if crit is not None:
                p_max=crit[0]*1.02   # margen pequeño sobre la Pc para no cortar antes de tiempo

            lineas={}
            for idx,beta in self.calidades.items():
                r=construir_isocalidad(self.z, beta, self.kij,
                                       max_pts=self.max_pts, p_max=p_max,
                                       critico=crit)
                lineas[idx]=r.get('puntos',[])

            self.done.emit({'envolvente':env, 'lineas':lineas})
        except Exception as e:
            self.error.emit(str(e))


class RegionesWorker(QThread):
    """Worker que recalcula la envolvente (Michelsen) con la composición
    ACTUAL y luego el mapa de densidad + curva de transición.  Todo en
    el mismo hilo para garantizar que envolvente y mapa correspondan
    exactamente a la misma composición.
    """
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, z, kij, n_grid=100, n_curva=40):
        super().__init__()
        self.z = z; self.kij = kij
        self.n_grid = n_grid; self.n_curva = n_curva

    def run(self):
        try:
            # 1) Envolvente por Michelsen (rápido y robusto con la
            #    composición actual)
            from envolvente_michelsen import construir_envolvente
            import envolvente as _env
            r_mich = construir_envolvente(self.z, self.kij, max_pts=8000)
            env_pts = r_mich.get('envolvente', [])
            crit    = r_mich.get('critico')
            if not env_pts:
                # Fallback: usar Ziervogel
                env_res = _env.curva_envolvente(self.z, self.kij)
            else:
                # Dividir en burbuja/rocío alrededor del crítico (mismo
                # esquema que EnvWorker en modo Michelsen)
                ic = None
                if crit is not None:
                    try:
                        ic = env_pts.index(crit)
                    except ValueError:
                        # buscar punto más cercano
                        best_d = float('inf')
                        for i, pt in enumerate(env_pts):
                            d = abs(pt[0]-crit[0]) + abs(pt[1]-crit[1])
                            if d < best_d:
                                best_d = d; ic = i
                if ic is not None:
                    env_res = {'burbuja': env_pts[:ic+1],
                               'rocio':   env_pts[ic:],
                               'critico_burbuja': True,
                               'critico_rocio':   True,
                               'critico': crit,
                               'metodo': 'michelsen'}
                else:
                    env_res = {'burbuja': env_pts, 'rocio': [],
                               'critico_burbuja': False,
                               'critico_rocio':   False,
                               'critico': None,
                               'metodo': 'michelsen'}
            # 2) Mapa de densidad con esa envolvente
            reg_res = rf.calcular_mapa_densidad(
                self.z, self.kij, env_res,
                n_grid=self.n_grid, n_curva=self.n_curva)
            self.done.emit({'envolvente': env_res, 'regiones': reg_res})
        except Exception as e:
            self.error.emit(str(e))


class TabEnvolvente(QWidget):
    def __init__(self, get_z, get_kij):
        super().__init__()
        self.get_z=get_z; self.get_kij=get_kij
        self.worker=None; self.result=None
        self.iso_worker=None
        self.regiones_worker=None
        self._regiones=None      # Resultado de rf.ejecutar_completo o None
        self._build()

    def _build(self):
        self.setObjectName('envTab')
        self.setStyleSheet(f'QWidget#envTab {{ background:{GRAY_LBL}; }}')
        root=QVBoxLayout(self)
        root.setContentsMargins(4,10,4,4); root.setSpacing(3)

        title=QLabel("ThermoPhase — Envolvente de Fases")
        title.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_HDR)
        root.addWidget(title)

        content=QHBoxLayout()
        content.setContentsMargins(6,4,6,4); content.setSpacing(8)

        # Contenedor izquierdo: placeholder (vacío) o canvas (con datos)
        self.left_box = QWidget()
        self.left_box.setStyleSheet(
            f'background:{GRAY_PLOT_BG};border:1px solid {BORDER};')
        self.left_box.setSizePolicy(QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Expanding)
        left_lay = QVBoxLayout(self.left_box)
        left_lay.setContentsMargins(6,6,6,6); left_lay.setSpacing(0)

        # Gráfico (oculto al inicio)
        self.fig=Figure(figsize=(1,1))
        self.fig.patch.set_facecolor(GRAY_PLOT_BG)   # recuadro exterior igual al margen
        self.ax=self.fig.add_subplot(111)
        self.ax.set_position([0.115, 0.085, 0.86, 0.895])
        self.canvas=FigureCanvas(self.fig)
        # Mismo color que left_box: el margen de 6 px queda visible alrededor
        self.canvas.setStyleSheet(f"background-color: {GRAY_PLOT_BG};")
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                                  QSizePolicy.Policy.Expanding)
        self.canvas.setVisible(False)   # oculto hasta calcular
        left_lay.addWidget(self.canvas)
        # Cursor interactivo: muestra P y T en la posición del mouse
        self._hover_annot = None
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
        # Cursor en forma de cruz al estar sobre el gráfico
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)
        # Punto marcado por el usuario (P_psia, T_F) o None
        self._punto_usuario = None

        content.addWidget(self.left_box, stretch=1)

        # Panel derecho
        right=QWidget(); right.setFixedWidth(210)
        vr=QVBoxLayout(right); vr.setContentsMargins(0,0,0,0); vr.setSpacing(6)

        # Selector de método de cálculo
        from PyQt6.QtWidgets import QComboBox
        met_lbl=QLabel("Metodo:")
        met_lbl.setStyleSheet(
            f'font-family:"{FONT_F}";font-size:{FS}pt;color:{TEXT};'
            f'background:transparent;')
        met_lbl.setFixedHeight(16)
        vr.addWidget(met_lbl)
        self.cmb_metodo=QComboBox()
        self.cmb_metodo.addItems(["Ziervogel-Poling","Michelsen"])
        self.cmb_metodo.setFixedHeight(24)
        _aplicar_estilo_combo(self.cmb_metodo)
        vr.addWidget(self.cmb_metodo)

        self.btn=QPushButton("Calcular Envolvente")
        self.btn.setStyleSheet(BTN_STYLE); self.btn.setFixedHeight(30)
        self.btn.clicked.connect(self.calcular)
        vr.addWidget(self.btn)

        # Barra de progreso estándar
        self.prog=QProgressBar()
        self.prog.setRange(0,0)            # modo indeterminado
        self.prog.setVisible(False)
        self.prog.setTextVisible(False)    # sin texto
        self.prog.setFixedHeight(18)
        self.prog.setStyleSheet(
            f'QProgressBar {{ border:1px solid #888888; background:#E8E8E8;'
            f'border-radius:0px; }}'
            f'QProgressBar::chunk {{ background:#2d7d2d; }}')
        vr.addWidget(self.prog)

        # Toggle discreto: mostrar mapa de densidad + curva de transición
        # monofásica sobre el gráfico de envolvente (estilo Whitson).
        # El label "(cargando)" al lado se muestra mientras el worker
        # calcula la envolvente + el mapa; luego se oculta.
        h_reg = QHBoxLayout()
        h_reg.setContentsMargins(0, 0, 0, 0); h_reg.setSpacing(3)
        self.chk_reg = QCheckBox("Mostrar mapa de densidad")
        self.chk_reg.setStyleSheet(
            f'QCheckBox {{ color:{TEXT}; font-family:"{FONT_F}"; '
            f'font-size:{FS}pt; padding:2px 0px; }}'
            f'QCheckBox::indicator {{ width:12px; height:12px; }}')
        self.chk_reg.toggled.connect(self._on_toggle_regiones)
        h_reg.addWidget(self.chk_reg)
        self.lbl_reg_cargando = QLabel("")
        self.lbl_reg_cargando.setStyleSheet(
            f'color:{TEXT_DIM}; font-family:"{FONT_F}"; '
            f'font-size:{FS-2}pt; padding-top:3px;')
        h_reg.addWidget(self.lbl_reg_cargando)
        h_reg.addStretch()
        _reg_row = QWidget(); _reg_row.setLayout(h_reg)
        vr.addWidget(_reg_row)

        sep=QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f'color:{BORDER};')
        vr.addWidget(sep)

        res_title=QLabel("Puntos especiales:")
        res_title.setStyleSheet(LBL_SEC); res_title.setFixedHeight(22)
        vr.addWidget(res_title)

        grid=QGridLayout(); grid.setSpacing(4); grid.setContentsMargins(0,2,0,0)
        lbl_style=(f'font-family:"{FONT_F}";font-size:{FS}pt;'
                   f'color:{TEXT};background:transparent;')

        def res_val():
            l=QLabel(""); l.setStyleSheet(LBL_RES)
            l.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            return l

        rows=[("Cricondentérmica (°F):","cric_T"),
              ("Cricondenbárica (psi):","cric_P")]
        self.res_labels={}
        for r,(txt,key) in enumerate(rows):
            lbl=QLabel(txt); lbl.setStyleSheet(lbl_style); lbl.setWordWrap(True)
            grid.addWidget(lbl,r,0)
            rv=res_val(); self.res_labels[key]=rv
            grid.addWidget(rv,r,1)
        vr.addLayout(grid)

        # ── Sección: marcar un punto en el gráfico (triángulo verde) ──
        sep2=QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f'color:{BORDER};')
        vr.addWidget(sep2)
        pt_title=QLabel("Marcar punto:")
        pt_title.setStyleSheet(LBL_SEC); pt_title.setFixedHeight(22)
        vr.addWidget(pt_title)

        gp=QGridLayout(); gp.setSpacing(4); gp.setContentsMargins(0,2,0,0)
        ed_style=(f'QLineEdit {{ background:{WHITE};border:1px solid {BORDER};'
                  f'color:{TEXT};font-family:"{FONT_F}";font-size:{FS}pt;'
                  f'padding:1px 4px; }}')
        lblP=QLabel("Presión (psia):"); lblP.setStyleSheet(lbl_style)
        self.ed_pP=QLineEdit(); self.ed_pP.setStyleSheet(ed_style)
        self.ed_pP.setFixedHeight(22)
        gp.addWidget(lblP,0,0); gp.addWidget(self.ed_pP,0,1)
        lblT=QLabel("Temperatura (°F):"); lblT.setStyleSheet(lbl_style)
        self.ed_pT=QLineEdit(); self.ed_pT.setStyleSheet(ed_style)
        self.ed_pT.setFixedHeight(22)
        gp.addWidget(lblT,1,0); gp.addWidget(self.ed_pT,1,1)
        vr.addLayout(gp)

        hb_pt=QHBoxLayout(); hb_pt.setSpacing(4)
        self.btn_pt=QPushButton("Colocar")
        self.btn_pt.setStyleSheet(BTN_STYLE); self.btn_pt.setFixedHeight(26)
        self.btn_pt.clicked.connect(self._colocar_punto)
        hb_pt.addWidget(self.btn_pt)
        self.btn_pt_clear=QPushButton("Quitar")
        self.btn_pt_clear.setStyleSheet(BTN_STYLE); self.btn_pt_clear.setFixedHeight(26)
        self.btn_pt_clear.clicked.connect(self._quitar_punto)
        hb_pt.addWidget(self.btn_pt_clear)
        vr.addLayout(hb_pt)

        # ── Sección: líneas de isocalidad (fracción de vapor constante) ──
        sep3=QFrame(); sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet(f'color:{BORDER};')
        vr.addWidget(sep3)
        iso_title=QLabel("Líneas de isocalidad:")
        iso_title.setStyleSheet(LBL_SEC); iso_title.setFixedHeight(22)
        vr.addWidget(iso_title)

        # Colores fijos, uno por línea (mismo orden que las celdas)
        self.ISO_COLORS = ['#c0392b','#e67e22','#27ae60','#2980b9','#8e44ad']

        gi=QGridLayout(); gi.setSpacing(4); gi.setContentsMargins(0,2,0,0)
        self.ed_iso=[]   # QLineEdit de cada celda (texto = % de calidad, vacío = no calcular)
        for i in range(5):
            sw=QLabel(); sw.setFixedSize(10,10)
            sw.setStyleSheet(f'background:{self.ISO_COLORS[i]};'
                             f'border:1px solid {BORDER};')
            lbl=QLabel(f"Línea de isocalidad N°{i+1}:")
            lbl.setStyleSheet(lbl_style); lbl.setWordWrap(True)
            ed=QLineEdit(); ed.setStyleSheet(ed_style); ed.setFixedHeight(22)
            ed.setPlaceholderText("% vapor")
            self.ed_iso.append(ed)
            gi.addWidget(sw,i,0)
            gi.addWidget(lbl,i,1)
            gi.addWidget(ed,i,2)
        gi.setColumnStretch(1,1)
        vr.addLayout(gi)

        self.btn_iso=QPushButton("Calcular Isocalidad")
        self.btn_iso.setStyleSheet(BTN_STYLE); self.btn_iso.setFixedHeight(26)
        self.btn_iso.clicked.connect(self.calcular_isocalidad)
        vr.addWidget(self.btn_iso)

        self.prog_iso=QProgressBar()
        self.prog_iso.setRange(0,0)
        self.prog_iso.setVisible(False)
        self.prog_iso.setTextVisible(False)
        self.prog_iso.setFixedHeight(18)
        self.prog_iso.setStyleSheet(
            f'QProgressBar {{ border:1px solid #888888; background:#E8E8E8;'
            f'border-radius:0px; }}'
            f'QProgressBar::chunk {{ background:#2d7d2d; }}')
        vr.addWidget(self.prog_iso)

        self._isocalidad = {}   # {indice_celda: [(P,T),...]}

        vr.addStretch()

        self.btn_exp=QPushButton("Exportar CSV")
        self.btn_exp.setStyleSheet(BTN_STYLE); self.btn_exp.setEnabled(False)
        self.btn_exp.clicked.connect(self.exportar_csv)
        vr.addWidget(self.btn_exp)

        content.addWidget(right)
        root.addLayout(content, stretch=1)


    def calcular(self):
        z=self.get_z()
        if abs(sum(z)-1.0)>1e-3:
            dialogos.advertencia(self,
                "La suma de fracciones debe ser 1.0")
            return
        kij=self.get_kij()
        metodo = 'michelsen' if self.cmb_metodo.currentIndex()==1 else 'ziervogel'
        # Una nueva envolvente puede venir de una composición distinta: las
        # líneas de isocalidad calculadas antes ya no corresponden y se
        # descartan (el usuario debe recalcularlas si las sigue necesitando).
        self._isocalidad = {}
        self.btn.setEnabled(False); self.btn.setText("Calculando...")
        self.prog.setVisible(True)
        self.worker=EnvWorker(z,kij,metodo,max_pts=10000)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_error(self,msg):
        self.btn.setEnabled(True); self.btn.setText("Calcular Envolvente")
        self.prog.setVisible(False)
        dialogos.error(self, msg)

    def _on_done(self,res):
        self.btn.setEnabled(True); self.btn.setText("Calcular Envolvente")
        self.prog.setVisible(False)
        self.result=res
        self.canvas.setVisible(True)   # mostrar el gráfico ya con datos
        # La envolvente cambió: invalidar cualquier mapa de densidad previo
        self._regiones = None
        self.chk_reg.blockSignals(True)
        self.chk_reg.setChecked(False)
        self.chk_reg.blockSignals(False)
        self._plot(res)
        self._update_results(res)
        self.btn_exp.setEnabled(True)

    def calcular_isocalidad(self):
        """Lee las celdas de % de calidad llenas, valida, y lanza el cálculo.
        SIEMPRE recalcula la envolvente (Michelsen) desde la composición
        actual antes de trazar las líneas — la composición pudo cambiar
        desde el último cálculo de envolvente, así que no se reutiliza una
        envolvente guardada."""
        z=self.get_z()
        if abs(sum(z)-1.0)>1e-3:
            dialogos.advertencia(self,
                "La suma de fracciones debe ser 1.0")
            return

        calidades={}
        for i,ed in enumerate(self.ed_iso):
            txt=ed.text().strip()
            if not txt: continue
            try:
                val=float(txt.replace(',', '.'))
            except ValueError:
                dialogos.advertencia(self, f"Valor inválido en Línea de isocalidad N°{i+1}.")
                return
            if not (0.0 < val < 100.0):
                dialogos.advertencia(self, f"La calidad N°{i+1} debe estar entre 0 y 100 (%).")
                return
            calidades[i]=val/100.0   # a fracción 0-1

        if not calidades:
            dialogos.info(self, "Ingrese al menos un valor de % de vapor en las celdas.")
            return

        kij=self.get_kij()
        self.btn_iso.setEnabled(False); self.btn_iso.setText("Calculando...")
        self.prog_iso.setVisible(True)
        # env_result=None fuerza al worker a recalcular la envolvente con
        # Michelsen desde la composición actual, en vez de reutilizar una
        # ya calculada previamente.
        self.iso_worker=IsoWorker(z,kij,calidades,env_result=None)
        self.iso_worker.done.connect(self._on_iso_done)
        self.iso_worker.error.connect(self._on_iso_error)
        self.iso_worker.start()

    def _on_iso_error(self,msg):
        self.btn_iso.setEnabled(True); self.btn_iso.setText("Calcular Isocalidad")
        self.prog_iso.setVisible(False)
        dialogos.error(self, msg)

    def _on_iso_done(self,res):
        self.btn_iso.setEnabled(True); self.btn_iso.setText("Calcular Isocalidad")
        self.prog_iso.setVisible(False)
        # La envolvente del worker es siempre fresca (recalculada con la
        # composición actual): se adopta como resultado principal vigente.
        env=res.get('envolvente')
        if env is not None:
            self.result=env
            self.canvas.setVisible(True)
            self._update_results(env)
            self.btn_exp.setEnabled(True)
            # Asegurar que el selector de método refleje Michelsen, ya que
            # las líneas de isocalidad sólo están implementadas con ese motor.
            if self.cmb_metodo.currentIndex()!=1:
                self.cmb_metodo.blockSignals(True)
                self.cmb_metodo.setCurrentIndex(1)
                self.cmb_metodo.blockSignals(False)
        self._isocalidad = res.get('lineas', {})
        self._plot(self.result if self.result is not None else {'burbuja':[],'rocio':[]})

    # ── Mapa de densidad (toggle discreto) ──────────────────────
    def _on_toggle_regiones(self, checked):
        """Handler del QCheckBox 'Mostrar mapa de densidad'.

        Marcado → recalcula la envolvente por Michelsen con la
                  composición actual y luego el mapa de densidad, y
                  replotea todo.  De este modo el mapa y la envolvente
                  SIEMPRE corresponden a la misma composición.
        Desmarcado → limpia el mapa y replotea la envolvente sola.
        """
        if not checked:
            self._regiones = None
            if self.result is not None:
                self._plot(self.result)
            return
        # Lanzar cálculo (envelope + mapa) con la composición actual
        z = self.get_z()
        if abs(sum(z)-1.0) > 1e-3:
            dialogos.advertencia(self,
                "La suma de fracciones debe ser 1.0")
            self.chk_reg.blockSignals(True)
            self.chk_reg.setChecked(False)
            self.chk_reg.blockSignals(False)
            return
        kij = self.get_kij()
        self.chk_reg.setEnabled(False)
        self.lbl_reg_cargando.setText("(cargando)")
        self.regiones_worker = RegionesWorker(
            z, kij, n_grid=100, n_curva=40)
        self.regiones_worker.done.connect(self._on_regiones_done)
        self.regiones_worker.error.connect(self._on_regiones_error)
        self.regiones_worker.finished.connect(self._on_regiones_finished)
        self.regiones_worker.start()

    def _on_regiones_error(self, msg):
        dialogos.error(self, msg)
        self.chk_reg.blockSignals(True)
        self.chk_reg.setChecked(False)
        self.chk_reg.blockSignals(False)

    def _on_regiones_done(self, data):
        """El worker devolvió {envolvente, regiones}.  Actualizamos ambos.
        La envolvente se refresca porque quizás cambió la composición."""
        self.result = data['envolvente']
        self._regiones = data['regiones']
        self._isocalidad = {}    # invalidar isocalidades previas
        self._update_results(self.result)
        self.btn_exp.setEnabled(True)
        self.canvas.setVisible(True)
        self._plot(self.result)

    def _on_regiones_finished(self):
        self.lbl_reg_cargando.setText("")
        self.chk_reg.setEnabled(True)

    # ── Guardar / restaurar estado ─────────────────────────────────────
    def get_estado(self):
        """Devuelve inputs y resultado (envolvente + mapa + isocalidades)."""
        calidades = [ed.text().strip() for ed in self.ed_iso]
        return {
            'entrada': {
                'metodo':    self.cmb_metodo.currentText(),
                'mostrar_regiones': self.chk_reg.isChecked(),
                'calidades': calidades,
                'punto_manual_P': self.ed_pP.text().strip(),
                'punto_manual_T': self.ed_pT.text().strip(),
            },
            'resultado': {
                'envolvente':    self.result,
                'regiones':      self._regiones,
                'isocalidad':    self._isocalidad,
                'punto_usuario': self._punto_usuario,
            } if self.result is not None else None,
        }

    def set_estado(self, datos):
        """Restaura la envolvente, mapa e isocalidades sin recalcular.
        Solo re-dibuja el canvas con los datos previamente guardados."""
        e = datos.get('entrada', {}) or {}
        # Metodo
        m = e.get('metodo', 'Ziervogel-Poling')
        idx = self.cmb_metodo.findText(m)
        if idx >= 0:
            self.cmb_metodo.setCurrentIndex(idx)
        # Calidades
        cals = e.get('calidades', [])
        for i, ed in enumerate(self.ed_iso):
            ed.setText(cals[i] if i < len(cals) else "")
        # Punto manual (P,T)
        self.ed_pP.setText(e.get('punto_manual_P', "") or "")
        self.ed_pT.setText(e.get('punto_manual_T', "") or "")
        # Resultado
        r = datos.get('resultado')
        if not r:
            return
        env = r.get('envolvente')
        if env is None:
            return
        self.result = env
        # Reconstruir isocalidad (json convierte las claves int a str)
        raw_iso = r.get('isocalidad') or {}
        self._isocalidad = {}
        for k, v in raw_iso.items():
            try:
                self._isocalidad[int(k)] = [tuple(pt) for pt in v]
            except Exception:
                pass
        # Reconstruir regiones (mapa de densidad)
        reg = r.get('regiones')
        if reg is not None:
            import numpy as _np
            reg_np = {
                'Tg':      _np.asarray(reg.get('Tg'), dtype=float),
                'Pg':      _np.asarray(reg.get('Pg'), dtype=float),
                'rho_map': _np.asarray(reg.get('rho_map'), dtype=float),
            }
            # Poligono de la envolvente cerrado (T,P) — imprescindible
            # para el fill gris que colorea el interior de la envolvente
            # sobre el mapa de densidad. Si falta este dato el interior
            # queda sin colorear al abrir la simulacion.
            poly = reg.get('poly_env_TP')
            if poly:
                reg_np['poly_env_TP'] = _np.asarray(poly, dtype=float)
            # Curva de transicion LIQ<->VAP (por si en el futuro se
            # vuelve a activar su dibujado)
            if reg.get('curva_T') is not None:
                reg_np['curva_T'] = _np.asarray(reg['curva_T'], dtype=float)
            if reg.get('curva_P') is not None:
                reg_np['curva_P'] = _np.asarray(reg['curva_P'], dtype=float)
            for k in ('rho_min','rho_max'):
                if k in reg: reg_np[k] = float(reg[k])
            self._regiones = reg_np
            self.chk_reg.blockSignals(True)
            self.chk_reg.setChecked(True)
            self.chk_reg.blockSignals(False)
        else:
            self._regiones = None
            self.chk_reg.blockSignals(True)
            self.chk_reg.setChecked(False)
            self.chk_reg.blockSignals(False)
        # Punto usuario
        pu = r.get('punto_usuario')
        if pu is not None and len(pu) == 2:
            self._punto_usuario = (float(pu[0]), float(pu[1]))
        else:
            self._punto_usuario = None
        # Mostrar canvas y actualizar
        self.canvas.setVisible(True)
        self.btn_exp.setEnabled(True)
        self._update_results(self.result)
        self._plot(self.result)

    def _plot(self,res):
        ax=self.ax; ax.clear()
        self._hover_annot = None   # se invalida al limpiar los ejes
        ax.set_facecolor('#FFFFFF')
        ax.set_axisbelow(True)   # rejilla por detrás de los marcadores

        # Aplicar la posición del axes principal PRIMERO, para que las
        # coordenadas de figura sean consistentes cuando después
        # agreguemos la colorbar como axes independiente.
        ax.set_position([0.115, 0.085, 0.86, 0.895])

        # Limpiar cualquier axes hijo previo (colorbar y su contenedor
        # gris del cálculo anterior) — ax.clear() no los remueve porque
        # son axes independientes, no hijos del subplot.
        fig = self.canvas.figure
        for a in list(fig.axes):
            if a is not ax:
                try:
                    fig.delaxes(a)
                except Exception:
                    pass
        # Por seguridad también limpiar patches sueltos de figura
        # (versiones anteriores del código añadían un Rectangle overlay
        # con transFigure que podía cubrir todo el gráfico si la posición
        # del inset aún no estaba resuelta).
        fig.patches.clear()

        # ── Mapa de densidad + fill envolvente + curva de transición ──
        # Cuando el usuario activa el mapa de densidad, se dibuja:
        #   • Fondo (zorder=0): imshow del mapa de densidad en lb/ft³
        #   • Fill gris (zorder=1): interior de la envolvente con el
        #     polígono continuo del recorrido natural (sin escalones)
        #   • Curva de transición LIQ↔VAP como línea negra fina continua
        #   • Colorbar en un axes independiente colocado con coordenadas
        #     absolutas de figura, envuelto en otro axes contenedor gris
        #     con bordes negros (estilo Win95, similar a la leyenda)
        # La envolvente misma se dibuja después como LÍNEAS CONTINUAS.
        reg = self._regiones
        if reg is not None:
            import matplotlib.cm as _cm
            Tg_F = reg['Tg'] - 459.67
            Pg   = reg['Pg']
            rho  = reg['rho_map']
            try:
                cmap = matplotlib.colormaps.get_cmap('RdYlGn').copy()
            except (AttributeError, KeyError):
                cmap = _cm.get_cmap('RdYlGn').copy()
            cmap.set_bad(alpha=0.0)
            valid = rho[np.isfinite(rho)]
            if valid.size > 0:
                v_max = float(np.percentile(valid, 98))
                v_min = 0.0
            else:
                v_max, v_min = 45.0, 0.0
            im = ax.imshow(np.ma.masked_invalid(rho),
                           extent=[Tg_F[0], Tg_F[-1], Pg[0], Pg[-1]],
                           origin='lower', aspect='auto',
                           cmap=cmap, alpha=0.5, vmin=v_min, vmax=v_max,
                           interpolation='bilinear', zorder=0)
            # Fill gris del interior de la envolvente con el polígono
            # de recorrido natural (sin invertir la rocío)
            poly = reg.get('poly_env_TP')
            if poly is not None and len(poly) >= 3:
                poly_F = np.column_stack([poly[:,0] - 459.67, poly[:,1]])
                ax.fill(poly_F[:,0], poly_F[:,1],
                        color='#E8E8E8', alpha=1.0, zorder=1,
                        edgecolor='none')
            # Curva de transición LIQ↔VAP: OCULTA temporalmente
            # (a Sergio no le convence que no llegue hasta el punto crítico
            # verdadero — se está estudiando por qué difiere de la
            # intersección burbuja/rocío).  El cálculo se sigue haciendo
            # en el worker, sólo no se dibuja.
            # if len(reg['curva_T']) > 0:
            #     ax.plot(reg['curva_T'] - 459.67, reg['curva_P'],
            #             linestyle='-', color='#000000', linewidth=0.8,
            #             label='Transición monofásica', zorder=4)
            # Colorbar en axes independiente, en coordenadas absolutas
            # de figura basadas en la posición del ax principal ya
            # aplicada arriba con set_position (sin depender de inset_
            # axes ni de Rectangle overlay que causaban problemas de
            # layout en PyQt).
            ax_pos = ax.get_position()
            # Contenedor gris: dimensiones generosas para dar espacio al
            # label "ρ (lb/ft³)" y a los números de los ticks
            cont_w   = 0.095 * ax_pos.width
            cont_h   = 0.36  * ax_pos.height
            cont_x   = ax_pos.x0 + 0.02  * ax_pos.width
            cont_y   = ax_pos.y0 + 0.03  * ax_pos.height
            # Axes CONTENEDOR con fondo gris estilo leyenda Win95
            cont = fig.add_axes([cont_x, cont_y, cont_w, cont_h])
            cont.set_facecolor(GRAY_PLOT_BG)
            cont.set_xticks([]); cont.set_yticks([])
            for s in cont.spines.values():
                s.set_edgecolor('#000000'); s.set_linewidth(1.0)
            # Axes de la BARRA de color (dentro del contenedor):
            # más angosta, dejando espacio a la derecha para el label
            bar_w    = 0.22 * cont_w
            bar_h    = 0.80 * cont_h
            bar_x    = cont_x + 0.15 * cont_w
            bar_y    = cont_y + 0.10 * cont_h
            cax = fig.add_axes([bar_x, bar_y, bar_w, bar_h])
            cbar = fig.colorbar(im, cax=cax)
            cbar.set_label('ρ (lb/ft³)', fontsize=7, color=TEXT, labelpad=2)
            cbar.ax.tick_params(labelsize=6, colors=TEXT, length=2,
                                width=0.8, pad=1)
            cbar.outline.set_edgecolor('#000000')
            cbar.outline.set_linewidth(0.8)

        burb=res.get('burbuja',[]); rocio=res.get('rocio',[])
        Tb=[t-459.67 for _,t in burb]; Pb=[p for p,_ in burb]
        Td=[t-459.67 for _,t in rocio]; Pd=[p for p,_ in rocio]

        # Estilo de las curvas de burbuja/rocío depende de si el mapa
        # está activo: con mapa → líneas continuas del mismo grosor que
        # la de transición (pegadas al fill gris, sin espacios).
        # Sin mapa → marcadores triangulares (estilo original).
        if self._regiones is not None:
            if Tb and Pb:
                ax.plot(Tb, Pb, linestyle='-', color='#a83218',
                        linewidth=0.9, label='Curva de Burbuja', zorder=5)
            if Td and Pd:
                ax.plot(Td, Pd, linestyle='-', color='#1a4fa8',
                        linewidth=0.9, label='Curva de Rocío', zorder=5)
        else:
            if Tb and Pb:
                ax.plot(Tb,Pb,linestyle='none',marker='^',
                        color='#a83218',markersize=3,
                        label='Curva de Burbuja')
            if Td and Pd:
                ax.plot(Td,Pd,linestyle='none',marker='^',
                        color='#1a4fa8',markersize=3,
                        label='Curva de Rocío')

        # Líneas de isocalidad (finas, un color distinto por línea)
        for idx,pts in getattr(self,'_isocalidad',{}).items():
            if not pts: continue
            color=self.ISO_COLORS[idx % len(self.ISO_COLORS)]
            Ti=[t-459.67 for _,t in pts]; Pi=[p for p,_ in pts]
            txt=self.ed_iso[idx].text().strip()
            ax.plot(Ti,Pi,linestyle='-',linewidth=0.7,
                    color=color, label=f'{txt}% vapor', zorder=3)

        # Punto marcado por el usuario (triángulo verde)
        if self._punto_usuario is not None:
            Pp, Tp_F = self._punto_usuario
            ax.plot([Tp_F],[Pp],linestyle='none',marker='^',
                    color='#2d9d2d',markersize=5,
                    markeredgecolor='#145214',markeredgewidth=0.5,
                    label='Punto', zorder=5)

        ax.set_xlabel("Temperatura (°F)", fontsize=10, color=TEXT)
        ax.set_ylabel("Presión (psia)", fontsize=10, color=TEXT)

        # ── Estilo Modelo A (Win95 hundido) ───────────────────
        # Marco negro cerrado en los 4 lados, ticks hacia adentro
        # en los 4 lados, rejilla sólida fina y leyenda en caja recta.
        ax.tick_params(labelsize=8, colors='#000000', direction='in',
                       top=True, right=True, length=4, width=1.0)
        for s in ax.spines.values():
            s.set_edgecolor('#000000'); s.set_linewidth(1.4)
        ax.grid(True, linestyle='-', linewidth=0.8, alpha=1.0, color=GRAY_LBL)
        if Tb or Td:
            leg = ax.legend(fontsize=8, framealpha=1.0, fancybox=False,
                            edgecolor='#000000', facecolor=GRAY_PLOT_BG)
            leg.get_frame().set_linewidth(1.0)
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
        # Cuando hay regiones monofásicas activas, forzar los límites al rango
        # extendido (imshow no siempre los ajusta al inflar el gráfico)
        if self._regiones is not None:
            Tg_F = self._regiones['Tg'] - 459.67
            Pg   = self._regiones['Pg']
            ax.set_xlim(float(Tg_F[0]),  float(Tg_F[-1]))
            ax.set_ylim(float(Pg[0]),    float(Pg[-1]))
        # Nota: set_position() se aplicó al inicio de _plot para que las
        # coordenadas absolutas del axes contenedor de la colorbar sean
        # consistentes.  No repetir aquí.
        self.canvas.draw_idle()

    def _colocar_punto(self):
        """Lee P (psia) y T (°F) de los campos y marca un triángulo verde."""
        try:
            Pp = float(self.ed_pP.text().replace(',', '.'))
            Tp = float(self.ed_pT.text().replace(',', '.'))
        except ValueError:
            dialogos.advertencia(self,
                "Ingrese valores numéricos válidos de presión y temperatura.")
            return
        self._punto_usuario = (Pp, Tp)
        # Redibujar si ya hay una envolvente calculada
        if self.result is not None:
            self._plot(self.result)
        else:
            # Si no hay envolvente, igual mostrar el punto solo
            self.canvas.setVisible(True)
            self._plot({'burbuja': [], 'rocio': []})

    def _quitar_punto(self):
        """Quita el punto marcado y redibuja."""
        self._punto_usuario = None
        if self.result is not None:
            self._plot(self.result)
        else:
            self._plot({'burbuja': [], 'rocio': []})

    def _on_hover(self, event):
        # Solo si hay datos y el cursor está dentro del área de trazado
        if not self.canvas.isVisible() or event.inaxes != self.ax:
            if self._hover_annot is not None:
                self._hover_annot.set_visible(False)
                self.canvas.draw_idle()
            return
        T = event.xdata   # °F (eje X)
        P = event.ydata   # psia (eje Y)
        if T is None or P is None:
            return
        # Crear o actualizar la anotación
        if self._hover_annot is None:
            self._hover_annot = self.ax.annotate(
                "", xy=(0,0), xytext=(12,12),
                textcoords="offset points",
                fontsize=8, fontfamily='Arial Narrow', color="#000000",
                bbox=dict(boxstyle="round,pad=0.4", fc=GRAY_PLOT_BG,
                          ec="#888888", lw=0.8),
                zorder=10)

        # ── Posicionamiento dinámico para no salirse del área ──────
        # Decidir a qué lado del cursor mostrar el recuadro según en qué
        # parte del eje está, para que nunca se pierda fuera del gráfico.
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        fx = (T - xmin) / (xmax - xmin) if xmax != xmin else 0.5
        fy = (P - ymin) / (ymax - ymin) if ymax != ymin else 0.5
        # Si está en la mitad derecha, mostrar el recuadro hacia la izquierda
        dx = -12 if fx > 0.5 else 12
        # Si está en la mitad superior, mostrar el recuadro hacia abajo
        dy = -12 if fy > 0.5 else 12
        ha = 'right' if dx < 0 else 'left'
        va = 'top'   if dy < 0 else 'bottom'
        self._hover_annot.set_ha(ha)
        self._hover_annot.set_va(va)
        self._hover_annot.set_position((dx, dy))

        self._hover_annot.xy = (T, P)
        self._hover_annot.set_text(f"T = {T:.1f} °F\nP = {P:.1f} psia")
        self._hover_annot.set_visible(True)
        self.canvas.draw_idle()

    def _update_results(self,res):
        burb=res.get('burbuja',[]); rocio=res.get('rocio',[])
        def fv(v): return f"{v:.1f}" if v is not None else ""
        Tb=[t-459.67 for _,t in burb]; Pb=[p for p,_ in burb]
        Td=[t-459.67 for _,t in rocio]; Pd=[p for p,_ in rocio]
        all_T=Tb+Td; all_P=Pb+Pd
        # Cricondentérmica = T máxima de la envolvente
        self.res_labels['cric_T'].setText(fv(max(all_T)) if all_T else "")
        # Cricondenbárica = P máxima de la envolvente
        self.res_labels['cric_P'].setText(fv(max(all_P)) if all_P else "")

    def exportar_csv(self):
        if not self.result: return
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        path,_=QFileDialog.getSaveFileName(self,"Guardar CSV",
            "envolvente.csv","CSV (*.csv)")
        if not path: return
        try:
            with open(path,'w',encoding='utf-8') as f:
                f.write("Curva,P (psia),T (R),T (F)\n")
                for p,t in self.result.get('burbuja',[]):
                    f.write(f"Burbuja,{p:.4f},{t:.4f},{t-459.67:.4f}\n")
                for p,t in self.result.get('rocio',[]):
                    f.write(f"Rocio,{p:.4f},{t:.4f},{t-459.67:.4f}\n")
                for idx,pts in getattr(self,'_isocalidad',{}).items():
                    txt=self.ed_iso[idx].text().strip()
                    etiqueta=f"Isocalidad_{txt}pct"
                    for p,t in pts:
                        f.write(f"{etiqueta},{p:.4f},{t:.4f},{t-459.67:.4f}\n")
            dialogos.info(self, f"CSV guardado:\n{path}")
        except Exception as e:
            dialogos.error(self, str(e))

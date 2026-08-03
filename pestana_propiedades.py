"""
Pestaña Propiedades Termodinámicas para ThermoPhase.
Calcula Entalpía y Entropía molar de la corriente y por fase,
dada T y P, usando la composición global de la pestaña de Equilibrio.

Método según PVTsim (Method Documentation, "Thermal and Volumetric
Properties"):
    H = Σ zi H_id_i + H_res           S = Σ zi S_id_i + S_res
con Cp° = polinomio de 3er grado (Reid et al., 1977), Tref = 273.15 K
(0 °C / 32 °F) y Pref = 1 atm — sin offsets propios de HYSYS.

Soporta Peng-Robinson y Soave-Redlich-Kwong (la función de partida es la
misma; sólo cambian δ1, δ2 y los parámetros a, b, m de cada EOS).

Unidades: H en Btu/lbmol, S en Btu/(lbmol·°F)  [= Btu/(lbmol·°R), pues un
intervalo de 1 °F equivale a 1 °R].
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGridLayout, QFrame, QAbstractSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from eos import NC
import idioma as _i18n

# ── Estilo (mismo que las demás pestañas) ─────────────────────
WHITE="#FFFFFF"; GRAY_TIT="#A8A8A8"; GRAY_HDR="#C8C8C8"; GRAY_LBL="#D0D0D0"
GRAY_RES="#E8E8E8"; BORDER="#888888"; TEXT="#000000"; TEXT_DIM="#555555"
TEXT_RES="#000080"; FONT_F="Arial Narrow"; FS=10

BTN_STYLE=(f'background:{GRAY_LBL};border:2px outset {BORDER};'
           f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
LBL_TIT=(f'background:{GRAY_TIT};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_SEC=(f'background:{GRAY_LBL};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')


# ── Worker en segundo plano ───────────────────────────────────
class PropWorker(QThread):
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)
    def __init__(self, z, T_R, P, kij, eos):
        super().__init__()
        self.z=z; self.T=T_R; self.P=P; self.kij=kij; self.eos=eos
    def run(self):
        try:
            import eos as eng
            import entalpia_entropia_gen as hs
            # Entalpia/entropia GENERICAS con la EOS elegida (PR o SRK),
            # metodo estandar (funcion de partida), sin ajustes de HYSYS.
            eng.set_eos(self.eos)
            res_flash = eng.calcular(self.z, self.T, self.P, kij=self.kij)
            res_hs    = hs.calcular_HS(self.z, self.T, self.P, res_flash,
                                       eos=self.eos, kij=self.kij)
            res_hs['modo'] = res_flash.get('modo', '?')
            self.done.emit(res_hs)
        except Exception as e:
            import traceback
            self.error.emit(f"{e}\n{traceback.format_exc()}")


class TabPropiedades(QWidget):
    def __init__(self, get_z, get_kij):
        super().__init__()
        self.get_z=get_z; self.get_kij=get_kij
        self.worker=None
        self.last_result=None
        self._build()

    # helper para etiquetas uniformes
    def _lbl(self, txt, res=False, w=None, dim=False):
        l=QLabel(txt)
        if res:
            style=(f'background:{WHITE};border:1px solid {BORDER};'
                   f'color:{TEXT_RES};padding:2px 6px;'
                   f'font-family:"{FONT_F}";font-size:{FS}pt;')
        elif dim:
            style=(f'background:transparent;border:none;'
                   f'color:{TEXT_DIM};padding:2px 6px;'
                   f'font-family:"{FONT_F}";font-size:9pt;')
        else:
            style=(f'background:transparent;border:1px solid {BORDER};'
                   f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
        l.setStyleSheet(style); l.setFixedHeight(24)
        if w: l.setFixedWidth(w)
        return l

    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root=QVBoxLayout(self)
        root.setContentsMargins(4,10,4,4); root.setSpacing(3)

        # Título
        title=QLabel("ThermoPhase — Propiedades Termodinamicas (Entalpia / Entropia)")
        title.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_TIT)
        root.addWidget(title)

        # ── Panel de entrada ──────────────────────────────────
        in_title=QLabel("Datos de entrada:")
        in_title.setStyleSheet(LBL_SEC); in_title.setFixedHeight(22)
        root.addWidget(in_title)

        in_box=QFrame()
        in_box.setStyleSheet('background:transparent;border:none;')
        gl=QGridLayout(in_box); gl.setContentsMargins(6,6,6,6); gl.setSpacing(6)

        gl.addWidget(self._lbl("Temperatura (°R):", w=140), 0, 0)
        self.sp_T=QDoubleSpinBox()
        self.sp_T.setRange(0.0, 3000.0); self.sp_T.setDecimals(2)
        self.sp_T.setSpecialValueText(" "); self.sp_T.setValue(0.0)
        self.sp_T.setFixedHeight(24)
        self.sp_T.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_T.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gl.addWidget(self.sp_T, 0, 1)

        gl.addWidget(self._lbl("Presion (psia):", w=140), 1, 0)
        self.sp_P=QDoubleSpinBox()
        self.sp_P.setRange(0.0, 15000.0); self.sp_P.setDecimals(2)
        self.sp_P.setSpecialValueText(" "); self.sp_P.setValue(0.0)
        self.sp_P.setFixedHeight(24)
        self.sp_P.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_P.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gl.addWidget(self.sp_P, 1, 1)

        self.btn=QPushButton("Calcular propiedades")
        self.btn.setStyleSheet(BTN_STYLE); self.btn.setFixedHeight(26)
        self.btn.clicked.connect(self.calcular)
        gl.addWidget(self.btn, 2, 0, 1, 2)

        gl.setColumnStretch(0,0); gl.setColumnStretch(1,1)
        root.addWidget(in_box)

        # ── Panel de resultados ───────────────────────────────
        res_title=QLabel("Resultados:")
        res_title.setStyleSheet(LBL_SEC); res_title.setFixedHeight(22)
        root.addWidget(res_title)

        res_box=QFrame()
        res_box.setStyleSheet('background:transparent;border:none;')
        rl=QGridLayout(res_box); rl.setContentsMargins(6,6,6,6); rl.setSpacing(4)

        # Fila 0: cabeceras
        rl.addWidget(self._lbl(""),                            0, 0)
        h_stream=self._lbl("Corriente global")
        h_stream.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(h_stream,                                 0, 1)
        h_vap=self._lbl("Fase vapor")
        h_vap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(h_vap,                                    0, 2)
        h_liq=self._lbl("Fase liquida")
        h_liq.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(h_liq,                                    0, 3)

        # Fila 1: Entalpía
        rl.addWidget(self._lbl("Entalpia molar [Btu/lbmol]:", w=210), 1, 0)
        self.h_stream=self._lbl("", res=True); self.h_stream.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.h_vap   =self._lbl("", res=True); self.h_vap.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.h_liq   =self._lbl("", res=True); self.h_liq.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.h_stream, 1, 1)
        rl.addWidget(self.h_vap,    1, 2)
        rl.addWidget(self.h_liq,    1, 3)

        # Fila 2: Entropía
        rl.addWidget(self._lbl("Entropia molar [Btu/lbmol-F]:", w=210), 2, 0)
        self.s_stream=self._lbl("", res=True); self.s_stream.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.s_vap   =self._lbl("", res=True); self.s_vap.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.s_liq   =self._lbl("", res=True); self.s_liq.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.s_stream, 2, 1)
        rl.addWidget(self.s_vap,    2, 2)
        rl.addWidget(self.s_liq,    2, 3)

        # Fila 3: Fraccion de fase
        rl.addWidget(self._lbl("Fraccion molar de fase:", w=210), 3, 0)
        # Vacío por defecto — se rellenará con "1.0000" al ejecutar
        # el cálculo (misma convención que las demás celdas)
        self.vf_stream=self._lbl("", res=True); self.vf_stream.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.vf_vap   =self._lbl("", res=True); self.vf_vap.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.vf_liq   =self._lbl("", res=True); self.vf_liq.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.vf_stream, 3, 1)
        rl.addWidget(self.vf_vap,    3, 2)
        rl.addWidget(self.vf_liq,    3, 3)

        rl.setColumnStretch(0,0)
        rl.setColumnStretch(1,1); rl.setColumnStretch(2,1); rl.setColumnStretch(3,1)
        root.addWidget(res_box)

        # ── Estado / modo ─────────────────────────────────────
        st_row=QHBoxLayout(); st_row.setContentsMargins(6,0,6,0)
        self.lbl_modo=QLabel("")
        self.lbl_modo.setStyleSheet(
            f'color:{TEXT_DIM};font-family:"{FONT_F}";font-size:9pt;background:transparent;')
        st_row.addWidget(self.lbl_modo)
        st_row.addStretch()
        root.addLayout(st_row)

        root.addStretch()

    # ── Ejecutar cálculo ──────────────────────────────────────
    def calcular(self):
        import dialogos as dialogos
        # Validar composición
        z=self.get_z(); s=sum(z)
        if s<=0:
            dialogos.advertencia(self, _i18n.t(
                "Composicion vacia. Ingrese la composicion en la "
                "pestaña de Equilibrio de fases."))
            return
        # Normalizar
        z=[zi/s for zi in z]

        T=self.sp_T.value(); P=self.sp_P.value()
        if T<=0 or P<=0:
            dialogos.advertencia(self,
                _i18n.t("Ingrese Temperatura y Presion positivas."))
            return

        self.btn.setEnabled(False); self.btn.setText(_i18n.t("Calculando..."))
        self.lbl_modo.setText("")
        self._clear_results()

        import eos as eng
        # get_z() ya fijo la EOS del contexto (principal o del fluido).
        eos_ctx = eng.get_eos()
        kij = self.get_kij()
        self.worker=PropWorker(z, T, P, kij, eos_ctx)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _clear_results(self):
        for lbl in (self.h_stream,self.h_vap,self.h_liq,
                    self.s_stream,self.s_vap,self.s_liq,
                    self.vf_vap,self.vf_liq):
            lbl.setText("")
        self.vf_stream.setText("1.0000")

    def _fmt(self, v, nd=3):
        if v is None: return ""
        try:
            return f"{v:,.{nd}f}"
        except Exception:
            return str(v)

    def _on_done(self, r):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular propiedades"))
        self.last_result = r
        self._render(r)

    def _render(self, r):
        """Muestra los resultados. Llamado por el worker y por set_estado."""
        V=r.get('V',0.0); L=r.get('L',0.0)
        modo=r.get('modo','?')

        self.h_stream.setText(self._fmt(r.get('H_stream'), 3))
        self.s_stream.setText(self._fmt(r.get('S_stream'), 4))
        self.h_vap.setText(self._fmt(r.get('H_vapor'), 3))
        self.s_vap.setText(self._fmt(r.get('S_vapor'), 4))
        self.h_liq.setText(self._fmt(r.get('H_liquido'), 3))
        self.s_liq.setText(self._fmt(r.get('S_liquido'), 4))

        self.vf_stream.setText("1.0000")
        self.vf_vap.setText(f"{V:.4f}" if r.get('H_vapor')   is not None else "")
        self.vf_liq.setText(f"{L:.4f}" if r.get('H_liquido') is not None else "")

        # Etiqueta de modo
        modo_txt={
            'vapor_unico':   'Sistema en fase vapor unica.',
            'liquido_unico': 'Sistema en fase liquida unica.',
            'vapor_liquido': 'Sistema bifasico vapor-liquido.',
            'bifasico':      'Sistema bifasico vapor-liquido.',
            'supercritico':  'Sistema en region supercritica.',
        }.get(modo, f'Modo: {modo}')
        self.lbl_modo.setText(_i18n.t(modo_txt))

    def _on_error(self, msg):
        import dialogos as dialogos
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular propiedades"))
        self.lbl_modo.setText("")
        dialogos.error(self, msg)

    # ── Guardar / restaurar estado ────────────────────────────
    def get_estado(self):
        return {
            'entrada': {
                'T_R':   float(self.sp_T.value()),
                'P_psi': float(self.sp_P.value()),
            },
            'resultado': self.last_result,   # dict o None
        }

    def set_estado(self, datos):
        e = datos.get('entrada', {}) or {}
        try:    self.sp_T.setValue(float(e.get('T_R', 0.0) or 0.0))
        except: self.sp_T.setValue(0.0)
        try:    self.sp_P.setValue(float(e.get('P_psi', 0.0) or 0.0))
        except: self.sp_P.setValue(0.0)
        r = datos.get('resultado')
        if r:
            self.last_result = r
            self._render(r)


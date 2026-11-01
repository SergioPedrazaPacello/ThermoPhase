"""
pestana_orificio.py — Módulo Medidor de orificio (AGA 3 + AGA 8).

Una sola ventana con el estilo de las ventanas de ingreso de ThermoPhase:
datos de entrada a la izquierda (cada uno con su lista de unidades), la
cromatografía a la derecha y, abajo, el caudal calculado con su lista de
unidades.

Convenciones (iguales a las de las calculadoras de campo):
  · la presión estática puede ser manométrica (se suma la presión
    atmosférica) o absoluta, según la unidad elegida;
  · "H₂O referido al agua a 39.2 °F (4 °C) o a 60 °F (AGA 3);
  · el caudal estándar se expresa a la presión y temperatura base
    ingresadas, en todas sus unidades.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QComboBox, QLineEdit, QApplication)
from PyQt6.QtCore import Qt

import idioma as _i18n
import unidades as _u
import dialogos
import aga3 as ag
import aga8_detail as a8
import pestana_op_unitarias as po

M_FT3 = 0.028316846592
LB_KG = 0.45359237
PSI = ag.PSI_PA
W = po.W_CAMPO              # ancho común de campos y listas
W_U = 112                   # ancho de las listas de unidades


# ── Unidades: (nombre, a_SI(v), desde_SI(v)) ────────────────────────────
def _lin(f, off=0.0):
    return (lambda v: v*f + off, lambda v: (v - off)/f)


U_PEST = [("psig", *_lin(PSI)), ("psia", *_lin(PSI)), ("kPag", *_lin(1e3)), ("kPaa", *_lin(1e3)),
          ("barg", *_lin(1e5)), ("bara", *_lin(1e5)), ("kg/cm²g", *_lin(98066.5)),
          ("kg/cm²a", *_lin(98066.5))]
U_PABS = [("psia", *_lin(PSI)), ("kPaa", *_lin(1e3)), ("bara", *_lin(1e5)), ("kg/cm²a", *_lin(98066.5))]
# Pulgada de agua según la temperatura de referencia del agua (Pa)
H2O_REF = [("60 °F (AGA 3)", ag.INH2O_PA), ("68 °F (20 °C)", 248.64135),
           ("39.2 °F (4 °C)", ag.INH2O_4C_PA)]
_INH2O = [ag.INH2O_PA]          # referencia vigente (la fija la ventana)
U_DP = [("inH₂O", lambda v: v*_INH2O[0], lambda p: p/_INH2O[0]),
        ("kPa", *_lin(1e3)), ("psi", *_lin(PSI)), ("mbar", *_lin(100.0)), ("mmH₂O", *_lin(9.80665))]
U_T = [("°F", lambda v: (v - 32.0)/1.8 + 273.15, lambda k: (k - 273.15)*1.8 + 32.0),
       ("°C", lambda v: v + 273.15, lambda k: k - 273.15)]
U_L = [("in", *_lin(0.0254)), ("mm", *_lin(1e-3))]
# Caudal: desde (qm kg/s, Qb m³/s a condiciones base)
U_Q = [("MMscfd", lambda qm, qb: qb/M_FT3*86400.0/1e6),
       ("MCF/d", lambda qm, qb: qb/M_FT3*86400.0/1e3),
       ("scf/h", lambda qm, qb: qb/M_FT3*3600.0),
       ("E3M3/d", lambda qm, qb: qb*86400.0/1e3),
       ("Sm³/d", lambda qm, qb: qb*86400.0),
       ("Sm³/h", lambda qm, qb: qb*3600.0),
       ("kg/h", lambda qm, qb: qm*3600.0),
       ("lb/h", lambda qm, qb: qm*3600.0/LB_KG)]
# Caudal especificado → (nombre, factor a SI, tipo): 'std' m³/s a condiciones base, 'mas' kg/s
U_QIN = [("MMscfd", 1e6*M_FT3/86400.0, 'std'), ("MCF/d", 1e3*M_FT3/86400.0, 'std'),
         ("scf/h", M_FT3/3600.0, 'std'), ("E3M3/d", 1e3/86400.0, 'std'),
         ("Sm³/d", 1.0/86400.0, 'std'), ("Sm³/h", 1.0/3600.0, 'std'),
         ("kg/h", 1.0/3600.0, 'mas'), ("lb/h", LB_KG/3600.0, 'mas')]
INCOGNITAS = ['Q', 'dP', 'd']
Y_METODOS = [('ISO', "AGA 3 (2012) / ISO 5167-2"), ('1992', "AGA 3 (1992)")]


def _f(t):
    return po._a_float(t)


def _num(v, sig=7):
    t = f"{v:.{sig}g}"
    if 'e' in t:
        t = f"{v:.4f}"
    return t


class CampoUnidad:
    """Campo numérico con lista de unidades; al cambiar la unidad convierte
    el valor escrito, de modo que la magnitud física no cambia."""

    def __init__(self, dlg, unidades, idx=0, ancho=W - W_U - 4):
        self.u = unidades
        self.e = dlg._campo(ancho)
        self.c = QComboBox(); self.c.setFixedSize(W_U, 22); dlg.h['estilo_combo'](self.c)
        self.c.addItems([n for n, *_r in unidades])
        self.c.setCurrentIndex(idx)
        self._idx = idx
        self.c.currentIndexChanged.connect(self._cambio)

    def _cambio(self, i):
        v = _f(self.e.text())
        if v is not None:
            si = self.u[self._idx][1](v)
            self.e.setText(_num(self.u[i][2](si)))
        self._idx = i

    def si(self):
        v = _f(self.e.text())
        return None if v is None else self.u[self.c.currentIndex()][1](v)

    def set_si(self, v):
        self.e.setText(_num(self.u[self.c.currentIndex()][2](v)))

    def nombre(self):
        return self.u[self.c.currentIndex()][0]

    def layout(self):
        f = QHBoxLayout(); f.setSpacing(4); f.addWidget(self.e); f.addWidget(self.c)
        return f

    def set_visible(self, on):
        self.e.setVisible(on); self.c.setVisible(on)


# ════════════════════════════════════════════════════════════════════════
class VentanaOrificio(QWidget):
    def __init__(self, h, fuentes, datos_fuente, activos):
        super().__init__()
        from eos import NC
        self.NC = NC
        self.h = h; self.datos_fuente = datos_fuente
        self.on_tamano = None; self.res = None
        self.setObjectName('oriTab')
        self.setStyleSheet(f'QWidget#oriTab {{ background:#e0e0e0; }}')
        root = QVBoxLayout(self); root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)
        root.addWidget(po._titulo("ThermoPhase — " + _i18n.t("Medidor de orificio (AGA 3)")))
        cols = QHBoxLayout(); cols.setSpacing(12)
        root.addLayout(cols)
        F = _u.sistema() == 'FIELD'

        # ── Columna izquierda: datos ────────────────────────────────────
        c1 = QVBoxLayout(); c1.setSpacing(4)
        gm = QGridLayout(); gm.setSpacing(4)
        # Qué se calcula (por ahora solo el caudal; luego presión diferencial
        # y diámetro del orificio) y, para el caudal, punto único o serie.
        self.c_calc = self._combo(["Caudal", "Presión diferencial", "Diámetro del orificio"])
        gm.addWidget(self._etq("Modo de cálculo:"), 0, 0); gm.addWidget(self.c_calc, 0, 1)
        self.c_modo = self._combo(["Punto único", "Serie de tiempo"])
        self.l_modo = self._etq("Cálculo de caudal:")
        gm.addWidget(self.l_modo, 1, 0); gm.addWidget(self.c_modo, 1, 1)
        c1.addLayout(gm)
        c1.addSpacing(4)
        c1.addWidget(self._lbl_txt("Flujo básico:"))
        g = QGridLayout(); g.setSpacing(4); r = 0
        self.f_P = CampoUnidad(self, U_PEST, 0 if F else 2)
        r = self._fila(g, r, "Presión estática:", self.f_P)
        self.f_dP = CampoUnidad(self, U_DP, 0 if F else 1)
        r = self._fila(g, r, "Presión diferencial:", self.f_dP)
        self.f_T = CampoUnidad(self, U_T, 0 if F else 1)
        r = self._fila(g, r, "Temperatura de flujo:", self.f_T)
        self.f_d = CampoUnidad(self, U_L, 0 if F else 1)
        r = self._fila(g, r, "Diámetro del orificio:", self.f_d)
        self.f_D = CampoUnidad(self, U_L, 0 if F else 1)
        r = self._fila(g, r, "Diámetro del tubo:", self.f_D)
        self.c_toma = self._combo(["Aguas arriba", "Aguas abajo"])
        r = self._fila_w(g, r, "Toma de presión estática:", self.c_toma)
        # Caudal especificado (modos presión diferencial y diámetro del orificio)
        self.f_Qin = CampoUnidad(self, [(n, (lambda v, f=f: v*f), (lambda x, f=f: x/f))
                                        for n, f, _t in U_QIN], 0 if F else 3)
        self.l_Qin = self._etq("Caudal especificado:")
        g.addWidget(self.l_Qin, r, 0); g.addLayout(self.f_Qin.layout(), r, 1); r += 1
        c1.addLayout(g)

        c1.addSpacing(4)
        c1.addWidget(self._lbl_txt("Configuración avanzada:"))
        g = QGridLayout(); g.setSpacing(4); r = 0
        self.f_Patm = CampoUnidad(self, U_PABS, 0 if F else 1)
        self.l_Patm = self._etq("Presión atmosférica:")
        g.addWidget(self.l_Patm, r, 0); g.addLayout(self.f_Patm.layout(), r, 1); r += 1
        self.c_z = self._combo(["AGA 8 (Detail)", "Ecuación de estado (flash)", "Manual"])
        r = self._fila_w(g, r, "Factor de compresibilidad:", self.c_z)
        self.l_eos = self._etq("Ecuación de estado:"); self.c_eos = self._combo(h['eos_items'])
        g.addWidget(self.l_eos, r, 0); g.addWidget(self.c_eos, r, 1); r += 1
        self.l_Zf = self._etq("Compresibilidad en flujo:"); self.e_Zf = self._campo()
        g.addWidget(self.l_Zf, r, 0); g.addWidget(self.e_Zf, r, 1); r += 1
        self.l_Zb = self._etq("Compresibilidad base:"); self.e_Zb = self._campo()
        g.addWidget(self.l_Zb, r, 0); g.addWidget(self.e_Zb, r, 1); r += 1
        self.l_G = self._etq("Gravedad específica ideal:"); self.e_G = self._campo()
        g.addWidget(self.l_G, r, 0); g.addWidget(self.e_G, r, 1); r += 1
        self.f_Pb = CampoUnidad(self, U_PABS, 0 if F else 1)
        r = self._fila(g, r, "Presión base:", self.f_Pb)
        self.f_Tb = CampoUnidad(self, U_T, 0 if F else 1)
        r = self._fila(g, r, "Temperatura base:", self.f_Tb)
        mats = [n for _k, n, _a in ag.MATERIALES]
        self.f_Trd = CampoUnidad(self, U_T, 0 if F else 1)
        r = self._fila(g, r, "Temperatura del orificio:", self.f_Trd)
        self.c_mat_d = self._combo(mats); self.c_mat_d.setCurrentIndex(len(mats) - 1)
        r = self._fila_w(g, r, "Material del orificio:", self.c_mat_d)
        self.f_TrD = CampoUnidad(self, U_T, 0 if F else 1)
        r = self._fila(g, r, "Temperatura del tubo:", self.f_TrD)
        self.c_mat_D = self._combo(mats); self.c_mat_D.setCurrentIndex(len(mats) - 1)
        r = self._fila_w(g, r, "Material del tubo:", self.c_mat_D)
        self.c_y = self._combo([t for _k, t in Y_METODOS])
        r = self._fila_w(g, r, "Factor de expansión:", self.c_y)
        self.c_h2o = self._combo([t for t, _v in H2O_REF])
        r = self._fila_w(g, r, "Referencia de inH₂O:", self.c_h2o)
        c1.addLayout(g)
        c1.addStretch(1)
        cols.addLayout(c1)

        # ── Columna derecha: cromatografía y caudal ─────────────────────
        c2 = QVBoxLayout(); c2.setSpacing(4)
        fc = QHBoxLayout(); fc.setSpacing(6)
        fc.addWidget(self._lbl_txt("Cromatografía:")); fc.addSpacing(12)
        fc.addWidget(self._lbl_txt("Cargar de:"))
        self.cmb_fuente = QComboBox(); self.cmb_fuente.setFixedSize(170, 22)
        h['estilo_combo'](self.cmb_fuente)
        fc.addWidget(self.cmb_fuente)
        c2.addLayout(fc)
        self.cont_tc = QVBoxLayout(); self.cont_tc.setContentsMargins(0, 0, 0, 0)
        c2.addLayout(self.cont_tc)
        self.tc = None
        self._construir_tabla(activos)

        fb = QHBoxLayout(); fb.setSpacing(8)
        self.b_norm = QPushButton(_i18n.t("Normalizar")); self.b_ok = QPushButton(_i18n.t("Calcular"))
        for b in (self.b_norm, self.b_ok):
            b.setFixedHeight(26); b.setMinimumWidth(84); b.setStyleSheet(po.BTN_QSS)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        fb.addStretch(1); fb.addWidget(self.b_ok); fb.addWidget(self.b_norm)
        c2.addLayout(fb)
        c2.addSpacing(10)
        self.l_resultado = self._lbl_txt("Resultado:")
        c2.addWidget(self.l_resultado)
        gr = QGridLayout(); gr.setSpacing(4)
        self.l_Q = QLabel(""); self.l_Q.setFixedSize(W - W_U - 4, 22)
        self.l_Q.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.l_Q.setStyleSheet(f'background:{po.GRAY_EMPTY}; color:{po.TEXT_RES};'
                               f' border:1px solid {po.BORDER}; font-family:"{po.FONT_F}";'
                               f' font-size:{po.FS}pt; padding:0px 4px;')
        self.c_Qu = QComboBox(); self.c_Qu.setFixedSize(W_U, 22); h['estilo_combo'](self.c_Qu)
        self.c_Qu.addItems([n for n, _f in U_Q]); self.c_Qu.setCurrentIndex(0 if F else 3)
        self.c_dPu = QComboBox(); self.c_dPu.setFixedSize(W_U, 22); h['estilo_combo'](self.c_dPu)
        self.c_dPu.addItems([n for n, *_r in U_DP]); self.c_dPu.setCurrentIndex(0 if F else 1)
        self.c_du = QComboBox(); self.c_du.setFixedSize(W_U, 22); h['estilo_combo'](self.c_du)
        self.c_du.addItems([n for n, *_r in U_L]); self.c_du.setCurrentIndex(0 if F else 1)
        self.l_Q.setFixedWidth(130)
        hq = QHBoxLayout(); hq.setSpacing(4); hq.addWidget(self.l_Q)
        for c_ in (self.c_Qu, self.c_dPu, self.c_du):
            hq.addWidget(c_)
        # Relación de diámetros β (modo diámetro del orificio)
        self.l_beta_t = self._etq("Relación β:"); self.l_beta_t.setMinimumWidth(0)
        self.l_beta = QLabel(""); self.l_beta.setFixedSize(130, 22)
        self.l_beta.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lq = self._etq("Caudal:"); lq.setMinimumWidth(0)
        self.l_caudal = lq
        gr.addWidget(lq, 0, 0); gr.addLayout(hq, 0, 1)
        self.l_beta.setStyleSheet(self.l_Q.styleSheet())
        hb = QHBoxLayout(); hb.setSpacing(4); hb.addWidget(self.l_beta); hb.addStretch(1)
        gr.addWidget(self.l_beta_t, 1, 0); gr.addLayout(hb, 1, 1)
        c2.addLayout(gr)
        self.lbl_aviso = QLabel(""); self.lbl_aviso.setWordWrap(True)
        self.lbl_aviso.setStyleSheet(f'font-family:"{po.FONT_F}";font-size:{po.FS}pt;'
                                     f'color:{po.AVISO};background:transparent;')
        self.lbl_aviso.setVisible(False)
        c2.addWidget(self.lbl_aviso)
        c2.addStretch(1)
        self.w_c2 = QWidget(); self.w_c2.setLayout(c2); self.w_c2.setStyleSheet('background:transparent;')
        cols.addWidget(self.w_c2, 0, Qt.AlignmentFlag.AlignTop)
        cols.addStretch(1)

        self.b_norm.clicked.connect(self._normalizar)
        self.b_ok.clicked.connect(self.calcular)
        self.c_Qu.currentIndexChanged.connect(lambda _i: self._mostrar())
        self.c_dPu.currentIndexChanged.connect(lambda _i: self._mostrar())
        self.c_du.currentIndexChanged.connect(lambda _i: self._mostrar())
        self.c_calc.currentIndexChanged.connect(lambda _i: self._on_calc())
        self.c_z.currentIndexChanged.connect(lambda _i: self._visibles())
        self.c_modo.currentIndexChanged.connect(lambda _i: self._visibles())
        self.serie = None
        self.c_h2o.currentIndexChanged.connect(self._on_h2o)
        self.f_P.c.currentIndexChanged.connect(lambda _i: self._visibles())
        self.cmb_fuente.activated.connect(lambda _i: self._cargar_fuente(self.cmb_fuente.currentData()))

        # Valores iniciales
        self.f_P.set_si(100.0*PSI)
        self.f_dP.set_si(20.0*ag.INH2O_4C_PA)
        self.f_T.set_si((90.0 - 32.0)/1.8 + 273.15)
        self.f_d.set_si(0.5*0.0254); self.f_D.set_si(2.0*0.0254)
        for f in (self.f_Patm, self.f_Pb):
            f.set_si(14.7*PSI)
        for f in (self.f_Tb, self.f_Trd, self.f_TrD):
            f.set_si((60.0 - 32.0)/1.8 + 273.15)
        self.e_Zf.setText("1"); self.e_Zb.setText("1"); self.e_G.setText("0.6")
        self.actualizar(fuentes, activos)
        if fuentes:
            self.cmb_fuente.setCurrentIndex(1)
            self._cargar_fuente(fuentes[0][0])
        self._visibles()

    # ── construcción ────────────────────────────────────────────────────
    def _lbl_txt(self, t):
        l = QLabel(_i18n.t(t)); l.setStyleSheet(po.TXT_QSS); return l

    def _etq(self, t):
        l = QLabel(_i18n.t(t)); l.setStyleSheet(po.LBL_QSS); l.setFixedHeight(22)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        l.setMinimumWidth(190)
        return l

    def _campo(self, w=None):
        e = QLineEdit(); e.setStyleSheet(po.ED_QSS); e.setFixedSize(W if w is None else w, 22)
        e.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return e

    def _combo(self, items):
        c = QComboBox(); c.setFixedSize(W, 22); self.h['estilo_combo'](c)
        c.addItems([_i18n.t(x) for x in items])
        return c

    def _fila(self, g, r, txt, campo):
        g.addWidget(self._etq(txt), r, 0); g.addLayout(campo.layout(), r, 1)
        return r + 1

    def _fila_w(self, g, r, txt, w):
        g.addWidget(self._etq(txt), r, 0); g.addWidget(w, r, 1)
        return r + 1

    def _on_h2o(self, i):
        _INH2O[0] = H2O_REF[i][1]

    def incognita(self):
        return INCOGNITAS[self.c_calc.currentIndex()]

    def es_serie(self):
        return self.incognita() == 'Q' and self.c_modo.currentIndex() == 1

    def _on_calc(self):
        self.res = None; self.l_Q.setText(""); self.l_beta.setText("")
        self.lbl_aviso.setVisible(False)
        self._visibles()

    def _visibles(self):
        _INH2O[0] = H2O_REF[self.c_h2o.currentIndex()][1]
        serie = self.es_serie()
        inc = self.incognita()
        self.l_modo.setVisible(inc == 'Q'); self.c_modo.setVisible(inc == 'Q')
        for f in (self.f_P, self.f_dP, self.f_T):
            f.e.setEnabled(not serie)        # en serie, solo se elige la unidad
        self.f_dP.e.setEnabled(not serie and inc != 'dP')
        self.f_d.e.setEnabled(inc != 'd')
        self.l_Qin.setVisible(inc != 'Q'); self.f_Qin.set_visible(inc != 'Q')
        for w in (self.l_resultado, self.l_caudal, self.l_Q):
            w.setVisible(not serie)
        self.c_Qu.setVisible(not serie and inc == 'Q')
        self.c_dPu.setVisible(inc == 'dP'); self.c_du.setVisible(inc == 'd')
        self.l_beta_t.setVisible(inc == 'd'); self.l_beta.setVisible(inc == 'd')
        self.l_caudal.setText(_i18n.t({'Q': "Caudal:", 'dP': "Presión diferencial:",
                                       'd': "Diámetro del orificio:"}[inc]))
        if serie:
            self.lbl_aviso.setVisible(False)
        self.b_ok.setText(_i18n.t("Abrir serie" if serie else "Calcular"))
        if self.serie is not None:
            self.serie.actualizar_encabezados()
        self.l_eos.setVisible(self.c_z.currentIndex() == 1)
        self.c_eos.setVisible(self.c_z.currentIndex() == 1)
        man = self.c_z.currentIndex() == 2
        for w in (self.l_Zf, self.e_Zf, self.l_Zb, self.e_Zb, self.l_G, self.e_G):
            w.setVisible(man)
        gauge = self.f_P.nombre().endswith('g')
        self.l_Patm.setVisible(gauge); self.f_Patm.set_visible(gauge)
        self._ajustar()

    def _ajustar(self):
        self.layout().invalidate(); self.layout().activate()
        if self.on_tamano is not None:
            # después de que Qt aplique la visibilidad de las filas
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: (self.layout().activate(),
                                          self.on_tamano(self.sizeHint())))

    # ── cromatografía (componentes activos de ThermoPhase) ─────────────
    def _construir_tabla(self, activos):
        from eos import NOMBRES, componente_etiqueta
        NC = self.NC
        z_prev = self._crudo() if self.tc is not None else None
        if self.tc is not None:
            self.cont_tc.removeWidget(self.tc); self.tc.deleteLater()
        self.act = [i for i in sorted(set(activos)) if i <= NC]
        tc = self.tc = po._tabla(len(self.act) + 2, 2)
        tc.setColumnWidth(0, 250); tc.setColumnWidth(1, 110)
        tc.setItem(0, 0, po._cell(_i18n.t("Componente"), bg=po.GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        tc.setItem(0, 1, po._cell(_i18n.t("Composición"), bg=po.GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        for r, i in enumerate(self.act, 1):
            nom = NOMBRES[i] if i < NC else componente_etiqueta(NC)
            tc.setItem(r, 0, po._cell(_i18n.t(nom), bg=po.GRAY_LBL))
            tc.setItem(r, 1, po._cell("", editable=True))
        self.rs = len(self.act) + 1
        tc.setItem(self.rs, 0, po._cell(_i18n.t("Sumatorias:"), bg=po.GRAY_LBL))
        tc.setItem(self.rs, 1, po._cell("", bg=po.GRAY_EMPTY, color=po.TEXT_RES))
        for r in range(self.rs + 1):
            tc.setRowHeight(r, po.ROW_H)
        po._ajustar(tc)
        self.cont_tc.addWidget(tc, 0, Qt.AlignmentFlag.AlignLeft)
        try:
            self.h['registrar'](tc)
        except Exception:
            pass
        tc.itemChanged.connect(self._on_cambio)
        if z_prev:
            self._set_z(z_prev)

    def actualizar(self, fuentes, activos):
        """Al reabrir: lista de fuentes y componentes activos al día."""
        act = self.cmb_fuente.currentData()
        self.cmb_fuente.blockSignals(True); self.cmb_fuente.clear()
        self.cmb_fuente.addItem("", None)
        for k, nom in fuentes:
            self.cmb_fuente.addItem(nom, k)
        self.cmb_fuente.setCurrentIndex(max(0, self.cmb_fuente.findData(act)))
        self.cmb_fuente.blockSignals(False)
        nuevos = [i for i in sorted(set(activos)) if i <= self.NC]
        if nuevos != self.act:
            self._construir_tabla(activos)
            self._ajustar()

    def _crudo(self):
        z = [0.0]*(self.NC + 1)
        for r, i in enumerate(self.act, 1):
            z[i] = po._get_comp(self.tc.item(r, 1))
        return z

    def _upd_suma(self):
        self.tc.blockSignals(True)
        self.tc.item(self.rs, 1).setText(f"{sum(self._crudo()):.4f}")
        self.tc.blockSignals(False)

    def _on_cambio(self, it):
        if it.column() != 1 or it.row() in (0, self.rs):
            return
        v = po._a_float(it.text())
        self.tc.blockSignals(True)
        if v is not None and it.data(po._UR_TXT) != it.text():
            po._set_comp(it, v)
        self.tc.blockSignals(False)
        self._upd_suma()

    def _set_z(self, z):
        self.tc.blockSignals(True)
        for r, i in enumerate(self.act, 1):
            v = z[i] if i < len(z) else 0.0
            it = self.tc.item(r, 1)
            if v:
                po._set_comp(it, v)
            else:
                it.setText(""); it.setData(po._UR_VAL, None)
        self.tc.blockSignals(False)
        self._upd_suma()

    def _normalizar(self):
        z = self._crudo(); s = sum(z)
        if s <= 0:
            return
        base = 100.0 if abs(s - 100.0) < abs(s - 1.0) else 1.0
        self._set_z([v/s*base for v in z])

    def _cargar_fuente(self, clave):
        if clave is None:
            return
        d = self.datos_fuente(clave)
        if d is None:
            return
        self._set_z(list(d[1]))

    # ── cálculo ─────────────────────────────────────────────────────────
    def _leer(self, serie=False):
        def req(campo, msg, pos=True):
            if serie and campo in (self.f_P, self.f_dP, self.f_T):
                return {self.f_P: 1.0e5, self.f_dP: 1.0e3, self.f_T: 288.15}[campo]
            v = campo.si()
            if v is None or (pos and v <= 0):
                raise ValueError(msg)
            return v
        zc = self._crudo(); s = sum(zc)
        man = self.c_z.currentIndex() == 2
        if not man:
            if s <= 1e-12 or sum(zc[:self.NC]) <= 1e-12:
                raise ValueError("Ingrese la cromatografía de la corriente.")
            if abs(s - 1.0) > 1e-3 and abs(s - 100.0) > 1e-1:
                raise ValueError("La composicion debe sumar 1 (fraccion molar) o 100 (porcentaje molar)")
            x = a8.desde_thermophase([v/s for v in zc])
        else:
            x = [0.0]*22
        D = req(self.f_D, "Ingrese el diámetro del tubo.")
        inc = 'Q' if serie else self.incognita()
        d = req(self.f_d, "Ingrese el diámetro del orificio.") if inc != 'd' else None
        if d is not None and d >= D:
            raise ValueError("El diámetro del orificio debe ser menor que el del tubo.")
        P = req(self.f_P, "Ingrese la presión estática.", pos=False)
        if self.f_P.nombre().endswith('g') and not serie:
            P += req(self.f_Patm, "Ingrese la presión atmosférica.", pos=False)
        if P <= 0:
            raise ValueError("La presión absoluta debe ser mayor que cero.")
        dP = req(self.f_dP, "Ingrese la presión diferencial.") if inc != 'dP' else None
        T = req(self.f_T, "Ingrese la temperatura de flujo.")
        Pb = req(self.f_Pb, "Ingrese las condiciones base.")
        Tb = req(self.f_Tb, "Ingrese las condiciones base.")
        Trd = req(self.f_Trd, "Ingrese la temperatura del orificio.")
        TrD = req(self.f_TrD, "Ingrese la temperatura del tubo.")
        mats = [k for k, _n, _a in ag.MATERIALES]
        # Valores fijos admitidos por AGA 3 para gas natural
        k = ag.K_DEFECTO                 # exponente isentrópico 1.3
        mu = ag.MU_DEFECTO*1e3           # viscosidad 0.010268 cP
        spec = dict(op='orificio', x=x, calcular=inc, d_ref=d, D_ref=D,
                    alfa_d=ag.ALFA_F[mats[self.c_mat_d.currentIndex()]]*1.8,
                    alfa_D=ag.ALFA_F[mats[self.c_mat_D.currentIndex()]]*1.8,
                    T_ref_d=Trd, T_ref_D=TrD, T_f=T, P_f=P,
                    toma='arriba' if self.c_toma.currentIndex() == 0 else 'abajo', dP=dP,
                    Pb=Pb, Tb=Tb, z_metodo=('AGA8', 'EOS', 'MANUAL')[self.c_z.currentIndex()],
                    y_metodo=Y_METODOS[self.c_y.currentIndex()][0],
                    k_metodo='FIJO', k_val=k, mu_val=mu*1e-3)
        if spec['z_metodo'] == 'EOS':
            eos_c = self.h['eos_code'](self.c_eos.currentIndex())
            spec['eos'] = eos_c; spec['kij'] = self.h['kij_base'](eos_c)
            if spec['x'][18] > 1e-12:
                raise ValueError("La opción ecuación de estado no admite agua en la cromatografía; "
                                 "use AGA 8.")
        if inc != 'Q':
            v = req(self.f_Qin, "Ingrese el caudal especificado.")
            spec['flujo_obj'] = (v, U_QIN[self.f_Qin.c.currentIndex()][2])
        if man:
            for key, e, msg in (('Zf_man', self.e_Zf, "Ingrese el factor Z en condiciones de flujo."),
                                ('Zb_man', self.e_Zb, "Ingrese el factor Z en condiciones base."),
                                ('G_man', self.e_G, "Ingrese la gravedad específica ideal.")):
                v = _f(e.text())
                if not v or v <= 0:
                    raise ValueError(msg)
                spec[key] = v
        return spec

    def calcular(self):
        if self.es_serie():
            import pestana_orificio_serie as _ser
            if self.serie is None:
                self.serie = _ser.VentanaSerie(self)
            self.serie.actualizar_encabezados()
            self.serie.show(); self.serie.raise_(); self.serie.activateWindow()
            return
        try:
            spec = self._leer()
        except ValueError as ex:
            dialogos.advertencia(self, _i18n.t(str(ex)))
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            res = ag.calcular(spec)
        except ValueError as ex:
            QApplication.restoreOverrideCursor()
            dialogos.advertencia(self, _i18n.t(str(ex)))
            return
        except Exception as ex:
            QApplication.restoreOverrideCursor()
            dialogos.error(self, str(ex))
            return
        QApplication.restoreOverrideCursor()
        if res.get('aga3') is None:
            dialogos.advertencia(self, _i18n.t(res.get('error_aga3') or "Sin solución"))
            return
        self.res = res
        self._mostrar()

    def _mostrar(self):
        if self.res is None:
            return
        q = self.res['aga3']
        inc = self.res.get('calcular', 'Q')
        if inc == 'dP':
            v = U_DP[self.c_dPu.currentIndex()][2](q['dP'])
        elif inc == 'd':
            v = U_L[self.c_du.currentIndex()][2](q['d_ref'])
            self.l_beta.setText(f"{q['beta']:.5f}")
        else:
            v = U_Q[self.c_Qu.currentIndex()][1](q['qm'], q['Qb'])
        self.l_Q.setText(_num(v, 8))
        av = [_i18n.t("Advertencia:") + " " + _i18n.t(a) for a in self.res.get('avisos') or []]
        self.lbl_aviso.setText("\n".join(av)); self.lbl_aviso.setVisible(bool(av))
        self.lbl_aviso.setFixedWidth(self.tc.width())
        self._ajustar()

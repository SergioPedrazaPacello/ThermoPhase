"""
pestana_orificio.py — Medidor de orificio (AGA 3) dentro de Operaciones
unitarias.

DialogoOrificio: ventana de ingreso de datos del módulo (menú Cálculos ›
Medidor de orificio): PanelOrificio (medidor, condiciones de flujo y modelo)
a la izquierda y la cromatografía a la derecha.

TabOrificio: ventana de resultados con el cálculo AGA 3 completo y el
simplificado (Cd = 0.6, sin Y ni corrección térmica) lado a lado.
"""
from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QComboBox, QFileDialog, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEventLoop

import idioma as _i18n
import unidades as _u
import dialogos
import aga3 as ag
import pestana_op_unitarias as po

M_FT3 = 0.028316846592
LB_KG = 0.45359237

# Unidades de presión diferencial → Pa
DP_UNID = [("inH₂O (60 °F)", ag.INH2O_PA), ("psi", ag.PSI_PA), ("kPa", 1000.0),
           ("mbar", 100.0), ("mmH₂O", 9.80665)]
# Unidades de caudal → (factor a SI, tipo): std m³/s a condiciones base, kg/s
Q_UNID = [("MMscfd", 1e6*M_FT3/86400.0, 'std'), ("Mscfd", 1e3*M_FT3/86400.0, 'std'),
          ("scf/h", M_FT3/3600.0, 'std'), ("Sm³/d", 1.0/86400.0, 'std'),
          ("Sm³/h", 1.0/3600.0, 'std'), ("lb/h", LB_KG/3600.0, 'mas'),
          ("kg/h", 1.0/3600.0, 'mas')]
INCOGNITAS = [('Q', "Caudal"), ('dP', "Presión diferencial"), ('d', "Diámetro del orificio")]
Z_METODOS = [('AGA8', "AGA 8 (Detail)"), ('EOS', "Ecuación de estado"), ('MANUAL', "Manual")]
Y_METODOS = [('1992', "AGA 3 (1992)"), ('ISO', "ISO 5167-2 (2003)")]


def _field():
    return _u.sistema() == 'FIELD'


def u_len():
    return 'in' if _field() else 'mm'


def len_a_m(v):
    return v*0.0254 if _field() else v/1000.0


def len_desde_m(m):
    return m/0.0254 if _field() else m*1000.0


def p_a_pa(v):
    return _u.p_a_psia(v)*ag.PSI_PA


def p_desde_pa(p):
    return _u.p_desde_psia(p/ag.PSI_PA)


def t_a_k(v):
    return _u.t_a_R(v)/1.8


def t_desde_k(k):
    return _u.t_desde_R(k*1.8)


def u_alfa():
    return '10⁻⁶/°F' if _field() else '10⁻⁶/°C'


def alfa_desde_F(a):
    """Coeficiente de dilatación (1/°F) → valor mostrado (×10⁶)."""
    return a*1e6 if _field() else a*1.8e6


def alfa_a_K(v):
    """Valor mostrado (×10⁶ por °F o °C) → 1/K."""
    return v*1e-6*1.8 if _field() else v*1e-6


def _f(t):
    return po._a_float(t)


# ════════════════════════════════════════════════════════════════════════
# Panel de datos (ventana de ingreso)
# ════════════════════════════════════════════════════════════════════════
class PanelOrificio(QWidget):
    def __init__(self, dlg, h):
        super().__init__()
        self.dlg = dlg; self.h = h
        self.setStyleSheet('background:transparent;')
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(4)
        W = po.W_CAMPO

        def combo(items, w=W):
            c = QComboBox(); c.setFixedSize(w, 22); h['estilo_combo'](c)
            for it in items:
                if isinstance(it, tuple):
                    c.addItem(_i18n.t(it[1]), it[0])
                else:
                    c.addItem(_i18n.t(it))
            return c

        def par(campo, cmb):
            f = QHBoxLayout(); f.setSpacing(4); f.addWidget(campo); f.addWidget(cmb)
            return f

        # ── Medidor ─────────────────────────────────────────────────────
        v.addWidget(dlg._lbl_txt("Medidor:"))
        g = QGridLayout(); g.setSpacing(4); r = 0
        self.c_inc = combo(INCOGNITAS)
        g.addWidget(dlg._etq("Calcular:"), r, 0); g.addWidget(self.c_inc, r, 1); r += 1
        self.l_d = dlg._etq(""); self.e_d = dlg._campo()
        g.addWidget(self.l_d, r, 0); g.addWidget(self.e_d, r, 1); r += 1
        mats = [(k, n) for k, n, _a in ag.MATERIALES]
        self.c_mat_d = combo(mats)
        g.addWidget(dlg._etq("Material de la placa:"), r, 0); g.addWidget(self.c_mat_d, r, 1); r += 1
        self.l_D = dlg._etq(""); self.e_D = dlg._campo()
        g.addWidget(self.l_D, r, 0); g.addWidget(self.e_D, r, 1); r += 1
        self.c_mat_D = combo(mats); self.c_mat_D.setCurrentIndex(len(mats) - 1)
        g.addWidget(dlg._etq("Material del tubo:"), r, 0); g.addWidget(self.c_mat_D, r, 1); r += 1
        self.l_Tr = dlg._etq(""); self.e_Tr = dlg._campo()
        g.addWidget(self.l_Tr, r, 0); g.addWidget(self.e_Tr, r, 1); r += 1
        self.l_tomas = dlg._etq("Tomas de presión:")
        lt = QLabel(_i18n.t("Bridadas")); lt.setStyleSheet(po.TXT_QSS)
        g.addWidget(self.l_tomas, r, 0); g.addWidget(lt, r, 1); r += 1
        v.addLayout(g)

        # ── Condiciones de flujo ────────────────────────────────────────
        v.addSpacing(4)
        v.addWidget(dlg._lbl_txt("Condiciones de flujo:"))
        g = QGridLayout(); g.setSpacing(4); r = 0
        self.l_P = dlg._etq(""); self.e_P = dlg._campo(W - 112)
        self.c_Ptipo = combo(["Absoluta", "Manométrica"], 108)
        g.addWidget(self.l_P, r, 0); g.addLayout(par(self.e_P, self.c_Ptipo), r, 1); r += 1
        self.l_Patm = dlg._etq(""); self.e_Patm = dlg._campo()
        g.addWidget(self.l_Patm, r, 0); g.addWidget(self.e_Patm, r, 1); r += 1
        self.c_toma = combo([('arriba', "Aguas arriba"), ('abajo', "Aguas abajo")])
        g.addWidget(dlg._etq("Toma de presión estática:"), r, 0); g.addWidget(self.c_toma, r, 1); r += 1
        self.l_dP = dlg._etq("Presión diferencial:"); self.e_dP = dlg._campo(W - 112)
        self.c_dPu = combo([n for n, _f in DP_UNID], 108)
        g.addWidget(self.l_dP, r, 0); g.addLayout(par(self.e_dP, self.c_dPu), r, 1); r += 1
        self.l_T = dlg._etq(""); self.e_T = dlg._campo()
        g.addWidget(self.l_T, r, 0); g.addWidget(self.e_T, r, 1); r += 1
        self.l_Q = dlg._etq("Caudal:"); self.e_Q = dlg._campo(W - 112)
        self.c_Qu = combo([n for n, _f, _t in Q_UNID], 108)
        g.addWidget(self.l_Q, r, 0); g.addLayout(par(self.e_Q, self.c_Qu), r, 1); r += 1
        v.addLayout(g)

        # ── Modelo ──────────────────────────────────────────────────────
        v.addSpacing(4)
        v.addWidget(dlg._lbl_txt("Modelo:"))
        g = QGridLayout(); g.setSpacing(4); r = 0
        self.c_z = combo(Z_METODOS)
        g.addWidget(dlg._etq("Factor de compresibilidad:"), r, 0); g.addWidget(self.c_z, r, 1); r += 1
        self.c_eos = combo(h['eos_items'])
        g.addWidget(dlg._etq("Ecuación de estado:"), r, 0); g.addWidget(self.c_eos, r, 1); r += 1
        self.l_Zf = dlg._etq("Z en condiciones de flujo:"); self.e_Zf = dlg._campo()
        g.addWidget(self.l_Zf, r, 0); g.addWidget(self.e_Zf, r, 1); r += 1
        self.l_Zb = dlg._etq("Z en condiciones base:"); self.e_Zb = dlg._campo()
        g.addWidget(self.l_Zb, r, 0); g.addWidget(self.e_Zb, r, 1); r += 1
        self.c_y = combo(Y_METODOS)
        g.addWidget(dlg._etq("Factor de expansión:"), r, 0); g.addWidget(self.c_y, r, 1); r += 1
        self.e_k = dlg._campo(W - 112); self.c_k = combo(["Fijo", "AGA 8"], 108)
        g.addWidget(dlg._etq("Exponente isentrópico:"), r, 0); g.addLayout(par(self.e_k, self.c_k), r, 1); r += 1
        self.e_mu = dlg._campo(W - 112); self.c_mu = combo(["Fijo", "LBC"], 108)
        g.addWidget(dlg._etq("Viscosidad (cP):"), r, 0); g.addLayout(par(self.e_mu, self.c_mu), r, 1); r += 1
        self.l_Pb = dlg._etq(""); self.e_Pb = dlg._campo()
        g.addWidget(self.l_Pb, r, 0); g.addWidget(self.e_Pb, r, 1); r += 1
        self.l_Tb = dlg._etq(""); self.e_Tb = dlg._campo()
        g.addWidget(self.l_Tb, r, 0); g.addWidget(self.e_Tb, r, 1); r += 1
        v.addLayout(g)

        for c in (self.c_inc, self.c_Ptipo, self.c_z, self.c_k, self.c_mu):
            c.currentIndexChanged.connect(lambda _i: self._visibles())
        self._etiquetas()
        self._defectos()

    # ── etiquetas y visibilidad ─────────────────────────────────────────
    def _etiquetas(self):
        uP = _u.u('P'); uT = _u.u('T'); uL = u_len()
        self.l_d.setText(f"{_i18n.t('Diámetro del orificio')} ({uL}):")
        self.l_D.setText(f"{_i18n.t('Diámetro interno del tubo')} ({uL}):")
        self.l_Tr.setText(f"{_i18n.t('Temperatura de referencia')} ({uT}):")
        self.l_P.setText(f"{_i18n.t('Presión estática')} ({uP}):")
        self.l_Patm.setText(f"{_i18n.t('Presión atmosférica')} ({uP}):")
        self.l_T.setText(f"{_i18n.t('Temperatura de flujo')} ({uT}):")
        self.l_Pb.setText(f"{_i18n.t('Presión base')} ({uP}):")
        self.l_Tb.setText(f"{_i18n.t('Temperatura base')} ({uT}):")

    def _defectos(self):
        F = _field()
        self.e_d.setText("")
        self.e_D.setText("")
        self.e_Tr.setText(f"{t_desde_k((68 + 459.67)/1.8):.2f}")
        self.e_Patm.setText(f"{_u.p_desde_psia(14.696):.3f}")
        self.e_k.setText("1.3")
        self.e_mu.setText("0.010268")
        self.e_Zf.setText("1.0"); self.e_Zb.setText("1.0")
        if F:
            self.e_Pb.setText(f"{_u.p_desde_psia(14.696):.3f}"); self.e_Tb.setText("60.00")
            self.c_Qu.setCurrentIndex(0)
        else:
            self.e_Pb.setText(f"{_u.p_desde_psia(101.325/6.894757293168):.3f}")
            self.e_Tb.setText("15.00")
            self.c_Qu.setCurrentIndex(3); self.c_dPu.setCurrentIndex(2)
        self._visibles()

    def incognita(self):
        return self.c_inc.currentData() or 'Q'

    def _visibles(self):
        inc = self.incognita()
        self.e_d.setEnabled(inc != 'd')
        self.e_dP.setEnabled(inc != 'dP')
        q = inc != 'Q'
        self.l_Q.setVisible(q); self.e_Q.setVisible(q); self.c_Qu.setVisible(q)
        man = self.c_Ptipo.currentIndex() == 1
        self.l_Patm.setVisible(man); self.e_Patm.setVisible(man)
        zm = self.c_z.currentData() == 'MANUAL'
        for w in (self.l_Zf, self.e_Zf, self.l_Zb, self.e_Zb):
            w.setVisible(zm)
        self.e_k.setEnabled(self.c_k.currentIndex() == 0)
        self.e_mu.setEnabled(self.c_mu.currentIndex() == 0)
        if hasattr(self.dlg, '_on_spec'):
            self.dlg._on_spec()            # reajusta el alto de la ventana

    # ── estado (para reabrir la ventana con los últimos datos) ──────────
    _CAMPOS = ('e_d', 'e_D', 'e_Tr', 'e_P', 'e_Patm', 'e_dP', 'e_T', 'e_Q',
               'e_Zf', 'e_Zb', 'e_k', 'e_mu', 'e_Pb', 'e_Tb')
    _COMBOS = ('c_inc', 'c_mat_d', 'c_mat_D', 'c_Ptipo', 'c_toma', 'c_dPu', 'c_Qu',
               'c_z', 'c_eos', 'c_y', 'c_k', 'c_mu')

    def estado(self):
        d = {k: getattr(self, k).text() for k in self._CAMPOS}
        d.update({k: getattr(self, k).currentIndex() for k in self._COMBOS})
        d['sistema'] = _u.sistema()
        return d

    def aplicar(self, d):
        if not d or d.get('sistema') != _u.sistema():
            return                      # unidades distintas: valores por defecto
        for k in self._COMBOS:
            if k in d:
                c = getattr(self, k)
                c.blockSignals(True); c.setCurrentIndex(d[k]); c.blockSignals(False)
        for k in self._CAMPOS:
            if k in d:
                getattr(self, k).setText(d[k])
        self._visibles()

    def set_eos(self, eos_c):
        self.c_eos.setCurrentIndex(self.h['eos_idx'](eos_c))

    # ── lectura ─────────────────────────────────────────────────────────
    def leer(self, z, kij_fuente):
        """Especificación SI del motor AGA 3; lanza ValueError con el
        mensaje para el usuario si falta un dato."""
        def num(e, msg, pos=True):
            v = _f(e.text())
            if v is None or (pos and v <= 0):
                raise ValueError(msg)
            return v
        inc = self.incognita()
        D = len_a_m(num(self.e_D, "Ingrese el diámetro interno del tubo."))
        d = len_a_m(num(self.e_d, "Ingrese el diámetro del orificio.")) if inc != 'd' else None
        if d is not None and d >= D:
            raise ValueError("El diámetro del orificio debe ser menor que el del tubo.")
        Tr = t_a_k(num(self.e_Tr, "Ingrese la temperatura de referencia.", pos=False))
        Pv = num(self.e_P, "Ingrese la presión estática.", pos=False)
        P = p_a_pa(Pv)
        if self.c_Ptipo.currentIndex() == 1:
            P += p_a_pa(num(self.e_Patm, "Ingrese la presión atmosférica."))
        if P <= 0:
            raise ValueError("La presión absoluta debe ser mayor que cero.")
        dP = None
        if inc != 'dP':
            dP = num(self.e_dP, "Ingrese la presión diferencial.")*DP_UNID[self.c_dPu.currentIndex()][1]
        T = t_a_k(num(self.e_T, "Ingrese la temperatura de flujo.", pos=False))
        if T <= 0:
            raise ValueError("La presión y la temperatura absoluta deben ser mayores que cero.")
        Pb = p_a_pa(num(self.e_Pb, "Ingrese las condiciones base."))
        Tb = t_a_k(num(self.e_Tb, "Ingrese las condiciones base.", pos=False))
        eos_c = self.h['eos_code'](self.c_eos.currentIndex())
        kf = kij_fuente
        kij = kf[1] if (kf and kf[0] == eos_c) else self.h['kij_base'](eos_c)
        spec = dict(op='orificio', z=list(z), calcular=inc, d_ref=d, D_ref=D,
                    alfa_d=ag.ALFA_F[self.c_mat_d.currentData()]*1.8,
                    alfa_D=ag.ALFA_F[self.c_mat_D.currentData()]*1.8,
                    T_ref=Tr, T_f=T, P_f=P, toma=self.c_toma.currentData(), dP=dP,
                    Pb=Pb, Tb=Tb, z_metodo=self.c_z.currentData(), eos=eos_c, kij=kij,
                    y_metodo=self.c_y.currentData(),
                    k_metodo='AGA8' if self.c_k.currentIndex() == 1 else 'FIJO',
                    mu_metodo='EOS' if self.c_mu.currentIndex() == 1 else 'FIJO')
        if spec['k_metodo'] == 'FIJO':
            spec['k_val'] = num(self.e_k, "Ingrese el exponente isentrópico.")
        if spec['mu_metodo'] == 'FIJO':
            spec['mu_val'] = num(self.e_mu, "Ingrese la viscosidad.")*1e-3
        if spec['z_metodo'] == 'MANUAL':
            spec['Zf_man'] = num(self.e_Zf, "Ingrese el factor Z en condiciones de flujo.")
            spec['Zb_man'] = num(self.e_Zb, "Ingrese el factor Z en condiciones base.")
        if inc != 'Q':
            nom, fac, tipo = Q_UNID[self.c_Qu.currentIndex()]
            spec['flujo_obj'] = (num(self.e_Q, "Ingrese el caudal.")*fac, tipo)
        return spec

    def info_entrada(self):
        """Datos para la ventana de resultados (unidades elegidas)."""
        return dict(dP_u=self.c_dPu.currentIndex(), Q_u=self.c_Qu.currentIndex(),
                    eos_nombre=self.c_eos.currentText(),
                    toma=self.c_toma.currentText(), mat_d=self.c_mat_d.currentText(),
                    mat_D=self.c_mat_D.currentText())


# ════════════════════════════════════════════════════════════════════════
# Ventana de ingreso de datos
# ════════════════════════════════════════════════════════════════════════
class _Worker(QThread):
    done = pyqtSignal(dict)
    aviso = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, spec):
        super().__init__()
        self.spec = spec

    def run(self):
        try:
            self.done.emit(ag.calcular(self.spec))
        except ValueError as ex:
            self.aviso.emit(str(ex))
        except Exception as ex:
            self.error.emit(str(ex))


class DialogoOrificio(QDialog):
    """fuentes: [(clave, nombre)]; datos_fuente(clave) → (nombre, z, kij, eos,
    metodo); activos: índices de componentes activos (agua = NC); previo:
    datos del último cálculo; h: helpers de la ventana principal."""

    def __init__(self, parent, fuentes, datos_fuente, activos, previo, h):
        super().__init__(parent)
        from eos import NC, NOMBRES, componente_etiqueta
        self.NC = NC
        self.fuentes = fuentes; self.datos_fuente = datos_fuente; self.h = h
        self.act = [i for i in sorted(set(activos)) if i <= NC]
        self.resultado = None; self.entrada = None; self._kij_fuente = None
        self._tam_fijo = None
        self.setWindowTitle(_i18n.t("Medidor de orificio (AGA 3)"))
        self.setStyleSheet('QDialog { background:#e0e0e0; }')
        root = QVBoxLayout(self); root.setContentsMargins(14, 12, 14, 12); root.setSpacing(8)
        root.addWidget(po._titulo(_i18n.t("ThermoPhase — Ingreso de datos")))
        cols = QHBoxLayout(); cols.setSpacing(16)

        c1 = QVBoxLayout(); c1.setSpacing(4)
        self.panel = PanelOrificio(self, h)
        c1.addWidget(self.panel); c1.addStretch(1)
        cols.addLayout(c1)

        c2 = QVBoxLayout(); c2.setSpacing(4)
        fc = QHBoxLayout(); fc.setSpacing(6)
        fc.addWidget(self._lbl_txt("Cromatografía:")); fc.addStretch()
        fc.addWidget(self._lbl_txt("Cargar de:"))
        self.cmb_fuente = QComboBox(); self.cmb_fuente.setFixedSize(170, 22)
        h['estilo_combo'](self.cmb_fuente)
        self.cmb_fuente.addItem("", None)
        for k, nom in fuentes:
            self.cmb_fuente.addItem(nom, k)
        fc.addWidget(self.cmb_fuente)
        c2.addLayout(fc)
        tc = self.tc = po._tabla(len(self.act) + 2, 2)
        tc.setColumnWidth(0, 210); tc.setColumnWidth(1, 110)
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
        c2.addWidget(tc, 0, Qt.AlignmentFlag.AlignRight)
        c2.addStretch(1)
        cols.addLayout(c2)
        root.addLayout(cols)
        try:
            h['registrar'](tc)
        except Exception:
            pass
        tc.itemChanged.connect(self._on_cambio)

        fila = QHBoxLayout(); fila.setSpacing(8)
        self.b_norm = QPushButton(_i18n.t("Normalizar"))
        self.b_ok = QPushButton(_i18n.t("Calcular")); self.b_can = QPushButton(_i18n.t("Cancelar"))
        for b in (self.b_norm, self.b_ok, self.b_can):
            b.setFixedHeight(26); b.setMinimumWidth(84); b.setStyleSheet(po.BTN_QSS)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        fila.addWidget(self.b_norm); fila.addStretch(); fila.addWidget(self.b_ok); fila.addWidget(self.b_can)
        root.addLayout(fila)
        self.b_norm.clicked.connect(self._normalizar)
        self.b_can.clicked.connect(self.reject)
        self.b_ok.clicked.connect(self._calcular)
        self.cmb_fuente.activated.connect(lambda _i: self._cargar_fuente(self.cmb_fuente.currentData()))

        self._aplicar_previo(previo)
        self.adjustSize(); self.setFixedSize(self.sizeHint())
        self._tam_fijo = self.size()

    # ── helpers usados por PanelOrificio ────────────────────────────────
    def _lbl_txt(self, t):
        l = QLabel(_i18n.t(t)); l.setStyleSheet(po.TXT_QSS); return l

    def _etq(self, t):
        l = QLabel(_i18n.t(t) if t else ""); l.setStyleSheet(po.LBL_QSS); l.setFixedHeight(22)
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        l.setMinimumWidth(170)
        return l

    def _campo(self, w=None):
        w = po.W_CAMPO if w is None else w
        e = QLineEdit(); e.setStyleSheet(po.ED_QSS); e.setFixedSize(w, 22)
        e.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return e

    def _on_spec(self):
        """Ajusta el alto de la ventana a las filas visibles (ancho fijo)."""
        if self._tam_fijo is None:
            return
        lay = self.layout(); lay.invalidate(); lay.activate()
        self.setFixedSize(self._tam_fijo.width(),
                          max(lay.sizeHint().height(), lay.totalMinimumSize().height()))

    # ── composición ─────────────────────────────────────────────────────
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
        _nombre, z, kij, eos_c, _met = d
        self._set_z(z)
        self.panel.set_eos(eos_c)
        self._kij_fuente = (eos_c, kij)

    def _aplicar_previo(self, p):
        if not p:
            if self.fuentes:
                self.cmb_fuente.setCurrentIndex(1)
                self._cargar_fuente(self.fuentes[0][0])
            return
        self._kij_fuente = p.get('kij_fuente')
        self._set_z(p.get('z_crudo') or [])
        self.panel.aplicar(p.get('panel'))

    # ── cálculo ─────────────────────────────────────────────────────────
    def _leer(self):
        adv = lambda m: (dialogos.advertencia(self, _i18n.t(m)), None)[1]
        zc = self._crudo(); s = sum(zc)
        if s <= 1e-12 or sum(zc[:self.NC]) <= 1e-12:
            return adv("Ingrese la cromatografía de la corriente.")
        if abs(s - 1.0) > 1e-3 and abs(s - 100.0) > 1e-1:
            return adv("La composicion debe sumar 1 (fraccion molar) o 100 (porcentaje molar)")
        z = [v/s for v in zc]
        try:
            spec = self.panel.leer(z, self._kij_fuente)
        except ValueError as ex:
            return adv(str(ex))
        self.entrada = dict(self.panel.info_entrada(), z_crudo=zc,
                            kij_fuente=self._kij_fuente, panel=self.panel.estado())
        return spec

    def _calcular(self):
        spec = self._leer()
        if spec is None:
            return
        txt = self.b_ok.text()
        for b in (self.b_ok, self.b_can, self.b_norm):
            b.setEnabled(False)
        self.b_ok.setText(_i18n.t("Calculando..."))
        out = {}
        w = _Worker(spec)
        lazo = QEventLoop()
        w.done.connect(lambda r: out.update(r=r))
        w.aviso.connect(lambda m: out.update(aviso=m))
        w.error.connect(lambda m: out.update(error=m))
        w.finished.connect(lazo.quit)
        w.start()
        lazo.exec()
        for b in (self.b_ok, self.b_can, self.b_norm):
            b.setEnabled(True)
        self.b_ok.setText(txt)
        if 'r' in out:
            self.resultado = out['r']
            self.accept()
        elif 'aviso' in out:
            dialogos.advertencia(self, _i18n.t(out['aviso']))
        else:
            dialogos.error(self, _i18n.t(out.get('error', "Error")))

    def reject(self):
        if not self.b_can.isEnabled():
            return
        super().reject()


# ════════════════════════════════════════════════════════════════════════
# Ventana de resultados
# ════════════════════════════════════════════════════════════════════════
class TabOrificio(QWidget):
    def __init__(self, on_nuevo=None):
        super().__init__()
        self.on_nuevo = on_nuevo; self.on_tamano = None
        self.res = None; self.entrada = None
        self.W = 706
        self.setObjectName('oriTab')
        self.setStyleSheet(f'QWidget#oriTab {{ background:{po.GRAY_LBL}; }}')
        root = QVBoxLayout(self); root.setContentsMargins(13, 9, 13, 8); root.setSpacing(6)
        root.addWidget(po._titulo("ThermoPhase — " + _i18n.t("Medidor de orificio (AGA 3)")))
        bar = QHBoxLayout(); bar.setSpacing(6)
        self.lbl_op = po._seccion(""); bar.addWidget(self.lbl_op, 1)
        self.btn_nuevo = QPushButton(_i18n.t("Nuevo cálculo"))
        self.btn_csv = QPushButton(_i18n.t("Exportar CSV"))
        for b in (self.btn_nuevo, self.btn_csv):
            b.setFixedHeight(24); b.setStyleSheet(po.BTN_QSS)
            b.setCursor(Qt.CursorShape.PointingHandCursor); bar.addWidget(b)
        self.btn_nuevo.clicked.connect(lambda: self.on_nuevo and self.on_nuevo())
        self.btn_csv.clicked.connect(self.exportar_csv)
        root.addLayout(bar)
        root.addWidget(po._seccion(_i18n.t("Resultados del medidor")))
        self.tbl = po._tabla(1, 1); root.addWidget(self.tbl)
        root.addSpacing(4)
        root.addWidget(po._seccion(_i18n.t("Propiedades del gas")))
        self.tbl_gas = po._tabla(1, 1); root.addWidget(self.tbl_gas)
        self.lbl_aviso = QLabel(""); self.lbl_aviso.setWordWrap(True)
        self.lbl_aviso.setStyleSheet(f'font-family:"{po.FONT_F}";font-size:{po.FS}pt;'
                                     f'color:{po.AVISO};background:transparent;')
        root.addWidget(self.lbl_aviso)
        root.addStretch(1)

    def set_ancho(self, ancho_ventana):
        m = self.layout().contentsMargins()
        self.W = int(ancho_ventana) - m.left() - m.right() - 2
        if self.res is not None:
            self._render()

    def mostrar(self, res, entrada):
        self.res = res; self.entrada = entrada or {}
        self._render()

    # ── filas ───────────────────────────────────────────────────────────
    def _filas(self):
        r = self.res; e = self.entrada; F = _field()
        dPn, dPf = DP_UNID[e.get('dP_u', 0)]
        Qn, Qf, Qt = Q_UNID[e.get('Q_u', 0)]
        hhv = r.get('hhv_mas')           # BTU/lb

        def q_std(q):
            return q['Qb']/(1e6*M_FT3/86400.0) if F else q['Qb']*86400.0

        def energia(q):
            if not hhv:
                return None
            btu_d = q['qm']/LB_KG*86400.0*hhv
            return btu_d/1e6 if F else btu_d*1.05505585262e-6       # MMBtu/d | GJ/d
        uL = u_len()
        filas = [
            ("Caudal másico", 'lb/h' if F else 'kg/h',
             lambda q: q['qm']*3600.0/(LB_KG if F else 1.0), 2, True),
            ("Caudal a condiciones base", 'MMscfd' if F else 'Sm³/d', q_std, 4 if F else 1, True),
            ("Caudal a condiciones de flujo", 'ft³/h' if F else 'm³/h',
             lambda q: q['Qf']*3600.0/(M_FT3 if F else 1.0), 2, True),
            ("Caudal de energía (PCS)", 'MMBtu/d' if F else 'GJ/d', energia, 3, True),
        ]
        if Qn not in ('MMscfd', 'Sm³/d', 'lb/h', 'kg/h'):
            filas.insert(2, (f"Caudal ({Qn})", "",
                             (lambda q, f_=Qf, t_=Qt: (q['Qb'] if t_ == 'std' else q['qm'])/f_),
                             2, True))
        filas += [
            ("Presión diferencial", dPn, lambda q: q['dP']/dPf, 3, True),
            ("Diámetro del orificio a T de referencia", uL, lambda q: len_desde_m(q['d_ref']), 4, True),
            ("Diámetro del orificio a T de flujo", uL, lambda q: len_desde_m(q['d']), 4, False),
            ("Diámetro del tubo a T de flujo", uL, lambda q: len_desde_m(q['D']), 4, False),
            ("Relación de diámetros β", "", lambda q: q['beta'], 5, False),
            ("Coeficiente de descarga Cd", "", lambda q: q['Cd'], 6, False),
            ("Factor de velocidad de aproximación Ev", "", lambda q: q['Ev'], 6, False),
            ("Factor de expansión Y", "", lambda q: q['Y'], 6, False),
            ("Número de Reynolds del tubo", "", lambda q: q['ReD'], 0, False),
            ("Relación ΔP/P₁", "", lambda q: q['x1'], 5, False),
        ]
        return filas

    def _filas_gas(self):
        r = self.res; F = _field()
        q = r.get('aga3') or r.get('simple')
        uP = _u.u('P'); ud = 'lb/ft³' if F else 'kg/m³'
        dens = lambda v: v/16.018463374 if F else v
        f = [("Presión aguas arriba P₁", uP, p_desde_pa(q['P1']), 3),
             ("Presión aguas abajo P₂", uP, p_desde_pa(q['P2']), 3),
             ("Densidad en condiciones de flujo", ud, dens(q['rho1']), 5),
             ("Factor Z en condiciones de flujo", "", q['Zf'], 6)]
        if q.get('Zf2') is not None:
            f.append(("Factor Z aguas abajo", "", q['Zf2'], 6))
        f += [("Densidad en condiciones base", ud, dens(r['base']['rho']), 6),
              ("Factor Z en condiciones base", "", r['base']['Z'], 6),
              ("Masa molar", "g/mol", r['base']['M'], 4),
              ("Densidad relativa real", "", r['Gr'], 6),
              ("Densidad relativa ideal", "", r['Gi'], 6),
              ("Exponente isentrópico", "", q['kappa'], 4),
              ("Viscosidad", "cP", q['mu']*1e3, 6)]
        if r.get('hhv_mas'):
            f.append(("Poder calorífico superior másico", 'Btu/lb' if F else 'MJ/kg',
                      r['hhv_mas'] if F else r['hhv_mas']*2.326e-3, 2))
        return f

    def _render(self):
        r = self.res
        if r is None:
            return
        cal = dict(INCOGNITAS)[r.get('calcular', 'Q')]
        zt = dict(Z_METODOS)[r.get('z_metodo', 'AGA8')]
        yt = dict(Y_METODOS)[r.get('y_metodo', '1992')]
        self.lbl_op.setText(f"{_i18n.t('Calcular')}: {_i18n.t(cal)} — Z: {_i18n.t(zt)} — "
                            f"Y: {_i18n.t(yt)}")
        filas = self._filas()
        t = self.tbl
        t.clearSpans(); t.clear()
        t.setRowCount(len(filas) + 1); t.setColumnCount(4)
        hdr = ["", _i18n.t("AGA 3"), _i18n.t("Simplificado (Cd = 0.6)"), _i18n.t("Diferencia (%)")]
        for c, h in enumerate(hdr):
            t.setItem(0, c, po._cell(h, bg=po.GRAY_LBL, align=Qt.AlignmentFlag.AlignCenter))
        col0 = 300
        t.setColumnWidth(0, col0)
        resto = self.W - 1 - col0; wc = resto//3
        t.setColumnWidth(1, wc); t.setColumnWidth(2, wc); t.setColumnWidth(3, resto - 2*wc)
        qa, qs = r.get('aga3'), r.get('simple')
        for k, (base, un, fn, dec, dif) in enumerate(filas, 1):
            t.setItem(k, 0, po._cell(f"{_i18n.t(base)}" + (f" [{un}]:" if un else ":"), bg=po.GRAY_LBL))
            va = fn(qa) if qa else None
            vs = fn(qs) if qs else None
            t.setItem(k, 1, po._cell(po._fmt(va, dec), color=po.TEXT_RES))
            t.setItem(k, 2, po._cell(po._fmt(vs, dec), color=po.TEXT_RES))
            dtxt = ""
            if dif and va and vs is not None and abs(vs - va) > 1e-12*abs(va):
                dtxt = po._fmt((vs - va)/va*100.0, 3)
            t.setItem(k, 3, po._cell(dtxt, color=po.TEXT_RES, bg=po.WHITE if dif else po.GRAY_RES))
        for k in range(t.rowCount()):
            t.setRowHeight(k, po.ROW_H)
        po._ajustar(t)

        fg = self._filas_gas()
        t = self.tbl_gas
        nf = (len(fg) + 1)//2
        t.clear(); t.setRowCount(nf); t.setColumnCount(4)
        wv = 110; we = (self.W - 1 - 2*wv)//2
        for c, w_ in enumerate((we, wv, self.W - 1 - 2*wv - we, wv)):
            t.setColumnWidth(c, w_)
        for k in range(nf*2):
            fi, c = k % nf, 2*(k//nf)
            if k < len(fg):
                base, un, v, dec = fg[k]
                t.setItem(fi, c, po._cell(f"{_i18n.t(base)}" + (f" [{un}]:" if un else ":"), bg=po.GRAY_LBL))
                t.setItem(fi, c + 1, po._cell(po._fmt(v, dec), color=po.TEXT_RES))
            else:
                t.setItem(fi, c, po._cell("", bg=po.GRAY_LBL)); t.setItem(fi, c + 1, po._cell("", bg=po.GRAY_RES))
        for fi in range(nf):
            t.setRowHeight(fi, po.ROW_H)
        po._ajustar(t)

        av = [_i18n.t("Advertencia:") + " " + _i18n.t(a) for a in r.get('avisos') or []]
        for m in ('aga3', 'simple'):
            if r.get('error_' + m):
                nom = "AGA 3" if m == 'aga3' else _i18n.t("Simplificado (Cd = 0.6)")
                av.append(f"{nom}: {_i18n.t(r['error_' + m])}")
        self.lbl_aviso.setText("\n".join(av)); self.lbl_aviso.setVisible(bool(av))
        self.layout().activate()
        if self.on_tamano is not None:
            m = self.layout().contentsMargins()
            self.on_tamano(self.W + 2 + m.left() + m.right(), self.sizeHint().height() + 2)

    def exportar_csv(self):
        if self.res is None:
            return
        path, _f = QFileDialog.getSaveFileName(self, _i18n.t("Exportar CSV"),
                                               "medidor_orificio.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.lbl_op.text() + "\n")
                for t in (self.tbl, self.tbl_gas):
                    for r in range(t.rowCount()):
                        fila = [(t.item(r, c).text() if t.item(r, c) else "")
                                for c in range(t.columnCount())]
                        f.write(";".join(fila) + "\n")
                    f.write("\n")
                if self.lbl_aviso.text():
                    f.write(self.lbl_aviso.text() + "\n")
            dialogos.info(self, f"{_i18n.t('CSV guardado:')}\n{path}")
        except Exception as ex:
            dialogos.error(self, str(ex))

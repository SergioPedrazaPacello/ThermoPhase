"""
flash_multiple.py — Flash múltiple: el cálculo de equilibrio de fases repetido
en una lista de puntos (P, T) para un mismo fluido.

Usa el mismo motor que la pestaña de Equilibrio de fases y que el Análisis de
sensibilidad (pestana_propiedades._punto): flash bifásico sin agua o flash
trifásico de Huron-Vidal con agua, con la EOS, los kij y el método de densidad
del fluido.  El resultado es una tabla: N.° de corrida, presión, temperatura y
las propiedades elegidas.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QSizePolicy,
                             QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QBrush, QColor

import idioma as _i18n
import unidades as _u
import dialogos
from pestana_propiedades import _punto, _PROPS_SENS, _PROPS_BY_KEY, _conv_mag

WHITE = "#FFFFFF"; GRAY_TIT = "#A8A8A8"; GRAY_LBL = "#D0D0D0"
BORDER = "#888888"; TEXT = "#000000"; TEXT_RES = "#000080"; SEL_BG = "#DCDCDC"
FONT_F = "Arial Narrow"; FS = 10; ROW_H = 22

# decimales por propiedad (el resto, 4)
_DEC = {'H_stream': 2, 'S_stream': 4, 'fv_bg': 6, 'fv_rs': 2, 'fv_rsw': 2,
        'agua_cont': 3, 'agua_cap': 3, 'mu_l': 5, 'mu_v': 5, 'mu_w': 5,
        'frac_v': 6, 'frac_l': 6, 'frac_w': 6, 'y_w': 6, 'x_w': 6}

# selección inicial
DEFAULT_KEYS = ['frac_v', 'frac_l', 'ZV', 'ZL', 'rho_v', 'rho_l']


# ── Puntos de saturación y de hidrato de cada corrida ───────────────────
# (key, etiqueta, magnitud): 'T' temperatura, 'P' presión, 'dT' diferencia
# de temperatura.  Se calculan con los mismos motores que las ventanas de
# Puntos de saturación y de Formación de hidratos.
EXTRAS = [
    ('sat_T_rocio',   "Temperatura de rocío", 'T'),
    ('sat_T_burbuja', "Temperatura de burbuja", 'T'),
    ('hid_T',         "Temperatura de hidrato", 'T'),
    ('sat_P_rocio',   "Presión de rocío", 'P'),
    ('sat_P_burbuja', "Presión de burbuja", 'P'),
    ('hid_P',         "Presión de hidrato", 'P'),
    ('hid_margen',    "Margen de hidrato", 'dT'),
]
_EXTRA_BY_KEY = {k: (k, b, m) for k, b, m in EXTRAS}
SEPARADOR = '__sep__'
_DEC.update({k: 2 for k in _EXTRA_BY_KEY})


def propiedades_disponibles(agua):
    """[(key, etiqueta con unidad)] del catálogo (con o sin agua), seguido
    del grupo de puntos de saturación e hidratos (precedido de SEPARADOR)."""
    out = []
    for key, base, mag, solo_agua, _f in _PROPS_SENS:
        if solo_agua and not agua:
            continue
        out.append((key, etiqueta(key)))
    out.append((SEPARADOR, _i18n.t("Puntos de saturación e hidratos (a la presión o temperatura de la corrida)")))
    for key, _b, _m in EXTRAS:
        out.append((key, etiqueta(key)))
    return out


def _unidad_extra(mag):
    return _u.u('P') if mag == 'P' else _u.u('T')


def etiqueta(key):
    if key in _EXTRA_BY_KEY:
        _k, base, mag = _EXTRA_BY_KEY[key]
        return f"{_i18n.t(base)} [{_unidad_extra(mag)}]"
    _k, base, mag, _sa, _f = _PROPS_BY_KEY[key]
    unidad = f" [{_u.u(mag)}]" if mag else ""
    return f"{_i18n.t(base)}{unidad}"


def _convertir_extra(key, v):
    """Valor interno (°R, psia o ΔT en °R) → unidades activas."""
    mag = _EXTRA_BY_KEY[key][2]
    if mag == 'P':
        return _u.p_desde_psia(v)
    if mag == 'dT':
        return _u.t_desde_R(v + 459.67) - _u.t_desde_R(459.67)
    return _u.t_desde_R(v)


def _puntos_extra(keys, z, kij, eos_c, P, T_R):
    """Puntos de saturación / hidrato de una corrida (unidades internas).
    None en las celdas cuyo punto no existe o no converge."""
    out = {}
    need = set(keys)
    if not need:
        return out
    zz = [float(v) for v in z]
    agua = len(zz) > 13 and zz[13] > 1e-12
    z13 = zz[:13]; s13 = sum(z13)
    if s13 <= 0:
        return {k: None for k in keys}
    z13 = [v/s13 for v in z13]
    if need & {'sat_T_rocio', 'sat_T_burbuja', 'sat_P_rocio', 'sat_P_burbuja'}:
        import saturacion as _sat
        zs = ([v/sum(zz[:14]) for v in zz[:14]] if agua else z13)
        for key, tipo, val, campo in (('sat_T_rocio', 'T_rocio', P, 'T'),
                                      ('sat_T_burbuja', 'T_burbuja', P, 'T'),
                                      ('sat_P_rocio', 'P_rocio', T_R, 'P'),
                                      ('sat_P_burbuja', 'P_burbuja', T_R, 'P')):
            if key not in need:
                continue
            try:
                r = _sat.punto_saturacion(tipo, val, zs, kij, eos=eos_c)
                v = r.get(campo) if (r and r.get('exito', True) and r.get(campo)) else None
                out[key] = float(v) if v else None
            except Exception:
                out[key] = None
    if need & {'hid_T', 'hid_P', 'hid_margen'}:
        import hidratos as _hid
        z_full = zz[:14] if agua else None
        if need & {'hid_T', 'hid_margen'}:
            try:
                r = _hid.punto_hidrato(z13, 'T', P, kij, eos_c, z_full=z_full)
                Th = float(r['T_R']) if r else None
            except Exception:
                Th = None
            out['hid_T'] = Th
            out['hid_margen'] = (T_R - Th) if Th else None
        if 'hid_P' in need:
            try:
                r = _hid.punto_hidrato(z13, 'P', T_R, kij, eos_c, z_full=z_full)
                out['hid_P'] = float(r['P_psia']) if r else None
            except Exception:
                out['hid_P'] = None
    return {k: out.get(k) for k in keys}


class FlashMultWorker(QThread):
    fila = pyqtSignal(int, dict)         # índice, propiedades crudas (FIELD)
    done = pyqtSignal()
    error = pyqtSignal(int, str)

    def __init__(self, z, kij, eos, metodo, agua, puntos, keys):
        super().__init__()
        self.z = z; self.kij = kij; self.eos = eos; self.metodo = metodo
        self.agua = agua; self.puntos = puntos; self.keys = keys

    def run(self):
        import eos as _eng
        previa = _eng.get_eos()
        cap = 'agua_cap' in self.keys
        fvol = bool({'fv_bo', 'fv_rs', 'fv_bw', 'fv_rsw'} & set(self.keys))
        try:
            _eng.set_eos(self.eos)
            for i, (P, T_R) in enumerate(self.puntos):
                try:
                    vals = {}
                    props = [k for k in self.keys if k not in _EXTRA_BY_KEY]
                    extras = [k for k in self.keys if k in _EXTRA_BY_KEY]
                    r = (_punto(self.z, T_R, P, self.kij, self.eos, self.metodo,
                                self.agua, capacidad=cap, fvol=fvol)
                         if props else None)
                    if extras:
                        vals.update(_puntos_extra(extras, self.z, self.kij,
                                                  self.eos, P, T_R))
                        _eng.set_eos(self.eos)
                    for k in props:
                        try:
                            v = _PROPS_BY_KEY[k][4](r)
                        except Exception:
                            v = None
                        vals[k] = None if v is None else float(v)
                    self.fila.emit(i, vals)
                except Exception as ex:
                    self.error.emit(i, str(ex))
        finally:
            try:
                _eng.set_eos(previa)
            except Exception:
                pass
            self.done.emit()


class TabFlashMultiple(QWidget):
    """Ventana de resultados del flash múltiple."""

    def __init__(self, on_nuevo=None):
        super().__init__()
        self.on_nuevo = on_nuevo
        self.spec = None             # dict(nombre, z, kij, eos, metodo, agua, puntos, keys)
        self.res = {}                # i -> dict de valores crudos (o 'error')
        self.worker = None
        self._build()

    def _build(self):
        self.setObjectName('flashMultTab')
        self.setStyleSheet(f'QWidget#flashMultTab {{ background:{GRAY_LBL}; }}')
        root = QVBoxLayout(self); root.setContentsMargins(8, 10, 8, 8); root.setSpacing(6)
        t = QLabel("ThermoPhase — Flash múltiple")
        t.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        t.setFixedHeight(22)
        t.setStyleSheet(f'background:{GRAY_TIT};color:{TEXT};border:1px solid {BORDER};'
                        f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
        root.addWidget(t)
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet(f'background:{GRAY_LBL};color:{TEXT};border:1px solid {BORDER};'
                                    f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 8px;')
        self.lbl_info.setFixedHeight(22)
        root.addWidget(self.lbl_info)
        self.tbl = QTableWidget(0, 0)
        self.tbl.horizontalHeader().hide(); self.tbl.verticalHeader().hide()
        self.tbl.setShowGrid(True)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tbl.setWordWrap(True)
        self.tbl.setStyleSheet(
            f'QTableWidget {{ background:{WHITE}; border:1px solid {BORDER};'
            f' font-family:"{FONT_F}"; font-size:{FS}pt; gridline-color:{BORDER};'
            f' selection-background-color:{SEL_BG}; selection-color:{TEXT}; }}'
            f'QTableWidget::item {{ padding:2px 6px; }}')
        self.tbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self.tbl, 1)
        self.prog = QProgressBar(); self.prog.setTextVisible(False)
        self.prog.setFixedHeight(16); self.prog.setVisible(False)
        self.prog.setStyleSheet(
            'QProgressBar { border:1px solid #888888; background:#E8E8E8; border-radius:0px; }'
            'QProgressBar::chunk { background:#2d7d2d; }')
        root.addWidget(self.prog)
        fila = QHBoxLayout(); fila.setSpacing(8)
        btn = (f'background:#C8C8C8;border:2px outset {BORDER};'
               f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;padding:1px 12px;')
        self.btn_nuevo = QPushButton("Nuevo cálculo"); self.btn_nuevo.setStyleSheet(btn)
        self.btn_nuevo.clicked.connect(lambda: self.on_nuevo and self.on_nuevo())
        self.btn_csv = QPushButton("Exportar CSV"); self.btn_csv.setStyleSheet(btn)
        self.btn_csv.setEnabled(False); self.btn_csv.clicked.connect(self.exportar_csv)
        fila.addStretch(); fila.addWidget(self.btn_nuevo); fila.addWidget(self.btn_csv)
        root.addLayout(fila)

    # ── cálculo ─────────────────────────────────────────────────────────
    def calcular(self, spec):
        if self.worker is not None and self.worker.isRunning():
            return
        self.spec = spec; self.res = {}
        self._render()
        self.prog.setRange(0, len(spec['puntos'])); self.prog.setValue(0)
        self.prog.setVisible(True)
        self.btn_nuevo.setEnabled(False); self.btn_csv.setEnabled(False)
        self.worker = FlashMultWorker(spec['z'], spec['kij'], spec['eos'], spec['metodo'],
                                      spec['agua'], spec['puntos'], spec['keys'])
        self.worker.fila.connect(self._on_fila)
        self.worker.error.connect(self._on_err)
        self.worker.done.connect(self._on_done)
        self.worker.start()

    def _on_fila(self, i, vals):
        self.res[i] = vals; self._pintar_fila(i); self.prog.setValue(len(self.res))

    def _on_err(self, i, msg):
        self.res[i] = {'_error': msg}; self._pintar_fila(i); self.prog.setValue(len(self.res))

    def _on_done(self):
        self.prog.setVisible(False)
        self.btn_nuevo.setEnabled(True); self.btn_csv.setEnabled(True)
        errs = [i + 1 for i, v in self.res.items() if '_error' in v]
        if errs:
            dialogos.advertencia(self, _i18n.t("No convergió el cálculo en las corridas:")
                                 + " " + ", ".join(map(str, sorted(errs))))

    # ── tabla ───────────────────────────────────────────────────────────
    def _titulos(self):
        return (["N°", f"{_i18n.t('Presion')} ({_u.u('P')})",
                 f"{_i18n.t('Temperatura')} ({_u.u('T')})"]
                + [etiqueta(k) for k in self.spec['keys']])

    def _render(self):
        if not self.spec:
            return
        tit = self._titulos(); n = len(self.spec['puntos'])
        nombre = self.spec['nombre']
        # Solo el nombre de la corriente; el cálculo usa su EOS y su método
        # de densidad.
        self.lbl_info.setText(nombre)
        t = self.tbl
        t.clear(); t.setRowCount(n + 1); t.setColumnCount(len(tit))
        gris = QBrush(QColor(GRAY_LBL))
        for c, txt in enumerate(tit):
            it = QTableWidgetItem(txt); it.setBackground(gris)
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(0, c, it)
        t.setRowHeight(0, 44)
        t.setColumnWidth(0, 40); t.setColumnWidth(1, 90); t.setColumnWidth(2, 100)
        for c in range(3, len(tit)):
            t.setColumnWidth(c, 130)
        for i in range(n):
            t.setRowHeight(i + 1, ROW_H)
            self._pintar_fila(i)

    def _pintar_fila(self, i):
        if not self.spec:
            return
        t = self.tbl; r = i + 1
        P, T_R = self.spec['puntos'][i]
        gris = QBrush(QColor(GRAY_LBL))
        def put(c, txt, bg=None, color=TEXT, al=Qt.AlignmentFlag.AlignRight):
            it = QTableWidgetItem(txt)
            it.setTextAlignment(al | Qt.AlignmentFlag.AlignVCenter)
            if bg is not None: it.setBackground(bg)
            it.setForeground(QBrush(QColor(color)))
            t.setItem(r, c, it)
        put(0, str(i + 1), gris, al=Qt.AlignmentFlag.AlignCenter)
        put(1, f"{_u.p_desde_psia(P):.2f}")
        put(2, f"{_u.t_desde_R(T_R):.2f}")
        vals = self.res.get(i)
        for c, k in enumerate(self.spec['keys'], 3):
            if vals is None:
                put(c, ""); continue
            if '_error' in vals:
                put(c, "—", color='#a00000'); continue
            v = vals.get(k)
            if v is None:
                put(c, ""); continue
            if k in _EXTRA_BY_KEY:
                v = _convertir_extra(k, v)
            else:
                v = _conv_mag(_PROPS_BY_KEY[k][2], v)
            put(c, f"{v:.{_DEC.get(k, 4)}f}", color=TEXT_RES)

    def aplicar_unidades(self, old=None):
        self._render()

    def retraducir_grafico(self):
        self._render()

    def exportar_csv(self):
        if not self.spec:
            return
        path, _ = QFileDialog.getSaveFileName(self, _i18n.t("Guardar CSV"),
                                              "flash_multiple.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8-sig') as f:
                tit = self._titulos()
                f.write(";".join(tit) + "\n")
                for r in range(1, self.tbl.rowCount()):
                    f.write(";".join((self.tbl.item(r, c).text() if self.tbl.item(r, c) else "")
                                     for c in range(len(tit))) + "\n")
        except Exception as ex:
            dialogos.error(self, str(ex))

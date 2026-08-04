"""
Pestaña Puntos de Saturación para ThermoPhase.
Calcula T de rocío, T de burbuja, P de rocío, P de burbuja.
Mismo estilo (Arial Narrow) que el resto del programa.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QGridLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSizePolicy, QAbstractSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from eos import NOMBRES, NC
import dialogos as dialogos
import idioma as _i18n
import eos as _eng
import unidades as _u
WHITE="#FFFFFF"; GRAY_TIT="#A8A8A8"; GRAY_HDR="#C8C8C8"; GRAY_LBL="#D0D0D0"
GRAY_RES="#E8E8E8"; BORDER="#888888"; TEXT="#000000"; TEXT_DIM="#555555"
TEXT_RES="#000080"; FONT_F="Arial Narrow"; FS=10

# ── Estilo retro de las listas desplegables (QComboBox) ───────
# Cambia de modelo comentando el activo y descomentando otro.
# Modelo 1 — Windows 95 clásico  (ACTIVO)
COMBO_STYLE = (
    f'QComboBox {{ background:{WHITE}; border:2px inset {BORDER};'
    f' color:{TEXT}; font-family:"{FONT_F}"; font-size:{FS}pt; padding:1px 4px; }}'
    f'QComboBox:on {{ border:2px inset #555555; }}'
    f'QAbstractItemView {{ background:{WHITE}; border:1px solid #000000;'
    f' color:{TEXT}; selection-background-color:#DCDCDC; selection-color:#000000;'
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

BTN_STYLE=(f'background:{GRAY_LBL};border:2px outset {BORDER};'
           f'font-family:"{FONT_F}";font-size:{FS}pt;min-height:22px;')
LBL_TIT=(f'background:{GRAY_TIT};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_SEC=(f'background:{GRAY_LBL};color:{TEXT};border:1px solid {BORDER};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:0px 6px;')
LBL_RES=(f'background:{GRAY_LBL};border:1px solid {BORDER};color:{TEXT_RES};'
         f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px 6px;')


# ── Worker para cálculo en segundo plano ──────────────────────
class SatWorker(QThread):
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)
    def __init__(self, tipo, valor, z, kij, eos=None):
        super().__init__()
        self.tipo=tipo; self.valor=valor; self.z=z; self.kij=kij; self.eos=eos
    def run(self):
        try:
            import eos as _eng
            if self.eos:
                _eng.set_eos(self.eos)      # los puntos de saturacion obedecen la EOS elegida
            from envolvente import punto_saturacion
            res = punto_saturacion(self.tipo, self.valor, self.z, self.kij)
            self.done.emit(res if res else {})
        except Exception as e:
            self.error.emit(str(e))


class TabSaturacion(QWidget):
    # Mapeo desplegable → (tipo_calc, unidad_entrada, etiqueta_entrada, unidad_result)
    TIPOS = {
        "Temperatura de Rocío":   ('T_rocio',   'P', 'Presion (psi):',      'T'),
        "Temperatura de Burbuja": ('T_burbuja', 'P', 'Presion (psi):',      'T'),
        "Presion de Rocío":       ('P_rocio',   'T', 'Temperatura (°R):',   'P'),
        "Presion de Burbuja":     ('P_burbuja', 'T', 'Temperatura (°R):',   'P'),
    }

    def __init__(self, get_z, get_kij):
        super().__init__()
        self.get_z=get_z; self.get_kij=get_kij
        self.worker=None
        self.last_result=None
        self._res_unit=None
        self._tipo_txt=None
        self._build()

    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')
        root=QVBoxLayout(self)
        root.setContentsMargins(4,10,4,4); root.setSpacing(3)

        # Título
        title=QLabel("ThermoPhase — Puntos de Saturación")
        title.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22); title.setStyleSheet(LBL_TIT)
        root.addWidget(title)

        # ── Panel de entrada ──────────────────────────────────
        in_box=QFrame()
        in_box.setStyleSheet('background:transparent;border:none;')
        gl=QGridLayout(in_box); gl.setContentsMargins(6,6,6,6); gl.setSpacing(6)

        def lbl(txt, res=False):
            l=QLabel(txt)
            if res:
                l.setStyleSheet(
                    f'background:transparent;border:1px solid {BORDER};'
                    f'color:{TEXT_RES};padding:2px 6px;'
                    f'font-family:"{FONT_F}";font-size:{FS}pt;')
            else:
                l.setStyleSheet(
                    f'background:transparent;border:1px solid {BORDER};'
                    f'padding:2px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
            l.setFixedHeight(24)
            return l

        # Selector de tipo de cálculo
        gl.addWidget(lbl("Calcular:"), 0, 0)
        self.cmb_tipo=QComboBox()
        self.cmb_tipo.addItems(list(self.TIPOS.keys()))
        self.cmb_tipo.setFixedHeight(24)
        _aplicar_estilo_combo(self.cmb_tipo)
        self.cmb_tipo.currentTextChanged.connect(self._on_tipo_change)
        gl.addWidget(self.cmb_tipo, 0, 1)

        # Etiqueta + campo de condición (P o T)
        self.lbl_cond=lbl("Presion (psi):")
        self.lbl_cond.setFixedWidth(130)
        gl.addWidget(self.lbl_cond, 1, 0)
        self.sp_cond=QDoubleSpinBox()
        self.sp_cond.setRange(0.0, 15000.0); self.sp_cond.setDecimals(2)
        self.sp_cond.setSpecialValueText(" ")   # muestra vacío en el mínimo
        self.sp_cond.setValue(0.0)              # inicia vacío
        self.sp_cond.setFixedHeight(24)
        # Sin flechas de incremento/decremento
        self.sp_cond.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_cond.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gl.addWidget(self.sp_cond, 1, 1)

        # Botón calcular
        self.btn=QPushButton("Calcular punto de saturacion")
        self.btn.setStyleSheet(BTN_STYLE); self.btn.setFixedHeight(26)
        self.btn.clicked.connect(self.calcular)
        gl.addWidget(self.btn, 2, 0, 1, 2)

        gl.setColumnStretch(0,0); gl.setColumnStretch(1,1)

        # ── Panel de resultados (a la derecha de la entrada) ──
        res_outer=QVBoxLayout(); res_outer.setSpacing(3)
        res_title=QLabel("Resultado:")
        res_title.setStyleSheet(LBL_SEC); res_title.setFixedHeight(22)
        res_outer.addWidget(res_title)

        res_box=QFrame()
        res_box.setStyleSheet('background:transparent;border:none;')
        rl=QGridLayout(res_box); rl.setContentsMargins(6,4,6,4); rl.setSpacing(4)

        self.lbl_res_label=lbl("Temperatura de rocio (°F):")
        rl.addWidget(self.lbl_res_label, 0, 0)
        self.lbl_res_val=lbl("", res=True)
        self.lbl_res_val.setFixedWidth(120)
        self.lbl_res_val.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.lbl_res_val, 0, 1)

        self.lbl_res2_label=lbl("Equivalente (°R / psi):")
        rl.addWidget(self.lbl_res2_label, 1, 0)
        self.lbl_res2_val=lbl("", res=True)
        self.lbl_res2_val.setFixedWidth(120)
        self.lbl_res2_val.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        rl.addWidget(self.lbl_res2_val, 1, 1)

        self.lbl_estado=QLabel("")
        self.lbl_estado.setStyleSheet(
            f'color:{TEXT_DIM};font-family:"{FONT_F}";font-size:9pt;background:transparent;')
        rl.addWidget(self.lbl_estado, 2, 0, 1, 2)

        # Etiqueta estira para llenar, valor fijo a la derecha → sin huecos
        rl.setColumnStretch(0,1); rl.setColumnStretch(1,0)
        res_outer.addWidget(res_box)

        # Layout horizontal: entrada (izq) + resultado (der), repartido 50/50
        top_row=QHBoxLayout(); top_row.setSpacing(10)
        in_wrap=QVBoxLayout(); in_wrap.setSpacing(3)
        in_title=QLabel("Datos de entrada:")
        in_title.setStyleSheet(LBL_SEC); in_title.setFixedHeight(22)
        in_wrap.addWidget(in_title)
        in_wrap.addWidget(in_box)
        top_row.addLayout(in_wrap, 1)      # entrada ocupa mitad
        top_row.addLayout(res_outer, 1)    # resultado ocupa mitad
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.addLayout(top_row)

        # ── Tabla de composiciones de las fases ───────────────
        comp_title=QLabel("Composicion de las fases en equilibrio:")
        comp_title.setStyleSheet(LBL_SEC); comp_title.setFixedHeight(22)
        root.addWidget(comp_title)

        self.tbl=QTableWidget(NC+1, 3)
        self.tbl.setHorizontalHeaderLabels(["Componente","Fase Vapor","Fase Liquida"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tbl.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;gridline-color:{BORDER};}}'
            f'QHeaderView::section {{ background:{GRAY_HDR};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px; }}')
        hh=self.tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(1,130); self.tbl.setColumnWidth(2,130)
        self.tbl.verticalHeader().setDefaultSectionSize(22)
        self.tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        GRIS_NOMBRE = QColor("#E8E8E8")   # gris claro para nombres
        BLANCO = QColor(WHITE)
        for i in range(NC):
            it=QTableWidgetItem(NOMBRES[i].rstrip(':'))
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS_NOMBRE))
            self.tbl.setItem(i,0,it)
            for c in (1,2):
                cell=QTableWidgetItem("")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cell.setBackground(QBrush(BLANCO))
                self.tbl.setItem(i,c,cell)
        # Fila sumatorias
        sit=QTableWidgetItem("Sumatorias:")
        sit.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        sit.setBackground(QBrush(GRIS_NOMBRE))
        self.tbl.setItem(NC,0,sit)
        for c in (1,2):
            cell=QTableWidgetItem("")
            cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            cell.setBackground(QBrush(BLANCO))
            self.tbl.setItem(NC,c,cell)

        root.addWidget(self.tbl)

        # ── Panel de propiedades del punto de saturación ──────
        prop_title=QLabel("Propiedades del punto de saturacion:")
        prop_title.setStyleSheet(LBL_SEC); prop_title.setFixedHeight(22)
        root.addWidget(prop_title)

        self.tbl_prop=QTableWidget(6, 3)
        self.tbl_prop.setHorizontalHeaderLabels(
            ["Propiedad","Fase Vapor","Fase Liquida"])
        self.tbl_prop.verticalHeader().setVisible(False)
        self.tbl_prop.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_prop.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_prop.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tbl_prop.setStyleSheet(
            f'QTableWidget {{ border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;gridline-color:{BORDER};}}'
            f'QHeaderView::section {{ background:{GRAY_HDR};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;padding:2px; }}')
        hp=self.tbl_prop.horizontalHeader()
        hp.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hp.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hp.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tbl_prop.setColumnWidth(1,130); self.tbl_prop.setColumnWidth(2,130)
        self.tbl_prop.verticalHeader().setDefaultSectionSize(22)
        self.tbl_prop.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_prop.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        _props=["Peso molecular","Factor de compresibilidad",
                "Densidad masica [lb/ft3]","Gravedad especifica"]
        GRIS=QColor("#E8E8E8"); BLANCO_P=QColor(WHITE)
        for r,lbl_p in enumerate(_props):
            it=QTableWidgetItem(lbl_p)
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            it.setBackground(QBrush(GRIS))
            self.tbl_prop.setItem(r,0,it)
            for c in (1,2):
                cc=QTableWidgetItem("")
                cc.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                cc.setBackground(QBrush(BLANCO_P))
                self.tbl_prop.setItem(r,c,cc)
        self.tbl_prop.setRowCount(4)
        root.addWidget(self.tbl_prop)
        root.addStretch()   # el espacio sobrante va al fondo, no entre tablas

    def showEvent(self, event):
        super().showEvent(event)
        self._fit_table_heights()

    def _fit_table_heights(self):
        """Ajusta la altura de cada tabla a la suma real de sus filas,
        para mostrar todas sin scrollbar (robusto ante DPI/versión Windows)."""
        for tbl, nrows in [(self.tbl, NC+1), (self.tbl_prop, 4)]:
            h = tbl.horizontalHeader().height()
            for r in range(nrows):
                h += tbl.rowHeight(r)
            h += 2*tbl.frameWidth() + 2
            tbl.setFixedHeight(h)

    def _tipo_es(self):
        """Clave ESPAÑOL del tipo seleccionado (robusto a la traduccion)."""
        try:
            import idioma
            idx = self.cmb_tipo.currentIndex()
            es = self.cmb_tipo.property(f"_i18n_es_{idx}")
            if es and es in self.TIPOS:
                return es
            txt = self.cmb_tipo.currentText()
            es2 = idioma._TRAD_INV.get(txt, txt)
            return es2 if es2 in self.TIPOS else txt
        except Exception:
            return self.cmb_tipo.currentText()

    def _on_tipo_change(self, txt):
        tipo, unidad, etiqueta, _ = self.TIPOS[self._tipo_es()]
        if unidad=='P':
            self.lbl_cond.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
            self.sp_cond.setRange(0.0, 999999.0)
        else:
            self.lbl_cond.setText(f"{_i18n.t('Temperatura')} ({_u.u_abs()}):")
            self.sp_cond.setRange(0.0, 9999.0)
        # No forzar valor — dejar lo que el usuario haya puesto o vacío

    def calcular(self):
        z=self.get_z()
        if abs(sum(z)-1.0)>1e-3:
            dialogos.advertencia(self,
                "La suma de fracciones debe ser 1.0")
            return
        kij=self.get_kij()
        tipo, unidad, etiqueta, res_unit = self.TIPOS[self._tipo_es()]
        valor=self.sp_cond.value()
        if valor <= 0.0:
            dialogos.advertencia(self,
                "Ingrese un valor de presion o temperatura.")
            return
        # Convertir al interno del motor: P->psia, T->°R
        valor = _u.p_a_psia(valor) if unidad=='P' else _u.R_desde_abs(valor)

        self.btn.setEnabled(False); self.btn.setText(_i18n.t("Calculando..."))
        self.lbl_estado.setText("")
        self._res_unit=res_unit; self._tipo_txt=self.cmb_tipo.currentText()
        eos_ctx = _eng.get_eos()          # EOS activa (ya fijada por get_z)
        self.worker=SatWorker(tipo, valor, z, kij, eos_ctx)
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def aplicar_unidades(self, old):
        """Convierte el valor de entrada, actualiza etiquetas y re-muestra el
        resultado en el sistema de unidades activo."""
        tipo, unidad, etiqueta, res_unit = self.TIPOS[self._tipo_es()]
        v = self.sp_cond.value()
        if v > 0:
            if unidad == 'P':
                v_int = _u.p_a_psia(v, old); self.sp_cond.setValue(_u.p_desde_psia(v_int))
            else:
                v_int = _u.R_desde_abs(v, old); self.sp_cond.setValue(_u.abs_desde_R(v_int))
        # Etiqueta de condicion
        if unidad == 'P':
            self.lbl_cond.setText(f"{_i18n.t('Presion')} ({_u.u('P')}):")
        else:
            self.lbl_cond.setText(f"{_i18n.t('Temperatura')} ({_u.u_abs()}):")
        # Re-render del ultimo resultado (internos °R/psia)
        if getattr(self, 'last_result', None) is not None:
            self._render(self.last_result)

    def _on_error(self, msg):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular punto de saturacion"))
        dialogos.error(self, msg)

    def _on_done(self, res):
        self.btn.setEnabled(True); self.btn.setText(_i18n.t("Calcular punto de saturacion"))
        if not res or not res.get('exito'):
            self.lbl_estado.setText(_i18n.t("No se encontro punto de saturacion"))
            self.lbl_res_val.setText(""); self.lbl_res2_val.setText("")
            self.last_result = None
            return
        self.last_result = res
        self._render(res)

    def _render(self, res):
        """Muestra el resultado en pantalla. Se llama tanto desde el worker
        (calculo nuevo) como desde set_estado (carga desde archivo)."""

        T=res['T']; P=res['P']   # internos: °R, psia
        if self._res_unit=='T':
            self.lbl_res_label.setText(f"{self._tipo_txt} ({_u.u('T')}):")
            self.lbl_res_val.setText(f"{_u.t_desde_R(T):.2f}")
            self.lbl_res2_label.setText(f"{_i18n.t('Equivalente')} ({_u.u_abs()}):")
            self.lbl_res2_val.setText(f"{_u.abs_desde_R(T):.2f}")
        else:
            self.lbl_res_label.setText(f"{self._tipo_txt} ({_u.u('P')}):")
            self.lbl_res_val.setText(f"{_u.p_desde_psia(P):.2f}")
            self.lbl_res2_label.setText(f"{_i18n.t('Temperatura')} ({_u.u('T')}):")
            self.lbl_res2_val.setText(f"{_u.t_desde_R(T):.2f}")

        self.lbl_estado.setText(_i18n.t("Convergencia exitosa."))

        # Llenar tabla de composiciones
        x=res.get('x',[0]*NC); y=res.get('y',[0]*NC)
        sx=sum(x); sy=sum(y)
        for i in range(NC):
            self.tbl.item(i,1).setText(f"{y[i]:.4f}")
            self.tbl.item(i,2).setText(f"{x[i]:.4f}")
            self.tbl.item(i,1).setBackground(QBrush(QColor(WHITE)))
            self.tbl.item(i,2).setBackground(QBrush(QColor(WHITE)))
            self.tbl.item(i,1).setForeground(QBrush(QColor(TEXT_RES)))
            self.tbl.item(i,2).setForeground(QBrush(QColor(TEXT_RES)))
        self.tbl.item(NC,1).setText(f"{sy:.4f}")
        self.tbl.item(NC,2).setText(f"{sx:.4f}")

        # Llenar panel de propiedades
        p=res.get('props',{})
        def setp(row, key_v, key_l, fmt="{:.4f}"):
            vv=p.get(key_v); vl=p.get(key_l)
            self.tbl_prop.item(row,1).setText(fmt.format(vv) if vv is not None else "")
            self.tbl_prop.item(row,2).setText(fmt.format(vl) if vl is not None else "")
            self.tbl_prop.item(row,1).setForeground(QBrush(QColor(TEXT_RES)))
            self.tbl_prop.item(row,2).setForeground(QBrush(QColor(TEXT_RES)))
        setp(0,'PM_v','PM_l')
        setp(1,'ZV','ZL')
        setp(2,'rho_v','rho_l')
        setp(3,'sg_v','sg_l')

    # ── Guardar / restaurar estado ────────────────────────────
    def get_estado(self):
        """Devuelve inputs + resultado calculado (si existe)."""
        return {
            'entrada': {
                'tipo':  self._tipo_es(),
                'valor': float(self.sp_cond.value()),
            },
            'resultado': self.last_result,   # dict o None
        }

    def set_estado(self, datos):
        """Restaura inputs y re-renderiza el resultado sin recalcular."""
        e = datos.get('entrada', {}) or {}
        tipo = e.get('tipo', '')
        idx = self.cmb_tipo.findText(tipo)
        if idx < 0 and tipo in self.TIPOS:
            idx = list(self.TIPOS.keys()).index(tipo)
        if idx >= 0:
            self.cmb_tipo.setCurrentIndex(idx)
        try:
            self.sp_cond.setValue(float(e.get('valor', 0.0)))
        except (TypeError, ValueError):
            self.sp_cond.setValue(0.0)
        # Renderizar resultado si estaba
        r = datos.get('resultado')
        if not r:
            return
        self.last_result = r
        # Reconstruir _res_unit y _tipo_txt (necesarios para _render)
        if tipo in self.TIPOS:
            _, _, _, self._res_unit = self.TIPOS[tipo]
            self._tipo_txt = tipo
        self._render(r)

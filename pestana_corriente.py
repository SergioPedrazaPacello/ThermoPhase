"""
pestana_corriente.py — Pestaña "Propiedades de la corriente".

Solo interfaz (placeholder). Reune propiedades de calidad y economia de la
corriente global de gas natural, tipicas de un gas de venta / especificacion:

  · Calidad del gas : poder calorifico bruto (HHV) y neto (LHV), indice de
                      Wobbe, numero de metano, gravedad especifica (aire=1),
                      contenido de inertes (N2+CO2).
  · Licuables (GPM) : galones de liquido por mil pies cubicos para C2+, C3+,
                      C4+, C5+ y riqueza en bbl/MMscf.
  · Energia         : BOE (barriles equivalentes de petroleo) y caudal
                      energetico en MMBTU/dia.

Los calculos NO estan implementados todavia: los campos muestran "—".
Mantiene la misma estetica retro (Arial Narrow, paleta plomo) que el resto
de las pestañas y la interfaz de tamaño fijo.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QGridLayout, QFrame, QAbstractSpinBox
)
from PyQt6.QtCore import Qt

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

# Ancho de contenido, para armonizar con las demás pestañas
W_TAB = 710


class TabCorriente(QWidget):
    def __init__(self, get_z, get_kij):
        super().__init__()
        self.get_z = get_z
        self.get_kij = get_kij
        self._campos = {}
        self._build()

    # ── helpers de etiquetas / campos ────────────────────────
    def _lbl(self, txt, w=None, align_r=False):
        l = QLabel(txt)
        al = (Qt.AlignmentFlag.AlignRight if align_r
              else Qt.AlignmentFlag.AlignLeft) | Qt.AlignmentFlag.AlignVCenter
        l.setAlignment(al)
        l.setStyleSheet(
            f'background:transparent;border:none;color:{TEXT};'
            f'padding:1px 4px;font-family:"{FONT_F}";font-size:{FS}pt;')
        l.setFixedHeight(22)
        if w:
            l.setFixedWidth(w)
        return l

    def _campo(self, clave, unidad="", w_val=110, w_uni=90):
        """Devuelve un widget compuesto: [ valor (readonly) ][ unidad ]."""
        cont = QWidget()
        h = QHBoxLayout(cont)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(3)
        val = QLabel("—")
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        val.setFixedHeight(22)
        val.setFixedWidth(w_val)
        val.setStyleSheet(
            f'background:{GRAY_RES};border:1px solid {BORDER};color:{TEXT_RES};'
            f'padding:1px 6px;font-family:"{FONT_F}";font-size:{FS}pt;')
        h.addWidget(val)
        if unidad:
            u = QLabel(unidad)
            u.setFixedHeight(22)
            u.setFixedWidth(w_uni)
            u.setStyleSheet(
                f'background:transparent;border:none;color:{TEXT_DIM};'
                f'padding:1px 2px;font-family:"{FONT_F}";font-size:9pt;')
            h.addWidget(u)
        h.addStretch()
        self._campos[clave] = val
        return cont

    def _seccion(self, root, titulo):
        s = QLabel(titulo)
        s.setStyleSheet(LBL_SEC)
        s.setFixedHeight(22)
        root.addWidget(s)

    def _grid_filas(self, filas):
        """Construye un QFrame con un grid de (etiqueta, campo) en dos columnas."""
        box = QFrame()
        box.setStyleSheet('background:transparent;border:none;')
        g = QGridLayout(box)
        g.setContentsMargins(6, 4, 6, 4)
        g.setHorizontalSpacing(10)
        g.setVerticalSpacing(4)
        # Distribuye en 2 columnas de pares (etiqueta, campo)
        media = (len(filas) + 1) // 2
        for i, (texto, clave, unidad) in enumerate(filas):
            col = 0 if i < media else 2
            fila = i if i < media else i - media
            g.addWidget(self._lbl(texto, w=185, align_r=True), fila, col)
            g.addWidget(self._campo(clave, unidad), fila, col + 1)
        g.setColumnStretch(1, 1)
        g.setColumnStretch(3, 1)
        return box

    # ── construccion ─────────────────────────────────────────
    def _build(self):
        self.setStyleSheet(f'background:{GRAY_LBL};')

        # Centrado horizontal como en la pestaña de equilibrio
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch()

        box = QWidget()
        box.setFixedWidth(W_TAB)
        root = QVBoxLayout(box)
        root.setContentsMargins(4, 10, 4, 4)
        root.setSpacing(3)

        # ── Título ───────────────────────────────────────────
        title = QLabel("ThermoPhase — Propiedades de la Corriente (Gas de Venta)")
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title.setFixedHeight(22)
        title.setStyleSheet(LBL_TIT)
        root.addWidget(title)

        # ── Condiciones de referencia ────────────────────────
        self._seccion(root, "Condiciones de referencia:")
        ref = QFrame()
        ref.setStyleSheet('background:transparent;border:none;')
        gr = QGridLayout(ref)
        gr.setContentsMargins(6, 4, 6, 4)
        gr.setHorizontalSpacing(10); gr.setVerticalSpacing(4)

        gr.addWidget(self._lbl("Presión base (psia):", w=185, align_r=True), 0, 0)
        self.sp_Pb = QDoubleSpinBox()
        self.sp_Pb.setRange(0.0, 20.0); self.sp_Pb.setDecimals(3)
        self.sp_Pb.setValue(14.696); self.sp_Pb.setFixedHeight(22)
        self.sp_Pb.setFixedWidth(110)
        self.sp_Pb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_Pb.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gr.addWidget(self.sp_Pb, 0, 1)

        gr.addWidget(self._lbl("Temperatura base (°F):", w=185, align_r=True), 0, 2)
        self.sp_Tb = QDoubleSpinBox()
        self.sp_Tb.setRange(0.0, 120.0); self.sp_Tb.setDecimals(2)
        self.sp_Tb.setValue(60.0); self.sp_Tb.setFixedHeight(22)
        self.sp_Tb.setFixedWidth(110)
        self.sp_Tb.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_Tb.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gr.addWidget(self.sp_Tb, 0, 3)

        gr.addWidget(self._lbl("Caudal de gas (MMscfd):", w=185, align_r=True), 1, 0)
        self.sp_Q = QDoubleSpinBox()
        self.sp_Q.setRange(0.0, 5000.0); self.sp_Q.setDecimals(3)
        self.sp_Q.setValue(0.0); self.sp_Q.setSpecialValueText(" ")
        self.sp_Q.setFixedHeight(22); self.sp_Q.setFixedWidth(110)
        self.sp_Q.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.sp_Q.setStyleSheet(
            f'QDoubleSpinBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt; }}')
        gr.addWidget(self.sp_Q, 1, 1)

        gr.addWidget(self._lbl("Base del poder calorífico:", w=185, align_r=True), 1, 2)
        self.cmb_base = QComboBox()
        self.cmb_base.addItems(["Real (Z corregido)", "Ideal"])
        self.cmb_base.setFixedHeight(22); self.cmb_base.setFixedWidth(150)
        self.cmb_base.setStyleSheet(
            f'QComboBox {{ background:{WHITE};border:1px solid {BORDER};'
            f'font-family:"{FONT_F}";font-size:{FS}pt;padding:1px 4px; }}')
        gr.addWidget(self.cmb_base, 1, 3)

        gr.setColumnStretch(1, 1); gr.setColumnStretch(3, 1)
        root.addWidget(ref)

        # Botón calcular (placeholder)
        self.btn = QPushButton("Calcular propiedades de la corriente")
        self.btn.setStyleSheet(BTN_STYLE)
        self.btn.setFixedHeight(26)
        self.btn.clicked.connect(self._placeholder)
        root.addWidget(self.btn)

        # ── Calidad del gas ──────────────────────────────────
        self._seccion(root, "Calidad del gas:")
        root.addWidget(self._grid_filas([
            ("Poder calorífico bruto (HHV):", "hhv", "BTU/scf"),
            ("Poder calorífico neto (LHV):",  "lhv", "BTU/scf"),
            ("Índice de Wobbe:",              "wobbe", "BTU/scf"),
            ("Número de metano (MN):",        "mn", "—"),
            ("Gravedad específica (aire=1):", "sg_gas", "—"),
            ("Contenido de inertes (N₂+CO₂):", "inertes", "% mol"),
        ]))

        # ── Contenido de líquidos (GPM) ──────────────────────
        self._seccion(root, "Contenido de líquidos (GPM):")
        root.addWidget(self._grid_filas([
            ("GPM C2+:", "gpm_c2", "gal/Mscf"),
            ("GPM C3+:", "gpm_c3", "gal/Mscf"),
            ("GPM C4+:", "gpm_c4", "gal/Mscf"),
            ("GPM C5+:", "gpm_c5", "gal/Mscf"),
            ("Riqueza de licuables:", "riqueza", "bbl/MMscf"),
            ("Cricondentherm (rocío HC):", "cricon", "°F"),
        ]))

        # ── Equivalencias energéticas ────────────────────────
        self._seccion(root, "Equivalencias energéticas:")
        root.addWidget(self._grid_filas([
            ("Caudal energético:", "energia", "MMBTU/d"),
            ("BOE del gas:",       "boe", "bbl-eq/d"),
            ("Factor de conversión:", "factor_boe", "scf/BOE"),
            ("Poder calorífico volumétrico:", "pc_vol", "MMBTU/MMscf"),
        ]))

        # Nota de estado
        nota = QLabel("Nota: módulo de cálculo pendiente de implementación "
                      "(interfaz preliminar).")
        nota.setStyleSheet(
            f'background:transparent;border:none;color:{TEXT_DIM};'
            f'font-family:"{FONT_F}";font-size:9pt;padding:2px 4px;')
        root.addWidget(nota)

        root.addStretch()
        outer.addWidget(box)
        outer.addStretch()

    # ── placeholder ──────────────────────────────────────────
    def _placeholder(self):
        try:
            import dialogos
            dialogos.info(
                self,
                "El cálculo de propiedades de la corriente aún no está "
                "implementado.\n\nEsta pestaña es una vista preliminar de la "
                "interfaz.")
        except Exception:
            pass

    # ── Estado (para guardar/abrir .tpsim) ───────────────────
    def get_estado(self):
        return {
            'entrada': {
                'P_base':  float(self.sp_Pb.value()),
                'T_base':  float(self.sp_Tb.value()),
                'caudal':  float(self.sp_Q.value()),
                'base_pc': self.cmb_base.currentText(),
            },
            'resultado': None,
        }

    def set_estado(self, datos):
        e = (datos or {}).get('entrada', {}) or {}
        self.sp_Pb.setValue(float(e.get('P_base', 14.696) or 14.696))
        self.sp_Tb.setValue(float(e.get('T_base', 60.0) or 60.0))
        self.sp_Q.setValue(float(e.get('caudal', 0.0) or 0.0))
        idx = self.cmb_base.findText(e.get('base_pc', "Real (Z corregido)"))
        if idx >= 0:
            self.cmb_base.setCurrentIndex(idx)
        # Resetear campos de resultado a "—"
        for val in self._campos.values():
            val.setText("—")

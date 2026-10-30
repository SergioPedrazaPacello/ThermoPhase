"""
numeros.py — Lectura de números ingresados por el usuario.

El separador decimal puede ser el punto o la coma ("0.25" y "0,25" valen lo
mismo).  Si el texto trae ambos (p. ej. "1.234,5" o "1,234.5", típico de un
valor copiado de Excel), el último que aparece es el decimal y el otro se toma
como separador de miles.  Se ignoran espacios y el signo "%".

También incluye SpinNum, un QDoubleSpinBox que acepta la coma decimal.
"""
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QValidator, QRegularExpressionValidator, QPalette, QColor
from PyQt6.QtCore import QLocale, Qt, pyqtSignal, QRegularExpression


def normalizar_texto(txt):
    """Texto numérico con punto decimal (sin miles, espacios ni %)."""
    t = str(txt).strip().replace(' ', '').replace(' ', '').replace('%', '')
    if ',' in t and '.' in t:
        if t.rfind(',') > t.rfind('.'):
            t = t.replace('.', '').replace(',', '.')
        else:
            t = t.replace(',', '')
    elif ',' in t:
        if t.count(',') > 1:            # "1,234,567" → miles
            t = t.replace(',', '')
        else:
            t = t.replace(',', '.')
    return t


def a_float(txt, defecto=None):
    """float del texto del usuario; `defecto` si está vacío o no es número."""
    t = normalizar_texto(txt)
    if t == '':
        return defecto
    try:
        return float(t)
    except ValueError:
        return defecto


def fmt_comp(v, min_dec=4, max_dec=10):
    """Texto de una fracción/porcentaje de composición SIN perder precisión:
    hasta `max_dec` decimales (quita ceros sobrantes y el ruido de coma
    flotante, p. ej. 6.130000000000001 → 6.13) y al menos `min_dec`."""
    t = f"{float(v):.{max_dec}f}".rstrip('0')
    ent, _, dec = t.partition('.')
    if len(dec) < min_dec:
        dec = dec + '0'*(min_dec - len(dec))
    return f"{ent}.{dec}"


def es_numero(txt):
    return a_float(txt) is not None


def composicion_a_fracciones(valores, umbral=1.5):
    """Convierte una composición ingresada como fracción o como porcentaje a
    fracciones: si la suma supera `umbral` (p. ej. ≈100) se interpreta como
    porcentaje molar y se divide por 100.  Devuelve (fracciones, es_pct)."""
    s = sum(valores)
    if s > umbral:
        return [v/100.0 for v in valores], True
    return list(valores), False


class SpinNum(QLineEdit):
    """Campo numérico (sustituye al QDoubleSpinBox).

    En algunos equipos con Windows (escalado de pantalla, estilo «windows11»)
    el QDoubleSpinBox reducía su editor interno a una franja de pocos píxeles
    y el número no se veía.  Este campo es un QLineEdit simple con la misma
    interfaz que usaba el programa: setRange, setDecimals, setSpecialValueText,
    setButtonSymbols, value, setValue y la señal valueChanged(float).
    Acepta punto o coma como separador decimal.  El «valor especial» (el
    mínimo, con texto especial definido) se muestra como campo vacío."""

    valueChanged = pyqtSignal(float)

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._min = 0.0; self._max = 99.99; self._dec = 2
        self._esp = None                  # texto del valor especial
        self._v = 0.0
        self.setValidator(QRegularExpressionValidator(
            QRegularExpression(r'^-?\d*([.,]\d*)?$'), self))
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setTextMargins(2, 0, 2, 0)
        pal = self.palette()
        for grp in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive,
                    QPalette.ColorGroup.Disabled):
            pal.setColor(grp, QPalette.ColorRole.Base, QColor("#FFFFFF"))
            pal.setColor(grp, QPalette.ColorRole.Text, QColor("#000000"))
        self.setPalette(pal)
        self.textEdited.connect(self._on_editado)
        self.editingFinished.connect(self._mostrar)
        self._mostrar()

    # ── interfaz compatible con QDoubleSpinBox ──────────────────────────
    def setRange(self, lo, hi):
        self._min, self._max = float(lo), float(hi)
        self._v = min(max(self._v, self._min), self._max)
        self._mostrar()

    def setMinimum(self, lo): self.setRange(lo, self._max)
    def setMaximum(self, hi): self.setRange(self._min, hi)
    def minimum(self): return self._min
    def maximum(self): return self._max

    def setDecimals(self, d):
        self._dec = int(d); self._mostrar()

    def decimals(self): return self._dec

    def setSpecialValueText(self, t):
        self._esp = t; self._mostrar()

    def setButtonSymbols(self, *_a):
        pass

    def setStyleSheet(self, qss):
        super().setStyleSheet(qss.replace('QDoubleSpinBox', 'QLineEdit'))

    def value(self):
        return self._v

    def setValue(self, v):
        v = round(min(max(float(v), self._min), self._max), self._dec)
        cambio = v != self._v
        self._v = v
        self._mostrar()
        if cambio:
            self.valueChanged.emit(v)

    # ── internos ────────────────────────────────────────────────────────
    def _es_especial(self):
        return self._esp is not None and self._v == self._min

    def _mostrar(self):
        txt = "" if self._es_especial() else f"{self._v:.{self._dec}f}"
        if self.text() != txt:
            self.setText(txt)
        if not self.hasFocus():
            self.setCursorPosition(0)

    def _on_editado(self, txt):
        v = a_float(txt)
        if v is None:
            if txt.strip() in ("", "-"):
                v = self._min                     # campo vacío = valor especial
            else:
                return
        v = min(max(v, self._min), self._max)
        if v != self._v:
            self._v = v
            self.valueChanged.emit(v)

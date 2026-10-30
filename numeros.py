"""
numeros.py — Lectura de números ingresados por el usuario.

El separador decimal puede ser el punto o la coma ("0.25" y "0,25" valen lo
mismo).  Si el texto trae ambos (p. ej. "1.234,5" o "1,234.5", típico de un
valor copiado de Excel), el último que aparece es el decimal y el otro se toma
como separador de miles.  Se ignoran espacios y el signo "%".

También incluye SpinNum, un QDoubleSpinBox que acepta la coma decimal.
"""
from PyQt6.QtWidgets import QDoubleSpinBox
from PyQt6.QtGui import QValidator
from PyQt6.QtCore import QLocale


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


class SpinNum(QDoubleSpinBox):
    """QDoubleSpinBox que acepta punto o coma como separador decimal."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.setLocale(QLocale(QLocale.Language.C))      # muestra con punto
        # Estilo Fusion por widget (como los combos): el estilo nativo de
        # Windows 11 («windows11», Qt 6.7+) no respeta la hoja de estilo de
        # los QDoubleSpinBox y deja el texto invisible.  Con Fusion el QSS se
        # aplica igual en todas las versiones de Windows.
        try:
            from PyQt6.QtWidgets import QStyleFactory
            from PyQt6.QtGui import QPalette, QColor
            from PyQt6.QtCore import Qt
            self._estilo = QStyleFactory.create("Fusion")
            if self._estilo is not None:
                self.setStyle(self._estilo)
            pal = self.palette()
            for grp in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive,
                        QPalette.ColorGroup.Disabled):
                pal.setColor(grp, QPalette.ColorRole.Base, QColor("#FFFFFF"))
                pal.setColor(grp, QPalette.ColorRole.Text, QColor("#000000"))
            self.setPalette(pal)
            self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            le = self.lineEdit()
            if le is not None:
                le.setTextMargins(0, 0, 0, 0)
        except Exception:
            pass

    def validate(self, text, pos):
        t = text.replace(',', '.')
        estado, _t, _p = super().validate(t, pos)
        return estado, text, pos

    def valueFromText(self, text):
        t = text
        if self.prefix() and t.startswith(self.prefix()):
            t = t[len(self.prefix()):]
        if self.suffix() and t.endswith(self.suffix()):
            t = t[:-len(self.suffix())]
        v = a_float(t)
        return self.value() if v is None else v

    def fixup(self, text):
        return text.replace(',', '.')

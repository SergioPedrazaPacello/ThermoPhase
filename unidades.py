"""
unidades.py — Sistema de unidades de ThermoPhase.

El MOTOR trabaja SIEMPRE en unidades internas FIELD (psia, °R, lb/ft³,
Btu/lbmol, Btu/(lbmol·°F), ft³/lbmol). Este modulo solo convierte al ENTRAR
y al MOSTRAR, de modo que la fisica validada no cambia.

Tres sistemas (mismas convenciones que HYSYS):
    FIELD  : psia, °F, lb/ft³, Btu/lbmol,  Btu/(lbmol·°F),  ft³/lbmol
    SI     : kPa,  °C, kg/m³,  kJ/kgmol,   kJ/(kgmol·°C),   m³/kgmol
    METRIC : bar,  °C, kg/m³,  kcal/kgmol, kcal/(kgmol·°C), m³/kgmol   (EuroSI)
"""

_SISTEMA = 'FIELD'

SISTEMAS = ['FIELD', 'SI', 'METRIC']
# Etiqueta legible del sistema (para el desplegable de la barra)
NOMBRE_SISTEMA = {'FIELD': 'Field', 'SI': 'SI', 'METRIC': 'Metric'}
_NOMBRE_INV = {v: k for k, v in NOMBRE_SISTEMA.items()}

# Unidades por magnitud y sistema
U = {
    'FIELD':  {'P': 'psia', 'T': '°F', 'dens': 'lb/ft³',
               'H': 'Btu/lbmol', 'S': 'Btu/lbmol·°F', 'V': 'ft³/lbmol'},
    'SI':     {'P': 'kPa',  'T': '°C', 'dens': 'kg/m³',
               'H': 'kJ/kgmol', 'S': 'kJ/kgmol·°C', 'V': 'm³/kgmol'},
    'METRIC': {'P': 'bar',  'T': '°C', 'dens': 'kg/m³',
               'H': 'kcal/kgmol', 'S': 'kcal/kgmol·°C', 'V': 'm³/kgmol'},
}

# ── Factores de conversion desde la unidad interna FIELD ─────────────
# Presion: interna psia
_P_FACTOR = {'FIELD': 1.0, 'SI': 6.8947572932, 'METRIC': 0.0689475729}
# Densidad: interna lb/ft³ -> kg/m³
_DENS_FACTOR = {'FIELD': 1.0, 'SI': 16.018463374, 'METRIC': 16.018463374}
# Entalpia: interna Btu/lbmol -> kJ/kgmol (×2.326) o kcal/kgmol (×0.5555556)
_H_FACTOR = {'FIELD': 1.0, 'SI': 2.326, 'METRIC': 0.5555555556}
# Entropia: interna Btu/(lbmol·°F) -> kJ/(kgmol·°C) (×4.1868) o kcal/(kgmol·°C) (×1.0)
_S_FACTOR = {'FIELD': 1.0, 'SI': 4.1868, 'METRIC': 1.0}
# Volumen molar: interna ft³/lbmol -> m³/kgmol (×0.0624279606)
_V_FACTOR = {'FIELD': 1.0, 'SI': 0.0624279606, 'METRIC': 0.0624279606}


def set_sistema(s):
    global _SISTEMA
    s = str(s).upper()
    if s in SISTEMAS:
        _SISTEMA = s
    elif s in _NOMBRE_INV:
        _SISTEMA = _NOMBRE_INV[s]


def sistema():
    return _SISTEMA


def u(mag, sis=None):
    """Etiqueta de unidad de la magnitud ('P','T','dens','H','S','V')."""
    return U[sis or _SISTEMA][mag]


# ── PRESION (interna psia) ───────────────────────────────────────────
def p_desde_psia(p, sis=None):
    return p * _P_FACTOR[sis or _SISTEMA]

def p_a_psia(v, sis=None):
    f = _P_FACTOR[sis or _SISTEMA]
    return v / f if f else v


# ── TEMPERATURA ──────────────────────────────────────────────────────
# Referencias internas: °F (para inputs) y °R (para el motor).
def t_desde_F(tf, sis=None):
    """°F -> unidad de temperatura del sistema (°F o °C)."""
    s = sis or _SISTEMA
    return tf if s == 'FIELD' else (tf - 32.0) / 1.8      # °C

def t_a_F(v, sis=None):
    """unidad del sistema -> °F."""
    s = sis or _SISTEMA
    return v if s == 'FIELD' else v * 1.8 + 32.0

def t_desde_R(tr, sis=None):
    """°R -> unidad del sistema (°F o °C)."""
    return t_desde_F(tr - 459.67, sis)

def t_a_R(v, sis=None):
    """unidad del sistema -> °R."""
    return t_a_F(v, sis) + 459.67

def dt_desde_F(dtf, sis=None):
    """Convierte un INTERVALO/diferencia de temperatura (°F -> °C)."""
    s = sis or _SISTEMA
    return dtf if s == 'FIELD' else dtf / 1.8


# Campo de temperatura ABSOLUTA (°R en Field, K en SI/Metric)
def u_abs(sis=None):
    return '°R' if (sis or _SISTEMA) == 'FIELD' else 'K'

def R_desde_abs(v, sis=None):
    """Valor del campo absoluto (°R o K) -> °R (interno del motor)."""
    return v if (sis or _SISTEMA) == 'FIELD' else v * 1.8

def abs_desde_R(tr, sis=None):
    """°R -> valor del campo absoluto (°R o K)."""
    return tr if (sis or _SISTEMA) == 'FIELD' else tr / 1.8

def offset_abs_rel(sis=None):
    """abs = rel + offset  (°R=°F+459.67 ; K=°C+273.15)."""
    return 459.67 if (sis or _SISTEMA) == 'FIELD' else 273.15


# ── DENSIDAD, ENTALPIA, ENTROPIA, VOLUMEN MOLAR ─────────────────────
def dens_desde(v, sis=None):   return v * _DENS_FACTOR[sis or _SISTEMA]
def H_desde(v, sis=None):      return v * _H_FACTOR[sis or _SISTEMA]
def S_desde(v, sis=None):      return v * _S_FACTOR[sis or _SISTEMA]
def V_desde(v, sis=None):      return v * _V_FACTOR[sis or _SISTEMA]

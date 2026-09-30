"""Contenido de agua y capacidad de agua de la fase gas [lb/MMscf].

Contenido de agua
    Agua que el gas lleva realmente, leída del flash en (T, P):
        W = y_w · M_w · (10⁶ / V_std)
    con y_w la fracción molar de agua en la fase vapor, M_w el peso molecular
    del agua y V_std el volumen molar de gas ideal a condiciones estándar
    (60 °F y 14.696 psia → 379.48 scf/lbmol).  Es la base "gas húmedo" de la
    GPSA y de la carta de McKetta-Wehe (lb de agua por MMscf de gas, contando
    el vapor de agua en los scf).  V_std es de gas ideal, como en HYSYS y en la
    GPSA, por eso no depende de la composición: 1 lbmol de cualquier gas ocupa
    379.48 scf estándar.  La composición entra sólo a través de y_w.

Capacidad de agua (contenido de saturación)
    Agua que el mismo gas tendría en equilibrio con agua libre a la misma
    (T, P).  Se obtiene con un segundo flash: la composición HC de la fase
    vapor más un pequeño exceso de agua libre (hidratos.saturar_agua), y se
    lee y_w de su vapor.  Si el flash original ya tiene fase acuosa, el vapor
    está saturado y la capacidad es igual al contenido.

Ambas propiedades sólo tienen sentido para la fase vapor.
"""
import numpy as np
import eos as _e

T_STD_R = 519.67                 # 60 °F
P_STD_PSIA = 14.696
V_STD = _e.R_GAS*T_STD_R/P_STD_PSIA        # scf/lbmol, gas ideal (≈379.48)
K_LB_MMSCF = _e.AGUA_PM*1.0e6/V_STD         # lb/MMscf por unidad de y_w


def contenido(y_w):
    """Contenido de agua [lb/MMscf] de una fase vapor con fracción y_w."""
    if y_w is None:
        return None
    return float(y_w)*K_LB_MMSCF


def capacidad(y_hc, T_R, P_psia, eos=None):
    """Capacidad de agua [lb/MMscf] del gas de composición HC `y_hc`
    (13 componentes, o 14 con el agua, que se descarta) a (T, P)."""
    import flash_agua as _fa
    import hidratos as _h
    if eos is None:
        eos = _e.get_eos()
    y = np.asarray(y_hc, dtype=float)[:_e.NC]
    if y.sum() <= 0:
        return None
    y = y/y.sum()
    try:
        zz = _h.saturar_agua(y, T_R, P_psia, eos)
        r = _fa.flash_trifasico(zz, float(T_R), float(P_psia), eos=eos,
                                metodo='hv')
        if (r.get('beta_V') or 0.0) <= 1e-12 or r.get('y') is None:
            return None
        return contenido(np.asarray(r['y'])[_e.NC])
    except Exception:
        return None


def propiedades_gas(y14, T_R, P_psia, eos=None, hay_agua_libre=False):
    """(contenido, capacidad) [lb/MMscf] de la fase vapor y14 (14 comp.; con
    13 el contenido es 0).  Con agua libre en el flash, capacidad = contenido."""
    if y14 is None:
        return None, None
    y = np.asarray(y14, dtype=float)
    yw = float(y[_e.NC]) if len(y) > _e.NC else 0.0
    cont = contenido(yw)
    if hay_agua_libre:
        return cont, cont
    return cont, capacidad(y, T_R, P_psia, eos)

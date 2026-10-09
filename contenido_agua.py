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


# ── Saturación con agua (composición saturada exacta) ─────────────────────
def saturar_exacto(z, T_R, P_psia, eos=None):
    """Satura con agua la parte de hidrocarburos de `z` (13 o 14 comp.; el
    agua que traiga se descarta) a (T, P): agrega exactamente el agua que la
    mezcla admite sin formar agua libre (fase acuosa incipiente, β_W → 0).

    Es la opción "Saturate w. water" de PVTsim: con esa cantidad de agua, al
    bajar la temperatura a presión constante condensa una fase acuosa.
    La relación agua/hidrocarburo se lee del agua disuelta en las fases de
    hidrocarburo de un flash con un exceso mínimo de agua libre, y se afina
    reduciendo ese exceso; las proporciones entre hidrocarburos no cambian.

    Devuelve dict: z_sat (14 comp.), r_sat (mol agua / mol HC), beta_V,
    beta_L (fases de hidrocarburo de la mezcla saturada), y_w (agua en el
    vapor) y cont_gas [lb/MMscf] del gas saturado (None sin vapor)."""
    import flash_agua as _fa
    import hidratos as _h
    if eos is None:
        eos = _e.get_eos()
    z13 = np.asarray(z, dtype=float)[:_e.NC]
    if z13.sum() <= 0:
        return None
    z13 = z13/z13.sum()
    T_R = float(T_R); P_psia = float(P_psia)

    def z14(r):
        return np.concatenate([z13/(1.0 + r), [r/(1.0 + r)]])

    def r_hc(zz):
        """(β_W, agua/HC en las fases de hidrocarburo) del flash de zz."""
        res = _fa.flash_trifasico(zz, T_R, P_psia, eos=eos, metodo='hv')
        bW = res.get('beta_W', 0.0) or 0.0
        if bW <= 1e-14 or res.get('w') is None:
            return bW, None
        w = np.asarray(res['w'], dtype=float)
        n_w = zz[_e.NC] - bW*w[_e.NC]
        n_hc = (1.0 - zz[_e.NC]) - bW*(1.0 - w[_e.NC])
        if n_hc <= 0 or n_w <= 0:
            return bW, None
        return bW, n_w/n_hc

    zz = np.asarray(_h.saturar_agua(z13, T_R, P_psia, eos, exceso=0.01), dtype=float)
    r = zz[_e.NC]/(1.0 - zz[_e.NC])
    bW, rs = r_hc(zz)
    if rs is None:
        return None
    r = rs
    for e in (0.002, 0.0004):
        bW, rs = r_hc(z14(r*(1.0 + e)))
        if rs is None:
            break
        r = rs
    zs = z14(r)
    res = _fa.flash_trifasico(zs, T_R, P_psia, eos=eos, metodo='hv')
    bV = float(res.get('beta_V') or 0.0); bL = float(res.get('beta_L') or 0.0)
    yw = None; cont = None
    if bV > 1e-12 and res.get('y') is not None:
        yw = float(np.asarray(res['y'])[_e.NC]); cont = contenido(yw)
    return {'z_sat': [float(v) for v in zs], 'r_sat': float(r),
            'beta_V': bV, 'beta_L': bL, 'y_w': yw, 'cont_gas': cont}

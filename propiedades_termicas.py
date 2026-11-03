# -*- coding: utf-8 -*-
"""
propiedades_termicas.py — Propiedades derivadas de la ecuación de estado por
fase, como las reporta PVTsim en el flash:

    Cp, Cv              capacidades caloríficas molares   [J/(mol·°C)]
    κ = Cp/Cv           coeficiente isoentrópico
    μJT                 coeficiente de Joule-Thomson      [°C/bar]
    u                   velocidad del sonido              [m/s]
    V                   volumen molar                     [cm³/mol]

Ecuación cúbica genérica (PR: δ1 = 1+√2, δ2 = 1−√2; SRK: δ1 = 1, δ2 = 0):

    P = RT/(V−b) − a(T)/[(V+δ1 b)(V+δ2 b)]

    (∂P/∂T)_V = R/(V−b) − a'/[(V+δ1 b)(V+δ2 b)]
    (∂P/∂V)_T = −RT/(V−b)² + a(2V+(δ1+δ2)b)/[(V+δ1 b)(V+δ2 b)]²
    Cv = Cv⁰ + T·a''/[(δ1−δ2) b]·ln[(V+δ1 b)/(V+δ2 b)],   Cv⁰ = Cp⁰ − R
    Cp = Cv − T·(∂P/∂T)_V² / (∂P/∂V)_T
    μJT = [T(∂V/∂T)_P − V]/Cp,   (∂V/∂T)_P = −(∂P/∂T)_V/(∂P/∂V)_T
    u = √[ −(V²/M)·(Cp/Cv)·(∂P/∂V)_T ]

a(T) es el parámetro de atracción de la mezcla con la misma regla de mezcla
del flash (clásica, o Huron-Vidal con agua); sus derivadas en T se obtienen
por diferencias centrales.  Con traslado de volumen de Peneloux (c constante)
V se reemplaza por V − c en μJT, u y el volumen molar; Cp y Cv no cambian.

Unidades internas: psia, ft³/lbmol, °R.
"""
import math

R_GAS = 10.7316                    # psia·ft³/(lbmol·°R)
_J_POR_U = 6894.757293168*0.028316846592*1.8/453.59237   # psia·ft³/(lbmol·°R) → J/(mol·K)
_M2S2_POR_U = 6894.757293168*0.028316846592/0.45359237   # psia·ft³/lb → m²/s²
_JT_U = 14.503773773/1.8                                   # °R/psia → °C/bar
_CM3MOL_POR_FT3LBMOL = 62.427960576                        # ft³/lbmol → cm³/mol


def _cp0_mezcla(comp, T_R, eos):
    """Cp⁰ de la mezcla [J/(mol·K)] con los polinomios de la base de la EOS."""
    import entalpia_entropia_gen as _hs
    T_K = T_R/1.8
    s = 0.0
    nhc = len(_hs.CP_REID)
    for i, x in enumerate(comp):
        if x <= 0:
            continue
        if i < nhc:
            s += x*_hs.cp_ideal(i, T_K, eos)
        else:                                   # agua (índice 13)
            import propiedades_agua as _pa
            c = _pa._cp_agua(eos)
            s += x*(c[0] + c[1]*T_K + c[2]*T_K**2 + c[3]*T_K**3)
    return s


def _funcion_a(comp, eos, kij=None):
    """Devuelve (a(T), b, δ1, δ2) con la regla de mezcla del flash."""
    import eos as _e
    d1, d2 = (1.0, 0.0) if _e.es_srk(eos) else (1.0 + math.sqrt(2.0), 1.0 - math.sqrt(2.0))
    if len(comp) > _e.NC and comp[_e.NC] > 0:
        import propiedades_agua as _pa
        def a_de_T(T):
            am, _bm = _pa._am_bm_14(list(comp), T, eos)
            return float(am)
        _am0, bm = _pa._am_bm_14(list(comp), 500.0, eos)
        return a_de_T, float(bm), d1, d2
    import entalpia_entropia_gen as _hs
    c13 = list(comp[:_e.NC])
    s = sum(c13)
    c13 = [v/s for v in c13] if s > 0 else c13

    def a_de_T(T):
        return _hs._params_eos(c13, T, eos, kij)[0]
    bm = _hs._params_eos(c13, 500.0, eos, kij)[1]
    return a_de_T, bm, d1, d2


def propiedades_fase(comp, T_R, P, Z, PM, eos, kij=None, c_pen=0.0):
    """Cp, Cv [J/(mol·°C)], kappa, JT [°C/bar], u [m/s] y V [cm³/mol] de una
    fase de composición `comp` (13 ó 14 componentes) con factor Z de la EOS
    (sin traslado).  c_pen: traslado de Peneloux de la fase [ft³/lbmol]."""
    if Z is None or Z <= 0 or PM is None or PM <= 0:
        return None
    try:
        a_de_T, b, d1, d2 = _funcion_a(comp, eos, kij)
        h = max(1e-3*T_R, 0.05)
        a0 = a_de_T(T_R); ap = a_de_T(T_R + h); am_ = a_de_T(T_R - h)
        a1 = (ap - am_)/(2*h)
        a2 = (ap - 2*a0 + am_)/(h*h)
        V = Z*R_GAS*T_R/P
        q1 = V + d1*b; q2 = V + d2*b
        dPdT = R_GAS/(V - b) - a1/(q1*q2)
        dPdV = -R_GAS*T_R/(V - b)**2 + a0*(2*V + (d1 + d2)*b)/(q1*q2)**2
        Cv_res = T_R*a2/((d1 - d2)*b)*math.log(q1/q2)          # psia·ft³/(lbmol·°R)
        Cp0 = _cp0_mezcla(comp, T_R, eos)                       # J/(mol·K)
        Rj = R_GAS*_J_POR_U
        Cv = (Cp0 - Rj) + Cv_res*_J_POR_U
        Cp = Cv - T_R*dPdT**2/dPdV*_J_POR_U
        Cp_u = Cp/_J_POR_U
        import eos as _e
        # volumen con la convención de unidades de PVTsim (R en atm) y traslado
        Vr = (V - c_pen)/_e.factor_rho(eos)
        dVdT = -dPdT/dPdV/_e.factor_rho(eos)
        JT = (T_R*dVdT - Vr)/Cp_u*_JT_U
        u2 = -(Vr*Vr/PM)*(Cp/Cv)*dPdV*_M2S2_POR_U
        u = math.sqrt(u2) if u2 > 0 else None
        return {'Cp': Cp, 'Cv': Cv, 'kappa': Cp/Cv, 'JT': JT, 'u': u,
                'Vm': Vr*_CM3MOL_POR_FT3LBMOL}
    except Exception:
        return None

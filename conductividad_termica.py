# -*- coding: utf-8 -*-
"""
conductividad_termica.py — Conductividad térmica de las fases de hidrocarburo.

Dos métodos, que acompañan al método de viscosidad elegido:

1) Tipo LBC (con la viscosidad LBC):
       λ = λ_traslación + λ_interna
       λ_tr  = C1·T^C2·P^C3·(a1 + a2ρr + a3ρr² + a4ρr³ + a5ρr⁴)
       λ_int = 1.1865·ζ·(Cp⁰ − 2.5R)·f(ρr)/M̄n
       f(ρr) = 1 + 0.053432ρr − 0.030182ρr² − 0.029725ρr³
   T en K, P en atm, ζ la viscosidad de gas diluido de la mezcla (cP, Stiel-
   Thodos + Herning-Zipperer, la misma de LBC), ρr la densidad reducida de LBC
   y M̄n el peso molecular medio.  λ en mW/(m·K).

2) Estados correspondientes (con la viscosidad CSP), Christensen y
   Fredenslund (1980) / Pedersen y Fredenslund (1987), metano de referencia
   (Hanley et al. 1975):
       λ_mix = (Tc,mix/Tco)^(−1/6)(Pc,mix/Pco)^(2/3)(M_mix/Mo)^(−1/2)
               ·(α_mix/α_o)·[λ_o(To,Po) − λ_int,o(To)] + λ_int,mix(T)

Unidades internas de salida: mW/(m·K).
"""
import math
import numpy as np

R_PVT = 0.08206*101.325        # J/(mol·K), la de PVTsim

_C1, _C2, _C3 = 2.30528, -0.59394, 0.06928
_A = (270.28341, -148.95858, 408.63577, -127.74598, 13.52979)


def _f_rho(rr):
    return 1.0 + 0.053432*rr - 0.030182*rr**2 - 0.029725*rr**3


def conductividad_LBC(comp, T_R, P, Z, eos=None):
    """λ (mW/(m·K)) por el método tipo LBC.  Z es el factor de compresibilidad
    equivalente a la densidad de la fase (el mismo que usa la viscosidad)."""
    import eos as _e
    import propiedades_termicas as _pt
    e = eos if eos is not None else _e.get_eos()
    comp = np.asarray(comp, dtype=float)
    n = len(comp)
    if n > _e.NC:
        import propiedades_agua as _pa
        Tc, Pc, M, Vc = _pa._lbc_params14(e)
    else:
        Tc, Pc, M, Vc = _e._lbc_params(e)
    Tc = np.asarray(Tc)[:n]; Pc = np.asarray(Pc)[:n]; M = np.asarray(M)[:n]; Vc = np.asarray(Vc)[:n]
    m = comp > 0
    z = comp[m]; z = z/z.sum()
    Tc, Pc, M, Vc = Tc[m], Pc[m], M[m], Vc[m]
    TK = T_R/1.8
    Patm = P/_e.PSIA_ATM_PVT
    rr = Patm*float(np.sum(z*Vc))/(Z*TK)
    xi = Tc**(1.0/6.0)/(np.sqrt(M)*Pc**(2.0/3.0))
    Tr = TK/Tc
    eps = np.where(Tr <= 1.5, _e._ST_C_BAJA*Tr**0.94,
                   17.78e-5*np.abs(4.58*Tr - 1.67)**0.625)/xi
    sM = np.sqrt(M)
    zeta = float(np.sum(z*eps*sM)/np.sum(z*sM))
    Mn = float(np.sum(z*M))
    cp0 = _pt._cp0_mezcla(list(comp), T_R, e)
    l_int = 1000.0*1.1865*zeta*(cp0 - 2.5*R_PVT)*_f_rho(rr)/Mn
    poly = sum(a*rr**k for k, a in enumerate(_A))
    l_tr = _C1*TK**_C2*Patm**_C3*poly
    return l_int + l_tr


# ── Estados correspondientes ───────────────────────────────────────────────
_GT = (None, -2.147621e5, 2.190461e5, -8.618097e4, 1.496099e4, -4.730660e2,
       -2.331178e2, 3.778439e1, -2.320481, 5.311764e-2)
_LA, _LB, _LC, _LF = -0.25276292, 0.33432859, 1.12, 168.0
_L = (None, -7.0403639907, 12.319512908, -885.25979933, 72.835897919,
      0.74421462902, -2.9706914540, 2220.9758501)
_M = (None, -8.55109, 12.5539, -1020.85, 238.394, 1.31563, -72.5759, 1411.60)


def _lambda_metano(T, P_atm, fase=None):
    """λ del metano (mW/(m·K)) por Hanley et al. (1975) con el término de baja
    temperatura de Pedersen y Fredenslund (1987); sin término crítico."""
    import viscosidad_csp as _v
    r = _v.densidad_metano(T, P_atm, fase)*_v.M_C1/1000.0     # g/cm³
    l0 = sum(_GT[i]*T**((i - 4)/3.0) for i in range(1, 10))
    l1 = _LA + _LB*(_LC - math.log(T/_LF))**2
    th = (r - _v.RHO_C_C1)/_v.RHO_C_C1
    r01 = r**0.1; r05 = math.sqrt(r)
    d1 = math.exp(_L[1] + _L[4]/T)*(math.exp(min(700.0, r01*(_L[2] + _L[3]/T**1.5)
                                   + th*r05*(_L[5] + _L[6]/T + _L[7]/T**2))) - 1.0)
    d2 = math.exp(_M[1] + _M[4]/T)*(math.exp(min(700.0, r01*(_M[2] + _M[3]/T**1.5)
                                   + th*r05*(_M[5] + _M[6]/T + _M[7]/T**2))) - 1.0)
    ht = math.tanh((T - _v.T_FUSION_C1)/_v.ANCHO_FUSION)
    F1 = 0.5*(1.0 + ht); F2 = 0.5*(1.0 - ht)
    return l0 + l1*r + F1*d1 + F2*d2, r


def _cp0_metano(T_K, eos):
    import entalpia_entropia_gen as _hs
    return _hs.cp_ideal(2, T_K, eos)


def conductividad_CSP(comp, T_R, P, eos=None, fase=None):
    """λ (mW/(m·K)) por estados correspondientes (metano de referencia)."""
    import eos as _e
    import viscosidad_csp as _v
    import propiedades_termicas as _pt
    e = eos if eos is not None else _e.get_eos()
    comp = list(comp)
    Tc_l, Pc_l, M_l = _v._props(e, len(comp))
    z = np.asarray(comp, dtype=float); msk = z > 0
    z = z[msk]/z[msk].sum()
    Tc = np.asarray(Tc_l)[msk]; Pc = np.asarray(Pc_l)[msk]; Mi = np.asarray(M_l)[msk]
    Tco, Pco, Mo = Tc_l[2], Pc_l[2], M_l[2]
    TK = T_R/1.8; Patm = P/14.69595

    s = (Tc/Pc)**(1.0/3.0)
    V = (s[:, None] + s[None, :])**3
    Tij = np.sqrt(Tc[:, None]*Tc[None, :])
    zz = z[:, None]*z[None, :]
    num = float(np.sum(zz*V*Tij)); den = float(np.sum(zz*V))
    Tcm = num/den; Pcm = 8.0*num/den**2
    # M_mix por Chapman-Enskog (Murad y Gubbins).  La constante se toma de
    # modo que un componente puro dé su propio peso molecular (con 1/16, como
    # aparece impreso, el límite de componente puro daría M/2).
    w = np.sqrt(1.0/Mi[:, None] + 1.0/Mi[None, :])*(Tc[:, None]*Tc[None, :])**0.25
    Mmix = (1.0/8.0)*(float(np.sum(zz*w/(s[:, None] + s[None, :])**2))**-2) \
        * Tcm**(-1.0/3.0)*Pcm**(4.0/3.0)
    # α por componente y de la mezcla
    alfa_i = []
    for Tci, Pci, Mi_ in zip(Tc, Pc, Mi):
        rri = _v.densidad_metano(TK*Tco/Tci, Patm*Pco/Pci, fase)*Mo/1000.0/_v.RHO_C_C1
        alfa_i.append(1.0 + 0.0006004*rri**2.043*Mi_**1.086)
    alfa_i = np.asarray(alfa_i)
    a_mix = float(np.sum(zz*np.sqrt(alfa_i[:, None]*alfa_i[None, :])))
    rr = _v.densidad_metano(TK*Tco/Tcm, Patm*Pco/Pcm, fase)*Mo/1000.0/_v.RHO_C_C1
    a_o = 1.0 + 0.0006004*rr**2.043*Mo**1.086

    To = TK*Tco*a_o/(Tcm*a_mix)
    Po = Patm*Pco*a_o/(Pcm*a_mix)
    lam_o, r_o = _lambda_metano(To, Po, fase)
    # contribuciones internas (manual de PVTsim): η* es la viscosidad del GAS a
    # la temperatura de cálculo y 1 atm — para el metano de referencia a To y
    # para la mezcla a T, ambas por el modelo de viscosidad CSP con el estado
    # gaseoso de la referencia.
    eta_o = _v.viscosidad_metano(To, 1.0, 'V')
    l_int_o = 1000.0*1.18653*eta_o*(_cp0_metano(To, e) - 2.5*R_PVT) \
        * _f_rho(r_o/_v.RHO_C_C1)/Mo
    Mn = float(np.sum(z*Mi))
    Mw = float(np.sum(z*Mi**2)/np.sum(z*Mi))
    eta_m = _v.viscosidad_CSP(comp, TK, 1.0, Tc_l, Pc_l, M_l, fase='V')
    cp0 = _pt._cp0_mezcla(comp, T_R, e)
    l_int_m = 1000.0*1.18653*eta_m*(cp0 - 2.5*R_PVT)*_f_rho(rr)/Mn
    fac = (Tcm/Tco)**(-1.0/6.0)*(Pcm/Pco)**(2.0/3.0)*(Mmix/Mo)**(-0.5)*(a_mix/a_o)
    return float(fac*(lam_o - l_int_o) + l_int_m)


def conductividad_fase(comp, T_R, P, Z, eos=None, fase=None):
    """λ (mW/(m·K)) con el método que acompaña a la viscosidad activa."""
    import eos as _e
    try:
        if _e.get_metodo_viscosidad() == 'CSP':
            return conductividad_CSP(comp, T_R, P, eos, fase)
        return conductividad_LBC(comp, T_R, P, Z, eos)
    except Exception:
        return None

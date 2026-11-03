# -*- coding: utf-8 -*-
"""
viscosidad_csp.py — Viscosidad por ESTADOS CORRESPONDIENTES (CSP)
(Pedersen et al. 1984, 1987; Lindeloff et al. 2004), método por defecto de
PVTsim para las fases de hidrocarburo.

    η_mix(P,T) = (Tc,mix/Tco)^(-1/6)·(Pc,mix/Pco)^(2/3)·(M_mix/Mo)^(1/2)
                 ·(α_mix/α_o)·η_o(Po, To)

    Po = P·Pco·α_o/(Pc,mix·α_mix) ;  To = T·Tco·α_o/(Tc,mix·α_mix)

  • Referencia: METANO.  Densidad por la BWR de McCarty (1974) y viscosidad
    por Hanley, McCarty & Haynes (1975), con el término Δη'' de Pedersen &
    Fredenslund (1987) para metano sólido en el estado de referencia
    (T_F = 90.69 K, mezcla con tangente hiperbólica, ΔT = (T−T_F)/5).
  • Reglas de mezcla de Murad & Gubbins (1977) para Tc,mix y Pc,mix.
  • M_mix = 1.304e-4·(M̄w^2.303 − M̄n^2.303) + M̄n.
  • α = 1 + 7.378e-3·ρr^1.847·M^0.5173 (mezcla con M_mix, metano con Mo),
    ρr = ρ_metano(T·Tco/Tc,mix, P·Pco/Pc,mix)/ρco, ρco = 0.16284 g/cm³.
  • Aceites pesados (Lindeloff et al. 2004): si To < 75 K se combina con la
    correlación de Rønningsen (1993); bajo 50 K se usa sólo ésta.

Las propiedades de componente (Tc, Pc, M) son las de la base de datos de la
EOS activa (PVTsim o HYSYS).  Unidades internas: T en K, P en atm, ρ metano
en mol/L (BWR) y g/cm³ (Hanley); viscosidad en cP.
"""
import math
import numpy as np

# ── Metano: referencia ──────────────────────────────────────────────────────
M_C1 = 16.043
RHO_C_C1 = 0.16284            # g/cm³  (densidad crítica del metano)
T_FUSION_C1 = 90.69           # K
ANCHO_FUSION = 5.0            # K, ancho de la transición tanh
R_BWR = 0.08205616            # L·atm/(mol·K)
GAMMA_BWR = 0.0096

# BWR de McCarty (1974): constantes N1..N32 (P atm, ρ mol/L, T K)
_N = (None,
      -1.8439486666e-2, 1.0510162064, -1.6057820303e1, 8.4844027563e2,
      -4.2738409106e4, 7.6565285254e-4, -4.8360724197e-1, 8.5195473835e1,
      -1.6607434721e4, -3.7521074532e-5, 2.8616309259e-2, -2.8685298973,
      1.1906973942e-4, -8.5315715698e-3, 3.8365063841, 2.4986828379e-5,
      5.7974531455e-6, -7.1648329297e-3, 1.2577853784e-4, 2.2240102466e4,
      -1.4800512328e6, 5.0498054887e1, 1.6428375992e6, 2.1325387196e-1,
      3.7791273422e1, -1.1857016815e-5, -3.1630780767e1, -4.1006782941e-6,
      1.4870043284e-3, 3.1512261532e-9, -2.1670774745e-6, 2.4000551079e-5)

# Hanley et al. (1975), viscosidad en μP (= 1e-4 cP), ρ en g/cm³
_GV = (None, -2.090975e5, 2.647269e5, -1.472818e5, 4.716740e4, -9.491872e3,
       1.219979e3, -9.627993e1, 4.274152, -8.141531e-2)
_HA, _HB, _HC, _HF = 1.696985927, -0.133372346, 1.4, 168.0
_J = (None, -10.3506, 17.5716, -3019.39, 188.730, 0.0429036, 145.290, 6127.68)
_K = (None, -9.74602, 18.0834, -4126.66, 44.6055, 0.976544, 81.8134, 15649.9)


def _bwr_coef(T):
    N = _N
    a = [0.0]*16
    a[1] = R_BWR*T
    a[2] = N[1]*T + N[2]*math.sqrt(T) + N[3] + N[4]/T + N[5]/T**2
    a[3] = N[6]*T + N[7] + N[8]/T + N[9]/T**2
    a[4] = N[10]*T + N[11] + N[12]/T
    a[5] = N[13]
    a[6] = N[14]/T + N[15]/T**2
    a[7] = N[16]/T
    a[8] = N[17]/T + N[18]/T**2
    a[9] = N[19]/T**2
    a[10] = N[20]/T**2 + N[21]/T**3
    a[11] = N[22]/T**2 + N[23]/T**4
    a[12] = N[24]/T**2 + N[25]/T**3
    a[13] = N[26]/T**2 + N[27]/T**4
    a[14] = N[28]/T**2 + N[29]/T**3
    a[15] = N[30]/T**2 + N[31]/T**3 + N[32]/T**4
    return a


def _bwr_P(r, a):
    """Presión (atm) de la BWR de McCarty a densidad r (mol/L)."""
    s = 0.0
    rn = r
    for n in range(1, 10):
        s += a[n]*rn
        rn *= r
    e = math.exp(-GAMMA_BWR*r*r)
    for n in range(10, 16):
        s += e*a[n]*r**(2*n - 17)
    return s


# Gauss-Legendre para la integral de la energía libre residual
_GL_X, _GL_W = np.polynomial.legendre.leggauss(48)


def _mu_residual(r, T, a):
    """Potencial químico/RT (salvo función de T) a densidad r:
       ln r + ∫0^r (P − ρRT)/(ρ²RT) dρ + P/(rRT)."""
    RT = R_BWR*T
    x = 0.5*r*(_GL_X + 1.0)
    w = 0.5*r*_GL_W
    integ = 0.0
    for xi, wi in zip(x, w):
        integ += wi*(_bwr_P(xi, a) - xi*RT)/(xi*xi)
    return math.log(r) + integ/RT + _bwr_P(r, a)/(r*RT)


def densidad_metano(T, P_atm, fase=None):
    """Densidad del metano (mol/L) por la BWR de McCarty a (T [K], P [atm]).
    Entre varias raíces mecánicamente estables se toma la de mayor densidad."""
    a = _bwr_coef(T)
    rs = np.concatenate([np.geomspace(1e-6, 1.0, 120), np.linspace(1.0, 40.0, 1560)[1:]])
    f = [_bwr_P(r, a) - P_atm for r in rs]
    raices = []
    for k in range(1, len(rs)):
        if f[k-1] == 0.0:
            raices.append(rs[k-1]); continue
        if f[k-1]*f[k] < 0:
            lo, hi = rs[k-1], rs[k]
            flo = f[k-1]
            for _ in range(80):
                m = 0.5*(lo + hi)
                fm = _bwr_P(m, a) - P_atm
                if flo*fm <= 0:
                    hi = m
                else:
                    lo, flo = m, fm
                if hi - lo < 1e-12*max(1.0, hi):
                    break
            r = 0.5*(lo + hi)
            h = 1e-6*max(r, 1e-6)
            if _bwr_P(r + h, a) - _bwr_P(r - h, a) > 0:   # dP/dρ > 0
                raices.append(r)
    if not raices:
        # P fuera del alcance de la malla (sólo a muy alta presión)
        return float(rs[-1]) if f[-1] < 0 else float(rs[0])
    if len(raices) == 1:
        return raices[0]
    if fase == 'V':
        # fase gaseosa: estado de referencia gaseoso (raíz de menor densidad)
        return min(raices)
    # Como PVTsim, el estado de referencia toma la raíz de mayor densidad
    # (metano líquido en el estado correspondiente de una fase densa); validado
    # contra sus corridas CS (con la de menor Gibbs el líquido pesado a baja
    # presión salía hasta 90 % bajo).
    return max(raices)


def _eta_hanley(rho_g, T):
    """Viscosidad del metano (cP) por Hanley et al. (1975) con el término de
    metano sólido de Pedersen & Fredenslund (1987).  rho_g en g/cm³."""
    e0 = 0.0
    for i in range(1, 10):
        e0 += _GV[i]*T**((i - 4)/3.0)
    e1 = (_HA + _HB*(_HC - math.log(T/_HF))**2)*rho_g
    th = (rho_g - RHO_C_C1)/RHO_C_C1
    r01 = rho_g**0.1
    r05 = math.sqrt(rho_g)
    J, K = _J, _K
    d1 = math.exp(J[1] + J[4]/T)*(math.exp(min(700.0, r01*(J[2] + J[3]/T**1.5)
                                  + th*r05*(J[5] + J[6]/T + J[7]/T**2))) - 1.0)
    d2 = math.exp(K[1] + K[4]/T)*(math.exp(min(700.0, r01*(K[2] + K[3]/T**1.5)
                                  + th*r05*(K[5] + K[6]/T + K[7]/T**2))) - 1.0)
    dT = (T - T_FUSION_C1)/ANCHO_FUSION
    ht = math.tanh(dT)
    F1 = 0.5*(ht + 1.0); F2 = 0.5*(1.0 - ht)
    return (e0 + e1 + F1*d1 + F2*d2)*1e-4


def viscosidad_metano(T, P_atm, fase=None):
    """Viscosidad del metano de referencia (cP) a (T [K], P [atm])."""
    r = densidad_metano(T, P_atm, fase)
    return _eta_hanley(r*M_C1/1000.0, T)


def _alfa(rho_r, M):
    return 1.0 + 7.378e-3*rho_r**1.847*M**0.5173


def _ronningsen(T, P_atm, Mn, Mw, f3=1.0, f4=1.0):
    """Correlación de aceite estabilizado (Rønningsen 1993) adaptada por
    Lindeloff et al. (2004), con corrección de presión.  cP."""
    vf3 = 0.2252*(T/Mn) + 0.9738
    vf4 = 0.5354*vf3 - 0.1170
    if Mw/Mn <= 1.5:
        M = Mn*(1.5/(vf3*f3))**(vf4*f4)
    else:
        M = Mn*(Mw/(vf3*f3*Mn))**(vf4*f4)
    c = -0.01101 if T <= 564.49 else 0.01101
    log_eta = -0.07995 + c*M - 371.8/T + 6.215*M/T
    eta0 = 10.0**log_eta
    return eta0*math.exp(0.00384*(P_atm**0.8226 - 1.0)/0.8226)


def viscosidad_CSP(z, T_K, P_atm, Tc_K, Pc_atm, M, i_c1=2,
                   csp1=1.0, csp2=1.0, csp3=1.0, csp4=1.0, fase=None):
    """Viscosidad (cP) de una fase de composición z por estados
    correspondientes.  Tc_K, Pc_atm, M: propiedades de cada componente (base
    de datos de la EOS); i_c1: índice del metano (referencia)."""
    z = np.asarray(z, dtype=float)
    m = z > 0
    if not np.any(m):
        return None
    z = z[m]/z[m].sum()
    Tc = np.asarray(Tc_K, dtype=float)[m]
    Pc = np.asarray(Pc_atm, dtype=float)[m]
    Mi = np.asarray(M, dtype=float)[m]
    Tco = float(Tc_K[i_c1]); Pco = float(Pc_atm[i_c1]); Mo = float(M[i_c1])

    # Murad & Gubbins
    s = (Tc/Pc)**(1.0/3.0)
    V = (s[:, None] + s[None, :])**3
    Tij = np.sqrt(Tc[:, None]*Tc[None, :])
    zz = z[:, None]*z[None, :]
    num = float(np.sum(zz*V*Tij))
    den = float(np.sum(zz*V))
    Tcm = num/den
    Pcm = 8.0*num/den**2

    Mw = float(np.sum(z*Mi**2)/np.sum(z*Mi))
    Mn = float(np.sum(z*Mi))
    Mmix = 1.304e-4*csp1*(Mw**(2.303*csp2) - Mn**(2.303*csp2)) + Mn

    # densidad reducida en el estado correspondiente del metano
    Tr0 = T_K*Tco/Tcm
    Pr0 = P_atm*Pco/Pcm
    rho_r = densidad_metano(Tr0, Pr0, fase)*Mo/1000.0/RHO_C_C1
    a_mix = _alfa(rho_r, Mmix)
    a_o = _alfa(rho_r, Mo)

    To = T_K*Tco*a_o/(Tcm*a_mix)
    Po = P_atm*Pco*a_o/(Pcm*a_mix)
    fac = (Tcm/Tco)**(-1.0/6.0)*(Pcm/Pco)**(2.0/3.0)*(Mmix/Mo)**0.5*(a_mix/a_o)

    def _csp():
        return float(fac*viscosidad_metano(To, Po, fase))

    if To >= 75.0:
        return _csp()
    eta_h = _ronningsen(T_K, P_atm, Mn, Mw, csp3, csp4)
    if To < 50.0:
        return float(eta_h)
    ht = math.tanh((To - 70.0)/5.0)
    F1 = 0.5*(ht + 1.0); F2 = 0.5*(1.0 - ht)
    return float(F1*_csp() + F2*eta_h)


# ── Interfaz con el motor (unidades internas de ThermoPhase) ────────────────
def _props(eos, n):
    import eos as _e
    tc, pc, _om, pm = _e.crit_props(eos)
    Tc = list(np.asarray(tc, dtype=float)/1.8)
    Pc = list(np.asarray(pc, dtype=float)/14.69595)
    M = list(np.asarray(pm, dtype=float))
    if n > len(Tc):
        import flash_agua as _fa
        Tc14, Pc14, _o, PM14, _k = _fa._params_14(eos)
        Tc = list(np.asarray(Tc14, dtype=float)/1.8)
        Pc = list(np.asarray(Pc14, dtype=float)/14.69595)
        M = list(np.asarray(PM14, dtype=float))
    return Tc[:n], Pc[:n], M[:n]


def viscosidad_fase(comp, T_R, P_psia, eos=None, fase=None):
    """Viscosidad CSP (cP) de una fase (13 ó 14 componentes) a (T °R, P psia)
    con las propiedades de componente de la EOS indicada (o la activa)."""
    import eos as _e
    e = eos if eos is not None else _e.get_eos()
    comp = list(comp)
    Tc, Pc, M = _props(e, len(comp))
    try:
        return viscosidad_CSP(comp, T_R/1.8, P_psia/14.69595, Tc, Pc, M, fase=fase)
    except Exception:
        return None

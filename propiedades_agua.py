# -*- coding: utf-8 -*-
"""
propiedades_agua.py — Propiedades por fase del flash TRIFÁSICO (V–L–Acuosa).

Extiende a la FASE ACUOSA (agua, índice 13) las mismas propiedades que
ThermoPhase ya calcula para vapor y líquido en el flash bifásico:

    • Peso molecular            PM      (Σ x_i·PM_i)
    • Factor de compresibilidad Z       (raíz de la EOS que usó el flash)
    • Densidad másica           ρ       (lb/ft³, método de la EOS)
    • Gravedad específica       sg      (ρ/62.4 líquidos, PM/28.9625 gas)
    • Viscosidad                μ       (cP, Lohrenz-Bray-Clark)
    • Entalpía molar            H       (BTU/lbmol, Reid Cp⁰ + partida EOS)
    • Entropía molar            S       (BTU/lbmol·R)

Criterios (idénticos a los del motor de ThermoPhase, extendidos a 14 comp.):

  – Vapor y líquido HC:  el agua en estas fases es TRAZA (p.ej. y_H2O≈4e-6),
    de modo que sus propiedades se calculan renormalizando sobre los 13 HC y
    reutilizando EXACTAMENTE el motor existente (eos.py + entalpia_entropia_gen),
    por lo que coinciden al bit con el caso sin agua.

  – Fase acuosa:  dominada por agua (>99%). Se usa la densidad de la EOS con
    los parámetros del agua (ρ = P·PM/(Z·R·T)) —el método por defecto de
    ThermoPhase cuando COSTALD no aplica (COSTALD no tiene datos del agua)—,
    LBC y la entalpía/entropía Reid+partida sobre los 14 componentes.

Todo se calcula con el MISMO conjunto de parámetros (Tc, Pc, ω, kij) y la
misma regla de mezcla (Huron-Vidal / clásica) que empleó el flash, para que
las propiedades sean termodinámicamente consistentes con el equilibrio.
"""

import math
import numpy as np

R_GAS = 10.7316            # psia·ft³/(lbmol·°R)
IDX_AGUA = 13
NC = 13                   # componentes hidrocarburos

# ── Parámetros del agua (coherentes con flash_agua) ─────────────────────────
AGUA_PM  = 18.015100479126
AGUA_VC  = 55.9           # cm³/mol (volumen crítico del agua)
# COSTALD del agua: HYSYS toma por defecto V*_CTD = Vc y ω_CTD = ω_SRK
# (manual HYSYS: VSTCTD default = VC, OMGCTD default = OMEGA).  Con esos
# valores COSTALD reproduce la densidad del agua líquida a ~0.4 % (62.6 vs
# 62.4 lb/ft³ a 60 °F), muy superior a la densidad de la EOS cúbica.
AGUA_VSTAR = 55.9*0.0160185   # V* del agua (ft³/lbmol) = Vc convertido
AGUA_OMEGA_SRK_C = 0.34400001168251
# Cp⁰ del agua, polinomio de Reid, Prausnitz & Sherwood (1977) [J/(mol·K)],
# T en K:  Cp⁰ = C1 + C2·T + C3·T² + C4·T³
CP_REID_AGUA = (3.224e+1, 1.924e-3, 1.055e-5, -3.596e-9)

# Constantes de la ruta H/S (idénticas a entalpia_entropia_gen)
R_BTU  = 1.98588
CONV   = 144.0/778.169
PREF   = 14.696
TREF_K = 273.15
J_TO_BTUlbmol  = 453.59237/1055.05585
J_TO_BTUlbmolR = J_TO_BTUlbmol*(5.0/9.0)
SQRT2  = math.sqrt(2.0)

# VC extendido a 14 componentes (13 HC de eos.py + agua)
def _vc14():
    import eos as _e
    return np.array(list(_e.VC) + [AGUA_VC], dtype=float)


# ════════════════════════════════════════════════════════════════════════════
# Densidad
# ════════════════════════════════════════════════════════════════════════════
def _rho_eos(comp, PM_fase, Z, T, P):
    """Densidad másica por la EOS (lb/ft³):  ρ = P·PM/(Z·R·T)."""
    if Z is None or Z <= 0 or PM_fase is None or PM_fase <= 0:
        return None
    return P*PM_fase/(Z*R_GAS*T)


def _vstar_om14():
    """V*_COSTALD (ft³/lbmol) y ω_SRK de 14 comp. (13 HC de eos.py + agua)."""
    import eos as _e
    vstar = list(_e.VSTAR_COSTALD) + [AGUA_VSTAR]
    omega = list(_e.OMEGA_SRK)     + [AGUA_OMEGA_SRK_C]
    return np.array(vstar, dtype=float), np.array(omega, dtype=float)


def _costald_Vs14(comp, T, TC14):
    """Volumen molar de líquido saturado por COSTALD sobre 14 componentes.

    Usa la MISMA regla de mezcla de Hankinson-Thomson que el motor de 13 comp.,
    de modo que los hidrocarburos/CO₂ disueltos en la fase acuosa SÍ entran en
    el cálculo de la densidad (igual que en la fase líquida HC).  Devuelve None
    fuera del rango de validez de COSTALD (Tr ≥ 1)."""
    vstar, omega = _vstar_om14()
    n = len(comp)
    s_xV   = sum(comp[i]*vstar[i]            for i in range(n))
    s_xV13 = sum(comp[i]*vstar[i]**(1/3.0)   for i in range(n))
    s_xV23 = sum(comp[i]*vstar[i]**(2/3.0)   for i in range(n))
    Vm_star = 0.25*(s_xV + 3.0*s_xV13*s_xV23)
    if Vm_star <= 0:
        return None
    num = 0.0
    for i in range(n):
        if comp[i] == 0: continue
        for j in range(n):
            if comp[j] == 0: continue
            num += comp[i]*comp[j]*math.sqrt(vstar[i]*TC14[i]*vstar[j]*TC14[j])
    Tcm = num/Vm_star
    omega_m = sum(comp[i]*omega[i] for i in range(n))
    Tr = T/Tcm
    if Tr >= 1.0:
        return None
    tau = 1.0 - Tr
    V0 = (1 - 1.52816*tau**(1/3.0) + 1.43907*tau**(2/3.0)
            - 0.81446*tau + 0.190454*tau**(4/3.0))
    Vd = ((-0.296123 + 0.386914*Tr - 0.0427258*Tr**2 - 0.0480645*Tr**3)
          / (Tr - 1.00001))
    Vs = Vm_star*V0*(1.0 - omega_m*Vd)
    return Vs if Vs > 0 else None


def _rho_costald14(comp, PM_fase, T, TC14, rho_eos):
    """Densidad másica de una fase líquida por COSTALD-14 (lb/ft³).

    Fuera del rango de COSTALD (Tr ≥ 1) devuelve la densidad de la EOS, igual
    que hace el motor para los hidrocarburos."""
    Vs = _costald_Vs14(comp, T, TC14)
    if Vs and Vs > 0 and PM_fase:
        return PM_fase/Vs
    return rho_eos


# ════════════════════════════════════════════════════════════════════════════
# Viscosidad Lohrenz-Bray-Clark extendida a 14 componentes (incluye agua)
# ════════════════════════════════════════════════════════════════════════════
_LBC_A = (0.10230, 0.023364, 0.058533, -0.040758, 0.0093324)
_CM3MOL_A_FT3LBMOL = 0.0160185

def _visc_gas_diluido(i, T_R, TC, PC, PM):
    Tc_K   = TC[i]/1.8
    Pc_atm = PC[i]/14.696
    xi_i   = (Tc_K**(1.0/6.0))/(PM[i]**0.5 * Pc_atm**(2.0/3.0))
    Tr_i   = (T_R/1.8)/Tc_K
    if Tr_i <= 1.5:
        return 34.0e-5*(Tr_i**0.94)/xi_i
    return 17.78e-5*(4.58*Tr_i - 1.67)**(5.0/8.0)/xi_i

def _visc_LBC14(comp, T_R, rho_masa, PM_fase, TC, PC, PM, VC):
    """Viscosidad de fase (cP) por LBC sobre 14 componentes."""
    if rho_masa is None or rho_masa <= 0 or PM_fase is None:
        return None
    z = comp
    n = len(z)
    eta_i = [(_visc_gas_diluido(i, T_R, TC, PC, PM) if z[i] != 0 else 0.0)
             for i in range(n)]
    num = sum(z[i]*eta_i[i]*PM[i]**0.5 for i in range(n) if z[i] != 0)
    den = sum(z[i]*PM[i]**0.5          for i in range(n) if z[i] != 0)
    if den <= 0:
        return None
    eta_star = num/den
    s_zTc = sum(z[i]*(TC[i]/1.8)    for i in range(n) if z[i] != 0)
    s_zM  = sum(z[i]*PM[i]          for i in range(n) if z[i] != 0)
    s_zPc = sum(z[i]*(PC[i]/14.696) for i in range(n) if z[i] != 0)
    xi = (s_zTc**(1.0/6.0))/(s_zM**0.5 * s_zPc**(2.0/3.0))
    Vc_m = sum(z[i]*VC[i]*_CM3MOL_A_FT3LBMOL for i in range(n) if z[i] != 0)
    rho_molar = rho_masa/PM_fase
    rho_r = rho_molar*Vc_m
    a1, a2, a3, a4, a5 = _LBC_A
    poly = a1 + a2*rho_r + a3*rho_r**2 + a4*rho_r**3 + a5*rho_r**4
    val = poly**4 - 1.0e-4
    if val < 0:
        val = 0.0
    return val/xi + eta_star


# ════════════════════════════════════════════════════════════════════════════
# Entalpía / entropía de la fase acuosa (14 componentes)
# ════════════════════════════════════════════════════════════════════════════
def _cp_ideal14(i, T_K):
    import entalpia_entropia_gen as _hs
    if i < NC:
        return _hs.cp_ideal(i, T_K)
    C1, C2, C3, C4 = CP_REID_AGUA
    return C1 + C2*T_K + C3*T_K**2 + C4*T_K**3

def _simpson(f, Ta, Tb, N=2000):
    if N % 2:
        N += 1
    h = (Tb - Ta)/N
    s = f(Ta) + f(Tb)
    for k in range(1, N, 2):
        s += 4.0*f(Ta + k*h)
    for k in range(2, N, 2):
        s += 2.0*f(Ta + k*h)
    return s*h/3.0

def _H_ideal14(i, T_R):
    T_K = T_R*5.0/9.0
    return _simpson(lambda T: _cp_ideal14(i, T), TREF_K, T_K)*J_TO_BTUlbmol

def _S_ideal14(i, T_R, P):
    T_K = T_R*5.0/9.0
    return (_simpson(lambda T: _cp_ideal14(i, T)/T, TREF_K, T_K)*J_TO_BTUlbmolR
            - R_BTU*math.log(P/PREF))

def _params_eos14(comp, T_R, eos, TC, PC, om, kij):
    """(am, bm, da/dT, d1, d2) de 14 componentes con regla clásica cuadrática
    para el término de partida (misma convención que entalpia_entropia_gen)."""
    import eos as _e
    es_srk = _e.es_srk(eos)
    if es_srk:
        ai = 0.42748*R_GAS**2*TC**2/PC; b0 = 0.08664
        m  = 0.480 + 1.574*om - 0.176*om**2
    else:
        ai = 0.45724*R_GAS**2*TC**2/PC; b0 = 0.07780
        m  = 0.37464 + 1.54226*om - 0.26992*om**2
    bi = b0*R_GAS*TC/PC
    sqrtTr = np.sqrt(T_R/TC)
    salpha = 1.0 + m*(1.0 - sqrtTr)
    aa = ai*salpha**2                                   # a_i·α(T)
    daa = ai*2.0*salpha*(-m/(2.0*np.sqrt(T_R*TC)))      # d(a_i·α)/dT
    d1, d2 = (1.0, 0.0) if es_srk else (1.0+SQRT2, 1.0-SQRT2)
    n = len(comp)
    am = 0.0; da_dT = 0.0
    for i in range(n):
        xi = comp[i]
        if xi == 0: continue
        for j in range(n):
            xj = comp[j]
            if xj == 0: continue
            f = 1.0 - kij[i][j]
            aij = math.sqrt(aa[i]*aa[j])*f
            am += xi*xj*aij
            if aa[i]*aa[j] > 0:
                daij = 0.5*aij*(daa[i]/aa[i] + daa[j]/aa[j])
                da_dT += xi*xj*daij
    bm = float(sum(comp[i]*bi[i] for i in range(n)))
    return am, bm, da_dT, d1, d2

def _H_fase14(comp, T_R, P, Z, eos, TC, PC, om, kij):
    am, bm, da_dT, d1, d2 = _params_eos14(comp, T_R, eos, TC, PC, om, kij)
    H_id = sum(comp[i]*_H_ideal14(i, T_R) for i in range(len(comp)) if comp[i] > 0)
    B  = bm*P/(R_GAS*T_R)
    lt = math.log((Z + d1*B)/(Z + d2*B))
    H_dep = R_BTU*T_R*(Z - 1.0) + ((T_R*da_dT - am)/((d1-d2)*bm))*lt*CONV
    return H_id + H_dep

def _S_fase14(comp, T_R, P, Z, eos, TC, PC, om, kij):
    am, bm, da_dT, d1, d2 = _params_eos14(comp, T_R, eos, TC, PC, om, kij)
    S_id = sum(comp[i]*_S_ideal14(i, T_R, P) for i in range(len(comp)) if comp[i] > 0)
    S_mix = 0.0
    for i in range(len(comp)):
        if comp[i] > 1e-15:
            S_mix -= R_BTU*comp[i]*math.log(comp[i])
    B  = bm*P/(R_GAS*T_R)
    lt = math.log((Z + d1*B)/(Z + d2*B))
    S_dep = R_BTU*math.log(Z - B) + (da_dT/((d1-d2)*bm))*lt*CONV
    return S_id + S_mix + S_dep


# ════════════════════════════════════════════════════════════════════════════
# API principal
# ════════════════════════════════════════════════════════════════════════════
def _norm13(comp14):
    """Renormaliza una composición de 14 comp. sobre los 13 HC (descarta agua)."""
    c = np.asarray(comp14, dtype=float)[:NC]
    s = c.sum()
    return (c/s) if s > 0 else c, s

def propiedades_fases(rt, T, P, eos, kij=None, metodo_densidad='EOS'):
    """Propiedades por fase (vapor, líquido, acuosa) del flash trifásico `rt`.

    Devuelve un dict con, por fase, PM/Z/rho(lb/ft³)/sg/mu(cP)/H/S(BTU/lbmol).
    Vapor y líquido HC se calculan con el motor de 13 comp. (idénticos al caso
    sin agua); la fase acuosa con los 14 comp. y parámetros del agua.
    """
    import eos as _e
    import flash_agua as _fa
    import entalpia_entropia_gen as _hs

    es_srk = _e.es_srk(eos)
    Tc14, Pc14, om14, PM14, kij14 = _fa._params_14(eos)
    VC14 = _vc14()

    y = rt.get('y'); x = rt.get('x'); w = rt.get('w')
    bV = rt.get('beta_V', 0.0); bL = rt.get('beta_L', 0.0); bW = rt.get('beta_W', 0.0)
    ZV = rt.get('Z_V'); ZL = rt.get('Z_L'); ZW = rt.get('Z_W')

    out = {'V': {}, 'L': {}, 'W': {}}

    # ── Vapor (renormalizado a 13 HC → motor existente) ──
    if bV > 1e-9 and y is not None:
        y13, _ = _norm13(y)
        PMv = float(np.dot(y, PM14))
        rho_v = _rho_eos(y, PMv, ZV, T, P)
        sg_v = PMv/28.9625
        mu_v = _visc_LBC14(list(y), T, rho_v, PMv, Tc14, Pc14, PM14, VC14)
        try:
            Hv = _hs.H_fase(list(y13), T, P, ZV, eos, kij)
            Sv = _hs.S_fase(list(y13), T, P, ZV, eos, kij)
        except Exception:
            Hv = Sv = None
        out['V'] = {'PM': PMv, 'Z': ZV, 'rho': rho_v, 'sg': sg_v,
                    'mu': mu_v, 'H': Hv, 'S': Sv}

    # ── Líquido HC ──
    if bL > 1e-9 and x is not None:
        x13, _ = _norm13(x)
        PMl = float(np.dot(x, PM14))
        rho_l_eos = _rho_eos(x, PMl, ZL, T, P)
        rho_l = rho_l_eos
        # Densidad de líquido con el método pedido (COSTALD sobre los 13 HC).
        if metodo_densidad == 'COSTALD':
            try:
                mix = _e._costald_mix_params(list(x13))
                if mix is not None:
                    Tcm = mix[0]; Tr = T/Tcm
                    PMl13 = float(sum(x13[i]*_e.PM[i] for i in range(NC)))
                    if Tr <= 0.95:
                        V_liq = _e.V_liq_costald_smooth(list(x13), T, P, kij=None)
                        if V_liq and V_liq > 0:
                            rho_l = PMl13/V_liq
                    elif Tr < 1.0:
                        V_cost = _e.V_liq_costald_smooth(list(x13), T, P, kij=None)
                        rho_cost = PMl13/V_cost if (V_cost and V_cost > 0) else rho_l_eos
                        frac = (Tr-0.95)/0.05; wgt = frac*frac
                        rho_l = (1.0-wgt)*rho_cost + wgt*rho_l_eos
            except Exception:
                rho_l = rho_l_eos
        sg_l = rho_l/62.4 if rho_l else None
        mu_l = _visc_LBC14(list(x), T, rho_l, PMl, Tc14, Pc14, PM14, VC14)
        try:
            Hl = _hs.H_fase(list(x13), T, P, ZL, eos, kij)
            Sl = _hs.S_fase(list(x13), T, P, ZL, eos, kij)
        except Exception:
            Hl = Sl = None
        out['L'] = {'PM': PMl, 'Z': ZL, 'rho': rho_l, 'sg': sg_l,
                    'mu': mu_l, 'H': Hl, 'S': Sl}

    # ── Fase acuosa (14 comp., parámetros del agua) ──
    if bW > 1e-9 and w is not None:
        PMw = float(np.dot(w, PM14))
        rho_w_eos = _rho_eos(w, PMw, ZW, T, P)
        rho_w = rho_w_eos
        # Con COSTALD activo, la fase acuosa usa COSTALD-14 sobre la
        # composición COMPLETA (agua + HC/CO₂ disueltos), igual que la fase
        # líquida HC. Fuera del rango de COSTALD cae a la densidad de la EOS.
        if metodo_densidad == 'COSTALD':
            rho_w = _rho_costald14(list(w), PMw, T, Tc14, rho_w_eos)
        sg_w = rho_w/62.4 if rho_w else None
        mu_w = _visc_LBC14(list(w), T, rho_w, PMw, Tc14, Pc14, PM14, VC14)
        try:
            Hw = _H_fase14(list(w), T, P, ZW, eos, Tc14, Pc14, om14, kij14)
            Sw = _S_fase14(list(w), T, P, ZW, eos, Tc14, Pc14, om14, kij14)
        except Exception:
            Hw = Sw = None
        out['W'] = {'PM': PMw, 'Z': ZW, 'rho': rho_w, 'sg': sg_w,
                    'mu': mu_w, 'H': Hw, 'S': Sw}

    return out

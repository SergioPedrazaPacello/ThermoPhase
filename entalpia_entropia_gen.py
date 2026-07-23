"""
entalpia_entropia_gen.py -- Entalpia y entropia molar GENERICAS (PR y SRK)

Metodo segun PVTsim Method Documentation, seccion "Thermal and Volumetric
Properties" (Enthalpy / Entropy), SIN offsets propios de HYSYS:

    H = SUM z_i H_id_i + H_res          H_id_i = INT[Tref->T] Cp_id_i dT
    S = SUM z_i S_id_i + S_res          S_id_i = INT[Tref->T] Cp_id_i/T dT
                                                 - R ln(P/Pref) - R ln(z_i)

Convenciones de PVTsim adoptadas:
  * Tref = 273.15 K (0 C / 32 F)   -- entalpias relativas al gas ideal a Tref
  * Pref = 1 atm = 14.696 psia
  * Cp_id = C1 + C2 T + C3 T^2 + C4 T^3  (polinomio de 3er grado),
    coeficientes de Reid, Prausnitz & Sherwood (1977).

Terminos residuales: PVTsim los obtiene de la EOS via
    H_res = -R T^2 (d ln phi / dT)_P        S_res = H_res/T - R ln phi
Aqui se usan las formas CERRADAS equivalentes (verificadas numericamente
contra la ruta de fugacidad: coinciden a ~1e-5 en PR y SRK).

Unidades (sistema ingles):
    H  ->  BTU/lbmol
    S  ->  BTU/(lbmol.R)
    T  ->  R   (interno)      P -> psia

La cubica se escribe en forma unificada
    P = RT/(V-b) - a(T) / [(V + d1 b)(V + d2 b)]
    PR :  d1 = 1+sqrt2 ,  d2 = 1-sqrt2   (d1-d2 = 2 sqrt2)
    SRK:  d1 = 1       ,  d2 = 0         (d1-d2 = 1)

Funciones de partida (identicas en forma para ambas EOS):
    H - H_ig = R T (Z-1) + (T da/dT - a)/[(d1-d2) b] . ln[(Z+d1 B)/(Z+d2 B)]
    S - S_ig = R ln(Z-B) +    (da/dT)  /[(d1-d2) b] . ln[(Z+d1 B)/(Z+d2 B)]
con B = bP/(RT).
"""

import math
import eos as eng

# --- Constantes / conversiones (sistema ingles) --------------------
R_BTU    = 1.98588            # BTU/(lbmol.R)
CONV     = 144.0 / 778.169    # 1 psi.ft3 -> BTU  = 0.185053
PREF     = 14.696             # 1 atm en psia (valor usado por PVTsim)
TREF_K   = 273.15             # K  (0 C / 32 F) -- referencia de PVTsim
J_TO_BTUlbmol = 453.59237 / 1055.05585  # 1 J/mol -> BTU/lbmol   = 0.429923
# 1 J/(mol.K) -> BTU/(lbmol.R):  (J/mol->BTU/lbmol) * (K->R factor 5/9)
J_TO_BTUlbmolR = J_TO_BTUlbmol * (5.0 / 9.0)             # = 0.238846
SQRT2    = math.sqrt(2.0)

# Cp0 gas ideal - polinomio de 3er grado usado por PVTsim:
#     Cp0 = C1 + C2 T + C3 T^2 + C4 T^3   [J/(mol.K)],  T en K
# Coeficientes de Reid, Prausnitz & Sherwood, "The Properties of Gases and
# Liquids" (1977) -- los que PVTsim carga por defecto en su base de datos.
# Orden canonico del motor: N2, CO2, C1, C2, C3, iC4, nC4, iC5, nC5, C6..C9.
CP_REID = [
    ( 3.115e+1, -1.357e-2,  2.680e-5, -1.168e-8),   # N2
    ( 1.980e+1,  7.344e-2, -5.602e-5,  1.715e-8),   # CO2
    ( 1.925e+1,  5.213e-2,  1.197e-5, -1.132e-8),   # C1
    ( 5.409e+0,  1.781e-1, -6.938e-5,  8.713e-9),   # C2
    (-4.224e+0,  3.063e-1, -1.586e-4,  3.215e-8),   # C3
    (-1.390e+0,  3.847e-1, -1.846e-4,  2.895e-8),   # iC4
    ( 9.487e+0,  3.313e-1, -1.108e-4, -2.822e-9),   # nC4
    (-9.525e+0,  5.066e-1, -2.729e-4,  5.723e-8),   # iC5
    (-3.626e+0,  4.873e-1, -2.580e-4,  5.305e-8),   # nC5
    (-4.413e+0,  5.820e-1, -3.119e-4,  6.494e-8),   # C6
    (-5.146e+0,  6.762e-1, -3.651e-4,  7.658e-8),   # C7
    (-6.096e+0,  7.712e-1, -4.195e-4,  8.855e-8),   # C8
    (-8.374e+0,  8.729e-1, -4.823e-4,  1.031e-7),   # C9
]

# Correlacion Aly-Lee (DIPPR 107) -- se conserva como alternativa/contraste.
CP_ALYLEE = [
    ( 29.11,   8.615,  1702.0,   0.1035,  909.8),   # N2
    ( 29.37,  34.54,   1428.0,  26.40,    588.0),   # CO2
    ( 33.30,  80.30,   2102.0,  42.13,    995.1),   # C1
    ( 40.23, 135.1,    1682.0,  75.74,    758.7),   # C2
    ( 51.92, 192.4,    1627.0, 116.8,     723.6),   # C3
    ( 65.49, 247.8,    1587.0, 157.5,    -707.0),   # iC4
    ( 71.34, 243.0,    1630.0, 150.3,    -730.4),   # nC4
    ( 74.60, 326.5,    1545.0, 192.3,     666.7),   # iC5
    ( 88.05, 301.1,    1650.0, 189.2,    -747.6),   # nC5
    (104.4,  352.3,    1695.0, 236.9,    -761.6),   # C6
    (120.2,  400.1,    1677.0, 274.0,    -756.4),   # C7
    (135.5,  443.1,    1636.0, 305.4,     746.4),   # C8
    (151.8,  491.5,    1645.0, 347.0,     749.6),   # C9
]


# ============================================================
# 1) PARTE DE GAS IDEAL  (unica para PR y SRK)
# ============================================================
def cp_ideal(i, T_K):
    """Cp0 del componente i [J/(mol.K)] a T en K.
    Polinomio de 3er grado con coeficientes de Reid et al. (1977), tal como
    lo usa PVTsim por defecto."""
    C1, C2, C3, C4 = CP_REID[i]
    return C1 + C2 * T_K + C3 * T_K ** 2 + C4 * T_K ** 3


def cp_ideal_alylee(i, T_K):
    """Cp0 por Aly-Lee (DIPPR 107) [J/(mol.K)] -- alternativa de contraste."""
    A, B, C, D, E = CP_ALYLEE[i]
    Ea = abs(E)
    return (A
            + B * (C / (T_K * math.sinh(C / T_K))) ** 2
            + D * (Ea / (T_K * math.cosh(Ea / T_K))) ** 2)


def _simpson(f, Ta, Tb, N=2000):
    if N % 2:
        N += 1
    h = (Tb - Ta) / N
    s = f(Ta) + f(Tb)
    for k in range(1, N, 2):
        s += 4.0 * f(Ta + k * h)
    for k in range(2, N, 2):
        s += 2.0 * f(Ta + k * h)
    return s * h / 3.0


def _int_Cp(i, Ta_K, Tb_K):
    """int Cp0 dT  [J/mol]."""
    return _simpson(lambda T: cp_ideal(i, T), Ta_K, Tb_K)


def _int_CpT(i, Ta_K, Tb_K):
    """int Cp0/T dT  [J/(mol.K)]."""
    return _simpson(lambda T: cp_ideal(i, T) / T, Ta_K, Tb_K)


def H_ideal_i(i, T_R):
    """H_ig del componente i puro [BTU/lbmol], referencia 0 a Tref."""
    T_K = T_R * 5.0 / 9.0
    return _int_Cp(i, TREF_K, T_K) * J_TO_BTUlbmol


def S_ideal_i(i, T_R, P):
    """S_ig del componente i puro [BTU/(lbmol.R)], referencia 0 a Tref,Pref."""
    T_K = T_R * 5.0 / 9.0
    return (_int_CpT(i, TREF_K, T_K) * J_TO_BTUlbmolR
            - R_BTU * math.log(P / PREF))


# ============================================================
# 2) PARAMETROS DE LA EOS (a, b, da/dT) para PR o SRK
# ============================================================
def _params_eos(comp, T_R, eos):
    """Devuelve (am, bm, da_dT, d1, d2) en unidades internas del motor
    (a: psi.ft6/lbmol2, b: ft3/lbmol) para la EOS pedida ('PR' o 'SRK')."""
    NC = eng.NC
    if eos == 'SRK':
        aa  = eng._ai_alpha_vec_srk(T_R)          # ai*alpha por componente
        bi  = [eng.bi_srk(i) for i in range(NC)]
        kij = eng.KIJ_DEFAULT_SRK
        TC  = eng.TC_SRK
        ai_ = [eng.ai_srk(i) for i in range(NC)]
        mi_ = [eng.mi_srk(i) for i in range(NC)]
        d1, d2 = 1.0, 0.0
    else:
        aa  = eng._ai_alpha_vec_pr(T_R)
        bi  = [eng.bi_pr(i) for i in range(NC)]
        kij = eng.KIJ_DEFAULT_PR
        TC  = eng.TC
        ai_ = [eng.ai_pr(i) for i in range(NC)]
        mi_ = [eng.mi_pr(i) for i in range(NC)]
        d1, d2 = 1.0 + SQRT2, 1.0 - SQRT2

    # d(ai*alpha)/dT = ai * dalpha/dT ;  dalpha/dT = -m*sqrt(alpha)/sqrt(T*Tc)
    daa = [0.0] * NC
    for i in range(NC):
        if aa[i] > 0 and ai_[i] > 0:
            salpha = math.sqrt(aa[i] / ai_[i])    # = sqrt(alpha_i)
            daa[i] = ai_[i] * (-mi_[i] * salpha / math.sqrt(T_R * TC[i]))

    am = 0.0; da_dT = 0.0
    for i in range(NC):
        xi = comp[i]
        if xi == 0:
            continue
        for j in range(NC):
            xj = comp[j]
            if xj == 0:
                continue
            f = (1.0 - kij[i][j])
            aij = math.sqrt(aa[i] * aa[j]) * f
            am += xi * xj * aij
            if aa[i] * aa[j] > 0:
                daij = 0.5 * aij * (daa[i] / aa[i] + daa[j] / aa[j])
                da_dT += xi * xj * daij
    bm = sum(comp[i] * bi[i] for i in range(NC))
    return am, bm, da_dT, d1, d2


# ============================================================
# 3) FUNCIONES DE PARTIDA (genericas)
# ============================================================
def H_departure(T_R, P, Z, am, bm, da_dT, d1, d2):
    """(H - H_ig) [BTU/lbmol]."""
    B  = bm * P / (eng.R_GAS * T_R)
    lt = math.log((Z + d1 * B) / (Z + d2 * B))
    return R_BTU * T_R * (Z - 1.0) + ((T_R * da_dT - am) / ((d1 - d2) * bm)) * lt * CONV


def S_departure(T_R, P, Z, am, bm, da_dT, d1, d2):
    """(S - S_ig) [BTU/(lbmol.R)] (el termino -R ln(P/Pref) va en la parte ideal)."""
    B  = bm * P / (eng.R_GAS * T_R)
    lt = math.log((Z + d1 * B) / (Z + d2 * B))
    return R_BTU * math.log(Z - B) + (da_dT / ((d1 - d2) * bm)) * lt * CONV


# ============================================================
# 4) H y S de una FASE
# ============================================================
def H_fase(comp, T_R, P, Z, eos):
    am, bm, da_dT, d1, d2 = _params_eos(comp, T_R, eos)
    H_id = sum(comp[i] * H_ideal_i(i, T_R) for i in range(eng.NC) if comp[i] > 0)
    return H_id + H_departure(T_R, P, Z, am, bm, da_dT, d1, d2)


def S_fase(comp, T_R, P, Z, eos):
    am, bm, da_dT, d1, d2 = _params_eos(comp, T_R, eos)
    S_id = sum(comp[i] * S_ideal_i(i, T_R, P) for i in range(eng.NC) if comp[i] > 0)
    S_mix = 0.0
    for i in range(eng.NC):
        if comp[i] > 1e-15:
            S_mix -= R_BTU * comp[i] * math.log(comp[i])
    return S_id + S_mix + S_departure(T_R, P, Z, am, bm, da_dT, d1, d2)


# ============================================================
# 5) INTERFAZ - a partir del resultado de un flash
# ============================================================
def _pick_Z(comp, T_R, P, kind, eos):
    am, bm, da_dT, d1, d2 = _params_eos(comp, T_R, eos)
    A, B = eng.AB(am, bm, T_R, P)
    ZV, ZL = (eng.solve_Z_srk(A, B) if eos == 'SRK' else eng.solve_Z_pr(A, B))
    if kind == 'V':
        return ZV if ZV is not None else ZL
    return ZL if ZL is not None else ZV


def calcular_HS(z, T_R, P, res_flash, eos=None):
    """H y S de la corriente y por fase a partir de un flash. `eos` fija la
    ecuacion de estado ('PR'/'SRK'); si es None usa la activa del motor."""
    if eos is None:
        eos = eng.get_eos()
    V  = res_flash.get('V', 0.0)
    L  = 1.0 - V
    ZV = res_flash.get('ZV', None)
    ZL = res_flash.get('ZL', None)
    y  = res_flash.get('y', None)
    x  = res_flash.get('x', None)

    out = {'V': V, 'L': L, 'eos': eos,
           'H_vapor': None, 'S_vapor': None,
           'H_liquido': None, 'S_liquido': None,
           'H_stream': None, 'S_stream': None}

    if V >= 1.0 - 1e-10:
        Z = ZV if ZV is not None else _pick_Z(z, T_R, P, 'V', eos)
        H = H_fase(z, T_R, P, Z, eos); S = S_fase(z, T_R, P, Z, eos)
        out.update(H_vapor=H, S_vapor=S, H_stream=H, S_stream=S)
        return out
    if V <= 1e-10:
        Z = ZL if ZL is not None else _pick_Z(z, T_R, P, 'L', eos)
        H = H_fase(z, T_R, P, Z, eos); S = S_fase(z, T_R, P, Z, eos)
        out.update(H_liquido=H, S_liquido=S, H_stream=H, S_stream=S)
        return out
    if y is None or x is None:
        return out
    Hv = H_fase(y, T_R, P, ZV, eos); Sv = S_fase(y, T_R, P, ZV, eos)
    Hl = H_fase(x, T_R, P, ZL, eos); Sl = S_fase(x, T_R, P, ZL, eos)
    out.update(H_vapor=Hv, S_vapor=Sv, H_liquido=Hl, S_liquido=Sl,
               H_stream=V * Hv + L * Hl, S_stream=V * Sv + L * Sl)
    return out

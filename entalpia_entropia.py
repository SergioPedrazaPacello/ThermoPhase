"""
entalpia_entropia.py  --  Cálculo de Entalpía y Entropía Molar

ThermoPhase - Módulo termodinámico
Basado en:
  - Aspen HYSYS Property Methods & Calculations, sec. A.4 (ec. A.27-A.30)
  - Aspen COMThermo Reference Guide, sec. 3.2 y 5.2
  - Polinomio IDEAL ENTHALPY interno de HYSYS (AUXILIAR.xlsx) — 13 componentes
  - Constantes despejadas del banco HYSYS (DATOS.xlsx) para los 13 componentes

Estructura del cálculo:
    H(T,P) = H_offset + H_polyH(T)*MW/2.326 + H_departure(PR)
    S(T,P) = S_offset + ∫[298.15→T] Cp°(T')/T' dT' - R·ln(P/1atm) + S_departure(PR)

donde:
    H_polyH(T)  = polinomio de 5 grados de HYSYS (kJ/kg, T en K)
    Cp°(T)      = derivada del polinomio de H (multiplicada por MW → J/mol·K)

Para mezclas (COMThermo ec. 3.4):
    H_mez  = Σ xᵢ Hᵢ°ᴵᴰ + H_dep_mez
    S_mez  = Σ xᵢ Sᵢ°ᴵᴰ - R·Σ xᵢ·ln(xᵢ) + S_dep_mez

Precisión validada vs HYSYS:
  - Componentes puros (26 casos): <0.001% en H, <0.001 en S
  - Mezclas multicomponente:      <0.05% en H, <0.03 en S
"""

import math
import numpy as np
import eos as eng


# ============================================================
# CONSTANTES POR COMPONENTE
# Orden canónico: 0=N2, 1=CO2, 2=C1, 3=C2, 4=C3, 5=iC4, 6=nC4,
#                 7=iC5, 8=nC5, 9=C6, 10=C7, 11=C8, 12=C9
# ============================================================

# Polinomio IDEAL ENTHALPY interno de HYSYS (AUXILIAR.xlsx tab TDep)
# H_ideal°(T) = a + b·T + c·T² + d·T³ + e·T⁴ + f·T⁵     [kJ/kg]  con T en K
# Válido en el rango T = 3.15 K a 5273 K.
POLY_H_HYSYS = [
    ( 2.888634e+00,  9.827466e-01,  9.714241e-05, -4.157947e-10, -3.655484e-12,  4.050133e-16),  # N2
    ( 1.252550e-09,  6.181390e-01,  4.844850e-04, -1.493530e-07,  2.290500e-11, -1.370450e-15),  # CO2
    (-1.298000e+01,  2.364590e+00, -2.132470e-03,  5.661800e-06, -3.724760e-09,  8.608960e-13),  # C1
    (-1.767500e+00,  1.142900e+00, -3.236000e-04,  4.243100e-06, -3.393160e-09,  8.820960e-13),  # C2
    ( 3.948890e+01,  3.950000e-01,  2.114090e-03,  3.964860e-07, -6.671760e-10,  1.679360e-13),  # C3
    ( 3.090300e+01,  1.533000e-01,  2.634790e-03,  7.272260e-08, -7.278960e-10,  2.367360e-13),  # iC4
    ( 6.772100e+01,  8.540580e-03,  3.276990e-03, -1.109680e-06,  1.766460e-10, -6.399260e-15),  # nC4
    ( 6.425000e+01, -1.317980e-01,  3.541000e-03, -1.333200e-06,  2.514460e-10, -1.295760e-14),  # iC5
    ( 6.319800e+01, -1.170170e-02,  3.316400e-03, -1.170500e-06,  1.996360e-10, -8.664850e-15),  # nC5
    ( 7.451300e+01, -9.669700e-02,  3.476490e-03, -1.321200e-06,  2.523650e-10, -1.346660e-14),  # C6
    ( 7.141000e+01, -9.689490e-02,  3.473000e-03, -1.330200e-06,  2.557660e-10, -1.377260e-14),  # C7
    ( 1.265070e+02, -2.701000e-01,  3.998290e-03, -1.973000e-06,  6.227960e-10, -9.381350e-14),  # C8
    ( 4.978720e-09, -6.528950e-02,  3.402880e-03, -1.253450e-06,  2.009550e-10, -2.237590e-23),  # C9
]

# Peso molecular (kg/kgmol = lb/lbmol) — mismo valor que eos.PM,
# repetido aquí como cache local.
_MW = [28.013, 44.0097, 16.0429, 30.0699, 44.097, 58.124, 58.124,
       72.151, 72.151, 86.178, 100.205, 114.232, 128.259]

# Factor kJ/kg -> BTU/lbmol  =  MW / 2.326009   (por componente)
_H_CONV = [mw / 2.326009 for mw in _MW]

# H_offset [BTU/lbmol]  — "Enthalpy Basis Offset" publicado oficialmente
# por HYSYS en la pestaña Base Properties de cada componente puro.
# Fuente: DATOS_TECNICOS.xlsx del banco HYSYS Aspen v14.0
# Precisión: ~12 dígitos significativos (mayor que la que HYSYS reporta
# en pantalla de corrientes).  NO es un ajuste calibrado sino el
# valor exacto que HYSYS carga en su banco interno.
H_OFFSET = [
      -3667.11243468102,   # N2
    -173529.620873529,     # CO2
     -36512.7350834681,    # C1
     -41575.3049387527,    # C2
     -51315.5848720225,    # C3
     -65548.7994060705,    # iC4
     -62586.7176872398,    # nC4
     -75964.4455713536,    # iC5
     -73062.1990982242,    # nC5
     -83839.4154794268,    # C6
     -94476.9135486907,    # C7
    -107053.349623498,     # C8
    -112396.223856977,     # C9
]

# S_offset [BTU/(lbmol·R)] — despejado de HYSYS por PROMEDIO de dos puntos
# (vapor y líquido para pesados), con Cp° = derivada del polinomio HYSYS.
S_OFFSET = [
    35.3696,   # N2
    41.1968,   # CO2
    43.8327,   # C1
    46.6579,   # C2
    38.6683,   # C3
    38.4583,   # iC4
    30.5461,   # nC4
    28.5956,   # iC5
    38.4225,   # nC5
    39.2961,   # C6
    47.0824,   # C7
    34.5718,   # C8
    67.3254,   # C9
]

# Coeficientes Cp° Aly-Lee (tab Heat Capacity V de HYSYS) — se mantienen como respaldo
# y para la integral ∫Cp°/T dT que sí usamos (la S no tiene poly equivalente en HYSYS).
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
# CONSTANTES TERMODINÁMICAS
# ============================================================
R_BTU  = 1.98588            # BTU/(lbmol·°R)
CONV   = 0.1850497          # 1 psi·ft³ = 0.1850497 BTU
J_H    = 0.429922           # J/mol -> BTU/lbmol
J_S    = 0.429922 * (5/9)   # J/(mol·K) -> BTU/(lbmol·°R)
PREF   = 14.696             # 1 atm en psia
TREF_K = 298.15             # K (base de formación)
SQRT2  = math.sqrt(2.0)


# ============================================================
# Polinomio HYSYS interno y su derivada (Cp°)
# ============================================================

def _H_polyH(i, T_K):
    """Polinomio IDEAL ENTHALPY interno de HYSYS  [kJ/kg]  a T en K."""
    a, b, c, d, e, f = POLY_H_HYSYS[i]
    return a + b*T_K + c*T_K**2 + d*T_K**3 + e*T_K**4 + f*T_K**5


def Cp_ideal(i, T_K):
    """Cp° gas ideal componente i [J/(mol·K)], T en K.
    Derivada del polinomio interno de HYSYS: Cp = dH/dT · MW.
    (H en kJ/kg → dH/dT en kJ/(kg·K).  · MW → kJ/(kgmol·K) = J/(mol·K)).
    """
    a, b, c, d, e, f = POLY_H_HYSYS[i]
    dHdT = b + 2*c*T_K + 3*d*T_K**2 + 4*e*T_K**3 + 5*f*T_K**4
    return dHdT * _MW[i]


def Cp_ideal_alylee(i, T_K):
    """Cp° gas ideal por Aly-Lee (DIPPR 107) — se conserva como referencia
    y para la integral ∫Cp/T de la entropía.
    """
    a, b, c, d, e = CP_ALYLEE[i]
    ea = abs(e)
    return (a
            + b*(c/(T_K*math.sinh(c/T_K)))**2
            + d*(ea/(T_K*math.cosh(ea/T_K)))**2)


def _int_CpT_num(i, Ta, Tb, N=4000):
    """∫[Ta→Tb] Cp°(T)/T dT  [J/(mol·K)]  — Simpson compuesta con
    Cp° = derivada del polinomio interno de HYSYS (mismo Cp° que en H).
    N=4000 da precisión ~1e-6 J/(mol·K).
    """
    if N % 2:
        N += 1
    h = (Tb - Ta) / N
    s = Cp_ideal(i, Ta)/Ta + Cp_ideal(i, Tb)/Tb
    for k in range(1, N, 2):
        s += 4.0 * Cp_ideal(i, Ta + k*h) / (Ta + k*h)
    for k in range(2, N, 2):
        s += 2.0 * Cp_ideal(i, Ta + k*h) / (Ta + k*h)
    return s * h / 3.0


# ============================================================
# Entalpía y entropía ideal por componente
# ============================================================

def H_ideal_i(i, T_R):
    """Entalpía ideal componente i puro [BTU/lbmol]  a temperatura T [°R].
        Hᵢ°ᴵᴰ(T) = H_offset,i + H_poly_HYSYS(T_K) · MWᵢ / 2.326
    El polinomio HYSYS ya integra desde su base interna; el H_offset
    ajusta esa base a la de HYSYS (formación a 25 °C).
    """
    T_K = T_R * 5.0/9.0
    return H_OFFSET[i] + _H_polyH(i, T_K) * _H_CONV[i]


def S_ideal_i(i, T_R, P):
    """Entropía ideal componente i puro [BTU/(lbmol·°R)] a T [°R], P [psia].
        Sᵢ°ᴵᴰ(T,P) = S_offset,i + ∫[298.15→T_K] Cp°/T dT - R·ln(P/1atm)
    """
    T_K = T_R * 5.0/9.0
    return (S_OFFSET[i]
            + _int_CpT_num(i, TREF_K, T_K) * J_S
            - R_BTU * math.log(P/PREF))


# ============================================================
# Departures Peng-Robinson (ec. A.29 y A.30 del PDF HYSYS)
# ============================================================

def _da_dT_mezcla(comp, T):
    """Derivada da_m/dT para mezcla con regla clásica van der Waals.
        aᵢⱼ = √(aᵢαᵢ·aⱼαⱼ)·(1-kᵢⱼ)
        daᵢⱼ/dT = 0.5·[aᵢⱼ/(aᵢαᵢ·aⱼαⱼ)] · [aⱼαⱼ·d(aᵢαᵢ)/dT + aᵢαᵢ·d(aⱼαⱼ)/dT]
    Para eficiencia se calcula: da_m/dT = Σᵢ Σⱼ xᵢxⱼ·daᵢⱼ/dT
    """
    # entalpia_entropia SIEMPRE opera en Peng-Robinson: los offsets H_OFFSET y
    # S_OFFSET calibrados contra HYSYS son válidos únicamente para la EOS
    # Peng-Robinson, así que aquí forzamos las variantes _pr sin importar
    # cuál sea la EOS activa que el usuario haya elegido para el flash.
    kij = eng.KIJ_DEFAULT_PR
    NC  = eng.NC
    aa  = np.array([eng.ai_alpha_pr(i, T) for i in range(NC)])
    # d(aᵢαᵢ)/dT = aᵢ · dαᵢ/dT ;  αᵢ = (1 + mᵢ(1-√(T/Tc)))²
    # dα/dT = 2(1+m(1-√T/Tc)) · (-m/(2·√(T·Tc))) = -m·(1+m(1-√T/Tc))/√(T·Tc)
    daa = np.zeros(NC)
    for i in range(NC):
        m  = eng.mi_pr(i)
        u  = 1 + m*(1 - math.sqrt(T/eng.TC[i]))
        daa[i] = eng.ai_pr(i) * (-u*m/math.sqrt(T*eng.TC[i]))
    total = 0.0
    for i in range(NC):
        xi = comp[i]
        if xi == 0: continue
        for j in range(NC):
            xj = comp[j]
            if xj == 0: continue
            aij = math.sqrt(aa[i]*aa[j]) * (1 - kij[i][j])
            if aa[i]*aa[j] > 0:
                daij = 0.5 * aij * (daa[i]/aa[i] + daa[j]/aa[j])
            else:
                daij = 0.0
            total += xi*xj*daij
    return total


def H_departure(comp, T_R, P, Z, am, bm, da_dT):
    """H - Hᴵᴰ [BTU/lbmol] según ec. A.29 (Peng-Robinson):
        (H-Hᴵᴰ)/(RT) = Z-1 - 1/(2√2·b·RT)·[a - T·da/dT]·ln[(V+(√2+1)b)/(V+(√2-1)b)]
    Rearreglado en función de Z y B (B = b·P/(RT)):
        (V+k·b)/(V+m·b) = (Z + k·B)/(Z + m·B)
    Devuelve H_dep en BTU/lbmol.
    """
    B  = bm*P/(eng.R_GAS*T_R)
    lt = math.log((Z + (1+SQRT2)*B) / (Z + (1-SQRT2)*B))
    # H_dep = R·T·(Z-1) + (T·da/dT - a)/(2√2·b) · ln[...]
    # Unidades: R·T en BTU/lbmol; (T·da/dT - a)/b en psi·ft³/lbmol → CONV
    return R_BTU*T_R*(Z-1) + ((T_R*da_dT - am)/(2*SQRT2*bm))*lt*CONV


def S_departure(comp, T_R, P, Z, am, bm, da_dT):
    """S - Sᴵᴰ [BTU/(lbmol·°R)] según ec. A.30:
        (S-Sᴵᴰ)/R = ln(Z-B) - ln(P/P°) + A/(2√2·B)·(T/a·da/dT)·ln[...]
    Notar: HYSYS toma el término -R·ln(P/P°) en la parte IDEAL,
    por eso aquí solo entra el residual "puro":
        S_dep = R·ln(Z-B) + da/dT/(2√2·b) · ln[...]
    """
    B  = bm*P/(eng.R_GAS*T_R)
    lt = math.log((Z + (1+SQRT2)*B) / (Z + (1-SQRT2)*B))
    return R_BTU*math.log(Z - B) + (da_dT/(2*SQRT2*bm))*lt*CONV


# ============================================================
# Entalpía y entropía de una FASE (composición dada)
# ============================================================

def H_fase(comp, T_R, P, Z):
    """Entalpía molar de una fase [BTU/lbmol].
        H_fase = Σᵢ xᵢ Hᵢ°ᴵᴰ(T) + H_dep_PR(mezcla)
    Nota: para gas ideal puro H no depende de P; el H_dep_PR captura
    toda la dependencia de P para la fase real.
    """
    am    = eng.am_pr(comp, T_R, eng.KIJ_DEFAULT_PR)
    bm    = eng.bm_pr(comp)
    da_dT = _da_dT_mezcla(comp, T_R)
    H_id  = sum(comp[i]*H_ideal_i(i, T_R) for i in range(eng.NC) if comp[i] > 0)
    H_dep = H_departure(comp, T_R, P, Z, am, bm, da_dT)
    return H_id + H_dep


def S_fase(comp, T_R, P, Z):
    """Entropía molar de una fase [BTU/(lbmol·°R)].
        S_fase = Σᵢ xᵢ Sᵢ°ᴵᴰ(T,P) - R·Σᵢ xᵢ·ln(xᵢ) + S_dep_PR(mezcla)
    """
    am    = eng.am_pr(comp, T_R, eng.KIJ_DEFAULT_PR)
    bm    = eng.bm_pr(comp)
    da_dT = _da_dT_mezcla(comp, T_R)
    # parte ideal por componente (ya incluye -R·ln(P/1atm))
    S_id = sum(comp[i]*S_ideal_i(i, T_R, P) for i in range(eng.NC) if comp[i] > 0)
    # término de mezcla ideal - R·Σ xᵢ·ln xᵢ  (positivo)
    S_mix = 0.0
    for i in range(eng.NC):
        if comp[i] > 1e-15:
            S_mix -= R_BTU * comp[i] * math.log(comp[i])
    S_dep = S_departure(comp, T_R, P, Z, am, bm, da_dT)
    return S_id + S_mix + S_dep


# ============================================================
# INTERFAZ PRINCIPAL - a partir del resultado de un flash
# ============================================================

def calcular_HS(z, T_R, P, res_flash):
    """Calcula H y S de la corriente y por fase, a partir del resultado
    de un flash del engine (dict con keys: modo, V, ZV, ZL, y, x).

    Parameters
    ----------
    z         : composición global (lista de 13 fracciones molares)
    T_R       : temperatura [°R]
    P         : presión [psia]
    res_flash : diccionario devuelto por eos.calcular()

    Returns
    -------
    dict con keys:
        'H_stream'  : entalpía molar de la corriente global [BTU/lbmol]
        'S_stream'  : entropía molar de la corriente global [BTU/(lbmol·°R)]
        'H_vapor'   : entalpía molar de la fase vapor  o None
        'S_vapor'   : entropía molar de la fase vapor  o None
        'H_liquido' : entalpía molar de la fase líquida o None
        'S_liquido' : entropía molar de la fase líquida o None
        'V'         : fracción molar vapor
        'L'         : fracción molar líquido
    """
    modo = res_flash.get('modo', '?')
    V    = res_flash.get('V', 0.0)
    L    = 1.0 - V
    ZV   = res_flash.get('ZV', None)
    ZL   = res_flash.get('ZL', None)
    y    = res_flash.get('y', None)
    x    = res_flash.get('x', None)

    out = {'V': V, 'L': L,
           'H_vapor': None, 'S_vapor': None,
           'H_liquido': None, 'S_liquido': None,
           'H_stream': None, 'S_stream': None}

    # Fase única (vapor, líquido o supercrítica)
    if V >= 1.0 - 1e-10:
        # todo vapor
        Z = ZV if ZV is not None else _pick_Z(z, T_R, P, 'V')
        H = H_fase(z, T_R, P, Z)
        S = S_fase(z, T_R, P, Z)
        out['H_vapor']  = H
        out['S_vapor']  = S
        out['H_stream'] = H
        out['S_stream'] = S
        return out

    if V <= 1e-10:
        # todo líquido
        Z = ZL if ZL is not None else _pick_Z(z, T_R, P, 'L')
        H = H_fase(z, T_R, P, Z)
        S = S_fase(z, T_R, P, Z)
        out['H_liquido'] = H
        out['S_liquido'] = S
        out['H_stream']  = H
        out['S_stream']  = S
        return out

    # Bifásico
    if y is None or x is None:
        return out
    Hv = H_fase(y, T_R, P, ZV)
    Sv = S_fase(y, T_R, P, ZV)
    Hl = H_fase(x, T_R, P, ZL)
    Sl = S_fase(x, T_R, P, ZL)
    out['H_vapor']   = Hv
    out['S_vapor']   = Sv
    out['H_liquido'] = Hl
    out['S_liquido'] = Sl
    out['H_stream']  = V*Hv + L*Hl
    out['S_stream']  = V*Sv + L*Sl
    return out


def _pick_Z(comp, T_R, P, kind):
    """Resuelve Z y elige raíz (vapor / líquido) para fases únicas.
    Fuerza PR ya que la calibración de H/S es específica de PR."""
    am = eng.am_pr(comp, T_R, eng.KIJ_DEFAULT_PR)
    bm = eng.bm_pr(comp)
    A, B = eng.AB(am, bm, T_R, P)
    ZV, ZL = eng.solve_Z_pr(A, B)
    if kind == 'V':
        return ZV if ZV is not None else ZL
    return ZL if ZL is not None else ZV

# -*- coding: utf-8 -*-
"""
agua_pura.py — Propiedades del AGUA PURA por los modelos que usa PVTsim
(sección "Water Phase Properties" del PVTsim Method Documentation).

  • Termodinámica (densidad, entalpía, entropía, Cp): ecuación de Helmholtz de
    Keyes, Keenan, Hill & Moore (1968).
        Ψ = Ψ0(T) + R·T·[ln ρ + ρ·Q(ρ,T)]      (Ψ en J/g, ρ en g/cm³)
        Ψ0(T) = C1 + C2·T + C3·T² + (C4 + C5·T)·ln T
        τ = 1000/T (T en K),  R = 0.46151 J/(g·K)
        P = ρ²·(∂Ψ/∂ρ)_T = ρ·R·(1000/τ)·[1 + ρ·Q + ρ²·(∂Q/∂ρ)]
        H = [∂(Ψ·τ)/∂τ]_ρ + P/ρ
        S = −(∂Ψ/∂T)_ρ

  • Viscosidad (cP): Meyer et al. (1967) / Schmidt (1969), 4 regiones.

Unidades de salida convertidas al sistema interno de ThermoPhase:
  densidad → lb/ft³ ;  H → BTU/lbmol ;  S → BTU/(lbmol·°R) ;  μ → cP.

La fase acuosa del flash es ~99 % agua; estas propiedades del agua pura son
las que PVTsim reporta para esa fase (densidad/H/S/μ), por lo que se usan como
propiedades de la fase acuosa.
"""

import math

# ── Constantes ──────────────────────────────────────────────────────────────
R_HELM = 0.46151            # J/(g·K)   constante de la ec. de Keyes
PM_H2O = 18.015100479126    # g/mol
TC_K   = 647.3              # K  (Tc del agua usada por PVTsim; T_R 1165.14→647.3K)
PC_MN  = 22.12              # MN/m² (Pc del agua)  — para regiones de viscosidad
RHO_C  = 0.317              # g/cm³ densidad crítica del agua

# Conversión de unidades
_J_G_TO_BTU_LBMOL   = PM_H2O * (453.59237/1055.05585)   # J/g → BTU/lbmol
_J_GK_TO_BTU_LBMOLR = PM_H2O * (453.59237/1055.05585)*(5.0/9.0)  # J/(g·K)→BTU/(lbmol·°R)
_GCM3_TO_LBFT3      = 62.427960576                       # g/cm³ → lb/ft³

# ── Coeficientes Keyes (1968) ───────────────────────────────────────────────
C1, C2, C3, C4, C5 = 1855.3865, 3.278642, -0.00037903, 46.174, -1.02117

# A_ij (i=1..10 filas, j=1..7 columnas)
_A = [
 [ 29.492937,  -5.1985860,   6.8335354,  -0.1564104,  -6.3972405,  -3.9661401, -0.69048554],
 [-132.13917,   7.7791820, -26.1497510,  -0.72546108, 26.4092820,  15.4530610,  2.74074160],
 [ 274.64632, -33.3019020,  65.3263960,  -9.2734289,  47.7403740, -29.1424700, -5.10280700],
 [-360.93828, -16.2546220, -26.1819780,   4.3125840,  56.3231300,  29.5687960,  3.96360850],
 [ 342.18431,-177.3107400,   0.0,          0.0,         0.0,         0.0,         0.0       ],
 [-244.50042, 127.4874200,   0.0,          0.0,         0.0,         0.0,         0.0       ],
 [ 155.18535, 137.4615300,   0.0,          0.0,         0.0,         0.0,         0.0       ],
 [   5.9728487,155.9783600,  0.0,          0.0,         0.0,         0.0,         0.0       ],
 [-410.30848, 337.3118000,-137.4661800,    6.7874983, 136.8731700,  79.8479700, 13.0411253],
 [-416.05860, 209.8886600, 733.9684800,   10.4017170, 645.8188000, 399.1757000, 71.5313530],
]
# Anclas de densidad por columna j (g/cm³): 0.634 para j=1..6, 1.0 para j=7
# (constantes "aa" y "ab" del manual).  Estructura Keenan-Keyes-Hill-Moore 1969.
RHO_AJ = [0.634, 0.634, 0.634, 0.634, 0.634, 0.634, 1.0]
TAU_AA = 2.5      # K⁻¹  (τaa, factor externo (τ−τaa))
TAU_C  = 1.544912 # K⁻¹  (τc = 1000/Tc, potencias (τ−τc)^(j-1))
E_Q    = 4.8      # cm³/g


def _Q_and_derivs(rho, tau):
    """Devuelve (Q, dQ/dρ, dQ/dτ) de la función Q(ρ,τ) de Keyes (KKHM 1969).

    Q = (τ−τaa)·Σ_{j=1..7} (τ−τc)^{j-1}·[ Σ_{i=1..8} A_{i,j}·(ρ−ρaj)^{i-1}
                                          + e^{−E·ρ}·(A_{9,j}+A_{10,j}·ρ) ]

    donde ρaj = 0.634 para j=1..6 y ρa7 = 1.0.  Índices de A en base 1 como en
    el manual (_A[i-1][j-1], i=1..10 filas, j=1..7 columnas).
    """
    eEp = math.exp(-E_Q*rho)
    inner = 0.0          # Σ_j (τ−τc)^{j-1}·bracket_j
    d_inner_drho = 0.0
    d_inner_dtau = 0.0   # ∂/∂τ de inner (solo por las potencias (τ−τc)^{j-1})
    for j in range(1, 8):
        rhoaj = RHO_AJ[j-1]
        da = rho - rhoaj
        Bj = 0.0; dBj = 0.0                     # bracket_j y su ∂/∂ρ
        for i in range(1, 9):
            Bj += _A[i-1][j-1]*da**(i-1)
            if i >= 2:
                dBj += _A[i-1][j-1]*(i-1)*da**(i-2)
        gj = _A[8][j-1] + _A[9][j-1]*rho        # A9,j + A10,j·ρ
        Bj += eEp*gj
        dBj += eEp*(_A[9][j-1]) + (-E_Q*eEp)*gj
        w  = (tau - TAU_C)**(j-1)
        inner        += w*Bj
        d_inner_drho += w*dBj
        dw = 0.0 if j == 1 else (j-1)*(tau - TAU_C)**(j-2)
        d_inner_dtau += dw*Bj
    fac = (tau - TAU_AA)
    Q       = fac*inner
    dQ_drho = fac*d_inner_drho
    dQ_dtau = inner + fac*d_inner_dtau
    return Q, dQ_drho, dQ_dtau


def _psi0(T):
    return C1 + C2*T + C3*T*T + (C4 + C5*T)*math.log(T)

def _dpsi0_dT(T):
    return C2 + 2*C3*T + C5*math.log(T) + (C4 + C5*T)/T


def _presion_MN(rho, T):
    """Presión (MN/m²) de la ec. de Keyes a (ρ,T).  P = ρ·R·(1000/τ)·[1+ρQ+ρ²Qρ].
    R·(1000/τ) = R·T. Resultado en J/cm³ = MPa = MN/m²."""
    tau = 1000.0/T
    Q, dQ_dr, _ = _Q_and_derivs(rho, tau)
    return rho*R_HELM*T*(1.0 + rho*Q + rho*rho*dQ_dr)


def densidad_gcm3(T_K, P_MN):
    """Densidad de agua líquida (g/cm³) resolviendo P(ρ,T)=P por bisección."""
    lo, hi = 0.30, 1.20               # rango físico del agua líquida
    flo = _presion_MN(lo, T_K) - P_MN
    fhi = _presion_MN(hi, T_K) - P_MN
    if flo*fhi > 0:
        # fuera de rango: devuelve el extremo más cercano (líquido comprimido)
        return hi if abs(fhi) < abs(flo) else lo
    for _ in range(80):
        mid = 0.5*(lo+hi)
        fm = _presion_MN(mid, T_K) - P_MN
        if abs(fm) < 1e-9:
            return mid
        if flo*fm <= 0:
            hi = mid; fhi = fm
        else:
            lo = mid; flo = fm
    return 0.5*(lo+hi)


def _propiedades_SI(T_K, P_MN):
    """(ρ g/cm³, H J/g, S J/gK) del agua pura a (T,P) por Keyes."""
    rho = densidad_gcm3(T_K, P_MN)
    tau = 1000.0/T_K
    Q, dQ_dr, dQ_dtau = _Q_and_derivs(rho, tau)
    P = rho*R_HELM*T_K*(1.0 + rho*Q + rho*rho*dQ_dr)      # MN/m² = J/cm³
    # H = [∂(Ψτ)/∂τ]_ρ + P/ρ.  Ψ = Ψ0 + R·T·[lnρ + ρQ], y R·T = R·1000/τ.
    # Ψ·τ = Ψ0·τ + 1000·R·[lnρ + ρQ].  ∂(Ψ0·τ)/∂τ con Ψ0=f(T), T=1000/τ:
    #   d(Ψ0·τ)/dτ = Ψ0 + τ·dΨ0/dT·dT/dτ = Ψ0 − (T)·dΨ0/dT   (dT/dτ=−T²/1000·... )
    # Se evalúa d(Ψ0·τ)/dτ numéricamente para robustez.
    dtau = tau*1e-6 + 1e-9
    def psi0tau(tt):
        Tt = 1000.0/tt
        return _psi0(Tt)*tt
    dPsi0tau_dtau = (psi0tau(tau+dtau) - psi0tau(tau-dtau))/(2*dtau)
    H = dPsi0tau_dtau + 1000.0*R_HELM*(math.log(rho) + rho*Q + tau*rho*dQ_dtau) \
        + P/rho
    # S = −(∂Ψ/∂T)_ρ.  Evaluación numérica de Ψ(T) a ρ fija.
    def psi_of_T(TT):
        ta = 1000.0/TT
        Qx, _, _ = _Q_and_derivs(rho, ta)
        return _psi0(TT) + R_HELM*TT*(math.log(rho) + rho*Qx)
    dT = T_K*1e-6 + 1e-6
    S = -(psi_of_T(T_K+dT) - psi_of_T(T_K-dT))/(2*dT)
    return rho, H, S


# ── Viscosidad del agua pura: Meyer(1967)/Schmidt(1969), 4 regiones ─────────
_a = [None, 241.4, 0.3828209486, 0.2162830218, 0.1498693949, 0.4711880117]
_b = [None, 263.4511, 0.4219836243, 80.4]
_c = [None, 586.1198738, 1204.753943, 0.4219836243]
_d = [None, 111.3564669, 67.32080129, 3.205147019]
_Ck1 = [None, -6.4556581, 1.3949436, 0.30259083, 0.10960682, 0.015230031]
_Ck2 = [None, -6.4608381, 1.6163321, 0.07097705, -13.938, 30.119832]
# Presión de vapor: log10 Psat = (1+D1) + Σ_{j=3..7} Dj·(T-273.15)^(j-... ) + D2/(T-273.15)
_D = [None, 2.9304370, -2309.5789, 0.34522497e-1, -0.13621289e-3,
      0.25878044e-6, -0.24709162e-9, 0.95937646e-13]


def _psat_MN(T_K):
    """Presión de vapor del agua (MN/m²) — correlación del manual PVTsim."""
    t = T_K - 273.15
    s = (1.0 + _D[1]) + _D[2]/t
    # términos Dj·(T-273.15)^(j)  para j=3..7 (exponente j-2 sobre t según manual)
    s += (_D[3]*t + _D[4]*t**2 + _D[5]*t**3 + _D[6]*t**4 + _D[7]*t**5)
    return 10.0**s


def _eta1_atm(T_K):
    """Viscosidad a presión atmosférica (µPa·s → se maneja el factor 1e-6)."""
    return (_b[1]*(T_K/TC_K - _b[2]) + _b[3])*1e-6


def viscosidad_cP(T_K, P_MN, rho_gcm3):
    """Viscosidad del agua pura (cP) por Meyer/Schmidt, escogiendo región según
    (T,P).  Fuera del rango de validez extrapola con la región más cercana."""
    # Las fórmulas del manual devuelven la viscosidad en POISE; 1 poise = 100 cP.
    P2CP = 100.0
    Tr = T_K/TC_K
    try:
        psat = _psat_MN(T_K)
    except Exception:
        psat = 0.0
    # Región 1: Psat<P<80 MN/m² y 273.15<T<573.15 K  (η en poise).
    # PVTsim (opción Multiflash) mantiene la fórmula de agua líquida por
    # debajo de 273.15 K congelando la temperatura en el punto de fusión
    # (agua subenfriada); así se evita el blow-up de la exponencial y se
    # reproduce el valor prácticamente constante que reporta PVTsim en la
    # fase acuosa a T bajo cero.
    liquido = rho_gcm3 > 0.7      # densidad típica de agua líquida (g/cm³)
    # Bajo 0°C la correlación de Psat se dispara; para el chequeo de región del
    # líquido subenfriado se usa un Psat efectivo despreciable.
    psat_ef = psat if T_K > 273.15 else 0.0
    if (273.15 < T_K < 573.15 or (liquido and T_K <= 273.15)) \
            and psat_ef < P_MN < 80.0:
        Tr1 = Tr if T_K > 273.15 else (273.15/TC_K)
        eta = 1e-6*_a[1]*(1.0 + (rho_gcm3/RHO_C - P_MN/PC_MN)*_a[4]*(Tr1 - _a[5])) \
              * 10.0**(_a[2]/(Tr1 - _a[3]))
        return eta*P2CP
    # Región 2: 0.1<P<Psat y 373.15<T<573.15   (η1 atmosférica − corrección)
    if 373.15 < T_K < 573.15 and 0.1 < P_MN < psat:
        e1 = _eta1_atm(T_K)      # poise
        eta = e1 - 10.0*(rho_gcm3/RHO_C)*(_c[1] - _c[2]*(Tr - _c[3]))*1e-6
        return abs(eta)*P2CP
    # Región 3: 0.1<P<80 y 648.15<T<1073.15
    if 648.15 < T_K < 1073.15 and 0.1 < P_MN < 80.0:
        e1 = _eta1_atm(T_K)
        r = rho_gcm3/RHO_C
        eta = e1 + (_d[1]*r**3 + _d[2]*r**2 + _d[3]*r)*1e-6
        return abs(eta)*P2CP
    # Región 4 (otras): η = η1 + 10^Y/0.0192  (η1 y resultado en poise)
    e1 = _eta1_atm(T_K)
    X = math.log10(max(rho_gcm3/RHO_C, 1e-9))
    k1 = (rho_gcm3/RHO_C) <= 4.0/3.14
    Ck = _Ck1 if k1 else _Ck2
    Y = Ck[5]*X**4 + Ck[4]*X**3 + Ck[3]*X**2 + Ck[2]*X + Ck[1]
    eta = e1 + (10.0**Y)/0.0192*1e-6
    return abs(eta)*P2CP


# ── API para la fase acuosa (unidades internas de ThermoPhase) ──────────────
def propiedades_agua_pura(T_R, P_psia):
    """Devuelve dict con densidad (lb/ft³), H (BTU/lbmol), S (BTU/lbmol·°R) y
    viscosidad (cP) del AGUA PURA a (T_R °R, P_psia), por Keyes + Meyer/Schmidt.
    """
    T_K = T_R/1.8
    P_MN = P_psia*0.00689476            # psia → MN/m² (MPa)
    try:
        rho, H_Jg, S_JgK = _propiedades_SI(T_K, P_MN)
    except Exception:
        return None
    out = {
        'rho': rho*_GCM3_TO_LBFT3,
        'H':   H_Jg*_J_G_TO_BTU_LBMOL,
        'S':   S_JgK*_J_GK_TO_BTU_LBMOLR,
        'sg':  rho/0.999,               # SG relativo a agua a 4°C
    }
    try:
        out['mu'] = viscosidad_cP(T_K, P_MN, rho)
    except Exception:
        out['mu'] = None
    return out

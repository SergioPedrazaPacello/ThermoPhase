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

  • Viscosidad (cP): formulación IAPS 1985 (Sengers & Watson) evaluada con la
    densidad de Keyes.  (Se conserva viscosidad_cP, Meyer/Schmidt, como
    referencia del manual de PVTsim.)

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
 [-132.13917,   7.7779182, -26.1497510,  -0.72546108, 26.4092820,  15.4530610,  2.74074160],
 [ 274.64632, -33.3019020,  65.3263960,  -9.2734289, -47.7403740, -29.1424700, -5.10280700],
 [-360.93828, -16.2546220, -26.1819780,   4.3125840,  56.3231300,  29.5687960,  3.96360850],
 [ 342.18431,-177.3107400,   0.0,          0.0,         0.0,         0.0,         0.0       ],
 [-244.50042, 127.4874200,   0.0,          0.0,         0.0,         0.0,         0.0       ],
 [ 155.18535, 137.4615300,   0.0,          0.0,         0.0,         0.0,         0.0       ],
 [   5.9728487,155.9783600,  0.0,          0.0,         0.0,         0.0,         0.0       ],
 [-410.30848, 337.3118000,-137.4661800,    6.7874983, 136.8731700,  79.8479700, 13.0411253],
 [-416.05860,-209.8886600,-733.9684800,   10.4017170, 645.8188000, 399.1757000, 71.5313530],
]
# Nota: la tabla A_ij del manual de PVTsim tiene erratas de signo en A(3,5),
# A(10,2) y A(10,3) y un dígito en A(2,2); aquí van los valores originales de
# Keenan, Keyes, Hill & Moore (Steam Tables, 1969, Tabla I).  Con ellos la
# densidad del líquido reproduce las tablas de vapor a 0.01-0.05 %.
# Constantes de la función Q (manual: ρa, ρb, τa, τc, E)
RHO_A  = 0.634    # g/cm³  (columna j = 1)
RHO_B  = 1.0      # g/cm³  (columnas j = 2..7)
TAU_A  = 2.5      # K⁻¹
TAU_C  = 1.544912 # K⁻¹    (= 1000/Tc)
E_Q    = 4.8      # cm³/g


def _Q_and_derivs(rho, tau):
    """Devuelve (Q, dQ/dρ, dQ/dτ) de la función Q(ρ,τ) de Keyes et al. (1968),
    en la forma del manual (Keenan-Keyes-Hill-Moore):

    Q = Σ_{i=1..8} A_{i,1}(ρ−ρa)^{i-1} + e^{−Eρ}(A_{9,1} + A_{10,1}ρ)
        + (τ−τc)·Σ_{j=2..7} (τ−τa)^{j-2}·[ Σ_{i=1..8} A_{i,j}(ρ−ρb)^{i-1}
                                            + e^{−Eρ}(A_{9,j} + A_{10,j}ρ) ]

    ρa = 0.634 g/cm³, ρb = 1.0 g/cm³, τa = 2.5 K⁻¹, τc = 1.544912 K⁻¹,
    E = 4.8 cm³/g.  Índices de A en base 1 (_A[i-1][j-1])."""
    eEp = math.exp(-E_Q*rho)

    def corchete(j, rref):
        B = 0.0; dB = 0.0
        d = rho - rref
        for i in range(1, 9):
            a = _A[i-1][j-1]
            B += a*d**(i-1)
            if i >= 2:
                dB += a*(i-1)*d**(i-2)
        g = _A[8][j-1] + _A[9][j-1]*rho
        B += eEp*g
        dB += eEp*_A[9][j-1] - E_Q*eEp*g
        return B, dB

    Q, dQr = corchete(1, RHO_A)
    S = 0.0; dSr = 0.0; dSt = 0.0
    for j in range(2, 8):
        B, dB = corchete(j, RHO_B)
        w = (tau - TAU_A)**(j-2)
        dw = 0.0 if j == 2 else (j-2)*(tau - TAU_A)**(j-3)
        S += w*B; dSr += w*dB; dSt += dw*B
    fac = tau - TAU_C
    Q += fac*S
    dQr += fac*dSr
    dQt = S + fac*dSt
    return Q, dQr, dQt


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


def _g_rel(rho, T):
    """Energía de Gibbs específica relativa (J/g) a T fija: R·T·(ln ρ + ρQ) + P/ρ
    (el término ψ0(T) es común a todas las raíces y se omite)."""
    Q, _, _ = _Q_and_derivs(rho, 1000.0/T)
    return R_HELM*T*(math.log(rho) + rho*Q) + _presion_MN(rho, T)/rho


def densidad_gcm3(T_K, P_MN):
    """Densidad del agua (g/cm³) por la ecuación de Keyes: entre las raíces
    mecánicamente estables de P(ρ,T) = P se elige la de menor energía de Gibbs
    (líquido o vapor según T y P)."""
    rs = [10.0**(-6.0 + 6.12*k/600.0) for k in range(601)]      # 1e-6 … 1.32
    f = [_presion_MN(r, T_K) - P_MN for r in rs]
    raices = []
    for k in range(1, len(rs)):
        if f[k-1]*f[k] < 0:
            lo, hi, flo = rs[k-1], rs[k], f[k-1]
            for _ in range(100):
                m = 0.5*(lo + hi)
                fm = _presion_MN(m, T_K) - P_MN
                if flo*fm <= 0:
                    hi = m
                else:
                    lo, flo = m, fm
                if hi - lo < 1e-13:
                    break
            r = 0.5*(lo + hi)
            h = 1e-7*r
            if _presion_MN(r + h, T_K) > _presion_MN(r - h, T_K):
                raices.append(r)
    if not raices:
        return rs[-1] if f[-1] < 0 else rs[0]
    # La ecuación tiene lazos no físicos en la zona bifásica: la fase se
    # decide con la presión de vapor (líquido si P > Psat o T < 0 °C, vapor
    # si P < Psat); sobre Tc, la raíz de menor energía de Gibbs.
    if T_K < TC_K:
        try:
            ps = _psat_MN(T_K) if T_K > 273.15 else 0.0
        except Exception:
            ps = 0.0
        return max(raices) if P_MN >= ps else min(raices)
    return min(raices, key=lambda r: _g_rel(r, T_K))


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
    """Presión de vapor del agua (MN/m²) — correlación del manual PVTsim.
    log10(Psat) = (D1−1) + D2/T + Σ_{j=3}^{7} Dj·T^(j−2), con T en Kelvin
    absoluta y Psat en MN/m² (verificado <0.1 % contra Psat del agua)."""
    T = T_K
    s = (_D[1] - 1.0) + _D[2]/T
    s += (_D[3]*T + _D[4]*T**2 + _D[5]*T**3 + _D[6]*T**4 + _D[7]*T**5)
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
    # Región 1: Psat<P<80 MN/m² y 273.15<T<573.15 K  (η en poise):
    #   η = 10⁻⁶·a₁·[1 + (P/Pc − Psat/Pc)·a₄·(T/Tc − a₅)]·10^[a₂/(T/Tc − a₃)]
    # Es la ecuación de la IFC-67 (Meyer et al. 1967),
    #   η[μP] = 241.4·10^[247.8/(T−140)]·[1 + 1.0467·10⁻⁶ (P−Psat)[bar]·(T−305)],
    # reducida con Tc = 647.3 K y Pc = 221.2 bar: a₂ = 247.8/Tc, a₃ = 140/Tc,
    # a₅ = 305/Tc y a₄ = 1.0467·10⁻⁶·Pc·Tc = 0.14987 (los valores tabulados en
    # el manual).  La impresión del manual pone ρ/ρc en el primer término del
    # corchete; la deducción de a₄ muestra que el término es P/Pc.
    # El agua líquida bajo 0 °C (subenfriada en la ecuación de estado) usa la
    # misma ecuación, extrapolada.
    liquido = rho_gcm3 > RHO_C
    psat_ef = psat if T_K > 273.15 else 0.0
    if (273.15 < T_K < 573.15 or (liquido and T_K <= 273.15)) \
            and psat_ef < P_MN < 80.0:
        eta = 1e-6*_a[1]*(1.0 + (P_MN - psat_ef)/PC_MN*_a[4]*(Tr - _a[5])) \
              * 10.0**(_a[2]/(Tr - _a[3]))
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


# ── Viscosidad del agua: formulación IAPS 1985 ──────────────────────────────
# Sengers & Watson (1986), J. Phys. Chem. Ref. Data 15, 1291:
#   μ = μ*·μ0(T̄)·exp[ρ̄·Σ_i Σ_j H_ij (1/T̄ − 1)^i (ρ̄ − 1)^j]
#   μ0 = √T̄ / Σ_{k=0..3} H_k/T̄^k,  T̄ = T/647.27 K,  ρ̄ = ρ/317.763 kg/m³,
#   μ* = 55.071 μPa·s.
# Con la densidad de Keyes reproduce la viscosidad del agua que reporta PVTsim
# para la fase acuosa a ±0.6 % entre 0 y 150 °C (PVTsim la da igual para PR y
# SRK y con o sin gas disuelto: depende sólo de T y P).
_H0_85 = (1.0, 0.978197, 0.579829, -0.202354)
_H_85 = (( 0.5132047, 0.2151778, -0.2818107,  0.1778064, -0.0417661, 0.0,          0.0),
         ( 0.3205656, 0.7317883, -1.070786,   0.4605040,  0.0,       -0.01578386,   0.0),
         ( 0.0,       1.241044,  -1.263184,   0.2340379,  0.0,        0.0,          0.0),
         ( 0.0,       1.476783,   0.0,       -0.4924179,  0.1600435,  0.0,         -0.003629481),
         (-0.7782567, 0.0,        0.0,        0.0,        0.0,        0.0,          0.0),
         ( 0.1885447, 0.0,        0.0,        0.0,        0.0,        0.0,          0.0))
# Bajo el punto de congelación la fase "acuosa" de la EOS es agua subenfriada
# (en la realidad hielo).  Como PVTsim, las propiedades de transporte del agua
# se extrapolan en el líquido subenfriado y se mantienen constantes bajo
# −30 °C (243.15 K), límite inferior de las correlaciones de agua de PVTsim
# (se verifica en su conductividad térmica, constante bajo 243.15 K).
T_MIN_VISC = 243.15     # K


def viscosidad_iaps85_cP(T_K, rho_gcm3):
    Tb = T_K/647.27
    rb = rho_gcm3*1000.0/317.763
    m0 = math.sqrt(Tb)/sum(h/Tb**k for k, h in enumerate(_H0_85))
    x = 1.0/Tb - 1.0
    y = rb - 1.0
    s = 0.0
    for i in range(6):
        for j in range(7):
            h = _H_85[i][j]
            if h:
                s += h*x**i*y**j
    return 55.071e-6*m0*math.exp(rb*s)*1000.0


def viscosidad_agua_cP(T_R, P_psia):
    """Viscosidad del agua pura (cP) a (T °R, P psia) por las ecuaciones de
    Meyer et al. (1967) y Schmidt (1969) del manual de PVTsim, con la densidad
    de Keyes (1968).  Bajo 243.15 K se mantiene el valor de 243.15 K, el mismo
    límite que tiene la conductividad térmica del agua."""
    T_K = max(T_R/1.8, T_MIN_VISC)
    P_MN = P_psia*0.00689476
    rho = densidad_gcm3(T_K, P_MN)
    return viscosidad_cP(T_K, P_MN, rho)


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
        out['mu'] = viscosidad_agua_cP(T_R, P_psia)
    except Exception:
        out['mu'] = None
    return out


# ── Conductividad térmica del agua (manual de PVTsim, Meyer/Schmidt) ─────────
_KA = (-0.92247, 6.728934102, -10.11230521, 6.996953832, -2.31606251)
_KB = (-0.20954276, 1.320227345, -2.485904388, 1.517081933)
_KC = (0.08104183147, -0.4513858027, 0.8057261332, -0.4668315566)


def conductividad_agua_mW(T_R, P_psia):
    """Conductividad térmica del agua pura (mW/(m·K)) a (T °R, P psia).
    Región 1 (líquido, P > Psat, 273.15–623.15 K), extrapolada al líquido
    subenfriado hasta 243.15 K y constante por debajo; en el vapor
    (P < Psat) la expresión de baja densidad del manual."""
    T = max(T_R/1.8, T_MIN_VISC)
    P = P_psia*0.00689476
    try:
        ps = _psat_MN(T) if T > 273.15 else 0.0
    except Exception:
        ps = 0.0
    Tr = T/TC_K
    if P >= ps and T < 623.15:
        S1 = sum(a*Tr**i for i, a in enumerate(_KA))
        S2 = sum(b*Tr**i for i, b in enumerate(_KB))
        S3 = sum(c*Tr**i for i, c in enumerate(_KC))
        x = (P - ps)/PC_MN
        return (S1 + x*(S2 + x*S3))*1e3              # W/(cm·K)·1e-2 → mW/(m·K)
    t = T - 273.15
    rho = densidad_gcm3(T, P)
    l1 = (17.6 + 0.0587*t + 1.04e-4*t*t - 4.51e-8*t**3)*1e-5
    lam = l1 + (103.51 + 0.4198*t - 2.771e-5*t*t)*rho*1e-5 \
        + 2.1482e14/t**4.2*rho*rho*1e-5
    return lam*1e5                                   # W/(cm·K) → mW/(m·K)

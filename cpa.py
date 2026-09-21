# -*- coding: utf-8 -*-
"""
Término de asociación CPA (Cubic-Plus-Association) sobre Peng-Robinson.

PVTsim (Calsep) reemplazó Huron-Vidal por CPA para sistemas con agua porque
Huron-Vidal —una regla de mezcla puramente cúbica— no reproduce la solubilidad
mutua agua-hidrocarburo/gas: no representa el enlace de hidrógeno del agua ni la
solvatación de CO₂/H₂S con el agua.  CPA añade a la EOS cúbica un término de
asociación de la teoría SAFT/Wertheim que sí captura esos fenómenos.

Modelo:
    Z = Z_física(PR) + Z_asociación
    ln φ_i = ln φ_i(PR) + ln φ_i(asociación)

El término de asociación (Michelsen & Hendriks 2001, forma simplificada):
    (A^assoc)/RT = Σ_i x_i Σ_{A_i} [ ln X_{A_i} − X_{A_i}/2 + 1/2 ]
donde X_{A_i} = fracción de sitios A del componente i NO enlazados, solución de
    X_{A_i} = 1 / ( 1 + ρ Σ_j x_j Σ_{B_j} X_{B_j} Δ^{A_i B_j} )
y la fuerza de asociación
    Δ^{A_i B_j} = g(ρ) · [ exp(ε^{A_i B_j}/(R T)) − 1 ] · b_{ij} · β^{A_i B_j}
con g(ρ) = 1/(1 − 1.9 η),  η = b ρ /4  (radial distribution simplificada, CPA
estándar de Kontogeorgis),  b_ij = (b_i + b_j)/2,  ρ = densidad molar = 1/v.

Esquemas de sitios:
    Agua  : 4C  → 2 sitios A (donores) + 2 sitios B (aceptores), simétrico.
    CO₂/H₂S: solvatante → NO auto-asocia, pero SUS sitios cruzan con los del agua
             (solvatación).  Se modela con ε, β cruzados agua-solvatante.

Parámetros de asociación (ε^{AB}/R en K, β adimensional).  Para el agua se usan
los valores CPA estándar (Kontogeorgis et al.); la solvatación CO₂–agua usa los
valores de combinación de PVTsim/CPA.  Todos se pueden ajustar en ASSOC_PARAMS.
"""

import numpy as np

R_GAS = 10.7316          # psia·ft³/(lbmol·°R)
IDX_AGUA = 13

# ── Parámetros de asociación por componente ─────────────────────────────────
# scheme: '4C' (agua), 'solvation' (solo cruza con agua), None (inerte).
# eps: energía de asociación ε^{AB}/R en KELVIN (se convierte a °R en el cálculo).
# beta: volumen de asociación (adimensional).
# Orden interno N₂,CO₂,C1..C9,H₂O (índices 0..13).
ASSOC = {
    13: {'scheme': '4C', 'eps_K': 2003.25, 'beta': 0.0692},   # H₂O (Kontogeorgis 4C)
    1:  {'scheme': 'solv', 'eps_K': 0.0,    'beta': 0.0},      # CO₂ (solvatación cruzada)
}

# Solvatación cruzada: ε (K) y β para el par (solvatante, agua).  El solvatante
# no auto-asocia; su fuerza de cruce con el agua se define aquí.  Valores tipo
# CPA para CO₂–H₂O (Tsivintzelis et al. 2011): ε_cross/R≈0 con la regla CR-1
# usa ε_cross = ε_agua/2; β_cross ajustable.  Para H₂S análogo.
SOLV_CROSS = {
    1: {'eps_K': 1001.6, 'beta': 0.0500},    # CO₂–H₂O
}


def _sites(scheme):
    """Número de sitios (A, B) para un esquema.  4C: 2 A + 2 B."""
    if scheme == '4C':
        return 2, 2
    return 0, 0


def _delta_matrix(z, b_i, rho, T_R):
    """Fuerza de asociación Δ entre sitios, agregada por par de componentes.
    Devuelve una matriz efectiva Δ_ij (agua/solvatante) para resolver X.

    Se usa el esquema simplificado de dos tipos de sitio (A=donor, B=aceptor).
    Para 4C simétrico, un sitio A de i solo enlaza con un sitio B de j.
    """
    N = len(z)
    T_K = T_R/1.8
    g = 1.0/(1.0 - 1.9*(b_i @ z)*rho/4.0)     # RDF de CPA (η = bρ/4, b de mezcla)
    Delta = np.zeros((N, N))
    for i in range(N):
        ai = ASSOC.get(i)
        if ai is None:
            continue
        for j in range(N):
            aj = ASSOC.get(j)
            if aj is None:
                continue
            bij = 0.5*(b_i[i] + b_i[j])
            # energía y volumen de cruce
            if i == IDX_AGUA and j == IDX_AGUA:
                epsK = ai['eps_K']; beta = ai['beta']
            elif i == IDX_AGUA or j == IDX_AGUA:
                solv = j if i == IDX_AGUA else i
                sc = SOLV_CROSS.get(solv)
                if sc is None:
                    continue
                epsK = sc['eps_K']; beta = sc['beta']
            else:
                continue      # solvatante-solvatante no asocia
            eps_R = epsK*1.8                       # K → °R (ε/R en °R)
            Delta[i, j] = g*(np.exp(eps_R/T_R) - 1.0)*bij*beta
    return Delta


def _solve_X(z, b_i, rho, T_R, max_iter=200, tol=1e-12):
    """Resuelve las fracciones de sitios no enlazados X.
    Modelo de dos sitios por componente asociante (A y B), con 4C simétrico:
    X_A de i depende de los sitios B de todos los j, y viceversa.  Para 4C
    simétrico X_A = X_B por componente, así que se resuelve un X por componente
    asociante con multiplicidad de sitios.
    Devuelve dict {i: X_i} y la matriz Delta usada."""
    N = len(z)
    Delta = _delta_matrix(z, b_i, rho, T_R)
    idx = [i for i in range(N) if ASSOC.get(i) is not None and z[i] > 1e-300]
    if not idx:
        return {}, Delta
    # multiplicidad de sitios aceptores por componente (para 4C, 2 sitios B)
    nB = {}
    for i in idx:
        a, b = _sites(ASSOC[i]['scheme'])
        nB[i] = b if ASSOC[i]['scheme'] == '4C' else 1   # solvatante: 1 sitio efectivo
    X = {i: 0.5 for i in idx}
    for _ in range(max_iter):
        Xn = {}
        for i in idx:
            s = 0.0
            for j in idx:
                # sitios A de i enlazan con sitios B de j
                s += z[j]*nB[j]*X[j]*Delta[i, j]
            Xn[i] = 1.0/(1.0 + rho*s)
        err = max(abs(Xn[i]-X[i]) for i in idx)
        X = Xn
        if err < tol:
            break
    return X, Delta


def lnphi_assoc(z, b_i, Z, T_R, P):
    """Contribución de asociación a ln φ_i (CPA).

    Usa la formulación de la derivada del término de Helmholtz de asociación
    respecto a n_i (Michelsen-Hendriks).  Para el esquema de sitios simétrico:

        ln φ_i^assoc = Σ_{A_i} ln X_{A_i}  −  (1/2) ρ (∂/∂n_i)[...]
    En la forma práctica de CPA (Kontogeorgis & Folas 2010, ec. 8.35):

        ln φ_i^assoc = Σ_{A_i} ln X_{A_i}  −  (1/2) Σ_j x_j Σ_{B_j}(1−X_{B_j}) · (1/g)(∂g/∂n_i)

    Se implementa la parte dominante Σ_A ln X_A por componente (con multiplicidad
    de sitios), que es la contribución principal a la fugacidad; el término del
    RDF se incluye de forma compacta vía la derivada de η.
    """
    z = np.asarray(z, dtype=float)
    N = len(z)
    v = Z*R_GAS*T_R/P              # volumen molar (ft³/lbmol)
    rho = 1.0/v                    # densidad molar
    X, Delta = _solve_X(z, b_i, rho, T_R)
    lnphi = np.zeros(N)
    if not X:
        return lnphi
    # multiplicidad de sitios por componente
    mult = {}
    for i in X:
        a, b = _sites(ASSOC[i]['scheme'])
        mult[i] = (a + b) if ASSOC[i]['scheme'] == '4C' else 1
    # término principal: Σ_sites ln X  (por componente, con su multiplicidad)
    for i in X:
        lnphi[i] += mult[i]*np.log(X[i])
    # término del RDF (aproximación compacta): −(1/2)·(Σ_j x_j m_j (1−X_j))·(b_i/b_m/(1/1.9η−1))
    bm = float(b_i @ z)
    eta = bm*rho/4.0
    Qsum = 0.0
    for j in X:
        Qsum += z[j]*mult[j]*(1.0 - X[j])
    dg_over_g = (1.9/4.0)*rho/(1.0 - 1.9*eta)     # (1/g)(∂g/∂ρ)·(ρ derivadas)
    for i in range(N):
        lnphi[i] += -0.5*Qsum*dg_over_g*b_i[i]
    return lnphi


def hay_asociacion(z):
    z = np.asarray(z, dtype=float)
    return len(z) > IDX_AGUA and z[IDX_AGUA] > 1e-12

# -*- coding: utf-8 -*-
"""
Regla de mezcla de Huron-Vidal para mezclas hidrocarburo-agua.

Basado en Lindeloff & Michelsen, "Phase Envelope Calculations for
Hydrocarbon-Water Mixtures", SPE Journal, sept. 2003 (SPE 85971), que es el
enfoque usado por PVTsim. La regla de mezcla original de Huron-Vidal (1979)
con un modelo NRTL modificado para la energía de exceso G^E permite representar
mezclas con componentes polares (agua) manteniendo la EOS cúbica clásica.

Propiedad clave (requisito 4 del paper): con α_ij = 0 y los parámetros de
energía g elegidos según las ecuaciones 6-8 del paper, la regla Huron-Vidal
se REDUCE EXACTAMENTE a la regla de mezcla cuadrática clásica

    a_m = Σ_i Σ_j z_i z_j √(a_i a_j)(1 - k_ij)

para los pares hidrocarburo-hidrocarburo. Solo los pares que involucran agua
(HC-polar y polar-polar) usan parámetros de interacción propios.

    IMPORTANTE — reducción exacta:
    Este módulo se activa SOLO cuando el agua está presente en la mezcla. En
    ausencia de agua, el motor sigue usando la regla cuadrática original de
    eos.py y los resultados son idénticos bit a bit a los actuales. Esto
    preserva toda la validación previa de los 13 componentes hidrocarburos.

Ecuaciones implementadas (numeración del paper):
    (3)  a = b · [ Σ z_i (a_i/b_i)  −  G^E/ln2 ]
    (4)  G^E/RT = Σ_i z_i · [ Σ_j τ_ji b_j z_j exp(-α_ji τ_ji) ]
                             / [ Σ_k b_k z_k exp(-α_ki τ_ki) ]
    (5)  τ_ji = (g_ji - g_ii) / (R T)
    (6)  α_ij = 0                       (para pares HC-HC → reducción cuadrática)
    (7)  g_ii = -(a_i/b_i) ln2
    (8)  g_ji = -2 √(b_i b_j)/(b_i+b_j) · √(g_ii g_jj) (1 - k_ij)

Con (6)-(8), la ec. (3) devuelve la a_m cuadrática. Para pares con agua se
usan α_ij y g_ij específicos (parámetros de interacción del agua, pendientes
de calibrar contra PVTsim/HYSYS).

NOTA: Los parámetros de interacción del agua (WATER_KIJ y WATER_ALPHA) son
PRELIMINARES (valores de literatura). Se reemplazarán por los de PVTsim/HYSYS
cuando estén disponibles, sin cambiar la estructura del cálculo.
"""

import numpy as np

LN2 = np.log(2.0)


# ── Índice del agua en el orden canónico extendido ──────────────────────────
# El agua se añade como componente 14 (índice 13), tras C9.
IDX_AGUA = 13


# ── Parámetros de interacción del agua (PRELIMINARES) ───────────────────────
# k_ij del agua con cada componente HC + consigo misma. Valores típicos de
# literatura para agua-hidrocarburo con PR (grandes, ~0.5, muy distintos de los
# HC-HC). Se calibrarán contra PVTsim/HYSYS. Orden: N₂, CO₂, C1..C9, H₂O.
# (Estos son marcadores; el agua-agua es 0.)
WATER_KIJ_PRELIM = {
    # componente_idx : k_ij(agua, componente)
    0:  0.48,   # N₂ - H₂O
    1:  0.20,   # CO₂ - H₂O  (menor, CO₂ algo soluble)
    2:  0.50,   # C1 - H₂O
    3:  0.50,   # C2 - H₂O
    4:  0.50,   # C3 - H₂O
    5:  0.50,   # iC4 - H₂O
    6:  0.50,   # nC4 - H₂O
    7:  0.50,   # iC5 - H₂O
    8:  0.50,   # nC5 - H₂O
    9:  0.50,   # C6 - H₂O
    10: 0.50,   # C7 - H₂O
    11: 0.50,   # C8 - H₂O
    12: 0.50,   # C9 - H₂O
    13: 0.00,   # H₂O - H₂O
}

# α_ij (nonrandomness) para pares con agua. α=0 reduce a cuadrática; para agua
# se usa un valor típico NRTL (~0.2-0.3) que introduce el efecto de composición
# local. PRELIMINAR.
WATER_ALPHA_PRELIM = 0.0   # arranque conservador: α=0 → reducción cuadrática
                           # incluso para el agua, hasta calibrar. Así la
                           # Etapa 1 es un cambio estructural SIN efecto físico
                           # nuevo todavía (validable como no-regresión).


# ── Propiedades preliminares del agua (literatura) ──────────────────────────
# Se reemplazarán por las de PVTsim/HYSYS. En unidades internas (°R, psia).
AGUA_TC_R   = 1164.77      # 647.096 K → °R
AGUA_PC_PSI = 3200.11      # 22.064 MPa → psia
AGUA_OMEGA  = 0.3443
AGUA_PM     = 18.0153


def hay_agua(z, tol=1e-12):
    """True si la composición incluye agua en fracción apreciable."""
    z = np.asarray(z, dtype=float)
    return len(z) > IDX_AGUA and z[IDX_AGUA] > tol


def construir_g(ai, bi, kij_arr, alpha_water=WATER_ALPHA_PRELIM):
    """Matrices g_ij y α_ij para la regla Huron-Vidal, a partir de los
    parámetros de la EOS (ai·α(T) y bi) y la matriz k_ij extendida.

    Para pares HC-HC devuelve exactamente los g de las ecuaciones 7-8 con α=0,
    lo que reproduce la regla cuadrática. Para pares con agua usa α = alpha_water.

    ai, bi : arrays (N,) de a_i·α(T) y b_i.
    kij_arr: matriz (N,N) de interacción binaria (incluye fila/col del agua).
    Devuelve (g, alpha) matrices (N,N).
    """
    N = len(ai)
    gii = -(ai / bi) * LN2                      # ec. 7 (diagonal)
    g = np.zeros((N, N))
    alpha = np.zeros((N, N))
    for i in range(N):
        g[i, i] = gii[i]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            # ec. 8: g_ji = -2 √(b_i b_j)/(b_i+b_j) √(g_ii g_jj)(1-k_ij)
            fac = 2.0 * np.sqrt(bi[i]*bi[j]) / (bi[i]+bi[j])
            g[j, i] = -fac * np.sqrt(gii[i]*gii[j]) * (1.0 - kij_arr[i, j])
            # α: 0 para HC-HC; alpha_water si alguno es agua
            if i == IDX_AGUA or j == IDX_AGUA:
                alpha[j, i] = alpha_water
    return g, alpha


def am_huron_vidal(z, ai, bi, kij_arr, T, alpha_water=WATER_ALPHA_PRELIM):
    """Parámetro atractivo a_m por la regla Huron-Vidal (ec. 3-4).

    z  : fracciones molares (N,)
    ai : a_i·α(T) (N,)
    bi : b_i (N,)
    kij_arr : matriz k_ij (N,N)
    T  : temperatura (°R)
    Devuelve a_m (float).
    """
    z = np.asarray(z, dtype=float)
    N = len(z)
    bm = float(z @ bi)
    g, alpha = construir_g(ai, bi, kij_arr, alpha_water)
    R = 10.7316
    tau = (g - np.diag(g).reshape(1, N)) / (R * T)   # τ_ji = (g_ji - g_ii)/RT
    # G^E/RT (ec. 4)
    E = np.exp(-alpha * tau)                          # exp(-α_ji τ_ji)
    num = (tau * (bi.reshape(1, N) * z.reshape(1, N)) * E)   # τ_ji b_j z_j exp(...)
    # sumas por columna i: Σ_j
    GE_RT = 0.0
    for i in range(N):
        den_i = float(np.sum(bi * z * E[:, i]))
        if den_i <= 0:
            continue
        num_i = float(np.sum(tau[:, i] * bi * z * E[:, i]))
        GE_RT += z[i] * num_i / den_i
    GE = GE_RT * R * T
    # ec. 3: a = b [ Σ z_i a_i/b_i − G^E/ln2 ]
    suma = float(np.sum(z * ai / bi))
    am = bm * (suma - GE / LN2)
    return am

# -*- coding: utf-8 -*-
"""
tension_superficial.py — Tensiones interfaciales entre fases.

Gas–líquido de hidrocarburos: Weinaug y Katz (1943), parachores [P]_i:
    σ^(1/4) = Σ_i [P]_i·(ρ̄_L·x_i − ρ̄_V·y_i)      σ en mN/m (= dyn/cm)
ρ̄ = densidades molares (mol/cm³) de las fases calculadas con la ecuación de
estado (con el traslado de Peneloux si está activo).

Agua–hidrocarburo: Firoozabadi y Ramey (1988):
    σ^(1/4) = a1·Δρ^(1 + b1)/T_r^0.3125
Δρ = |ρ_agua − ρ_HC| (g/cm³); T_r = T/Σx_i·Tc_i de la fase de hidrocarburo;
a1, b1 según el intervalo de Δρ.
"""
import numpy as np

# Parachores (N2 … nC9, agua).  El agua disuelta en las fases de
# hidrocarburos no se incluye en la suma (parachor 0), como en PVTsim.
PARACHOR = (41.0, 78.0, 77.3, 108.9, 151.9, 181.5, 191.7, 225.0, 233.9,
            271.0, 311.0, 351.0, 391.0, 0.0)

_FR = ((0.2, 2.2062, -0.94716), (0.5, 2.915, -0.76852), (1e9, 3.3858, -0.62590))


def gas_liquido(x, y, rho_mol_L, rho_mol_V):
    """σ (mN/m) entre líquido (x, ρ̄_L mol/cm³) y gas (y, ρ̄_V mol/cm³)."""
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    n = min(len(x), len(y), len(PARACHOR))
    P = np.asarray(PARACHOR[:n])
    s = float(rho_mol_L*np.dot(P, x[:n]) - rho_mol_V*np.dot(P, y[:n]))
    return s**4 if s > 0 else 0.0


def agua_hc(rho_agua_gcm3, rho_hc_gcm3, comp_hc, Tc_R, T_R):
    """σ (mN/m) entre la fase acuosa y una fase de hidrocarburo."""
    dr = abs(rho_agua_gcm3 - rho_hc_gcm3)
    if dr <= 0:
        return 0.0
    c = np.asarray(comp_hc, dtype=float)
    n = min(len(c), len(Tc_R))
    c = c[:n]/c[:n].sum()
    Tr = T_R/float(np.dot(c, np.asarray(Tc_R, dtype=float)[:n]))
    for lim, a1, b1 in _FR:
        if dr < lim:
            break
    return (a1*dr**(1.0 + b1)/Tr**0.3125)**4

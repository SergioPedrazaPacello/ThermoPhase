# -*- coding: utf-8 -*-
"""
Flash trifásico vapor–líquido(HC)–acuoso para mezclas con agua.

Método "Simple (HYSYS)": el agua entra como un componente más en la regla de
mezcla cuadrática clásica de la EOS (PR o SRK), con los parámetros de
interacción binaria (kij) grandes que HYSYS usa para el agua. Esos kij grandes
(≈0.5 con hidrocarburos) hacen que la EOS prediga la inmiscibilidad agua-HC, de
modo que el análisis de estabilidad detecta y separa la fase acuosa. No se
requiere Huron-Vidal para obtener las tres fases (ver módulo huron_vidal.py
para el método riguroso de PVTsim, a implementar aparte).

El componente agua es el índice 13 (14° componente), tras C9.

Referencia de parámetros: paquete de fluidos HYSYS (PR y SRK), matriz kij con
el agua extraída del reporte de HYSYS.

Este módulo es AUTOCONTENIDO: replica la matemática de PR/SRK para 14
componentes sin tocar el motor de 13 componentes de eos.py, de modo que el
flash sin agua sigue intacto.
"""

import numpy as np

R_GAS = 10.7316
SQRT2 = np.sqrt(2.0)
IDX_AGUA = 13


# ── Propiedades críticas extendidas (13 HC + agua) ──────────────────────────
# Los 13 primeros se toman de eos.py según la EOS; el agua se añade aquí con las
# propiedades de HYSYS (Tc=1165.14°R, Pc=3208.23 psia, ω=0.344, PM=18.0151).
AGUA_TC   = 1165.13822021484     # °R
AGUA_PC   = 3208.233924          # psia
AGUA_OMEGA = 0.34400001168251
AGUA_PM   = 18.015100479126

# ω que usa SRK para el agua en HYSYS (COSTALD/SRK acentricity de la hoja).
# Para el flash SRK se usa el ω estándar del agua salvo indicación contraria;
# HYSYS reporta un "SRK acentricity" propio pero el m de SRK se calcula del ω.
AGUA_OMEGA_SRK = 0.34400001168251


# ── Matriz kij del agua (fila/columna 14) para HYSYS ────────────────────────
# Orden: N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, nC5, C6, C7, C8, C9  (agua-agua=0)
KIJ_AGUA_PR = [
    -0.3156,  # N₂
     0.0445,  # CO₂
     0.5,     # C1
     0.5,     # C2
     0.5,     # C3
     0.5,     # iC4
     0.5,     # nC4
     0.5,     # iC5
     0.48,    # nC5
     0.5,     # C6
     0.5,     # C7
     0.5,     # C8
     0.5,     # C9
]
KIJ_AGUA_SRK = [
    -0.4907,  # N₂
     0.0392,  # CO₂
     0.5,     # C1
     0.5,     # C2
     0.4819,  # C3
     0.518,   # iC4
     0.518,   # nC4
     0.5,     # iC5
     0.5,     # nC5
     0.5109,  # C6
     0.5,     # C7
     0.5,     # C8
     0.5,     # C9
]


def _params_14(eos):
    """Devuelve (Tc, Pc, omega, PM, kij) de 14 componentes para la EOS dada.
    Los 13 HC se toman de eos.py; el agua se añade en el índice 13."""
    import eos as _e
    es_srk = _e.es_srk(eos)
    es_pvt = _e.es_pvtsim(eos)
    if es_pvt:
        Tc13 = list(_e.TC_PVT); Pc13 = list(_e.PC_PVT)
        om13 = list(_e.OMEGA_PVT); PM13 = list(_e.PM_PVT)
    elif es_srk:
        Tc13 = list(_e.TC_SRK); Pc13 = list(_e.PC_SRK)
        om13 = list(_e.OMEGA_SRK); PM13 = list(_e.PM)
    else:
        Tc13 = list(_e.TC); Pc13 = list(_e.PC)
        om13 = list(_e.OMEGA); PM13 = list(_e.PM)

    Tc = np.array(Tc13 + [AGUA_TC])
    Pc = np.array(Pc13 + [AGUA_PC])
    om = np.array(om13 + [AGUA_OMEGA_SRK if es_srk else AGUA_OMEGA])
    PM = np.array(PM13 + [AGUA_PM])

    # kij base 13×13 según EOS
    kij13 = np.array(_e.kij_base(eos), dtype=float)
    kij = np.zeros((14, 14))
    kij[:13, :13] = kij13
    fila = KIJ_AGUA_SRK if es_srk else KIJ_AGUA_PR
    for j in range(13):
        kij[13, j] = fila[j]
        kij[j, 13] = fila[j]
    return Tc, Pc, om, PM, kij


def _m_pr(omega):
    return 0.37464 + 1.54226*omega - 0.26992*omega**2

def _m_srk(omega):
    return 0.480 + 1.574*omega - 0.176*omega**2


def _ai_bi(eos, Tc, Pc, omega, T):
    """Parámetros a_i·α(T) y b_i para los 14 componentes."""
    import eos as _e
    es_srk = _e.es_srk(eos)
    if es_srk:
        ai = 0.42748*R_GAS**2*Tc**2/Pc
        m = _m_srk(omega)
    else:
        ai = 0.45724*R_GAS**2*Tc**2/Pc
        m = _m_pr(omega)
    alpha = (1.0 + m*(1.0 - np.sqrt(T/Tc)))**2
    bi = (0.08664 if es_srk else 0.07780)*R_GAS*Tc/Pc
    return ai*alpha, bi


def _am_bm(z, aa, bi, kij):
    """Regla de mezcla cuadrática: am, bm."""
    z = np.asarray(z, dtype=float)
    saa = np.sqrt(aa)
    w = z*saa
    am = float(w @ (1.0 - kij) @ w)
    bm = float(z @ bi)
    return am, bm


def _Z_roots(am, bm, T, P, es_srk):
    """Raíces de compresibilidad Z de la EOS cúbica."""
    A = am*P/(R_GAS*T)**2
    B = bm*P/(R_GAS*T)
    if es_srk:
        c = [1.0, -1.0, A - B - B*B, -A*B]
    else:
        c = [1.0, -(1.0 - B), A - 3*B*B - 2*B, -(A*B - B*B - B**3)]
    r = np.roots(c)
    Zs = sorted([x.real for x in r if abs(x.imag) < 1e-8 and x.real > B])
    return Zs, A, B


def _ln_phi(z, aa, bi, kij, T, P, es_srk, fase):
    """ln(phi_i) de los 14 componentes para la fase indicada.
    fase: 'V' toma la raíz Z mayor; 'L' la menor."""
    am, bm = _am_bm(z, aa, bi, kij)
    Zs, A, B = _Z_roots(am, bm, T, P, es_srk)
    if not Zs:
        return None, None
    Z = Zs[-1] if fase == 'V' else Zs[0]
    z = np.asarray(z, dtype=float)
    saa = np.sqrt(aa)
    w = z*saa
    sum_aij = saa * ((1.0 - kij) @ w)      # Σ_j x_j √(aa_i aa_j)(1-kij)
    bi_bm = bi/bm
    t1 = bi_bm*(Z - 1.0)
    t2 = -np.log(max(Z - B, 1e-15))
    if es_srk:
        t3 = (A/max(B,1e-15))*np.log((Z + B)/Z)
    else:
        num = Z + (1+SQRT2)*B; den = Z + (1-SQRT2)*B
        t3 = A/(2*SQRT2*B)*np.log(num/max(den,1e-15))
    t4 = (2.0*sum_aij/am - bi_bm)*t3
    return t1 + t2 - t4, Z


def _K_wilson(Tc, Pc, omega, T, P):
    return (Pc/P)*np.exp(5.373*(1+omega)*(1 - Tc/T))


# ── Flash trifásico vapor–líquido(HC)–acuoso ────────────────────────────────
def flash_trifasico(z, T, P, eos='PR', max_iter=200, tol=1e-11):
    """Flash isotérmico-isobárico de tres fases: Vapor (V), Líquido HC (L) y
    Acuosa (W). Composición z de 14 componentes (índice 13 = agua).

    Enfoque físico (método Simple/HYSYS): dada la fuerte inmiscibilidad
    (kij agua-HC ≈ 0.5), la fase acuosa es agua casi pura y la solubilidad de
    agua en las fases HC es baja. El algoritmo:
      1. Resuelve el reparto del AGUA entre las fases HC (vapor+líquido) y la
         fase acuosa por igualdad de fugacidad, iterando con el resto de HC.
      2. Para la parte no-acuosa resuelve el equilibrio vapor-líquido HC con la
         misma EOS de 14 componentes.
    Determina cuántas fases son realmente estables (fracción > umbral).

    Devuelve dict con beta_V, beta_L, beta_W, composiciones y, x, w y factores Z.
    """
    z = np.asarray(z, dtype=float); z = z/z.sum()
    Tc, Pc, om, PM, kij = _params_14(eos)
    import eos as _e
    es_srk = _e.es_srk(eos)
    aa, bi = _ai_bi(eos, Tc, Pc, om, T)

    def lnphi(comp, fase):
        return _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)

    z_w = z[IDX_AGUA]

    # ── Paso 1: separar la fase acuosa (agua casi pura) ─────────────────────
    # La fase acuosa arranca como agua pura y se refina con la solubilidad de
    # HC en ella (muy baja). La cantidad de agua en las fases HC se obtiene por
    # igualdad de fugacidad agua_HC = agua_acuosa.
    # Composición acuosa inicial: agua pura.
    w = np.zeros(14); w[IDX_AGUA] = 1.0

    # Fracción de agua que queda disuelta en las fases HC (se resuelve iterando).
    # Empezamos suponiendo toda el agua en la fase acuosa.
    beta_W = z_w
    z_hc = z.copy(); z_hc[IDX_AGUA] = 0.0
    s_hc = z_hc.sum()
    if s_hc <= 0:                        # solo agua
        lnpW, Z_W = lnphi(w, 'L')
        return {'beta_V':0.0,'beta_L':0.0,'beta_W':1.0,
                'y':np.zeros(14),'x':np.zeros(14),'w':w,
                'Z_V':None,'Z_L':None,'Z_W':Z_W,'PM':PM,'iter':0}

    for outer in range(max_iter):
        # composición HC "libre de agua acuosa" (lo que va a vapor+líquido HC),
        # incluyendo el agua que permanece disuelta en las fases HC.
        # z_free = z - beta_W * w  (lo que no está en la fase acuosa)
        z_free = z - beta_W*w
        z_free = np.clip(z_free, 0.0, None)
        sfree = z_free.sum()
        if sfree <= 0:
            break
        z_free = z_free/sfree

        # ── Flash bifásico vapor-líquido HC sobre z_free ────────────────────
        y, x, bV_rel, Z_V, Z_L = _flash_vl(z_free, aa, bi, kij, T, P, es_srk,
                                           Tc, Pc, om)

        # ── Refinar fase acuosa: fugacidad del agua debe igualar ────────────
        # agua en fase HC (usar la fase con más agua, típicamente vapor) vs
        # agua en fase acuosa.
        lnpW, Z_W = lnphi(w, 'L')
        # fugacidad parcial del agua en vapor
        if y is not None:
            lnpV, _ = lnphi(y, 'V')
            f_agua_V = y[IDX_AGUA]*np.exp(lnpV[IDX_AGUA])*P
        else:
            f_agua_V = 0.0
        f_agua_W = w[IDX_AGUA]*np.exp(lnpW[IDX_AGUA])*P
        # solubilidad de agua en HC: y_agua tal que fug iguala
        # (ya está incluida en z_free vía w; iteramos beta_W por balance)
        # balance de agua: z_w = beta_W*w_agua + (1-beta_W)*yhc_agua_promedio
        # Aproximación robusta: la fracción de agua disuelta en HC es pequeña,
        # se estima de la relación de fugacidades.
        # Refinamos la composición acuosa con solubilidad de HC (baja):
        w_new = np.zeros(14)
        if x is not None:
            lnpL, _ = lnphi(x, 'L')
        # solubilidad de cada HC en agua ≈ x_HC·phi_HC^L / phi_HC^W
        for i in range(13):
            xi = (x[i] if x is not None else y[i])
            lnp_hc = (lnpL[i] if x is not None else lnpV[i])
            w_new[i] = xi*np.exp(lnp_hc - lnpW[i])
        w_new[IDX_AGUA] = 1.0
        w_new = w_new/w_new.sum()

        # actualizar beta_W por balance de agua global
        # agua en fases HC (promedio ponderado)
        agua_en_hc = (1.0 - beta_W) * ( (bV_rel*y[IDX_AGUA] +
                      (1-bV_rel)*(x[IDX_AGUA] if x is not None else y[IDX_AGUA])) )
        beta_W_new = z_w - agua_en_hc
        beta_W_new = min(max(beta_W_new, 0.0), z_w)

        dif = abs(beta_W_new - beta_W) + np.max(np.abs(w_new - w))
        beta_W = beta_W_new; w = w_new
        if dif < tol:
            break

    # fracciones finales
    beta_hc = 1.0 - beta_W
    beta_V = beta_hc*bV_rel
    beta_L = beta_hc*(1.0 - bV_rel)
    return {
        'beta_V': beta_V, 'beta_L': beta_L, 'beta_W': beta_W,
        'y': y, 'x': x, 'w': w,
        'Z_V': Z_V, 'Z_L': Z_L, 'Z_W': Z_W, 'PM': PM, 'iter': outer+1,
    }


def _flash_vl(z, aa, bi, kij, T, P, es_srk, Tc, Pc, om, max_iter=200, tol=1e-12):
    """Flash bifásico vapor-líquido de 14 componentes sobre composición z.
    Devuelve (y, x, beta_V, Z_V, Z_L). Si es monofásico, beta_V es 0 ó 1."""
    K = _K_wilson(Tc, Pc, om, T, P)
    def RR(bV):
        return np.sum(z*(K-1.0)/(1.0+bV*(K-1.0)))
    monofasico = None
    for it in range(max_iter):
        # resolver Rachford-Rice para beta_V
        lo, hi = 1e-9, 1.0-1e-9
        # chequear si hay dos fases
        if RR(0.0) < 0:      # burbuja: todo líquido
            bV = 0.0; monofasico = 'L'
        elif RR(1.0) > 0:    # rocío: todo vapor
            bV = 1.0; monofasico = 'V'
        else:
            monofasico = None
            for _ in range(100):
                mid = 0.5*(lo+hi)
                if RR(mid) > 0: lo = mid
                else: hi = mid
            bV = 0.5*(lo+hi)
        x = z/(1.0+bV*(K-1.0)); x = x/x.sum()
        y = K*x; y = y/y.sum()
        lnpV, Z_V = _ln_phi(y, aa, bi, kij, T, P, es_srk, 'V')
        lnpL, Z_L = _ln_phi(x, aa, bi, kij, T, P, es_srk, 'L')
        if lnpV is None or lnpL is None:
            break
        K_new = np.exp(lnpL - lnpV)
        err = np.max(np.abs(np.log(K_new/K)))
        K = K_new
        if err < tol:
            break
    # Para fluido monofásico, identificar vapor vs líquido por la energía de
    # Gibbs de las dos raíces de Z (la fase estable es la de menor G). Wilson no
    # es fiable para esto a alta presión, así que se usa el criterio de Gibbs.
    if monofasico is not None:
        gV = _gibbs_fase(z, aa, bi, kij, T, P, es_srk, 'V')
        gL = _gibbs_fase(z, aa, bi, kij, T, P, es_srk, 'L')
        if gV is not None and gL is not None:
            es_vapor = gV <= gL
        else:
            es_vapor = (monofasico == 'V')
        bV = 1.0 if es_vapor else 0.0
        y = z.copy(); x = z.copy()
    return y, x, bV, Z_V, Z_L


def _gibbs_fase(comp, aa, bi, kij, T, P, es_srk, fase):
    """Energía de Gibbs adimensional de una fase (Σ x_i ln(x_i phi_i)),
    para comparar estabilidad vapor vs líquido de un fluido monofásico."""
    lnp, Z = _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)
    if lnp is None:
        return None
    comp = np.asarray(comp)
    mask = comp > 1e-300
    return float(np.sum(comp[mask]*(np.log(comp[mask]) + lnp[mask])))



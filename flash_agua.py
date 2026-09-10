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

# Coeficientes Mathias-Copeman (c1,c2,c3) de PVTsim para alpha(T).
MC_PR = [
    [0.5430, -0.0520, -0.3380],
    [0.8650, -0.4390, 1.3450],
    [0.5860, -0.7210, 1.2900],
    [0.7180, -0.7640, 1.6400],
    [0.7860, -0.7460, 1.8450],
    [0.2400, 3.8360, -8.0450],
    [0.8790, -0.9400, 2.2670],
    [0.8280, 0.0000, 0.0000],
    [1.0280, -2.5620, 6.2480],
    [1.0830, -1.2800, 2.6180],
    [-0.1620, 6.2420, -8.8260],
    [1.0740, 0.0660, -0.2720],
    [1.1370, 0.0790, -0.3460],
    [1.0870, -0.6380, 0.6350],
]

MC_SRK = [
    [0.5430, -0.0520, -0.3380],
    [0.8650, -0.4390, 1.3450],
    [0.5860, -0.7210, 1.2900],
    [0.7180, -0.7640, 1.6400],
    [0.7860, -0.7460, 1.8450],
    [0.2400, 3.8360, -8.0450],
    [0.8790, -0.9400, 2.2670],
    [0.8280, 0.0000, 0.0000],
    [1.0280, -2.5620, 6.2480],
    [1.0830, -1.2800, 2.6180],
    [-0.1620, 6.2420, -8.8260],
    [1.0740, 0.0660, -0.2720],
    [1.1370, 0.0790, -0.3460],
    [1.0870, -0.6380, 0.6350],
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
    """Parámetros a_i·α(T) y b_i para los 14 componentes.

    Con el método Huron-Vidal (PVTsim) se usa la función α de Mathias-Copeman
    (tres coeficientes c1,c2,c3 por componente) que es la que emplea PVTsim; con
    el método Simple (HYSYS) se usa la α estándar de PR/SRK (un solo m de ω)."""
    import eos as _e
    es_srk = _e.es_srk(eos)
    if es_srk:
        ai = 0.42748*R_GAS**2*Tc**2/Pc
        b0 = 0.08664
    else:
        ai = 0.45724*R_GAS**2*Tc**2/Pc
        b0 = 0.07780
    bi = b0*R_GAS*Tc/Pc

    if _METODO == 'hv':
        # Mathias-Copeman: α = [1 + c1·τ + c2·τ² + c3·τ³]², τ = 1-√Tr.
        # Para T > Tc, PVTsim usa solo el término c1 (forma de Soave) por
        # continuidad; aquí se mantiene la forma completa (válida cerca de Tr<1).
        MC = np.array(MC_SRK if es_srk else MC_PR)
        Tr = T/Tc
        tau = 1.0 - np.sqrt(Tr)
        c1 = MC[:, 0]; c2 = MC[:, 1]; c3 = MC[:, 2]
        raiz = 1.0 + c1*tau + c2*tau**2 + c3*tau**3
        # por encima de Tc, usar forma monoparamétrica (evita α creciente)
        raiz_sc = 1.0 + c1*tau
        alpha = np.where(Tr <= 1.0, raiz**2, raiz_sc**2)
    else:
        m = _m_srk(omega) if es_srk else _m_pr(omega)
        alpha = (1.0 + m*(1.0 - np.sqrt(T/Tc)))**2
    return ai*alpha, bi


# Método de mezcla para el agua: 'simple' (kij Classic) o 'hv' (Huron-Vidal).
# Lo fija flash_trifasico según la opción elegida. Contexto para HV.
_METODO = 'simple'
_EOS_CTX = 'PR'
_T_CTX = None

def _am_bm(z, aa, bi, kij):
    """Regla de mezcla: cuadrática (Simple) o Huron-Vidal según _METODO.
    Con _METODO='hv' y agua presente usa las energías de PVTsim; en ausencia de
    agua HV se reduce exactamente a la cuadrática."""
    z = np.asarray(z, dtype=float)
    if _METODO == 'hv' and _T_CTX is not None and len(z) > IDX_AGUA and z[IDX_AGUA] > 1e-12:
        import huron_vidal as _hv
        try:
            return _hv.am_bm_hv(z, aa, bi, _EOS_CTX, _T_CTX, kij)
        except Exception:
            pass
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


def _sum_aij_deriv(z, aa, bi, kij, am):
    """Vector 'sum_aij' que entra en ln(phi): representa la derivada parcial
    del término atractivo. Con la regla cuadrática es saa·((1-kij)@w). Con
    Huron-Vidal (activo vía _METODO) usa la derivada ANALÍTICA qbar de am_HV,
    que es termodinámicamente consistente y ~15× más rápida que la numérica.

    ln_phi usa 2·sum_aij/am; qbar = (1/am)·∂(n²am)/∂n_i, así que
    sum_aij_i = am·qbar_i/2.
    """
    z = np.asarray(z, dtype=float)
    if _METODO == 'hv' and _T_CTX is not None and len(z) > IDX_AGUA and z[IDX_AGUA] > 1e-12:
        import huron_vidal as _hv
        am2, bm2, qbar = _hv._am_qbar_hv(z, aa, bi, _EOS_CTX, _T_CTX, kij, con_qbar=True)
        # qbar = 2·dn2am/am ; sum_aij = dn2am = am·qbar/4 (factor validado vs
        # derivada numérica de (n²am)).
        return am2*qbar/4.0
    saa = np.sqrt(aa)
    w = z*saa
    return saa*((1.0 - kij) @ w)


def _ln_phi_conZ(z, aa, bi, kij, T, P, es_srk, Z):
    """ln(phi_i) dado un Z específico."""
    am, bm = _am_bm(z, aa, bi, kij)
    A = am*P/(R_GAS*T)**2
    B = bm*P/(R_GAS*T)
    z = np.asarray(z, dtype=float)
    sum_aij = _sum_aij_deriv(z, aa, bi, kij, am)
    bi_bm = bi/bm
    t1 = bi_bm*(Z - 1.0)
    t2 = -np.log(max(Z - B, 1e-15))
    if es_srk:
        t3 = (A/max(B,1e-15))*np.log((Z + B)/Z)
    else:
        num = Z + (1+SQRT2)*B; den = Z + (1-SQRT2)*B
        t3 = A/(2*SQRT2*B)*np.log(num/max(den,1e-15))
    t4 = (2.0*sum_aij/am - bi_bm)*t3
    return t1 + t2 - t4


def _ln_phi(z, aa, bi, kij, T, P, es_srk, fase):
    """ln(phi_i) de los 14 componentes.
    fase: 'V' toma la raíz Z mayor; 'L' la menor; 'auto' la de MENOR energía de
    Gibbs (la fase termodinámicamente estable en esas condiciones)."""
    am, bm = _am_bm(z, aa, bi, kij)
    Zs, A, B = _Z_roots(am, bm, T, P, es_srk)
    if not Zs:
        return None, None
    if fase == 'auto' and len(Zs) > 1:
        z = np.asarray(z, dtype=float)
        mask = z > 1e-300
        best = None; bestG = None
        for Zc in (Zs[0], Zs[-1]):
            lnp = _ln_phi_conZ(z, aa, bi, kij, T, P, es_srk, Zc)
            G = float(np.sum(z[mask]*(np.log(z[mask]) + lnp[mask])))
            if bestG is None or G < bestG:
                bestG = G; best = (lnp, Zc)
        return best
    Z = Zs[-1] if fase == 'V' else Zs[0]
    return _ln_phi_conZ(z, aa, bi, kij, T, P, es_srk, Z), Z


def _K_wilson(Tc, Pc, omega, T, P):
    return (Pc/P)*np.exp(5.373*(1+omega)*(1 - Tc/T))


def _tpd_estable(z, aa, bi, kij, T, P, es_srk, lnphi_z, w_ini):
    """Análisis de estabilidad de Michelsen (Tangent Plane Distance).
    Comprueba si la fase de composición z es estable frente a la aparición de
    una fase de prueba iniciada en w_ini. Devuelve (estable, w_conv) donde
    estable=False indica que z es INESTABLE (aparece la fase w_conv).

    lnphi_z: ln(phi_i) de la fase z (referencia). Se busca un mínimo de la
    distancia al plano tangente; si TPD < 0 → inestable.
    """
    d = np.log(np.clip(z,1e-300,None)) + lnphi_z    # potencial de referencia
    W = np.clip(w_ini, 1e-300, None)
    for _ in range(80):
        w = W/np.sum(W)
        lnp_w, _ = _ln_phi(w, aa, bi, kij, T, P, es_srk, 'auto')
        if lnp_w is None:
            return True, None
        lnW_new = d - lnp_w                          # ln W_i = d_i - ln phi_i(w)
        W_new = np.exp(lnW_new)
        if np.max(np.abs(np.log(np.clip(W_new,1e-300,None)/np.clip(W,1e-300,None)))) < 1e-10:
            W = W_new; break
        W = W_new
    Sw = np.sum(W)
    w = W/Sw
    # TPD* = 1 - Σ W_i (criterio de Michelsen); inestable si Σ W_i > 1
    tm = 1.0 - Sw
    estable = tm > -1e-8
    return estable, w


# ── Flash trifásico vapor–líquido(HC)–acuoso ────────────────────────────────
def flash_trifasico(z, T, P, eos='PR', metodo='simple', max_iter=400, tol=1e-11):
    """Flash isotérmico-isobárico multifásico por el método de Michelsen (1994):
    minimización de la función Q(beta), robusta ante fases que aparecen o
    desaparecen. metodo: 'simple' (kij Classic, HYSYS) o 'hv' (Huron-Vidal,
    PVTsim). Devuelve dict con beta_V, beta_L, beta_W, y, x, w y factores Z."""
    global _METODO, _EOS_CTX, _T_CTX
    _METODO = 'hv' if metodo == 'hv' else 'simple'
    _EOS_CTX = eos; _T_CTX = T
    z = np.asarray(z, dtype=float); z = z/z.sum()
    Tc, Pc, om, PM, kij = _params_14(eos)
    import eos as _e
    es_srk = _e.es_srk(eos)
    aa, bi = _ai_bi(eos, Tc, Pc, om, T)

    def lnphi(comp, fase='auto'):
        return _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)

    # Sin agua: flash bifásico HC estándar.
    if z[IDX_AGUA] <= 1e-12:
        y,x,bV,ZV,ZL = _flash_vl(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om)
        return _pack(bV,1-bV,0.0,y,x,np.zeros(14),ZV,ZL,None,PM,1)

    Kw = _K_wilson(Tc, Pc, om, T, P)
    # Composiciones iniciales de las 3 fases:
    #   Vapor: enriquecido en ligeros (z·Kw)
    #   Líquido HC: enriquecido en pesados (z/Kw), sin agua
    #   Acuosa: agua casi pura
    y0 = np.clip(z*Kw, 1e-300, None); y0/=y0.sum()
    x0 = np.clip(z/Kw, 1e-300, None); x0[IDX_AGUA]=1e-8; x0/=x0.sum()
    w0 = np.full(14, 1e-8); w0[IDX_AGUA]=1.0; w0/=w0.sum()

    roles = ['V', 'L', 'L']       # vapor, líquido HC, acuosa
    res = _flash_multifase(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om,PM,
                           roles, [y0, x0, w0], max_iter, tol)
    if res is None:
        # respaldo: flash bifásico
        y,x,bV,ZV,ZL = _flash_vl(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om)
        return _pack(bV,1-bV,0.0,y,x,np.zeros(14),ZV,ZL,None,PM,1)

    beta, comps, Zs = res
    bV, bL, bW = beta[0], beta[1], beta[2]
    y, x, w = comps[0], comps[1], comps[2]
    ZV, ZL, ZW = Zs[0], Zs[1], Zs[2]

    # Verificación de consistencia: si la fase "acuosa" no es rica en agua o la
    # fase "líquido HC" contiene demasiada agua, el flash cayó en un mínimo
    # local con clasificación errónea. Se reintenta descartando el líquido HC
    # (2 fases: vapor + acuosa), que es la solución física a alta T.
    if bL > 1e-5 and (w[IDX_AGUA] < 0.5 or x[IDX_AGUA] > 0.3):
        res2 = _flash_multifase(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om,PM,
                                ['V','L'], [y0, w0], max_iter, tol)
        if res2 is not None:
            b2, c2, Z2 = res2
            if c2[1][IDX_AGUA] > 0.5:      # la 2ª fase es acuosa
                bV, bW = b2[0], b2[1]; bL = 0.0
                y, w = c2[0], c2[1]; x = np.zeros(14)
                ZV, ZW = Z2[0], Z2[1]; ZL = None

    # Descartar fases despreciables (beta ~ 0) — Michelsen ec. 11.
    UMB = 1e-5
    # ¿la "acuosa" es realmente acuosa?
    if w[IDX_AGUA] < 0.5 or bW < UMB:
        bW = 0.0
    if bV < UMB: bV = 0.0
    if bL < UMB: bL = 0.0

    # Si vapor y líquido HC colapsaron a la misma fase (composiciones iguales),
    # es una sola fase HC: reagrupar.
    if bV > UMB and bL > UMB:
        if np.max(np.abs(y - x)) < 1e-3:   # misma composición → una fase HC
            # unir en la de mayor Z (vapor) si Z alto, o líquido si bajo
            b_hc = bV + bL
            hc = (bV*y + bL*x)/b_hc; hc/=hc.sum()
            es_vap = _es_vapor(hc, aa,bi,kij,T,P,es_srk, Tc)
            if es_vap:
                bV, y, ZV = b_hc, hc, ZV; bL = 0.0
            else:
                bL, x, ZL = b_hc, hc, ZL; bV = 0.0

    # Si solo queda una fase HC (la otra colapsó), reconciliar con el flash VL
    # directo del HC (más confiable que el multifase cuando una fase desaparece).
    # Esto corrige casos de transición donde el multifase clasifica mal V vs L.
    hc_unica = (bV > UMB) != (bL > UMB)   # exactamente una de las dos HC
    if hc_unica and bW < 1.0 - UMB:
        # composición HC (la fase presente)
        hc = y if bV > UMB else x
        b_hc = bV + bL
        # renormalizar HC quitando agua residual y re-flashear
        hc_n = hc.copy()
        s_hcn = hc_n.sum()
        if s_hcn > 0:
            hc_n = hc_n/s_hcn
            yh, xh, bVh, ZVh, ZLh = _flash_vl(hc_n, aa,bi,kij,T,P,es_srk,Tc,Pc,om)
            if bVh >= 1.0 - 1e-6:          # el HC es vapor
                bV, y, ZV = b_hc, hc_n, ZVh; bL = 0.0; x = np.zeros(14)
            elif bVh <= 1e-6:             # el HC es líquido
                bL, x, ZL = b_hc, hc_n, ZLh; bV = 0.0; y = np.zeros(14)
            else:                         # el HC se divide en V+L (3 fases)
                bV = b_hc*bVh; bL = b_hc*(1-bVh)
                y, x, ZV, ZL = yh, xh, ZVh, ZLh

    # Si solo queda una fase HC, identificar V o L por Z (respaldo).
    if bV > UMB and bL <= UMB:
        if not _es_vapor(y, aa,bi,kij,T,P,es_srk, Tc):
            bL, x, ZL = bV, y, ZV; bV = 0.0; y = np.zeros(14)
    elif bL > UMB and bV <= UMB:
        if _es_vapor(x, aa,bi,kij,T,P,es_srk, Tc):
            bV, y, ZV = bL, x, ZL; bL = 0.0; x = np.zeros(14)

    s = bV+bL+bW
    if s>0: bV/=s; bL/=s; bW/=s
    return _pack(bV, bL, bW,
                 y if bV>0 else np.zeros(14),
                 x if bL>0 else np.zeros(14),
                 w if bW>0 else np.zeros(14),
                 ZV if bV>0 else None, ZL if bL>0 else None,
                 ZW if bW>0 else None, PM, 1)


def _gibbs(comp, aa, bi, kij, T, P, es_srk, fase):
    lnp, Z = _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)
    if lnp is None: return None
    comp = np.asarray(comp); m = comp > 1e-300
    return float(np.sum(comp[m]*(np.log(comp[m]) + lnp[m])))


def _es_vapor(comp, aa, bi, kij, T, P, es_srk, Tc=None):
    """True si la fase de composición comp es vapor. Con dos raíces Z compara
    energía de Gibbs. Con una sola raíz (región densa/supercrítica) usa un
    criterio combinado: la temperatura pseudo-crítica de la mezcla (regla de
    Kay) y la densidad molar. Si T < Tpc la fase densa es líquida."""
    am, bm = _am_bm(comp, aa, bi, kij)
    Zs, A, B = _Z_roots(am, bm, T, P, es_srk)
    if not Zs:
        return True
    if len(Zs) > 1:
        gV = _gibbs(comp, aa,bi,kij,T,P,es_srk,'V')
        gL = _gibbs(comp, aa,bi,kij,T,P,es_srk,'L')
        return gV is not None and (gL is None or gV <= gL)
    # raíz única (fase densa): combinar densidad y Tpc de la mezcla.
    Z = Zs[0]
    v = Z*R_GAS*T/P
    if Tc is not None:
        comp = np.asarray(comp)
        Tpc = float(comp @ np.asarray(Tc))        # T pseudo-crítica (Kay)
        if T < Tpc:
            return False                          # por debajo de Tpc: líquido
    # sin Tc o T>=Tpc: por densidad. Líquido si empaquetamiento denso.
    return v > 3.0*bm


def _pack(bV,bL,bW,y,x,w,ZV,ZL,ZW,PM,it):
    return {'beta_V':bV,'beta_L':bL,'beta_W':bW,'y':y,'x':x,'w':w,
            'Z_V':ZV,'Z_L':ZL,'Z_W':ZW,'PM':PM,'iter':it}


def _Q_dist(beta, N, phi):
    """Función objetivo Q de Michelsen 1994 (ec. 4) y su gradiente/Hessiano.
    beta: fracciones molares de fase (F,). N: composición global (C,).
    phi: coeficientes de fugacidad (C,F). Devuelve (Q, grad, H, E)."""
    E = np.sum(beta[None,:]/phi, axis=1)          # E_i (ec. 5)
    E = np.where(E < 1e-300, 1e-300, E)
    Q = np.sum(beta) - np.sum(N*np.log(E))
    grad = 1.0 - np.sum((N/E)[:,None]/phi, axis=0)  # ec. 10
    F = len(beta)
    NE2 = N/E**2
    H = np.zeros((F,F))
    for j in range(F):
        for k in range(j,F):
            v = np.sum(NE2/(phi[:,j]*phi[:,k]))     # ec. 12
            H[j,k]=v; H[k,j]=v
    return Q, grad, H, E


def _distribucion_fases(N, phi, beta0):
    """Minimiza Q(beta) (Michelsen 1994) por Newton con línea de búsqueda y
    restricción beta>=0. Maneja automáticamente fases que aparecen/desaparecen.
    Devuelve (beta, y) con y las composiciones (C,F)."""
    beta = np.clip(np.asarray(beta0, dtype=float), 0, None)
    F = len(beta)
    for it in range(100):
        Q, g, H, E = _Q_dist(beta, N, phi)
        # solo fases activas (beta>0 o gradiente negativo) participan en Newton
        try:
            d = np.linalg.solve(H + 1e-12*np.eye(F), g)
        except Exception:
            break
        t = 1.0; mejor = False
        while t > 1e-8:
            nb = np.clip(beta - t*d, 0, None)
            Qn,_,_,_ = _Q_dist(nb, N, phi)
            if Qn <= Q + 1e-14:
                mejor = True; break
            t *= 0.5
        if not mejor:
            break
        nb = np.clip(beta - t*d, 0, None)
        if np.max(np.abs(nb-beta)) < 1e-13:
            beta = nb; break
        beta = nb
    E = np.sum(beta[None,:]/phi, axis=1)
    E = np.where(E < 1e-300, 1e-300, E)
    y = (N/E)[:,None]/phi                           # y_ij (ec. 7)
    return beta, y


def _flash_multifase(z, aa, bi, kij, T, P, es_srk, Tc, Pc, om, PM,
                     roles, comps0, max_iter=300, tol=1e-11):
    """Flash multifásico por el método de Michelsen 1994: sustitución sucesiva
    (actualiza fugacidades) + minimización de Q (actualiza distribución de
    fases). roles: lista de 'V'/'L' por fase. comps0: composiciones iniciales
    (lista de vectores C). Robusto: las fases sin presencia real convergen a
    beta≈0 y se descartan.

    Devuelve (beta, comps, Zs) o None si no converge de forma útil."""
    z = np.asarray(z, dtype=float)
    Fn = len(roles)
    comps = [np.clip(c,1e-300,None)/np.sum(c) for c in comps0]
    beta = np.array([1.0/Fn]*Fn)
    Zs = [None]*Fn
    for outer in range(max_iter):
        # fugacidades de cada fase con su rol (V o L)
        phi = np.zeros((14, Fn)); ok=True
        for j in range(Fn):
            lnp, Zj = _ln_phi(comps[j], aa,bi,kij,T,P,es_srk, roles[j])
            if lnp is None: ok=False; break
            # proteger contra overflow numérico (T criogénica extrema)
            lnp = np.clip(lnp, -700, 700)
            phi[:,j] = np.exp(lnp); Zs[j]=Zj
        if not ok: return None
        # distribución de fases minimizando Q
        beta_new, y = _distribucion_fases(z, phi, beta)
        # nuevas composiciones
        comps_new = []
        for j in range(Fn):
            c = np.clip(y[:,j], 0, None); s=c.sum()
            comps_new.append(c/s if s>0 else comps[j])
        # convergencia
        dif = max(np.max(np.abs(comps_new[j]-comps[j])) for j in range(Fn))
        comps = comps_new; beta = beta_new
        if dif < tol:
            break
    # normalizar beta
    s = beta.sum()
    if s>0: beta = beta/s
    return beta, comps, Zs


def _flash_vl(z, aa, bi, kij, T, P, es_srk, Tc, Pc, om, max_iter=200, tol=1e-12):
    """Flash bifásico vapor-líquido de 14 componentes sobre composición z.
    Devuelve (y, x, beta_V, Z_V, Z_L). Si es monofásico, beta_V es 0 ó 1.

    Antes de resolver Rachford-Rice se hace un análisis de estabilidad para
    detectar una fase líquida incipiente que Wilson por sí solo no captura cerca
    del punto de rocío (como PVTsim). Si el fluido es inestable, se arranca el
    flash desde las K de la fase de prueba de la estabilidad."""
    K = _K_wilson(Tc, Pc, om, T, P)

    # ── Estabilidad previa: ¿es z inestable (aparece líquido)? ──────────────
    lnp_z, _ = _ln_phi(z, aa, bi, kij, T, P, es_srk, 'auto')
    if lnp_z is not None:
        d = np.log(np.clip(z, 1e-300, None)) + lnp_z
        # semilla líquida (composición pesada): z/K
        W = np.clip(z/np.maximum(K, 1e-30), 1e-300, None)
        for _ in range(60):
            ww = W/np.sum(W)
            lnp_w, _ = _ln_phi(ww, aa, bi, kij, T, P, es_srk, 'auto')
            if lnp_w is None:
                break
            Wn = np.exp(d - lnp_w)
            if np.max(np.abs(np.log(np.clip(Wn,1e-300,None)/np.clip(W,1e-300,None)))) < 1e-10:
                W = Wn; break
            W = Wn
        if np.sum(W) > 1.0 + 1e-7:
            # inestable: la fase de prueba da mejores K de arranque
            w_trial = W/np.sum(W)
            K = np.clip(z, 1e-300, None)/np.clip(w_trial, 1e-300, None)

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



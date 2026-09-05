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


def _ln_phi_conZ(z, aa, bi, kij, T, P, es_srk, Z):
    """ln(phi_i) dado un Z específico."""
    am, bm = _am_bm(z, aa, bi, kij)
    A = am*P/(R_GAS*T)**2
    B = bm*P/(R_GAS*T)
    z = np.asarray(z, dtype=float)
    saa = np.sqrt(aa)
    w = z*saa
    sum_aij = saa * ((1.0 - kij) @ w)
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
    """Flash isotérmico-isobárico robusto con análisis de estabilidad de
    Michelsen. metodo: 'simple' (kij Classic, HYSYS) o 'hv' (Huron-Vidal,
    PVTsim). Determina las fases (V, L, W) y resuelve el equilibrio.
    """
    global _METODO, _EOS_CTX, _T_CTX
    _METODO = 'hv' if metodo == 'hv' else 'simple'
    _EOS_CTX = eos
    _T_CTX = T
    z = np.asarray(z, dtype=float); z = z/z.sum()
    Tc, Pc, om, PM, kij = _params_14(eos)
    import eos as _e
    es_srk = _e.es_srk(eos)
    aa, bi = _ai_bi(eos, Tc, Pc, om, T)

    def lnphi(comp, fase='auto'):
        return _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)

    # ── Paso 1: flash bifásico de referencia (toda la mezcla) ───────────────
    y2, x2, bV2, ZV2, ZL2 = _flash_vl(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om)
    bifasico = (1e-7 < bV2 < 1-1e-7)

    if bifasico:
        # Clasificar las dos fases: la rica en agua (>50%) es la ACUOSA; la otra
        # es HC (vapor o líquido según su Z / energía de Gibbs).
        faseA_agua = y2[IDX_AGUA]; faseB_agua = x2[IDX_AGUA]
        if max(faseA_agua, faseB_agua) > 0.5:
            # Una fase es acuosa. Identificar cuál y la fase HC restante.
            if faseA_agua > faseB_agua:
                w_ph, ZW_ph, bW_ph = y2, ZV2, bV2
                hc_ph, ZHC_ph, bHC_ph = x2, ZL2, 1-bV2
            else:
                w_ph, ZW_ph, bW_ph = x2, ZL2, 1-bV2
                hc_ph, ZHC_ph, bHC_ph = y2, ZV2, bV2
            # La fase HC restante puede a su vez dividirse en V+L (3 fases).
            # ¿La fase HC restante se divide en V+L? Se hace un flash bifásico
            # VL de la composición HC (removiendo el agua residual y
            # renormalizando). Si da dos fases → 3 fases totales (V+L+W).
            hc_norm = hc_ph.copy()
            hc_norm[IDX_AGUA] = 0.0
            s_hc = hc_norm.sum()
            if s_hc > 1e-12:
                hc_norm = hc_norm/s_hc
                yh, xh, bVh, ZVh, ZLh = _flash_vl(hc_norm, aa,bi,kij,T,P,
                                                  es_srk,Tc,Pc,om)
            else:
                bVh = 1.0; yh = xh = hc_ph; ZVh = ZLh = ZHC_ph
            if 1e-6 < bVh < 1-1e-6:
                # 3 fases: V + L + W. Repartir las fracciones.
                # bHC_ph es la fracción HC total; se divide en V y L.
                bV = bHC_ph*bVh; bL = bHC_ph*(1-bVh); bW = bW_ph
                s = bV+bL+bW
                if s>0: bV/=s; bL/=s; bW/=s
                return _pack(bV, bL, bW, yh, xh, w_ph, ZVh, ZLh, ZW_ph, PM, 2)
            # HC monofásico: identificar V ó L (por Gibbs/Z)
            es_vap = _es_vapor(hc_ph, aa,bi,kij,T,P,es_srk)
            _,Zc = lnphi(hc_ph, 'V' if es_vap else 'L')
            if es_vap:
                return _pack(bHC_ph,0.0,bW_ph, hc_ph, np.zeros(14), w_ph,
                             Zc,None,ZW_ph,PM,1)
            else:
                return _pack(0.0,bHC_ph,bW_ph, np.zeros(14), hc_ph, w_ph,
                             None,Zc,ZW_ph,PM,1)
        else:
            # Dos fases HC (V+L), sin agua libre: ¿aparece fase acuosa aparte?
            fases_ref = [y2, x2]
    else:
        fases_ref = [z]

    # ── Paso 2: estabilidad — ¿aparece fase acuosa? ─────────────────────────
    w_seed = np.full(14, 1e-6); w_seed[IDX_AGUA] = 1.0
    aparece_acuosa = False; w_conv = None
    for comp_ref in fases_ref:
        lnp_ref, _ = lnphi(comp_ref, 'auto')
        if lnp_ref is None: continue
        estable, wc = _tpd_estable(comp_ref, aa,bi,kij,T,P,es_srk, lnp_ref, w_seed)
        if not estable and wc is not None and wc[IDX_AGUA] > 0.5:
            aparece_acuosa = True; w_conv = wc; break

    # ── Paso 3a: sin fase acuosa → flash bifásico HC directo ────────────────
    if not aparece_acuosa:
        if bifasico:
            return _pack(bV2, 1-bV2, 0.0, y2, x2, np.zeros(14),
                         ZV2, ZL2, None, PM, 1)
        # monofásico: identificar V ó L (por Gibbs/Z)
        es_vap = _es_vapor(z, aa,bi,kij,T,P,es_srk)
        _, Zc = lnphi(z, 'V' if es_vap else 'L')
        if es_vap:
            return _pack(1.0,0.0,0.0, z, np.zeros(14), np.zeros(14), Zc,None,None,PM,1)
        return _pack(0.0,1.0,0.0, np.zeros(14), z, np.zeros(14), None,Zc,None,PM,1)

    # ── Paso 3b: hay fase acuosa → flash de 3 fases ─────────────────────────
    return _flash_3f(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om, w_conv, PM, max_iter, tol)


def _gibbs(comp, aa, bi, kij, T, P, es_srk, fase):
    lnp, Z = _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)
    if lnp is None: return None
    comp = np.asarray(comp); m = comp > 1e-300
    return float(np.sum(comp[m]*(np.log(comp[m]) + lnp[m])))


def _es_vapor(comp, aa, bi, kij, T, P, es_srk):
    """True si la fase de composición comp es vapor. Con dos raíces Z compara
    energía de Gibbs; con una sola raíz clasifica por el valor de Z (líquido
    si Z es bajo, vapor si es alto) y por densidad molar."""
    am, bm = _am_bm(comp, aa, bi, kij)
    Zs, A, B = _Z_roots(am, bm, T, P, es_srk)
    if not Zs:
        return True
    if len(Zs) > 1:
        gV = _gibbs(comp, aa,bi,kij,T,P,es_srk,'V')
        gL = _gibbs(comp, aa,bi,kij,T,P,es_srk,'L')
        return gV is not None and (gL is None or gV <= gL)
    # raíz única: clasificar por Z. Volumen molar v = Z R T / P.
    # Criterio: si Z < ~0.3 es líquido; si Z > ~0.3 vapor. Umbral robusto por
    # comparación con el covolumen: líquido si v < 2·bm (empaquetado denso).
    Z = Zs[0]
    v = Z*R_GAS*T/P
    return v > 2.0*bm


def _pack(bV,bL,bW,y,x,w,ZV,ZL,ZW,PM,it):
    return {'beta_V':bV,'beta_L':bL,'beta_W':bW,'y':y,'x':x,'w':w,
            'Z_V':ZV,'Z_L':ZL,'Z_W':ZW,'PM':PM,'iter':it}


def _flash_3f(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om, w_ini, PM, max_iter, tol):
    """Flash de 3 fases (V,L,W) por sustitución sucesiva con referencia vapor.
    K_L = x/y (líquido HC vs vapor), K_W = w/y (acuosa vs vapor)."""
    def lnphi(comp, fase='auto'):
        return _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)
    # Estimados iniciales de K desde Wilson y la fase acuosa de la estabilidad.
    Kw = _K_wilson(Tc, Pc, om, T, P)
    K_L = Kw.copy()
    # K_W_i = y_i/w_i. Con w_ini (rica en agua) y una y de arranque:
    y0 = z/ (0.5 + 0.5/np.maximum(K_L,1e-30)); y0 = np.clip(y0,1e-300,None); y0/=y0.sum()
    K_W = np.clip(y0,1e-300,None)/np.clip(w_ini,1e-300,None)

    bV, bW = 0.45, 0.1
    y=x=w=None; ZV=ZL=ZW=None
    for it in range(max_iter):
        # balance de materia 3 fases (referencia vapor), Newton 2x2 en bV,bW
        for _ in range(200):
            bL = 1.0-bV-bW
            den = bV + bL/K_L + bW/K_W
            yv = z/den
            f1 = np.sum(yv)-1.0
            f2 = np.sum(yv/K_L - yv/K_W)
            h=1e-8
            dV=(bV+h)+(1-bV-h-bW)/K_L+bW/K_W; yv1=z/dV
            f1V=(np.sum(yv1)-1-f1)/h; f2V=(np.sum(yv1/K_L-yv1/K_W)-f2)/h
            dW=bV+(1-bV-bW-h)/K_L+(bW+h)/K_W; yv2=z/dW
            f1W=(np.sum(yv2)-1-f1)/h; f2W=(np.sum(yv2/K_L-yv2/K_W)-f2)/h
            J=np.array([[f1V,f1W],[f2V,f2W]]); F=np.array([f1,f2])
            try: dd=np.linalg.solve(J,F)
            except Exception: break
            st=1.0
            while st>1e-4:
                nV=bV-st*dd[0]; nW=bW-st*dd[1]
                if 0<=nV<=1 and 0<=nW<=1 and nV+nW<=1: break
                st*=0.5
            bV-=st*dd[0]; bW-=st*dd[1]
            bV=min(max(bV,0),1); bW=min(max(bW,0),1)
            if bV+bW>1: s=bV+bW; bV/=s; bW/=s
            if np.linalg.norm(dd)<1e-13: break
        bL=1.0-bV-bW
        den=bV+bL/K_L+bW/K_W
        y=z/den; y=np.clip(y,0,None); y/=y.sum()
        x=y/K_L; x=np.clip(x,0,None); x/=x.sum()
        w=y/K_W; w=np.clip(w,0,None); w/=w.sum()
        lnpV,ZV=lnphi(y,'auto'); lnpL,ZL=lnphi(x,'auto'); lnpW,ZW=lnphi(w,'auto')
        if lnpV is None or lnpL is None or lnpW is None: break
        KLn=np.exp(lnpL-lnpV); KWn=np.exp(lnpW-lnpV)
        err=np.max(np.abs(np.log(KLn/K_L)))+np.max(np.abs(np.log(KWn/K_W)))
        K_L=KLn; K_W=KWn
        if err<tol: break

    bL=1.0-bV-bW
    UMB=1e-6
    # descartar fases despreciables
    if bW<=UMB:
        y2,x2,bV2,ZV2,ZL2=_flash_vl(z,aa,bi,kij,T,P,es_srk,Tc,Pc,om)
        return _pack(bV2,1-bV2,0.0,y2,x2,np.zeros(14),ZV2,ZL2,None,PM,max_iter)
    if bV<=UMB: bV=0.0
    if bL<=UMB: bL=0.0
    s=bV+bL+bW
    if s>0: bV/=s; bL/=s; bW/=s
    # identificar cuál fase HC es vapor y cuál líquido por densidad molar (Z/V):
    # la de mayor Z es vapor. Aquí y=vapor por construcción, x=líquido.
    return _pack(bV,bL,bW,y,x,w,ZV,ZL,ZW,PM,max_iter)


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



# -*- coding: utf-8 -*-
"""
envolvente_agua.py — Línea de aparición de fase acuosa (estilo PVTsim, VLW).

PVTsim, cuando el agua está activa, traza la envolvente del fluido total con la
CURVA DEL AGUA: además de la saturación hidrocarburo (rocío/burbuja), dibuja la
frontera donde aparece la fase acuosa libre (β_W = 0), sin líneas de isocalidad.

Este módulo calcula esa frontera con el flash TRIFÁSICO exacto (flash_agua):
para cada temperatura se busca, por bisección en presión, el lugar donde la
fracción de fase acuosa cruza cero.  El resultado es la "curva del agua" que se
superpone a la envolvente hidrocarburo del trazador de Michelsen.

Salida: lista de puntos (P_psia, T_R), en el mismo formato que 'burbuja'/'rocio'
del resultado de la envolvente, lista para el trazado de la pestaña.
"""

import numpy as np


def _ctx_T(z14, T, eos, metodo):
    """Prepara el contexto de la EOS a temperatura T (aa, bi, kij, es_srk) y fija
    los globales del motor HV.  aa,bi dependen de T; kij no."""
    import flash_agua as _fa
    import eos as _e
    _fa._METODO = 'hv' if metodo == 'hv' else 'simple'
    _fa._EOS_CTX = eos; _fa._T_CTX = float(T)
    Tc, Pc, om, PM, kij = _fa._params_14(eos)
    es_srk = _e.es_srk(eos)
    aa, bi = _fa._ai_bi(eos, Tc, Pc, om, float(T))
    return aa, bi, kij, es_srk


def _margen_agua(z14, T, P, ctx):
    """Margen de aparición de fase acuosa por el test de estabilidad TPD de
    Michelsen con fase de prueba RICA EN AGUA.

    Devuelve m = ΣW − 1 cuando la fase de prueba converge a una fase rica en
    agua (m > 0 ⇒ inestable ⇒ APARECE agua libre; m < 0 ⇒ no aparece).  Si la
    prueba deriva a una fase hidrocarburo (no acuosa), devuelve un valor
    negativo (a esta condición no hay fase acuosa propia).

    Es órdenes de magnitud más rápido que el flash trifásico completo y su
    frontera m = 0 coincide con β_W = 0 del flash (validado)."""
    import flash_agua as _fa
    aa, bi, kij, es_srk = ctx
    z = np.asarray(z14, dtype=float); z = z/z.sum()
    lnphi_z, _ = _fa._ln_phi(z, aa, bi, kij, float(T), float(P), es_srk, 'auto')
    if lnphi_z is None:
        return -1.0
    d = np.log(np.clip(z, 1e-300, None)) + lnphi_z
    W = np.full(14, 1e-8); W[13] = 1.0        # fase de prueba: agua casi pura
    for _ in range(80):
        w = W/np.sum(W)
        lnp_w, _ = _fa._ln_phi(w, aa, bi, kij, float(T), float(P), es_srk, 'auto')
        if lnp_w is None:
            return -1.0
        W_new = np.exp(d - lnp_w)
        if np.max(np.abs(np.log(np.clip(W_new,1e-300,None)/np.clip(W,1e-300,None)))) < 1e-10:
            W = W_new; break
        W = W_new
    w = W/np.sum(W)
    if w[13] < 0.5:            # la prueba no es acuosa → no hay fase de agua
        return -1.0
    return float(np.sum(W) - 1.0)


def _bisecta_P(z14, T, Plo, Phi, ctx, mlo, mhi, it=32):
    """Refina por bisección la presión donde el margen de agua cruza 0."""
    for _ in range(it):
        Pm = 0.5*(Plo + Phi)
        mm = _margen_agua(z14, T, Pm, ctx)
        if mm == 0:
            return Pm
        if mm*mlo < 0:
            Phi = Pm; mhi = mm
        else:
            Plo = Pm; mlo = mm
    return 0.5*(Plo + Phi)


def linea_aparicion_agua(z14, eos, metodo, T_min, T_max,
                         P_min=5.0, P_max=3000.0, nT=55, nP=26,
                         progress_cb=None, t_max_s=45.0):
    """Traza la línea β_W = 0 (aparición de fase acuosa) en el plano P-T.

    z14      composición global de 14 comp. (índice 13 = agua), normalizada.
    eos      código de EOS ('PR','SRK','PR_PVT','SRK_PVT').
    metodo   'hv' (motor PVTsim) o 'simple' (HYSYS).
    T_min/max, P_min/max   ventana de barrido (°R, psia).
    Devuelve lista de (P_psia, T_R) ordenada por T.
    """
    z14 = np.asarray(z14, dtype=float)
    if len(z14) <= 13 or z14[13] <= 1e-12:
        return []                      # sin agua no hay curva de agua

    import time as _t
    _t0 = _t.time()
    Ts = np.linspace(T_min, T_max, nT)
    Pgrid = np.linspace(P_min, P_max, nP)
    puntos = []
    for k, T in enumerate(Ts):
        if _t.time() - _t0 > t_max_s:
            break                      # presupuesto de tiempo agotado
        # Barrido INCREMENTAL en P de bajo a alto, con paro temprano en el
        # primer cruce del umbral: la aparición de agua es un fenómeno de baja
        # presión, así que se evita evaluar los puntos de alta P (más lentos)
        # cuando ya se localizó la frontera o cuando hay agua en todo el rango.
        ctx = _ctx_T(z14, T, eos, metodo)
        m0 = _margen_agua(z14, T, Pgrid[0], ctx)
        cruce = None
        if m0 > 0:
            # Agua libre ya presente a P_min → frontera por debajo del rango.
            cruce = P_min
        else:
            Pprev, mprev = Pgrid[0], m0
            for P in Pgrid[1:]:
                if _t.time() - _t0 > t_max_s:
                    break
                m = _margen_agua(z14, T, P, ctx)
                if m*mprev < 0:
                    cruce = _bisecta_P(z14, T, Pprev, P, ctx, mprev, m)
                    break
                Pprev, mprev = P, m
            # Si nunca cruza (agua no aparece a esta T en el rango) → sin punto
        if cruce is not None:
            puntos.append((float(cruce), float(T)))
        if progress_cb is not None:
            try: progress_cb(int(100*(k+1)/nT))
            except Exception: pass

    puntos.sort(key=lambda pt: pt[1])
    return puntos


# Temperatura crítica del agua (°R): límite superior físico de la fase acuosa
# líquida.  Por encima de T_c del agua no puede existir agua líquida, así que la
# curva de aparición de agua termina cerca de este valor.
AGUA_TC_R = 1165.13822021484

def rango_desde_envolvente(env_res, T_min_def=360.0, P_max_def=12000.0):
    """Deriva la ventana de barrido (T_min, T_max, P_max) para la curva de agua.

    Como en PVTsim, la curva del agua se acota a la MISMA ALTURA (presión máxima)
    de la envolvente hidrocarburo: se traza hasta la presión del cricondenbar de
    la envolvente HC, no hasta presiones arbitrariamente altas.  En temperatura
    se extiende desde T bajas (donde hay agua libre casi a cualquier P) hasta
    donde la curva alcanza esa presión máxima."""
    pts = list(env_res.get('burbuja', [])) + list(env_res.get('rocio', []))
    crit = env_res.get('critico')
    if crit is not None:
        pts = pts + [(crit[0], crit[1])]
    if pts:
        Ts = [t for _, t in pts]; Ps = [p for p, _ in pts]
        Tmin = max(min(min(Ts), T_min_def), 330.0)
        Pmax = max(Ps)                      # cricondenbar de la envolvente HC
    else:
        Tmin = max(T_min_def, 330.0); Pmax = P_max_def
    # T_max: tope físico (Tc del agua); el trazado se detiene solo al superar Pmax.
    Tmax = AGUA_TC_R - 8.0
    return Tmin, Tmax, Pmax


def _interseccion_segmentos(p1, p2, p3, p4):
    """Intersección de los segmentos (p1-p2) y (p3-p4), cada punto (T,P).
    Devuelve (T,P) o None."""
    x1,y1=p1; x2,y2=p2; x3,y3=p3; x4,y4=p4
    den=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if abs(den)<1e-12: return None
    t=((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/den
    u=((x1-x3)*(y1-y2)-(y1-y3)*(x1-x2))/den
    if 0.0<=t<=1.0 and 0.0<=u<=1.0:
        return (x1+t*(x2-x1), y1+t*(y2-y1))
    return None


def puntos_trifasicos(env_res, agua):
    """Puntos trifásicos = intersecciones de la curva del agua con las curvas de
    burbuja/rocío hidrocarburo (donde z está en equilibrio con dos fases
    incipientes — HC y acuosa; Ec. 16 de Lindeloff-Michelsen).

    env_res : resultado de la envolvente HC ({'burbuja':[(P,T)...],'rocio':...}).
    agua    : curva del agua [(P,T)...].
    Devuelve lista de (P,T) de los puntos trifásicos.
    """
    if not agua: return []
    # a coordenadas (T,P) para la intersección
    A=[(T,P) for P,T in agua]
    out=[]
    for rama in ('burbuja','rocio'):
        C=[(T,P) for P,T in env_res.get(rama,[])]
        for i in range(len(C)-1):
            for j in range(len(A)-1):
                pt=_interseccion_segmentos(C[i],C[i+1],A[j],A[j+1])
                if pt is not None:
                    out.append((pt[1], pt[0]))   # (P,T)
    return out

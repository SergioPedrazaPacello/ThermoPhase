"""
Motor Envolvente de Fases — Metodo de MICHELSEN (1980)
=======================================================
Continuacion por pseudo-longitud de arco con Newton-Raphson multivariable
y tangente exacta (vector nulo del Jacobiano fisico via SVD).

ESTRATEGIA BIDIRECCIONAL (soluciona la cola de baja presion de rocio):
  Trazo 1: desde burbuja a baja P → sube por burbuja → rodea critico
           → baja por rama de rocio superior hasta que la continuacion
           se detenga (tipicamente ~100-150 psi en gases livianos).
  Trazo 2: desde ROCIO a baja P → sube por rama de rocio inferior hasta
           conectarse con el Trazo 1. Arranca en la rama correcta y nunca
           compite con la de burbuja → resuelve el problema de la cola.
  Combinados: envolvente completa burbuja + rocio hasta presiones bajas.

SUBESPACIO ACTIVO: el sistema se arma solo con los componentes presentes
  (z_i > 0), reduciendo el Jacobiano de (NC+2) a (m+2). Gran aceleracion
  para composiciones con componentes ausentes (tipico en produccion).

Variables:  X = (lnK_1..lnK_m, lnT, lnP)   (m+2)
  g_i = lnK_i + ln phi_i(vapor) - ln phi_i(liquido) = 0   (i=1..m)
  g_{m+1} = SUM(K_i z_i) - 1 = 0
  g_{m+2} = t·(X - X_ref) - ds = 0      (restriccion de arco)
Ref: Michelsen, M.L. (1980). Fluid Phase Equilib. 4: 1-10.
"""
import numpy as np
import copy
import math
from eos import (
    NC, TC, PC, OMEGA, KIJ_DEFAULT,
    am, bm, AB, solve_Z, ln_phi_i, ln_phi_vec,
    get_eos, crit_props, es_srk,
)

R_GAS     = 10.7316
WILSON_C  = np.log(10.0) * (7.0/3.0)
kij_g     = None   # kij global, fijado en construir_envolvente
_max = max  # alias para max escalar (legibilidad)

# Criticas de la EOS ACTIVA (Tc, Pc, omega). Se fijan al inicio de
# construir_envolvente con crit_props(get_eos()), de modo que la siembra de
# Wilson use los parametros correctos de la EOS elegida (PR/SRK x HYSYS/PVTsim)
# y no los de HYSYS-PR fijos. Este era el motivo de que la envolvente de SRK
# PVTsim no trazara la cola de burbuja.
_TCa = list(TC)
_PCa = list(PC)
_OMa = list(OMEGA)

def _fijar_criticas_activas():
    global _TCa, _PCa, _OMa
    tc, pc, om, _pm = crit_props(get_eos())
    _TCa = list(tc); _PCa = list(pc); _OMa = list(om)


# ── Helpers de bajo nivel ────────────────────────────────────────────────────
def _set_kij(kij):
    global kij_g; kij_g = kij

def _cardano_Z(A, B):
    """(No usado en el flujo actual; kept for backwards-compat).
    Antes tenia el algoritmo PR hardcoded — se cambio a delegar en el
    engine para que responda a la EOS activa.
    """
    return solve_Z(A, B)

def _Ki_wilson(i, T, P):
    return (_PCa[i]/P) * np.exp(WILSON_C*(1+_OMa[i])*(1-_TCa[i]/T))

def _gibbs_dep_pr(Z, A, B):
    """Salida de Gibbs adimensional PR (sin constante)."""
    sqrt2 = math.sqrt(2.0)
    d = Z + (1 - sqrt2)*B; n = Z + (1 + sqrt2)*B
    if d <= 0: d = 1e-30
    if n <= 0: n = 1e-30
    if Z <= B: Z = B + 1e-12
    return Z - 1.0 - math.log(Z - B) - A/(2*sqrt2*B)*math.log(n/d)

def _gibbs_dep_srk(Z, A, B):
    """Salida de Gibbs adimensional SRK (sin constante).
    G^res/RT = Z - 1 - ln(Z - B) - (A/B) · ln((Z+B)/Z)
    """
    if Z <= B: Z = B + 1e-12
    ratio = (Z + B)/Z
    if ratio <= 0: ratio = 1e-30
    if B <= 0: B = 1e-30
    return Z - 1.0 - math.log(Z - B) - (A/B)*math.log(ratio)

def _gibbs_dep(Z, A, B):
    """Salida de Gibbs residual segun EOS activa. Menor = mas estable.
    CRITICO: esta es la funcion que usa _ln_phi_full para elegir entre las
    raices ZV y ZL. Si se usa la formula PR con SRK activa, la eleccion
    invierte la raiz y la envolvente Michelsen se rompe entera."""
    if es_srk(get_eos()):
        return _gibbs_dep_srk(Z, A, B)
    return _gibbs_dep_pr(Z, A, B)

def _ln_phi_full(comp_full, T, P, vapor=None):
    """
    Coeficientes de fugacidad con seleccion de Z por MINIMA energia de Gibbs.
    Funciona correctamente tanto para la rama de burbuja (incipiente vapor)
    como para la de rocio inferior (incipiente liquido, K<1 para livianos).
    El parametro vapor se ignora — la fisica elige la raiz correcta.
    """
    am_ = am(comp_full, T, kij_g); bm_ = bm(comp_full)
    A, B = AB(am_, bm_, T, P)
    ZV, ZL = solve_Z(A, B)
    # Elegir la raiz de menor Gibbs (fase fisicamente estable)
    gV = _gibbs_dep(ZV, A, B)
    gL = _gibbs_dep(ZL, A, B)
    Z  = ZV if gV <= gL else ZL
    return ln_phi_vec(comp_full, T, P, Z, am_, bm_, kij_g)


# ── Sistema de Michelsen (subespacio activo) ─────────────────────────────────
def _funciones(X, z, act, spec):
    """
    G(X) = 0 (dimension m+2). act = indices de componentes activos.
    spec: ('coord', idx, val)       -> X[idx] - val = 0
          ('arc',   t_arc, Xref, ds)-> t_arc·(X-Xref) - ds = 0  [restriccion de arco]
    En la restriccion de arco, el corrector no puede saltar a otra rama
    sin violar la distancia ds a lo largo de la tangente.
    """
    m  = len(act)
    T  = np.exp(X[m]); P = np.exp(X[m+1])
    K  = np.exp(X[:m])
    x_full = np.array(z, dtype=float)
    y_full = np.zeros(NC)
    Kz = K * x_full[act]; sKz = Kz.sum()
    if sKz <= 0: sKz = 1e-300
    for k, i in enumerate(act): y_full[i] = Kz[k]/sKz

    lpL = _ln_phi_full(x_full, T, P, False)
    lpV = _ln_phi_full(y_full, T, P, True)

    G = np.zeros(m+2)
    for k, i in enumerate(act): G[k] = X[k] + lpV[i] - lpL[i]
    G[m] = sKz - 1.0
    if spec[0] == 'coord':
        G[m+1] = X[spec[1]] - spec[2]
    else:
        _, t_arc, Xref, ds = spec
        G[m+1] = float(np.dot(t_arc, X - Xref)) - ds
    return G


def _funciones_beta(X, z, act, spec, beta):
    """
    Igual que _funciones, pero generaliza la ecuación de cierre a fracción
    de vapor FIJA beta (línea de isocalidad), en vez del caso límite beta=0
    (envolvente convencional, fase líquida con traza de vapor incipiente).

    Para beta=0 esto se reduce exactamente a _funciones (envolvente normal).
    Para 0<beta<1 traza el lugar geométrico donde Fv=beta es constante.

    Ecuación de Rachford-Rice generalizada (Michelsen & Mollerup):
        sum_i [ z_i (K_i - 1) / (1 + beta(K_i - 1)) ] = 0
    Las composiciones de cada fase (para evaluar phi) también cambian:
        x_i = z_i / (1 + beta(K_i-1))      y_i = K_i x_i
    """
    m  = len(act)
    T  = np.exp(X[m]); P = np.exp(X[m+1])
    K  = np.exp(X[:m])
    z_act = np.array(z, dtype=float)[act]

    denom = 1.0 + beta*(K-1.0)
    denom = np.where(np.abs(denom)<1e-12, 1e-12, denom)
    x_act = z_act/denom
    y_act = K*x_act

    x_full = np.array(z, dtype=float)   # componentes ausentes ya son 0
    y_full = np.zeros(NC)
    sx = 0.0; sy = 0.0
    for k, i in enumerate(act):
        x_full[i] = x_act[k]; y_full[i] = y_act[k]
        sx += x_act[k]; sy += y_act[k]
    if sx>0: 
        for i in act: x_full[i] = x_full[i]/sx
    if sy>0:
        for i in act: y_full[i] = y_full[i]/sy

    lpL = _ln_phi_full(x_full, T, P, False)
    lpV = _ln_phi_full(y_full, T, P, True)

    G = np.zeros(m+2)
    for k, i in enumerate(act): G[k] = X[k] + lpV[i] - lpL[i]
    G[m] = float(np.sum(z_act*(K-1.0)/denom))
    if spec[0] == 'coord':
        G[m+1] = X[spec[1]] - spec[2]
    else:
        _, t_arc, Xref, ds = spec
        G[m+1] = float(np.dot(t_arc, X - Xref)) - ds
    return G


def _jacobiano(X, z, act, spec, h=1e-6, Gfun=_funciones):
    n = len(act)+2
    J = np.zeros((n, n))
    for j in range(n):
        Xp = X.copy(); Xm = X.copy()
        Xp[j] += h; Xm[j] -= h
        J[:, j] = (Gfun(Xp, z, act, spec)
                 - Gfun(Xm, z, act, spec)) / (2*h)
    return J


def _resolver_punto(X0, z, act, spec, tol=1e-9, max_it=40, Gfun=_funciones):
    """Newton modificado: reutiliza el Jacobiano; lo refresca si el residual
    no mejora. La solucion converge al mismo G(X)=0 que Newton completo."""
    X   = X0.copy()
    G   = Gfun(X, z, act, spec)
    res = np.linalg.norm(G, ord=np.inf)
    if res < tol: return X, True
    J = _jacobiano(X, z, act, spec, Gfun=Gfun)
    refrescar = False
    for _ in range(max_it):
        if refrescar:
            J = _jacobiano(X, z, act, spec, Gfun=Gfun); refrescar = False
        try:
            dX = np.linalg.solve(J, -G)
        except np.linalg.LinAlgError:
            return X, False
        mx = np.max(np.abs(dX))
        if mx > 0.5: dX *= 0.5/mx
        X  = X + dX
        G  = Gfun(X, z, act, spec)
        rn = np.linalg.norm(G, ord=np.inf)
        if rn < tol: return X, True
        if rn > 0.9*res: refrescar = True
        res = rn
    return X, (res < tol*100)


def _tangente(X, z, act, t_prev=None, Gfun=_funciones):
    """Tangente exacta = vector nulo del Jacobiano fisico (SVD).
    Valida incluso en pliegues verticales (cricondentermica, cola baja P)."""
    n  = len(act)+2
    Jf = np.zeros((len(act)+1, n))
    h  = 1e-6
    for j in range(n):
        Xp = X.copy(); Xm = X.copy()
        Xp[j] += h; Xm[j] -= h
        fp = Gfun(Xp, z, act, ('coord',0,X[0]))[:len(act)+1]
        fm = Gfun(Xm, z, act, ('coord',0,X[0]))[:len(act)+1]
        Jf[:, j] = (fp - fm)/(2*h)
    try:
        _, _, Vt = np.linalg.svd(Jf)
    except np.linalg.LinAlgError:
        return t_prev
    t = Vt[-1]; nrm = np.linalg.norm(t)
    if nrm < 1e-30: return t_prev
    t = t/nrm
    if t_prev is not None and np.dot(t, t_prev) < 0: t = -t
    return t


# ── Inicializacion Wilson (burbuja y rocio) ──────────────────────────────────
def _init_burbuja(z, act, P0):
    """Punto de burbuja a baja presion via Wilson. Retorna X o None."""
    m  = len(act)
    T0 = float(np.sum(z*np.array(_TCa))) * 0.6
    for _ in range(300):
        Kw = np.array([_Ki_wilson(i, T0, P0) for i in range(NC)])
        f  = np.sum(z*Kw) - 1.0
        df = sum(z[i]*Kw[i]*(WILSON_C*(1+_OMa[i])*_TCa[i]/T0**2) for i in range(NC))
        if abs(df) < 1e-30: break
        Tn = T0 - f/df
        if Tn <= 0: Tn = T0*0.5
        if abs(Tn-T0) < 1e-8: T0 = Tn; break
        T0 = Tn
    Kw = np.array([_Ki_wilson(i, T0, P0) for i in act])
    X  = np.concatenate([np.log(Kw), [np.log(T0)], [np.log(P0)]])
    X, ok = _resolver_punto(X, z, act, ('coord', m+1, np.log(P0)))
    return X if ok else None


def _semilla_rocio(z, act, P_try):
    """Estimación de un punto de ROCÍO a presión P_try por bisección robusta.
    Devuelve X (sin resolver con Newton) o None si no hay cruce de T.

    Clave: para el rocío la estimación inicial de las K es la INVERSA de
    Wilson (K_rocio = 1/Kw), no Wilson directo — esto es lo que hace converger
    a Newton en mezclas con componentes pesados dominantes (p. ej. 50% C9),
    donde usar Kw directo diverge. El rango de T de bisección es amplio porque
    la rama de rocío de esas mezclas está a temperaturas muy altas."""
    m = len(act)
    # Adaptar el rango inferior de T según la componente más volátil presente.
    Tc_min_act = min(_TCa[i] for i in act)
    Ta = max(50.0, 0.30 * Tc_min_act)   # cubre mezclas criogénicas
    Tb = 1600.0
    fa = sum(z[i]/_max(_Ki_wilson(i,Ta,P_try),1e-30) for i in range(NC)) - 1.0
    fb = sum(z[i]/_max(_Ki_wilson(i,Tb,P_try),1e-30) for i in range(NC)) - 1.0
    if fa*fb > 0:
        return None
    T0 = 0.5*(Ta+Tb)
    for _ in range(80):
        T0 = 0.5*(Ta+Tb)
        fm = sum(z[i]/_max(_Ki_wilson(i,T0,P_try),1e-30) for i in range(NC)) - 1.0
        if abs(fm) < 1e-10 or (Tb-Ta) < 1e-3: break
        if fm*fa < 0: Tb = T0
        else: Ta = T0; fa = fm
    Kw_act  = np.array([_Ki_wilson(i, T0, P_try) for i in act])
    K_rocio = 1.0/np.where(Kw_act > 1e-30, Kw_act, 1e-30)
    return np.concatenate([np.log(K_rocio), [np.log(T0)], [np.log(P_try)]])


def _semilla_burbuja(z, act, P_try):
    """Estimación de Wilson de un punto de BURBUJA a presión P_try.
    Devuelve X (sin resolver) o None si no converge la T de Wilson.
    El rango de búsqueda de T se adapta a la Tc mínima de la mezcla para
    cubrir mezclas criogénicas (CO2/C2, N2/C1, etc.)."""
    m = len(act)
    # Adaptar el rango inferior de T según la componente más volátil presente.
    # La envolvente puede estar a temperaturas muy bajas (p. ej. CO2/C2 ≈ -140°F).
    Tc_min_act = min(_TCa[i] for i in act)
    Ta = max(50.0, 0.30 * Tc_min_act)   # ~30% de Tc_min (criogénico)
    Tb = 1600.0
    fa = sum(z[i]*_Ki_wilson(i,Ta,P_try) for i in range(NC)) - 1.0
    fb = sum(z[i]*_Ki_wilson(i,Tb,P_try) for i in range(NC)) - 1.0
    if fa*fb > 0:
        return None
    T0 = 0.5*(Ta+Tb)
    for _ in range(80):
        T0 = 0.5*(Ta+Tb)
        fm = sum(z[i]*_Ki_wilson(i,T0,P_try) for i in range(NC)) - 1.0
        if abs(fm) < 1e-10 or (Tb-Ta) < 1e-3: break
        if fm*fa < 0: Tb = T0
        else: Ta = T0; fa = fm
    Kw_act = np.array([_Ki_wilson(i, T0, P_try) for i in act])
    X = np.concatenate([np.log(Kw_act), [np.log(T0)], [np.log(P_try)]])
    return X


def _init_robusto(z, act):
    """
    Encuentra UN punto de arranque sobre la envolvente que converja con el
    flash riguroso, probando varias presiones y ambas ramas (rocío y burbuja).
    Devuelve (X, tipo) con tipo in {'rocio','burbuja'} o (None, None).
    """
    P_lista = [200, 300, 150, 400, 100, 500, 80, 600, 50, 700, 30, 800,
               250, 350, 450, 120, 60, 40, 20, 14.7, 1000, 1200, 1500, 10]
    m = len(act)
    SUMK2_MIN = 0.6
    mejor_candidato = None
    mejor_sk = -1.0
    for P_try in P_lista:
        for tipo, semilla in (('rocio', _semilla_rocio),
                              ('burbuja', _semilla_burbuja)):
            X0 = semilla(z, act, P_try)
            if X0 is None:
                continue
            X, ok = _resolver_punto(X0, z, act,
                                    ('coord', m+1, np.log(P_try)), tol=1e-8)
            if not ok:
                continue
            if not (np.all(np.isfinite(X)) and X[m] > 0 and X[m+1] != 0):
                continue
            sk = float(np.sum(X[:m]**2))
            try:
                t_test = _tangente(X, z, act)
                if t_test is None:
                    continue
            except Exception:
                continue
            if sk >= SUMK2_MIN:
                return X, tipo
            if sk > mejor_sk:
                mejor_sk = sk
                mejor_candidato = (X, tipo)
    if mejor_candidato is not None:
        return mejor_candidato
    return None, None


# ── Bucle de continuacion (reutilizable) ─────────────────────────────────────
def _trazar(X0, z, act, t0, max_pts, paso_ini=0.10,
            PASO_MIN=5e-4, PASO_MAX=0.10,
            p_stop_max=None, p_stop_min=None, Gfun=_funciones,
            crit_stop=None, sumk2_stop=None):
    """
    Traza la envolvente (o línea de isocalidad, según Gfun) desde X0 en la
    direccion t0 hasta max_pts puntos.
    p_stop_max: detener cuando P > este valor (para trazo de rocio que no
                debe sobrepasar la zona ya cubierta por el trazo de burbuja).
    p_stop_min: detener cuando P < este valor (cierre por presion baja).
    crit_stop:  (Pc,Tc) punto crítico conocido; detener al acercarse a él
                (cierre limpio de la rama de rocío en el crítico).
    sumk2_stop: umbral de sum(lnK)². Cuando un punto cae por debajo, la rama
                llegó a la vecindad del punto crítico (Ki→1) y se DETIENE de
                forma limpia ANTES de entrar en la zona mal condicionada del
                crítico. Esto evita los "puntos flotantes" que la continuación
                generaba al desplazarse hacia adentro de la región bifásica
                justo en la cúspide (Jacobiano casi singular).
    Gfun: función de residuales G(X)=0 a resolver (_funciones para la
          envolvente normal, o una versión con functools.partial de
          _funciones_beta para una línea de isocalidad a beta fijo).
    Retorna (lista_de_pts, X_ultimo, min_sumK2, crit_punto, i_crit).
      i_crit = índice en `pts` del mínimo sum(lnK)² (la cúspide/crítico de
               esta rama). Permite recortar exactamente en el crítico y
               descartar cualquier sobrepaso hacia la otra rama.
    """
    m     = len(act)
    pts   = [(np.exp(X0[m+1]), np.exp(X0[m]))]
    X_prev = X0.copy()
    t      = t0.copy()

    min_sumK2  = float(np.sum(X0[:m]**2))
    crit_punto = (np.exp(X0[m+1]), np.exp(X0[m]))
    i_crit     = 0

    if crit_stop is not None:
        lnTc_s = np.log(crit_stop[1]); lnPc_s = np.log(crit_stop[0])

    # Para detección de lazo cerrado / estancamiento: posición de arranque
    # en el plano (lnT, lnP) y longitud de arco acumulada.
    lnT0_s = X0[m]; lnP0_s = X0[m+1]
    arco_acum = 0.0
    # Ventana de posiciones recientes en (lnT,lnP) para detectar serpenteo
    # local: si la curva genera muchos puntos sin salir de una caja diminuta,
    # la continuación se atascó (típico nudo cerca del crítico).
    ventana = []
    VENT_N = 50          # tamaño de la ventana
    VENT_DIAM = 0.04     # diámetro mínimo (en lnT,lnP) que la ventana debe cubrir

    paso  = paso_ini
    fallos = 0

    for _ in range(max_pts):
        exito = False; paso_try = paso; Xn = None
        for _it in range(16):
            X_pred = X_prev + t * paso_try
            spec   = ('arc', t, X_prev.copy(), paso_try)
            Xn, ok = _resolver_punto(X_pred, z, act, spec, Gfun=Gfun)
            if ok:
                av = np.linalg.norm(Xn - X_prev)
                if 0.2*paso_try < av < 4*paso_try:
                    exito = True; break
            paso_try *= 0.5
            if paso_try < PASO_MIN: break

        if not exito:
            fallos += 1
            if fallos >= 3: break
            paso = PASO_MIN; continue
        fallos = 0

        pts.append((np.exp(Xn[m+1]), np.exp(Xn[m])))

        # Rastrear punto critico
        s = float(np.sum(Xn[:m]**2))
        if s < min_sumK2:
            min_sumK2  = s
            crit_punto = (np.exp(Xn[m+1]), np.exp(Xn[m]))
            i_crit     = len(pts) - 1

        # Parada LIMPIA al alcanzar la vecindad del crítico (Ki→1). Se corta
        # ANTES de la zona mal condicionada para no generar puntos flotantes.
        if sumk2_stop is not None and s < sumk2_stop:
            break

        # Parada por cercanía al crítico conocido (cierre de rama de rocío)
        if crit_stop is not None:
            dln = ((Xn[m]-lnTc_s)**2 + (Xn[m+1]-lnPc_s)**2)**0.5
            if dln < 8e-3:
                break

        # Detección de SERPENTEO LOCAL: si las últimas VENT_N posiciones
        # caben en una caja de diámetro < VENT_DIAM en (lnT,lnP), la curva se
        # atascó dando vueltas (nudo cerca del crítico) → cortar.
        ventana.append((Xn[m], Xn[m+1]))
        if len(ventana) > VENT_N:
            ventana.pop(0)
            lnTs = [p[0] for p in ventana]; lnPs = [p[1] for p in ventana]
            diam = ((max(lnTs)-min(lnTs))**2 + (max(lnPs)-min(lnPs))**2)**0.5
            if diam < VENT_DIAM:
                break

        # Detección de LAZO CERRADO: si tras avanzar un arco apreciable la
        # curva regresa muy cerca del punto de arranque (en lnT,lnP), la
        # envolvente ya se cerró sobre sí misma → detener.
        arco_acum += float(np.linalg.norm(Xn - X_prev))
        dln0 = ((Xn[m]-lnT0_s)**2 + (Xn[m+1]-lnP0_s)**2)**0.5
        if arco_acum > 0.5 and dln0 < 0.02:
            break

        t_new = _tangente(Xn, z, act, t_prev=t, Gfun=Gfun)
        if t_new is None: break
        cosang = float(np.dot(t, t_new))
        X_prev = Xn.copy(); t = t_new

        # Control adaptativo de paso segun curvatura local
        if cosang < 0.2:
            paso = max(paso_try*0.35, PASO_MIN)
        elif cosang < 0.7:
            paso = max(paso_try*0.7, PASO_MIN)
        else:
            paso = min(paso_try*1.25, PASO_MAX)

        Pn = np.exp(Xn[m+1])
        # Condicion de parada por presion
        if p_stop_max is not None and Pn > p_stop_max: break
        if p_stop_min is not None and Pn < p_stop_min: break

    return pts, X_prev, min_sumK2, crit_punto, i_crit


# ── Limpieza geométrica de reversiones ("puntos flotantes") ──────────────────
def _despike(curve, cos_min=-0.40, proteger=None):
    """
    Elimina "puntos flotantes": vértices donde la curva se revierte de forma
    abrupta (giro > ~115°, cos del ángulo entrante/saliente < cos_min). Un giro
    así no ocurre en una envolvente de fases física —ni siquiera en la
    cricondenterma o la cricondenbárica, que giran <90°— por lo que tales
    vértices son siempre artefactos numéricos de la continuación cerca del
    crítico (Jacobiano casi singular).

    Se elimina iterativamente el vértice con el giro más cerrado mientras quede
    alguno por debajo de cos_min; al borrarlo, sus vecinos se unen directamente
    (la curva "salta" el flotante). Trabaja en el plano log(P)-log(T), donde la
    traza avanza de forma homogénea. `proteger` = punto (P,T) que nunca se
    elimina (el crítico).
    """
    if len(curve) < 3:
        return curve
    pts = list(curve)

    def _cos(i, arr):
        a0 = (math.log(max(arr[i][0],1e-9)) - math.log(max(arr[i-1][0],1e-9)),
              math.log(max(arr[i][1],1e-9)) - math.log(max(arr[i-1][1],1e-9)))
        a1 = (math.log(max(arr[i+1][0],1e-9)) - math.log(max(arr[i][0],1e-9)),
              math.log(max(arr[i+1][1],1e-9)) - math.log(max(arr[i][1],1e-9)))
        n0 = math.hypot(*a0); n1 = math.hypot(*a1)
        if n0 < 1e-12 or n1 < 1e-12:
            return 1.0
        return (a0[0]*a1[0] + a0[1]*a1[1])/(n0*n1)

    for _ in range(len(pts)):
        peor_i = -1; peor_c = cos_min
        for i in range(1, len(pts)-1):
            if proteger is not None and pts[i] == proteger:
                continue
            c = _cos(i, pts)
            if c < peor_c:
                peor_c = c; peor_i = i
        if peor_i < 0:
            break
        pts.pop(peor_i)
    return pts


def _max_salto_P(env):
    """Mayor salto en presión entre puntos consecutivos y span de P.
    Un salto grande respecto al span indica una envolvente NO cerrada
    (la rama de burbuja no alcanzó el crítico → diagonal artificial)."""
    if len(env) < 2:
        return 0.0, 0.0
    Ps = [p[0] for p in env]
    span = max(Ps) - min(Ps)
    mj = max(abs(env[i][0] - env[i-1][0]) for i in range(1, len(env)))
    return mj, span


def _bajar_burbuja_desde_critico(z, act, P_ini, max_pts, paso, crit=None):
    """
    Obtiene el lado de BURBUJA de mezclas muy asimétricas (alto metano +
    pesado) BAJANDO desde el crítico. La rama β=0 de burbuja no se puede SUBIR
    desde abajo (la pared casi vertical estanca la continuación), pero sí se
    puede recorrer descendiendo desde el crítico: se arranca en ROCÍO a presión
    moderada, se sube hasta el crítico y se CRUZA, continuando por la rama de
    burbuja hacia abajo.

    Devuelve los puntos del lado de burbuja (desde el crítico hacia abajo),
    ORDENADOS ascendentes en presión, o [] si no logra cruzar un crítico nítido.
    """
    m = len(act)
    Xd = None
    for P0 in [200, 150, 250, 300, 100, 350, 400, 120, 80, 450]:
        Xs = _semilla_rocio(z, act, P0)
        if Xs is None:
            continue
        X, ok = _resolver_punto(Xs, z, act, ('coord', m+1, np.log(P0)), tol=1e-8)
        if ok and np.all(np.isfinite(X)) and X[m] > 0 and \
           float(np.sum(X[:m]**2)) > 0.05:
            Xd = X; break
    if Xd is None:
        return []
    t = _tangente(Xd, z, act)
    if t is None:
        return []
    t_up = t if t[m+1] >= 0 else -t   # subir hacia el crítico

    pts, _, mk, cr, icrit = _trazar(
        Xd, z, act, t_up.copy(), max_pts=max_pts, paso_ini=0.05,
        PASO_MAX=paso, p_stop_min=P_ini*0.95)
    # Debe haber cruzado un crítico nítido (Ki→1) y dejado puntos después.
    if mk > 0.5 or icrit <= 1 or icrit >= len(pts)-1:
        return []
    desc = pts[icrit:]                  # crítico → burbuja (descendente, arco)
    crit_ref = cr if cr is not None else (pts[icrit][0], pts[icrit][1])
    Pc = crit_ref[0]
    Pd = [p[0] for p in desc]
    # La burbuja descendente sólo es útil si DESCIENDE de verdad (baja hacia la
    # región de la burbuja-desde-abajo) y no se dispara a presiones absurdas
    # (Tipo III divergente: el locus se va al infinito → no cierra).
    if not Pd or min(Pd) > 0.6*Pc or max(Pd) > 60.0*max(Pc, 1.0):
        return []
    # Devolver en orden de ARCO ascendente [estancamiento → cricondenbárica →
    # crítico]. NO se ordena por presión: la cricondenbárica suele estar por
    # ENCIMA del crítico, así que ordenar por P rompería la curva en el tope.
    return list(reversed(desc))


def _completar_rocio_desde_critico(*_a, **_k):
    """(Obsoleto) El rocío de mezclas casi-ideales se conserva ahora despicando
    cada rama por separado, no reconstruyéndolo. Se deja un stub inofensivo por
    compatibilidad."""
    return []


# ── Rama de burbuja de ALTA PRESIÓN (mezclas de rango de ebullición amplio) ──
def _rama_alta_presion(z, act, env_pmax, max_pts, paso_max):
    """Captura la rama de burbuja que asciende a presiones muy altas a baja T,
    típica de mezclas con livianos + pesados (p. ej. C1/C9).

    La estrategia de dos ramas (sembrado a P moderada) no la alcanza porque a
    baja T la ecuación de burbuja tiene varias raíces y el crítico queda en
    medio.  Aquí se siembra desde el FLASH (que da las K incipientes) en el
    medio de la rama y se traza en ambas direcciones: una hacia el crítico
    (subiendo por el lazo) y otra hacia baja T (la rama ascendente de alta P).

    Devuelve la línea de burbuja COMPLETA ordenada [alta P … crítico], o []
    si no hay una rama de alta presión que supere holgadamente `env_pmax`
    (mezclas normales → no aporta nada y no se toca la envolvente).
    """
    from eos import calcular
    m = len(act)
    Tc_mix = sum(z[i]*_TCa[i] for i in range(NC))
    umbral = max(env_pmax*1.30, env_pmax + 3000.0)   # debe superar el lazo
    P_escaneo = [300, 600, 1000, 1500, 2500, 4000, 6000, 9000,
                 13000, 18000, 24000, 31000]
    for frac in (0.80, 0.78, 0.82, 0.76, 0.84):
        Ts = frac*Tc_mix
        # Punto de burbuja: primera transición V→0 subiendo en P.
        Pbif = Pliq = None
        for P in P_escaneo:
            V = calcular(z, Ts, float(P), kij_g).get('V', 1.0)
            if 0.02 < V < 0.98 and Pbif is None:
                Pbif = P
            elif V < 0.01 and Pbif is not None and P > Pbif:
                Pliq = P; break
        if Pbif is None or Pliq is None:
            continue
        lo, hi = Pbif, Pliq
        for _ in range(45):
            mid = 0.5*(lo+hi)
            if calcular(z, Ts, mid, kij_g).get('V', 1.0) < 0.005:
                hi = mid
            else:
                lo = mid
        Pb = hi
        r = calcular(z, Ts, Pb, kij_g)
        K = np.array(r.get('K', []))
        if K.size < NC:
            continue
        X = np.zeros(m+2)
        for j, i in enumerate(act):
            X[j] = math.log(max(K[i], 1e-300))
        X[m] = math.log(Ts); X[m+1] = math.log(Pb)
        Xr, _ok = _resolver_punto(X, z, act, ('coord', m+1, math.log(Pb)),
                                  tol=1e-7)
        if not np.all(np.isfinite(Xr)) or float(np.sum(Xr[:m]**2)) < 0.05:
            continue
        t0 = _tangente(Xr, z, act)
        if t0 is None:
            continue
        # Dirección hacia T decreciente = rama ascendente de alta presión.
        t_dn = t0 if t0[m] < 0 else -t0
        pdn, _, _, _, _ = _trazar(
            Xr, z, act, t_dn.copy(), max_pts=max_pts, paso_ini=0.02,
            PASO_MAX=min(paso_max, 0.06), p_stop_max=env_pmax*10.0)
        pmax = max((p for p, _ in pdn), default=0.0)
        if pmax < umbral:
            continue   # esta semilla no reveló rama de alta presión
        # Dirección hacia el crítico = sube por el lazo (parada limpia en crít).
        t_up = -t_dn
        pup, _, mk2_up, crit_up, i_up = _trazar(
            Xr, z, act, t_up.copy(), max_pts=max_pts, paso_ini=0.02,
            PASO_MAX=min(paso_max, 0.06), sumk2_stop=1.5e-3)
        # Cortar EXACTAMENTE en el crítico (mínimo sum(lnK)²) para no
        # sobrepasar hacia la rama de rocío.
        if mk2_up < 0.5 and 0 < i_up < len(pup):
            pup = pup[:i_up+1]
        crit_hp = crit_up if mk2_up < 0.5 else None
        # Línea completa ordenada [alta P … semilla … crítico].
        linea = list(reversed(pdn)) + pup[1:]
        return linea, crit_hp
    return [], None


# ── Punto de entrada principal ───────────────────────────────────────────────
def construir_envolvente(z, kij=None, progress_cb=None,
                         P_ini=14.7, max_pts=2000, paso_max=0.10):
    """
    Construye la envolvente completa por continuación de Michelsen en UNA SOLA
    VUELTA CONTINUA (Opción A).

    En vez de trazar burbuja y rocío por separado y empalmarlos (lo que
    generaba huecos, solapamientos y fallos de dirección en mezclas
    asimétricas o con ramas de rocío largas), se arranca en UN punto robusto
    de la envolvente —probando varias presiones y ambas ramas hasta hallar
    uno que converja con el flash riguroso— y se deja que la continuación de
    pseudo-longitud de arco recorra toda la curva siguiendo la tangente, sin
    decisiones de dirección ambiguas.

    La continuación se hace en las DOS direcciones a partir del punto de
    arranque (hacia adelante y hacia atrás), y los dos tramos se concatenan
    en una sola curva continua. El punto crítico se detecta como el punto de
    mínimo sum(lnK)² a lo largo del recorrido (las dos fases se vuelven
    idénticas: Ki→1).

    Retorna {'envolvente':[(P,T)...], 'critico':(Pc,Tc) o None}.
    """
    global kij_g
    if kij is None: kij = copy.deepcopy(KIJ_DEFAULT)
    kij_g = kij
    _fijar_criticas_activas()
    z = np.array(z, dtype=float)

    act = [i for i in range(NC) if z[i] > 1e-8]
    if len(act) < 2: return {'envolvente': [], 'critico': None}
    m = len(act)

    # ════════════════════════════════════════════════════════════════════════
    # ESTRATEGIA ROBUSTA DE DOS RAMAS INDEPENDIENTES
    # ────────────────────────────────────────────────────────────────────────
    # En vez de una sola continuación que deba CRUZAR el punto crítico (donde
    # el Jacobiano es singular y el trazado se atasca/serpentea), se trazan
    # por separado las dos ramas, cada una arrancando en una zona bien
    # condicionada (baja presión) y avanzando HACIA el crítico:
    #
    #   • Rama de BURBUJA: arranca en burbuja a baja P, sube hasta el crítico.
    #   • Rama de ROCÍO:   arranca en rocío   a baja P, sube hasta el crítico.
    #
    # Ninguna necesita cruzar el crítico (sólo llegar a él), así que no hay
    # serpenteo. Luego se ensamblan en orden: burbuja (P↑) + rocío invertido
    # (P↓), formando la envolvente cerrada continua.
    #
    # Cada rama se traza con la continuación de arco (robusta, con paso
    # adaptativo y tangente por SVD), deteniéndose al acercarse al crítico
    # (Ki→1, sum(lnK)²→0) o al volver a presión baja.
    # ════════════════════════════════════════════════════════════════════════

    # ── GATE 1: mezclas casi-ideales (par de ebullición cercana) ────────────
    # Cuando los componentes activos son casi idénticos (p. ej. iC5/nC5), Ki≈1
    # a lo largo de TODA la envolvente (no sólo en el crítico). La tangente se
    # vuelve mal condicionada y la continuación puede "saltar los rieles" y
    # divergir a P,T no físicas. Detectamos el caso por el spread de Tc de los
    # componentes activos y reducimos el paso SÓLO en ese caso (las mezclas
    # normales mantienen su paso y velocidad intactos).
    Tc_act = [_TCa[i] for i in act]
    casi_ideal = (max(Tc_act) / max(min(Tc_act), 1e-9)) < 1.10
    if casi_ideal:
        paso_max = min(paso_max, 0.025)

    # Umbral de parada al acercarse al crítico (sum(lnK)² pequeño ⇒ Ki→1).
    # Lo bastante pequeño para que la cúspide quede bien definida, pero lo
    # bastante grande para detenernos ANTES de la zona mal condicionada del
    # crítico (donde la continuación se desvía hacia adentro = "flotantes").
    SUMK2_STOP = 1.5e-3
    # En mezclas casi-ideales (astilla delgada, Ki≈1 en toda la curva) las dos
    # ramas se enredan al acercarse al crítico. Detenerlas algo ANTES y cerrar
    # con el punto crítico promediado da una cúspide mucho más limpia.
    if casi_ideal:
        SUMK2_STOP = 2.0e-2

    def _trazar_rama(semilla_fn):
        """Arranca en la rama dada a presión moderada y la traza COMPLETA en
        las dos direcciones:
          • hacia ARRIBA  → sube hasta el punto crítico (parada limpia).
          • hacia ABAJO   → baja la cola hasta P_ini (≈ atmosférica).
        Concatena ambas en orden de presión ascendente: [P_ini … crítico].
        Devuelve (lista_pts ascendente en P, crit_punto|None).

        Esto resuelve dos problemas a la vez:
          1) la cola de baja presión (antes la rama sólo subía desde el punto
             de arranque y nunca bajaba a presiones cercanas a la atmosférica);
          2) los puntos flotantes desde el crítico (la rama sube y se DETIENE
             limpiamente al llegar a la vecindad del crítico, sin entrar en la
             zona mal condicionada que los generaba)."""
        # Buscar un punto de arranque que converja, a presión MODERADA (bien
        # condicionada, lejos del crítico). Desde ahí se extiende en ambas
        # direcciones, así que la presión exacta de arranque no es crítica.
        X_arr = None
        for P_try in [80, 50, 120, 30, 160, 200, 100, 250, 20, 300, 14.7]:
            Xs = semilla_fn(z, act, P_try)
            if Xs is None:
                continue
            Xr, ok = _resolver_punto(Xs, z, act,
                                     ('coord', m+1, np.log(P_try)), tol=1e-8)
            if ok and np.all(np.isfinite(Xr)) and Xr[m] > 0 and Xr[m+1] != 0:
                # Rechazar si arrancó ya sobre el crítico (mal condicionado)
                if float(np.sum(Xr[:m]**2)) > 0.05:
                    X_arr = Xr; break
        if X_arr is None:
            return [], None

        t_arr = _tangente(X_arr, z, act)
        if t_arr is None:
            return [], None
        # Orientar la tangente hacia P creciente (subir hacia el crítico).
        t_up = t_arr if t_arr[m+1] >= 0 else -t_arr
        t_dn = -t_up

        # ── Tramo ARRIBA: del arranque al crítico, con parada limpia ────────
        pts_up, _, minK2_up, crit_up, i_up = _trazar(
            X_arr, z, act, t_up.copy(),
            max_pts=max_pts, paso_ini=0.05, PASO_MAX=paso_max,
            p_stop_min=P_ini*0.95, sumk2_stop=SUMK2_STOP
        )
        # Recortar EXACTAMENTE en el crítico (mínimo sum(lnK)²): descarta
        # cualquier punto que la continuación haya generado más allá del
        # crítico (sobrepaso hacia la otra rama) → evita flotantes.
        if minK2_up < 0.5 and 0 < i_up < len(pts_up):
            pts_up = pts_up[:i_up+1]
        crit = crit_up if minK2_up < 0.5 else None

        # ── Tramo ABAJO: del arranque a P_ini (cola de baja presión) ────────
        pts_dn, _, _, _, _ = _trazar(
            X_arr, z, act, t_dn.copy(),
            max_pts=max_pts, paso_ini=0.05, PASO_MAX=paso_max,
            p_stop_min=P_ini*0.95
        )

        # ── Ensamblar la rama: [P_ini … arranque … crítico] ────────────────
        # reversed(pts_dn) va de P baja hasta el arranque; pts_up[1:] continúa
        # del arranque hacia el crítico (se omite el arranque duplicado).
        rama = list(reversed(pts_dn)) + pts_up[1:]

        # Asegurar orden de presión globalmente ascendente hacia el crítico.
        if len(rama) >= 2 and rama[0][0] > rama[-1][0]:
            rama = list(reversed(rama))
        return rama, crit

    # ── Trazar ambas ramas ──────────────────────────────────────────────────
    pts_burb, crit_b = _trazar_rama(_semilla_burbuja)
    if progress_cb: progress_cb(len(pts_burb))
    pts_dew, crit_d = _trazar_rama(_semilla_rocio)
    if progress_cb: progress_cb(len(pts_burb)+len(pts_dew))

    # ── Punto crítico: cúspide donde ambas ramas se encuentran ──────────────
    # Cada rama se detuvo limpiamente en la vecindad del crítico (sum(lnK)²
    # pequeño). El crítico real es donde ambas coinciden: si las dos ramas lo
    # hallaron y están cerca, se PROMEDIA (cúspide suave, sin escalón); si sólo
    # una lo halló, se usa esa; si discrepan mucho, se toma la de mayor presión.
    crit = crit_b if crit_b is not None else crit_d
    if crit_b is not None and crit_d is not None:
        dP = abs(crit_b[0]-crit_d[0]); dT = abs(crit_b[1]-crit_d[1])
        escalaP = max(crit_b[0], crit_d[0], 1.0)
        escalaT = max(crit_b[1], crit_d[1], 1.0)
        if dP/escalaP < 0.08 and dT/escalaT < 0.08:
            crit = (0.5*(crit_b[0]+crit_d[0]), 0.5*(crit_b[1]+crit_d[1]))
        else:
            crit = crit_b if crit_b[0] >= crit_d[0] else crit_d

    # ── Captura de la rama de burbuja de ALTA PRESIÓN ───────────────────────
    # Para mezclas de rango de ebullición amplio (livianos + pesados) la rama
    # de burbuja asciende a P muy alta a baja T y la estrategia de dos ramas no
    # la alcanza. Se detecta y, de existir, se reemplaza la rama de burbuja por
    # la línea completa [alta P … crítico]. Para mezclas normales no aporta
    # nada (devuelve []) y la envolvente queda idéntica.  Sólo se intenta si el
    # rango de ebullición es amplio (Tc_max/Tc_min de los activos alto), para
    # no penalizar el rendimiento de las mezclas comunes.
    Tc_ratio = max(Tc_act) / max(min(Tc_act), 1e-9)
    if (not casi_ideal) and Tc_ratio > 2.5:
        try:
            env_pmax = 0.0
            if pts_burb: env_pmax = max(env_pmax, max(p for p, _ in pts_burb))
            if pts_dew:  env_pmax = max(env_pmax, max(p for p, _ in pts_dew))
            rama_hp, crit_hp = _rama_alta_presion(z, act, env_pmax, max_pts, paso_max)
            if rama_hp and len(rama_hp) >= 10:
                pts_burb = rama_hp        # línea completa [alta P … crítico]
                if crit_hp is not None:
                    crit = crit_hp
                elif crit is None and crit_d is not None:
                    crit = crit_d
        except Exception:
            pass

    # ── Ensamblar la envolvente cerrada ─────────────────────────────────────
    # burbuja (P baja → crítico) + [crítico] + rocío (crítico → P baja).
    # Como ambas ramas terminan ya muy cerca del crítico y se cierran en el
    # único punto `crit` promediado, la cúspide queda limpia (sin flotantes).
    envolvente = []
    if pts_burb:
        envolvente += pts_burb
    if crit is not None:
        envolvente.append(crit)
    if pts_dew:
        envolvente += list(reversed(pts_dew))

    # Si una rama falló por completo, devolver lo que se tenga (mejor algo que
    # nada); si ambas fallaron, intentar el método de una sola vuelta como
    # respaldo final.
    if len(envolvente) < 4:
        return _envolvente_respaldo(z, act, kij, P_ini, max_pts, paso_max,
                                    progress_cb, casi_ideal=casi_ideal)

    # Limpieza final: eliminar cualquier "punto flotante" residual (reversión
    # abrupta) que la continuación haya dejado en la cúspide del crítico.
    if casi_ideal:
        # Astilla casi-azeotrópica (iC5/nC5): burbuja y rocío casi COINCIDEN.
        # La rama de rocío frecuentemente queda muy corta o con puntos
        # incoherentes post-crítico. Se despica la burbuja y se usa como
        # espejo para el rocío (burbuja = rocío ≈ misma (P,T) en la astilla).
        b = _despike(list(pts_burb), cos_min=-0.40) if len(pts_burb) > 2 \
            else list(pts_burb)
        # Verificar si el rocío cubre suficiente rango de P
        P_b_rng = (max(p[0] for p in b) - min(p[0] for p in b)) if b else 0.0
        P_d_rng = (max(p[0] for p in pts_dew) - min(p[0] for p in pts_dew)
                   ) if pts_dew else 0.0
        if P_d_rng < 0.5 * P_b_rng:
            # Rocío insuficiente: usar burbuja como espejo (sliver simétrico)
            d = list(b)
        else:
            d = _despike(list(pts_dew), cos_min=-0.40) if len(pts_dew) > 2 \
                else list(pts_dew)
        if b:
            envolvente = list(b) + ([crit] if crit else []) + list(reversed(d))
        # Si la burbuja también falló, dejar la envolvente ensamblada y
        # aplicar despike estándar
        if not b:
            envolvente = _despike(envolvente, cos_min=-0.40, proteger=crit)
    else:
        envolvente = _despike(envolvente, cos_min=-0.40, proteger=crit)

    # ── GATE 2: cerrar la burbuja en mezclas asimétricas (alto metano) ───────
    # La rama β=0 de burbuja no puede SUBIR la pared casi vertical desde abajo
    # y se estanca lejos del crítico (queda un salto/diagonal hasta el crítico,
    # que con marcadores se ve como un HUECO). El lado de burbuja SÍ se obtiene
    # BAJANDO desde el crítico (continuando el rocío más allá del crítico). Se
    # empalma por presión con la burbuja-desde-abajo, dando una curva de
    # burbuja continua [P_ini → crítico]. Determinista e integrado:
    #   • Si la burbuja YA alcanzó el crítico (casos normales), no se hace nada
    #     → CERO efecto sobre los resultados que ya funcionan.
    #   • Si se estancó, se reconstruye sólo el tramo que faltaba.
    if crit is not None and pts_burb:
        P_top_burb = pts_burb[-1][0]
        if P_top_burb < 0.85 * crit[0]:        # la burbuja no llegó al crítico
            desc = _bajar_burbuja_desde_critico(
                z, act, P_ini, max_pts, min(paso_max, 0.05), crit)
            # desc = lado de burbuja en orden de arco [estancamiento→…→crítico].
            # Aceptar sólo si realmente alcanza la zona alta (cricondenbárica
            # cerca o por encima del crítico).
            if desc and max(p[0] for p in desc) > 0.9 * crit[0]:
                # Empalmar por el punto MÁS CERCANO al tope de la burbuja-abajo
                # (la esquina), preservando el orden de arco (no ordenar por P).
                last = pts_burb[-1]
                j = min(range(len(desc)),
                        key=lambda i: (desc[i][0]-last[0])**2 +
                                      (desc[i][1]-last[1])**2)
                burb_full = list(pts_burb) + desc[j+1:]
                nueva = burb_full + [crit] + list(reversed(pts_dew))
                nueva = _despike(nueva, cos_min=-0.40, proteger=crit)
                # Adoptar sólo si elimina el salto grande (cierra de verdad).
                mj0, _ = _max_salto_P(envolvente)
                mj1, _ = _max_salto_P(nueva)
                if mj1 < mj0:
                    envolvente = nueva

    # ── Crítico estimado (si ambas ramas fallaron en detectarlo) ─────────────
    # En mezclas multicomponente con muchos componentes, sum(lnK)² puede no
    # bajar de 0.5 aunque la envolvente esté completa. Sin crit la GUI pone
    # todo en burbuja. Se usa la cricondenbárica como estimación: suficiente
    # para que el split burbuja/rocío de la GUI sea correcto.
    if crit is None and len(envolvente) >= 4:
        idx_pmax = max(range(len(envolvente)), key=lambda i: envolvente[i][0])
        crit = envolvente[idx_pmax]

    return {'envolvente': envolvente, 'critico': crit}


def _envolvente_respaldo(z, act, kij, P_ini, max_pts, paso_max, progress_cb,
                         casi_ideal=False):
    """
    Respaldo: método de una sola vuelta continua desde un punto de arranque
    robusto cualquiera. Se usa cuando la estrategia de dos ramas no produjo
    una envolvente utilizable (mezclas patológicas, p.ej. iC5/nC5 donde
    K≈1 y el seed no supera sumK2>0.05, o mezclas multicomponente asimétricas).
    """
    m = len(act)
    X0, tipo = _init_robusto(z, act)
    if X0 is None:
        return {'envolvente': [], 'critico': None}
    t0 = _tangente(X0, z, act)
    if t0 is None:
        return {'envolvente': [], 'critico': None}
    sk0 = float(np.sum(X0[:m]**2))
    # Para casi-ideales (K≈1 en toda la curva) sk0 siempre es pequeño;
    # no limitar max_pts, o sólo obtendremos ~60 pts desde la zona crítica.
    mp = max_pts if casi_ideal else (min(max_pts, 60) if sk0 < 0.05 else max_pts)
    paso = 0.10   # paso robusto siempre: el paso fino 0.025 falla en seeds casi-críticos
    try:
        pts_fwd, _, mkf, cf, ifwd = _trazar(X0, z, act, t0.copy(), max_pts=mp,
                                      paso_ini=0.05, PASO_MAX=paso,
                                      p_stop_min=P_ini*0.95)
        pts_bwd, _, mkb, cb, ibwd = _trazar(X0, z, act, -t0.copy(), max_pts=mp,
                                      paso_ini=0.05, PASO_MAX=paso,
                                      p_stop_min=P_ini*0.95)
    except Exception:
        return {'envolvente': [], 'critico': None}
    envolvente = list(reversed(pts_bwd)) + pts_fwd[1:]
    crit = None
    mk = min(mkf, mkb)
    if mk < 0.5:
        crit = cf if mkf <= mkb else cb

    # ── Estimación del crítico si el motor no lo detectó (mk≥0.5) ───────────
    # En mezclas multicomponente el mínimo de sum(lnK)² puede no bajar de 0.5
    # aunque la envolvente esté completa. Sin crit la GUI pone todo en burbuja
    # (o rocío). Se estima como el punto de MÁXIMA PRESIÓN de la envolvente
    # (cricondenbárica) — suficiente para que la GUI haga el split correcto.
    if crit is None and len(envolvente) >= 4:
        idx_pmax = max(range(len(envolvente)), key=lambda i: envolvente[i][0])
        crit = envolvente[idx_pmax]

    # ── Para casi-ideales: separar burbuja/rocío y hacer espejo ─────────────
    # La curva continua cruza el crítico y baja por el otro lado, pero en
    # mezclas casi-azeotrópicas burbuja y rocío son casi idénticas. Al hacer
    # el split en el crítico el lado de rocío queda muy corto (sólo la zona
    # alta). Se reconstruye el rocío como espejo de la burbuja (mismo P,T)
    # para que la GUI dibuje ambas curvas completas.
    if casi_ideal and crit is not None and envolvente:
        ic = min(range(len(envolvente)),
                 key=lambda i: (envolvente[i][0]-crit[0])**2 +
                               (envolvente[i][1]-crit[1])**2)
        burb_part = envolvente[:ic+1]
        dew_part  = envolvente[ic:]
        P_b_rng = (max(p[0] for p in burb_part) - min(p[0] for p in burb_part)
                   ) if burb_part else 0.0
        P_d_rng = (max(p[0] for p in dew_part)  - min(p[0] for p in dew_part)
                   ) if dew_part else 0.0
        if P_d_rng < 0.5 * P_b_rng and len(burb_part) > 4:
            b_lim = _despike(list(burb_part), cos_min=-0.40)
            # Reensamblar: burbuja limpia + crítico + espejo como rocío
            envolvente = b_lim + [crit] + list(reversed(b_lim))

    return {'envolvente': envolvente, 'critico': crit}


# ── Líneas de isocalidad (fracción de vapor constante) ───────────────────────
def construir_isocalidad(z, beta, kij=None, P_ini=14.7, max_pts=3000,
                         paso_max=0.10, p_max=None, critico=None):
    """
    Traza la línea de isocalidad (quality line) a fracción de vapor FIJA
    `beta` (0<beta<1), usando la misma continuación de Michelsen que la
    envolvente principal, generalizada con la ecuación de Rachford-Rice
    para beta constante (ver _funciones_beta).

    Arranca igual que la rama de burbuja (Wilson a baja presión; beta→0 es
    el caso límite que coincide con la curva de burbuja en sí), pero
    resolviendo desde el inicio con la ecuación de cierre a beta fijo.

    Todas las líneas de isocalidad CONVERGEN al punto crítico de la mezcla
    (donde las fases líquida y vapor se vuelven idénticas y Ki→1 para todo
    componente). La traza se detiene cuando alcanza el crítico, detectado
    de forma robusta por dos vías combinadas:
      • criterio riguroso: sum(lnK)² < umbral pequeño (los Ki tienden a 1);
      • criterio geométrico: la curva pasa muy cerca del `critico` ya
        conocido de la envolvente principal (si se proporciona).
    Esto funciona tanto cuando el crítico cae cerca de la cricondenterma
    como cuando cae sobre la pendiente de la curva de burbuja (donde la
    curva de alta calidad debe rodear el máximo de presión y bajar en
    temperatura antes de llegar al crítico — un mínimo local de sum(lnK)²
    NO es señal de fin en ese caso).

    Retorna {'puntos': [(P,T)...]}.
    """
    global kij_g
    if kij is None: kij = copy.deepcopy(KIJ_DEFAULT)
    kij_g = kij
    _fijar_criticas_activas()
    z = np.array(z, dtype=float)
    beta = float(beta)
    if beta<=0.0: beta=1e-4
    if beta>=1.0: beta=1.0-1e-4

    act = [i for i in range(NC) if z[i] > 1e-8]
    if len(act) < 2: return {'puntos': []}
    m = len(act)

    from functools import partial
    Gfun = partial(_funciones_beta, beta=beta)

    # Arranque: igual que _init_burbuja (Wilson a baja P), pero resuelto
    # directamente con la ecuación de cierre a beta fijo.
    T0 = float(np.sum(z*np.array(_TCa))) * 0.6
    for _ in range(300):
        Kw = np.array([_Ki_wilson(i, T0, P_ini) for i in range(NC)])
        denom = 1.0+beta*(Kw-1.0)
        f  = float(np.sum(z*(Kw-1.0)/np.where(np.abs(denom)<1e-12,1e-12,denom)))
        dT = T0*1e-5
        Kw2 = np.array([_Ki_wilson(i, T0+dT, P_ini) for i in range(NC)])
        denom2 = 1.0+beta*(Kw2-1.0)
        f2 = float(np.sum(z*(Kw2-1.0)/np.where(np.abs(denom2)<1e-12,1e-12,denom2)))
        df = (f2-f)/dT
        if abs(df) < 1e-30: break
        Tn = T0 - f/df
        if Tn <= 0: Tn = T0*0.5
        if abs(Tn-T0) < 1e-8: T0 = Tn; break
        T0 = Tn
    Kw = np.array([_Ki_wilson(i, T0, P_ini) for i in act])
    X0 = np.concatenate([np.log(Kw), [np.log(T0)], [np.log(P_ini)]])
    X0, ok = _resolver_punto(X0, z, act, ('coord', m+1, np.log(P_ini)),
                             Gfun=Gfun)
    if not ok: return {'puntos': []}

    t0 = _tangente(X0, z, act, Gfun=Gfun)
    if t0 is None: return {'puntos': []}
    if t0[m+1] < 0: t0 = -t0   # apuntar hacia P creciente

    # Continuación propia (misma mecánica que _trazar). Se detiene al llegar
    # al punto crítico, detectado por sum(lnK)² muy pequeño (Ki→1) o por
    # cercanía geométrica al crítico conocido.
    pts = [(np.exp(X0[m+1]), np.exp(X0[m]))]
    X_prev = X0.copy(); t = t0.copy()
    PASO_MIN=5e-4
    paso = 0.06; fallos = 0

    # Umbral riguroso de crítico: en el punto crítico todos los ln(Ki)→0, así
    # que sum(lnK)² → 0. Un valor pequeño marca que la curva ya llegó.
    SUMK2_CRIT = 2.0e-3
    # Escala de distancia para el criterio geométrico (en el plano lnT-lnP).
    if critico is not None:
        lnTc = np.log(critico[1]); lnPc = np.log(critico[0])

    for _ in range(max_pts):
        exito=False; paso_try=paso; Xn=None
        for _it in range(16):
            X_pred = X_prev + t*paso_try
            spec = ('arc', t, X_prev.copy(), paso_try)
            Xn, ok = _resolver_punto(X_pred, z, act, spec, Gfun=Gfun)
            if ok:
                av = np.linalg.norm(Xn-X_prev)
                if 0.2*paso_try < av < 4*paso_try:
                    exito=True; break
            paso_try *= 0.5
            if paso_try < PASO_MIN: break
        if not exito:
            fallos += 1
            if fallos >= 3: break
            paso = PASO_MIN; continue
        fallos = 0

        sumK2 = float(np.sum(Xn[:m]**2))
        Pn = np.exp(Xn[m+1]); Tn = np.exp(Xn[m])
        pts.append((Pn, Tn))

        # ── Parada por llegada al punto crítico ──────────────────
        # (a) criterio riguroso: los Ki tienden a 1 (sum(lnK)² → 0)
        if sumK2 < SUMK2_CRIT:
            break
        # (b) criterio geométrico: muy cerca del crítico conocido. La
        #     distancia se mide en el plano log (lnT,lnP), donde la traza
        #     avanza de forma homogénea; el umbral equivale a ~0.5% en T y P.
        if critico is not None:
            dln = ((Xn[m]-lnTc)**2 + (Xn[m+1]-lnPc)**2)**0.5
            if dln < 6e-3:
                break

        if Pn < P_ini*0.95:
            break

        t_new = _tangente(Xn, z, act, t_prev=t, Gfun=Gfun)
        if t_new is None: break
        cosang = float(np.dot(t, t_new))
        X_prev = Xn.copy(); t = t_new
        if cosang < 0.2: paso = max(paso_try*0.35, PASO_MIN)
        elif cosang < 0.7: paso = max(paso_try*0.7, PASO_MIN)
        else: paso = min(paso_try*1.25, paso_max)

    # Cierre limpio al punto crítico: la continuación se vuelve mal
    # condicionada justo en el crítico (Jacobiano singular: ambas fases se
    # vuelven idénticas), por lo que la traza suele detenerse a una distancia
    # pequeña pero no nula. Si terminó razonablemente cerca del crítico
    # conocido, se añade el crítico como punto final para que todas las
    # líneas converjan exactamente a él (como en los diagramas de referencia).
    if critico is not None and len(pts) > 2:
        Pf, Tf = pts[-1]
        dln_fin = ((np.log(Tf)-lnTc)**2 + (np.log(Pf)-lnPc)**2)**0.5
        if dln_fin < 0.05:   # ~5% en escala log: claramente en la zona crítica
            pts.append((critico[0], critico[1]))

    return {'puntos': pts}

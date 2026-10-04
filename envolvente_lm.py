# -*- coding: utf-8 -*-
"""
envolvente_lm.py — Envolvente de fases para mezclas HIDROCARBURO-AGUA por el
método de Lindeloff & Michelsen (SPE 85971, SPE Journal, sept. 2003), tal como
la traza PVTsim cuando el agua está activa.

Todas las líneas se calculan sobre la COMPOSICIÓN TOTAL (con agua) y con el
MISMO modelo termodinámico del flash trifásico (flash_agua / Huron-Vidal), de
modo que las fronteras son exactamente las del flash validado contra PVTsim.

Líneas (nomenclatura de PVTsim):
  2-HC : 1 fase → 2 fases, fase incipiente HIDROCARBURO   (Línea I del paper)
  2-Aq : 1 fase → 2 fases, fase incipiente ACUOSA         (Línea II)
  3-Aq : 2 fases (V+L) → 3 fases, incipiente ACUOSA        (Línea III)
  3-HC : 2 fases (HC+Aq) → 3 fases, incipiente HIDROCARBURO (Línea IV)

Algoritmo (paper, sección "Phase Envelope Algorithm"):
  1. Rocío (Ec. 9-10) desde P0 = 0.5 atm con la fase incipiente que da la T más
     alta; cada punto se prueba por estabilidad (Ec. 11-12) frente a la fase
     del otro tipo.
  2. Al detectarse inestabilidad se calcula el PUNTO TRIFÁSICO (Ec. 16): z en
     equilibrio con dos fases incipientes.  El rocío continúa con la otra fase
     incipiente.
  3. Desde cada punto trifásico nacen dos líneas trifásicas (Ec. 17-20), una
     con incipiente acuosa (3-Aq) y otra con incipiente HC (3-HC); se usa la
     fase incipiente w como referencia de los K y β = fracción en la fase y.
  Continuación de Michelsen (1980): variables logarítmicas, sensibilidad dX/dS,
  especificación = variable de mayor sensibilidad, control de paso.
"""

import numpy as np

from envolvente_trifasica import Termo, N, IDX_AGUA

P_ATM = 14.696


# ════════════════════════════════════════════════════════════════════════════
# Utilidades: subconjunto de componentes presentes (z_i > 0)
# ════════════════════════════════════════════════════════════════════════════
class Sistema:
    def __init__(self, z14, eos, metodo='hv'):
        z14 = np.asarray(z14, dtype=float)
        z14 = z14/z14.sum()
        self.act = np.where(z14 > 1e-14)[0]
        self.n = len(self.act)
        self.z = z14[self.act]
        self.iw = int(np.where(self.act == IDX_AGUA)[0][0]) if IDX_AGUA in self.act else None
        self.tm = Termo(eos, metodo)

    def full(self, c):
        f = np.zeros(N); f[self.act] = c
        return f

    def lnphi(self, c, T, P, fase='auto'):
        c = np.asarray(c, dtype=float)
        if not np.all(np.isfinite(c)) or c.sum() <= 0:
            return None
        lp = self.tm.lnphi(self.full(c), T, P, fase)
        if lp is None or not np.all(np.isfinite(lp[self.act])):
            return None
        return lp[self.act]

    def bm(self, c, T):
        """Covolumen de mezcla (normalizado): la fase HC de mayor b_m es la
        'líquida' de un par HC (criterio de raíz de Michelsen)."""
        self.tm._fijar_T(T)
        c = np.asarray(c, dtype=float); c = c/np.sum(c)
        return float(np.dot(c, self.tm._bi[self.act]))

    def raices_par(self, a, b, T):
        """Tipo de raíz ('L'/'V') para dos fases HC a y b: la más pesada toma la
        raíz líquida y la otra la de vapor (continuidad en el punto crítico)."""
        return ('L', 'V') if self.bm(a, T) >= self.bm(b, T) else ('V', 'L')

    def es_acuosa(self, c):
        c = np.asarray(c)/np.sum(c)
        return self.iw is not None and c[self.iw] > 0.5


def _jac(fun, X, f0, h=1e-7):
    J = np.empty((len(f0), len(X)))
    for k in range(len(X)):
        Xk = X.copy(); dx = h*max(1.0, abs(X[k])); Xk[k] += dx
        fk = fun(Xk)
        if fk is None:
            Xk[k] = X[k] - dx
            fk = fun(Xk)
            if fk is None:
                return None
            J[:, k] = (f0 - fk)/dx
        else:
            J[:, k] = (fk - f0)/dx
    return J


def _newton(fun, X0, tol=1e-10, maxit=30, maxstep=2.0, J0=None):
    """Newton con Jacobiano numérico.  Si se da J0 se usa como Jacobiano inicial
    (método de cuerdas) y solo se recalcula cuando la convergencia se estanca:
    la solución es la misma (el criterio de parada es el residuo), solo cambia
    el costo."""
    X = X0.copy()
    J = J0
    fprev = None
    for it in range(maxit):
        f = fun(X)
        if f is None:
            return None, it
        nf = np.max(np.abs(f))
        if nf < tol:
            return X, it
        if J is None or (fprev is not None and nf > 0.25*fprev):
            J = _jac(fun, X, f)
            if J is None:
                return None, it
        fprev = nf
        try:
            dX = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError:
            return None, it
        mx = np.max(np.abs(dX))
        if mx > maxstep:
            dX *= maxstep/mx
        lam = 1.0
        for _ in range(25):
            fn = fun(X + lam*dX)
            if fn is not None and np.max(np.abs(fn)) < 2.0*nf + 1e-8:
                break
            lam *= 0.5
        else:
            if J0 is not None and J is J0:
                J = None; continue
            return None, it
        X = X + lam*dX
    f = fun(X)
    if f is not None and np.max(np.abs(f)) < 1e-7:
        return X, maxit
    return None, maxit


# ════════════════════════════════════════════════════════════════════════════
# Estabilidad (Ec. 11-12): prueba con fase de un TIPO dado ('hc' o 'aq')
# ════════════════════════════════════════════════════════════════════════════
def estabilidad(S, comp, T, P, tipo, W0=None):
    """Devuelve (k, y) donde k = −ln ΣY (k<0 ⇒ inestable) y y la composición de
    prueba convergida, iniciando con una fase del tipo pedido."""
    lz = S.lnphi(comp, T, P)
    if lz is None:
        return None, None
    d = np.log(comp) + lz
    if W0 is None:
        K = S.tm.K_wilson(T, P)[S.act]
        if tipo == 'aq':
            W = np.full(S.n, 1e-6)
            if S.iw is not None:
                W[S.iw] = 1.0
        else:
            W = comp/K
            if S.iw is not None:
                W[S.iw] = 1e-8
    else:
        W = np.asarray(W0, dtype=float).copy()
    for _ in range(300):
        y = W/W.sum()
        lw = S.lnphi(y, T, P)
        if lw is None:
            return None, None
        Wn = np.exp(np.clip(d - lw, -700, 700))
        if np.max(np.abs(np.log(Wn/W))) < 1e-11:
            W = Wn; break
        W = Wn
    y = W/W.sum()
    # solución trivial (y = comp): no informa estabilidad; su k ≈ 0 con ruido
    # numérico de signo arbitrario.  Se devuelve estable y sin composición
    # para no arrastrarla como estimación inicial del siguiente punto.
    comp = np.asarray(comp, dtype=float); m = comp > 0
    if np.max(np.abs(np.log(np.clip(y[m], 1e-300, None)/comp[m]))) < 1e-4:
        return 0.0, None
    return -np.log(W.sum()), y


# ════════════════════════════════════════════════════════════════════════════
# Línea de rocío (2-HC / 2-Aq): Ec. 9-10 + especificación
#   X = [lnK (n), lnT, lnP],  w = K·z
# ════════════════════════════════════════════════════════════════════════════
def _res_dew(S, X, spec, Sv):
    n = S.n
    lnK = np.clip(X[:n], -500, 80); T = np.exp(X[n]); P = np.exp(X[n+1])
    if not (120 < T < 3000 and 0.01 < P < 1e5):
        return None
    w = np.exp(lnK)*S.z
    if S.es_acuosa(w):
        fw, fz = 'L', 'auto'
    else:
        fw, fz = S.raices_par(w, S.z, T)
    lw = S.lnphi(w, T, P, fw); lz = S.lnphi(S.z, T, P, fz)
    if lw is None or lz is None:
        return None
    g = np.empty(n+2)
    g[:n] = lnK + lw - lz
    g[n] = w.sum() - 1.0
    g[n+1] = X[spec] - Sv
    return g


def _dew_inicial(S, P0):
    """Punto inicial del rocío a P0: se prueban ambos tipos de fase incipiente
    (inicialización de Wilson del paper, Ec. 13-14) y se elige la T MÁS ALTA."""
    mejores = []
    for tipo in ('hc', 'aq'):
        def defecto(T):
            lnl = S.tm.lnphi_wilson_liq(T, P0, tipo)[S.act]
            return np.sum(S.z/np.exp(lnl)) - 1.0
        Ts = np.linspace(150, 1500, 400)
        fs = [defecto(T) for T in Ts]
        Tg = None
        for a in range(len(Ts)-1, 0, -1):          # raíz de mayor T
            if fs[a-1]*fs[a] <= 0:
                lo, hi = Ts[a-1], Ts[a]
                for _ in range(60):
                    m = 0.5*(lo+hi)
                    if defecto(lo)*defecto(m) <= 0: hi = m
                    else: lo = m
                Tg = 0.5*(lo+hi); break
        if Tg is None:
            continue
        lnl = S.tm.lnphi_wilson_liq(Tg, P0, tipo)[S.act]
        w = S.z/np.exp(lnl); w /= w.sum()
        # Partial Newton en T (φ sin derivada composicional), luego Newton completo
        T = Tg
        for _ in range(60):
            lz = S.lnphi(S.z, T, P0); lw = S.lnphi(w, T, P0)
            if lz is None or lw is None:
                break
            Wn = S.z*np.exp(lz - lw)
            f = np.log(Wn.sum())
            if abs(f) < 1e-10:
                w = Wn/Wn.sum(); break
            h = 1e-3*T
            lz2 = S.lnphi(S.z, T+h, P0); lw2 = S.lnphi(w, T+h, P0)
            if lz2 is None or lw2 is None:
                break
            f2 = np.log((S.z*np.exp(lz2 - lw2)).sum())
            dfdT = (f2 - f)/h
            if dfdT == 0:
                break
            T = float(np.clip(T - f/dfdT, 0.7*T, 1.3*T))
            w = Wn/Wn.sum()
        X0 = np.concatenate([np.log(np.clip(w/S.z, 1e-300, None)), [np.log(T), np.log(P0)]])
        X, _ = _newton(lambda XX: _res_dew(S, XX, S.n+1, np.log(P0)), X0)
        if X is None:
            continue
        wf = np.exp(X[:S.n])*S.z
        # que la fase incipiente sea del tipo buscado y no trivial
        if np.max(np.abs(X[:S.n])) < 1e-3:
            continue
        if (tipo == 'aq') != S.es_acuosa(wf):
            continue
        mejores.append((np.exp(X[S.n]), tipo, X))
    if not mejores:
        return None
    mejores.sort(key=lambda t: -t[0])
    return mejores[0][1], mejores[0][2]


def _sens(fun_spec, X, n_eq, spec_row):
    f = fun_spec(X)
    if f is None:
        return None
    J = _jac(fun_spec, X, f)
    if J is None:
        return None
    rhs = np.zeros(n_eq); rhs[spec_row] = 1.0
    try:
        t = np.linalg.solve(J, rhs)
    except np.linalg.LinAlgError:
        return None
    _sens.J = J
    return t


def _continuar(res_fun, X, spec, idx_T, idx_P, parar, dS0=0.03, dSmax=0.12,
               direccion=None, max_pts=5000, forzar_spec=None, idx_crit=None,
               umbral_crit=0.1):
    """Continuación genérica de Michelsen.  res_fun(X, spec, Sv) → residuo;
    parar(X, pts) → True para terminar.  Devuelve lista de X convergidos.

    idx_crit: índices de los lnK que se anulan en un punto crítico (fase
    incipiente ≡ fase presente).  Al acercarse (max|lnK| < umbral) se da un
    salto que CRUZA el crítico especificando el lnK dominante en −(valor actual),
    como en Michelsen (1980), evitando caer en la solución trivial."""
    n_eq = len(X)
    pts = [X.copy()]
    dS = dS0
    prev_t = None
    cruzado = False
    if forzar_spec is not None:
        spec, sgn = forzar_spec
    for _ in range(max_pts):
        if idx_crit is not None and not cruzado and prev_t is not None:
            lk = X[idx_crit]
            k = int(np.argmax(np.abs(lk)))
            # cruce cuando ya está cerca o cuando el próximo paso llegaría
            # al crítico (si no, Newton cae en la solución trivial lnK = 0)
            paso_k = 1.5*dS*abs(prev_t[idx_crit[k]])
            if (abs(lk[k]) < max(umbral_crit, paso_k)
                    and prev_t[idx_crit[k]]*lk[k] < 0):
                kk = idx_crit[k]
                # Predicción CÚBICA en el lnK dominante con los últimos puntos
                # (la curva tiene mucha curvatura en el crítico; el predictor
                # lineal se sale de la envolvente).  Si Newton no converge se
                # prueba un salto más largo y el predictor lineal.
                hist = [q for q in pts if not np.isnan(q[0])][-4:]
                Xn = None
                for fac in (1.0, 2.0, 3.0, 5.0):
                    objetivo = -np.sign(lk[k])*max(fac*abs(lk[k]), 0.1*fac)
                    preds = []
                    if len(hist) >= 3:
                        s_ = np.array([q[kk] for q in hist])
                        Hm = np.array(hist)
                        deg = min(3, len(hist)-1)
                        preds.append(np.array([np.polyval(np.polyfit(s_, Hm[:, c], deg), objetivo)
                                               for c in range(len(X))]))
                    preds.append(X + prev_t*(objetivo - X[kk])/prev_t[kk])
                    for Xp in preds:
                        Xn, nit = _newton(lambda XX: res_fun(XX, kk, objetivo), Xp)
                        if (Xn is not None
                                and np.max(np.abs(Xn[idx_crit])) > 0.5*abs(objetivo)
                                and Xn[kk]*objetivo > 0):
                            break
                        Xn = None
                    if Xn is not None:
                        break
                if Xn is not None:
                    pts.append(np.full_like(X, np.nan))       # marca de crítico
                    X = Xn; pts.append(X.copy()); cruzado = True
                    if parar(X, pts):
                        break
                    continue
        Sv = X[spec]
        t = _sens(lambda XX: res_fun(XX, spec, Sv), X, n_eq, n_eq-1)
        if t is None:
            break
        if prev_t is None:
            if direccion is not None:
                d = direccion(t)
            elif forzar_spec is not None:
                d = sgn
            else:
                d = 1.0
            t = t*d
        else:
            if np.dot(t, prev_t) < 0:
                t = -t
        # nueva especificación: mayor sensibilidad (T y P en logaritmo, lnK).
        # Se excluyen los lnK de componentes traza en una fase muy diluida
        # (|lnK| > 30, p. ej. nC9 en la fase acuosa, lnK ≈ −100 a −400): su
        # sensibilidad es proporcional a su magnitud (lnK ≈ A/T), dominaría
        # la elección y forzaría pasos diminutos en T y P.
        cand = np.abs(t)
        lejos = np.abs(X) > 30.0
        lejos[[idx_T, idx_P]] = False
        if np.any(cand[~lejos] > 0):
            cand = np.where(lejos, 0.0, cand)
        k = int(np.argmax(cand))
        t = t/abs(t[k])
        prev_t = t.copy()
        spec = k
        Xp = X + t*dS
        J0 = getattr(_sens, 'J', None)
        if J0 is not None:
            J0 = J0.copy(); J0[-1, :] = 0.0; J0[-1, spec] = 1.0
        Xn, nit = _newton(lambda XX: res_fun(XX, spec, Xp[spec]), Xp, J0=J0)
        if (Xn is not None and idx_crit is not None
                and np.max(np.abs(Xn[idx_crit])) < 1e-3):
            Xn = None          # solución trivial (fase incipiente ≡ presente)
        if Xn is None:
            dS *= 0.5
            if dS < 1e-5:
                # Rescate: la especificación elegida (a menudo el lnK de un
                # componente traza, de sensibilidad enorme) no admite más
                # pasos.  Se continúa especificando ln T con pasos finitos en
                # la dirección de avance; si ninguno converge, la línea termina.
                sgn = 1.0 if t[idx_T] >= 0 else -1.0
                Xr = None
                for paso in (0.005, 0.01, 0.02, 0.0025):
                    Xq = X.copy(); Xq[idx_T] += sgn*paso
                    Xr, _nit = _newton(lambda XX: res_fun(XX, idx_T, Xq[idx_T]), Xq)
                    if (Xr is not None and idx_crit is not None
                            and np.max(np.abs(Xr[idx_crit])) < 1e-3):
                        Xr = None
                    if Xr is not None:
                        break
                if Xr is None:
                    break
                X = Xr; pts.append(X.copy()); dS = dS0
                if parar(X, pts):
                    break
            continue
        X = Xn
        pts.append(X.copy())
        if parar(X, pts):
            break
        if nit <= 3:
            dS = min(dS*1.4, dSmax)
        elif nit > 6:
            dS *= 0.6
    return pts


# ════════════════════════════════════════════════════════════════════════════
# Punto trifásico (Ec. 16): z en equilibrio con dos fases incipientes w, x
#   X = [lnKw (n), lnKx (n), lnT, lnP]
# ════════════════════════════════════════════════════════════════════════════
def _res_3p(S, X):
    n = S.n
    lKw = np.clip(X[:n], -500, 80); lKx = np.clip(X[n:2*n], -500, 80)
    T = np.exp(X[2*n]); P = np.exp(X[2*n+1])
    if not (120 < T < 3000 and 0.01 < P < 1e5):
        return None
    w = np.exp(lKw)*S.z; x = np.exp(lKx)*S.z
    lz = S.lnphi(S.z, T, P); lw = S.lnphi(w, T, P); lx = S.lnphi(x, T, P)
    if lz is None or lw is None or lx is None:
        return None
    return np.concatenate([lKw + lw - lz, lKx + lx - lz, [w.sum()-1.0, x.sum()-1.0]])


# ════════════════════════════════════════════════════════════════════════════
# Líneas trifásicas (Ec. 17-20)
#   X = [lnKy (n), lnKx (n), lnT, lnP, β]   (w incipiente = referencia)
# ════════════════════════════════════════════════════════════════════════════
def _comp3(S, X):
    n = S.n
    lKy = np.clip(X[:n], -500, 80); lKx = np.clip(X[n:2*n], -500, 80)
    b = X[2*n+2]
    Ky = np.exp(lKy); Kx = np.exp(lKx)
    den = b*Ky + (1.0-b)*Kx
    if np.any(den <= 0):
        return None
    w = S.z/den
    return w, Ky*w, Kx*w


def _res_3l(S, X, spec, Sv):
    n = S.n
    T = np.exp(X[2*n]); P = np.exp(X[2*n+1]); b = X[2*n+2]
    if not (120 < T < 3000 and 0.01 < P < 1e5) or not (-0.05 < b < 1.05):
        return None
    c = _comp3(S, X)
    if c is None:
        return None
    w, y, x = c
    # raíces: fase acuosa → líquida; par HC → la más pesada líquida
    ph = {}
    comps = {'w': w, 'y': y, 'x': x}
    hc = [k for k, v in comps.items() if not S.es_acuosa(v)]
    for k, v in comps.items():
        if S.es_acuosa(v):
            ph[k] = 'L'
    if len(hc) == 2:
        ph[hc[0]], ph[hc[1]] = S.raices_par(comps[hc[0]], comps[hc[1]], T)
    for k in hc:
        ph.setdefault(k, 'auto')
    lw = S.lnphi(w, T, P, ph['w']); ly = S.lnphi(y, T, P, ph['y']); lx = S.lnphi(x, T, P, ph['x'])
    if lw is None or ly is None or lx is None:
        return None
    g = np.empty(2*n+3)
    g[:n] = X[:n] + ly - lw
    g[n:2*n] = X[n:2*n] + lx - lw
    g[2*n] = w.sum() - 1.0
    g[2*n+1] = np.sum(y - x)
    g[2*n+2] = X[spec] - Sv
    return g



# ════════════════════════════════════════════════════════════════════════════
# Región trifásica AISLADA (sin punto trifásico sobre el rocío) — paper:
# "in case no three-phase point is found on the dewline, a search for an inner,
# isolated three-phase region ... is carried out".
# ════════════════════════════════════════════════════════════════════════════
def _buscar_interna(S, eos, dew_pts_PT, P0, T_min):
    """Busca un punto de frontera 2→3 fases bajo la línea de rocío con el flash
    trifásico y devuelve X inicial de las Ec. 17-20 (con P fija) o None."""
    import flash_agua as _fa
    if not dew_pts_PT:
        return None
    dew = sorted(dew_pts_PT)
    Pmx = min(max(p for p, _ in dew), 5000.0)
    Ps = np.exp(np.linspace(np.log(max(P0*1.5, dew[0][0])), np.log(Pmx*0.95), 12))
    # empezar por presiones intermedias (donde suele estar la región interna)
    Pref = np.exp(0.5*(np.log(Ps[0]) + np.log(Ps[-1])))
    Ps = sorted(Ps, key=lambda p: abs(np.log(p/Pref)))
    z14 = S.full(S.z)
    def fases(T, P):
        r = _fa.flash_trifasico(z14, float(T), float(P), S.tm.eos, 'hv')
        return r, sum(1 for k in ('beta_V', 'beta_L', 'beta_W') if r[k] > 1e-7)
    for P in Ps:
        Tdew = float(np.interp(P, [p for p, _ in dew], [t for _, t in dew]))
        T_prev = Tdew - 0.5
        r_prev, nf_prev = fases(T_prev, P)
        T = T_prev
        while T > T_min + 5:
            T -= 10.0
            r, nf = fases(T, P)
            if nf == 3 and nf_prev == 2:
                lo, hi, r_lo = T, T_prev, r     # lo: 3 fases, hi: 2 fases
                for _ in range(12):
                    m = 0.5*(lo + hi)
                    rm, nm = fases(m, P)
                    if nm == 3:
                        lo, r_lo = m, rm
                    else:
                        hi = m
                # fase nueva = la de menor β en el lado trifásico
                bet = {'y': r_lo['beta_V'], 'x': r_lo['beta_L'], 'w': r_lo['beta_W']}
                comp = {'y': np.asarray(r_lo['y']), 'x': np.asarray(r_lo['x']),
                        'w': np.asarray(r_lo['w'])}
                nueva = min(bet, key=bet.get)
                pres = [k for k in bet if k != nueva]
                wv = comp[nueva][S.act]; a = comp[pres[0]][S.act]; b = comp[pres[1]][S.act]
                ba, bb = bet[pres[0]], bet[pres[1]]
                beta = ba/(ba + bb)
                wv = np.clip(wv, 1e-300, None); a = np.clip(a, 1e-300, None); b = np.clip(b, 1e-300, None)
                X = np.concatenate([np.log(a/wv), np.log(b/wv), [np.log(lo), np.log(P), beta]])
                n = S.n
                Xs, _ = _newton(lambda XX: _res_3l(S, XX, 2*n+1, np.log(P)), X, maxit=60)
                if Xs is not None:
                    tipo = 'aq' if S.es_acuosa(np.exp(-Xs[:n])*0 + wv) else 'hc'
                    return Xs, tipo
            T_prev, r_prev, nf_prev = T, r, nf
    return None


def _aterrizar(S, pts, jb):
    """Si la línea trifásica terminó con β fuera de [0, 1] (salió de la
    región), reemplaza el último punto por la solución EXACTA con β en el
    límite, partiendo del penúltimo punto válido."""
    reales = [q for q in pts if not np.isnan(q[0])]
    if len(reales) < 3:
        return pts
    b = reales[-1][jb]
    if -1e-9 <= b <= 1.0 + 1e-9:
        return pts
    lim = 0.0 if b < 0 else 1.0
    Xa = reales[-2]
    t = reales[-1] - Xa
    if t[jb] != 0:
        Xp = Xa + t*(lim - Xa[jb])/t[jb]
    else:
        Xp = Xa
    Xs, _ = _newton(lambda XX: _res_3l(S, XX, jb, lim), Xp, maxit=40)
    out = pts[:-1]
    if Xs is not None:
        out.append(Xs)
    return out

# ════════════════════════════════════════════════════════════════════════════
# API principal
# ════════════════════════════════════════════════════════════════════════════
def _adelgazar(pts, dmin=0.004):
    """Reduce puntos muy juntos (distancia relativa en lnT-lnP < dmin),
    conservando extremos.  Solo afecta a la densidad visual de marcadores."""
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for p in pts[1:-1]:
        q = out[-1]
        if abs(np.log(p[1]/q[1]))*10 + abs(np.log(p[0]/q[0])) >= dmin*10:
            out.append(p)
    out.append(pts[-1])
    return out


_DEBUG_BIN = False


def _linea_trifasica_binaria(S, Pmin, Pmax, T_min):
    """Línea trifásica V-L_HC-Aq de una mezcla binaria HC + agua.

    A T fija las tres fases coexisten a una sola presión.  Incógnitas
    X = [ln(x/y) (2), ln(w/y) (2), y_HC, ln P] con igualdad de fugacidades
    (4 ec.) y Σx = Σw = 1.  Se recorre en T desde una presión intermedia hacia
    abajo (hasta Pmin) y hacia arriba hasta que L_HC y V se igualan (UCEP).
    Devuelve ([(P, T), …] ordenada por T, (P_ucep, T_ucep) | None)."""
    ih = 0 if S.iw == 1 else 1
    iw = S.iw
    tm = S.tm

    def res(X, T):
        lKx = X[0:2]; lKw = X[2:4]; yh = X[4]; P = np.exp(X[5])
        if not (0.0 < yh < 1.0) or not (1e-6 < P < 1e5):
            return None
        y = np.zeros(2); y[ih] = yh; y[iw] = 1.0 - yh
        x = np.exp(np.clip(lKx, -500, 80))*y
        w = np.exp(np.clip(lKw, -500, 80))*y
        ly = S.lnphi(y, T, P, 'V'); lx = S.lnphi(x/x.sum(), T, P, 'L')
        lw = S.lnphi(w/w.sum(), T, P, 'L')
        if ly is None or lx is None or lw is None:
            return None
        g = np.empty(6)
        g[0:2] = lKx + lx - ly
        g[2:4] = lKw + lw - ly
        g[4] = x.sum() - 1.0
        g[5] = w.sum() - 1.0
        return g

    # estimación inicial (Wilson): P ≈ Psat_HC + Psat_agua
    try:
        TcA, PcA, omA = (np.asarray(v, dtype=float)[S.act] for v in (tm.Tc, tm.Pc, tm.om))
    except Exception:
        return [], None
    def psat(k, T):
        return PcA[k]*np.exp(5.373*(1.0 + omA[k])*(1.0 - TcA[k]/T))
    def X_ini(T):
        Ph, Pw = psat(ih, T), psat(iw, T)
        P = Ph + Pw
        y = np.zeros(2); y[ih] = Ph/P; y[iw] = Pw/P
        x = np.zeros(2); x[ih] = 1.0 - 1e-4; x[iw] = 1e-4
        w = np.zeros(2); w[ih] = 1e-5; w[iw] = 1.0 - 1e-5
        return np.array([np.log(x[0]/y[0]), np.log(x[1]/y[1]),
                         np.log(w[0]/y[0]), np.log(w[1]/y[1]), y[ih], np.log(P)])
    # T de arranque: Psat_HC ≈ 50 psia (sin exceder 0.95·Tc del HC)
    T0 = None
    for T in np.linspace(0.3*TcA[ih], 0.95*TcA[ih], 400):
        if psat(ih, T) >= 50.0:
            T0 = T; break
    cand = ([T0] if T0 is not None else []) + [f*TcA[ih] for f in (0.8, 0.7, 0.9, 0.95, 0.6)]
    X0 = None
    for T0 in cand:
        X0, _ = _newton(lambda XX: res(XX, T0), X_ini(T0), tol=1e-11, maxit=80, maxstep=1.0)
        if X0 is not None and np.max(np.abs(X0[0:2])) > 1e-3:
            break
        X0 = None
    if X0 is None:
        return [], None

    def recorrer(direc):
        pts = []; X = X0.copy(); T = T0; dT = 2.0
        while dT > 1e-3:
            Tn = T + direc*dT
            Xn, _ = _newton(lambda XX: res(XX, Tn), X, tol=1e-11, maxit=40, maxstep=0.5)
            if Xn is None or np.max(np.abs(Xn[0:2])) < 1e-4:
                dT *= 0.5; continue
            P = float(np.exp(Xn[5]))
            if P < Pmin or P > Pmax or Tn < T_min:
                break
            X, T = Xn, Tn
            pts.append((T, X.copy()))
            dT = min(dT*1.3, 10.0)
            if direc > 0 and np.max(np.abs(X[0:2])) < 0.02:
                dT = min(dT, 0.2)
        return pts

    abajo = recorrer(-1.0); arriba = recorrer(+1.0)
    todos = abajo[::-1] + [(T0, X0)] + arriba
    lin = [(float(np.exp(X[5])), float(T)) for T, X in todos]
    ucep = None
    if len(arriba) >= 3:
        # UCEP: ln(x_HC/y_HC) → 0, extrapolado con los últimos puntos
        sel = arriba[-4:]
        # variable de cruce: el ln(x/y) de mayor magnitud al inicio (para C1 +
        # agua el del HC es ~0 en toda la línea; el del agua no)
        kc = int(np.argmax(np.abs(X0[0:2])))
        s_ = np.array([X[kc] for _, X in sel])
        deg = min(2, len(sel) - 1)
        Tu = float(np.polyval(np.polyfit(s_, [T for T, _ in sel], deg), 0.0))
        Pu = float(np.exp(np.polyval(np.polyfit(s_, [X[5] for _, X in sel], deg), 0.0)))
        if _DEBUG_BIN:
            print('UCEP dbg', [(round(T,4), float(X[ih])) for T, X in sel], Tu, Pu)
        if np.isfinite(Tu) and np.isfinite(Pu) and Tu >= sel[-1][0] - 0.05:
            ucep = (Pu, Tu)
            lin.append(ucep)
    return lin, ucep


def envolvente_agua(z14, eos, metodo='hv', P0=0.5*P_ATM, Pmin=0.37*P_ATM,
                    T_min=250.0, P_max=None, progress_cb=None):
    """Traza las líneas 2-HC, 2-Aq, 3-Aq, 3-HC y el punto crítico.

    Devuelve dict {'2-HC': [(P,T)...], '2-Aq': [...], '3-Aq': [...],
                   '3-HC': [...], 'critico': [(P,T)...], 'trifasicos': [(P,T)]}
    (P en psia, T en °R)."""
    S = Sistema(z14, eos, metodo)
    n = S.n
    # Mezcla BINARIA (un solo hidrocarburo + agua): la región trifásica
    # degenera en una LÍNEA univariante V-L_HC-Aq (análoga a la curva de
    # presión de vapor del HC puro) que termina en el punto crítico final
    # superior (UCEP).  Se traza aparte; las líneas trifásicas del caso general
    # (Ec. 17-20 con β como especificación) no aplican.
    binaria = (n == 2 and S.iw is not None)
    out = {'2-HC': [], '2-Aq': [], '3-Aq': [], '3-HC': [], 'critico': [],
           'trifasicos': []}
    ini = _dew_inicial(S, P0)
    if ini is None:
        return out
    tipo, X = ini
    iT, iP = n, n+1

    def TP_dew(X):
        return float(np.exp(X[iT])), float(np.exp(X[iP]))

    PMAX_ABS = 15000.0
    lineas_dew = []          # (tipo, [X...])
    trif = []                # soluciones X de Ec. 16 con (tipo_w, tipo_x)
    for _rama in range(4):
        otro = 'aq' if tipo == 'hc' else 'hc'
        estado = {'Xprev': None, 'W': None}

        def parar(Xc, pts, otro=otro, estado=estado):
            T, P = TP_dew(Xc)
            if P > PMAX_ABS or P < Pmin*0.999 or T < 150:
                return True
            lnK = Xc[:n]
            if np.max(np.abs(lnK)) < 1e-3:       # punto crítico del rocío
                return True
            k, y = estabilidad(S, S.z, T, P, otro, estado['W'])
            if k is not None and k < -1e-9 and ((otro == 'aq') == S.es_acuosa(y)):
                estado['inestable'] = (Xc.copy(), y)
                return True
            if y is not None and ((otro == 'aq') == S.es_acuosa(y)):
                estado['W'] = y
            return False

        # sentido: hacia presión creciente
        def dirf(t):
            return 1.0 if t[iP] > 0 else -1.0
        pts = _continuar(lambda XX, sp, Sv: _res_dew(S, XX, sp, Sv), X, iP,
                         iT, iP, parar, direccion=dirf)
        if _rama > 0:
            pts = [X_inicio_rama] + pts
        if 'inestable' not in estado:
            lineas_dew.append((tipo, pts))
            break
        # quitar el último punto (inestable) y resolver el punto trifásico
        Xu, y = estado['inestable']
        Xa = pts[-2] if len(pts) > 1 else pts[-1]
        # estimación inicial: w del último punto estable, x de la estabilidad
        lKw = Xa[:n]
        lKx = np.log(np.clip(y/S.z, 1e-300, None))
        X3 = np.concatenate([lKw, lKx, [Xa[iT], Xa[iP]]])
        X3s, _ = _newton(lambda XX: _res_3p(S, XX), X3, maxit=60)
        if X3s is None:
            X3 = np.concatenate([Xu[:n], lKx, [Xu[iT], Xu[iP]]])
            X3s, _ = _newton(lambda XX: _res_3p(S, XX), X3, maxit=60)
        if X3s is None:
            lineas_dew.append((tipo, pts[:-1]))
            break
        # recortar la rama al punto trifásico
        T3, P3 = float(np.exp(X3s[2*n])), float(np.exp(X3s[2*n+1]))
        rama = [p for p in pts[:-1] if np.exp(p[iP]) <= P3 + 1e-9]
        Xend = np.concatenate([X3s[:n], [X3s[2*n], X3s[2*n+1]]])
        rama.append(Xend)
        lineas_dew.append((tipo, rama))
        trif.append((X3s, tipo, otro))
        # continuar el rocío con la otra fase incipiente desde el punto trifásico
        tipo = otro
        X = np.concatenate([X3s[n:2*n], [X3s[2*n], X3s[2*n+1]]])
        X_inicio_rama = X.copy()
        # avanzar un paso para no re-detectar el mismo punto
        X, _ = _newton(lambda XX: _res_dew(S, XX, iP, X[iP] + 0.01), X)
        if X is None:
            break

    # ── líneas trifásicas desde cada punto trifásico ─────────────────────────
    j2T, j2P, jb = 2*n, 2*n+1, 2*n+2
    lin3 = []
    llegadas = set()          # (índice de punto trifásico, tipo) ya alcanzados
    TP3 = [(X3s[2*n], X3s[2*n+1]) for X3s, _, _ in trif]
    for itp, (X3s, tw, tx) in enumerate([] if binaria else trif):
        lKw = X3s[:n]; lKx = X3s[n:2*n]
        for incip in ('aq', 'hc'):
            if (itp, incip) in llegadas:
                continue      # esa línea ya se trazó llegando desde otro punto
            # w = incipiente (del tipo incip); y = z (β=1); x = la otra incipiente
            if incip == tw:
                lw, lx_ = lKw, lKx
            else:
                lw, lx_ = lKx, lKw
            # K referidos a w:  Ky = z/w = 1/Kw ; Kx = x/w
            lKy = -lw
            lKxw = lx_ - lw
            X = np.concatenate([lKy, lKxw, [X3s[2*n], X3s[2*n+1], 1.0]])
            def parar3(Xc, pts):
                T = np.exp(Xc[j2T]); P = np.exp(Xc[j2P]); b = Xc[jb]
                return (P < Pmin or P > PMAX_ABS or T < T_min or b < -1e-9
                        or b > 1.0 + 1e-9 and len(pts) > 3)
            pts = _continuar(lambda XX, sp, Sv: _res_3l(S, XX, sp, Sv), X, jb,
                             j2T, j2P, parar3, forzar_spec=(jb, -1.0),
                             idx_crit=np.arange(n) if incip == 'hc' else None)
            pts = _aterrizar(S, pts, jb)
            # ¿terminó en OTRO punto trifásico?  (paper: "the tracing of the
            # three-phase line is terminated if computations return to a
            # three-phase point")  → no volver a trazarla desde ese punto.
            ult = pts[-1]
            for jtp, (lT, lP) in enumerate(TP3):
                if jtp != itp and abs(ult[j2T]-lT) < 5e-3 and abs(ult[j2P]-lP) < 2e-2:
                    llegadas.add((jtp, incip))
            lin3.append((incip, pts))
            out.setdefault('_raw', []).append((incip, pts))

    # ── región trifásica aislada (ningún punto trifásico en el rocío) ───────
    if not trif and not binaria:
        dew_PT = [(float(np.exp(p[iP])), float(np.exp(p[iT])))
                  for _, pts in lineas_dew for p in pts]
        ini3 = _buscar_interna(S, eos, dew_PT, P0, T_min)
        if ini3 is not None:
            Xs, incip = ini3
            X_ini = Xs.copy()
            def parar_i(Xc, pts):
                if np.isnan(Xc[0]):
                    return False
                T = np.exp(Xc[j2T]); P = np.exp(Xc[j2P]); b = Xc[jb]
                if P < Pmin or P > PMAX_ABS or T < T_min or b < -1e-9 or b > 1.0 + 1e-9:
                    return True
                # curva cerrada: regreso al punto de partida
                if len(pts) > 20 and abs(Xc[j2T]-X_ini[j2T]) < 2e-3 and abs(Xc[j2P]-X_ini[j2P]) < 2e-3:
                    return True
                return False
            ramas = []
            for sgn in (+1.0, -1.0):
                pts = _continuar(lambda XX, sp, Sv: _res_3l(S, XX, sp, Sv), Xs,
                                 j2P, j2T, j2P, parar_i, forzar_spec=(j2P, sgn),
                                 idx_crit=np.arange(n) if incip == 'hc' else None)
                ramas.append(pts)
                # si la primera rama cerró la curva, no hace falta la segunda
                if len(pts) > 20 and abs(pts[-1][j2P]-X_ini[j2P]) < 2e-3 and abs(pts[-1][j2T]-X_ini[j2T]) < 2e-3:
                    break
            # unir: rama(−) invertida + rama(+)
            if len(ramas) == 2:
                pts_all = ramas[1][::-1] + ramas[0][1:]
            else:
                pts_all = ramas[0]
            lin3.append((incip, pts_all))
            out.setdefault('_raw', []).append((incip, pts_all))

    # ── salida en (P, T) + punto crítico en 3-HC (cambio de signo de lnKy) ──
    out['_S'] = S
    out['binaria'] = binaria
    out['_raw_dew'] = lineas_dew
    seg = {'2-HC': [], '2-Aq': [], '3-Aq': [], '3-HC': []}
    for tipo, pts in lineas_dew:
        key = '2-HC' if tipo == 'hc' else '2-Aq'
        seg[key].append([(float(np.exp(p[iP])), float(np.exp(p[iT]))) for p in pts])
    if binaria:
        lin_b, ucep = _linea_trifasica_binaria(S, Pmin, PMAX_ABS, T_min)
        if len(lin_b) >= 2:
            seg['3-HC'].append(lin_b)
        if ucep is not None:
            out['critico'].append(ucep)
    for X3s, tw, tx in ([] if binaria else trif):
        out['trifasicos'].append((float(np.exp(X3s[2*n+1])), float(np.exp(X3s[2*n]))))
    for incip, pts in lin3:
        key = '3-Aq' if incip == 'aq' else '3-HC'
        good = []; crit_at = None
        for p in pts:
            if np.isnan(p[0]):
                crit_at = len(good); continue
            T = float(np.exp(p[j2T])); P = float(np.exp(p[j2P]))
            if P < Pmin or T < T_min:
                continue
            good.append((P, T, p))
        if len(good) >= 2:
            seg[key].append([(P, T) for P, T, _ in good])
        if incip == 'hc' and crit_at is not None and 0 < crit_at < len(good):
            # crítico: lnK_dominante = 0; P y T por ajuste cúbico en ese lnK con
            # los dos puntos a cada lado del cruce.
            a = good[crit_at-1][2]
            i = int(np.argmax(np.abs(a[:n])))
            sel = good[max(0, crit_at-2):crit_at+2]
            sv = np.array([q[2][i] for q in sel])
            deg = min(3, len(sel)-1)
            Pc = float(np.exp(np.polyval(np.polyfit(sv, [np.log(q[0]) for q in sel], deg), 0.0)))
            Tc = float(np.exp(np.polyval(np.polyfit(sv, [np.log(q[1]) for q in sel], deg), 0.0)))
            out['critico'].append((Pc, Tc))
    # límite superior de presión de la 2-Aq (presentación): 1.20 × la mayor
    # presión de las líneas HC/trifásicas.  PVTsim la corta tras su primer
    # paso que supera la cricondenbárica.
    Ps = [p for k in ('2-HC', '3-Aq', '3-HC') for sg in seg[k] for p, _ in sg]
    if P_max is None and Ps:
        P_max = 1.20*max(Ps)
    if P_max is not None:
        nuevos = []
        for L2 in seg['2-Aq']:
            cort = [(P, T) for P, T in L2 if P <= P_max]
            for a in range(1, len(L2)):
                if L2[a-1][0] <= P_max < L2[a][0]:
                    f = (P_max - L2[a-1][0])/(L2[a][0] - L2[a-1][0])
                    cort.append((P_max, L2[a-1][1] + f*(L2[a][1] - L2[a-1][1])))
                    break
            if len(cort) >= 2:
                nuevos.append(cort)
        seg['2-Aq'] = nuevos
    for k in seg:
        seg[k] = [_adelgazar(sg) for sg in seg[k]]
        out[k] = [pt for sg in seg[k] for pt in sg]       # lista plana (compat.)
    out['segmentos'] = seg
    return out

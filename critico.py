"""
critico.py — Punto critico REAL de la mezcla, para la identificacion de fase
al estilo PVTsim.

PVTsim distingue liquido/gas de un fluido monofasico comparando T y P con el
punto critico REAL de la mezcla (no el pseudocritico de Kay). Aqui se obtiene
el punto critico reutilizando el trazador de envolvente de Michelsen (que lo
localiza como el punto donde Ki->1), con CACHE por composicion+EOS para que el
costo se pague una sola vez por fluido. Incluye guarda de reentrancia para no
recursar si el propio trazado dispara un flash monofasico.
"""
import copy
import eos as E

_CACHE = {}            # (eos, comp_redondeada) -> (Pc, Tc) | None
_EN_CURSO = set()      # claves en calculo (guarda anti-recursion)


def _clave(z):
    return (E._EOS_ACTIVA, tuple(round(float(v), 5) for v in z))


# ════════════════════════════════════════════════════════════════════════
# Cálculo DIRECTO del punto crítico (Heidemann y Khalil, 1980; Michelsen,
# 1980): con la energía de Helmholtz de la cúbica en variables (T, V, n),
#   1) λ_min(Q) = 0,  Q_ij = √(z_i z_j)·∂ln f_i/∂n_j   (a T, V fijos)
#   2) C = Σ Δn_i Δn_j Δn_k ∂³A/∂n_i∂n_j∂n_k = 0      (Δn = √z·u_min)
# Resuelve T para cada V (condición 1) y V por secante (condición 2).  Da el
# mismo punto que la envolvente de Michelsen (donde K→1) en una fracción de
# segundo, en lugar de trazar toda la envolvente.
# ════════════════════════════════════════════════════════════════════════
import numpy as np


_ACT = [None]


def _param_cubica():
    if E.es_srk(E._EOS_ACTIVA):
        return 1.0, 0.0
    return 1.0 + np.sqrt(2.0), 1.0 - np.sqrt(2.0)


def _lnf(n, T, V, bi, kij, d1, d2, act=None):
    """ln f_i (salvo constante) de la cúbica en variables (T, V, n)."""
    R = E.R_GAS
    aa = E.ai_alpha_vec_eos(E._EOS_ACTIVA, T)
    if act is not None:
        aa = aa[act]
    sa = np.sqrt(aa)
    Aij = np.outer(sa, sa)*(1.0 - kij)
    B = float(n @ bi); D = float(n @ Aij @ n); Di = 2.0*(Aij @ n)
    if V <= B:
        return None
    nt = n.sum()
    lg = np.log((V + d1*B)/(V + d2*B))
    f = lg/(R*B*(d1 - d2))
    fB = -f/B + (d1/(V + d1*B) - d2/(V + d2*B))/(R*B*(d1 - d2))
    # Ar/RT = -n·ln(1-B/V) - (D/T)·f
    dAr = (-np.log(1.0 - B/V) + nt*bi/(V - B)) - (Di/T)*f - (D/T)*fB*bi
    return np.log(np.clip(n, 1e-300, None)*R*T/V) + dAr


def _lambda_min(z, T, V, bi, kij, d1, d2, h=1e-6):
    n = np.asarray(z, dtype=float)
    f0 = _lnf(n, T, V, bi, kij, d1, d2, _ACT[0])
    if f0 is None:
        return None, None
    m = len(n)
    Jn = np.empty((m, m))
    for j in range(m):
        nj = n.copy(); dn = h*max(n[j], 1e-12); nj[j] += dn
        fj = _lnf(nj, T, V, bi, kij, d1, d2, _ACT[0])
        if fj is None:
            return None, None
        Jn[:, j] = (fj - f0)/dn
    sq = np.sqrt(n)
    Q = sq[:, None]*Jn*sq[None, :]
    Q = 0.5*(Q + Q.T)
    w, U = np.linalg.eigh(Q)
    u = U[:, 0]
    # orientación fija del autovector (la forma cúbica es impar en u):
    # Δn = √z·u con Σ Δn_i·b_i > 0
    if float((sq*u) @ bi) < 0:
        u = -u
    return float(w[0]), u


def _cubico(z, T, V, u, bi, kij, d1, d2, eps=1e-4):
    n = np.asarray(z, dtype=float)
    dn = np.sqrt(n)*u
    def b(sv):
        f1 = _lnf(n + sv*dn, T, V, bi, kij, d1, d2, _ACT[0])
        f0 = _lnf(n, T, V, bi, kij, d1, d2, _ACT[0])
        if f1 is None or f0 is None:
            return None
        return float(dn @ (f1 - f0))
    bp = b(eps); bm = b(-eps)
    if bp is None or bm is None:
        return None
    return (bp + bm)/(eps*eps)


def _T_lambda0(z, V, T0, bi, kij, d1, d2):
    """T tal que λ_min = 0 a volumen V (secante con salvaguarda)."""
    def g(T):
        lam, u = _lambda_min(z, T, V, bi, kij, d1, d2)
        return lam, u
    Ta = T0; la, _ = g(Ta)
    if la is None:
        return None, None
    Tb = Ta*(1.05 if la < 0 else 0.95); lb, u = g(Tb)
    for _ in range(80):
        if lb is None or la is None:
            return None, None
        if abs(lb) < 1e-10:
            return Tb, u
        if lb == la:
            break
        Tn = Tb - lb*(Tb - Ta)/(lb - la)
        Tn = min(max(Tn, 0.5*Tb), 1.5*Tb)
        Ta, la = Tb, lb
        Tb = Tn; lb, u = g(Tb)
        if abs(Tb - Ta) < 1e-10*Tb:
            return Tb, u
    return (Tb, u) if (lb is not None and abs(lb) < 1e-6) else (None, None)


def punto_critico_directo(z, kij):
    """(Pc[psia], Tc[°R]) por el método de Heidemann-Khalil, o None."""
    z = np.asarray(z, dtype=float); z = z/z.sum()
    act = np.where(z > 1e-12)[0]
    _ACT[0] = act
    zc = z[act]
    bi = np.asarray(E.bi_eos(E._EOS_ACTIVA), dtype=float)[act]
    kk = np.asarray(kij, dtype=float)[np.ix_(act, act)]
    d1, d2 = _param_cubica()
    B = float(zc @ bi)
    Tc_i = np.asarray(E.crit_props(E._EOS_ACTIVA)[0], dtype=float)[act]
    T = 1.5*float(zc @ Tc_i)
    if len(act) == 1:
        return None
    def C_de(k, Tg):
        V = k*B
        Tk, u = _T_lambda0(zc, V, Tg, bi, kk, d1, d2)
        if Tk is None:
            return None, None
        return _cubico(zc, Tk, V, u, bi, kk, d1, d2), Tk
    # barrido en V/B (de gas a líquido) para acotar el cambio de signo de C
    ks = [4.0, 3.5, 3.0, 2.6, 2.3, 2.0, 1.8, 1.65, 1.5, 1.4, 1.3, 1.2, 1.12]
    prev = None; Tg = T; bracket = None
    for k in ks:
        Ck, Tk = C_de(k, Tg)
        if Ck is None:
            continue
        Tg = Tk
        if prev is not None and prev[1]*Ck <= 0:
            bracket = (prev, (k, Ck, Tk)); break
        prev = (k, Ck, Tk)
    if bracket is None:
        return None
    (ka, Ca, Ta), (kb, Cb, Tb) = bracket
    # Illinois (regula falsi modificada)
    lado = 0
    for _ in range(80):
        kn = kb - Cb*(kb - ka)/(Cb - Ca)
        Cn, Tn = C_de(kn, Tb)
        if Cn is None:
            kn = 0.5*(ka + kb); Cn, Tn = C_de(kn, Tb)
            if Cn is None:
                return None
        if Cn*Cb < 0:
            ka, Ca, Ta = kb, Cb, Tb
            lado = 0
        else:
            if lado == 1:
                Ca *= 0.5
            lado = 1
        kb, Cb, Tb = kn, Cn, Tn
        if abs(kb - ka) < 1e-11*kb or abs(Cb) < 1e-12:
            break
    V = kb*B; T = Tb
    aa = E.ai_alpha_vec_eos(E._EOS_ACTIVA, T)
    sa = np.sqrt(aa)[act]
    D = float(zc @ (np.outer(sa, sa)*(1.0 - kk)) @ zc)
    P = E.R_GAS*T/(V - B) - D/((V + d1*B)*(V + d2*B))
    if not (np.isfinite(P) and P > 0 and np.isfinite(T) and T > 0):
        return None
    return (float(P), float(T))


def punto_critico(z, kij):
    """(Pc[psia], Tc[°R]) de la mezcla con la EOS activa, o None. Cacheado.
    Método directo (Heidemann-Khalil); si no converge, la envolvente."""
    k = _clave(z)
    if k in _CACHE:
        return _CACHE[k]
    if k in _EN_CURSO:            # reentrancia: aun calculandose
        return None
    try:
        crit = punto_critico_directo(z, kij)
    except Exception:
        crit = None
    if crit is not None:
        _CACHE[k] = crit
        return crit
    _EN_CURSO.add(k)
    crit = None
    try:
        import envolvente_michelsen as EM
        r = EM.construir_envolvente(list(z), kij, max_pts=400)
        crit = r.get('critico')
        if crit is not None:
            crit = (float(crit[0]), float(crit[1]))
    except Exception:
        crit = None
    finally:
        _EN_CURSO.discard(k)
    _CACHE[k] = crit
    return crit


def limpiar_cache():
    _CACHE.clear()

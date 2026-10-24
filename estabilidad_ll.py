"""
estabilidad_ll.py — Estabilidad y flash con separación LÍQUIDO-LÍQUIDO.

En mezclas muy asimétricas (mucho metano junto con pesados, p. ej. C1/C9
95/5) la ecuación de estado predice que, a temperatura baja, el líquido se
separa en dos: uno rico en metano y otro rico en el pesado.  La prueba de
estabilidad del motor principal (réplica de la macro del Excel, con fase de
prueba vapor contra raíz de vapor y líquido contra raíz de líquido) no
detecta esa separación y declara "líquido único".

Este módulo implementa la prueba de Michelsen en su forma general:
  · cada composición se evalúa con la raíz de MENOR energía de Gibbs;
  · fases de prueba: Wilson tipo vapor, Wilson tipo líquido, el componente
    más pesado casi puro y el más liviano casi puro;
  · la mezcla es inestable si la distancia al plano tangente (tm) de alguna
    fase de prueba es negativa.
y un flash bifásico por sustitución sucesiva con las mismas raíces, que
converge tanto a vapor-líquido como a líquido-líquido.
"""
import numpy as np
import eos as E

NC = E.NC


def asimetrica(z, umbral=2.4):
    """True si la mezcla es lo bastante asimétrica para que pueda haber
    separación líquido-líquido (relación de Tc entre el componente más pesado
    y el más liviano presentes)."""
    Tc = np.asarray(E.crit_props(E.get_eos())[0], dtype=float)[:NC]
    act = [i for i in range(NC) if z[i] > 1e-10]
    if len(act) < 2:
        return False
    return max(Tc[act]) / max(min(Tc[act]), 1e-9) > umbral


def lnphi_mg(x, T, P, kij):
    """ln φ con la raíz de mínima energía de Gibbs.  Devuelve (lnφ, Z)."""
    x = np.asarray(x, dtype=float)
    am = E.am(x, T, kij); bm = E.bm(x)
    A, B = E.AB(am, bm, T, P)
    ZV, ZL = E.solve_Z(A, B)
    mejor = None
    for Z in ((ZV,) if abs(ZV - ZL) < 1e-12 else (ZV, ZL)):
        if Z is None or not np.isfinite(Z) or Z <= B:
            continue
        lp = np.asarray(E.ln_phi_vec(list(x), T, P, Z, am, bm, kij), dtype=float)
        m = x > 0
        g = float(np.sum(x[m] * lp[m]))
        if mejor is None or g < mejor[0]:
            mejor = (g, lp, Z)
    if mejor is None:
        return None, None
    return mejor[1], mejor[2]


def prueba(z, T, P, kij, tol=1e-10, max_it=300):
    """Prueba de estabilidad de Michelsen con varias fases de prueba.

    Devuelve dict(inestable, tm, w) — w es la composición de la fase de prueba
    con menor tm (estimación de la fase incipiente)."""
    z = np.asarray(z, dtype=float)
    act = np.where(z > 1e-12)[0]
    lz, _ = lnphi_mg(z, T, P, kij)
    if lz is None:
        return {'inestable': False, 'tm': 0.0, 'w': None}
    d = np.zeros(NC); d[act] = np.log(z[act]) + lz[act]
    Kw = np.array([E.Ki_wilson(i, T, P) for i in range(NC)], dtype=float)
    Kw = np.clip(Kw, 1e-30, 1e30)
    Tc = np.asarray(E.crit_props(E.get_eos())[0], dtype=float)[:NC]
    i_pes = act[np.argmax(Tc[act])]; i_liv = act[np.argmin(Tc[act])]
    semillas = [z*Kw, z/Kw]
    for i_dom in (i_pes, i_liv):
        w = np.where(z > 1e-12, 1e-3, 0.0); w[i_dom] = 1.0
        semillas.append(w)
    mejor = {'inestable': False, 'tm': 0.0, 'w': None}
    for W in semillas:
        W = np.where(z > 1e-12, np.clip(W, 1e-300, None), 0.0)
        tm = None
        for _ in range(max_it):
            y = W/W.sum()
            lw, _ = lnphi_mg(y, T, P, kij)
            if lw is None:
                break
            Wn = np.zeros(NC)
            Wn[act] = np.exp(np.clip(d[act] - lw[act], -700, 700))
            dif = np.max(np.abs(np.log(Wn[act]/W[act])))
            W = Wn
            if dif < tol:
                break
        y = W/W.sum()
        if np.max(np.abs(np.log(y[act]/z[act]))) < 1e-4:
            continue                                   # solución trivial
        lw, _ = lnphi_mg(y, T, P, kij)
        if lw is None:
            continue
        # tm modificado: 1 + Σ W_i (ln W_i + ln φ_i(w) − d_i − 1)
        tm = 1.0 + float(np.sum(W[act]*(np.log(W[act]) + lw[act] - d[act] - 1.0)))
        if tm < mejor['tm']:
            mejor = {'inestable': tm < -1e-8, 'tm': tm, 'w': list(y)}
    return mejor


def inestable(z, T, P, kij):
    """Atajo: True si la mezcla se separa (vapor-líquido o líquido-líquido)."""
    try:
        return bool(prueba(z, T, P, kij)['inestable'])
    except Exception:
        return False


def _rr(z, K, act):
    """Rachford-Rice robusto (bisección + Newton) para β en (0, 1)."""
    zk = z[act]; Kk = K[act]
    def f(b):
        return float(np.sum(zk*(Kk - 1.0)/(1.0 + b*(Kk - 1.0))))
    lo, hi = 0.0, 1.0          # en [0, 1] los denominadores son siempre > 0
    if f(lo) < 0:
        return 0.0
    if f(hi) > 0:
        return 1.0
    for _ in range(100):
        m = 0.5*(lo + hi)
        if f(m) > 0: lo = m
        else: hi = m
        if hi - lo < 1e-14:
            break
    return 0.5*(lo + hi)


def flash(z, T, P, kij, w, tol=1e-12, max_it=500):
    """Flash bifásico con raíces de mínima Gibbs, arrancando con la fase de
    prueba w (K_i = w_i/z_i).  Devuelve dict(V, x, y, K) con y = fase de menor
    peso molecular, o None si no converge a dos fases distintas."""
    z = np.asarray(z, dtype=float)
    act = np.where(z > 1e-12)[0]
    w = np.asarray(w, dtype=float)
    # Arranque: fase x = alimentación, fase y = fase de prueba; las K salen de
    # las fugacidades (más robusto que K = w/z cuando la fase incipiente es
    # casi pura).
    x = z/z.sum(); y = np.where(z > 1e-12, np.clip(w, 1e-300, None), 0.0); y = y/y.sum()
    K = np.ones(NC); V = 0.5
    for it in range(max_it):
        lx, _ = lnphi_mg(x, T, P, kij); ly, _ = lnphi_mg(y, T, P, kij)
        if lx is None or ly is None:
            return None
        Kn = np.ones(NC); Kn[act] = np.exp(np.clip(lx[act] - ly[act], -46, 46))
        dif = np.max(np.abs(np.log(Kn[act]/K[act])))
        K = Kn
        V = _rr(z, K, act)
        if V <= 0.0 or V >= 1.0:
            return None
        x = np.zeros(NC); y = np.zeros(NC)
        x[act] = z[act]/(1.0 + V*(K[act] - 1.0)); y[act] = K[act]*x[act]
        x /= x.sum(); y /= y.sum()
        if it > 2 and dif < tol:
            break
    if np.max(np.abs(np.log(K[act]))) < 1e-4:
        return None                                    # trivial
    PM = np.asarray(E.crit_props(E.get_eos())[3], dtype=float)[:NC]
    if float(np.dot(y, PM)) > float(np.dot(x, PM)):    # y = fase liviana
        x, y = y, x; V = 1.0 - V
        K = np.where(K > 0, 1.0/K, 1.0)
    return {'V': float(V), 'x': list(x), 'y': list(y), 'K': list(K)}

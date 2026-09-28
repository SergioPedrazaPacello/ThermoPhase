# -*- coding: utf-8 -*-
"""
saturacion.py — Puntos de saturación (T/P de rocío y de burbuja) robustos.

Método (igual con o sin agua):
  1. BARRIDO de la variable libre (T o P) desde el lado MONOFÁSICO hacia el
     bifásico, con un indicador de "región bifásica HC" (vapor + líquido HC):
        - sin agua : análisis de estabilidad (Michelsen) con el motor eos.py;
        - con agua : flash trifásico (flash_agua, Huron-Vidal) sobre la
                     composición TOTAL; bifásico HC ⇔ β_V > 0 y β_L > 0
                     (con o sin fase acuosa presente).
     El primer cruce hallado desde el lado monofásico es el punto de saturación
     NORMAL (criterio de HYSYS: T de rocío = la mayor, T de burbuja = la menor,
     P de rocío = la menor, P de burbuja = la mayor).
  2. BISECCIÓN del cruce y
  3. NEWTON sobre las ecuaciones exactas de saturación (igualdad de
     fugacidades + Σw = 1 + especificación), con la composición de la fase de
     prueba / flash como estimación inicial:
        - sin agua : z ↔ fase incipiente (mismas ecuaciones que antes);
        - con agua : si hay fase acuosa, Ec. 17-20 de Lindeloff-Michelsen
                     (fase HC incipiente en equilibrio con HC + acuosa);
                     si no, Ec. 9-10 (rocío/burbuja con la composición total).
  4. El tipo del punto se verifica: rocío ⇔ la fase incipiente es la más
     pesada (líquida); burbuja ⇔ la incipiente es la más liviana (vapor).
  Respaldos: el método anterior (GoalSeek, sin agua) y la intersección con la
  envolvente (Michelsen sin agua / Lindeloff-Michelsen con agua) refinada por
  Newton.
"""
import numpy as np

import eos as E
import envolvente_lm as LM

NC = E.NC
IDX_AGUA = E.IDX_AGUA

# Tipo: (fase buscada, variable fija, criterio de selección)
_TIPOS = {
    'T_rocio':   ('D', 'P'),
    'T_burbuja': ('B', 'P'),
    'P_rocio':   ('D', 'T'),
    'P_burbuja': ('B', 'T'),
}


# ════════════════════════════════════════════════════════════════════════════
# Sistema sin agua (13 comp., motor eos.py) con la interfaz de LM.Sistema
# ════════════════════════════════════════════════════════════════════════════
class Sistema13:
    def __init__(self, z13, kij):
        z = np.asarray(z13, dtype=float)[:NC]
        z = z/z.sum()
        self.act = np.where(z > 1e-14)[0]
        self.n = len(self.act)
        self.z = z[self.act]
        self.iw = None
        self.kij = np.asarray(kij, dtype=float)
        self._bi = np.asarray(E.bi_eos(E.get_eos()), dtype=float)

    def full(self, c):
        f = np.zeros(NC); f[self.act] = c
        return f

    def lnphi(self, c, T, P, fase='auto'):
        c = np.asarray(c, dtype=float)
        if not np.all(np.isfinite(c)) or c.sum() <= 0:
            return None
        cf = self.full(c/c.sum())
        am_ = E.am(cf, T, self.kij); bm_ = E.bm(cf)
        ZV, ZL = _raices_Z(*E.AB(am_, bm_, T, P))
        if fase == 'L':
            Z = ZL
        elif fase == 'V':
            Z = ZV
        else:
            if abs(ZV - ZL) < 1e-12:
                Z = ZV
            else:
                lv = E.ln_phi_vec(cf, T, P, ZV, am_, bm_, self.kij)
                ll = E.ln_phi_vec(cf, T, P, ZL, am_, bm_, self.kij)
                gv = float(np.dot(cf, lv)); gl = float(np.dot(cf, ll))
                return (lv if gv <= gl else ll)[self.act]
        lp = E.ln_phi_vec(cf, T, P, Z, am_, bm_, self.kij)
        if not np.all(np.isfinite(lp[self.act])):
            return None
        return lp[self.act]

    def bm(self, c, T=None):
        c = np.asarray(c, dtype=float); c = c/np.sum(c)
        return float(np.dot(c, self._bi[self.act]))

    def raices_par(self, a, b, T):
        return ('L', 'V') if self.bm(a) >= self.bm(b) else ('V', 'L')

    def es_acuosa(self, c):
        return False


def _raices_Z(A, B):
    """(ZV, ZL) como eos.solve_Z, pero con la raíz líquida exacta a presiones
    bajas (B pequeño): Cardano la pierde o la degrada por cancelación. Se
    obtiene por Newton desde Z → B⁺ (f(B) < 0 y f cóncava ⇒ convergencia
    monótona a la raíz MENOR)."""
    ZV, ZL = E.solve_Z(A, B)
    if B > 1e-3:
        return ZV, ZL
    if E.es_srk(E.get_eos()):
        p2, p1, p0 = -1.0, A - B - B*B, -A*B
    else:
        p2, p1, p0 = -(1.0 - B), A - 3.0*B*B - 2.0*B, -(A*B - B*B - B*B*B)
    z = B*(1.0 + 1e-10)
    for _ in range(300):
        f = ((z + p2)*z + p1)*z + p0
        d = (3.0*z + 2.0*p2)*z + p1
        if d <= 0:
            return ZV, ZL                # sin raíz líquida (solo vapor)
        dz = f/d
        z -= dz
        if abs(dz) <= 1e-15*z:
            break
    d = (3.0*z + 2.0*p2)*z + p1
    if z > B and d > 0 and ZV - z > 1e-9*ZV:
        return ZV, z
    return ZV, ZL


def _wilson(S, T, P):
    K = np.array([E.Ki_wilson(i, T, P) for i in range(NC)])
    return K[S.act]


def _estabilidad13(S, T, P):
    """Prueba de estabilidad (Michelsen) con semillas vapor y líquido.
    Devuelve (inestable, y_prueba) — y_prueba = composición de la fase de
    prueba no trivial con mayor ΣW (la estimación de la fase incipiente)."""
    lz = S.lnphi(S.z, T, P, 'auto')
    if lz is None:
        return False, None
    d = np.log(S.z) + lz
    Kw = np.clip(_wilson(S, T, P), 1e-30, 1e30)
    mejor = None
    for W in (S.z*Kw, S.z/Kw):
        W = np.clip(W, 1e-300, None)
        for _ in range(400):
            y = W/W.sum()
            lw = S.lnphi(y, T, P, 'auto')
            if lw is None:
                break
            Wn = np.exp(np.clip(d - lw, -700, 700))
            if np.max(np.abs(np.log(np.clip(Wn, 1e-300, None)/W))) < 1e-10:
                W = Wn; break
            W = Wn
        y = W/W.sum()
        if np.max(np.abs(np.log(np.clip(y, 1e-300, None)/S.z))) < 1e-4:
            continue                              # solución trivial
        if mejor is None or W.sum() > mejor[0]:
            mejor = (W.sum(), y)
    if mejor is None:
        return False, None
    return mejor[0] > 1.0 + 1e-10, mejor[1]


# ════════════════════════════════════════════════════════════════════════════
# Barrido + bisección genéricos
# ════════════════════════════════════════════════════════════════════════════
def _frontera(indic, xs, rel=2e-4, saltar_dentro=True):
    """xs: valores de la variable libre ordenados desde el lado monofásico.
    Devuelve (x_dentro, info_dentro, x_fuera) del primer cruce, o None."""
    prev = None
    for x in xs:
        ins, info = indic(x)
        if ins:
            if prev is None:
                # el barrido arrancó dentro de una zona inestable (p. ej.
                # separación L-L a T muy baja): se busca primero la salida
                if not saltar_dentro:
                    return None
                continue
            a, b, ib = prev, x, info
            for _ in range(60):
                if abs(np.log(b/a)) < rel:
                    break
                m = np.sqrt(a*b)
                i2, inf2 = indic(m)
                if i2:
                    b, ib = m, inf2
                else:
                    a = m
            return b, ib, a
        prev = x
    return None


def _malla(lo, hi, paso, desde_arriba):
    n = int(np.ceil(np.log(hi/lo)/np.log(1.0 + paso))) + 1
    xs = lo*(1.0 + paso)**np.arange(n)
    xs = xs[xs <= hi*1.0000001]
    return xs[::-1] if desde_arriba else xs


# ════════════════════════════════════════════════════════════════════════════
# Newton sobre las ecuaciones de saturación
# ════════════════════════════════════════════════════════════════════════════
def _res_2f(S, X, spec, Sv):
    """= LM._res_dew con límites amplios de T y P (rocío inferior de fluidos
    pesados a P muy bajas)."""
    n = S.n
    T = np.exp(X[n]); P = np.exp(X[n+1])
    if not (50 < T < 3000 and 1e-14 < P < 1e5):
        return None
    lnK = np.clip(X[:n], -80, 80)
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


def _res_3f(S, X, spec, Sv):
    """= LM._res_3l (Ec. 17-20) con límites amplios de T y P."""
    n = S.n
    T = np.exp(X[2*n]); P = np.exp(X[2*n+1]); b = X[2*n+2]
    if not (50 < T < 3000 and 1e-14 < P < 1e5) or not (-0.05 < b < 1.05):
        return None
    c = LM._comp3(S, X)
    if c is None:
        return None
    w, y, x = c
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
    lw = S.lnphi(w, T, P, ph['w']); ly = S.lnphi(y, T, P, ph['y'])
    lx = S.lnphi(x, T, P, ph['x'])
    if lw is None or ly is None or lx is None:
        return None
    g = np.empty(2*n+3)
    g[:n] = X[:n] + ly - lw
    g[n:2*n] = X[n:2*n] + lx - lw
    g[2*n] = w.sum() - 1.0
    g[2*n+1] = np.sum(y - x)
    g[2*n+2] = X[spec] - Sv
    return g


def _newton_2f(S, inc, T, P, var_fija, valor):
    """Ec. 9-10: z (fase existente) ↔ w (incipiente). X = [lnK, lnT, lnP]."""
    n = S.n
    X0 = np.concatenate([np.log(np.clip(inc, 1e-300, None)/S.z),
                         [np.log(T), np.log(P)]])
    spec = n+1 if var_fija == 'P' else n
    Sv = np.log(valor)
    X0[spec] = Sv
    X, _ = LM._newton(lambda XX: _res_2f(S, XX, spec, Sv), X0,
                      tol=1e-12, maxit=60, maxstep=1.0)
    if X is None:
        return None
    lnK = X[:n]
    if np.max(np.abs(lnK)) < 1e-4:
        return None                               # solución trivial
    w = np.exp(lnK)*S.z
    Ts, Ps = float(np.exp(X[n])), float(np.exp(X[n+1]))
    if S.es_acuosa(w):
        return None
    tipo = 'D' if S.bm(w, Ts) > S.bm(S.z, Ts) else 'B'
    return {'T': Ts, 'P': Ps, 'tipo': tipo, 'inc': w, 'ex': S.z.copy(),
            'aq': None, 'beta': 1.0}


def _newton_3f(S, inc, ex, aq, beta, T, P, var_fija, valor):
    """Ec. 17-20 (Lindeloff-Michelsen): fase HC incipiente w en equilibrio con
    la fase HC existente y (fracción β) y la acuosa x (1-β)."""
    n = S.n
    inc = np.clip(inc, 1e-300, None)
    X0 = np.concatenate([np.log(np.clip(ex, 1e-300, None)/inc),
                         np.log(np.clip(aq, 1e-300, None)/inc),
                         [np.log(T), np.log(P), beta]])
    spec = 2*n+1 if var_fija == 'P' else 2*n
    Sv = np.log(valor)
    X0[spec] = Sv
    X, _ = LM._newton(lambda XX: _res_3f(S, XX, spec, Sv), X0,
                      tol=1e-12, maxit=60, maxstep=1.0)
    if X is None:
        return None
    b = float(X[2*n+2])
    if not (-1e-9 <= b <= 1.0 + 1e-9):
        return None
    c = LM._comp3(S, X)
    if c is None:
        return None
    w, y, x = c
    if np.max(np.abs(X[:n])) < 1e-4:
        return None                               # incipiente = existente
    if S.es_acuosa(w) or S.es_acuosa(y) or not S.es_acuosa(x):
        return None
    Ts, Ps = float(np.exp(X[2*n])), float(np.exp(X[2*n+1]))
    tipo = 'D' if S.bm(w, Ts) > S.bm(y, Ts) else 'B'
    return {'T': Ts, 'P': Ps, 'tipo': tipo, 'inc': w, 'ex': y, 'aq': x,
            'beta': b}


# ════════════════════════════════════════════════════════════════════════════
# Selección del punto normal entre varios candidatos
# ════════════════════════════════════════════════════════════════════════════
def _elegir(cands, tipo, var_fija):
    c = [s for s in cands if s is not None and s['tipo'] == tipo]
    if not c:
        return None
    if var_fija == 'P':         # se busca T
        return max(c, key=lambda s: s['T']) if tipo == 'D' else min(c, key=lambda s: s['T'])
    return min(c, key=lambda s: s['P']) if tipo == 'D' else max(c, key=lambda s: s['P'])


def _mallas(S_Tc, var_fija, tipo, P_lo=1e-6):
    """Malla de barrido de la variable libre, desde el lado monofásico."""
    Tc_max = float(np.max(S_Tc)); Tc_min = float(np.min(S_Tc))
    if var_fija == 'P':          # barrido en T
        lo = max(100.0, 0.35*Tc_min); hi = 1.15*Tc_max
        return _malla(lo, hi, 0.01, desde_arriba=(tipo == 'D'))
    lo, hi = min(1e-6, P_lo), 15000.0       # barrido en P
    return _malla(lo, hi, 0.08, desde_arriba=(tipo == 'B'))


# ════════════════════════════════════════════════════════════════════════════
# SIN AGUA
# ════════════════════════════════════════════════════════════════════════════
def _P_lo(z, Tc, Pc, om, T):
    """Cota inferior de P para el barrido: 1 % de la P de rocío de Wilson
    (1/Σ z_i/Psat_i), para atrapar el rocío inferior de fluidos pesados."""
    Ps = Pc*np.exp(5.373*(1.0 + om)*(1.0 - Tc/T))
    return 0.01/np.sum(z/np.maximum(Ps, 1e-300))


def _sat_seco(tipo_calc, valor, z13, kij):
    tipo, var_fija = _TIPOS[tipo_calc]
    S = Sistema13(z13, kij)
    cp = E.crit_props(E.get_eos())
    TC = np.asarray(cp[0], dtype=float)[S.act]
    P_lo = 1e-6
    if var_fija == 'T':
        P_lo = _P_lo(S.z, TC, np.asarray(cp[1], dtype=float)[S.act],
                     np.asarray(cp[2], dtype=float)[S.act], valor)
    cands = []

    def indic(v):
        T, P = (v, valor) if var_fija == 'P' else (valor, v)
        try:
            return _estabilidad13(S, T, P)
        except Exception:
            return False, None

    # 1) barrido + bisección + Newton
    fr = _frontera(indic, _mallas(TC, var_fija, tipo, P_lo))
    if fr is not None:
        v_in, y_in, v_out = fr
        T, P = (v_in, valor) if var_fija == 'P' else (valor, v_in)
        sol = _newton_2f(S, y_in, T, P, var_fija, valor)
        if sol is not None and abs(np.log((sol['T'] if var_fija == 'P' else sol['P'])/v_in)) < 0.05:
            cands.append(sol)

    # 2) método anterior (GoalSeek) como candidato adicional / respaldo
    if not cands:
        try:
            import envolvente as _env
            r = _env.punto_saturacion(tipo_calc, valor, list(z13), kij)
            if r and r.get('exito'):
                inc = np.asarray(r['x'] if tipo == 'D' else r['y'], dtype=float)[:NC]
                inc = inc[S.act]; inc = inc/inc.sum()
                sol = _newton_2f(S, inc, r['T'], r['P'], var_fija, valor)
                if sol is not None:
                    cands.append(sol)
        except Exception:
            pass
    sol = _elegir(cands, tipo, var_fija)
    if sol is None:
        return {'exito': False}
    T, P = sol['T'], sol['P']
    inc = S.full(sol['inc']); zf = S.full(S.z)
    if tipo == 'D':
        y, x = list(zf), list(inc)
    else:
        y, x = list(inc), list(zf)
    Ki = [y[i]/x[i] if x[i] > 0 else 1.0 for i in range(NC)]
    import envolvente as _env
    props = _env.propiedades_punto(T, P, x, y, kij)
    return {'T': T, 'P': P, 'x': x, 'y': y, 'z': list(zf), 'Ki': Ki,
            'exito': True, 'props': props, 'agua': False}


# ════════════════════════════════════════════════════════════════════════════
# CON AGUA (región bifásica HIDROCARBURO sobre la composición total)
# ════════════════════════════════════════════════════════════════════════════
def _sol_desde_flash(S, rt, T, P, var_fija, valor):
    """Newton desde un flash trifásico dentro de la región HC bifásica."""
    act = S.act
    bV, bL, bW = rt.get('beta_V', 0.0), rt.get('beta_L', 0.0), rt.get('beta_W', 0.0)
    y = np.asarray(rt['y'], dtype=float)[act]; x = np.asarray(rt['x'], dtype=float)[act]
    if bL <= bV:
        inc, ex, bex = x, y, bV
    else:
        inc, ex, bex = y, x, bL
    sols = []
    if bW and bW > 1e-9 and rt.get('w') is not None:
        aq = np.asarray(rt['w'], dtype=float)[act]
        sols.append(_newton_3f(S, inc/inc.sum(), ex/ex.sum(), aq/aq.sum(),
                               bex/(bex + bW), T, P, var_fija, valor))
        if sols[-1] is None or sols[-1]['beta'] > 1.0 - 1e-9:
            sols.append(_newton_2f(S, inc/inc.sum(), T, P, var_fija, valor))
    else:
        sols.append(_newton_2f(S, inc/inc.sum(), T, P, var_fija, valor))
        if sols[-1] is None:
            aq = np.full(S.n, 1e-6)
            if S.iw is not None:
                aq[S.iw] = 1.0
            sols.append(_newton_3f(S, inc/inc.sum(), ex/ex.sum(), aq/aq.sum(),
                                   0.999, T, P, var_fija, valor))
    return [s for s in sols if s is not None]


def _sol_desde_seco(S, seco, z14, tipo, var_fija, valor, eos=None):
    """Newton del sistema con agua desde el punto HC sin agua."""
    T, P = seco['T'], seco['P']
    act = S.act
    def ext(c13, xw):
        c = np.zeros(14); c[:NC] = np.asarray(c13, dtype=float)[:NC]
        c = c/c.sum()*(1.0 - xw); c[IDX_AGUA] = xw
        return c[act]
    inc13 = seco['x'] if tipo == 'D' else seco['y']
    ex13 = seco['y'] if tipo == 'D' else seco['x']
    inc = ext(inc13, 1e-4); ex = ext(ex13, 1e-4)
    zw = z14[IDX_AGUA]
    sols = []
    # (a) fases existentes (HC + acuosa) desde el flash en el punto sin agua
    try:
        import flash_agua as fa
        rt = fa.flash_trifasico(z14, T, P, eos=eos or E.get_eos(), metodo='hv')
    except Exception:
        rt = None
    if rt is not None and (rt.get('beta_W') or 0.0) > 1e-9:
        bV = rt.get('beta_V') or 0.0; bL = rt.get('beta_L') or 0.0
        hc = np.asarray(rt['y'] if bV >= bL else rt['x'], dtype=float)[act]
        aq = np.asarray(rt['w'], dtype=float)[act]
        bh = max(bV, bL)
        if S.es_acuosa(aq) and hc.sum() > 0:
            hc = hc/hc.sum()
            # fase incipiente consistente con la fase HC existente (que ya
            # cedió CO2/H2S… al agua): prueba de estabilidad sembrada con la
            # incipiente sin agua
            inc_a = inc
            try:
                k_, tr = LM.estabilidad(S, hc, T, P, 'hc', W0=inc)
                if tr is not None and not S.es_acuosa(tr) and \
                        np.max(np.abs(np.log(np.clip(tr, 1e-300, None)/np.clip(hc, 1e-300, None)))) > 1e-3:
                    inc_a = tr
            except Exception:
                pass
            s3 = _newton_3f(S, inc_a, hc, aq/aq.sum(),
                            bh/(bh + rt['beta_W']), T, P, var_fija, valor)
            if s3 is not None and s3['beta'] < 1.0 - 1e-9:
                sols.append(s3)
    # (b) fase acuosa inicial por prueba de estabilidad frente a la fase HC
    if not sols:
        try:
            k, aq = LM.estabilidad(S, ex, T, P, 'aq')
        except Exception:
            aq = None
        if aq is not None and S.es_acuosa(aq):
            s3 = _newton_3f(S, inc, ex, aq, max(1e-3, 1.0 - zw), T, P, var_fija, valor)
            if s3 is not None and s3['beta'] < 1.0 - 1e-9:
                sols.append(s3)
    if not sols:
        s2 = None if S.es_acuosa(S.z) else _newton_2f(S, inc, T, P, var_fija, valor)
        if s2 is not None:
            # sin fase acuosa: z (con agua) debe ser estable frente al agua
            try:
                k, aq2 = LM.estabilidad(S, S.z, s2['T'], s2['P'], 'aq')
                if k is not None and (k >= -1e-9 or not S.es_acuosa(aq2)):
                    sols.append(s2)
            except Exception:
                pass
    for s_ in sols:
        v0 = T if var_fija == 'P' else P
        vs = s_['T'] if var_fija == 'P' else s_['P']
        if s_['tipo'] == tipo and abs(np.log(vs/v0)) < 0.5:
            return s_
    return None


def _lado_externo_ok(indic, sol, tipo, var_fija):
    """El punto es el NORMAL si justo del lado monofásico (T mayor para el
    rocío en T, T menor para la burbuja en T, P menor para el rocío en P,
    P mayor para la burbuja en P) no hay región bifásica HC."""
    if var_fija == 'P':
        v = sol['T']; f = 1.003 if tipo == 'D' else 1.0/1.003
    else:
        v = sol['P']; f = 1.0/1.01 if tipo == 'D' else 1.01
    ins, _ = indic(v*f)
    return not ins


def _desde_envolvente(S, z14, eos, var_fija, valor):
    """Respaldo: intersección con las líneas HC de la envolvente de
    Lindeloff-Michelsen (2-HC y 3-HC), refinada por Newton."""
    r = LM.envolvente_agua(np.asarray(z14, dtype=float), eos, 'hv')
    S = r['_S']; n = S.n
    lv = np.log(valor)
    cands = []
    for tipo_l, pts in r.get('_raw_dew', []):
        if tipo_l != 'hc':
            continue
        k = n+1 if var_fija == 'P' else n
        for a, b in zip(pts[:-1], pts[1:]):
            if (a[k]-lv)*(b[k]-lv) <= 0 and a[k] != b[k]:
                f = (lv-a[k])/(b[k]-a[k]); X = a + f*(b-a)
                inc = np.exp(X[:n])*S.z
                cands.append(_newton_2f(S, inc/inc.sum(), np.exp(X[n]),
                                        np.exp(X[n+1]), var_fija, valor))
    for incip, pts in r.get('_raw', []):
        if incip != 'hc':
            continue
        k = 2*n+1 if var_fija == 'P' else 2*n
        pts = [p for p in pts if not np.isnan(p[0])]
        for a, b in zip(pts[:-1], pts[1:]):
            if (a[k]-lv)*(b[k]-lv) <= 0 and a[k] != b[k]:
                f = (lv-a[k])/(b[k]-a[k]); X = a + f*(b-a)
                c = LM._comp3(S, X)
                if c is None:
                    continue
                w, y, x = c
                cands.append(_newton_3f(S, w/w.sum(), y/y.sum(), x/x.sum(),
                                        float(np.clip(X[2*n+2], 0, 1)),
                                        np.exp(X[2*n]), np.exp(X[2*n+1]),
                                        var_fija, valor))
    return S, [c for c in cands if c is not None]


def _sat_agua(tipo_calc, valor, z14, eos):
    import flash_agua as fa
    tipo, var_fija = _TIPOS[tipo_calc]
    z14 = np.asarray(z14, dtype=float); z14 = z14/z14.sum()
    S = LM.Sistema(z14, eos, 'hv')
    cp = E.crit_props(eos)
    ihc = [i for i in S.act if i < NC]
    TC = np.asarray(cp[0], dtype=float)[ihc]
    P_lo = 1e-6
    if var_fija == 'T':
        zh = z14[ihc]/z14[ihc].sum()
        P_lo = _P_lo(zh, TC, np.asarray(cp[1], dtype=float)[ihc],
                     np.asarray(cp[2], dtype=float)[ihc], valor)

    def indic(v):
        T, P = (v, valor) if var_fija == 'P' else (valor, v)
        try:
            rt = fa.flash_trifasico(z14, T, P, eos=eos, metodo='hv')
        except Exception:
            return False, None
        bV = rt.get('beta_V', 0.0) or 0.0; bL = rt.get('beta_L', 0.0) or 0.0
        if not (bV > 1e-9 and bL > 1e-9):
            return False, rt
        # dos fases HC realmente distintas (descarta divisiones triviales
        # del flash cerca del punto crítico: V y L con la misma composición)
        y = np.asarray(rt['y'], dtype=float)[S.act]
        x = np.asarray(rt['x'], dtype=float)[S.act]
        d = np.max(np.abs(np.log(np.clip(y, 1e-300, None)/np.clip(x, 1e-300, None))))
        return d > 1e-4, rt

    # 1) Semilla: el punto de saturación HC SIN agua (mismo tipo, misma
    #    condición) — el agua sólo lo desplaza ligeramente, así que la rama
    #    (punto normal) se conserva.  Newton sobre el sistema con agua.
    cands = []
    seco = None
    try:
        kij_h = E.kij_base(eos)
        seco = _sat_seco(tipo_calc, valor, list(z14[:NC]/z14[:NC].sum()), kij_h)
    except Exception:
        seco = None
    if seco and seco.get('exito'):
        sol = _sol_desde_seco(S, seco, z14, tipo, var_fija, valor, eos)
        if sol is not None and _lado_externo_ok(indic, sol, tipo, var_fija):
            cands.append(sol)
    # 2) Barrido con el flash trifásico (región bifásica HC) + Newton:
    #    primero una ventana local alrededor del punto sin agua, luego global.
    if not (seco and seco.get('exito')):
        # Sin punto HC en la mezcla sin agua a esta condición: el agua sólo
        # desplaza ligeramente la región bifásica HC, así que tampoco lo hay.
        return {'exito': False}
    mallas = []
    if seco and seco.get('exito'):
        v0 = seco['T'] if var_fija == 'P' else seco['P']
        if var_fija == 'P':
            mallas.append(_malla(v0/1.12, v0*1.12, 0.004, desde_arriba=(tipo == 'D')))
        else:
            mallas.append(_malla(v0/2.5, v0*2.5, 0.02, desde_arriba=(tipo == 'B')))
    mallas.append(_mallas(TC, var_fija, tipo, P_lo))
    for k_m, malla in enumerate(mallas):
        if cands:
            break
        fr = _frontera(indic, malla, saltar_dentro=(k_m == len(mallas) - 1))
        if fr is None:
            continue
        v_in, rt, v_out = fr
        T, P = (v_in, valor) if var_fija == 'P' else (valor, v_in)
        for s in _sol_desde_flash(S, rt, T, P, var_fija, valor):
            vs = s['T'] if var_fija == 'P' else s['P']
            if abs(np.log(vs/v_in)) < 0.05 and s['tipo'] == tipo:
                cands.append(s)
    sol = _elegir(cands, tipo, var_fija)
    if sol is None and seco and seco.get('exito'):
        # sólo si el punto HC existe sin agua (si no, tampoco con agua)
        try:
            S, c2 = _desde_envolvente(S, z14, eos, var_fija, valor)
            sol = _elegir(c2, tipo, var_fija)
        except Exception:
            sol = None
    if sol is None:
        return {'exito': False}
    return _armar_agua(S, sol, z14, eos, tipo)


def _armar_agua(S, sol, z14, eos, tipo):
    """Resultado con agua: composiciones de 14 comp. (vapor, líquido HC,
    acuosa) y propiedades de cada fase con propiedades_agua."""
    import flash_agua as fa
    import propiedades_agua as pa
    T, P = sol['T'], sol['P']
    inc = S.full(sol['inc']); ex = S.full(sol['ex'])
    aq = S.full(sol['aq']) if sol['aq'] is not None else None
    b = sol['beta']
    if tipo == 'D':      # vapor existente, líquido HC incipiente
        y, x = ex, inc
        bV, bL = b, 0.0
    else:                # líquido HC existente, vapor incipiente
        y, x = inc, ex
        bV, bL = 0.0, b
    bW = (1.0 - b) if aq is not None else 0.0

    # Z de cada fase con el mismo modelo del flash (Huron-Vidal)
    fa._METODO = 'hv'; fa._EOS_CTX = eos; fa._T_CTX = T
    Tc, Pc, om, PM14, kij14 = fa._params_14(eos)
    aa, bi = fa._ai_bi(eos, Tc, Pc, om, T)
    es_srk = E.es_srk(eos)
    fy, fx = S.raices_par(sol['ex'] if tipo == 'D' else sol['inc'],
                          sol['inc'] if tipo == 'D' else sol['ex'], T)
    _, ZV = fa._ln_phi(y, aa, bi, kij14, T, P, es_srk, fy)
    _, ZL = fa._ln_phi(x, aa, bi, kij14, T, P, es_srk, fx)
    ZW = None
    if aq is not None:
        _, ZW = fa._ln_phi(aq, aa, bi, kij14, T, P, es_srk, 'L')
    # β mínimo para que propiedades_fases calcule también la fase incipiente
    eps = 1e-6
    rt = {'beta_V': max(bV, eps), 'beta_L': max(bL, eps), 'beta_W': bW,
          'y': y, 'x': x, 'w': aq if aq is not None else np.zeros(14),
          'Z_V': ZV, 'Z_L': ZL, 'Z_W': ZW, 'PM': PM14, 'z': z14}
    try:
        pr = pa.propiedades_fases(rt, T, P, eos, metodo_densidad='COSTALD')
    except Exception:
        pr = {'V': {}, 'L': {}, 'W': {}}
    pV, pL, pW = pr.get('V', {}) or {}, pr.get('L', {}) or {}, pr.get('W', {}) or {}
    props = {'PM_v': pV.get('PM'), 'PM_l': pL.get('PM'),
             'ZV': pV.get('Z'), 'ZL': pL.get('Z'),
             'rho_v': pV.get('rho'), 'rho_l': pL.get('rho'),
             'sg_v': pV.get('sg'), 'sg_l': pL.get('sg'),
             'H_v': pV.get('H'), 'H_l': pL.get('H'),
             'S_v': pV.get('S'), 'S_l': pL.get('S'),
             'mu_v': pV.get('mu'), 'mu_l': pL.get('mu')}
    # Mezcla (composición total, fases existentes)
    fases = [(bV, pV), (bL, pL), (bW, pW)]
    PMz = float(np.dot(z14, PM14))
    inv = 0.0
    for bk, pk in fases:
        if bk > 0 and pk.get('rho') and pk.get('PM'):
            inv += bk*pk['PM']/PMz/pk['rho']
    props['PM_z'] = PMz
    props['rho_z'] = (1.0/inv) if inv > 0 else None
    Ki = [y[i]/x[i] if x[i] > 0 else 1.0 for i in range(14)]
    return {'T': T, 'P': P, 'x': list(x), 'y': list(y), 'z': list(z14),
            'w': list(aq) if aq is not None else None, 'Ki': Ki,
            'exito': True, 'props': props, 'props_w': pW, 'agua': True,
            'beta_W': bW}


# ════════════════════════════════════════════════════════════════════════════
# Punto de entrada
# ════════════════════════════════════════════════════════════════════════════
def punto_saturacion(tipo_calc, valor, z, kij=None, eos=None):
    """tipo_calc: 'T_rocio' | 'T_burbuja' | 'P_rocio' | 'P_burbuja'.
    valor: P [psia] (para T_*) o T [°R] (para P_*).
    z: 13 comp. (sin agua) o 14 comp. (índice 13 = agua).
    Con agua > 0 el punto es el de la región bifásica HIDROCARBURO calculado
    sobre la composición total (Huron-Vidal, como el flash trifásico)."""
    eos = eos or E.get_eos()
    if kij is None:
        kij = E.kij_base(eos)
    z = list(z)
    if len(z) > NC and z[IDX_AGUA] > 1e-12:
        return _sat_agua(tipo_calc, valor, z, eos)
    z13 = np.asarray(z[:NC], dtype=float); z13 = z13/z13.sum()
    return _sat_seco(tipo_calc, valor, list(z13), kij)

"""
envolvente_auditoria.py — Verificación independiente de la envolvente de fases
y reconstrucción por barrido cuando la verificación falla.

La envolvente se traza por continuación (envolvente_michelsen).  En mezclas
asimétricas la continuación puede dejar defectos: rectas que unen tramos
sueltos, picos junto al crítico o ramas que faltan.  Este módulo:

  1. AUDITA la envolvente con pruebas de estabilidad de Michelsen, que no
     dependen de la continuación:
       · cada tramo largo de la curva debe separar una zona estable de una
         inestable (se prueba un punto a cada lado de su punto medio);
       · en varias isotermas, cada cambio estable↔inestable hallado por
         barrido de presión debe tener un cruce de la envolvente cerca, y
         viceversa.
  2. Si la auditoría falla, RECONSTRUYE la frontera bifásica por barrido de
     estabilidad en isotermas e isobaras, con bisección de cada cruce, y
     ordena los puntos en una curva.  El punto crítico es donde la fase
     incipiente cambia de tipo (burbuja ↔ rocío).

Si la auditoría pasa, la envolvente original se devuelve sin cambios.

Unidades: T en °R, P en psia (las del motor).
"""
import math
import numpy as np

import eos as E
import saturacion as S

P_TOPE = 10000.0


# ── Indicador de inestabilidad ──────────────────────────────────────────────
class _Indicador:
    def __init__(self, z, kij):
        self.sis = S.Sistema13(list(z)[:E.NC], kij)
        self._bz = self.sis.bm(self.sis.z)
        self.cache = {}
        self._idx_sem = None

    def _semillas_puras(self, T, P):
        """Prueba complementaria con semillas de componente casi puro.  Las
        semillas de Wilson (vapor/líquido) pueden caer en la solución trivial
        cuando la fase incipiente es un segundo líquido (p. ej. líquido rico en
        CO2 en mezclas C1/CO2 a baja T), dejando 'islas' falsamente estables
        dentro de la región bifásica.  Se usan semillas enriquecidas (25 % y 98 %) en
        los componentes más liviano y más pesado y en CO2, N2 y H2S."""
        sis = self.sis
        if self._idx_sem is None:
            act = list(sis.act); tc = [E.TC[i] for i in act]
            cand = {act[int(np.argmin(tc))], act[int(np.argmax(tc))]}
            for nombre in ('[CO₂]', '[N₂]', '[H₂S]'):
                for i in act:
                    if nombre in E.NOMBRES[i]:
                        cand.add(i)
            self._idx_sem = [act.index(i) for i in sorted(cand)]
        lz = sis.lnphi(sis.z, T, P, 'auto')
        if lz is None:
            return False, None
        d = np.log(sis.z) + lz
        n = len(sis.z)
        for k, a in ((k, a) for k in self._idx_sem for a in (0.25, 0.98)):
            W = (1.0 - a)*sis.z.copy(); W[k] += a
            for it in range(300):
                y = W/W.sum()
                lw = sis.lnphi(y, T, P, 'auto')
                if lw is None:
                    break
                Wn = np.exp(np.clip(d - lw, -700, 700))
                if np.max(np.abs(np.log(np.clip(Wn, 1e-300, None)/W))) < 1e-9:
                    W = Wn; break
                W = Wn
                if it > 20 and np.max(np.abs(np.log(np.clip(W/W.sum(), 1e-300, None)/sis.z))) < 1e-3:
                    break                                   # va a la trivial
            y = W/W.sum()
            if np.max(np.abs(np.log(np.clip(y, 1e-300, None)/sis.z))) < 1e-4:
                continue
            if W.sum() > 1.0 + 1e-8:
                return True, y
        return False, None

    def __call__(self, T, P):
        """(inestable, tipo) — tipo 'B' si la fase incipiente es más liviana
        que la alimentación (burbuja), 'D' si es más pesada (rocío)."""
        clave = (round(T, 6), round(P, 6))
        if clave in self.cache:
            return self.cache[clave]
        try:
            ins, y = S._estabilidad13(self.sis, float(T), float(P))
            if not ins:
                ins, y = self._semillas_puras(float(T), float(P))
        except Exception:
            ins, y = False, None
        tipo = None
        if ins and y is not None:
            tipo = 'D' if self.sis.bm(y) > self._bz else 'B'
        self.cache[clave] = (bool(ins), tipo)
        return self.cache[clave]


def _bisecar_P(ind, T, Pa, Pb, rel=2e-4):
    """Cruce en P entre Pa (estado sa) y Pb (estado distinto), en ln P."""
    sa = ind(T, Pa)[0]
    for _ in range(40):
        if abs(math.log(Pb/Pa)) < rel:
            break
        Pm = math.sqrt(Pa*Pb)
        if ind(T, Pm)[0] == sa:
            Pa = Pm
        else:
            Pb = Pm
    ins_a, ta = ind(T, Pa); ins_b, tb = ind(T, Pb)
    return math.sqrt(Pa*Pb), (ta if ins_a else tb)


def _bisecar_T(ind, P, Ta, Tb, rel=2e-4):
    sa = ind(Ta, P)[0]
    for _ in range(40):
        if abs(Tb - Ta) < rel*Ta:
            break
        Tm = 0.5*(Ta + Tb)
        if ind(Tm, P)[0] == sa:
            Ta = Tm
        else:
            Tb = Tm
    ins_a, ta = ind(Ta, P); ins_b, tb = ind(Tb, P)
    return 0.5*(Ta + Tb), (ta if ins_a else tb)


def _cruces_isoterma(ind, T, Ps):
    out = []
    est = [ind(T, P)[0] for P in Ps]
    for k in range(1, len(Ps)):
        if est[k] != est[k-1]:
            out.append(_bisecar_P(ind, T, Ps[k-1], Ps[k]))
    return out


def _cruces_isobara(ind, P, Ts):
    out = []
    est = [ind(T, P)[0] for T in Ts]
    for k in range(1, len(Ts)):
        if est[k] != est[k-1]:
            out.append(_bisecar_T(ind, P, Ts[k-1], Ts[k]))
    return out


def _cruces_polilinea_T(env, T):
    """Presiones donde la polilínea de la envolvente cruza la isoterma T."""
    out = []
    for i in range(1, len(env)):
        (p0, t0), (p1, t1) = env[i-1], env[i]
        if (t0 - T)*(t1 - T) < 0 or (t1 == T and t0 != T):
            f = (T - t0)/(t1 - t0) if t1 != t0 else 0.0
            out.append(math.exp(math.log(p0) + f*(math.log(p1) - math.log(p0))))
    return out


# ════════════════════════════════════════════════════════════════════════════
# 1) Auditoría
# ════════════════════════════════════════════════════════════════════════════
def auditar(z, kij, env, crit=None, n_iso=7, n_P=48, P_ini=14.7, T_rango=None):
    """Devuelve (ok, motivos).  ok=False si la envolvente tiene defectos."""
    motivos = []
    if not env or len(env) < 8:
        return False, ["envolvente vacía o muy corta"]
    ind = _Indicador(z, kij)
    Ts = [t for _, t in env]; lP = [math.log(max(p, 1e-6)) for p, _ in env]
    spT = max(max(Ts) - min(Ts), 1.0); spP = max(max(lP) - min(lP), 0.1)

    # ── a) tramos largos: deben separar estable de inestable ────────────────
    malos = 0
    for i in range(1, len(env)):
        (p0, t0), (p1, t1) = env[i-1], env[i]
        dx = (t1 - t0)/spT; dy = (math.log(p1) - math.log(p0))/spP
        L = math.hypot(dx, dy)
        if L < 0.04:
            continue
        tm = 0.5*(t0 + t1); lpm = 0.5*(math.log(p0) + math.log(p1))
        if crit is not None:
            dc = math.hypot((tm - crit[1])/spT, (lpm - math.log(crit[0]))/spP)
            if dc < 0.06:
                continue
        nx, ny = -dy/L, dx/L
        separa = False; probado = False
        # varias distancias: en zonas angostas (burbuja y rocío casi juntas)
        # sólo la menor queda a ambos lados de la frontera
        for d in (0.003, 0.012):
            Ta, Pa = tm + d*nx*spT, math.exp(lpm + d*ny*spP)
            Tb, Pb = tm - d*nx*spT, math.exp(lpm - d*ny*spP)
            if min(Pa, Pb) < P_ini*0.5 or max(Pa, Pb) > P_TOPE*1.05:
                continue
            probado = True
            if ind(Ta, Pa)[0] != ind(Tb, Pb)[0]:
                separa = True; break
        if probado and not separa:
            malos += 1
    if malos:
        motivos.append(f"{malos} tramo(s) que no separan zonas estable/inestable")

    # ── b) isotermas: cruces verdaderos vs cruces de la envolvente ──────────
    Tlo, Thi = (min(Ts), max(Ts)) if T_rango is None else T_rango
    Ps = list(np.exp(np.linspace(math.log(P_ini), math.log(P_TOPE*0.98), n_P)))
    faltan = sobran = 0
    for k in range(n_iso):
        T = Tlo + (k + 0.5)/n_iso*(Thi - Tlo)
        verd = [p for p, _t in _cruces_isoterma(ind, T, Ps)]
        envc = _cruces_polilinea_T(env, T)
        tol = lambda p: max(0.04*p, 15.0)
        for p in verd:
            if not any(abs(p - q) < tol(p) for q in envc):
                faltan += 1
        for q in envc:
            if q < P_ini*1.2 or q > P_TOPE*0.95:
                continue
            if any(abs(q - p) < tol(q) for p in verd):
                continue
            # verificación local (zonas angostas que la malla no resuelve)
            if not any(ind(T, q*(1-f))[0] != ind(T, q*(1+f))[0]
                       for f in (0.003, 0.01, 0.03)):
                sobran += 1
    if faltan:
        motivos.append(f"{faltan} cruce(s) de la frontera ausentes en la envolvente")
    if sobran:
        motivos.append(f"{sobran} cruce(s) de la envolvente sin frontera real")
    return (not motivos), motivos


# ════════════════════════════════════════════════════════════════════════════
# 2) Reconstrucción por barrido
# ════════════════════════════════════════════════════════════════════════════
def _cadenas(pts, spT, spP, salto_max=0.09, inicio=None):
    """Encadena puntos (T, lnP, tipo) por vecino más cercano en el espacio
    normalizado, creciendo por ambos extremos.  Devuelve la lista de tramos."""
    rest = list(pts)
    tramos = []
    norm = lambda a, b: math.hypot((a[0]-b[0])/spT, (a[1]-b[1])/spP)
    while rest:
        i0 = inicio(rest) if inicio else 0
        cad = [rest.pop(i0)]
        for lado in (1, 0):
            while rest:
                ref = cad[-1] if lado else cad[0]
                j = min(range(len(rest)), key=lambda i: norm(rest[i], ref))
                if norm(rest[j], ref) > salto_max:
                    break
                if lado:
                    cad.append(rest.pop(j))
                else:
                    cad.insert(0, rest.pop(j))
        tramos.append(cad)
    return tramos


def _bisecar_segmento(ind, A, B, n=12):
    """Cruce estable↔inestable entre A=(T,lnP) y B=(T,lnP); None si no hay."""
    ia = ind(A[0], math.exp(A[1])); ib = ind(B[0], math.exp(B[1]))
    if ia[0] == ib[0]:
        return None
    for _ in range(n):
        M = (0.5*(A[0]+B[0]), 0.5*(A[1]+B[1]))
        im = ind(M[0], math.exp(M[1]))
        if im[0] == ia[0]:
            A, ia = M, im
        else:
            B, ib = M, im
    tipo = ia[1] if ia[0] else ib[1]
    return (0.5*(A[0]+B[0]), 0.5*(A[1]+B[1]), tipo)


SALTO_CADENA = 0.12
SALTO_UNION = 0.15


def reconstruir(z, kij, env_ref=None, P_ini=14.7, progress_cb=None):
    """Frontera bifásica por barrido de estabilidad.  Devuelve el mismo dict
    que construir_envolvente ({'envolvente', 'critico', 'sin_critico',
    'pared_ll'}) o None si no se halla frontera.

    Puntos de la frontera:
      · barrido global en isotermas e isobaras (encuentra ramas que la
        continuación no trazó);
      · verificación local de cada punto de la envolvente de referencia
        (bisección en la normal a la curva), que conserva con precisión las
        zonas angostas que una malla global no resuelve.
    Los puntos se separan por tipo (burbuja / rocío según la fase incipiente)
    y cada tipo se encadena por separado; el crítico es el encuentro de las
    dos ramas."""
    ind = _Indicador(z, kij)
    act = [i for i in range(E.NC) if z[i] > 1e-8]
    Tc = [E.TC[i] for i in act]
    T_lo = max(0.40*min(Tc), 100.0)
    T_hi = max(Tc)*1.05
    if env_ref:
        T_hi = max(T_hi, max(t for _, t in env_ref)*1.03)
    Ps_g = list(np.exp(np.linspace(math.log(P_ini), math.log(P_TOPE*0.98), 36)))
    Ts_g = list(np.linspace(T_lo, T_hi, 50))
    pts = []
    n_ok = 0
    for T in Ts_g:
        for P, tipo in _cruces_isoterma(ind, T, Ps_g):
            pts.append((T, math.log(P), tipo))
        n_ok += 1
        if progress_cb:
            progress_cb(n_ok)
    for P in Ps_g:
        for T, tipo in _cruces_isobara(ind, P, Ts_g):
            pts.append((T, math.log(P), tipo))
        n_ok += 1
        if progress_cb:
            progress_cb(n_ok)
    spT = max(T_hi - T_lo, 1.0); spP = math.log(P_TOPE/P_ini)
    # verificación local de la envolvente de referencia
    if env_ref and len(env_ref) >= 3:
        ref = [(t, math.log(max(p, 1e-6))) for p, t in env_ref]
        paso = max(1, len(ref)//110)
        for k in range(0, len(ref), paso):
            a = ref[max(k-1, 0)]; b = ref[min(k+1, len(ref)-1)]
            dx = (b[0]-a[0])/spT; dy = (b[1]-a[1])/spP
            L = math.hypot(dx, dy)
            if L < 1e-9:
                continue
            nx, ny = -dy/L, dx/L
            c = ref[k]
            for d in (0.006, 0.02):
                A = (c[0] + d*nx*spT, c[1] + d*ny*spP)
                B = (c[0] - d*nx*spT, c[1] - d*ny*spP)
                if min(A[1], B[1]) < math.log(P_ini*0.9) or max(A[1], B[1]) > math.log(P_TOPE):
                    break
                r = _bisecar_segmento(ind, A, B)
                if r is not None and r[2] is not None:
                    pts.append(r)
                    break
    pts = [p for p in pts if p[2] in ('B', 'D')]
    if len(pts) < 6:
        return None
    norm = lambda a, b: math.hypot((a[0]-b[0])/spT, (a[1]-b[1])/spP)
    # rocío: tramo que contiene la cricondentérmica
    D = [p for p in pts if p[2] == 'D']; Bp = [p for p in pts if p[2] == 'B']
    if not D:
        return None
    td = _cadenas(D, spT, spP, SALTO_CADENA)
    i_tmax = max(D, key=lambda p: p[0])
    rocio = next(t for t in td if i_tmax in t)
    # burbuja: tramo con un extremo más cerca de un extremo del rocío
    burb = None; crit = None; tb = []
    if Bp:
        tb = _cadenas(Bp, spT, spP, SALTO_CADENA)
        mejor = None
        for t in tb:
            if len(t) < 3:
                continue
            for eb in (t[0], t[-1]):
                for ed in (rocio[0], rocio[-1]):
                    d = norm(eb, ed)
                    if mejor is None or d < mejor[0]:
                        mejor = (d, t, eb, ed)
        if mejor is not None and mejor[0] < 0.08:
            _d, burb, eb, ed = mejor
            if burb[-1] is not eb:
                burb = list(reversed(burb))
            if rocio[0] is not ed:
                rocio = list(reversed(rocio))
            crit = (math.exp(0.5*(eb[1]+ed[1])), 0.5*(eb[0]+ed[0]))
    # unir tramos sueltos a los extremos libres (ramas fragmentadas por la
    # malla o por cambio de tipo de fase incipiente, p. ej. pared L-L)
    extremos = {id(rocio[0]), id(rocio[-1])}
    if burb is not None:
        extremos |= {id(burb[0]), id(burb[-1])}
    sueltos = [t for t in (td + tb) if len(t) >= 2
               and id(t[0]) not in extremos and id(t[-1]) not in extremos]
    def _extender(cad, al_final):
        while sueltos:
            e = cad[-1] if al_final else cad[0]
            mejor = None
            for t in sueltos:
                for k, et in ((0, t[0]), (1, t[-1])):
                    d = norm(e, et)
                    if mejor is None or d < mejor[0]:
                        mejor = (d, t, k)
            if mejor is None or mejor[0] > SALTO_UNION:
                break
            _d, t, k = mejor
            sueltos.remove(t)
            if al_final:
                cad = cad + (list(t) if k == 0 else list(reversed(t)))
            else:
                cad = (list(reversed(t)) if k == 0 else list(t)) + cad
        return cad
    if burb is not None:
        burb = _extender(burb, False)
        rocio = _extender(rocio, True)
    else:
        rocio = _extender(_extender(rocio, True), False)
    if burb is None:
        # sin crítico: el rocío va del extremo de mayor presión a la cola baja
        if rocio[0][1] < rocio[-1][1]:
            rocio = list(reversed(rocio))
        env = [(math.exp(lp), T) for T, lp, _t in rocio]
    else:
        env = ([(math.exp(lp), T) for T, lp, _t in burb] + [crit] +
               [(math.exp(lp), T) for T, lp, _t in rocio])
    if len(env) < 6:
        return None
    pared_ll = max(p for p, _ in env) > 0.9*P_TOPE
    return {'envolvente': env, 'critico': crit, 'sin_critico': crit is None,
            'pared_ll': pared_ll, 'reconstruida': True}


def puntaje(motivos):
    """Suma de defectos de una lista de motivos de auditar()."""
    n = 0
    for m in motivos:
        try:
            n += int(m.split()[0])
        except Exception:
            n += 5
    return n


def perdidas(z, kij, env_o, env_r, n_max=90, P_ini=14.7, detalle=False):
    """Fracción de puntos de env_o confirmados como frontera real (prueba
    local en la normal) que env_r NO reproduce.  Protege las zonas angostas
    (mezclas casi puras) que la malla de la reconstrucción no resuelve."""
    if not env_o or not env_r:
        return (0.0, []) if detalle else 0.0
    ind = _Indicador(z, kij)
    allT = [t for _, t in env_o] + [t for _, t in env_r]
    allP = [math.log(max(p, 1e-6)) for p, _ in env_o] + [math.log(max(p, 1e-6)) for p, _ in env_r]
    spT = max(max(allT) - min(allT), 1.0); spP = max(max(allP) - min(allP), 0.1)
    R = np.array([(t/spT, math.log(max(p, 1e-6))/spP) for p, t in env_r])
    A_, V_ = R[:-1], R[1:] - R[:-1]
    L2_ = np.maximum((V_**2).sum(1), 1e-18)
    def dist_r(x, y):
        q = np.array([x, y])
        u = np.clip(((q - A_)*V_).sum(1)/L2_, 0.0, 1.0)
        return float(np.min(np.hypot(*(q - A_ - u[:, None]*V_).T)))
    O = [(t, math.log(max(p, 1e-6))) for p, t in env_o]
    paso = max(1, len(O)//n_max)
    conf = perd = 0
    idx = []
    for k in range(1, len(O)-1, paso):
        a, c, b = O[k-1], O[k], O[k+1]
        borde = c[1] < math.log(2.0*P_ini)   # la malla no resuelve el borde
        dx = (b[0]-a[0])/spT; dy = (b[1]-a[1])/spP; L = math.hypot(dx, dy)
        if L < 1e-12:
            continue
        nx, ny = -dy/L, dx/L
        real = False
        for d in (0.001, 0.003):
            Ta, Pa = c[0] + d*nx*spT, math.exp(c[1] + d*ny*spP)
            Tb, Pb = c[0] - d*nx*spT, math.exp(c[1] - d*ny*spP)
            if min(Pa, Pb) < P_ini*0.5 or max(Pa, Pb) > P_TOPE*1.05:
                break
            if ind(Ta, Pa)[0] != ind(Tb, Pb)[0]:
                real = True; break
        if not real:
            continue
        if dist_r(c[0]/spT, c[1]/spP) > 0.03:
            idx.append(k)
            if not borde:
                perd += 1
        if not borde:
            conf += 1
    f = perd/conf if conf else 0.0
    return (f, idx) if detalle else f


def injertar_cola(env_o, env_r, idx):
    """Si los puntos perdidos forman la cola de un extremo de env_o (p. ej. la
    rama de burbuja de baja presión que sigue más allá del pie de la pared
    líquido-líquido), la injerta en env_r como excursión desde su punto más
    cercano.  Devuelve la envolvente nueva o None si no aplica."""
    if not idx:
        return None
    n = len(env_o)
    lo, hi = min(idx), max(idx)
    if hi - lo > 0.3*n:
        return None
    if lo <= 3:
        cola = list(env_o[:hi+2])            # extremo inicial: cola[-1] es interno
    elif hi >= n - 4:
        cola = list(reversed(env_o[lo-1:]))  # extremo final, orientado igual
    else:
        return None
    pin = cola[-1]
    allT = [t for _, t in env_o]; allP = [math.log(max(p, 1e-6)) for p, _ in env_o]
    spT = max(max(allT)-min(allT), 1.0); spP = max(max(allP)-min(allP), 0.1)
    d = [math.hypot((t-pin[1])/spT, (math.log(p)-math.log(pin[0]))/spP) for p, t in env_r]
    m = int(np.argmin(d))
    if d[m] > 0.05:
        return None
    ida = list(reversed(cola[:-1]))          # desde el punto de unión hacia afuera
    if m == 0:
        return list(reversed(ida)) + list(env_r)
    if m == len(env_r) - 1:
        return list(env_r) + ida
    return list(env_r[:m+1]) + ida + list(reversed(ida[:-1])) + list(env_r[m:])


# ════════════════════════════════════════════════════════════════════════════
# 3) Relleno de cuerdas: tramos rectos largos que sustituyen una rama real
# ════════════════════════════════════════════════════════════════════════════
CUERDA_MIN = 0.12     # salto normalizado (en T o en lnP) que se revisa


def _dist_polilinea(Q, Pl, excluir=None):
    """Distancias normalizadas de los puntos Q (m×2) a la polilínea Pl (n×2),
    sin el segmento de índice 'excluir'."""
    A = Pl[:-1]; B = Pl[1:]
    if excluir is not None:
        m = np.ones(len(A), bool); m[excluir] = False
        A = A[m]; B = B[m]
    if len(A) == 0:
        return np.full(len(Q), np.inf)
    V = B - A; VV = np.einsum('ij,ij->i', V, V) + 1e-30
    W = Q[:, None, :] - A[None, :, :]
    u = np.clip(np.einsum('mij,ij->mi', W, V)/VV, 0, 1)
    D = W - u[..., None]*V[None, :, :]
    return np.sqrt(np.einsum('mij,mij->mi', D, D)).min(axis=1)


def rellenar_cuerdas(z, kij, env, crit=None, P_ini=14.7, n_lin=22, n_fino=44):
    """Busca tramos rectos largos de la envolvente que no siguen la frontera
    real (p. ej. una recta del crítico a un quiebre, en lugar de la rama que
    los une).  En la caja de cada tramo se hace un barrido fino de estabilidad
    en isotermas e isobaras; los cruces que no están ya sobre el resto de la
    curva forman la rama faltante, que reemplaza a la recta si une sus dos
    extremos.  Devuelve (env_nueva, n_tramos_rellenados)."""
    if not env or len(env) < 4:
        return env, 0
    Ts = [t for _, t in env]; lP = [math.log(max(p, 1e-6)) for p, _ in env]
    spT = max(max(Ts) - min(Ts), 1.0); spP = max(max(lP) - min(lP), 0.1)
    largos = [i for i in range(1, len(env))
              if max(abs(Ts[i]-Ts[i-1])/spT, abs(lP[i]-lP[i-1])/spP) > CUERDA_MIN]
    if not largos:
        return env, 0
    ind = _Indicador(z, kij)
    Pl = np.array([[t/spT, lp/spP] for t, lp in zip(Ts, lP)])
    reemplazos = {}
    for i in largos:
        a = (Ts[i-1], lP[i-1]); b = (Ts[i], lP[i])
        mT = 0.15*abs(b[0]-a[0]) + 0.01*spT; mP = 0.15*abs(b[1]-a[1]) + 0.01*spP
        T0, T1 = min(a[0], b[0]) - mT, max(a[0], b[0]) + mT
        L0 = max(min(a[1], b[1]) - mP, math.log(P_ini*0.9))
        L1 = min(max(a[1], b[1]) + mP, math.log(P_TOPE))
        Ps = list(np.exp(np.linspace(L0, L1, n_fino)))
        Tg = list(np.linspace(T0, T1, n_fino))
        pts = []
        for T in np.linspace(T0, T1, n_lin):
            pts += [(T, math.log(P)) for P, _t in _cruces_isoterma(ind, T, Ps)]
        for P in np.exp(np.linspace(L0, L1, n_lin)):
            pts += [(T, math.log(P)) for T, _t in _cruces_isobara(ind, P, Tg)]
        cad = _cadena_rama(pts, Pl, i, a, b, spT, spP)
        if cad is None:
            # rama no separable por barrido (p. ej. tramo largo casi recto):
            # se sigue la frontera de a hacia b (densificación)
            cad = _marchar(ind, a, b, spT, spP)
        if cad:
            reemplazos[i] = [(math.exp(lp), T) for T, lp in cad]
    if not reemplazos:
        return env, 0
    # colas metaestables: la continuación puede seguir una rama más allá de su
    # cruce con otra (cola de golondrina); esos puntos quedan DENTRO de la
    # región bifásica.  Se recortan a partir de los extremos de cada cuerda.
    # También se quitan los puntos que repiten un tramo ya presente en otra
    # parte de la curva (la continuación volvió sobre una rama ya trazada).
    quitar = set()
    for i in reemplazos:
        cadN = np.array([[t/spT, math.log(p)/spP] for p, t in reemplazos[i]])
        def _sobra(j, paso):
            if _interior(ind, env, j, spT, spP, paso):
                return True
            m = np.ones(len(Pl), bool); m[max(0, j-6):j+7] = False
            otros = Pl[m]
            if len(otros) >= 2 and _dist_polilinea(Pl[j][None, :], otros)[0] < 0.006:
                # duplicado sólo si lo cubre un tramo continuo (no un salto)
                return True
            if len(cadN) >= 2 and _dist_polilinea(Pl[j][None, :], cadN)[0] < 0.006:
                return True
            return False
        for j0, paso in ((i, 1), (i - 1, -1)):
            j = j0; n = 0; fallos = 0
            while 0 <= j <= len(env) - 1 and n < 60:
                if _sobra(j, paso if 0 <= j + paso < len(env) else -paso):
                    quitar.add(j); fallos = 0
                else:
                    # el extremo de la cuerda puede estar sobre la frontera
                    # aunque los siguientes sobren: se tolera un punto
                    fallos += 1
                    if fallos > 1 or n > 0:
                        break
                j += paso; n += 1
            # si el último revisado no sobraba, no se quita lo que lo precede
            # salvo lo ya marcado como sobrante
    out = [env[0]]
    for i in range(1, len(env)):
        if i in reemplazos:
            out += reemplazos[i]
        if i not in quitar:
            out.append(env[i])
    return out, len(reemplazos)


def _interior(ind, env, j, spT, spP, paso=0):
    """True si el punto j de la envolvente está dentro de la región bifásica
    (inestable a ambos lados de la curva, en dos distancias pequeñas).
    paso=±1: tangente unilateral hacia ese lado (junto a una cuerda)."""
    if paso:
        if not 0 <= j + paso < len(env):
            paso = -paso
        (p0, t0), (p1, t1) = env[j], env[j+paso]
    elif j == 0 or j == len(env) - 1:
        return False
    else:
        (p0, t0), (p1, t1) = env[j-1], env[j+1]
    dx = (t1 - t0)/spT; dy = (math.log(p1) - math.log(p0))/spP
    L = math.hypot(dx, dy)
    if L < 1e-12:
        return False
    nx, ny = -dy/L, dx/L
    p, t = env[j]; lp = math.log(p)
    for d in (0.002, 0.006):
        for sg in (1, -1):
            if not ind(t + sg*d*nx*spT, math.exp(lp + sg*d*ny*spP))[0]:
                return False
    return True


# ════════════════════════════════════════════════════════════════════════════
# 4) Lazos (cola de golondrina): la curva se cruza a sí misma
# ════════════════════════════════════════════════════════════════════════════
def _cruce_segmentos(P, i, j):
    """Intersección de los segmentos P[i]-P[i+1] y P[j]-P[j+1] (o None)."""
    a, b, c, d = P[i], P[i+1], P[j], P[j+1]
    r = b - a; s = d - c
    den = r[0]*s[1] - r[1]*s[0]
    if abs(den) < 1e-18:
        return None
    q = c - a
    u = (q[0]*s[1] - q[1]*s[0])/den
    v = (q[0]*r[1] - q[1]*r[0])/den
    if 0.0 < u < 1.0 and 0.0 < v < 1.0:
        return a + u*r
    return None


def recortar_lazos(z, kij, env, max_frac=0.35):
    """Quita los lazos que la continuación deja cuando sigue una rama más allá
    de su cruce con otra (cola de golondrina: puntos metaestables, DENTRO de la
    región bifásica).  El lazo se reemplaza por el punto de cruce; sólo se
    quita si sus puntos están dentro de la región bifásica según la prueba de
    estabilidad.  Devuelve (env_nueva, n_lazos)."""
    n = len(env)
    if n < 8:
        return env, 0
    Ts = [t for _, t in env]; lP = [math.log(max(p, 1e-6)) for p, _ in env]
    spT = max(max(Ts) - min(Ts), 1.0); spP = max(max(lP) - min(lP), 0.1)
    P = np.array([[t/spT, lp/spP] for t, lp in zip(Ts, lP)])
    A = P[:-1]; B = P[1:]
    lo = np.minimum(A, B); hi = np.maximum(A, B)
    ind = None
    lazos = []
    i = 0
    max_l = max(6, int(max_frac*n))
    while i < n - 3:
        js = np.nonzero((lo[i+2:, 0] <= hi[i, 0]) & (hi[i+2:, 0] >= lo[i, 0]) &
                        (lo[i+2:, 1] <= hi[i, 1]) & (hi[i+2:, 1] >= lo[i, 1]))[0] + i + 2
        hecho = False
        for j in js:
            if j - i > max_l:
                break
            X = _cruce_segmentos(P, i, j)
            if X is None:
                continue
            if ind is None:
                ind = _Indicador(z, kij)
            idx = list(range(i + 1, j + 1))
            muestra = idx[::max(1, len(idx)//5)][:6]
            dentro = sum(_interior(ind, env, k, spT, spP) for k in muestra
                         if 0 < k < n - 1)
            if dentro*2 > len(muestra):
                lazos.append((i, j, (math.exp(X[1]*spP), X[0]*spT)))
                i = j; hecho = True
                break
        i += 1 if not hecho else 0
        if hecho:
            i += 1
    if not lazos:
        return env, 0
    out = []; k = 0
    for i, j, X in lazos:
        out += env[k:i+1]; out.append(X); k = j + 1
    out += env[k:]
    return out, len(lazos)



# ════════════════════════════════════════════════════════════════════════════
# 5) Extremos sueltos: la curva termina a media presión
# ════════════════════════════════════════════════════════════════════════════
def prolongar_extremos(z, kij, env, P_ini=14.7, h=0.02, max_pasos=400):
    """Una envolvente debe terminar en la presión inicial (cola baja) o en el
    tope de presión.  Si un extremo queda a presión intermedia, la rama se
    abandonó: se continúa siguiendo la frontera de estabilidad (predictor en
    la dirección de avance, corrector por bisección en la normal) hasta P_ini,
    el tope, o hasta unirse al resto de la curva.  Devuelve (env, n_prolong)."""
    if not env or len(env) < 6:
        return env, 0
    Ts = [t for _, t in env]; lP = [math.log(max(p, 1e-6)) for p, _ in env]
    spT = max(max(Ts) - min(Ts), 1.0); spP = max(max(lP) - min(lP), 0.1)
    lo_P = math.log(P_ini); hi_P = math.log(P_TOPE*0.98)
    T_min = min(Ts) - 0.5*spT; T_max = max(Ts) + 0.5*spT
    ind = None
    n_ext = 0
    for lado in (1, 0):
        pts = [(t, lp) for t, lp in zip(Ts, lP)]
        if not lado:
            pts = pts[::-1]
        E0 = pts[-1]
        if E0[1] < lo_P + 0.4 or E0[1] > hi_P - 0.05:
            continue                                     # extremo legítimo
        if ind is None:
            ind = _Indicador(z, kij)
        N = np.array([[t/spT, l/spP] for t, l in pts])
        ref = N[:-6] if len(N) > 8 else N[:0]
        cur = np.array([E0[0]/spT, E0[1]/spP])
        k0 = max(0, len(N) - 4)
        d0 = cur - N[k0]
        nd = np.linalg.norm(d0)
        if nd < 1e-12:
            continue
        dirv = d0/nd
        nuevos = []
        for paso in range(max_pasos):
            hallado = None
            angs = (0, 20, -20, 45, -45, 70, -70, 100, -100) if paso == 0 else (0, 15, -15, 35, -35)
            for hh in (h, h/2, h/4):
                for a in angs:
                    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                    dv = np.array([ca*dirv[0] - sa*dirv[1], sa*dirv[0] + ca*dirv[1]])
                    X = cur + hh*dv
                    nv = np.array([-dv[1], dv[0]])
                    for dd in (0.6*hh, 1.5*hh):
                        A_ = X + dd*nv; B_ = X - dd*nv
                        r = _bisecar_segmento(ind, (A_[0]*spT, A_[1]*spP),
                                              (B_[0]*spT, B_[1]*spP), n=14)
                        if r is None:
                            continue
                        Y = np.array([r[0]/spT, r[1]/spP])
                        dy = Y - cur; L = np.linalg.norm(dy)
                        if L < 0.2*hh or np.dot(dy, dirv) < 0.2*L:
                            continue                     # no avanza
                        hallado = Y; break
                    if hallado is not None:
                        break
                if hallado is not None:
                    break
            if hallado is None:
                break
            dirv = (hallado - cur)/np.linalg.norm(hallado - cur)
            cur = hallado
            nuevos.append((cur[0]*spT, cur[1]*spP))
            if cur[1]*spP < lo_P or cur[1]*spP > hi_P or not (T_min < cur[0]*spT < T_max):
                break
            if len(ref) and paso > 2 and _dist_polilinea(cur[None, :], ref)[0] < 0.006:
                break                                    # se unió a la curva
        if len(nuevos) >= 3:
            n_ext += 1
            # el último punto se lleva exactamente al límite de presión que
            # cruzó (interpolando en el último tramo, sin deformar la curva)
            if len(nuevos) >= 2:
                (t0, l0), (t1, l1) = nuevos[-2], nuevos[-1]
                for lim in (lo_P, hi_P):
                    if (l1 - lim)*(l0 - lim) < 0:
                        f = (lim - l0)/(l1 - l0)
                        nuevos[-1] = (t0 + f*(t1 - t0), lim)
            ext = [(math.exp(min(max(l, lo_P), hi_P)), t) for t, l in nuevos]
            if lado:
                env = list(env) + ext
            else:
                env = ext[::-1] + list(env)
            Ts = [t for _, t in env]; lP = [math.log(max(p, 1e-6)) for p, _ in env]
    return env, n_ext


def _cadena_rama(pts, Pl, i, a, b, spT, spP):
    """Cruces del barrido local que no están sobre el resto de la curva,
    encadenados de a hacia b; None si no forman una rama que una ambos
    extremos o si la rama coincide con la recta."""
    if len(pts) < 4:
        return None
    Q = np.array([[t/spT, lp/spP] for t, lp in pts])
    d = _dist_polilinea(Q, Pl, excluir=i-1)
    nuevos = [p for p, dd in zip(pts, d) if dd > 0.004]
    if len(nuevos) < 4:
        return None
    norm = lambda u, v: math.hypot((u[0]-v[0])/spT, (u[1]-v[1])/spP)
    rest = list(nuevos); cad = [a]
    while rest:
        j = min(range(len(rest)), key=lambda k: norm(rest[k], cad[-1]))
        # junto al crítico ambas ramas convergen y sus cruces se confunden
        # con la curva: el primer enlace admite un salto mayor
        if norm(rest[j], cad[-1]) > (0.20 if len(cad) == 1 else 0.10):
            break
        cad.append(rest.pop(j))
    cad = cad[1:]
    if len(cad) < 4 or norm(cad[-1], b) > 0.15:
        return None
    Cq = np.array([[t/spT, lp/spP] for t, lp in cad])
    S2 = np.array([[a[0]/spT, a[1]/spP], [b[0]/spT, b[1]/spP]])
    if _dist_polilinea(Cq, S2).max() < 0.01:
        return None
    return cad


def _marchar(ind, a, b, spT, spP, h=0.02, max_pasos=200):
    """Sigue la frontera de estabilidad desde a hasta b (predictor hacia b,
    corrector por bisección en la normal).  Devuelve los puntos interiores
    (T, lnP) o None si se pierde la frontera."""
    A = np.array([a[0]/spT, a[1]/spP]); B = np.array([b[0]/spT, b[1]/spP])
    cur = A.copy()
    L0 = np.linalg.norm(B - A)
    if L0 < 2*h:
        return None
    dirv = (B - A)/L0
    out = []
    for _ in range(max_pasos):
        resto = B - cur
        dr = np.linalg.norm(resto)
        if dr < 1.5*h:
            return [(x*spT, y*spP) for x, y in out] or None
        objetivo = resto/dr
        dv = dirv + objetivo
        dv /= np.linalg.norm(dv)
        hallado = None
        for hh in (h, h/2, h/4):
            X = cur + hh*dv
            nv = np.array([-dv[1], dv[0]])
            for dd in (0.5*hh, 1.5*hh):
                P1 = X + dd*nv; P2 = X - dd*nv
                r = _bisecar_segmento(ind, (P1[0]*spT, P1[1]*spP),
                                      (P2[0]*spT, P2[1]*spP), n=14)
                if r is None:
                    continue
                Y = np.array([r[0]/spT, r[1]/spP])
                if np.dot(Y - cur, objetivo) <= 0.2*np.linalg.norm(Y - cur):
                    continue
                hallado = Y; break
            if hallado is not None:
                break
        if hallado is None:
            return None
        dirv = (hallado - cur)/np.linalg.norm(hallado - cur)
        cur = hallado
        out.append((cur[0], cur[1]))
    return None

"""
op_unitarias.py — Motor de las operaciones unitarias (estilo PVTsim).

Operaciones: compresor (clásico o PACE), expansor, enfriador, calentador,
bomba, válvula y separador de una etapa.  Todas se resuelven con los flashes
PT, PH y PS del programa (mismo motor que Equilibrio de fases), sobre la
corriente completa (con agua, flash trifásico).

Unidades internas: T [°R], P [psia], H [BTU/lbmol], S [BTU/(lbmol·°R)],
V [ft³/lbmol], densidad [lb/ft³], flujo molar [lbmol/h], potencia [BTU/h].
"""
import math
import numpy as np

from eos import NC

# Constantes de conversión
BTU_FT_LBF = 778.169262       # ft·lbf por BTU
PSI_FT3_BTU = 144.0 / BTU_FT_LBF   # psia·ft³ → BTU
BTUH_HP = 2544.4336           # BTU/h por hp
BTUH_KW = 3412.1416           # BTU/h por kW
SCF_LBMOL = 379.482           # scf/lbmol a 60 °F y 14.696 psia
N_PACE = 50                   # tramos de presión de la trayectoria PACE (como PVTsim)

OPERACIONES = ['compresor', 'expansor', 'enfriador', 'calentador',
               'bomba', 'valvula', 'separador']
NOMBRES = {'compresor': "Compresor", 'expansor': "Expansor",
           'enfriador': "Enfriador", 'calentador': "Calentador",
           'bomba': "Bomba", 'valvula': "Válvula", 'separador': "Separador"}


class SinSolucionOU(ValueError):
    """Las especificaciones no tienen solución (se muestra como advertencia)."""


# ── Estado de una corriente ─────────────────────────────────────────────
def estado(z, T, P, ctx):
    """Flash PT de la corriente y sus propiedades por fase.

    ctx = dict(kij, eos, metodo, agua).  Devuelve un dict con T, P, H, S, PM,
    rho, V (volumen molar de la mezcla) y 'fases': {'V'|'L'|'W': {beta,
    beta_m, comp(14), PM, rho, Z, H, S, mu}}."""
    import eos as eng
    from pestana_propiedades import _rho_mezcla
    kij, eos_c, met, agua = ctx['kij'], ctx['eos'], ctx['metodo'], ctx['agua']
    eng.set_eos(eos_c)
    T = float(T); P = float(P)
    fases = {}
    if not agua:
        z13 = list(z[:NC]); s = sum(z13); z13 = [v/s for v in z13]
        r = eng.calcular(z13, T, P, kij=kij, metodo_densidad=met)
        import entalpia_entropia_gen as hs
        h = hs.calcular_HS(z13, T, P, r, eos=eos_c, kij=kij)
        V = float(r.get('V') or 0.0); L = 1.0 - V
        Vm = float(r.get('Vm') if r.get('Vm') is not None else V)
        if V > 1e-10:
            fases['V'] = dict(beta=V, beta_m=Vm, comp=list(r['y']) + [0.0],
                              PM=r.get('PM_v'), rho=r.get('rho_v'), Z=r.get('ZV'),
                              H=h.get('H_vapor'), S=h.get('S_vapor'), mu=r.get('mu_v'))
        if L > 1e-10:
            fases['L'] = dict(beta=L, beta_m=1.0 - Vm, comp=list(r['x']) + [0.0],
                              PM=r.get('PM_l'), rho=r.get('rho_l'), Z=r.get('ZL'),
                              H=h.get('H_liquido'), S=h.get('S_liquido'), mu=r.get('mu_l'))
        # fase única: x / y pueden venir vacíos → composición global
        for f in fases.values():
            if not f['comp'] or len(f['comp']) < NC:
                f['comp'] = z13 + [0.0]
        H = h.get('H_stream'); S = h.get('S_stream')
        PM = r.get('PM_z') or sum(f['beta']*(f['PM'] or 0) for f in fases.values())
        rho = _rho_mezcla(r)
        zc = z13 + [0.0]
    else:
        import flash_agua as fa
        import propiedades_agua as pa
        z14 = np.asarray(z[:NC + 1], dtype=float); z14 = z14/z14.sum()
        rt = fa.flash_trifasico(z14, T, P, eos=eos_c, metodo='hv')
        rt = fa.identificar_fases_hc(rt, T, P, eos_c, kij)
        md = met if met in ('COSTALD', 'EOS', 'Peneloux') else 'EOS'
        pr = pa.propiedades_fases(rt, T, P, eos_c, metodo_densidad=md)
        comp = {'V': rt.get('y'), 'L': rt.get('x'), 'W': rt.get('w')}
        H = S = 0.0; PM = 0.0; inv = 0.0; ok = True
        for k in ('V', 'L', 'W'):
            b = float(rt.get('beta_' + k, 0.0) or 0.0)
            q = pr.get(k) or {}
            if b <= 1e-12 or not q:
                continue
            fases[k] = dict(beta=b, comp=[float(v) for v in comp[k]],
                            PM=q.get('PM'), rho=q.get('rho'), Z=q.get('Z'),
                            H=q.get('H'), S=q.get('S'), mu=q.get('mu'))
            PM += b*(q.get('PM') or 0.0)
            if q.get('rho') and q.get('PM'):
                inv += b*q['PM']/q['rho']
            if q.get('H') is None or q.get('S') is None:
                ok = False
            else:
                H += b*q['H']; S += b*q['S']
        if not ok:
            H = S = None
        rho = (PM/inv) if inv > 0 else None
        for f in fases.values():
            f['beta_m'] = f['beta']*(f['PM'] or 0.0)/PM if PM > 0 else None
        zc = [float(v) for v in z14]
    if H is None or S is None:
        raise ValueError("No se pudo calcular la entalpía/entropía de la corriente.")
    Vmol = (PM/rho) if rho else None
    return dict(T=T, P=P, H=float(H), S=float(S), PM=float(PM),
                rho=(float(rho) if rho else None), V=Vmol, z=zc, fases=fases)


def n_fases(e):
    return len([f for f in e['fases'].values() if f['beta'] > 1e-8])


# ── Flashes PH / PS sobre la corriente ─────────────────────────────────
def _T_de_H(z, P, H, ctx, T0):
    import flash_ph as fph
    return fph.flash_ph(list(z), P, H, ctx['kij'], ctx['eos'], ctx['metodo'],
                        ctx['agua'], T0=T0)


def _T_de_S(z, P, S, ctx, T0):
    import flash_ph as fph
    return fph.flash_ps(list(z), P, S, ctx['kij'], ctx['eos'], ctx['metodo'],
                        ctx['agua'], T0=T0)


# ── Funciones X e Y de Schultz ─────────────────────────────────────────
def _schultz(z, T, P, V, ctx, e=None):
    """Funciones de Schultz X = (T/V)(∂V/∂T)_P − 1 e Y = −(P/V)(∂V/∂P)_T,
    con derivadas exactas (diferencias centrales con paso muy pequeño).  Con
    una sola fase de hidrocarburo se deriva el volumen de la ecuación de
    estado (con el traslado de Peneloux si está activo); con varias fases,
    el volumen total del flash."""
    if e is not None and not ctx['agua'] and len(e['fases']) == 1:
        try:
            import entalpia_entropia_gen as hs
            import eos as eng
            tipo = 'V' if 'V' in e['fases'] else 'L'
            z13 = list(e['z'][:NC])
            pen = ctx['metodo'] == 'Peneloux'
            def Vf(T_, P_):
                v = hs._pick_Z(z13, T_, P_, tipo, ctx['eos'], ctx['kij'])*eng.R_GAS*T_/P_
                return eng.V_liq_peneloux(z13, v, ctx['eos']) if pen else v
            dT = 1e-5*T; dP = 1e-5*P
            V0 = Vf(T, P)
            dVdT = (Vf(T + dT, P) - Vf(T - dT, P))/(2*dT)
            dVdP = (Vf(T, P + dP) - Vf(T, P - dP))/(2*dP)
            return (T/V0)*dVdT - 1.0, -(P/V0)*dVdP
        except Exception:
            pass
    try:
        dT = 1e-4*T; dP = 1e-4*P
        dVdT = (estado(z, T + dT, P, ctx)['V'] - estado(z, T - dT, P, ctx)['V'])/(2*dT)
        dVdP = (estado(z, T, P + dP, ctx)['V'] - estado(z, T, P - dP, ctx)['V'])/(2*dP)
        return (T/V)*dVdT - 1.0, -(P/V)*dVdP
    except Exception:
        return None, None


# ── Operaciones ─────────────────────────────────────────────────────────
def _base(op, z, ctx, n, T1, P1):
    e1 = estado(z, T1, P1, ctx)
    return dict(op=op, n=float(n), entrada=e1, salida=None, datos={}, avisos=[],
                ctx_eos=ctx['eos'])


def _aviso_fases(res, que):
    """Advertencia de PVTsim si se forma más de una fase en la entrada o en la
    salida del compresor, expansor o bomba."""
    if n_fases(res['entrada']) > 1:
        res['avisos'].append("La mezcla forma más de una fase en la entrada.")
    if res['salida'] is not None and n_fases(res['salida']) > 1:
        res['avisos'].append("La mezcla forma más de una fase en la salida.")


def compresor_clasico(z, ctx, n, T1, P1, P2, eta):
    if P2 <= P1:
        raise SinSolucionOU("La presión de salida del compresor debe ser mayor que la de entrada.")
    res = _base('compresor', z, ctx, n, T1, P1)
    e1 = res['entrada']
    T2s = _T_de_S(z, P2, e1['S'], ctx, T1*(P2/P1)**0.25)
    e2s = estado(z, T2s, P2, ctx)
    dHs = e2s['H'] - e1['H']
    dH = dHs/eta
    T2 = _T_de_H(z, P2, e1['H'] + dH, ctx, T2s)
    e2 = estado(z, T2, P2, ctx)
    res['salida'] = e2
    res['datos'] = dict(metodo='clasico', eta=eta, T2s=T2s, dHs=dHs, dH=e2['H'] - e1['H'],
                        trabajo=n*(e2['H'] - e1['H']), relacion=P2/P1)
    _aviso_fases(res, "compresor")
    return res


def _pace(z, ctx, e1, P2, eta, n_tramos=N_PACE, con_xy=True, progreso=None):
    """Trayectoria de eficiencia constante (PACE): n tramos isentrópicos de
    ΔP corregidos por η.  Devuelve (estado de salida, lista de puntos)."""
    dP = (P2 - e1['P'])/n_tramos
    e = e1; pts = [e1]
    xs, ys = [], []        # X e Y al final de cada tramo (como PVTsim)
    for k in range(1, n_tramos + 1):
        Pk = e1['P'] + dP*k if k < n_tramos else P2
        Tks = _T_de_S(z, Pk, e['S'], ctx, e['T'])
        Hks = estado(z, Tks, Pk, ctx)['H']
        Hk = e['H'] + (Hks - e['H'])/eta
        Tk = _T_de_H(z, Pk, Hk, ctx, Tks)
        e = estado(z, Tk, Pk, ctx)
        pts.append(e)
        if con_xy and e['V']:
            X, Y = _schultz(z, e['T'], e['P'], e['V'], ctx, e)
            if X is not None:
                xs.append(X); ys.append(Y)
        if progreso:
            progreso()
    return e, pts, xs, ys


def _head(res):
    """HEAD = trabajo/(caudal másico·g) → ft (con g = gc): ΔH[BTU/lb]·778.17."""
    e1 = res['entrada']; e2 = res['salida']
    dH_lb = (e2['H'] - e1['H'])/e1['PM']
    return dH_lb*BTU_FT_LBF


def compresor_pace(z, ctx, n, T1, P1, spec, eta=1.0, P2=None, T2=None,
                   trabajo=None, head=None, progreso=None):
    """spec: 'P_eta' (P2, η), 'W_eta' (trabajo [BTU/h], η), 'H_eta' (head
    [ft], η) o 'P_T' (P2, T2 → η)."""
    import flash_ph as fph
    res = _base('compresor', z, ctx, n, T1, P1)
    e1 = res['entrada']

    cache = {}

    def correr(P2_, eta_, xy=False, n_t=N_PACE):
        clave = (P2_, eta_, n_t)
        if not xy and clave in cache:
            return cache[clave]
        r = _pace(z, ctx, e1, P2_, eta_, n_tramos=n_t, con_xy=xy,
                  progreso=progreso)
        if n_t == N_PACE:
            cache.clear()
        cache[clave] = r
        return r

    def secante(g, x0, x1, tol, lo, hi, nmax=12, f0=None, pend=None):
        """Secante; con `pend` el primer paso usa esa pendiente (la de la
        trayectoria gruesa) y basta una evaluación inicial."""
        f0 = g(x0) if f0 is None else f0
        if pend:
            x1 = min(max(x0 - f0/pend, lo), hi)
        f1 = g(x1)
        for _ in range(nmax):
            if abs(f1) < tol:
                return x1, (f1 - f0)/(x1 - x0) if x1 != x0 else pend
            if f1 == f0:
                break
            x2 = min(max(x1 - f1*(x1 - x0)/(f1 - f0), lo), hi)
            x0, f0, x1, f1 = x1, f1, x2, g(x2)
        if abs(f1) < 100*tol:
            return x1, pend
        raise SinSolucionOU("No se encontró solución para las especificaciones del compresor.")

    def resolver(g_full, g_grueso, x0, x1, lo, hi):
        """Raíz con una trayectoria gruesa de pocos tramos y luego afinada
        con la trayectoria completa (con la pendiente de la gruesa)."""
        xg, pend = secante(g_grueso, x0, x1, 1e-4, lo, hi)
        return secante(g_full, xg, None, 1e-8, lo, hi, pend=pend)[0]

    if spec == 'P_eta':
        if P2 <= P1:
            raise SinSolucionOU("La presión de salida del compresor debe ser mayor que la de entrada.")
    elif spec in ('W_eta', 'H_eta'):
        objetivo = trabajo if spec == 'W_eta' else head
        if objetivo is None or objetivo <= 0:
            raise SinSolucionOU("El trabajo o el head del compresor debe ser mayor que cero.")
        def g(lnP, n_t=N_PACE):
            e2, _p, _x, _y = correr(math.exp(lnP), eta, n_t=n_t)
            r = dict(entrada=e1, salida=e2)
            val = n*(e2['H'] - e1['H']) if spec == 'W_eta' else _head(r)
            return val/objetivo - 1.0
        gg = lambda x: g(x, 5)
        lo, hi = math.log(P1*1.0001), math.log(fph.P_MAX_PSIA)
        P2 = math.exp(resolver(g, gg, math.log(P1*1.5), math.log(P1*2.5), lo, hi))
    elif spec == 'P_T':
        if P2 <= P1:
            raise SinSolucionOU("La presión de salida del compresor debe ser mayor que la de entrada.")
        def g(eta_, n_t=N_PACE):
            e2, _p, _x, _y = correr(P2, eta_, n_t=n_t)
            return (e2['T'] - T2)/T2
        gg = lambda x: g(x, 5)
        eta = resolver(g, gg, 0.8, 0.7, 0.05, 1.0)
    if (P2, eta, N_PACE) in cache:
        # la última trayectoria completa ya es la solución: solo X e Y
        e2, pts, _x, _y = cache[(P2, eta, N_PACE)]
        xs, ys = [], []
        for p in pts[1:]:
            if p['V']:
                X, Y = _schultz(z, p['T'], p['P'], p['V'], ctx, p)
                if X is not None:
                    xs.append(X); ys.append(Y)
    else:
        e2, pts, xs, ys = correr(P2, eta, xy=True)
    res['salida'] = e2
    # Referencia isentrópica en un solo paso (para comparar)
    try:
        T2s = _T_de_S(z, P2, e1['S'], ctx, e1['T'])
        dHs = estado(z, T2s, P2, ctx)['H'] - e1['H']
    except Exception:
        T2s = dHs = None
    res['datos'] = dict(metodo='pace', eta=eta, T2s=T2s, dHs=dHs,
                        dH=e2['H'] - e1['H'], trabajo=n*(e2['H'] - e1['H']),
                        relacion=P2/P1, head=_head(res),
                        Xmin=min(xs) if xs else None, Xmax=max(xs) if xs else None,
                        Ymin=min(ys) if ys else None, Ymax=max(ys) if ys else None,
                        trayectoria=[(p['P'], p['T'], p['H'], p['S']) for p in pts])
    _aviso_fases(res, "compresor")
    return res


def expansor(z, ctx, n, T1, P1, P2, eta=1.0):
    if P2 >= P1:
        raise SinSolucionOU("La presión de salida del expansor debe ser menor que la de entrada.")
    res = _base('expansor', z, ctx, n, T1, P1)
    e1 = res['entrada']
    T2s = _T_de_S(z, P2, e1['S'], ctx, T1*(P2/P1)**0.25)
    dHs = estado(z, T2s, P2, ctx)['H'] - e1['H']       # < 0
    T2 = _T_de_H(z, P2, e1['H'] + eta*dHs, ctx, T2s)
    e2 = estado(z, T2, P2, ctx)
    res['salida'] = e2
    res['datos'] = dict(eta=eta, T2s=T2s, dHs=dHs, dH=e2['H'] - e1['H'],
                        trabajo=n*(e1['H'] - e2['H']), relacion=P1/P2)
    _aviso_fases(res, "expansor")
    return res


def intercambiador(op, z, ctx, n, T1, P1, T2, dP=0.0):
    """Enfriador o calentador: T de salida y caída de presión.  Capacidad =
    calor transferido al fluido por unidad de tiempo (negativa al enfriar)."""
    P2 = P1 - dP
    if P2 <= 0:
        raise SinSolucionOU("La caída de presión es mayor que la presión de entrada.")
    if op == 'enfriador' and T2 > T1:
        raise SinSolucionOU("En un enfriador la temperatura de salida debe ser menor que la de entrada.")
    if op == 'calentador' and T2 < T1:
        raise SinSolucionOU("En un calentador la temperatura de salida debe ser mayor que la de entrada.")
    res = _base(op, z, ctx, n, T1, P1)
    e1 = res['entrada']
    e2 = estado(z, T2, P2, ctx)
    res['salida'] = e2
    res['datos'] = dict(dH=e2['H'] - e1['H'], calor=n*(e2['H'] - e1['H']), dP=dP)
    return res


def bomba(z, ctx, n, T1, P1, P2, eta=1.0):
    """Bomba como en PVTsim: η = V̄·ΔP/ΔH, donde el «volumen medio bombeado»
    V̄ es el volumen molar de la corriente a la temperatura de ENTRADA y a la
    presión media (P1 + P2)/2.  Entonces ΔH = V̄·ΔP/η y un flash PH da la
    temperatura de salida.  (Verificado contra PVTsim en líquido y con
    cambio de fase: misma ΔH y temperatura de descarga.)  El volumen es el
    de la ecuación de estado (con Peneloux si está activo), como en PVTsim,
    aunque la densidad del líquido se informe con COSTALD."""
    if P2 <= P1:
        raise SinSolucionOU("La presión de salida de la bomba debe ser mayor que la de entrada.")
    res = _base('bomba', z, ctx, n, T1, P1)
    e1 = res['entrada']
    if 'L' not in e1['fases'] and 'W' not in e1['fases']:
        raise SinSolucionOU("La bomba no acepta una corriente de gas en la entrada.")
    ctx_v = dict(ctx, metodo='Peneloux' if ctx['metodo'] == 'Peneloux' else 'EOS')
    dP = P2 - P1
    V_m = estado(z, T1, 0.5*(P1 + P2), ctx_v)['V']
    dH = V_m*dP*PSI_FT3_BTU/eta
    T2 = _T_de_H(z, P2, e1['H'] + dH, ctx, T1)
    e2 = estado(z, T2, P2, ctx)
    res['salida'] = e2
    res['datos'] = dict(eta=eta, dH=e2['H'] - e1['H'], V_medio=V_m,
                        trabajo=n*(e2['H'] - e1['H']), relacion=P2/P1)
    _aviso_fases(res, "bomba")
    return res


def valvula(z, ctx, n, T1, P1, P2):
    if P2 >= P1:
        raise SinSolucionOU("La presión de salida de la válvula debe ser menor que la de entrada.")
    res = _base('valvula', z, ctx, n, T1, P1)
    e1 = res['entrada']
    T2 = _T_de_H(z, P2, e1['H'], ctx, T1)
    res['salida'] = estado(z, T2, P2, ctx)
    res['datos'] = dict(dP=P1 - P2, JT=(T2 - T1)/(P2 - P1))
    return res


def separador(z, ctx, n, T1, P1):
    res = _base('separador', z, ctx, n, T1, P1)
    res['datos'] = {}
    return res


def ejecutar(spec, progreso=None):
    """spec: dict con op, z, ctx, n (lbmol/h), T1, P1 y los datos propios de
    cada operación (ver ventana de ingreso)."""
    op = spec['op']; z = spec['z']; ctx = spec['ctx']; n = spec['n']
    T1 = spec['T1']; P1 = spec['P1']
    if op == 'compresor':
        if spec.get('metodo') == 'pace':
            return compresor_pace(z, ctx, n, T1, P1, spec['salida'],
                                  eta=spec.get('eta', 1.0), P2=spec.get('P2'),
                                  T2=spec.get('T2'), trabajo=spec.get('trabajo'),
                                  head=spec.get('head'), progreso=progreso)
        return compresor_clasico(z, ctx, n, T1, P1, spec['P2'], spec.get('eta', 1.0))
    if op == 'expansor':
        return expansor(z, ctx, n, T1, P1, spec['P2'], spec.get('eta', 1.0))
    if op in ('enfriador', 'calentador'):
        return intercambiador(op, z, ctx, n, T1, P1, spec['T2'], spec.get('dP', 0.0))
    if op == 'bomba':
        return bomba(z, ctx, n, T1, P1, spec['P2'], spec.get('eta', 1.0))
    if op == 'valvula':
        return valvula(z, ctx, n, T1, P1, spec['P2'])
    return separador(z, ctx, n, T1, P1)

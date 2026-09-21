# -*- coding: utf-8 -*-
"""
hidratos.py — Cálculo de formación de hidratos de gas (modelo PVTsim / Munck).

Reproduce el módulo de hidratos de PVTsim: modelo de van der Waals–Platteeuw
con adsorción de Langmuir (Munck et al., 1988) y término de referencia
(μβ−μα) integrado con las constantes de Erickson (1983) / Mehta-Sloan (1994).
Las fugacidades de los formadores se toman de un flash bifásico bien convergido
y se usa la fugacidad de MEZCLA (promedio molar sobre las fases HC presentes),
tal como especifica la documentación técnica de PVTsim (paso 4 del flash P/T).

Compatible con las cuatro EOS del programa mediante las funciones genéricas de
`eos` (eos.am, eos.bm, eos.solve_Z, eos.phi_vec, eos.Ki_wilson) que despachan
según la EOS activa. Para las EOS de HYSYS se aplica extrapolación pragmática:
el mismo modelo de PVTsim con las fugacidades de la EOS de HYSYS.

Convención de unidades interna: T en °R, P en psia (igual que el resto del
motor). Las constantes de referencia están en unidades SI (J/mol, cm³/mol, K).
"""
import numpy as np
import eos

# ── Constantes físicas ────────────────────────────────────────────────
R = 8.314472          # J/mol·K
T0 = 273.15           # K  (temperatura de referencia)
T0_R = 491.67         # °R (= 273.15 K, frontera hielo/líquido)
PSIA_PER_ATM = 14.696

# Índice de componentes (orden del motor).  Solo estos entran en cavidades.
_IDX = {'N2':0, 'CO2':1, 'C1':2, 'C2':3, 'C3':4, 'iC4':5, 'nC4':6,
        'iC5':7, 'nC5':8, 'nC6':9, 'nC7':10, 'nC8':11, 'nC9':12}

# Número de cavidades por molécula de agua (por celda unitaria):
#   sI : 46 H₂O, 2 pequeñas, 6 grandes
#   sII: 136 H₂O, 16 pequeñas, 8 grandes
_NU = {'I': (2.0/46.0, 6.0/46.0),
       'II': (16.0/136.0, 8.0/136.0)}

# ── Parámetros de Langmuir A/B por EOS ────────────────────────────────
# Formato por componente: [A_Is, B_Is, A_Il, B_Il, A_IIs, B_IIs, A_IIl, B_IIl]
#   A en °R/psia, B en K.  C_Ki = (A/T_R)·exp(B/T_K)  →  C en 1/psia.
#   None = el componente no entra en esa cavidad.
# Fuente: base de datos PVTsim (hojas PARAMETROS de los Excel de estudio),
# específicos para cada EOS.
_AB_PR = {
    'N2':  [0.008582, 1740, 0.004147, 2028, 0.008139, 1444, 0.1898, 229],
    'CO2': [3.245, 38.6, 0.0001382, 3856, 0.0003812, 2652, 0.0005987, 3183],
    'C1':  [102.8, -881.1, 0.0002506, 3405, 0.00863, 1865, 0.0007885, 2785],
    'C2':  [0, 0, 0.001061, 3583, 0, 0, 0.001212, 3770],
    'C3':  [None, None, None, None, 0, 0, 3.685e-06, 6081],
    'iC4': [None, None, None, None, 0, 0, 0.0002943, 4988],
    'nC4': [None, None, None, None, 0, 0, 2.663e-07, 6305],
    'iC5': [None]*8, 'nC5': [None]*8, 'nC6': [None]*8,
    'nC7': [None]*8, 'nC8': [None]*8, 'nC9': [None]*8,
}
_AB_SRK = {
    'N2':  [0.006553, 932.3, 0.004238, 2240, 0.0009317, 2004, 0.01176, 1596],
    'CO2': [6.026e-12, 7470, 0.01224, 2617, 7.548e-06, 3691, 0.02089, 2591],
    'C1':  [0.005947, 1594, 0.001543, 2952, 0.0002876, 2777, 0.1335, 1323],
    'C2':  [0, 0, 0.0003722, 3861, 0, 0, 0.0009137, 4000],
    'C3':  [None, None, None, None, 0, 0, 0.001026, 4521],
    'iC4': [None, None, None, None, 0, 0, 0.01016, 4013],
    'nC4': [None, None, None, None, 0, 0, 0.0001566, 4580],
    'iC5': [None]*8, 'nC5': [None]*8, 'nC6': [None]*8,
    'nC7': [None]*8, 'nC8': [None]*8, 'nC9': [None]*8,
}

# ── Constantes de referencia (μβ−μα) por EOS y estructura ─────────────
# dmu0, dHl (líq), dHi (hielo) en J/mol; dV (líq), dVi (hielo) en cm³/mol;
# dCp en J/mol·K.  sI se mantiene en los valores de Munck; sII afinado por EOS
# sobre la curva completa (desplazamientos mínimos vs Munck, específicos de la
# EOS — análogo a los parámetros de Langmuir, NO calibración por punto).
_REF_PR = {
    'I':  dict(dmu0=1264.0,   dHl=-4858.0,   dHi=1151.0, dV=4.6,     dVi=3.0, dCp=-39.16),
    'II': dict(dmu0=882.705,  dHl=-5250.68,  dHi=808.0,  dV=5.1111,  dVi=3.4, dCp=-39.16),
}
_REF_SRK = {
    'I':  dict(dmu0=1264.0,   dHl=-4858.0,   dHi=1151.0, dV=4.6,    dVi=3.0, dCp=-39.16),
    'II': dict(dmu0=882.783,  dHl=-5249.92,  dHi=808.0,  dV=5.1155, dVi=3.4, dCp=-39.16),
}


def _eos_family(nombre_eos):
    """Devuelve 'PR' o 'SRK' según la EOS activa (agrupa HYSYS y PVTsim).

    Extrapolación pragmática para HYSYS: se usan los parámetros de hidratos de
    la contraparte PVTsim (PR o SRK) con las fugacidades de la EOS de HYSYS.
    """
    return 'SRK' if eos.es_srk(nombre_eos) else 'PR'


def _params(nombre_eos):
    """(AB, REF) apropiados para la EOS activa."""
    if _eos_family(nombre_eos) == 'SRK':
        return _AB_SRK, _REF_SRK
    return _AB_PR, _REF_PR


def TK(T_R):
    """°R → K."""
    return T_R / 1.8


# ══════════════════════════════════════════════════════════════════════
# Fugacidad de mezcla (flash bifásico bien convergido)
# ══════════════════════════════════════════════════════════════════════
def fugacidad_mezcla(z, T_R, P_psia, kij, tol=1e-11, max_iter=600):
    """Fugacidades [psia] de los componentes en la fase HC.

    Corre un flash isotérmico (sustitución sucesiva) bien convergido.  En la
    zona bifásica f_v = f_l en equilibrio, por lo que la fugacidad de mezcla
    (promedio molar sobre las fases HC) coincide con la de cualquiera de las
    dos fases.  Fuera de la región bifásica devuelve la fugacidad de la única
    fase presente.  Usa las funciones genéricas de `eos`, así que respeta la
    EOS activa (PR/SRK, HYSYS/PVTsim).
    """
    z = np.asarray(z, dtype=float)
    NC = len(z)
    K = np.array([eos.Ki_wilson(i, T_R, P_psia) for i in range(NC)])

    def _rr(V):
        return float(np.sum(z * (K - 1.0) / (1.0 + V * (K - 1.0))))

    def _fug_una_fase(comp, raiz):
        am = eos.am(comp, T_R, kij); bm = eos.bm(comp)
        ZV, ZL = eos.solve_Z(*eos.AB(am, bm, T_R, P_psia))
        Z = ZV if raiz == 'V' else ZL
        return eos.phi_vec(comp, T_R, P_psia, Z, am, bm, kij) * comp * P_psia

    fase = '2'
    x = y = None
    for _ in range(max_iter):
        if _rr(1e-10) < 0.0:      # todo líquido
            fase = 'L'; break
        if _rr(1.0 - 1e-10) > 0.0:  # todo vapor
            fase = 'V'; break
        # Rachford-Rice por bisección
        lo, hi = 1e-12, 1.0 - 1e-12
        for _ in range(90):
            V = 0.5 * (lo + hi)
            if _rr(V) > 0.0:
                lo = V
            else:
                hi = V
        x = z / (1.0 + V * (K - 1.0)); y = K * x
        x = x / x.sum(); y = y / y.sum()
        amv = eos.am(y, T_R, kij); bmv = eos.bm(y)
        ZV, _ = eos.solve_Z(*eos.AB(amv, bmv, T_R, P_psia))
        phiv = eos.phi_vec(y, T_R, P_psia, ZV, amv, bmv, kij)
        aml = eos.am(x, T_R, kij); bml = eos.bm(x)
        _, ZL = eos.solve_Z(*eos.AB(aml, bml, T_R, P_psia))
        phil = eos.phi_vec(x, T_R, P_psia, ZL, aml, bml, kij)
        Kn = phil / phiv
        if np.max(np.abs(np.log(Kn / K))) < tol:
            K = Kn; break
        K = Kn

    if fase == 'V':
        return _fug_una_fase(z, 'V')
    if fase == 'L':
        return _fug_una_fase(z, 'L')
    # bifásico: f_v = f_l → basta la fase vapor
    return _fug_una_fase(y, 'V')


# ══════════════════════════════════════════════════════════════════════
# Términos del potencial químico
# ══════════════════════════════════════════════════════════════════════
def _dmu_H_beta(estruct, T_R, f_psia, AB):
    """(μH − μβ)/RT = Σ νᵢ ln(1 − Σ_K Y_Ki)  (estabilización de Langmuir)."""
    T_K = TK(T_R)
    nu_s, nu_l = _NU[estruct]
    si = 0 if estruct == 'I' else 4
    C_s = np.zeros(len(f_psia)); C_l = np.zeros(len(f_psia))
    for name, i in _IDX.items():
        ab = AB[name]
        As, Bs, Al, Bl = ab[si], ab[si+1], ab[si+2], ab[si+3]
        if As not in (None, 0):
            C_s[i] = (As / T_R) * np.exp(Bs / T_K)
        if Al not in (None, 0):
            C_l[i] = (Al / T_R) * np.exp(Bl / T_K)
    denom_s = 1.0 + float(C_s @ f_psia)
    denom_l = 1.0 + float(C_l @ f_psia)
    Y_s = float((C_s * f_psia).sum()) / denom_s
    Y_l = float((C_l * f_psia).sum()) / denom_l
    return (nu_s * np.log(max(1.0 - Y_s, 1e-300)) +
            nu_l * np.log(max(1.0 - Y_l, 1e-300)))


def _dmu_beta_alpha(estruct, T_R, P_psia, fase_agua, REF):
    """(μβ − μα)/RT — diferencia red vacía ↔ agua líquida/hielo.

    (μβ−μα)/RT = Δμ0/(R·T0) − ∫[ΔH0+ΔCp(T−T0)]/(R·T²)dT + ΔV·P/(R·T̄)
    con P0 = 0 y T̄ = (T+T0)/2.
    """
    r = REF[estruct]
    T = TK(T_R)
    P_atm = P_psia / PSIA_PER_ATM
    Tbar = (T + T0) / 2.0
    if fase_agua == 'liq':
        dH0, dV = r['dHl'], r['dV']
    else:
        dH0, dV = r['dHi'], r['dVi']
    dCp = r['dCp']
    intH = (-dH0 / R * (1.0/T - 1.0/T0)
            + dCp / R * (np.log(T/T0) + T0 * (1.0/T - 1.0/T0)))
    t_pv = (dV * 1e-6) * (P_atm * 101325.0) / (R * Tbar)
    return r['dmu0'] / (R * T0) - intH + t_pv


def actividad_agua(z_full, T_R, P_psia, nombre_eos=None, kij_full=None):
    """Actividad del agua a_w en la mezcla a (T,P), vía el flash trifásico.

    • Si hay fase acuosa libre (β_W > 0) el agua está saturada → a_w = 1.
    • Si NO hay agua libre (subsaturado, toda el agua disuelta en el gas/HC)
      → a_w = f_w(sistema)/f_w(agua líquida pura) < 1, y la curva de hidratos
      se desplaza (menos agua ⇒ hidrato más difícil), como en PVTsim.

    z_full: composición de 14 comp. (índice 13 = agua).  Devuelve 1.0 si no hay
    agua o si el cálculo falla (comportamiento conservador = agua saturada)."""
    import numpy as _np
    z_full = _np.asarray(z_full, dtype=float)
    if len(z_full) <= 13 or z_full[13] <= 1e-12:
        return 1.0
    if nombre_eos is None:
        nombre_eos = eos.get_eos()
    try:
        import flash_agua as _fa
        met = 'hv'
        r = _fa.flash_trifasico(z_full/ z_full.sum(), float(T_R), float(P_psia),
                                eos=nombre_eos, metodo=met)
        if r.get('beta_W', 0.0) > 1e-6:
            return 1.0                      # agua libre → saturada
        # Sin agua libre: a_w = (x_w·φ_w) en la fase HC / φ_w(agua pura líquida)
        _fa._METODO = met; _fa._EOS_CTX = nombre_eos; _fa._T_CTX = float(T_R)
        Tc, Pc, om, PM, kij = _fa._params_14(nombre_eos)
        es_srk = eos.es_srk(nombre_eos)
        aa, bi = _fa._ai_bi(nombre_eos, Tc, Pc, om, float(T_R))
        # fase que contiene el agua (vapor si β_V>0, si no líquido HC)
        if r.get('beta_V', 0.0) > 1e-9 and r.get('y') is not None:
            fase = _np.asarray(r['y']); tipo = 'V'
        else:
            fase = _np.asarray(r['x']); tipo = 'L'
        lnp, _ = _fa._ln_phi(fase, aa, bi, kij, float(T_R), float(P_psia), es_srk, tipo)
        if lnp is None:
            return 1.0
        f_w_sist = fase[13]*_np.exp(lnp[13])*P_psia
        # agua líquida pura
        wpure = _np.zeros(14); wpure[13] = 1.0
        lnpw, _ = _fa._ln_phi(wpure, aa, bi, kij, float(T_R), float(P_psia), es_srk, 'L')
        if lnpw is None:
            return 1.0
        f_w_pure = _np.exp(lnpw[13])*P_psia
        if f_w_pure <= 0:
            return 1.0
        a = f_w_sist/f_w_pure
        return float(min(max(a, 1e-6), 1.0))
    except Exception:
        return 1.0


def criterio(z, T_R, P_psia, kij=None, nombre_eos=None, a_w=1.0):
    """Δμ = (μH − μα)/RT del hidrato más estable.

    Cero → punto sobre la curva de hidratos.  < 0 → se forma hidrato.
    a_w: actividad del agua en la fase α (1 = agua pura/saturada).  Con a_w<1
    (agua subsaturada) el potencial del agua baja en RT·ln(a_w), por lo que la
    formación de hidrato exige más presión / menor temperatura.
    """
    if nombre_eos is None:
        nombre_eos = eos.get_eos()
    if kij is None:
        kij = eos.kij_base(nombre_eos)
    AB, REF = _params(nombre_eos)
    fase_agua = 'liq' if T_R >= T0_R else 'ice'
    f = fugacidad_mezcla(z, T_R, P_psia, kij)
    corr = 0.0 if a_w >= 1.0 else -np.log(max(a_w, 1e-12))
    vals = [(_dmu_H_beta(s, T_R, f, AB)
             + _dmu_beta_alpha(s, T_R, P_psia, fase_agua, REF) + corr)
            for s in ('I', 'II')]
    return min(vals)


def estructura_estable(z, T_R, P_psia, kij=None, nombre_eos=None, a_w=1.0):
    """Devuelve ('I'|'II', Δμ) de la estructura de menor potencial."""
    if nombre_eos is None:
        nombre_eos = eos.get_eos()
    if kij is None:
        kij = eos.kij_base(nombre_eos)
    AB, REF = _params(nombre_eos)
    fase_agua = 'liq' if T_R >= T0_R else 'ice'
    f = fugacidad_mezcla(z, T_R, P_psia, kij)
    corr = 0.0 if a_w >= 1.0 else -np.log(max(a_w, 1e-12))
    dI = _dmu_H_beta('I', T_R, f, AB) + _dmu_beta_alpha('I', T_R, P_psia, fase_agua, REF) + corr
    dII = _dmu_H_beta('II', T_R, f, AB) + _dmu_beta_alpha('II', T_R, P_psia, fase_agua, REF) + corr
    return ('I', dI) if dI < dII else ('II', dII)


# ══════════════════════════════════════════════════════════════════════
# Resolución de puntos de la curva
# ══════════════════════════════════════════════════════════════════════
def _brentq(func, a, b, xtol=1e-6, max_iter=80):
    """Brent simplificado (bisección robusta) sin dependencia de scipy."""
    fa, fb = func(a), func(b)
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0.0:
        raise ValueError("sin cambio de signo en [%g, %g] (f=%g, %g)"
                         % (a, b, fa, fb))
    for _ in range(max_iter):
        m = 0.5 * (a + b)
        fm = func(m)
        if abs(fm) < 1e-14 or (b - a) < xtol:
            return m
        if fa * fm < 0.0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def _raices_en_rango(func, a, b, n=48):
    """Devuelve todas las raíces de func en [a,b] detectando cambios de signo
    sobre una rejilla y refinando cada uno con brentq. Robusto para curvas de
    hidrato con forma cerrada (dos ramas) como ocurre sin metano."""
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    fs = []
    for x in xs:
        try:
            fs.append(func(x))
        except Exception:
            fs.append(None)
    raices = []
    for i in range(n):
        f0, f1 = fs[i], fs[i + 1]
        if f0 is None or f1 is None:
            continue
        if f0 == 0.0:
            raices.append(xs[i])
        elif f0 * f1 < 0.0:
            try:
                raices.append(_brentq(func, xs[i], xs[i + 1], xtol=1e-5))
            except ValueError:
                pass
    return raices


def temperatura_hidrato(z, P_psia, kij=None, nombre_eos=None,
                        T_min=300.0, T_max=560.0, a_w=1.0):
    """Temperatura de formación de hidrato [°R] a presión dada.

    La curva de hidratos puede ser monótona (con metano) o de forma cerrada
    con dos ramas (p. ej. sin metano). La frontera de formación es la raíz de
    MAYOR temperatura: por debajo de ella el hidrato es estable. Devuelve None
    si no hay ninguna raíz en el rango.

    a_w: actividad del agua (1 = saturada). Con a_w<1 la curva se desplaza.
    Se pasa fija (no se recalcula en cada evaluación) para no encarecer la
    resolución — a_w varía muy poco en la pequeña ventana de T de la raíz.
    """
    if nombre_eos is None:
        nombre_eos = eos.get_eos()
    if kij is None:
        kij = eos.kij_base(nombre_eos)

    def f(T_R):
        return criterio(z, T_R, P_psia, kij, nombre_eos, a_w=a_w)
    raices = _raices_en_rango(f, T_min, T_max)
    return max(raices) if raices else None


def presion_hidrato(z, T_R, kij=None, nombre_eos=None,
                    P_min=1e-3, P_max=12000.0, a_w=1.0):
    """Presión de formación de hidrato [psia] a temperatura dada.

    La frontera de formación es la raíz de MENOR presión: por encima de ella
    el hidrato es estable. Devuelve None si no hay raíz en el rango.
    """
    if nombre_eos is None:
        nombre_eos = eos.get_eos()
    if kij is None:
        kij = eos.kij_base(nombre_eos)

    def f(P):
        return criterio(z, T_R, P, kij, nombre_eos, a_w=a_w)
    # Rejilla log en presión: la curva cambia rápido a baja P.
    import math as _m
    n = 48
    xs = [P_min * (P_max / P_min) ** (i / n) for i in range(n + 1)]
    fs = []
    for x in xs:
        try:
            fs.append(f(x))
        except Exception:
            fs.append(None)
    raices = []
    for i in range(n):
        f0, f1 = fs[i], fs[i + 1]
        if f0 is None or f1 is None:
            continue
        if f0 == 0.0:
            raices.append(xs[i])
        elif f0 * f1 < 0.0:
            try:
                raices.append(_brentq(f, xs[i], xs[i + 1], xtol=1e-4))
            except ValueError:
                pass
    return min(raices) if raices else None


def punto_hidrato(z, modo, valor, kij=None, nombre_eos=None, z_full=None):
    """Calcula un punto de la curva de hidratos.

    modo='T'  → 'valor' es P [psia], se resuelve T [°R].
    modo='P'  → 'valor' es T [°R],   se resuelve P [psia].

    z_full: composición de 14 comp. (con agua). Si se da y hay agua, el punto
    considera la actividad del agua a_w (subsaturado desplaza la curva).

    Devuelve dict con T_R, P_psia, estructura, flash (composiciones y fracción
    de fase) y propiedades del flash en ese punto, o None si no hay solución.
    """
    if nombre_eos is None:
        nombre_eos = eos.get_eos()
    if kij is None:
        kij = eos.kij_base(nombre_eos)

    usar_aw = (z_full is not None and len(np.asarray(z_full)) > 13
               and np.asarray(z_full, dtype=float)[13] > 1e-12)

    if modo == 'T':
        P = float(valor)
        T = temperatura_hidrato(z, P, kij, nombre_eos)
        if T is not None and usar_aw:
            a_w = actividad_agua(z_full, float(T), P, nombre_eos)
            if a_w < 1.0:
                T = temperatura_hidrato(z, P, kij, nombre_eos, a_w=a_w)
        if T is None:
            return None
    else:
        T = float(valor)
        P = presion_hidrato(z, T, kij, nombre_eos)
        if P is not None and usar_aw:
            a_w = actividad_agua(z_full, T, float(P), nombre_eos)
            if a_w < 1.0:
                P = presion_hidrato(z, T, kij, nombre_eos, a_w=a_w)
        if P is None:
            return None

    a_w_fin = actividad_agua(z_full, T, P, nombre_eos) if usar_aw else 1.0
    est, dmu = estructura_estable(z, T, P, kij, nombre_eos, a_w=a_w_fin)
    return {'T_R': T, 'P_psia': P, 'estructura': est, 'dmu': dmu,
            'fase_agua': 'liq' if T >= T0_R else 'ice'}


# ══════════════════════════════════════════════════════════════════════
# Curva de formación de hidratos (para graficar sobre la envolvente)
# ══════════════════════════════════════════════════════════════════════
def curva_hidratos(z, kij=None, nombre_eos=None,
                   P_tope=None, T_min_R=None, n_puntos=60,
                   P_piso=5.0, z_full=None):
    """Genera la curva de formación de hidratos como lista de (T_R, P_psia).

    La curva se traza barriendo presión (resolviendo T en cada P), que es la
    forma robusta en la rama casi vertical de alta presión.

    Parámetros de recorte:
      P_tope   : presión máxima [psia].  Por defecto ~ cricondenbárica·1.05
                 si se provee vía `P_cricond`; si None se usa 6000 psia.
      T_min_R  : temperatura mínima [°R].  Por defecto 300°R (~ -160°F), que
                 cubre holgadamente el rango de interés operativo.
      P_piso   : presión mínima [psia] desde la que empezar (evita la cola de
                 presiones ínfimas donde la curva es casi horizontal).
    """
    if nombre_eos is None:
        nombre_eos = eos.get_eos()
    if kij is None:
        kij = eos.kij_base(nombre_eos)
    if P_tope is None:
        P_tope = 6000.0
    if T_min_R is None:
        T_min_R = 300.0

    # Rejilla de presión log-lineal: densa a baja P (donde la curva cambia
    # rápido) y espaciada a alta P (rama casi vertical).
    P_lo = max(P_piso, 1.0)
    presiones = np.geomspace(P_lo, P_tope, n_puntos)

    usar_aw = (z_full is not None and len(np.asarray(z_full)) > 13
               and np.asarray(z_full, dtype=float)[13] > 1e-12)
    pts = []
    for P in presiones:
        # Primero la T con agua saturada (a_w=1); luego, si hay agua definida,
        # se calcula a_w UNA vez en esa (T,P) y se reresuelve. Barato (1-2 flash
        # por punto) y correcto: a_w apenas cambia en la ventana de la raíz.
        T = temperatura_hidrato(z, float(P), kij, nombre_eos,
                                T_min=max(T_min_R, 290.0), T_max=560.0)
        if T is not None and usar_aw:
            a_w = actividad_agua(z_full, float(T), float(P), nombre_eos)
            if a_w < 1.0:
                T = temperatura_hidrato(z, float(P), kij, nombre_eos,
                                        T_min=max(T_min_R, 290.0), T_max=560.0,
                                        a_w=a_w)
        if T is None:
            continue
        if T < T_min_R:
            continue
        pts.append((T, float(P)))
    return pts

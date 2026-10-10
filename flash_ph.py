"""
flash_ph.py — Flash de presión y entalpía (PH) y de presión y entropía (PS).

Dada la presión y la entalpía molar de la mezcla, busca la temperatura a la
que el flash PT de la mezcla tiene exactamente esa entalpía:

    H(T, P) = H_especificada

La entalpía de la mezcla es la misma que muestra Equilibrio de fases (suma de
las fases ponderada por su fracción molar, con la EOS, los kij y el método de
densidad de la corriente; Peneloux desplaza H en −P·c).  A presión constante
H crece con T (dH/dT = Cp > 0, incluido el calor latente cuando cambia la
cantidad de cada fase), de modo que la solución es única: se acota un
intervalo con cambio de signo y se resuelve con el método de Brent (propio,
sin scipy), robusto
también cuando aparece o desaparece una fase dentro del intervalo.  El flash PS es idéntico con la entropía
(dS/dT = Cp/T > 0).
"""

class SinSolucion(ValueError):
    """No existe solución a las condiciones dadas (no es una falla del
    cálculo): la interfaz lo muestra como advertencia."""


def _brent(f, a, b, fa, fb, xtol=1e-5, maxiter=100):
    """Método de Brent (interpolación cuadrática inversa + secante +
    bisección) sobre [a, b] con f(a)·f(b) ≤ 0.  Sin dependencias externas
    (el programa no requiere scipy); fa y fb ya calculados se reutilizan."""
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if abs(fa) < abs(fb):
        a, b, fa, fb = b, a, fb, fa
    c, fc = a, fa
    d = e = b - a
    mflag = True
    for _ in range(maxiter):
        if fb == 0.0 or abs(b - a) < xtol:
            return b
        if fa != fc and fb != fc:
            s = (a*fb*fc/((fa - fb)*(fa - fc)) + b*fa*fc/((fb - fa)*(fb - fc))
                 + c*fa*fb/((fc - fa)*(fc - fb)))
        else:
            s = b - fb*(b - a)/(fb - fa)
        cond = ((s - (3*a + b)/4)*(s - b) >= 0
                or (mflag and abs(s - b) >= abs(b - c)/2)
                or (not mflag and abs(s - b) >= abs(c - d)/2)
                or (mflag and abs(b - c) < xtol)
                or (not mflag and abs(c - d) < xtol))
        if cond:
            s = (a + b)/2; mflag = True
        else:
            mflag = False
        fs = f(s)
        d, c, fc = c, b, fb
        if fa*fs < 0:
            b, fb = s, fs
        else:
            a, fa = s, fs
        if abs(fa) < abs(fb):
            a, b, fa, fb = b, a, fb, fa
    return b


T_MIN_R = 150.0          # ≈ −310 °F
T_MAX_R = 2500.0         # ≈ 2040 °F


def _propiedad_mezcla(z, T_R, P, kij, eos, metodo, agua, clave):
    import eos as _e
    from pestana_propiedades import _punto
    _e.set_eos(eos)
    r = _punto(z, float(T_R), float(P), kij, eos, metodo, agua)
    v = r.get(clave)
    if v is None:
        raise ValueError("No se pudo calcular la entalpía/entropía de la mezcla.")
    return float(v)


def entalpia_mezcla(z, T_R, P, kij, eos, metodo, agua):
    """Entalpía molar de la mezcla [BTU/lbmol] en (T, P), por el mismo motor
    que Equilibrio de fases."""
    return _propiedad_mezcla(z, T_R, P, kij, eos, metodo, agua, 'H_stream')


def entropia_mezcla(z, T_R, P, kij, eos, metodo, agua):
    """Entropía molar de la mezcla [BTU/lbmol·°R] en (T, P), por el mismo
    motor que Equilibrio de fases."""
    return _propiedad_mezcla(z, T_R, P, kij, eos, metodo, agua, 'S_stream')


def _resolver_T(f, T0, tol, nombre):
    """Temperatura con f(T) = 0, siendo f creciente en T (H o S menos su
    valor especificado a presión constante)."""
    T0 = min(max(float(T0), T_MIN_R + 1.0), T_MAX_R - 1.0)
    f0 = f(T0)
    if abs(f0) < 1e-12:
        return T0
    # Estimación por la pendiente local (Cp o Cp/T) y luego acotamiento
    # alrededor de esa estimación con pasos crecientes.
    T1 = T0 + 10.0 if T0 + 10.0 < T_MAX_R else T0 - 10.0
    f1 = f(T1)
    pend = (f1 - f0)/(T1 - T0)
    if pend > 1e-12:
        Te = T0 - f0/pend
        Te = min(max(Te, T_MIN_R + 1.0), T_MAX_R - 1.0)
        a, fa = Te, f(Te)
        paso = 3.0
    else:
        a, fa = T0, f0
        paso = 20.0
    if abs(fa) < 1e-12:
        return a
    while True:
        b = a + paso if fa < 0 else a - paso
        b = min(max(b, T_MIN_R), T_MAX_R)
        fb = f(b)
        if fa*fb <= 0:
            lo, hi, flo, fhi = (a, b, fa, fb) if a < b else (b, a, fb, fa)
            break
        if b in (T_MIN_R, T_MAX_R):
            raise SinSolucion(
                f"La {nombre} especificada está fuera del rango de temperatura "
                "calculable (−310 °F a 2040 °F) a esta presión.")
        a, fa = b, fb
        paso *= 2.0
    return _brent(f, lo, hi, flo, fhi, xtol=tol)


def flash_ph(z, P, H_spec, kij, eos, metodo='EOS', agua=False, T0=530.0,
             tol=1e-5):
    """Temperatura [°R] a la que la mezcla tiene la entalpía H_spec
    [BTU/lbmol] a la presión P [psia]."""
    f = lambda T: entalpia_mezcla(z, T, P, kij, eos, metodo, agua) - float(H_spec)
    return _resolver_T(f, T0, tol, "entalpía")


def flash_ps(z, P, S_spec, kij, eos, metodo='EOS', agua=False, T0=530.0,
             tol=1e-5):
    """Temperatura [°R] a la que la mezcla tiene la entropía S_spec
    [BTU/lbmol·°R] a la presión P [psia].  A presión constante
    dS/dT = Cp/T > 0, así que la solución también es única."""
    f = lambda T: entropia_mezcla(z, T, P, kij, eos, metodo, agua) - float(S_spec)
    return _resolver_T(f, T0, tol, "entropía")


# ════════════════════════════════════════════════════════════════════════════
# Flash con fracción de vapor especificada (P-β y T-β, como PVTsim)
# ════════════════════════════════════════════════════════════════════════════
# β es la fracción molar de vapor de las fases de HIDROCARBURO (sin la fase
# acuosa), igual que en PVTsim.  β = 0 → punto de burbuja; β = 1 → punto de
# rocío; 0 < β < 1 → punto de una línea de calidad.
P_MIN_PSIA = 0.5
P_MAX_PSIA = 15000.0


def beta_hc(z, T_R, P, kij, eos, metodo, agua):
    """Fracción de vapor de las fases de hidrocarburo en (T, P)."""
    import eos as _e
    from pestana_propiedades import _punto
    _e.set_eos(eos)
    r = _punto(z, float(T_R), float(P), kij, eos, metodo, agua)
    V = float(r.get('V') or 0.0); L = float(r.get('L') or 0.0)
    if V + L <= 1e-14:
        return 0.0
    return V/(V + L)


def _saturacion(tipo, valor, z, kij, eos, agua):
    """Valor de saturación (T [°R] o P [psia]) o None."""
    import saturacion as _sat
    zz = [float(v) for v in z]
    if agua:
        s = sum(zz[:14]); zs = [v/s for v in zz[:14]]
    else:
        s = sum(zz[:13]); zs = [v/s for v in zz[:13]]
    try:
        r = _sat.punto_saturacion(tipo, float(valor), zs, kij, eos=eos)
    except Exception:
        return None
    if not r or not r.get('exito', True):
        return None
    v = r.get('T' if tipo.startswith('T') else 'P')
    return float(v) if v else None


def _raiz_en_rejilla(g, xs, tol, ok=1e-4):
    """Primera raíz de g sobre la rejilla ordenada xs, refinada con Brent.
    Se descartan los cambios de signo que son saltos y no raíces (cerca del
    punto crítico el flash puede cambiar el rótulo vapor/líquido y β salta
    de ≈1 a 0): la raíz debe cumplir |g| < ok."""
    gp = None; xp = None
    for x in xs:
        try:
            gx = g(x)
        except Exception:
            continue
        if gp is not None and gp*gx <= 0:
            r = _brent(g, xp, x, gp, gx, xtol=tol)
            try:
                if abs(g(r)) < ok:
                    return r
            except Exception:
                pass
        xp, gp = x, gx
    return None


def _resolver_beta(g, lo, hi, glo, ghi, tol, ok=1e-4, n=24, log=False):
    """Raíz de g en [lo, hi]: Brent directo y, si cae en un salto, búsqueda
    en rejilla dentro del mismo intervalo."""
    import math
    r = _brent(g, lo, hi, glo, ghi, xtol=tol)
    try:
        if abs(g(r)) < ok:
            return r
    except Exception:
        pass
    if log:
        xs = [lo*math.exp(math.log(hi/lo)*k/n) for k in range(n + 1)]
    else:
        xs = [lo + (hi - lo)*k/n for k in range(n + 1)]
    return _raiz_en_rejilla(g, xs, tol, ok)


def flash_p_beta(z, P, beta, kij, eos, metodo='EOS', agua=False, tol=1e-5):
    """Temperatura [°R] a la que la mezcla, a la presión P [psia], tiene la
    fracción de vapor de hidrocarburos `beta`."""
    beta = float(beta)
    if not (0.0 <= beta <= 1.0):
        raise ValueError("La fracción de vapor debe estar entre 0 y 1.")
    if beta <= 0.0:
        Tb = _saturacion('T_burbuja', P, z, kij, eos, agua)
        if Tb is None:
            raise SinSolucion("No hay punto de burbuja a esta presión.")
        return Tb
    if beta >= 1.0:
        Td = _saturacion('T_rocio', P, z, kij, eos, agua)
        if Td is None:
            raise SinSolucion("No hay punto de rocío a esta presión.")
        return Td
    Tb = _saturacion('T_burbuja', P, z, kij, eos, agua)
    Td = _saturacion('T_rocio', P, z, kij, eos, agua)
    g = lambda T: beta_hc(z, T, P, kij, eos, metodo, agua) - beta
    T = None
    if Tb and Td and Td > Tb:
        # entre burbuja y rocío, β crece con T a presión constante
        T = _resolver_beta(g, Tb, Td, -beta, 1.0 - beta, tol)
    else:
        lo = (Tb or T_MIN_R + 1.0)
        hi = (Td or 1500.0)
        xs = [lo + (hi - lo)*k/40.0 for k in range(41)]
        T = _raiz_en_rejilla(g, xs, tol)
    if T is None:
        raise SinSolucion("No existe esa fracción de vapor a esta presión.")
    return T


def flash_t_beta(z, T_R, beta, kij, eos, metodo='EOS', agua=False, tol=1e-4):
    """Presión [psia] a la que la mezcla, a la temperatura T [°R], tiene la
    fracción de vapor de hidrocarburos `beta`.  En la zona retrógrada (entre
    la temperatura crítica y la cricondenterma) puede haber dos soluciones;
    se entrega la de menor presión."""
    import math
    beta = float(beta)
    if not (0.0 <= beta <= 1.0):
        raise ValueError("La fracción de vapor debe estar entre 0 y 1.")
    if beta <= 0.0:
        Pb = _saturacion('P_burbuja', T_R, z, kij, eos, agua)
        if Pb is None:
            raise SinSolucion("No hay punto de burbuja a esta temperatura.")
        return Pb
    Pd = _saturacion('P_rocio', T_R, z, kij, eos, agua)
    if beta >= 1.0:
        if Pd is None:
            raise SinSolucion("No hay punto de rocío a esta temperatura.")
        return Pd
    Pb = _saturacion('P_burbuja', T_R, z, kij, eos, agua)
    g = lambda P: beta_hc(z, T_R, P, kij, eos, metodo, agua) - beta
    P = None
    if Pb and Pd and Pb > Pd:
        # entre rocío y burbuja, β decrece con P a temperatura constante
        P = _resolver_beta(g, Pd, Pb, 1.0 - beta, -beta, tol, log=True)
    else:
        # zona retrógrada: rejilla logarítmica desde el rocío inferior
        lo = Pd if Pd else P_MIN_PSIA
        hi = 8000.0 if lo < 8000.0 else P_MAX_PSIA
        n = 18
        xs = [lo*math.exp(math.log(hi/lo)*k/n) for k in range(n + 1)]
        xs[0] = lo*1.0000001
        P = _raiz_en_rejilla(g, xs, tol)
    if P is None:
        raise SinSolucion("No existe esa fracción de vapor a esta temperatura.")
    return P

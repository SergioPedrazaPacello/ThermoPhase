"""
flash_ph.py — Flash de presión y entalpía (PH).

Dada la presión y la entalpía molar de la mezcla, busca la temperatura a la
que el flash PT de la mezcla tiene exactamente esa entalpía:

    H(T, P) = H_especificada

La entalpía de la mezcla es la misma que muestra Equilibrio de fases (suma de
las fases ponderada por su fracción molar, con la EOS, los kij y el método de
densidad de la corriente; Peneloux desplaza H en −P·c).  A presión constante
H crece con T (dH/dT = Cp > 0, incluido el calor latente cuando cambia la
cantidad de cada fase), de modo que la solución es única: se acota un
intervalo con cambio de signo y se resuelve con el método de Brent (propio,
sin scipy) (robusto
también cuando aparece o desaparece una fase dentro del intervalo).
"""

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


def entalpia_mezcla(z, T_R, P, kij, eos, metodo, agua):
    """Entalpía molar de la mezcla [BTU/lbmol] en (T, P), por el mismo motor
    que Equilibrio de fases."""
    import eos as _e
    from pestana_propiedades import _punto
    _e.set_eos(eos)
    r = _punto(z, float(T_R), float(P), kij, eos, metodo, agua)
    H = r.get('H_stream')
    if H is None:
        raise ValueError("No se pudo calcular la entalpía de la mezcla.")
    return float(H)


def flash_ph(z, P, H_spec, kij, eos, metodo='EOS', agua=False, T0=530.0,
             tol=1e-5):
    """Temperatura [°R] a la que la mezcla tiene la entalpía H_spec
    [BTU/lbmol] a la presión P [psia].  Lanza ValueError si no hay solución
    entre T_MIN_R y T_MAX_R."""
    f = lambda T: entalpia_mezcla(z, T, P, kij, eos, metodo, agua) - float(H_spec)
    T0 = min(max(float(T0), T_MIN_R + 1.0), T_MAX_R - 1.0)
    f0 = f(T0)
    if abs(f0) < 1e-9:
        return T0
    # Estimación por la pendiente local (≈ Cp) y luego acotamiento alrededor
    # de esa estimación con pasos crecientes (H crece con T).
    T1 = T0 + 10.0 if T0 + 10.0 < T_MAX_R else T0 - 10.0
    f1 = f(T1)
    pend = (f1 - f0)/(T1 - T0)
    if pend > 1e-9:
        Te = T0 - f0/pend
        Te = min(max(Te, T_MIN_R + 1.0), T_MAX_R - 1.0)
        a, fa = Te, f(Te)
        paso = 3.0
    else:
        a, fa = T0, f0
        paso = 20.0
    if abs(fa) < 1e-9:
        return a
    while True:
        b = a + paso if fa < 0 else a - paso
        b = min(max(b, T_MIN_R), T_MAX_R)
        fb = f(b)
        if fa*fb <= 0:
            lo, hi, flo, fhi = (a, b, fa, fb) if a < b else (b, a, fb, fa)
            break
        if b in (T_MIN_R, T_MAX_R):
            raise ValueError(
                "La entalpía especificada está fuera del rango de temperatura "
                "calculable (−310 °F a 2040 °F) a esta presión.")
        a, fa = b, fb
        paso *= 2.0
    return _brent(f, lo, hi, flo, fhi, xtol=tol)

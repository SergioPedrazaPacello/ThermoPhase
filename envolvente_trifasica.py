# -*- coding: utf-8 -*-
"""
envolvente_trifasica.py — Trazado de envolvente para mezclas HIDROCARBURO-AGUA
por el método de Lindeloff & Michelsen (SPE 85971, SPE J. Sept. 2003), tal como
lo hace PVTsim.

El diagrama PT genérico de un sistema HC-agua (Fig. 1 del paper) se construye en
tres etapas:

  1. Línea de rocío que separa la región monofásica de la bifásica (Líneas I y
     II): la fase incipiente w puede ser HIDROCARBURO o ACUOSA.
        Ec. 9 :  ln w_i + ln φ_i(w) − ln z_i − ln φ_i(z) = 0     (i=1..N)
        Ec.10 :  Σ w_i − 1 = 0
     Variables X = [ln K_i, ln T, ln P] con K_i = w_i/z_i, más una ecuación de
     especificación X_s = S. Newton completo + continuación de Michelsen (1980).

  2. Puntos trifásicos sobre la línea de rocío: donde la solución bifásica se
     vuelve inestable (test de plano tangente, Ec. 11-12) y z está en equilibrio
     con DOS fases incipientes (Ec. 16).

  3. Líneas trifásicas que separan la región bifásica de la trifásica (Líneas
     III y IV), con la fase incipiente w como referencia (Ec. 17-20) y β la
     fracción en la fase y.

Toda la termodinámica (φ, a_i·α, b_i, regla Huron-Vidal para pares agua-HC) se
toma del motor de 14 componentes de flash_agua.py, de modo que el modelo es el
MISMO que usa el flash trifásico validado.
"""

import numpy as np

N = 14                     # 13 HC + agua
IDX_AGUA = 13


# ════════════════════════════════════════════════════════════════════════════
# 1) Envoltura termodinámica de 14 componentes (sobre flash_agua)
# ════════════════════════════════════════════════════════════════════════════
class Termo:
    """Contexto termodinámico para (eos, metodo). Cachea a_i·α y b_i por T."""
    def __init__(self, eos, metodo):
        import flash_agua as _fa
        import eos as _e
        self.fa = _fa; self.e = _e
        self.eos = eos
        self.metodo = 'hv' if metodo == 'hv' else 'simple'
        self.Tc, self.Pc, self.om, self.PM, self.kij = _fa._params_14(eos)
        self.es_srk = _e.es_srk(eos)
        self._Tcache = None; self._aa = None; self._bi = None

    def _fijar_T(self, T):
        # Globales del motor HV (regla de mezcla depende de T).
        self.fa._METODO = self.metodo
        self.fa._EOS_CTX = self.eos
        self.fa._T_CTX = float(T)
        if self._Tcache != T:
            self._aa, self._bi = self.fa._ai_bi(self.eos, self.Tc, self.Pc,
                                                self.om, float(T))
            self._Tcache = T

    def lnphi(self, comp, T, P, fase='auto'):
        """ln φ_i de la composición comp (se normaliza) en (T,P)."""
        self._fijar_T(T)
        c = np.asarray(comp, dtype=float)
        s = c.sum()
        if s <= 0:
            return None
        c = c/s
        lnp, Z = self.fa._ln_phi(c, self._aa, self._bi, self.kij,
                                 float(T), float(P), self.es_srk, fase)
        return lnp

    def K_wilson(self, T, P):
        return self.fa._K_wilson(self.Tc, self.Pc, self.om, float(T), float(P))

    def lnphi_wilson_liq(self, T, P, tipo):
        """ln φ^l aproximado de Wilson para inicializar (Ec. 13 + regla +10).

        tipo='hc'  : líquido hidrocarburo  → +10 a los componentes ACUOSOS
        tipo='aq'  : líquido acuoso        → +10 a los componentes HC
        (el +10 expulsa a los componentes ajenos de esa fase incipiente)."""
        lnK = (np.log(self.Pc/P)
               + 5.373*(1.0 + self.om)*(1.0 - self.Tc/float(T)))   # ln K_Wilson
        # ln φ^l = ln K_Wilson  (con φ^v = 1, gas ideal)
        lnphi_l = lnK.copy()
        if tipo == 'hc':
            lnphi_l[IDX_AGUA] += 10.0
        else:  # 'aq'
            mask = np.ones(N, dtype=bool); mask[IDX_AGUA] = False
            lnphi_l[mask] += 10.0
        return lnphi_l


# ════════════════════════════════════════════════════════════════════════════
# 2) Solver de un punto de la LÍNEA DE ROCÍO  (Ec. 9-10 + especificación)
#    Variables X = [lnK_1..lnK_N, lnT, lnP].  w_i = exp(lnK_i)·z_i.
# ════════════════════════════════════════════════════════════════════════════
def _resid_dew(X, z, tm, spec_idx, S):
    lnK = np.clip(X[:N], -60.0, 60.0); lnT = X[N]; lnP = X[N+1]
    T = np.exp(lnT); P = np.exp(lnP)
    # Rango físico: fuera de él la EOS desborda; se rechaza el punto.
    if not (150.0 < T < 3000.0 and 0.05 < P < 60000.0):
        return None
    K = np.exp(lnK)
    w = K*z                              # incipiente (sin normalizar)
    try:
        lnphi_w = tm.lnphi(w, T, P)
        lnphi_z = tm.lnphi(z, T, P)
    except (OverflowError, FloatingPointError, ValueError):
        return None
    if lnphi_w is None or lnphi_z is None:
        return None
    g = np.empty(N+2)
    g[:N] = lnK + lnphi_w - lnphi_z      # Ec. 9
    g[N] = np.sum(w) - 1.0               # Ec. 10
    g[N+1] = X[spec_idx] - S             # especificación
    return g


def _jac_num(fun, X, f0, h=1e-6):
    n = len(X); J = np.empty((len(f0), n))
    for k in range(n):
        Xk = X.copy(); dx = h*max(1.0, abs(X[k])); Xk[k] += dx
        fk = fun(Xk)
        if fk is None:
            return None
        J[:, k] = (fk - f0)/dx
    return J


def _resolver_dew(X0, z, tm, spec_idx, S, tol=1e-9, maxit=40):
    """Newton completo para un punto de la línea de rocío. Devuelve (X, nit) o
    (None, nit)."""
    X = X0.copy()
    fun = lambda XX: _resid_dew(XX, z, tm, spec_idx, S)
    for it in range(maxit):
        f = fun(X)
        if f is None:
            return None, it
        if np.max(np.abs(f)) < tol:
            return X, it
        J = _jac_num(fun, X, f)
        if J is None:
            return None, it
        try:
            dX = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError:
            return None, it
        # Acotar el paso completo (log-variables) a un tamaño razonable; si el
        # punto resulta no evaluable, reducir a la mitad hasta que lo sea.
        mx = np.max(np.abs(dX))
        if mx > 4.0:
            dX = dX*(4.0/mx)
        lam = 1.0
        for _ls in range(20):
            Xn = X + lam*dX
            if fun(Xn) is not None:
                break
            lam *= 0.5
        else:
            return None, it
        X = Xn
    f = fun(X)
    if f is not None and np.max(np.abs(f)) < 1e-6:
        return X, maxit
    return None, maxit


def _dew_inicial(z, tm, P0, tipo):
    """Genera (X0, spec_idx, S) para el primer punto de la línea de rocío a P0,
    con fase incipiente 'hc' o 'aq'. Resuelve Ec. 14 (Σ z_i/φ^l_i = 1) para T."""
    # Buscar T que satisface Σ z_i/φ^l_i(T) = 1 (φ^v=1), por bisección en lnT.
    def defecto(T):
        lnphi_l = tm.lnphi_wilson_liq(T, P0, tipo)
        return np.sum(z/np.exp(lnphi_l)) - 1.0
    Tlo, Thi = 200.0, 1600.0
    flo, fhi = defecto(Tlo), defecto(Thi)
    if flo*fhi > 0:
        # no bracket: usar un T medio razonable
        Tsol = 560.0
    else:
        for _ in range(80):
            Tm = 0.5*(Tlo+Thi); fm = defecto(Tm)
            if flo*fm <= 0: Thi = Tm; fhi = fm
            else: Tlo = Tm; flo = fm
        Tsol = 0.5*(Tlo+Thi)
    lnphi_l = tm.lnphi_wilson_liq(Tsol, P0, tipo)
    w = z/np.exp(lnphi_l); w = w/np.sum(w)     # incipiente liquido (sesgado)
    # Un paso de sustitución sucesiva con la EOS real fija Eq. 9 casi a cero
    # (K = φ_z/φ_w), de modo que el residuo inicial ~= |Σw−1| es pequeño y el
    # Newton converge aunque los gases ligeros tengan φ enormes en agua.
    lnK = np.log(np.clip(w/z, 1e-300, None))
    for _ in range(3):
        lnphi_w = tm.lnphi(w, Tsol, P0)
        lnphi_z = tm.lnphi(z, Tsol, P0)
        if lnphi_w is None or lnphi_z is None:
            break
        lnK = np.clip(lnphi_z - lnphi_w, -60.0, 60.0)     # Ec. 9 → residuo≈0
        w = np.exp(lnK)*z; w = w/np.sum(w)
    X0 = np.concatenate([lnK, [np.log(Tsol), np.log(P0)]])
    spec_idx = N+1; S = np.log(P0)             # especificar P
    return X0, spec_idx, S, Tsol


# ════════════════════════════════════════════════════════════════════════════
# 3) Continuación de la línea de rocío (Michelsen 1980): sensibilidad dX/dS,
#    selección de variable de especificación y control de paso.
# ════════════════════════════════════════════════════════════════════════════
def _sensibilidad(X, z, tm, spec_idx, S):
    """dX/dS resolviendo J·(dX/dS) = e_spec (sólo la ec. de especificación
    depende de S)."""
    fun = lambda XX: _resid_dew(XX, z, tm, spec_idx, S)
    f = fun(X)
    if f is None:
        return None
    J = _jac_num(fun, X, f)
    if J is None:
        return None
    rhs = np.zeros(N+2); rhs[N+1] = 1.0        # ∂f_spec/∂S = −1 → J·dXdS = e
    try:
        return np.linalg.solve(J, rhs)
    except np.linalg.LinAlgError:
        return None


def _traza_dew(z, tm, tipo, P0=72.5, Pmax=15000.0, Pmin=3.0,
               Tmin=300.0, Tmax=1600.0, max_pts=400):
    """Traza una rama de la línea de rocío (incipiente 'hc' o 'aq') desde P0.
    Devuelve lista de dicts {P,T,X,w} ordenables para graficar y analizar."""
    X0, spec_idx, S, Tg = _dew_inicial(z, tm, P0, tipo)
    X, nit = _resolver_dew(X0, z, tm, spec_idx, S)
    if X is None:
        return []
    pts = []
    def registrar(X):
        T = np.exp(X[N]); P = np.exp(X[N+1])
        w = np.exp(X[:N])*z; w = w/np.sum(w)
        pts.append({'P': float(P), 'T': float(T), 'X': X.copy(), 'w': w})
    registrar(X)

    dS = 0.10                      # paso inicial en la variable de especificación
    direccion = +1.0               # sentido de avance (hacia mayor presión)
    sens_prev = None
    for _ in range(max_pts):
        sens = _sensibilidad(X, z, tm, spec_idx, S)
        if sens is None:
            break
        # nueva variable de especificación = la de mayor sensibilidad
        new_spec = int(np.argmax(np.abs(sens)))
        snorm = sens/sens[new_spec]            # dX/dS respecto a la nueva spec
        # mantener el sentido de avance por continuidad
        if sens_prev is not None:
            if np.dot(snorm, sens_prev) < 0:
                direccion = -direccion
        sens_prev = snorm.copy()
        spec_idx = new_spec
        S = X[spec_idx]
        # predicción
        paso = direccion*dS
        Xpred = X + snorm*paso
        Snew = S + paso
        Xsol, nit = _resolver_dew(Xpred, z, tm, spec_idx, Snew)
        if Xsol is None:
            dS *= 0.5
            if dS < 1e-4:
                break
            continue
        X = Xsol; S = Snew
        registrar(X)
        T = np.exp(X[N]); P = np.exp(X[N+1])
        if P > Pmax or P < Pmin or T > Tmax or T < Tmin:
            break
        # control de paso por número de iteraciones (objetivo 3-4)
        if nit <= 2:
            dS = min(dS*1.5, 0.35)
        elif nit >= 5:
            dS = max(dS*0.5, 1e-3)
    return pts

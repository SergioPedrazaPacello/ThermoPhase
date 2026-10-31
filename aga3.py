"""
aga3.py — Medición de gas con placa de orificio de cantos vivos y tomas
bridadas (AGA Report No. 3 / API MPMS cap. 14.3, Parte 1).

Dos modelos, calculados siempre en paralelo:

  'aga3'  Cálculo completo: corrección térmica de la placa y del tubo,
          coeficiente de descarga de Reader-Harris/Gallagher (iterado con el
          número de Reynolds), factor de velocidad de aproximación y factor de
          expansión (AGA 3 1992 o ISO 5167-2:2003).
  'simple' Ecuación básica del orificio con Cd = 0.6, Y = 1 y sin corrección
          térmica (supuestos del Daniel Orifice Flow Calculator, ASME MFC-3M).

Ecuación de caudal másico (unidades SI coherentes):
        qm = (π/4)·Cd·Ev·Y·d²·√(2·ρ1·ΔP)

La densidad del gas en condiciones de flujo y base se obtiene de AGA 8
DETAIL (aga8_detail), de la ecuación de estado activa o de un Z manual.

Unidades internas: m, Pa, K, kg/m³, Pa·s, kg/s.
"""
import math

import aga8_detail as a8

R_SI = 8.314462618          # J/(mol·K)
M_AIRE = 28.9625            # g/mol (AGA 3 / GPA 2145)
# Composición del aire seco para Z_aire con AGA 8 (N2, O2, Ar, CO2)
_AIRE = [0.0]*22
_AIRE[2], _AIRE[16], _AIRE[21], _AIRE[3] = 0.78102, 0.20946, 0.00916, 0.00036

IN_M = 0.0254
PSI_PA = 6894.757293168
INH2O_PA = PSI_PA/27.707     # pulgada de agua a 60 °F (AGA 3: 1 psi = 27.707 inH2O)
MU_DEFECTO = 0.010268e-3     # Pa·s (0.010268 cP, valor admitido por AGA 3)
K_DEFECTO = 1.3

# Coeficientes de dilatación lineal (1/°F) — AGA 3 Parte 1
MATERIALES = [
    ('ss', "Acero inoxidable 304/316", 9.25e-6),
    ('ss304', "Acero inoxidable 304", 9.61e-6),
    ('ss316', "Acero inoxidable 316", 8.89e-6),
    ('monel', "Monel 400", 7.95e-6),
    ('cs', "Acero al carbono", 6.20e-6),
]
ALFA_F = {k: a for k, _n, a in MATERIALES}


class SinSolucionAGA3(ValueError):
    pass


# ── Densidad del gas ────────────────────────────────────────────────────
def _x_aga8(z):
    return a8.desde_thermophase(z)


def _props_aga8(z, T, P):
    p = a8.propiedades(T, P/1000.0, _x_aga8(z))
    return dict(rho=p['rho'], Z=p['Z'], M=p['M'], kappa=p['kappa'])


def _props_eos(z, T, P, eos, kij):
    """Densidad y Z del gas con la ecuación de estado de ThermoPhase (sin agua)."""
    import eos as eng
    NC = eng.NC
    z13 = [float(v) for v in z[:NC]]
    s = sum(z13)
    z13 = [v/s for v in z13]
    prev = eng.get_eos()
    try:
        eng.set_eos(eos)
        r = eng.calcular(z13, T*1.8, P/PSI_PA, kij=kij, metodo_densidad='EOS')
    finally:
        eng.set_eos(prev)
    V = float(r.get('V') or 0.0)
    M = sum(z13[i]*eng.crit_props(eos)[3][i] for i in range(NC))
    Z = r.get('ZV') if V > 1e-9 else r.get('ZL')
    Z = float(Z)
    rho = P*M/1000.0/(Z*R_SI*T)
    mu = r.get('mu_v') if V > 1e-9 else r.get('mu_l')
    return dict(rho=rho, Z=Z, M=M, V=V, mu=(float(mu)*1e-3 if mu else None))


def fraccion_vapor(z, T, P, eos, kij):
    """Fracción de vapor del flash PT con la ecuación de estado (sin agua);
    None si no se puede evaluar."""
    try:
        return _props_eos(z, T, P, eos, kij)['V']
    except Exception:
        return None


def z_aire_base(Tb, Pb):
    return a8.propiedades(Tb, Pb/1000.0, _AIRE)['Z']


# ── Coeficiente de descarga de Reader-Harris/Gallagher (tomas bridadas) ──
def cd_rhg(beta, ReD, D):
    """Cd para tomas bridadas (AGA 3 Parte 1, ec. 1-7…1-13).  D en m."""
    D_in = D/IN_M
    L1 = L2 = 1.0/D_in                       # N4/D, N4 = 1 in
    M1 = max(2.8 - D_in, 0.0)
    M2 = 2.0*L2/(1.0 - beta)
    A = (19000.0*beta/ReD)**0.8
    B = beta**4/(1.0 - beta**4)
    C = (1.0e6/ReD)**0.35
    ci_ct = 0.5961 + 0.0291*beta**2 - 0.2290*beta**8 + 0.003*(1.0 - beta)*M1
    up = (0.0433 + 0.0712*math.exp(-8.5*L1) - 0.1145*math.exp(-6.0*L1))*(1.0 - 0.23*A)*B
    dn = -0.0116*(M2 - 0.52*M2**1.3)*beta**1.1*(1.0 - 0.14*A)
    ci_ft = ci_ct + up + dn
    return ci_ft + 0.000511*(1.0e6*beta/ReD)**0.7 + (0.0210 + 0.0049*A)*beta**4*C


def factor_expansion(beta, x1, k, metodo='1992'):
    """Y referido a la toma aguas arriba; x1 = ΔP/P1."""
    if metodo == 'ISO':
        return 1.0 - (0.351 + 0.256*beta**4 + 0.93*beta**8)*(1.0 - (1.0 - x1)**(1.0/k))
    return 1.0 - (0.41 + 0.35*beta**4)*x1/k


# ── Motor ────────────────────────────────────────────────────────────────
class Medidor:
    """Cálculo de un medidor de orificio.  spec (SI):
       z (14), d_ref, D_ref, alfa_d, alfa_D (1/K), T_ref, T_f, P_f (Pa abs en
       la toma), toma ('arriba'|'abajo'), dP, Pb, Tb, z_metodo ('AGA8'|'EOS'|
       'MANUAL'), eos, kij, Zf_man, Zb_man, y_metodo ('1992'|'ISO'),
       k_metodo ('FIJO'|'AGA8'), k_val, mu_metodo ('FIJO'|'EOS'), mu_val."""

    def __init__(self, spec):
        self.s = spec
        self._cache = {}
        z = spec['z']
        self.M_aga8 = a8.masa_molar(_x_aga8(z))
        sb = self._densidad(spec['Tb'], spec['Pb'], base=True)
        self.base = sb
        Zair = z_aire_base(spec['Tb'], spec['Pb'])
        rho_air = spec['Pb']*M_AIRE/1000.0/(Zair*R_SI*spec['Tb'])
        self.Z_aire = Zair
        self.Gr = sb['rho']/rho_air
        self.Gi = sb['M']/M_AIRE

    def _densidad(self, T, P, base=False):
        key = (round(T, 6), round(P, 3), base)
        if key in self._cache:
            return self._cache[key]
        s = self.s; m = s['z_metodo']
        if m == 'EOS':
            p = _props_eos(s['z'], T, P, s['eos'], s['kij'])
            p['kappa'] = None
        else:
            p = _props_aga8(s['z'], T, P)
            if m == 'MANUAL':
                Z = s['Zb_man'] if base else s['Zf_man']
                p['Z'] = Z
                p['rho'] = P*p['M']/1000.0/(Z*R_SI*T)
        self._cache[key] = p
        return p

    def _kappa(self, T, P):
        s = self.s
        if s.get('k_metodo') == 'AGA8':
            return _props_aga8(s['z'], T, P)['kappa']
        return s.get('k_val') or K_DEFECTO

    def _mu(self, T, P):
        s = self.s
        if s.get('mu_metodo') == 'EOS':
            try:
                mu = _props_eos(s['z'], T, P, s['eos'], s['kij'])['mu']
                if mu:
                    return mu
            except Exception:
                pass
        return s.get('mu_val') or MU_DEFECTO

    def evaluar(self, d_ref, dP, modelo):
        """Resultados del medidor para un diámetro de orificio y una ΔP."""
        s = self.s
        Tf = s['T_f']
        if modelo == 'aga3':
            d = d_ref*(1.0 + s['alfa_d']*(Tf - s['T_ref']))
            D = s['D_ref']*(1.0 + s['alfa_D']*(Tf - s['T_ref']))
        else:
            d = d_ref; D = s['D_ref']
        beta = d/D
        if not (0.0 < beta < 1.0):
            raise SinSolucionAGA3("La relación de diámetros β debe estar entre 0 y 1.")
        Ev = 1.0/math.sqrt(1.0 - beta**4)
        P1 = s['P_f'] if s['toma'] == 'arriba' else s['P_f'] + dP
        P2 = P1 - dP
        if P2 <= 0:
            raise SinSolucionAGA3("La presión diferencial supera la presión estática.")
        x1 = dP/P1
        f = self._densidad(Tf, P1)
        rho1 = f['rho']
        k = self._kappa(Tf, P1)
        mu = self._mu(Tf, P1)
        if modelo == 'aga3':
            Y = factor_expansion(beta, x1, k, s.get('y_metodo', '1992'))
        else:
            Y = 1.0
        base = (math.pi/4.0)*Ev*Y*d*d*math.sqrt(2.0*rho1*dP)
        if modelo == 'aga3':
            Cd = 0.6
            for _it in range(100):
                qm = Cd*base
                ReD = 4.0*qm/(math.pi*mu*D)
                Cn = cd_rhg(beta, ReD, D)
                if abs(Cn - Cd) < 1e-12:
                    Cd = Cn
                    break
                Cd = Cn
        else:
            Cd = 0.6
        qm = Cd*base
        ReD = 4.0*qm/(math.pi*mu*D) if qm > 0 else 0.0
        fd2 = self._densidad(Tf, P2) if s['toma'] == 'abajo' else None
        return dict(modelo=modelo, d=d, D=D, beta=beta, Ev=Ev, Y=Y, Cd=Cd,
                    qm=qm, ReD=ReD, x1=x1, P1=P1, P2=P2, rho1=rho1, Zf=f['Z'],
                    Zf2=(fd2['Z'] if fd2 else None), kappa=k, mu=mu,
                    Qf=qm/rho1, Qb=qm/self.base['rho'], d_ref=d_ref, dP=dP)

    def resolver(self, modelo):
        """Resuelve la incógnita elegida: 'Q' (caudal), 'dP' o 'd'."""
        s = self.s
        inc = s.get('calcular', 'Q')
        if inc == 'Q':
            return self.evaluar(s['d_ref'], s['dP'], modelo)
        qm_obj = s['qm_obj']
        if inc == 'dP':
            Pmax = s['P_f']*(0.95 if s['toma'] == 'arriba' else 20.0)
            g = lambda dp: self.evaluar(s['d_ref'], dp, modelo)['qm'] - qm_obj
            lo, hi = 1e-3, Pmax
            if s['toma'] == 'arriba':
                hi = s['P_f']*0.95
            if g(hi) < 0:
                raise SinSolucionAGA3("El caudal especificado no se alcanza con el orificio dado "
                                      "(presión diferencial excesiva).")
            x = _biseccion(g, lo, hi)
            return self.evaluar(s['d_ref'], x, modelo)
        # inc == 'd'
        g = lambda dd: self.evaluar(dd, s['dP'], modelo)['qm'] - qm_obj
        lo, hi = s['D_ref']*0.02, s['D_ref']*0.97
        if g(hi) < 0:
            raise SinSolucionAGA3("El caudal especificado requiere un orificio mayor que el tubo.")
        if g(lo) > 0:
            raise SinSolucionAGA3("El caudal especificado requiere un orificio demasiado pequeño.")
        x = _biseccion(g, lo, hi)
        return self.evaluar(x, s['dP'], modelo)


def _biseccion(g, lo, hi, tol=1e-12, nmax=200):
    """Raíz de g monótona creciente en [lo, hi] (bisección con secante)."""
    glo, ghi = g(lo), g(hi)
    if glo > 0:
        return lo
    for _ in range(nmax):
        x = lo - glo*(hi - lo)/(ghi - glo) if ghi != glo else 0.5*(lo + hi)
        if not (lo < x < hi) or (hi - lo) > 0.25*(abs(hi) + abs(lo)):
            x = 0.5*(lo + hi)
        gx = g(x)
        if abs(gx) < 1e-14 or (hi - lo) < tol*max(1.0, abs(x)):
            return x
        if gx < 0:
            lo, glo = x, gx
        else:
            hi, ghi = x, gx
    return 0.5*(lo + hi)


def avisos(r, s):
    """Límites de aplicación de AGA 3 Parte 1 para el cálculo completo."""
    out = []
    D_in = r['D']/IN_M; d_in = r['d']/IN_M
    if not (0.1 <= r['beta'] <= 0.75):
        out.append("β fuera del intervalo 0.10 – 0.75 de AGA 3.")
    if r['ReD'] < 4000:
        out.append("Número de Reynolds menor que 4000.")
    if D_in < 2.0 - 1e-9:
        out.append("Diámetro del tubo menor que 2 in (50 mm).")
    if d_in < 0.45:
        out.append("Diámetro del orificio menor que 0.45 in (11.4 mm).")
    if r['x1'] > 0.2:
        out.append("ΔP/P₁ mayor que 0.2: el factor de expansión queda fuera de su intervalo.")
    return out


def calcular(spec):
    """Punto de entrada: devuelve dict con los dos modelos y datos comunes."""
    m = Medidor(spec)
    if spec.get('flujo_obj'):
        v, tipo = spec['flujo_obj']
        spec['qm_obj'] = v*m.base['rho'] if tipo == 'std' else v
    res = {}
    for modelo in ('aga3', 'simple'):
        try:
            res[modelo] = m.resolver(modelo)
        except SinSolucionAGA3 as ex:
            res[modelo] = None
            res['error_' + modelo] = str(ex)
    if res.get('aga3') is None and res.get('simple') is None:
        raise SinSolucionAGA3(res.get('error_aga3') or "Sin solución")
    s = spec
    ref = res['aga3'] or res['simple']
    V = None
    if not (s['z'][13] if len(s['z']) > 13 else 0):
        V = fraccion_vapor(s['z'], s['T_f'], ref['P1'], s['eos'], s['kij'])
    adv = avisos(res['aga3'], s) if res.get('aga3') else []
    if V is not None and V < 1.0 - 1e-6:
        adv.insert(0, "El gas no es monofásico en condiciones de flujo (la ecuación de "
                      "estado predice líquido); AGA 3 exige gas en una sola fase.")
    # Poder calorífico superior másico (GPA 2172) del gas seco
    hhv_mas = None
    try:
        import poder_calorifico as pc
        import eos as eng
        z13 = list(s['z'][:eng.NC])
        hhv_mas = pc.poder_calorifico_fase(z13).get('hhv_mas')     # BTU/lb
    except Exception:
        pass
    res.update(op='orificio', base=m.base, M=m.M_aga8, Gr=m.Gr, Gi=m.Gi,
               Z_aire=m.Z_aire, avisos=adv, V_flujo=V, hhv_mas=hhv_mas,
               calcular=s.get('calcular', 'Q'), z_metodo=s['z_metodo'],
               y_metodo=s.get('y_metodo', '1992'), spec=s)
    return res

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
INH2O_4C_PA = 249.08891      # pulgada de agua a 4 °C (39.2 °F), convención convencional
MU_DEFECTO = 0.010268e-3     # Pa·s (0.010268 cP, valor admitido por AGA 3)
K_DEFECTO = 1.3

# Coeficientes de dilatación lineal (1/°F) — AGA 3 Parte 1 (2012)
MATERIALES = [
    ('ss', "Acero inoxidable 304/316", 9.25e-6),
    ('ss304', "Acero inoxidable 304", 9.61e-6),
    ('ss316', "Acero inoxidable 316", 8.89e-6),
    ('monel', "Monel 400", 7.72e-6),
    ('cs', "Acero al carbono", 6.20e-6),
]
ALFA_F = {k: a for k, _n, a in MATERIALES}


class SinSolucionAGA3(ValueError):
    pass


# ── Densidad del gas ────────────────────────────────────────────────────
def _props_aga8(x, T, P):
    """x: composición AGA 8 (22 posiciones, índice 0 sin uso)."""
    p = a8.propiedades(T, P/1000.0, x)
    return dict(rho=p['rho'], Z=p['Z'], M=p['M'], kappa=p['kappa'])


# Índice AGA 8 → índice ThermoPhase (N2, CO2, C1, …, nC9)
_INV_TP = {k: i for i, k in enumerate(a8.MAPA_TP[:13])}


def z_thermophase(x):
    """Composición de 13 componentes de ThermoPhase desde el vector AGA 8;
    None si el gas contiene agua u otros componentes ajenos a ThermoPhase."""
    if any(x[k] > 1e-12 for k in range(1, 22) if k not in _INV_TP):
        return None
    z = [0.0]*13
    for k, i in _INV_TP.items():
        z[i] = x[k]
    s = sum(z)
    return [v/s for v in z] if s > 0 else None


# Poder calorífico superior ideal (Btu/ft³ a 60 °F y 14.696 psia, GPA 2145)
# de los componentes AGA 8 que no tiene ThermoPhase (el agua, base seca: 0)
_HHV_EXTRA = {14: 7742.9, 15: 324.2, 17: 320.5, 19: 637.1}


def hhv_masico(x):
    """Poder calorífico superior másico (Btu/lb) del gas seco."""
    import poder_calorifico as pc
    num = 0.0; xs = 0.0
    for k in range(1, 22):
        if k == 18 or x[k] <= 0:
            continue
        if k in _INV_TP:
            hv = pc.HHV_VOL[_INV_TP[k]]
        else:
            hv = _HHV_EXTRA.get(k, 0.0)
        num += x[k]*hv; xs += x[k]
    if xs <= 0:
        return None
    M = sum(x[k]*a8.MMi[k] for k in range(1, 22) if k != 18)/xs
    return (num/xs)*pc.VM_IDEAL/M


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


def fraccion_vapor(x, T, P, eos='PR'):
    """Fracción de vapor del flash PT con la ecuación de estado (gas sin
    agua ni componentes ajenos a ThermoPhase); None si no se evalúa."""
    z = z_thermophase(x)
    if z is None:
        return None
    try:
        import eos as eng
        return _props_eos(z, T, P, eos, eng.kij_base(eos))['V']
    except Exception:
        return None


def patm_elevacion(h_m):
    """Presión atmosférica (Pa) a la elevación h (m) por la atmósfera
    estándar (U.S. Standard Atmosphere 1976 / ISA, troposfera):
        P = 101325·(1 − 2.25577·10⁻⁵·h)^5.25588"""
    return 101325.0*(1.0 - 2.25577e-5*h_m)**5.25588


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
       x (22, AGA 8), d_ref, D_ref, alfa_d, alfa_D (1/K), T_ref_d, T_ref_D,
       T_f, P_f (Pa abs en la toma), toma ('arriba'|'abajo'), dP, Pb, Tb,
       z_metodo ('AGA8'|'MANUAL'), Zf_man, Zb_man, G_man (gravedad específica
       ideal), y_metodo ('1992'|'ISO'), k_metodo ('FIJO'|'AGA8'), k_val, mu_val.
       G_ing (opcional, con AGA8 o EOS): gravedad específica REAL ingresada
       (como la «Specific Gravity: Entered» de los computadores de flujo).
       Los factores Z siguen siendo los de la composición, pero la masa molar
       se toma de la gravedad ingresada, M = G_r·M_aire·Z_b/Z_aire; con ello
       ρ_f, ρ_b y el caudal corresponden a esa gravedad (F_gr = 1/√G_r)."""

    def __init__(self, spec):
        self.s = spec
        self._cache = {}
        x = spec['x']
        self.M_aga8 = (spec['G_man']*M_AIRE if spec['z_metodo'] == 'MANUAL'
                       else a8.masa_molar(x))
        self.fM = 1.0                   # escala de masa molar (G ingresada)
        sb = self._densidad(spec['Tb'], spec['Pb'], base=True)
        Zair = z_aire_base(spec['Tb'], spec['Pb'])
        rho_air = spec['Pb']*M_AIRE/1000.0/(Zair*R_SI*spec['Tb'])
        self.Z_aire = Zair
        self.Gr_comp = sb['rho']/rho_air          # de la composición
        G_ing = spec.get('G_ing')
        if G_ing and spec['z_metodo'] != 'MANUAL':
            M_ef = G_ing*M_AIRE*sb['Z']/Zair
            self.fM = M_ef/sb['M']
            self.M_aga8 = M_ef
            self._cache = {}
            sb = self._densidad(spec['Tb'], spec['Pb'], base=True)
        self.base = sb
        self.Gr = sb['rho']/rho_air
        self.Gi = sb['M']/M_AIRE

    def _densidad(self, T, P, base=False):
        key = (round(T, 6), round(P, 3), base)
        if key in self._cache:
            return self._cache[key]
        s = self.s
        if s['z_metodo'] == 'MANUAL':
            Z = s['Zb_man'] if base else s['Zf_man']
            M = self.M_aga8
            p = dict(Z=Z, M=M, rho=P*M/1000.0/(Z*R_SI*T), kappa=None)
        elif s['z_metodo'] == 'EOS':
            z = z_thermophase(s['x'])
            if z is None:
                raise SinSolucionAGA3("La ecuación de estado no admite agua ni componentes ajenos "
                                      "a ThermoPhase; use AGA 8.")
            p = _props_eos(z, T, P, s['eos'], s['kij'])
            p['kappa'] = None
        else:
            p = _props_aga8(s['x'], T, P)
        if self.fM != 1.0:
            p = dict(p); p['rho'] = p['rho']*self.fM; p['M'] = p['M']*self.fM
        self._cache[key] = p
        return p

    def _kappa(self, T, P):
        s = self.s
        if s.get('k_metodo') == 'AGA8' and s['z_metodo'] != 'MANUAL':
            return _props_aga8(s['x'], T, P)['kappa']
        return s.get('k_val') or K_DEFECTO

    def _mu(self, T, P):
        return self.s.get('mu_val') or MU_DEFECTO

    def evaluar(self, d_ref, dP, modelo):
        """Resultados del medidor para un diámetro de orificio y una ΔP."""
        s = self.s
        Tf = s['T_f']
        if modelo == 'aga3':
            d = d_ref*(1.0 + s['alfa_d']*(Tf - s['T_ref_d']))
            D = s['D_ref']*(1.0 + s['alfa_D']*(Tf - s['T_ref_D']))
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
    V = (fraccion_vapor(s['x'], s['T_f'], ref['P1'], s.get('eos', 'PR'))
         if s['z_metodo'] != 'MANUAL' else None)
    adv = avisos(res['aga3'], s) if res.get('aga3') else []
    if V is not None and V < 1.0 - 1e-6:
        adv.insert(0, "El gas no es monofásico en condiciones de flujo (la ecuación de "
                      "estado predice líquido); AGA 3 exige gas en una sola fase.")
    # Poder calorífico superior másico (GPA 2172) del gas seco
    hhv_mas = None
    if s['z_metodo'] != 'MANUAL':
        try:
            hhv_mas = hhv_masico(s['x'])                             # Btu/lb
        except Exception:
            pass
    res.update(op='orificio', base=m.base, M=m.M_aga8, Gr=m.Gr, Gi=m.Gi,
               Gr_comp=m.Gr_comp, G_ing=s.get('G_ing'),
               Z_aire=m.Z_aire, avisos=adv, V_flujo=V, hhv_mas=hhv_mas,
               calcular=s.get('calcular', 'Q'), z_metodo=s['z_metodo'],
               y_metodo=s.get('y_metodo', '1992'), spec=s)
    return res

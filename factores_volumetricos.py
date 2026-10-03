"""
factores_volumetricos.py — Factores volumétricos de formación (Bg, Bo, Bw) y
relaciones gas en solución (Rs del petróleo, Rsw del agua).

Condiciones estándar: 60 °F (519.67 °R) y 14.696 psia.

Bg — gas (fase vapor del flash)
    Volumen del gas a (P, T) entre su volumen como gas ideal a condiciones
    estándar:
        Bg = V(P,T) / V_sc = (Z·T/P)·(P_sc/T_sc)          [ft³/scf]
    con Z el factor de compresibilidad de la fase vapor (el que se reporta,
    incluido el traslado de Peneloux si está activo).

Bo y Rs — petróleo (fase líquida de hidrocarburos)
    La fase líquida a (P, T) se lleva a condiciones estándar con un flash
    directo de una etapa (procedimiento "flash a condiciones estándar" de
    PVTsim).  Por mol de líquido a (P, T):
        V_o(P,T) = PM_L / ρ_L                              (densidad elegida)
        V_STO    = β_L,sc · PM_L,sc / ρ_L,sc              (petróleo de tanque)
        Bo = V_o(P,T) / V_STO                              [bbl/STB]
        Rs = β_V,sc · 379.48 scf / (V_STO en bbl)          [scf/STB]
    Por encima del punto de burbuja la fase líquida es toda la mezcla y Bo
    crece al bajar la presión (expansión del líquido); en el punto de burbuja
    es máximo; por debajo, el gas liberado deja un líquido de menor volumen y
    Bo disminuye.

Bw y Rsw — agua (fase acuosa)
    La fase acuosa a (P, T) se lleva a condiciones estándar con un flash
    trifásico de su composición (Huron-Vidal).  Rsw es el gas liberado por
    barril de agua a condiciones estándar.  Los volúmenes de agua se calculan
    con la densidad del agua pura de IAPWS-IF97 (región 1, agua líquida),
    porque las ecuaciones cúbicas y COSTALD sobrestiman la expansión térmica
    del agua y darían Bw de 1.05–1.07 donde el valor real es ≈1.02.  El gas
    disuelto (<0.5 % molar) no se incluye en el volumen, como en las
    correlaciones de McCain:
        V_w(P,T) = x_H2O · 18.015 / ρ_IF97(P,T)
        V_w,sc   = β_W,sc · x_H2O,sc · 18.015 / ρ_IF97(sc)
        Bw = V_w(P,T) / V_w,sc                             [bbl/STB]
    Fuera del rango de IF97 (T > 662 °F) se usa la densidad del método
    elegido.

Las densidades del petróleo a condiciones estándar se calculan con el mismo
método de densidad del cálculo principal (EOS, COSTALD o Peneloux).
"""
import numpy as np
import eos as _e

T_SC = 519.67                    # °R (60 °F)
P_SC = 14.696                    # psia
V_SC = _e.R_GAS*T_SC/P_SC        # scf/lbmol de gas ideal (≈379.48)
FT3_BBL = 5.614583               # ft³ por barril


# ── IAPWS-IF97, región 1 (agua líquida) ────────────────────────────────────
_I1 = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4,
       4, 5, 8, 8, 21, 23, 29, 30, 31, 32]
_J1 = [-2, -1, 0, 1, 2, 3, 4, 5, -9, -7, -1, 0, 1, 3, -3, 0, 1, 3, 17, -4, 0,
       6, -5, -2, 10, -8, -11, -6, -29, -31, -38, -39, -40, -41]
_N1 = [0.14632971213167, -0.84548187169114, -0.37563603672040e1,
       0.33855169168385e1, -0.95791963387872, 0.15772038513228,
       -0.16616417199501e-1, 0.81214629983568e-3, 0.28319080123804e-3,
       -0.60706301565874e-3, -0.18990068218419e-1, -0.32529748770505e-1,
       -0.21841717175414e-1, -0.52838357969930e-4, -0.47184321073267e-3,
       -0.30001780793026e-3, 0.47661393906987e-4, -0.44141845330846e-5,
       -0.72694996297594e-15, -0.31679644845054e-4, -0.28270797985312e-5,
       -0.85205128120103e-9, -0.22425281908000e-5, -0.65171222895601e-6,
       -0.14340520931100e-12, -0.40516996860117e-6, -0.12734301741641e-8,
       -0.17424871230634e-9, -0.68762131295531e-18, 0.14478307828521e-19,
       0.26335781662795e-22, -0.11947622640071e-22, 0.18228094581404e-23,
       -0.93537087292458e-25]
LBFT3_KGM3 = 0.0624279606


def rho_agua_if97(T, P):
    """Densidad del agua líquida pura [lb/ft³] a (T °R, P psia) por IAPWS-IF97
    región 1.  None fuera de 273.15–623.15 K o 0–100 MPa."""
    T_K = T/1.8
    p = P*0.00689475729                       # MPa
    if not (273.15 <= T_K <= 623.15) or not (0 < p <= 100.0):
        return None
    pi = p/16.53
    tau = 1386.0/T_K
    gp = sum(-n*i*(7.1 - pi)**(i - 1)*(tau - 1.222)**j
             for n, i, j in zip(_N1, _I1, _J1))
    v = 0.461526*T_K*pi*gp/p/1000.0           # m³/kg
    return LBFT3_KGM3/v


def bg(Z, T, P):
    """Bg [ft³/scf] de una fase vapor con factor Z a (T °R, P psia)."""
    if not Z or Z <= 0 or not P or P <= 0:
        return None
    return Z*T/P*(P_SC/T_SC)


def _flash_sc_seco(x13, eos, kij, metodo):
    """Flash de una etapa a condiciones estándar de una composición HC.
    Devuelve (β_V, β_L, V_L molar [ft³/lbmol] del líquido)."""
    x = np.asarray(x13, dtype=float)[:_e.NC]
    if x.sum() <= 0:
        return None
    x = list(x/x.sum())
    prev = _e.get_eos()
    try:
        _e.set_eos(eos)
        k = kij if kij is not None else _e.kij_base(eos)
        r = _e.calcular(x, T_SC, P_SC, k, metodo_densidad=metodo)
    finally:
        _e.set_eos(prev)
    bL = r.get('L') or 0.0
    if bL <= 1e-9 or not r.get('rho_l') or not r.get('PM_l'):
        return (r.get('V') or 0.0), 0.0, None
    return (r.get('V') or 0.0), bL, r['PM_l']/r['rho_l']


def bo_rs(x, PM_L, rho_L, eos, kij=None, metodo='EOS'):
    """(Bo [bbl/STB], Rs [scf/STB]) de la fase líquida HC de composición x
    (13 o 14 comp.; el agua disuelta se descarta) con PM_L y ρ_L [lb/ft³] a
    las condiciones del flash."""
    if x is None or not PM_L or not rho_L:
        return None, None
    try:
        sc = _flash_sc_seco(x, eos, kij, metodo)
    except Exception:
        return None, None
    if sc is None or sc[1] <= 1e-9 or not sc[2]:
        return None, None
    bV, bL, vL = sc
    # el líquido a (P,T) se renormaliza sin agua: sus moles HC son la base
    xa = np.asarray(x, dtype=float)
    f_hc = float(xa[:_e.NC].sum()) if len(xa) > _e.NC else 1.0
    V_res = PM_L/rho_L                        # ft³ por lbmol de líquido (P,T)
    V_sto = f_hc*bL*vL                        # ft³ de petróleo de tanque
    Bo = V_res/V_sto
    Rs = f_hc*bV*V_SC/(V_sto/FT3_BBL)
    return Bo, Rs


def bw_rsw(w14, PM_W, rho_W, eos, metodo='EOS', T=None, P=None):
    """(Bw [bbl/STB], Rsw [scf/STB]) de la fase acuosa de composición w (14
    comp.) con PM_W y ρ_W [lb/ft³] a las condiciones del flash (T °R,
    P psia).  Con T y P el volumen del agua se toma de IAPWS-IF97."""
    if w14 is None or not PM_W or not rho_W:
        return None, None
    try:
        import flash_agua as _fa
        import propiedades_agua as _pa
        w = np.asarray(w14, dtype=float)
        w = w/w.sum()
        rt = _fa.flash_trifasico(w, T_SC, P_SC, eos=eos, metodo='hv')
        bW = rt.get('beta_W') or 0.0
        if bW <= 1e-9:
            return None, None
        md = metodo if metodo in ('EOS', 'COSTALD', 'Peneloux') else 'EOS'
        pr = _pa.propiedades_fases(rt, T_SC, P_SC, eos, metodo_densidad=md)
        q = pr.get('W') or {}
        if not q.get('rho') or not q.get('PM'):
            return None, None
        V_sc = bW*q['PM']/q['rho']                 # ft³ de agua a cond. estándar
        bgas = rt.get('beta_V') or 0.0
        Bw = (PM_W/rho_W)/V_sc
        r_res = rho_agua_if97(T, P) if (T and P) else None
        r_sc = rho_agua_if97(T_SC, P_SC)
        xw = rt.get('w')
        if r_res and r_sc and xw is not None:
            PMa = 18.01528
            V_res = w[_e.NC]*PMa/r_res
            V_sc = bW*float(xw[_e.NC])*PMa/r_sc
            Bw = V_res/V_sc
        Rsw = bgas*V_SC/(V_sc/FT3_BBL)
        return Bw, Rsw
    except Exception:
        return None, None

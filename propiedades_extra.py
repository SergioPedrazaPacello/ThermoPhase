# -*- coding: utf-8 -*-
"""
propiedades_extra.py — Propiedades adicionales del flash por fase, como las
reporta PVTsim: volumen molar, Cp, Cv, Cp/Cv, coeficiente de Joule-Thomson,
velocidad del sonido, conductividad térmica y tensiones superficial/
interfaciales.

Todas en unidades internas FIELD:
    vol_molar  ft³/lbmol        cp, cv   Btu/(lbmol·°F)      kappa  —
    jt         °F/psi           vel_sonido ft/s
    cond_term  Btu/(h·ft·°F)    tension*   dyn/cm (= mN/m)
"""
import numpy as np

R_GAS = 10.7316
_J_A_BTU = 1.0/4.1868                         # J/(mol·K) → Btu/(lbmol·°F)
_CBAR_A_FPSI = 1.8/14.503773773               # °C/bar → °F/psi
_MS_A_FTS = 1.0/0.3048
_MW_A_BTU = 0.5777893/1000.0                  # mW/(m·K) → Btu/(h·ft·°F)
_CM3_A_FT3 = 1.0/62.427960576                 # cm³/mol → ft³/lbmol
_LBFT3_A_MOLCM3 = 453.59237/28316.846592      # lbmol/ft³ → mol/cm³


def _conv(o):
    if not o:
        return {}
    return {'vol_molar': o['Vm']*_CM3_A_FT3,
            'cp': o['Cp']*_J_A_BTU, 'cv': o['Cv']*_J_A_BTU, 'kappa': o['kappa'],
            'jt': o['JT']*_CBAR_A_FPSI,
            'vel_sonido': (o['u']*_MS_A_FTS) if o.get('u') else None}


def _rho_molar_eos(Z_eos, T, P, c_pen, eos):
    """Densidad molar (mol/cm³) de la EOS con el traslado de Peneloux."""
    import eos as _e
    Ze = Z_eos - P*c_pen/(R_GAS*T)
    return P*_e.factor_rho(eos)/(Ze*R_GAS*T)*_LBFT3_A_MOLCM3


def bifasico(r, T, P, eos, kij=None):
    """Propiedades extra del flash sin agua (resultado de eos.calcular).
    Devuelve {'V': {...}, 'L': {...}, 'mezcla': {...}}."""
    import eos as _e
    import propiedades_termicas as _pt
    import conductividad_termica as _ct
    import tension_superficial as _ts
    pen = bool(r.get('peneloux'))
    out = {'V': {}, 'L': {}, 'mezcla': {}}
    rho_mol = {}
    for f, key, Zk, rk, pk, bk in (('V', 'y', 'ZV', 'rho_v', 'PM_v', 'V'),
                                   ('L', 'x', 'ZL', 'rho_l', 'PM_l', 'L')):
        if (r.get(bk) or 0) <= 1e-9 or r.get(key) is None:
            continue
        comp = list(r[key]); PM = r.get(pk)
        Z = r.get(Zk + '_eos') or r.get(Zk)
        cpen = _e.c_peneloux_mezcla(comp, eos) if pen else 0.0
        o = _conv(_pt.propiedades_fase(comp, T, P, Z, PM, eos, kij, cpen))
        rho = r.get(rk)
        try:
            Zd = P*PM*_e.factor_rho(eos)/(rho*R_GAS*T)
            k = _ct.conductividad_fase(comp, T, P, Zd, eos, f)
            o['cond_term'] = k*_MW_A_BTU if k is not None else None
        except Exception:
            pass
        try:
            rho_mol[f] = _rho_molar_eos(Z, T, P, cpen, eos)
        except Exception:
            pass
        out[f] = o
    if 'V' in rho_mol and 'L' in rho_mol:
        try:
            st = _ts.gas_liquido(r['x'], r['y'], rho_mol['L'], rho_mol['V'])
            out['V']['tension'] = out['L']['tension'] = st
        except Exception:
            pass
    V = r.get('V') or 0.0; L = r.get('L') or 0.0
    _mezcla(out, {'V': V, 'L': L})
    return out


def trifasico(rt, pr, T, P, eos, peneloux=False):
    """Propiedades extra del flash con agua (rt: flash trifásico; pr: salida
    de propiedades_agua.propiedades_fases).  Fases 'V', 'L', 'W'."""
    import eos as _e
    import flash_agua as _fa
    import propiedades_termicas as _pt
    import conductividad_termica as _ct
    import tension_superficial as _ts
    import agua_pura as _ap
    Tc14 = _fa._params_14(eos)[0]
    out = {'V': {}, 'L': {}, 'W': {}, 'mezcla': {}}
    rho_mol = {}; rho_g = {}
    for f, key, Zk, bk in (('V', 'y', 'Z_V', 'beta_V'), ('L', 'x', 'Z_L', 'beta_L'),
                           ('W', 'w', 'Z_W', 'beta_W')):
        if (rt.get(bk) or 0) <= 1e-9 or rt.get(key) is None or not pr.get(f):
            continue
        comp = list(rt[key]); PM = pr[f].get('PM'); Z = rt.get(Zk)
        cpen = _e.c_peneloux_mezcla(comp, eos) if peneloux else 0.0
        o = _conv(_pt.propiedades_fase(comp, T, P, Z, PM, eos, None, cpen))
        try:
            if f == 'W':
                k = _ap.conductividad_agua_mW(T, P)
            else:
                Zd = P*PM*_e.factor_rho(eos)/(pr[f]['rho']*R_GAS*T)
                k = _ct.conductividad_fase(comp, T, P, Zd, eos, f)
            o['cond_term'] = k*_MW_A_BTU if k is not None else None
        except Exception:
            pass
        try:
            rho_mol[f] = _rho_molar_eos(Z, T, P, cpen, eos)
            rho_g[f] = rho_mol[f]*PM
        except Exception:
            pass
        out[f] = o
    try:
        if 'V' in rho_mol and 'L' in rho_mol:
            st = _ts.gas_liquido(rt['x'], rt['y'], rho_mol['L'], rho_mol['V'])
            out['V']['tension'] = out['L']['tension'] = st
        if 'W' in rho_g:
            for f, key in (('V', 'y'), ('L', 'x')):
                if f in rho_g:
                    out[f]['tension_agua'] = _ts.agua_hc(rho_g['W'], rho_g[f], rt[key], Tc14, T)
    except Exception:
        pass
    _mezcla(out, {'V': rt.get('beta_V') or 0.0, 'L': rt.get('beta_L') or 0.0,
                  'W': rt.get('beta_W') or 0.0})
    return out


def _mezcla(out, beta):
    """Columna de la mezcla: Cp, Cv y volumen molar como promedio molar de las
    fases (como PVTsim); Cp/Cv del cociente de las medias."""
    m = {}
    for clave in ('cp', 'cv', 'vol_molar'):
        s = 0.0; ok = False
        for f, b in beta.items():
            v = out.get(f, {}).get(clave)
            if b > 1e-9:
                if v is None:
                    ok = False; break
                s += b*v; ok = True
        if ok:
            m[clave] = s
    if m.get('cp') and m.get('cv'):
        m['kappa'] = m['cp']/m['cv']
    out['mezcla'] = m

# -*- coding: utf-8 -*-
"""
Poder calorífico (valor calorífico) de mezclas de hidrocarburos.

Reporta cuatro propiedades para cada fase (vapor, líquido y mezcla):
    • HHV (bruto / superior) — el agua de combustión condensa a líquido
    • LHV (neto / inferior)  — el agua de combustión permanece como vapor
cada una en dos bases:
    • volumétrica  → BTU/pie³ (gas ideal a 60 °F y 14.696 psia)
    • másica       → BTU/lb

Método (idéntico al de la referencia GPSA / "Ingeniería de gas", ec. 164):

    VC_mezcla = Σ yᵢ · VCᵢ

donde VCᵢ es el valor calorífico volumétrico del componente puro en base
gas ideal (BTU/pie³ a 60 °F, 14.696 psia), tabulado por GPSA-87.

La ponderación por fracción MOLAR de la fase da directamente el valor
calorífico volumétrico de esa fase (BTU/pie³ de gas ideal). Para la base
MÁSICA se convierte pasando por la base molar:

    VC_molar = VC_vol · Vm            [BTU/lbmol]   (Vm = vol. molar gas ideal)
    VC_masico = VC_molar / PM_fase    [BTU/lb]

Consideraciones por fase:
    • Vapor  → composición y (del gas en equilibrio)
    • Líquido→ composición x (del líquido en equilibrio)
    • Mezcla → composición global z
El poder calorífico volumétrico se expresa siempre en base GAS IDEAL, de modo
que el valor del líquido es el que tendría su composición evaporada a gas
ideal (coherente con la convención de las tablas GPSA y con HYSYS).

N₂ y CO₂ no son combustibles: su valor calorífico es 0 (diluyen la mezcla).

Fuente de los datos por componente: GPSA-87, "Valor calorífico, 60 °F",
columna BTU/pie³ gas ideal a 14.696 psia (Neto y Bruto).
"""

import numpy as np

try:
    from eos import NC, PM as _PM_EOS
except Exception:                       # respaldo defensivo
    NC = 13
    _PM_EOS = [28.013, 44.01, 16.043, 30.07, 44.097, 58.124, 58.124,
               72.151, 72.151, 86.178, 100.205, 114.232, 128.259]

# ── Constante de gas y condiciones estándar ─────────────────────────────────
# R_GAS en psia·pie³/(lbmol·°R); T estándar 60 °F = 519.67 °R; P 14.696 psia.
R_GAS = 10.7316
T_STD = 519.67
P_STD = 14.696
# Volumen molar del gas ideal a 60 °F y 14.696 psia (≈ 379.48 pie³/lbmol).
VM_IDEAL = R_GAS * T_STD / P_STD

# ── Valor calorífico volumétrico por componente (BTU/pie³ gas ideal, 60 °F) ──
# Orden canónico: N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, nC5, C6, C7, C8, C9.
# LHV = "Neto"; HHV = "Bruto". Fuente: GPSA-87.
#   N₂  : no combustible → 0
#   CO₂ : no combustible → 0
#   C1  : 909.4  / 1010.0
#   C2  : 1618.7 / 1769.7
#   C3  : 2314.9 / 2516.1
#   iC4 : 3000.4 / 3251.9
#   nC4 : 3010.8 / 3262.3
#   iC5 : 3699.0 / 4000.9
#   nC5 : 3706.9 / 4008.9
#   C6  : 4403.8 / 4755.9   (n-hexano)
#   C7  : 5100.0 / 5502.5   (n-heptano)
#   C8  : 5796.1 / 6248.9   (n-octano)
#   C9  : 6493.2 / 6996.5   (n-nonano)
LHV_VOL = [
    0.0,      # N₂
    0.0,      # CO₂
    909.4,    # C1
    1618.7,   # C2
    2314.9,   # C3
    3000.4,   # iC4
    3010.8,   # nC4
    3699.0,   # iC5
    3706.9,   # nC5
    4403.8,   # C6
    5100.0,   # C7
    5796.1,   # C8
    6493.2,   # C9
]
HHV_VOL = [
    0.0,      # N₂
    0.0,      # CO₂
    1010.0,   # C1
    1769.7,   # C2   (GPA 2145-96 / ASTM D3588; GPSA-87 daba 1769.6)
    2516.1,   # C3
    3251.9,   # iC4
    3262.3,   # nC4
    4000.9,   # iC5
    4008.9,   # nC5
    4755.9,   # C6
    5502.5,   # C7
    6248.9,   # C8
    6996.5,   # C9
]


def _vc_volumetrico(frac):
    """Valor calorífico volumétrico (BTU/pie³ gas ideal) de una composición.

    frac: secuencia de fracciones molares (longitud NC). Devuelve (LHV, HHV)
    en BTU/pie³.  Σ yᵢ·VCᵢ (GPSA-87, ec. 164).
    """
    if frac is None:
        return None, None
    z = np.asarray(frac, dtype=float)
    s = z.sum()
    if s <= 0:
        return None, None
    z = z / s                                  # normalizar por seguridad
    lhv = float(np.dot(z, LHV_VOL[:len(z)]))
    hhv = float(np.dot(z, HHV_VOL[:len(z)]))
    return lhv, hhv


def poder_calorifico_fase(frac, PM=None):
    """Poder calorífico de una fase a partir de su composición molar.

    frac : fracciones molares de la fase (vapor→y, líquido→x, mezcla→z).
    PM   : peso molecular de la fase (lb/lbmol). Si se omite, se calcula desde
           la composición y los PM de los componentes.

    Devuelve un dict con:
        'hhv_vol', 'lhv_vol'  → BTU/pie³ (gas ideal, 60 °F, 14.696 psia)
        'hhv_mas', 'lhv_mas'  → BTU/lb
    Cualquier valor puede ser None si la composición no es utilizable.
    """
    lhv_vol, hhv_vol = _vc_volumetrico(frac)
    if lhv_vol is None:
        out = {'hhv_vol': None, 'lhv_vol': None, 'hhv_mas': None, 'lhv_mas': None}
        out.update(propiedades_gas_real(None))
        return out

    if PM is None:
        z = np.asarray(frac, dtype=float)
        s = z.sum()
        PM = float(np.dot(z / s, _PM_EOS[:len(z)])) if s > 0 else None

    # base másica: BTU/lb = (BTU/pie³ · pie³/lbmol) / (lb/lbmol)
    if PM and PM > 0:
        lhv_mas = lhv_vol * VM_IDEAL / PM
        hhv_mas = hhv_vol * VM_IDEAL / PM
    else:
        lhv_mas = hhv_mas = None

    out = {'hhv_vol': hhv_vol, 'lhv_vol': lhv_vol,
           'hhv_mas': hhv_mas, 'lhv_mas': lhv_mas}
    out.update(propiedades_gas_real(frac, PM))
    return out


# ── GPM — contenido líquido (riqueza) del gas, C3+ ──────────────────────────
# GPM = galones de líquido recuperables por cada 1000 pie³ (normales) de gas.
# Se calcula sobre la fase GAS (vapor). Fórmula (GPSA / "Ingeniería de gas",
# ec. 160):
#     GPM = Σ (1000 · yᵢ · galᵢ_por_lbmol) / Vm
# donde galᵢ_por_lbmol es el volumen de líquido (galones) que produce un lbmol
# del componente i (columna "gal/lbs.mol" de GPSA-87, densidad de líquido a
# 60 °F, 14.696 psia) y Vm es el volumen molar del gas ideal a 60 °F.
#
# Convención GPM C3+: se suman propano y componentes más pesados. Metano,
# etano, N₂ y CO₂ no se recuperan como líquido y quedan fuera (factor 0).
#
# Orden canónico: N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, nC5, C6, C7, C8, C9.
# Valores gal/lbmol (GPSA-87, componentes normales):
#   C3=10.433  iC4=12.386  nC4=11.937  iC5=13.853  nC5=13.712
#   C6(n-hexano)=15.571  C7(n-heptano)=17.464  C8(n-octano)=19.381
#   C9(n-nonano)=21.311
GAL_POR_LBMOL = [
    0.0,      # N₂   (no recuperable)
    0.0,      # CO₂  (no recuperable)
    0.0,      # C1   (fuera de C3+)
    0.0,      # C2   (fuera de C3+)
    10.433,   # C3
    12.386,   # iC4
    11.937,   # nC4
    13.853,   # iC5
    13.712,   # nC5
    15.571,   # C6
    17.464,   # C7
    19.381,   # C8
    21.311,   # C9
]


def gpm_c3(frac):
    """GPM (galones por 1000 pie³ de gas) de la fase, componentes C3+.

    frac: fracciones molares de la fase GAS (vapor). Devuelve el GPM en
    gal/1000 pie³, o None si la composición no es utilizable.
    """
    if frac is None:
        return None
    z = np.asarray(frac, dtype=float)
    s = z.sum()
    if s <= 0:
        return None
    z = z / s
    gpm = float(np.dot(z, GAL_POR_LBMOL[:len(z)])) * 1000.0 / VM_IDEAL
    return gpm


# ══════════════════════════════════════════════════════════════════════════
#  BASE GAS REAL (GPA 2172 / ASTM D3588, constantes GPA 2145)
# ══════════════════════════════════════════════════════════════════════════
# El gas real a 60 °F y 14.696 psia no es ideal: 1 pie³ "real" contiene 1/Z
# veces los moles de 1 pie³ ideal, por eso
#     HHV_real = HHV_ideal / Z            G_real = G_ideal · Z_aire / Z_gas
# con Z de la mezcla por factores de sumatoria (GPA 2172):
#     Z = 1 − P_b · (Σ xᵢ·√bᵢ)²           P_b = 14.696 psia
# Base HÚMEDA: el gas se considera saturado con agua a 60 °F y 14.696 psia
# (x_w = P_v,agua/P_b = 0.25636/14.696 = 0.017444); el agua no aporta calor
# (base bruta) pero diluye el gas y entra en Z con su factor de sumatoria.
# Orden: N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, nC5, nC6, nC7, nC8, nC9.
SUMATORIA_RAIZ_B = [0.0044, 0.0197, 0.0116, 0.0239, 0.0344, 0.0458, 0.0478,
                    0.0581, 0.0631, 0.0802, 0.0944, 0.1137, 0.1331]
SUMATORIA_RAIZ_B_AGUA = 0.0623
SUMATORIA_RAIZ_B_AIRE = 0.0050
Z_AIRE = 1.0 - P_STD*SUMATORIA_RAIZ_B_AIRE**2          # 0.9996326
PV_AGUA_60F = 0.25636                                    # psia
X_AGUA_SAT = PV_AGUA_60F/P_STD                           # 0.017444
PM_AIRE = 28.9625


def z_estandar(frac, x_agua=0.0):
    """Z del gas a 60 °F y 14.696 psia por factores de sumatoria (GPA 2172).
    `frac`: composición seca (13 comp.); `x_agua`: fracción de agua agregada."""
    z = np.asarray(frac, dtype=float)
    s = z.sum()
    if s <= 0:
        return None
    z = z/s*(1.0 - x_agua)
    sb = float(np.dot(z, SUMATORIA_RAIZ_B[:len(z)])) + x_agua*SUMATORIA_RAIZ_B_AGUA
    return 1.0 - P_STD*sb*sb


PM_AGUA = 18.0153


def propiedades_gas_real(frac, PM=None):
    """Todas las combinaciones del poder calorífico y la gravedad específica.

    Volumétricas [BTU/pie³ a 60 °F, 14.696 psia]  (superior e inferior):
        ideal seca   = Σxᵢ·HVᵢ
        ideal húmeda = Σxᵢ·HVᵢ · (1 − x_w)
        real seca    = ideal seca / Z
        real húmeda  = ideal seca · (1 − x_w) / Z_sat
    Másicas [BTU/lb] (no dependen de ideal/real: no hay pie³):
        seca   = HV_molar / PM
        húmeda = HV_molar·(1 − x_w) / [PM·(1 − x_w) + 18.0153·x_w]
    """
    lhv, hhv = _vc_volumetrico(frac) if frac is not None else (None, None)
    claves = ('hhv_vol_hum', 'lhv_vol_hum', 'hhv_real', 'lhv_real', 'hhv_hum',
              'lhv_real_hum', 'hhv_mas_hum', 'lhv_mas_hum', 'sg_ideal', 'sg_real')
    if hhv is None:
        return {k: None for k in claves}
    z = np.asarray(frac, dtype=float); z = z/z.sum()
    if PM is None:
        PM = float(np.dot(z, _PM_EOS[:len(z)]))
    xw = X_AGUA_SAT
    Zs = z_estandar(z)
    Zh = z_estandar(z, xw)
    g_id = PM/PM_AIRE
    pm_hum = PM*(1.0 - xw) + PM_AGUA*xw
    return {'hhv_vol_hum': hhv*(1.0 - xw), 'lhv_vol_hum': lhv*(1.0 - xw),
            'hhv_real': hhv/Zs, 'lhv_real': lhv/Zs,
            'hhv_hum': hhv*(1.0 - xw)/Zh, 'lhv_real_hum': lhv*(1.0 - xw)/Zh,
            'hhv_mas_hum': hhv*VM_IDEAL*(1.0 - xw)/pm_hum if PM > 0 else None,
            'lhv_mas_hum': lhv*VM_IDEAL*(1.0 - xw)/pm_hum if PM > 0 else None,
            'sg_ideal': g_id, 'sg_real': g_id*Z_AIRE/Zs}


# Claves que se muestran por fase y para la mezcla (base composición).
CLAVES_PCAL = ('hhv_vol', 'hhv_vol_hum', 'hhv_real', 'hhv_hum',
               'lhv_vol', 'lhv_vol_hum', 'lhv_real', 'lhv_real_hum',
               'hhv_mas', 'hhv_mas_hum', 'lhv_mas', 'lhv_mas_hum')

# Combinaciones que SOLO tienen sentido para la fase gas.  La base REAL corrige
# con el Z del gas a condiciones estándar y la base HÚMEDA supone el gas
# saturado con agua a 60 °F: ambas describen un gas, no un líquido ni una
# mezcla bifásica.  Para el líquido y la mezcla quedan solo las bases ideal
# seca (volumétrica, como si se vaporizara) y másica seca.
CLAVES_SOLO_GAS = ('hhv_vol_hum', 'hhv_real', 'hhv_hum',
                   'lhv_vol_hum', 'lhv_real', 'lhv_real_hum',
                   'hhv_mas_hum', 'lhv_mas_hum')


def clave_liq_mezcla(key):
    """True si la clave de poder calorífico se muestra en líquido y mezcla."""
    return key in CLAVES_PCAL and key not in CLAVES_SOLO_GAS

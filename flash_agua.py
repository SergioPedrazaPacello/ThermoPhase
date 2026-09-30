# -*- coding: utf-8 -*-
"""
Flash trifásico vapor–líquido(HC)–acuoso para mezclas con agua.

Método "Simple (HYSYS)": el agua entra como un componente más en la regla de
mezcla cuadrática clásica de la EOS (PR o SRK), con los parámetros de
interacción binaria (kij) grandes que HYSYS usa para el agua. Esos kij grandes
(≈0.5 con hidrocarburos) hacen que la EOS prediga la inmiscibilidad agua-HC, de
modo que el análisis de estabilidad detecta y separa la fase acuosa. No se
requiere Huron-Vidal para obtener las tres fases (ver módulo huron_vidal.py
para el método riguroso de PVTsim, a implementar aparte).

El componente agua es el índice 13 (14° componente), tras C9.

Referencia de parámetros: paquete de fluidos HYSYS (PR y SRK), matriz kij con
el agua extraída del reporte de HYSYS.

Este módulo es AUTOCONTENIDO: replica la matemática de PR/SRK para 14
componentes sin tocar el motor de 13 componentes de eos.py, de modo que el
flash sin agua sigue intacto.
"""

import numpy as np

R_GAS = 10.7316
SQRT2 = np.sqrt(2.0)
IDX_AGUA = 13

# Constantes internas de PVTsim (ver _ai_bi).
PSIA_ATM_PVT = 14.696          # conversión psia→atm que usa PVTsim
PSIA_ATM_STD = 14.69594878     # la usada para pasar las Pc de la base a psia
OMEGA_A_PR_EXACTO = 0.4572355289   # Ωa de PR exacto (PVTsim)


# ── Propiedades críticas extendidas (13 HC + agua) ──────────────────────────
# Los 13 primeros se toman de eos.py según la EOS; el agua se añade aquí con las
# propiedades de HYSYS (Tc=1165.14°R, Pc=3208.23 psia, ω=0.344, PM=18.0151).
AGUA_TC   = 1165.13822021484     # °R
AGUA_PC   = 3208.233924          # psia
AGUA_OMEGA = 0.34400001168251
AGUA_PM   = 18.015100479126

# ω que usa SRK para el agua en HYSYS (COSTALD/SRK acentricity de la hoja).
# Para el flash SRK se usa el ω estándar del agua salvo indicación contraria;
# HYSYS reporta un "SRK acentricity" propio pero el m de SRK se calcula del ω.
AGUA_OMEGA_SRK = 0.34400001168251


# ── Fila kij del agua (fila/columna 14) ──────────────────────────────────────
# Orden: N₂, CO₂, C1, C2, C3, iC4, nC4, iC5, nC5, nC6, nC7, nC8, nC9 (agua-agua=0).
# Con el agua activa las 4 EOS usan el MISMO procedimiento (el de PVTsim): regla
# de mezcla Huron-Vidal para agua con N₂..nC6 (energías G0/GT/α de PVTsim, de la
# EOS correspondiente) y regla CLÁSICA con este kij para agua con nC7..nC9.
# Cada familia de EOS conserva sus propios kij:
#   • PVTsim  → fila del agua de la matriz clásica de PVTsim (hoja PARAMETROS).
#   • HYSYS   → fila del agua del paquete de fluidos de HYSYS (reporte HYSYS).
KIJ_AGUA_PVT_PR = [
    -0.48, 0.0952, 0.45, 0.45, 0.53, 0.52, 0.52, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
KIJ_AGUA_PVT_SRK = [
    -0.48, 0.10,   0.45, 0.45, 0.53, 0.52, 0.52, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
KIJ_AGUA_HYSYS_PR = [
    -0.3156, 0.0445, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.48, 0.5, 0.5, 0.5, 0.5]
KIJ_AGUA_HYSYS_SRK = [
    -0.4907, 0.0392, 0.5, 0.5, 0.4819, 0.518, 0.518, 0.5, 0.5, 0.5109, 0.5, 0.5, 0.5]
# Alias retro-compatibles (PVTsim).
KIJ_AGUA_PR = KIJ_AGUA_PVT_PR
KIJ_AGUA_SRK = KIJ_AGUA_PVT_SRK


def kij_agua_fila(eos):
    """Fila kij agua-HC (13 valores) de la EOS indicada (HYSYS o PVTsim)."""
    import eos as _e
    if _e.es_pvtsim(eos):
        return KIJ_AGUA_PVT_SRK if _e.es_srk(eos) else KIJ_AGUA_PVT_PR
    return KIJ_AGUA_HYSYS_SRK if _e.es_srk(eos) else KIJ_AGUA_HYSYS_PR

# Coeficientes Mathias-Copeman (c1,c2,c3) de PVTsim para alpha(T).
# Coeficientes Mathias-Copeman (C1,C2,C3) EXACTOS de la base de datos de PVTsim
# (ComponentParams: MCparams1-3; fuente Dahl 1991).  Orden N₂..nC9, H₂O.
MC_PR = [
    [0.5427000, -0.0524000, -0.3381000],
    [0.8653000, -0.4386000, 1.3447000],
    [0.5857000, -0.7206000, 1.2898999],
    [0.7178000, -0.7644000, 1.6396000],
    [0.7863000, -0.7459000, 1.8454000],
    [0.2400000, 3.8360000, -8.0450001],
    [0.8787000, -0.9399000, 2.2665999],
    [0.8282290, 0.0000000, 0.0000000],
    [1.0280000, -2.5620000, 6.2480001],
    [1.0827000, -1.2797000, 2.6177001],
    [-0.1620000, 6.2420001, -8.8260002],
    [1.0736001, 0.0656000, -0.2720000],
    [1.1365000, 0.0786000, -0.3464000],
    [1.0872999, -0.6377000, 0.6345000],
]

MC_SRK = [
    [0.5427000, -0.0524000, -0.3381000],
    [0.8653000, -0.4386000, 1.3447000],
    [0.5857000, -0.7206000, 1.2898999],
    [0.7178000, -0.7644000, 1.6396000],
    [0.7863000, -0.7459000, 1.8454000],
    [0.2400000, 3.8360000, -8.0450001],
    [0.8787000, -0.9399000, 2.2665999],
    [0.8282290, 0.0000000, 0.0000000],
    [1.0280000, -2.5620000, 6.2480001],
    [1.0827000, -1.2797000, 2.6177001],
    [-0.1620000, 6.2420001, -8.8260002],
    [1.0736001, 0.0656000, -0.2720000],
    [1.1365000, 0.0786000, -0.3464000],
    [1.0872999, -0.6377000, 0.6345000],
]




# ── Matriz kij HC-HC de PVTsim (13×13, sin agua) ────────────────────────────
# PVTsim usa su PROPIA base de kij binarios (Knapp et al. 1982), distinta de la
# que ThermoPhase usa para el flash sin agua (nivel HYSYS).  Cuando el agua está
# activa (método HV = PVTsim oficial), el equilibrio HC debe usar los kij de
# PVTsim para reproducir el reparto vapor/líquido exacto; de lo contrario el
# cociente de fugacidades fV/fL de los HC no cierra (difería hasta 3× para los
# pesados).  Extraídos de la hoja PARAMETROS de PVTsim (matriz clásica).
# Orden interno: N₂,CO₂,C1,C2,C3,iC4,nC4,iC5,nC5,nC6,nC7,nC8,nC9.
KIJ_HC_PVT_PR = [
    [0.0000, 0.0311, 0.0515, 0.0852, 0.1033, 0.0800, 0.0922, 0.1000, 0.1496, 0.1441, 0.0800, 0.0800, 0.0000],
    [0.0311, 0.0000, 0.1200, 0.1200, 0.1200, 0.1200, 0.1200, 0.1200, 0.1200, 0.1000, 0.1000, 0.1000, 0.0000],
    [0.0515, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0352, 0.0496, 0.0474, 0.0000],
    [0.0852, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0067, 0.0185, 0.0000, 0.0000],
    [0.1033, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0056, 0.0000, 0.0000, 0.0000],
    [0.0800, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0922, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0033, 0.0000, 0.0000, 0.0000],
    [0.1000, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.1496, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0074, 0.0000, 0.0000, 0.0000],
    [0.1441, 0.1000, 0.0352, 0.0067, 0.0056, 0.0000, 0.0033, 0.0000, 0.0074, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0800, 0.1000, 0.0496, 0.0185, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0800, 0.1000, 0.0474, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
]
KIJ_HC_PVT_SRK = [
    [0.0000, 0.0278, 0.0407, 0.0763, 0.0944, 0.0700, 0.0867, 0.0878, 0.1496, 0.1422, 0.0800, 0.0800, 0.0000],
    [0.0278, 0.0000, 0.1200, 0.1200, 0.1200, 0.1200, 0.1200, 0.1200, 0.1200, 0.1100, 0.1000, 0.1000, 0.0000],
    [0.0407, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0307, 0.0448, 0.0448, 0.0000],
    [0.0763, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0041, 0.0170, 0.0000, 0.0000],
    [0.0944, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0044, 0.0000, 0.0000, 0.0000],
    [0.0700, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0867, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, -0.0004, 0.0000, 0.0000, 0.0000],
    [0.0878, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.1496, 0.1200, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0019, -0.0022, 0.0000, 0.0000],
    [0.1422, 0.1100, 0.0307, 0.0041, 0.0044, 0.0000, -0.0004, 0.0000, 0.0019, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0800, 0.1000, 0.0448, 0.0170, 0.0000, 0.0000, 0.0000, 0.0000, -0.0022, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0800, 0.1000, 0.0448, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
    [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
]


# ── Propiedades críticas de PVTsim (14 componentes, incluye agua) ───────────
# PVTsim usa su propia base de propiedades críticas, que difiere de la de HYSYS
# en varios componentes (CO₂, C1, iC5, nC6…), hasta ~9 psia en Pc.  En método HV
# (motor PVTsim oficial) deben usarse estas para que a_i, b_i y α(T) — y por
# tanto el equilibrio de fases — coincidan exactamente con PVTsim.  Orden
# interno N₂..nC9, H₂O.  Fuente: hoja PARAMETROS de PVTsim (Tc °R, Pc psia).
# Valores EXACTOS de la base de datos de PVTsim (precisión completa; los HC se
# toman de eos.TC_PVT/PC_PVT/… y el agua de eos.AGUA_* para no duplicar cifras).
import eos as _eos_mod
TC_PVT_14    = list(_eos_mod.TC_PVT)    + [_eos_mod.AGUA_TC]
PC_PVT_14    = list(_eos_mod.PC_PVT)    + [_eos_mod.AGUA_PC]
OMEGA_PVT_14 = list(_eos_mod.OMEGA_PVT) + [_eos_mod.AGUA_OMEGA]
PM_PVT_14    = list(_eos_mod.PM_PVT)    + [_eos_mod.AGUA_PM]


def _params_14(eos):
    """Devuelve (Tc, Pc, omega, PM, kij) de 14 componentes para la EOS dada.
    Los 13 HC se toman de eos.py; el agua se añade en el índice 13.

    En método HV (agua activa, motor PVTsim) se usan las propiedades críticas
    y la matriz kij de PVTsim (TC/PC/OMEGA_PVT_14, KIJ_HC_PVT_*), no las del
    flash sin agua, para reproducir el equilibrio exacto de PVTsim."""
    import eos as _e
    es_srk = _e.es_srk(eos)
    es_pvt = _e.es_pvtsim(eos)

    # Propiedades críticas de 14 comp. según la EOS ELEGIDA:
    #  • EOS PVTsim  → arreglos de PVTsim (reproduce el flash PVTsim exacto).
    #  • EOS HYSYS   → Tc/Pc/ω de HYSYS + agua.  El método HV (regla de mezcla +
    #    matrices agua-gas G0/GT/α del Excel) se aplica IGUAL sobre estas props,
    #    de modo que "el método PVTsim corre también con las EOS de HYSYS" —
    #    resultado coherente con la EOS elegida, distinto de PVTsim puro pero
    #    físicamente fundamentado.
    # Con una EOS de PVTsim se usan SIEMPRE las propiedades de PVTsim (incluida
    # el agua), sin depender del estado global _METODO: antes, si _METODO aún no
    # era 'hv' al pedir los parámetros, el agua tomaba Tc/Pc de HYSYS (Pc 3208.23
    # vs 3203.72 psia) y desplazaba ~0.07 °R las líneas con fase acuosa.
    if es_pvt:
        Tc = np.array(TC_PVT_14, dtype=float)
        Pc = np.array(PC_PVT_14, dtype=float)
        om = np.array(OMEGA_PVT_14, dtype=float)
        PM = np.array(PM_PVT_14, dtype=float)
    else:
        if es_pvt:
            Tc13 = list(_e.TC_PVT); Pc13 = list(_e.PC_PVT)
            om13 = list(_e.OMEGA_PVT); PM13 = list(_e.PM_PVT)
        elif es_srk:
            Tc13 = list(_e.TC_SRK); Pc13 = list(_e.PC_SRK)
            om13 = list(_e.OMEGA_SRK); PM13 = list(_e.PM)
        else:
            Tc13 = list(_e.TC); Pc13 = list(_e.PC)
            om13 = list(_e.OMEGA); PM13 = list(_e.PM)
        Tc = np.array(Tc13 + [AGUA_TC])
        Pc = np.array(Pc13 + [AGUA_PC])
        om = np.array(om13 + [AGUA_OMEGA_SRK if es_srk else AGUA_OMEGA])
        PM = np.array(PM13 + [AGUA_PM])

    # kij HC-HC 13×13: SIEMPRE la matriz base de la EOS (kij_base), que para
    # PVTsim es la matriz exacta de su base de datos (validada componente a
    # componente).  [Antes, en modo HV se usaba KIJ_HC_PVT_PR, que estaba
    # desplazada un índice y desajustaba el equilibrio V/L de los HC — por eso
    # el HV daba peor resultado que el clásico incluso en mezclas sin agua.]
    kij13 = np.array(_e.kij_base(eos), dtype=float)
    kij = np.zeros((14, 14))
    kij[:13, :13] = kij13
    fila = kij_agua_fila(eos)
    for j in range(13):
        kij[13, j] = fila[j]
        kij[j, 13] = fila[j]
    return Tc, Pc, om, PM, kij


def _m_pr(omega):
    return 0.37464 + 1.54226*omega - 0.26992*omega**2

def _m_srk(omega):
    return 0.480 + 1.574*omega - 0.176*omega**2


def _ai_bi(eos, Tc, Pc, omega, T):
    """Parámetros a_i·α(T) y b_i para los 14 componentes.

    Con el EOS de PVTsim se usa la dependencia térmica de Mathias-Copeman (M&C)
    con los coeficientes (C1,C2,C3) de la base de datos de PVTsim (tomados de
    Dahl, 1991), que es lo que PVTsim aplica realmente — sus MC están poblados
    para todos los componentes y difieren de m(ω).  M&C reproduce la presión de
    vapor de cada componente (incluida el agua) y, con ello, la solubilidad
    mutua agua-HC que la α estándar no capturaba.  Fórmula (manual PVTsim, EOS):
        α(T) = [1 + C1(1-√Tr) + C2(1-√Tr)² + C3(1-√Tr)³]²   (Tr<1)
        α(T) = [1 + C1(1-√Tr)]²                              (Tr≥1)
    Con los EOS de HYSYS se mantiene la α estándar de PR/SRK."""
    import eos as _e
    es_srk = _e.es_srk(eos)
    es_pvt = _e.es_pvtsim(eos)
    if es_pvt:
        # PVTsim trabaja internamente en atm y convierte la presión del usuario
        # con 1 atm = 14.696 psia (manual: "1 atm/14.696 psia"), mientras que las
        # Pc de su base están en atm.  Nuestras Pc en psia se obtuvieron con
        # 14.69594878; para reproducir el cociente P/Pc de PVTsim se re-escalan
        # a Pc_atm·14.696.  Confirmado con los volúmenes molares de la corrida
        # PRUEBA: V = Z·R·T/P con R = 0.08206 L·atm/(mol·K) y P = psia/14.696
        # reproduce el volumen reportado a 8e-8.
        Pc = Pc*(PSIA_ATM_PVT/PSIA_ATM_STD)
    # Constantes Ωa/Ωb por EOS (verificadas contra las corridas PRUEBA de
    # PVTsim a 500 psia, 300-750 °R, y coherentes con el motor sin agua de HYSYS):
    #   PR  PVTsim : Ωa EXACTO 0.4572355289, Ωb 0.07780 (redondeado).  Con
    #                Ωa=0.45724 el error máx. en fracción molar era 1.6e-5; así,
    #                1.7e-7 (Ωb exacto lo empeora a 5e-5).
    #   SRK PVTsim : Ωa y Ωb EXACTOS (0.42748023354 / 0.08664034996).  Con los
    #                truncados 0.42748/0.08664 el error era 2.8e-6; así, 1.8e-7.
    #   PR  HYSYS  : 0.45724 / 0.07780 (como eos.ai_pr / eos.bi_pr).
    #   SRK HYSYS  : exactos (como eos.OMEGA_A_SRK / OMEGA_B_SRK).
    if es_srk:
        ai = _e.OMEGA_A_SRK*R_GAS**2*Tc**2/Pc
        b0 = _e.OMEGA_B_SRK
    elif es_pvt:
        ai = OMEGA_A_PR_EXACTO*R_GAS**2*Tc**2/Pc
        b0 = 0.07780
    else:
        ai = 0.45724*R_GAS**2*Tc**2/Pc
        b0 = 0.07780
    bi = b0*R_GAS*Tc/Pc

    # α de Soave/PR estándar para todos los componentes.  (Se evaluó Mathias-
    # Copeman para el agua con los coeficientes de la base de datos: con el HV
    # corregido empeora el reparto, porque su α del agua resulta ~4 % mayor que
    # la estándar, en dirección opuesta a la esperada; se mantiene la estándar,
    # que da el mejor calce con el HV de Pedersen 2001.)
    m = _m_srk(omega) if es_srk else _m_pr(omega)
    alpha = (1.0 + m*(1.0 - np.sqrt(T/Tc)))**2
    return ai*alpha, bi


# Método de mezcla para el agua: 'simple' (kij Classic) o 'hv' (Huron-Vidal).
# Lo fija flash_trifasico según la opción elegida. Contexto para HV.
_METODO = 'simple'
_EOS_CTX = 'PR'
_T_CTX = None

def _am_bm(z, aa, bi, kij):
    """Regla de mezcla: cuadrática (Simple) o Huron-Vidal según _METODO.
    Con _METODO='hv' y agua presente usa las energías de PVTsim; en ausencia de
    agua HV se reduce exactamente a la cuadrática."""
    z = np.asarray(z, dtype=float)
    if _METODO == 'hv' and _T_CTX is not None and len(z) > IDX_AGUA and z[IDX_AGUA] > 1e-12:
        import huron_vidal as _hv
        try:
            return _hv.am_bm_hv(z, aa, bi, _EOS_CTX, _T_CTX, kij)
        except Exception:
            pass
    saa = np.sqrt(aa)
    w = z*saa
    am = float(w @ (1.0 - kij) @ w)
    bm = float(z @ bi)
    return am, bm


def _Z_roots(am, bm, T, P, es_srk):
    """Raíces de compresibilidad Z de la EOS cúbica."""
    A = am*P/(R_GAS*T)**2
    B = bm*P/(R_GAS*T)
    if es_srk:
        c = [1.0, -1.0, A - B - B*B, -A*B]
    else:
        c = [1.0, -(1.0 - B), A - 3*B*B - 2*B, -(A*B - B*B - B**3)]
    Zs = sorted(z_ for z_ in _raices_cubica(c[1], c[2], c[3]) if z_ > B)
    return Zs, A, B


def _raices_cubica(a2, a1, a0):
    """Raíces reales de Z³ + a2 Z² + a1 Z + a0 = 0 (analítico + 2 pasos de
    Newton para pulir; equivalente a np.roots pero ~20× más rápido)."""
    import math
    q = (3.0*a1 - a2*a2)/9.0
    r = (9.0*a2*a1 - 27.0*a0 - 2.0*a2**3)/54.0
    D = q**3 + r*r
    if D > 0:
        sD = math.sqrt(D)
        s1 = math.copysign(abs(r + sD)**(1.0/3.0), r + sD)
        s2 = math.copysign(abs(r - sD)**(1.0/3.0), r - sD)
        roots = [s1 + s2 - a2/3.0]
    else:
        th = math.acos(max(-1.0, min(1.0, r/math.sqrt(-q**3)))) if q < 0 else 0.0
        sq = 2.0*math.sqrt(-q) if q < 0 else 0.0
        roots = [sq*math.cos(th/3.0) - a2/3.0,
                 sq*math.cos((th + 2.0*math.pi)/3.0) - a2/3.0,
                 sq*math.cos((th + 4.0*math.pi)/3.0) - a2/3.0]
    out = []
    for z_ in roots:
        for _ in range(2):
            f = ((z_ + a2)*z_ + a1)*z_ + a0
            d = (3.0*z_ + 2.0*a2)*z_ + a1
            if d == 0:
                break
            z_ -= f/d
        out.append(z_)
    return out


def _sum_aij_deriv(z, aa, bi, kij, am):
    """Vector 'sum_aij' que entra en ln(phi): representa la derivada parcial
    del término atractivo. Con la regla cuadrática es saa·((1-kij)@w). Con
    Huron-Vidal (activo vía _METODO) usa la derivada ANALÍTICA qbar de am_HV,
    que es termodinámicamente consistente y ~15× más rápida que la numérica.

    ln_phi usa 2·sum_aij/am; qbar = (1/am)·∂(n²am)/∂n_i, así que
    sum_aij_i = am·qbar_i/2.
    """
    z = np.asarray(z, dtype=float)
    if _METODO == 'hv' and _T_CTX is not None and len(z) > IDX_AGUA and z[IDX_AGUA] > 1e-12:
        import huron_vidal as _hv
        am2, bm2, qbar = _hv._am_qbar_hv(z, aa, bi, _EOS_CTX, _T_CTX, kij, con_qbar=True)
        # qbar = 2·dn2am/am ; sum_aij = dn2am = am·qbar/4 (factor validado vs
        # derivada numérica de (n²am)).
        return am2*qbar/4.0
    saa = np.sqrt(aa)
    w = z*saa
    return saa*((1.0 - kij) @ w)


def _ln_phi_conZ(z, aa, bi, kij, T, P, es_srk, Z):
    """ln(phi_i) dado un Z específico."""
    am, bm = _am_bm(z, aa, bi, kij)
    A = am*P/(R_GAS*T)**2
    B = bm*P/(R_GAS*T)
    z = np.asarray(z, dtype=float)
    sum_aij = _sum_aij_deriv(z, aa, bi, kij, am)
    bi_bm = bi/bm
    t1 = bi_bm*(Z - 1.0)
    t2 = -np.log(max(Z - B, 1e-15))
    if es_srk:
        t3 = (A/max(B,1e-15))*np.log((Z + B)/Z)
    else:
        num = Z + (1+SQRT2)*B; den = Z + (1-SQRT2)*B
        t3 = A/(2*SQRT2*B)*np.log(num/max(den,1e-15))
    t4 = (2.0*sum_aij/am - bi_bm)*t3
    return t1 + t2 - t4


def _ln_phi(z, aa, bi, kij, T, P, es_srk, fase):
    """ln(phi_i) de los 14 componentes.
    fase: 'V' toma la raíz Z mayor; 'L' la menor; 'auto' la de MENOR energía de
    Gibbs (la fase termodinámicamente estable en esas condiciones)."""
    am, bm = _am_bm(z, aa, bi, kij)
    Zs, A, B = _Z_roots(am, bm, T, P, es_srk)
    if not Zs:
        return None, None
    if fase == 'auto' and len(Zs) > 1:
        z = np.asarray(z, dtype=float)
        mask = z > 1e-300
        best = None; bestG = None
        for Zc in (Zs[0], Zs[-1]):
            lnp = _ln_phi_conZ(z, aa, bi, kij, T, P, es_srk, Zc)
            G = float(np.sum(z[mask]*(np.log(z[mask]) + lnp[mask])))
            if bestG is None or G < bestG:
                bestG = G; best = (lnp, Zc)
        return best
    Z = Zs[-1] if fase == 'V' else Zs[0]
    return _ln_phi_conZ(z, aa, bi, kij, T, P, es_srk, Z), Z


def _K_wilson(Tc, Pc, omega, T, P):
    return (Pc/P)*np.exp(5.373*(1+omega)*(1 - Tc/T))


def _tpd_estable(z, aa, bi, kij, T, P, es_srk, lnphi_z, w_ini):
    """Análisis de estabilidad de Michelsen (Tangent Plane Distance).
    Comprueba si la fase de composición z es estable frente a la aparición de
    una fase de prueba iniciada en w_ini. Devuelve (estable, w_conv) donde
    estable=False indica que z es INESTABLE (aparece la fase w_conv).

    lnphi_z: ln(phi_i) de la fase z (referencia). Se busca un mínimo de la
    distancia al plano tangente; si TPD < 0 → inestable.
    """
    d = np.log(np.clip(z,1e-300,None)) + lnphi_z    # potencial de referencia
    W = np.clip(w_ini, 1e-300, None)
    for _ in range(80):
        w = W/np.sum(W)
        lnp_w, _ = _ln_phi(w, aa, bi, kij, T, P, es_srk, 'auto')
        if lnp_w is None:
            return True, None
        lnW_new = d - lnp_w                          # ln W_i = d_i - ln phi_i(w)
        W_new = np.exp(lnW_new)
        if np.max(np.abs(np.log(np.clip(W_new,1e-300,None)/np.clip(W,1e-300,None)))) < 1e-10:
            W = W_new; break
        W = W_new
    Sw = np.sum(W)
    w = W/Sw
    # TPD* = 1 - Σ W_i (criterio de Michelsen); inestable si Σ W_i > 1
    tm = 1.0 - Sw
    estable = tm > -1e-8
    return estable, w


# ── Flash trifásico vapor–líquido(HC)–acuoso ────────────────────────────────
def flash_trifasico(z, T, P, eos='PR', metodo='simple', max_iter=400, tol=1e-11):
    """Flash isotérmico-isobárico multifásico por el método de Michelsen (1994):
    minimización de la función Q(beta), robusta ante fases que aparecen o
    desaparecen. metodo: 'simple' (kij Classic, HYSYS) o 'hv' (Huron-Vidal,
    PVTsim). Devuelve dict con beta_V, beta_L, beta_W, y, x, w y factores Z."""
    global _METODO, _EOS_CTX, _T_CTX
    _METODO = 'hv' if metodo == 'hv' else 'simple'
    _EOS_CTX = eos; _T_CTX = T
    z = np.asarray(z, dtype=float); z = z/z.sum()
    Tc, Pc, om, PM, kij = _params_14(eos)
    import eos as _e
    es_srk = _e.es_srk(eos)
    aa, bi = _ai_bi(eos, Tc, Pc, om, T)

    def lnphi(comp, fase='auto'):
        return _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)

    # Sin agua: flash bifásico HC estándar.
    if z[IDX_AGUA] <= 1e-12:
        y,x,bV,ZV,ZL = _flash_vl(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om)
        return _pack(bV,1-bV,0.0,y,x,np.zeros(14),ZV,ZL,None,PM,1)

    Kw = _K_wilson(Tc, Pc, om, T, P)
    # Composiciones iniciales de las 3 fases:
    #   Vapor: enriquecido en ligeros (z·Kw)
    #   Líquido HC: enriquecido en pesados (z/Kw), sin agua
    #   Acuosa: agua casi pura
    y0 = np.clip(z*Kw, 1e-300, None); y0/=y0.sum()
    x0 = np.clip(z/Kw, 1e-300, None); x0[IDX_AGUA]=1e-8; x0/=x0.sum()
    w0 = np.full(14, 1e-8); w0[IDX_AGUA]=1.0; w0/=w0.sum()

    roles = ['V', 'L', 'L']       # vapor, líquido HC, acuosa
    res = _flash_multifase(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om,PM,
                           roles, [y0, x0, w0], max_iter, tol)
    if res is None:
        # respaldo: flash bifásico
        y,x,bV,ZV,ZL = _flash_vl(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om)
        return _pack(bV,1-bV,0.0,y,x,np.zeros(14),ZV,ZL,None,PM,1)

    beta, comps, Zs = res
    # Si la tercera fase NO resultó acuosa (mínimo local: a T muy baja el HC
    # puede separarse en dos líquidos y "atrapar" la semilla de agua), se
    # reintenta con cuatro fases (V, L, L2, acuosa) y se reagrupan las fases
    # HC para no perder el agua del balance de materia.
    if comps[2][IDX_AGUA] < 0.5:
        x0b = np.clip(z*np.sqrt(Kw), 1e-300, None); x0b[IDX_AGUA] = 1e-8
        x0b /= x0b.sum()
        res4 = _flash_multifase(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om,PM,
                                ['V', 'L', 'L', 'L'], [y0, x0, x0b, w0],
                                max_iter, tol)
        if res4 is not None:
            b4, c4, Z4 = res4
            iaq = [j for j in range(4) if b4[j] > 1e-10 and c4[j][IDX_AGUA] > 0.5]
            ihc = [j for j in range(4) if b4[j] > 1e-10 and j not in iaq]
            if iaq:
                bW_ = sum(b4[j] for j in iaq)
                w_ = sum(b4[j]*c4[j] for j in iaq)/bW_
                # fases HC ordenadas por densidad molar (menos densa = V)
                def _dens(j):
                    lp_, Zj = _ln_phi(c4[j], aa,bi,kij,T,P,es_srk, ['V','L','L','L'][j])
                    return (P/(Zj*T)) if Zj else 0.0
                ihc.sort(key=_dens)
                if len(ihc) == 0:
                    beta = np.array([0.0, 0.0, bW_]); comps = [np.zeros(14), np.zeros(14), w_]
                    Zs = [None, None, Z4[iaq[0]]]
                elif len(ihc) == 1:
                    j = ihc[0]
                    beta = np.array([b4[j], 0.0, bW_]); comps = [c4[j], np.zeros(14), w_]
                    Zs = [Z4[j], None, Z4[iaq[0]]]
                else:
                    jv = ihc[0]; jl = ihc[1:]
                    bLl = sum(b4[j] for j in jl)
                    xl = sum(b4[j]*c4[j] for j in jl)/bLl
                    beta = np.array([b4[jv], bLl, bW_]); comps = [c4[jv], xl, w_]
                    Zs = [Z4[jv], Z4[jl[-1]], Z4[iaq[0]]]
    bV, bL, bW = beta[0], beta[1], beta[2]
    y, x, w = comps[0], comps[1], comps[2]
    ZV, ZL, ZW = Zs[0], Zs[1], Zs[2]

    # Si el líquido HC colapsó (β_L despreciable), el flash de 3 fases puede
    # dejar una fase L espuria que descuadra el balance de materia del agua.
    # Se re-resuelve con las 2 fases reales (vapor + acuosa) para un balance
    # exacto, que es lo físico cuando el HC no condensa.
    if bL < 1e-4 and bW > 1e-4:
        res2 = _flash_multifase(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om,PM,
                                ['V','L'], [y0, w0], max_iter, tol)
        if res2 is not None:
            b2, c2, Z2 = res2
            if c2[1][IDX_AGUA] > 0.5 and b2[0] > 1e-4:
                bV, bW, bL = b2[0], b2[1], 0.0
                y, w, x = c2[0], c2[1], np.zeros(14)
                ZV, ZW, ZL = Z2[0], Z2[1], None

    # Verificación de consistencia: si la fase "acuosa" no es rica en agua o la
    # fase "líquido HC" contiene demasiada agua, el flash cayó en un mínimo
    # local con clasificación errónea. Se reintenta descartando el líquido HC
    # (2 fases: vapor + acuosa), que es la solución física a alta T.
    if bL > 1e-5 and (w[IDX_AGUA] < 0.5 or x[IDX_AGUA] > 0.3):
        res2 = _flash_multifase(z, aa,bi,kij,T,P,es_srk,Tc,Pc,om,PM,
                                ['V','L'], [y0, w0], max_iter, tol)
        if res2 is not None:
            b2, c2, Z2 = res2
            if c2[1][IDX_AGUA] > 0.5:      # la 2ª fase es acuosa
                bV, bW = b2[0], b2[1]; bL = 0.0
                y, w = c2[0], c2[1]; x = np.zeros(14)
                ZV, ZW = Z2[0], Z2[1]; ZL = None

    # ── Fusionar fases acuosas duplicadas ───────────────────────────────────
    # Si el "líquido HC" (x) resultó rico en agua, es en realidad una segunda
    # fase acuosa espuria: se fusiona con la acuosa (w) para que el balance de
    # agua cierre. Sin esto, el flash puede "perder" agua al desaparecer el
    # líquido HC cerca del punto de rocío del HC.
    UMB = 1e-5
    if bL > 0 and x[IDX_AGUA] > 0.5:
        if bW > 0:
            b_ac = bL + bW
            w = (bL*x + bW*w)/b_ac; w = w/w.sum()
            bW = b_ac
        else:
            bW = bL; w = x
        bL = 0.0; x = np.zeros(14)

    # Descartar fases despreciables (beta ~ 0) — Michelsen ec. 11.
    # ¿la "acuosa" es realmente acuosa?
    if w[IDX_AGUA] < 0.5 and bW >= UMB:
        # la "acuosa" no es rica en agua: es otra fase HC → se une al líquido
        # HC (nunca se descarta masa del balance)
        if bL > 0:
            x = (bL*x + bW*w)/(bL + bW); x = x/x.sum(); bL = bL + bW
        else:
            x = w; bL = bW; ZL = ZW
        bW = 0.0
    elif bW < UMB:
        bW = 0.0
    if bV < UMB: bV = 0.0
    if bL < UMB: bL = 0.0

    # Si vapor y líquido HC colapsaron a la misma fase (composiciones iguales),
    # es una sola fase HC: reagrupar.
    if bV > UMB and bL > UMB:
        if np.max(np.abs(y - x)) < 1e-3:   # misma composición → una fase HC
            # unir en la de mayor Z (vapor) si Z alto, o líquido si bajo
            b_hc = bV + bL
            hc = (bV*y + bL*x)/b_hc; hc/=hc.sum()
            es_vap = _es_vapor(hc, aa,bi,kij,T,P,es_srk, Tc)
            if es_vap:
                bV, y, ZV = b_hc, hc, ZV; bL = 0.0
            else:
                bL, x, ZL = b_hc, hc, ZL; bV = 0.0

    # Si solo queda una fase HC (la otra colapsó), reconciliar con el flash VL
    # directo del HC (más confiable que el multifase cuando una fase desaparece).
    # Esto corrige casos de transición donde el multifase clasifica mal V vs L.
    hc_unica = (bV > UMB) != (bL > UMB)   # exactamente una de las dos HC
    if hc_unica and bW < 1.0 - UMB:
        # composición HC (la fase presente)
        hc = y if bV > UMB else x
        b_hc = bV + bL
        # renormalizar HC quitando agua residual y re-flashear
        hc_n = hc.copy()
        s_hcn = hc_n.sum()
        if s_hcn > 0:
            hc_n = hc_n/s_hcn
            yh, xh, bVh, ZVh, ZLh = _flash_vl(hc_n, aa,bi,kij,T,P,es_srk,Tc,Pc,om)
            if bVh >= 1.0 - 1e-6:          # el HC es vapor
                bV, y, ZV = b_hc, hc_n, ZVh; bL = 0.0; x = np.zeros(14)
            elif bVh <= 1e-6:             # el HC es líquido
                bL, x, ZL = b_hc, hc_n, ZLh; bV = 0.0; y = np.zeros(14)
            else:                         # el HC se divide en V+L (3 fases)
                bV = b_hc*bVh; bL = b_hc*(1-bVh)
                y, x, ZV, ZL = yh, xh, ZVh, ZLh

    # Si solo queda una fase HC, identificar V o L por Z (respaldo).
    # Al cambiar la etiqueta se toma la raíz de Z que corresponde a la nueva
    # fase (menor para líquido, mayor para vapor).
    if bV > UMB and bL <= UMB:
        if not _es_vapor(y, aa,bi,kij,T,P,es_srk, Tc):
            bL, x = bV, y; bV = 0.0; y = np.zeros(14)
            ZL = _ln_phi(x, aa,bi,kij,T,P,es_srk,'L')[1]
    elif bL > UMB and bV <= UMB:
        if _es_vapor(x, aa,bi,kij,T,P,es_srk, Tc):
            bV, y = bL, x; bL = 0.0; x = np.zeros(14)
            ZV = _ln_phi(y, aa,bi,kij,T,P,es_srk,'V')[1]

    s = bV+bL+bW
    if s>0: bV/=s; bL/=s; bW/=s
    return _pack(bV, bL, bW,
                 y if bV>0 else np.zeros(14),
                 x if bL>0 else np.zeros(14),
                 w if bW>0 else np.zeros(14),
                 ZV if bV>0 else None, ZL if bL>0 else None,
                 ZW if bW>0 else None, PM, 1)


def _gibbs(comp, aa, bi, kij, T, P, es_srk, fase):
    lnp, Z = _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)
    if lnp is None: return None
    comp = np.asarray(comp); m = comp > 1e-300
    return float(np.sum(comp[m]*(np.log(comp[m]) + lnp[m])))


def _es_vapor(comp, aa, bi, kij, T, P, es_srk, Tc=None):
    """True si la fase de composición comp es vapor. Con dos raíces Z compara
    energía de Gibbs. Con una sola raíz (región densa/supercrítica) usa un
    criterio combinado: la temperatura pseudo-crítica de la mezcla (regla de
    Kay) y la densidad molar. Si T < Tpc la fase densa es líquida."""
    am, bm = _am_bm(comp, aa, bi, kij)
    Zs, A, B = _Z_roots(am, bm, T, P, es_srk)
    if not Zs:
        return True
    if len(Zs) > 1:
        gV = _gibbs(comp, aa,bi,kij,T,P,es_srk,'V')
        gL = _gibbs(comp, aa,bi,kij,T,P,es_srk,'L')
        return gV is not None and (gL is None or gV <= gL)
    # raíz única (fase densa): combinar Z, densidad y Tpc de la mezcla.
    Z = Zs[0]
    v = Z*R_GAS*T/P
    # Un factor de compresibilidad alto es propio de una fase gaseosa aunque la
    # regla de Kay dé T<Tpc (p.ej. mezclas ricas en CO₂/C1 a baja T, donde Tpc
    # sube pero la fase sigue siendo vapor).  Z≥0.5 ⇒ vapor.
    if Z >= 0.5:
        return True
    if Tc is not None:
        comp = np.asarray(comp)
        Tpc = float(comp @ np.asarray(Tc))        # T pseudo-crítica (Kay)
        if T < Tpc:
            return False                          # por debajo de Tpc: líquido
    # sin Tc o T>=Tpc: por densidad. Líquido si empaquetamiento denso.
    return v > 3.0*bm


def _pack(bV,bL,bW,y,x,w,ZV,ZL,ZW,PM,it):
    return {'beta_V':bV,'beta_L':bL,'beta_W':bW,'y':y,'x':x,'w':w,
            'Z_V':ZV,'Z_L':ZL,'Z_W':ZW,'PM':PM,'iter':it}


def _Q_dist(beta, N, phi):
    """Función objetivo Q de Michelsen 1994 (ec. 4) y su gradiente/Hessiano.
    beta: fracciones molares de fase (F,). N: composición global (C,).
    phi: coeficientes de fugacidad (C,F). Devuelve (Q, grad, H, E)."""
    E = np.sum(beta[None,:]/phi, axis=1)          # E_i (ec. 5)
    E = np.where(E < 1e-300, 1e-300, E)
    Q = np.sum(beta) - np.sum(N*np.log(E))
    grad = 1.0 - np.sum((N/E)[:,None]/phi, axis=0)  # ec. 10
    F = len(beta)
    NE2 = N/E**2
    H = np.zeros((F,F))
    for j in range(F):
        for k in range(j,F):
            v = np.sum(NE2/(phi[:,j]*phi[:,k]))     # ec. 12
            H[j,k]=v; H[k,j]=v
    return Q, grad, H, E


def _distribucion_fases(N, phi, beta0):
    """Minimiza Q(beta) (Michelsen 1994) por Newton con línea de búsqueda y
    restricción beta>=0. Maneja automáticamente fases que aparecen/desaparecen.
    Devuelve (beta, y) con y las composiciones (C,F)."""
    beta = np.clip(np.asarray(beta0, dtype=float), 0, None)
    F = len(beta)
    for it in range(100):
        Q, g, H, E = _Q_dist(beta, N, phi)
        # Conjunto activo (condiciones KKT de min Q con β ≥ 0): una fase con
        # β = 0 y ∂Q/∂β ≥ 0 queda fija en cero y NO entra al paso de Newton.
        # (Incluirla daba direcciones malas cerca de fases que aparecen o
        # desaparecen: la búsqueda lineal recortaba el paso ~27 veces por
        # iteración y un flash llegaba a tardar 40 s.)
        act = (beta > 0.0) | (g < 0.0)
        if not np.any(act):
            break
        if np.max(np.abs(g[act])) < 1e-13:
            break
        ia = np.where(act)[0]
        d = np.zeros(F)
        try:
            d[ia] = np.linalg.solve(H[np.ix_(ia, ia)] + 1e-12*np.eye(len(ia)), g[ia])
        except Exception:
            break
        t = 1.0; mejor = False
        while t > 1e-8:
            nb = np.clip(beta - t*d, 0, None)
            Qn,_,_,_ = _Q_dist(nb, N, phi)
            if Qn <= Q + 1e-14:
                mejor = True; break
            t *= 0.5
        if not mejor:
            break
        nb = np.clip(beta - t*d, 0, None)
        if np.max(np.abs(nb-beta)) < 1e-13:
            beta = nb; break
        beta = nb
    E = np.sum(beta[None,:]/phi, axis=1)
    E = np.where(E < 1e-300, 1e-300, E)
    y = (N/E)[:,None]/phi                           # y_ij (ec. 7)
    return beta, y


def _flash_multifase(z, aa, bi, kij, T, P, es_srk, Tc, Pc, om, PM,
                     roles, comps0, max_iter=300, tol=1e-11):
    """Flash multifásico por el método de Michelsen 1994: sustitución sucesiva
    (actualiza fugacidades) + minimización de Q (actualiza distribución de
    fases). roles: lista de 'V'/'L' por fase. comps0: composiciones iniciales
    (lista de vectores C). Robusto: las fases sin presencia real convergen a
    beta≈0 y se descartan.

    Devuelve (beta, comps, Zs) o None si no converge de forma útil."""
    z = np.asarray(z, dtype=float)
    Fn = len(roles)
    comps = [np.clip(c,1e-300,None)/np.sum(c) for c in comps0]
    beta = np.array([1.0/Fn]*Fn)
    Zs = [None]*Fn
    for outer in range(max_iter):
        # fugacidades de cada fase con su rol (V o L)
        phi = np.zeros((14, Fn)); ok=True
        for j in range(Fn):
            lnp, Zj = _ln_phi(comps[j], aa,bi,kij,T,P,es_srk, roles[j])
            if lnp is None: ok=False; break
            # proteger contra overflow numérico (T criogénica extrema)
            lnp = np.clip(lnp, -700, 700)
            phi[:,j] = np.exp(lnp); Zs[j]=Zj
        if not ok: return None
        # distribución de fases minimizando Q
        beta_new, y = _distribucion_fases(z, phi, beta)
        # nuevas composiciones
        comps_new = []
        for j in range(Fn):
            c = np.clip(y[:,j], 0, None); s=c.sum()
            comps_new.append(c/s if s>0 else comps[j])
        # convergencia
        dif = max(np.max(np.abs(comps_new[j]-comps[j])) for j in range(Fn))
        comps = comps_new; beta = beta_new
        if dif < tol:
            break
    # normalizar beta
    s = beta.sum()
    if s>0: beta = beta/s
    return beta, comps, Zs


def _flash_vl(z, aa, bi, kij, T, P, es_srk, Tc, Pc, om, max_iter=200, tol=1e-12):
    """Flash bifásico vapor-líquido de 14 componentes sobre composición z.
    Devuelve (y, x, beta_V, Z_V, Z_L). Si es monofásico, beta_V es 0 ó 1.

    Antes de resolver Rachford-Rice se hace un análisis de estabilidad para
    detectar una fase líquida incipiente que Wilson por sí solo no captura cerca
    del punto de rocío (como PVTsim). Si el fluido es inestable, se arranca el
    flash desde las K de la fase de prueba de la estabilidad."""
    K = _K_wilson(Tc, Pc, om, T, P)

    # ── Estabilidad previa: ¿es z inestable (aparece líquido)? ──────────────
    lnp_z, _ = _ln_phi(z, aa, bi, kij, T, P, es_srk, 'auto')
    if lnp_z is not None:
        d = np.log(np.clip(z, 1e-300, None)) + lnp_z
        # semilla líquida (composición pesada): z/K
        W = np.clip(z/np.maximum(K, 1e-30), 1e-300, None)
        for _ in range(60):
            ww = W/np.sum(W)
            lnp_w, _ = _ln_phi(ww, aa, bi, kij, T, P, es_srk, 'auto')
            if lnp_w is None:
                break
            Wn = np.exp(d - lnp_w)
            if np.max(np.abs(np.log(np.clip(Wn,1e-300,None)/np.clip(W,1e-300,None)))) < 1e-10:
                W = Wn; break
            W = Wn
        if np.sum(W) > 1.0 + 1e-7:
            # inestable: la fase de prueba da mejores K de arranque
            w_trial = W/np.sum(W)
            K = np.clip(z, 1e-300, None)/np.clip(w_trial, 1e-300, None)

    def RR(bV):
        return np.sum(z*(K-1.0)/(1.0+bV*(K-1.0)))
    monofasico = None
    for it in range(max_iter):
        # resolver Rachford-Rice para beta_V
        lo, hi = 1e-9, 1.0-1e-9
        # chequear si hay dos fases
        if RR(0.0) < 0:      # burbuja: todo líquido
            bV = 0.0; monofasico = 'L'
        elif RR(1.0) > 0:    # rocío: todo vapor
            bV = 1.0; monofasico = 'V'
        else:
            monofasico = None
            for _ in range(100):
                mid = 0.5*(lo+hi)
                if RR(mid) > 0: lo = mid
                else: hi = mid
            bV = 0.5*(lo+hi)
        x = z/(1.0+bV*(K-1.0)); x = x/x.sum()
        y = K*x; y = y/y.sum()
        lnpV, Z_V = _ln_phi(y, aa, bi, kij, T, P, es_srk, 'V')
        lnpL, Z_L = _ln_phi(x, aa, bi, kij, T, P, es_srk, 'L')
        if lnpV is None or lnpL is None:
            break
        K_new = np.exp(lnpL - lnpV)
        err = np.max(np.abs(np.log(K_new/K)))
        K = K_new
        if err < tol:
            break
    # Para fluido monofásico, identificar vapor vs líquido por la energía de
    # Gibbs de las dos raíces de Z (la fase estable es la de menor G). Wilson no
    # es fiable para esto a alta presión, así que se usa el criterio de Gibbs.
    if monofasico is not None:
        gV = _gibbs_fase(z, aa, bi, kij, T, P, es_srk, 'V')
        gL = _gibbs_fase(z, aa, bi, kij, T, P, es_srk, 'L')
        if gV is not None and gL is not None:
            es_vapor = gV <= gL
        else:
            es_vapor = (monofasico == 'V')
        bV = 1.0 if es_vapor else 0.0
        y = z.copy(); x = z.copy()
    return y, x, bV, Z_V, Z_L


def _gibbs_fase(comp, aa, bi, kij, T, P, es_srk, fase):
    """Energía de Gibbs adimensional de una fase (Σ x_i ln(x_i phi_i)),
    para comparar estabilidad vapor vs líquido de un fluido monofásico."""
    lnp, Z = _ln_phi(comp, aa, bi, kij, T, P, es_srk, fase)
    if lnp is None:
        return None
    comp = np.asarray(comp)
    mask = comp > 1e-300
    return float(np.sum(comp[mask]*(np.log(comp[mask]) + lnp[mask])))




def identificar_fases_hc(rt, T, P, eos, kij13=None):
    """Identificación de las fases HC del flash con agua con el MISMO criterio
    del motor sin agua (PVTsim para sus EOS, HYSYS para las suyas):

    • Dos fases HC: la de menor densidad es el vapor (PVTsim).
    • Una sola fase HC: se clasifica como vapor o líquido con el flash del
      motor de 13 componentes sobre la composición HC de esa fase (sin agua),
      de modo que la etiqueta coincide con la que se obtiene sin agua.

    Modifica y devuelve `rt` (β, composiciones y Z de las fases V/L)."""
    import eos as _e
    bV = rt.get('beta_V', 0.0) or 0.0
    bL = rt.get('beta_L', 0.0) or 0.0
    if bV <= 0 and bL <= 0:
        return rt
    _METODO_prev = _METODO
    try:
        Tc, Pc, om, PM, kij = _params_14(eos)
        aa, bi = _ai_bi(eos, Tc, Pc, om, T)
        es_srk = _e.es_srk(eos)

        def Z_de(c, rol):
            _, Z = _ln_phi(np.asarray(c, dtype=float), aa, bi, kij, T, P, es_srk, rol)
            return Z

        if bV > 0 and bL > 0:
            y = np.asarray(rt['y'], dtype=float); x = np.asarray(rt['x'], dtype=float)
            # Dos fases HC "líquidas" (v/b < 2.5 en ambas) que el motor sin agua
            # ve como un único líquido estable: división espuria (T criogénica)
            # → se reúnen en una sola fase líquida (balance de materia intacto).
            def _vb(c, Z):
                am_, bm_ = _am_bm(c, aa, bi, kij)
                return (Z*R_GAS*T/P)/bm_ if (Z and bm_ > 0) else 99.0
            if _vb(y, rt['Z_V']) < 2.5 and _vb(x, rt['Z_L']) < 2.5:
                hc = (bV*y + bL*x)/(bV + bL)
                h13 = hc[:13]/hc[:13].sum()
                eos_prev = _e.get_eos()
                try:
                    _e.set_eos(eos)
                    k13 = kij13 if kij13 is not None else _e.kij_base(eos)
                    r = _e.calcular(list(h13), T, P, k13)
                finally:
                    _e.set_eos(eos_prev)
                if r['L'] >= 1.0 - 1e-9:
                    rt['x'], rt['y'] = hc, np.zeros(14)
                    rt['beta_L'], rt['beta_V'] = bV + bL, 0.0
                    rt['Z_L'], rt['Z_V'] = Z_de(hc, 'L'), None
                    return rt
            dv = float(np.dot(y, PM))/(rt['Z_V'] or 1.0)
            dl = float(np.dot(x, PM))/(rt['Z_L'] or 1.0)
            if dv > dl:                      # el "vapor" es el más denso → intercambiar
                rt['y'], rt['x'] = x, y
                rt['beta_V'], rt['beta_L'] = bL, bV
                rt['Z_V'], rt['Z_L'] = rt['Z_L'], rt['Z_V']
            return rt

        hc = np.asarray(rt['y'] if bV > 0 else rt['x'], dtype=float)
        b = bV if bV > 0 else bL
        h13 = hc[:13].copy(); s13 = h13.sum()
        if s13 <= 0:
            return rt
        h13 = h13/s13
        eos_prev = _e.get_eos()
        try:
            _e.set_eos(eos)
            k13 = kij13 if kij13 is not None else _e.kij_base(eos)
            r = _e.calcular(list(h13), T, P, k13)
        finally:
            _e.set_eos(eos_prev)
        if r['V'] >= 1.0 - 1e-9:
            es_v = True
        elif r['L'] >= 1.0 - 1e-9:
            es_v = False
        else:
            return rt                          # caso límite: se deja como está
        if es_v and bV <= 0:
            rt['y'], rt['x'] = hc, np.zeros(14)
            rt['beta_V'], rt['beta_L'] = b, 0.0
            rt['Z_V'], rt['Z_L'] = Z_de(hc, 'V'), None
        elif (not es_v) and bL <= 0:
            rt['x'], rt['y'] = hc, np.zeros(14)
            rt['beta_L'], rt['beta_V'] = b, 0.0
            rt['Z_L'], rt['Z_V'] = Z_de(hc, 'L'), None
        elif es_v:
            rt['Z_V'] = Z_de(hc, 'V')          # raíz coherente con la etiqueta
        else:
            rt['Z_L'] = Z_de(hc, 'L')
        return rt
    except Exception:
        return rt

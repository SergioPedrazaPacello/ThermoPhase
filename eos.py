"""
Motor Peng-Robinson — réplica EXACTA del Excel
Algoritmo: Análisis de Estabilidad Michelsen + Flash Muskat-McDowell
Determinación de fase única por criterio ΣKi·zi vs Σzi/Ki (mismo que Excel)
"""
import numpy as np
import copy
import math

R_GAS = 10.7316

COMPONENTES = ["N₂","CO₂","C1","C2","C3","iC4","nC4","iC5","nC5","C6","C7","C8","C9"]
NOMBRES = [
    "Nitrógeno [N₂]:",
    "Dióxido de carbono [CO₂]:",
    "Metano [C1]:",
    "Etano [C2]:",
    "Propano [C3]:",
    "Isobutano (2-metilpropano) [iC4]:",
    "n-Butano [nC4]:",
    "Isopentano (2-metilbutano) [iC5]:",
    "n-Pentano [nC5]:",
    "Hexano [C6]:",
    "Heptano [C7]:",
    "Octano [C8]:",
    "Nonano [C9]:"
]
PM = [28.013,44.0097,16.0429,30.0699,44.097,58.124,58.124,
      72.151,72.151,86.1779,100.205,114.232,128.259]
TC = [227.14920043945301,547.38001098632799,343.25820922851602,549.77041625976597,
      665.81641845703098,734.57281494140602,765.35820922851599,828.71641845703095,
      845.28001098632797,914.21641845703095,972.28443603515598,1023.47644042969,1070.27644042969]
PC = [492.31163474560498,1068.9278489999999,673.073579130908,708.34238530883795,
      617.37619874414099,529.04243227060499,550.65304957060505,483.49623909045403,
      489.51965902060499,439.69920907060498,396.93628085515098,362.10403957060498,333.59687255368698]
OMEGA = [3.9999801665544503e-2,0.23894000053405801,1.1498400010168599e-2,9.8600000143051106e-2,
         0.152400001883507,0.18479000031948101,0.20100000500678999,0.222240000963211,
         0.25389000773429898,0.30070000886917098,0.34979000687599199,0.401800006628037,0.445490002632141]
# Punto normal de ebullición (NBP), en °R. Usado por el criterio de
# identificación de fase supercrítica de HYSYS (umbral 230 K = 414°R):
# componentes con NBP < 230 K se consideran "livianos", el resto "pesados".
# Fuente: valores estándar de literatura (API / NIST), convertidos a Rankine.
NBP = [139.25,350.46,201.06,332.28,415.98,470.52,490.86,541.80,556.56,615.42,
       668.88,717.84,762.84]
# Matriz kij Peng-Robinson tal como HYSYS la reporta (default de PR).
KIJ_DEFAULT_PR = [
    [0,-1.9997e-2,3.5999e-2,5.0e-2,7.9998e-2,9.4999e-2,9.0e-2,9.4999e-2,0.1,0.149,0.1439,0.1,0.1],
    [-1.9997e-2,0,0.1,0.1298,0.135,0.1298,0.1298,0.125,0.125,0.125,0.1199,0.115,0.101],
    [3.5999e-2,0.1,0,2.2414e-3,6.8288e-3,1.3113e-2,1.2305e-2,1.7627e-2,1.7925e-2,2.3474e-2,2.8864e-2,3.4159e-2,3.8926e-2],
    [5.0e-2,0.1298,2.2414e-3,0,1.2580e-3,4.5735e-3,4.0964e-3,7.4133e-3,7.6094e-3,1.1414e-2,1.5324e-2,1.9319e-2,2.3017e-2],
    [7.9998e-2,0.135,6.8288e-3,1.2580e-3,0,1.0405e-3,8.1897e-4,2.5834e-3,2.7005e-3,5.1420e-3,7.8874e-3,1.0850e-2,1.3697e-2],
    [9.4999e-2,0.1298,1.3113e-2,4.5735e-3,1.0405e-3,0,1.3351e-5,3.4618e-4,3.9005e-4,1.5653e-3,3.2213e-3,5.2142e-3,7.2549e-3],
    [9.0e-2,0.1298,1.2305e-2,4.0964e-3,8.1897e-4,1.3351e-5,0,4.9514e-4,5.4723e-4,1.8663e-3,3.6464e-3,5.7502e-3,7.8831e-3],
    [9.4999e-2,0.125,1.7627e-2,7.4133e-3,2.5834e-3,3.4618e-4,4.9514e-4,0,1.2517e-6,4.3994e-4,1.4591e-3,2.8828e-3,4.4489e-3],
    [0.1,0.125,1.7925e-2,7.6094e-3,2.7005e-3,3.9005e-4,5.4723e-4,1.2517e-6,0,3.9345e-4,1.3733e-3,2.7618e-3,4.2986e-3],
    [0.149,0.125,2.3474e-2,1.1414e-2,5.1420e-3,1.5653e-3,1.8663e-3,4.3994e-4,3.9345e-4,0,2.9725e-4,1.0733e-3,2.0981e-3],
    [0.1439,0.1199,2.8864e-2,1.5324e-2,7.8874e-3,3.2213e-3,3.6464e-3,1.4591e-3,1.3733e-3,2.9725e-4,0,2.4128e-4,8.1754e-4],
    [0.1,0.115,3.4159e-2,1.9319e-2,1.0850e-2,5.2142e-3,5.7502e-3,2.8828e-3,2.7618e-3,1.0733e-3,2.4128e-4,0,1.7071e-4],
    [0.1,0.101,3.8926e-2,2.3017e-2,1.3697e-2,7.2549e-3,7.8831e-3,4.4489e-3,4.2986e-3,2.0981e-3,8.1754e-4,1.7071e-4,0]
]
NC = 13

# Matriz kij Soave-Redlich-Kwong extraída directamente de HYSYS.
# Fuente: reporte de Fluid Package HYSYS con paquete SRK, 13 componentes
# canonicos (N2, CO2, C1..C9). Simetrica; diagonal = 0.
KIJ_DEFAULT_SRK = [
    [0,-0.01710,0.03120,0.03190,0.08860,0.13150,0.05970,0.09300,0.09360,0.16500,0.07999,0.07999,0.07999],
    [-0.01710,0,0.09560,0.14010,0.13680,0.13680,0.14120,0.12970,0.13470,0.14200,0.10920,0.13500,0.13500],
    [0.03120,0.09560,0,0.00224,0.00683,0.01311,0.01230,0.01763,0.01793,0.02347,0.02886,0.03416,0.03893],
    [0.03190,0.14010,0.00224,0,0.00126,0.00457,0.00410,0.00741,0.00761,0.01141,0.01532,0.01932,0.02302],
    [0.08860,0.13680,0.00683,0.00126,0,0.00104,0.00082,0.00258,0.00270,0.00514,0.00789,0.01085,0.01370],
    [0.13150,0.13680,0.01311,0.00457,0.00104,0,0.00001,0.00035,0.00039,0.00157,0.00322,0.00521,0.00725],
    [0.05970,0.14120,0.01230,0.00410,0.00082,0.00001,0,0.00050,0.00055,0.00187,0.00365,0.00575,0.00788],
    [0.09300,0.12970,0.01763,0.00741,0.00258,0.00035,0.00050,0,0.00000,0.00044,0.00146,0.00288,0.00445],
    [0.09360,0.13470,0.01793,0.00761,0.00270,0.00039,0.00055,0.00000,0,0.00039,0.00137,0.00276,0.00430],
    [0.16500,0.14200,0.02347,0.01141,0.00514,0.00157,0.00187,0.00044,0.00039,0,0.00030,0.00107,0.00210],
    [0.07999,0.10920,0.02886,0.01532,0.00789,0.00322,0.00365,0.00146,0.00137,0.00030,0,0.00024,0.00082],
    [0.07999,0.13500,0.03416,0.01932,0.01085,0.00521,0.00575,0.00288,0.00276,0.00107,0.00024,0,0.00017],
    [0.07999,0.13500,0.03893,0.02302,0.01370,0.00725,0.00788,0.00445,0.00430,0.00210,0.00082,0.00017,0],
]

# Alias que apunta a la matriz por defecto de la EOS activa. Se usa como
# valor por defecto cuando el llamador no pasa kij explícito (por ejemplo,
# `calcular(z,T,P)`). Los módulos que deben quedarse en PR (entalpia_entropia.py)
# usan KIJ_DEFAULT_PR directamente.
KIJ_DEFAULT = KIJ_DEFAULT_PR

# ═══════════════════════════════════════════════════════════════════
# FUENTES ALTERNATIVAS DE kij  (HYSYS  /  PVTsim)
# ═══════════════════════════════════════════════════════════════════
# Volumenes criticos [cm3/mol] (Reid, Prausnitz & Sherwood). Coinciden
# con los V* de COSTALD ya presentes en el motor dentro del 2.3%.
VC = [89.8, 93.9, 99.2, 148.3, 200.0, 262.7, 255.0,
      306.0, 313.0, 370.0, 428.0, 486.0, 544.0]


def kij_chueh_prausnitz(n=1.0):
    """Matriz kij por la correlacion de Chueh y Prausnitz (1967), calculada
    SOLO a partir de volumenes criticos:

        kij = 1 - [ 2 Vci^(1/3) Vcj^(1/3) / (Vci^(1/3) + Vcj^(1/3)) ]^n

    Es la opcion generica que documenta PVTsim (exponente n, por defecto 1).
    No depende de la EOS: la misma matriz sirve para PR y para SRK.
    """
    v13 = [v ** (1.0 / 3.0) for v in VC]
    M = [[0.0] * NC for _ in range(NC)]
    for i in range(NC):
        for j in range(NC):
            if i == j:
                continue
            M[i][j] = 1.0 - (2.0 * (v13[i] * v13[j]) ** 0.5 /
                             (v13[i] + v13[j])) ** n
    return M


def _kij_desde_triangular(filas):
    """Construye la matriz simetrica 13x13 desde su triangular inferior.
    `filas[i]` = [kij(i,0), kij(i,1), ..., kij(i,i-1)] para i=1..NC-1."""
    M = [[0.0] * NC for _ in range(NC)]
    for i in range(1, NC):
        fila = filas[i - 1]
        for j in range(len(fila)):
            v = float(fila[j])
            M[i][j] = v
            M[j][i] = v
    return M


# PVTsim (Knapp et al., 1982) con los componentes pesados como n-alcanos
# (n-heptano, n-octano, n-nonano). Triangular inferior, filas C(i) vs los
# anteriores en orden: N2, CO2, C1, C2, C3, iC4, nC4, iC5, nC5, C6, C7, C8, C9.
_PVT_PR_TRI = [
    [-0.017],                                                          # CO2
    [0.0311, 0.12],                                                    # C1
    [0.0515, 0.12, 0],                                                 # C2
    [0.0852, 0.12, 0, 0],                                              # C3
    [0.1033, 0.12, 0, 0, 0],                                           # iC4
    [0.08, 0.12, 0, 0, 0, 0],                                          # nC4
    [0.0922, 0.12, 0, 0, 0, 0, 0],                                     # iC5
    [0.1, 0.12, 0, 0, 0, 0, 0, 0],                                     # nC5
    [0.1496, 0.12, 0, 0, 0, 0, 0, 0, 0],                              # C6
    [0.1441, 0.1, 0.0352, 0.0067, 0.0056, 0, 0.0033, 0, 0.0074, -0.0078],  # C7
    [0.08, 0.1, 0.0496, 0.0185, 0, 0, 0, 0, 0, 0, 0],                 # C8
    [0.08, 0.1, 0.0474, 0, 0, 0, 0, 0, 0, 0, 0, 0],                   # C9
]
_PVT_SRK_TRI = [
    [-0.0315],
    [0.0278, 0.12],
    [0.0407, 0.12, 0],
    [0.0763, 0.12, 0, 0],
    [0.0944, 0.12, 0, 0, 0],
    [0.07, 0.12, 0, 0, 0, 0],
    [0.0867, 0.12, 0, 0, 0, 0, 0],
    [0.0878, 0.12, 0, 0, 0, 0, 0, 0],
    [0.1496, 0.12, 0, 0, 0, 0, 0, 0, 0],
    [0.1422, 0.11, 0.0307, 0.0041, 0.0044, 0, -0.0004, 0, 0.0019, -0.0011],
    [0.08, 0.1, 0.0448, 0.017, 0, 0, 0, 0, -0.0022, 0, 0],
    [0.08, 0.1, 0.0448, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
KIJ_PVTSIM_PR  = _kij_desde_triangular(_PVT_PR_TRI)
KIJ_PVTSIM_SRK = _kij_desde_triangular(_PVT_SRK_TRI)

# ── Las CUATRO ecuaciones de estado disponibles ─────────────────────
#   'PR'      -> Peng-Robinson  (parametros HYSYS)
#   'SRK'     -> Soave-Redlich-Kwong (parametros HYSYS)
#   'PR_PVT'  -> Peng-Robinson  (parametros PVTsim / Reid 1977)
#   'SRK_PVT' -> Soave-Redlich-Kwong (parametros PVTsim / Reid 1977)
EOS_LISTA = ['PR', 'SRK', 'PR_PVT', 'SRK_PVT']

# Etiquetas legibles para la interfaz.
EOS_ETIQUETAS = {
    'PR':      'Peng-Robinson (HYSYS)',
    'SRK':     'SRK (HYSYS)',
    'PR_PVT':  'Peng-Robinson (PVTsim)',
    'SRK_PVT': 'SRK (PVTsim)',
}

# kij por defecto de cada EOS (una matriz por opcion).
KIJ_POR_EOS = {
    'PR':      KIJ_DEFAULT_PR,
    'SRK':     KIJ_DEFAULT_SRK,
    'PR_PVT':  KIJ_PVTSIM_PR,
    'SRK_PVT': KIJ_PVTSIM_SRK,
}


def es_srk(eos):
    """True si la EOS es del tipo Soave-Redlich-Kwong."""
    return eos in ('SRK', 'SRK_PVT')


def es_pvtsim(eos):
    """True si la EOS usa parametros de PVTsim."""
    return eos in ('PR_PVT', 'SRK_PVT')


def kij_base(eos):
    """Matriz kij por defecto de la EOS indicada (una de las 4)."""
    import copy as _c
    return _c.deepcopy(KIJ_POR_EOS.get(eos, KIJ_DEFAULT_PR))

# ═══════════════════════════════════════════════════════════════════
# ESTADO GLOBAL DE LA ECUACION DE ESTADO ACTIVA
# ═══════════════════════════════════════════════════════════════════
# La EOS activa determina que fórmulas de α(T), ai, bi, Z(A,B) y ln φi
# se aplican en el flash, la envolvente y la saturación. TODAS las
# funciones sin sufijo son despachadores que reenvían al bloque _pr o
# _srk. Las funciones con sufijo _pr son las originales (nunca cambian
# de comportamiento) y las usan los módulos que deben seguir en PR pase
# lo que pase (entalpia_entropia → propiedades termodinámicas).
EOS_DISPONIBLES = ('PR', 'SRK', 'PR_PVT', 'SRK_PVT')
_EOS_ACTIVA = 'PR'

def set_eos(name):
    """Cambia la EOS activa. Debe llamarse antes de cualquier cálculo.
    Opciones: PR, SRK (HYSYS) y PR_PVT, SRK_PVT (PVTsim)."""
    global _EOS_ACTIVA
    n = str(name).upper()
    if n not in EOS_DISPONIBLES:
        raise ValueError(f"EOS '{name}' no reconocida. Opciones: {EOS_DISPONIBLES}")
    _EOS_ACTIVA = n

def get_eos():
    """Devuelve el nombre de la EOS activa."""
    return _EOS_ACTIVA

# ── Parámetros individuales PR (Peng-Robinson 1976) ──────────────
def ai_pr(i):     return 0.45724*R_GAS**2*TC[i]**2/PC[i]
def bi_pr(i):     return 0.07780*R_GAS*TC[i]/PC[i]

# ═══════════════════════════════════════════════════════════════════
# PARAMETROS CRITICOS ESPECIFICOS POR ECUACION DE ESTADO
# ═══════════════════════════════════════════════════════════════════
# HALLAZGO (Aspen Physical Property Methods V8.8, cap. 2 "Property
# Method Descriptions", metodos HYSPR y HYSSRK):
# HYSYS NO comparte los parametros criticos entre PR y SRK. Mantiene
# dos juegos separados en su banco de datos:
#
#   Metodo HYSPR  -> TCHPR,  PCHPR,  OMGHPR, HPRKIJ, VTHPR
#   Metodo HYSSRK -> TCHSRK, PCHSRK, OMHSRK, HSRKIJ, VTHSRK
#
# El factor acentrico de SRK (OMHSRK) es el que HYSYS muestra como
# "SRK Acentricity" en la ficha de cada componente, y NO coincide con
# el de PR (p.ej. metano: 0.00740 en SRK vs 0.011498 en PR).
#
# Estos valores ya estaban extraidos de HYSYS en el proyecto, pero se
# usaban unicamente en COSTALD; el flash de SRK seguia tomando el
# omega de PR, lo que producia un sesgo sistematico en la fraccion de
# vapor (~+1e-3). Ahora el bloque SRK los usa de verdad.
#
# Precision COMPLETA tal como los reporta HYSYS (DATOS.xlsx).
OMEGA_SRK = [
    0.0357998013496399,   # N2
    0.237250000238419,    # CO2
    0.00740000000223517,  # C1
    0.098300002515316,    # C2
    0.153200000524521,    # C3
    0.182500004768372,    # iC4
    0.200800001621246,    # nC4
    0.239950001239777,    # iC5
    0.25220000743866,     # nC5
    0.300700008869171,    # C6
    0.350690007209778,    # C7
    0.399800002574921,    # C8
    0.447800010442734,    # C9
]

# Tc y Pc especificos de SRK (TCHSRK / PCHSRK). Verificado contra el
# reporte de HYSYS: coinciden BIT A BIT con los de PR en doble
# precision, de modo que HYSYS NO varia las criticas entre paquetes.
# Lo unico que cambia entre PR y SRK es el factor acentrico y los kij.
TC_SRK = list(TC)
PC_SRK = list(PC)

# ═══════════════════════════════════════════════════════════════════
# PROPIEDADES CRITICAS DE PVTsim  (Reid, Prausnitz & Sherwood 1977)
# ═══════════════════════════════════════════════════════════════════
# Provistas por el usuario desde la base de datos de PVTsim.
# Tc en °F (convertida a °R sumando 459.67), Pc en psia, factor acentrico
# UNICO para PR y SRK (PVTsim no separa omega por EOS, a diferencia de HYSYS).
_TC_PVT_F = [-232.51, 87.89, -116.59, 90.05, 205.97, 274.91, 305.69,
             369.05, 385.61, 453.65, 512.69, 564.17, 610.61]
TC_PVT = [t + 459.67 for t in _TC_PVT_F]                     # °R
PC_PVT = [492.32, 1069.87, 667.2, 708.35, 615.76, 529.06, 551.1,
          490.85, 489.38, 430.59, 396.79, 360.05, 335.07]     # psia
OMEGA_PVT = [0.04, 0.225, 0.008, 0.098, 0.152, 0.176, 0.193,
             0.227, 0.251, 0.296, 0.351, 0.394, 0.44]
PM_PVT = [28.014, 44.01, 16.043, 30.07, 44.097, 58.124, 58.124,
          72.151, 72.151, 86.178, 100.205, 114.232, 128.258]

# ── Parámetros individuales SRK (Soave-Redlich-Kwong 1972) ───────
# Constantes EXACTAS derivadas de las condiciones criticas:
#   Omega_a = 1 / (9 (2^(1/3) - 1))   = 0.4274802335...
#   Omega_b = (2^(1/3) - 1) / 3       = 0.0866403500...
# El manual de HYSYS (Property Methods and Calculations, tabla
# SRK vs PR) publica 0.42748 y 0.08664: los mismos valores truncados.
OMEGA_A_SRK = 0.42748023354
OMEGA_B_SRK = 0.08664034996

def ai_srk(i):    return OMEGA_A_SRK*R_GAS**2*TC_SRK[i]**2/PC_SRK[i]
def bi_srk(i):    return OMEGA_B_SRK*R_GAS*TC_SRK[i]/PC_SRK[i]

# ── Despachadores ai/bi ─────────────────────────────────────────
def ai(i):
    return float(ai_eos(_EOS_ACTIVA)[i])
def bi(i):
    return float(bi_eos(_EOS_ACTIVA)[i])

# NOTA sobre la traslacion volumetrica (Peneloux-Rauzy):
# Aqui habia definidas Z_RA(i), ci(i) y cm(comp), pero NUNCA se usaban
# en ningun calculo: eran codigo muerto. Se eliminaron.
#
# Es correcto que no afecten al flash. El manual de Aspen (Physical
# Property Methods, cap. 1, "Equation-of-State Models") lo dice de forma
# explicita: la traslacion volumetrica "is independent of VLE
# computation". La razon es algebraica: el desplazamiento c_i entra en
# ln(phi_i) como un termino -c_i*P/(RT) que es identico en la fase
# liquida y en la vapor, de modo que se cancela exactamente en
# K_i = phi_i^L / phi_i^V. Solo corrige el volumen molar (densidad),
# nunca el equilibrio.
#
# HYSYS reporta parametros de traslacion (VTHPR para PR, VTHSRK para
# SRK), pero para la DENSIDAD DE LIQUIDO el HYSYS de escritorio no los
# usa: aplica COSTALD + correccion de presion de Chueh-Prausnitz para
# Tr < 1, y el factor Z de la EOS por encima (manual HYSYS, seccion
# A.4.1). Eso es justamente lo que ya implementamos.

# ── COSTALD (Hankinson-Thomson 1979) para densidad de líquido ──
# Volumen característico V* (ft3/lbmol) por componente.
# Orden: N2, CO2, C1, C2, C3, iC4, nC4, iC5, nC5, C6, C7, C8, C9
# Valores exactos extraídos de HYSYS (Characteristic Volume).
# COSTALD usa el factor acentrico SRK (OMEGA_SRK), definido arriba.
VSTAR_COSTALD = [1.44406, 1.50301, 1.59207, 2.33469, 3.20497, 4.11402, 4.07494,
                 4.95916, 4.98687, 5.89800, 6.89499, 7.85577, 8.85661]

def costald_Vs(comp, T):
    """Volumen molar de líquido saturado por COSTALD (ft3/lbmol).

    Correlación de Hankinson-Thomson (1979) *válida sólo para Tr<1*
    (líquido saturado). En zona supercrítica (Tr≥1) el volumen predicho
    por COSTALD no tiene sentido físico y la extrapolación —forzando
    Tr=0.99 como se hacía antes— clava la densidad en su valor
    pseudocrítico y la vuelve invariante con la presión, exactamente
    porque COSTALD saturado sólo depende de T. Para no propagar ese
    artefacto la función retorna None en Tr≥1 y el consumidor cae
    automáticamente a la densidad de la EOS de Peng-Robinson (que es
    también lo que HYSYS con Fluid Package Peng-Robinson estándar usa
    en líquido supercrítico).
    """
    s_xV   = sum(comp[i]*VSTAR_COSTALD[i]          for i in range(NC))
    s_xV13 = sum(comp[i]*VSTAR_COSTALD[i]**(1/3.0) for i in range(NC))
    s_xV23 = sum(comp[i]*VSTAR_COSTALD[i]**(2/3.0) for i in range(NC))
    Vm_star = 0.25*(s_xV + 3.0*s_xV13*s_xV23)
    if Vm_star <= 0: return None
    num = 0.0
    for i in range(NC):
        if comp[i] == 0: continue
        for j in range(NC):
            if comp[j] == 0: continue
            num += comp[i]*comp[j]*np.sqrt(
                VSTAR_COSTALD[i]*TC[i]*VSTAR_COSTALD[j]*TC[j])
    Tcm = num/Vm_star
    omega_m = sum(comp[i]*OMEGA_SRK[i] for i in range(NC))
    Tr = T/Tcm
    if Tr >= 1.0:
        # Fuera del rango de validez de COSTALD: no extrapolar.
        return None
    tau = 1.0 - Tr
    V0 = (1 - 1.52816*tau**(1/3.0) + 1.43907*tau**(2/3.0)
            - 0.81446*tau + 0.190454*tau**(4/3.0))
    Vd = ((-0.296123 + 0.386914*Tr - 0.0427258*Tr**2 - 0.0480645*Tr**3)
          / (Tr - 1.00001))
    Vs = Vm_star*V0*(1.0 - omega_m*Vd)
    return Vs if Vs > 0 else None

# ── Corrección de presión Chueh-Prausnitz + Smooth Liquid Density ──
# Réplica del algoritmo HYSYS documentado en el manual oficial
# "Aspen HYSYS Properties and Methods Technical Reference", sección
# A.4.1 (Liquid Density):
#
#   "COSTALD [...] can be applied to sub-cooled liquid densities, i.e., at
#    pressures greater than the vapour pressure, using the Chueh and
#    Prausnitz correction factor for compressed fluids. It is used to
#    predict the density for all systems whose pseudo-reduced temperature
#    is below 1.0. Above this temperature, the equation of state
#    compressibility factor is used to calculate the liquid density."
#
# Con la opción "Smooth Liquid Density" activada (default de HYSYS con
# COSTALD), HYSYS interpola las densidades de líquido en la banda
# Tr∈[0.95, 1.0] entre la correlación COSTALD+Chueh-Prausnitz y la
# densidad de la EOS, para dar una transición continua al régimen
# supercrítico.  Referencia: Aspen HYSYS Documentation and Course Hero
# transcription of the manual.
#
# La ecuación de Chueh-Prausnitz (Prausnitz & Chueh 1968; el manual
# HYSYS la lista como opción del *Pressure Correction* con la forma
#   ρ = 1/[Vs·(1+B)^n],  B = f(P,Ps,T,Tc,Pc),  n = constante):
# aquí se usa la forma logarítmica equivalente, con la definición de
# β(Tr,ω,Pc) tomada de la extensión Hankinson-Brobst-Thomson (que HYSYS
# también acepta como opción "Tait's Equation" en el mismo menú):
#
#   V(T,P) = Vs(T) · [1 − c · ln((β+P)/(β+Ps))]
#   c = 0.0894
#   β/Pc = -1 + a(1-Tr)^(1/3) + b(1-Tr)^(2/3) + d(1-Tr) + e(1-Tr)^(4/3)
#   e = exp(f + g·ω + h·ω²)
#   a=-9.070217, b=62.45326, d=-135.1102, f=4.79594, g=0.250047, h=1.14188
#
# Ps (presión de saturación de la mezcla a T) se estima explícitamente
# vía Wilson (evita la iteración del punto de burbuja):
#   Ps = Σ zi · Pci · exp[5.373·(1+ωi)·(1−Tci/T)]

def _costald_mix_params(comp):
    """Tcm, ω_SRK,m, Pcm pseudocríticos de la regla COSTALD/Kay."""
    s_xV   = sum(comp[i]*VSTAR_COSTALD[i]          for i in range(NC))
    s_xV13 = sum(comp[i]*VSTAR_COSTALD[i]**(1/3.0) for i in range(NC))
    s_xV23 = sum(comp[i]*VSTAR_COSTALD[i]**(2/3.0) for i in range(NC))
    Vm_star = 0.25*(s_xV + 3.0*s_xV13*s_xV23)
    if Vm_star <= 0: return None
    num = 0.0
    for i in range(NC):
        if comp[i] == 0: continue
        for j in range(NC):
            if comp[j] == 0: continue
            num += comp[i]*comp[j]*np.sqrt(
                VSTAR_COSTALD[i]*TC[i]*VSTAR_COSTALD[j]*TC[j])
    Tcm = num/Vm_star
    om  = sum(comp[i]*OMEGA_SRK[i] for i in range(NC))
    Pcm = sum(comp[i]*PC[i] for i in range(NC))  # Pc pseudocrítica Kay
    return Tcm, om, Pcm

def _Ps_wilson(comp, T):
    """Presión de saturación (burbuja) por Wilson, forma explícita.
       Ps = Σ zi·Pci·exp[5.373·(1+ωi)·(1−Tci/T)]  [psia]
    """
    total = 0.0
    for i in range(NC):
        if comp[i] == 0: continue
        try:
            total += comp[i]*PC[i]*np.exp(5.373*(1.0+OMEGA[i])*(1.0-TC[i]/T))
        except (OverflowError, FloatingPointError):
            total += comp[i]*PC[i]*1e30
    return max(total, 1e-6)

def _Ps_burbuja_PR(comp, T, kij, max_iter=30, tol=1e-6):
    """Presión de burbuja de la mezcla por Peng-Robinson (Newton en P).
    Refina el estimado Wilson iterando K_i = φ_i^L/φ_i^V hasta que
    Σ zi·Ki = 1.  Cerca del punto crítico (Tr>0.9) Wilson subestima o
    sobreestima Ps por hasta 15%, y este refinamiento es indispensable
    para reproducir la Ps interna que HYSYS usa como referencia de la
    corrección Chueh-Prausnitz.  Fallback: Ps de Wilson si no converge.
    """
    P = _Ps_wilson(comp, T)
    Kw = [(PC[i]/P)*np.exp(5.373*(1.0+OMEGA[i])*(1.0-TC[i]/T))
          if comp[i]>0 else 1.0 for i in range(NC)]
    for _it in range(max_iter):
        y = [comp[i]*Kw[i] for i in range(NC)]
        sy = sum(y)
        if sy <= 0: break
        y = [yi/sy for yi in y]
        am_L = am(comp, T, kij); bm_L = bm(comp)
        am_V = am(y,    T, kij); bm_V = bm(y)
        _, ZL_ = solve_Z(*AB(am_L, bm_L, T, P))
        ZV_, _ = solve_Z(*AB(am_V, bm_V, T, P))
        phi_L = [phi_i(i, comp, T, P, ZL_, am_L, bm_L, kij) for i in range(NC)]
        phi_V = [phi_i(i, y,    T, P, ZV_, am_V, bm_V, kij) for i in range(NC)]
        Kw_new = [phi_L[i]/phi_V[i] if (phi_V[i]>0 and comp[i]>0) else Kw[i]
                  for i in range(NC)]
        S = sum(comp[i]*Kw_new[i] for i in range(NC))
        if abs(S - 1.0) < tol: break
        # Newton en P (relación aprox K∝1/P):  P_new = P·S
        P_new = P*S
        if P_new <= 0 or not np.isfinite(P_new): break
        # Amortiguar cerca del crítico
        P = 0.5*(P + P_new) if abs(S-1)>0.5 else P_new
        Kw = Kw_new
    return P if (P > 0 and np.isfinite(P)) else _Ps_wilson(comp, T)

def V_liq_costald_smooth(comp, T, P, kij=None, Ps=None):
    """Volumen molar de líquido según algoritmo HYSYS "Smooth Liquid Density"
    (COSTALD saturado + corrección Chueh-Prausnitz + interpolación EOS).

    Retorna None si la mezcla no admite estado líquido en (T,P) por COSTALD
    (Vs no calculable). El caller debe entonces caer a la EOS.

    Argumentos:
        Ps  — presión de saturación de la mezcla a T (psia).  Si es None,
              se calcula internamente por bubble-point PR (más preciso
              cerca del crítico que Wilson).  Pasarla explícitamente
              cuando el caller ya la conoce para evitar recomputarla.
        kij — matriz de kij; requerida sólo si Ps es None.
    """
    mix = _costald_mix_params(comp)
    if mix is None: return None
    Tcm, om, Pcm = mix
    Vs = costald_Vs(comp, T)         # None si Tr ≥ 1
    if Vs is None or Vs <= 0: return None
    Tr = T/Tcm
    if Ps is None:
        if kij is None: kij = KIJ_DEFAULT
        Ps = _Ps_burbuja_PR(comp, T, kij)
    if P <= Ps:
        return Vs                     # COSTALD saturado tal cual
    # Chueh-Prausnitz compressed-liquid correction
    tau = 1.0 - Tr
    a, b, d = -9.070217, 62.45326, -135.1102
    f, g, h = 4.79594, 0.250047, 1.14188
    e_val = np.exp(f + g*om + h*om*om)
    beta = Pcm*(-1.0 + a*tau**(1/3.0) + b*tau**(2/3.0)
                    + d*tau + e_val*tau**(4/3.0))
    c_CP = 0.0894
    if beta + Ps <= 0 or beta + P <= 0:
        return Vs                     # fuera del rango, mantener saturado
    V_CP = Vs*(1.0 - c_CP*np.log((beta + P)/(beta + Ps)))
    return V_CP if V_CP > 0 else Vs
# ── m, alpha, ai·alpha para cada EOS ───────────────────────────
# PR: m = 0.37464 + 1.54226 ω − 0.26992 ω²
# SRK: m = 0.480 + 1.574 ω − 0.176 ω²  (Soave 1972 original)
def mi_pr(i):     w=OMEGA[i]; return 0.37464+1.54226*w-0.26992*w**2
def mi_srk(i):    w=OMEGA_SRK[i]; return 0.480+1.574*w-0.176*w**2
def alpha_pr(i,T):  return (1+mi_pr(i) *(1-np.sqrt(T/TC[i])))**2
def alpha_srk(i,T): return (1+mi_srk(i)*(1-np.sqrt(T/TC_SRK[i])))**2
def ai_alpha_pr(i,T):  return ai_pr(i) *alpha_pr(i,T)
def ai_alpha_srk(i,T): return ai_srk(i)*alpha_srk(i,T)

def mi(i):
    return float(mi_eos(_EOS_ACTIVA)[i])
def alpha(i,T):
    m = mi_eos(_EOS_ACTIVA)[i]; TCa = tc_eos(_EOS_ACTIVA)[i]
    return (1.0 + m*(1.0 - np.sqrt(T/TCa)))**2
def ai_alpha(i,T):
    return ai(i)*alpha(i,T)

# Constantes precomputadas (por EOS) — evitan reevaluar en cada llamada
_AI_PR  = np.array([ai_pr(i)  for i in range(NC)])
_BI_PR  = np.array([bi_pr(i)  for i in range(NC)])
_MI_PR  = np.array([mi_pr(i)  for i in range(NC)])
_AI_SRK = np.array([ai_srk(i) for i in range(NC)])
_BI_SRK = np.array([bi_srk(i) for i in range(NC)])
_MI_SRK = np.array([mi_srk(i) for i in range(NC)])
_TC     = np.array(TC)        # criticas de PR
_TC_SRK = np.array(TC_SRK)    # criticas de SRK (banco HYSSRK)

# ── Arreglos por EOS para las 4 opciones (HYSYS y PVTsim) ────────────
# PVTsim usa las criticas de Reid (TC_PVT/PC_PVT) y un UNICO omega para PR
# y SRK. La forma cubica (Omega_a/Omega_b y formula de m) es la misma que
# en HYSYS; lo que cambia son Tc, Pc, omega y los kij.
_OA_PR, _OB_PR   = 0.45724, 0.07780
_OA_SRK, _OB_SRK = OMEGA_A_SRK, OMEGA_B_SRK
_TC_PVT_A = np.array(TC_PVT)
_PC_PVT_A = np.array(PC_PVT)
_OM_PVT_A = np.array(OMEGA_PVT)

def _mi_pr_arr(om):  return 0.37464 + 1.54226*om - 0.26992*om**2
def _mi_srk_arr(om): return 0.480   + 1.574 *om - 0.176 *om**2

_AI_PR_PVT  = _OA_PR *R_GAS**2*_TC_PVT_A**2/_PC_PVT_A
_BI_PR_PVT  = _OB_PR *R_GAS*_TC_PVT_A/_PC_PVT_A
_MI_PR_PVT  = _mi_pr_arr(_OM_PVT_A)
_AI_SRK_PVT = _OA_SRK*R_GAS**2*_TC_PVT_A**2/_PC_PVT_A
_BI_SRK_PVT = _OB_SRK*R_GAS*_TC_PVT_A/_PC_PVT_A
_MI_SRK_PVT = _mi_srk_arr(_OM_PVT_A)

# Tablas por codigo de EOS: (AI, BI, MI, TC)
_PARAMS_EOS = {
    'PR':      (_AI_PR,      _BI_PR,      _MI_PR,      _TC),
    'SRK':     (_AI_SRK,     _BI_SRK,     _MI_SRK,     _TC_SRK),
    'PR_PVT':  (_AI_PR_PVT,  _BI_PR_PVT,  _MI_PR_PVT,  _TC_PVT_A),
    'SRK_PVT': (_AI_SRK_PVT, _BI_SRK_PVT, _MI_SRK_PVT, _TC_PVT_A),
}

def ai_alpha_vec_eos(eos, T):
    """Vector ai·α(T) para la EOS indicada (una de las 4)."""
    AI, _BIv, MI, TCa = _PARAMS_EOS.get(eos, _PARAMS_EOS['PR'])
    al = (1.0 + MI*(1.0 - np.sqrt(T/TCa)))**2
    return AI*al

def ai_eos(eos):  return _PARAMS_EOS.get(eos, _PARAMS_EOS['PR'])[0]
def bi_eos(eos):  return _PARAMS_EOS.get(eos, _PARAMS_EOS['PR'])[1]
def mi_eos(eos):  return _PARAMS_EOS.get(eos, _PARAMS_EOS['PR'])[2]
def tc_eos(eos):  return _PARAMS_EOS.get(eos, _PARAMS_EOS['PR'])[3]

def crit_props(eos):
    """(TC[°R], PC[psia], OMEGA, PM) de la EOS — para la tabla de parametros."""
    if es_pvtsim(eos):
        return TC_PVT, PC_PVT, OMEGA_PVT, PM_PVT
    if es_srk(eos):
        return TC_SRK, PC_SRK, OMEGA_SRK, PM
    return TC, PC, OMEGA, PM

# Retro-compatibilidad: nombres antiguos (usados por si algún módulo
# externo los importaba) apuntan al bloque PR.
_AI = _AI_PR
_BI = _BI_PR
_MI = _MI_PR
_KIJ_ARR = np.array(KIJ_DEFAULT)

def _ai_alpha_vec_pr(T):
    al = (1.0 + _MI_PR*(1.0 - np.sqrt(T/_TC)))**2
    return _AI_PR*al

def _ai_alpha_vec_srk(T):
    al = (1.0 + _MI_SRK*(1.0 - np.sqrt(T/_TC_SRK)))**2
    return _AI_SRK*al

def _ai_alpha_vec(T):
    """Vector ai·α(T) para todos los componentes (según EOS activa)."""
    return ai_alpha_vec_eos(_EOS_ACTIVA, T)

def aij(i,j,T,kij):
    return np.sqrt(ai_alpha(i,T)*ai_alpha(j,T))*(1-kij[i][j])

def am(z,T,kij):
    # am = sum_i sum_j z_i z_j sqrt(aa_i aa_j)(1-kij_ij), vectorizado.
    aa = _ai_alpha_vec(T)
    saa = np.sqrt(aa)
    w = np.asarray(z)*saa                      # w_i = z_i sqrt(aa_i)
    kij_arr = kij if isinstance(kij, np.ndarray) else np.asarray(kij)
    # sum_ij w_i w_j (1-kij) = (sum w)^2 - w^T (kij) w
    return float(w.sum()**2 - w @ kij_arr @ w)

def bm(z):
    return sum(z[i]*bi(i) for i in range(NC))

# Variantes explícitas PR (usadas por entalpia_entropia para que la entalpía y
# entropía siempre se calculen en modo Peng-Robinson, independientemente
# de la EOS activa que haya elegido el usuario para el flash).
def am_pr(z,T,kij):
    aa = _ai_alpha_vec_pr(T)
    saa = np.sqrt(aa)
    w = np.asarray(z)*saa
    kij_arr = kij if isinstance(kij, np.ndarray) else np.asarray(kij)
    return float(w.sum()**2 - w @ kij_arr @ w)

def bm_pr(z):
    return sum(z[i]*bi_pr(i) for i in range(NC))

def AB(am_val,bm_val,T,P):
    A=am_val*P/(R_GAS*T)**2
    B=bm_val*P/(R_GAS*T)
    return A,B

def fase_supercritica(z,T,P,Z,kij):
    """
    Identificación de fase para fluidos con UNA SOLA raíz real de PR
    (región supercrítica, líquido comprimido monofásico o gas fuera de
    la envolvente). Réplica del algoritmo publicado en el manual oficial
    *Aspen HYSYS Properties and Methods Technical Reference* (Aspen
    Technology, © 1981-2013), sección "Supercritical Handling", que
    dice textualmente:

        "For the PR, SRK, SourPR, and Sour SRK cubic equations of state
         AT SUPERCRITICAL REGION:
         1. If the compressibility factor (Z) is greater than 0.3, and
            the isothermal compressibility factor (beta) is greater than
            0.75, a vapor fraction of 1.0 is assigned to the stream.
         2. If Z is greater than 0.75 and the sum of composition of
            light compounds (NBP<230K) is greater than the sum of
            composition of heavy compounds, a vapor fraction of 1.0 is
            assigned to the stream.
         Otherwise, vapor fraction of 0 is assigned to the stream and
         liquid correlations are used."

    El énfasis en "AT SUPERCRITICAL REGION" es clave: las reglas 1 y 2
    solamente se aplican cuando el fluido está genuinamente en
    condiciones supercríticas de la mezcla, es decir, T > Tc AND P > Pc
    de la mezcla. Fuera de esa zona la fase de la única raíz es
    inequívoca por su régimen y no se aplican las reglas de umbrales:

        • T < Tc  →  la temperatura es subcrítica: el fluido con una
                     sola raíz de PR es LÍQUIDO comprimido, sin importar
                     cuán alta sea la presión. (Esta rama es la que
                     recupera casos como gas seco a 300°R/8000 psi, y
                     mezclas C1/C2 90/10 a T muy baja y P>4000 psi,
                     donde el criterio ingenuo Z>0.75 ∧ ligeros>pesados
                     daba VAPOR incorrectamente.)

        • T > Tc, P < Pc  →  gas SOBRECALENTADO fuera de la envolvente;
                             siempre VAPOR.

        • T > Tc, P > Pc  →  supercrítico genuino: aplicar reglas 1 y 2
                             del manual, en ese orden.

    Definiciones:
        β = P·κ = -(P/V)·(∂V/∂P)_T  (compresibilidad isotérmica
        adimensional, β→1 gas ideal), con κ evaluada mediante derivadas
        analíticas exactas de la cúbica de PR.

        Tc, Pc de la mezcla: regla pseudocrítica de Kay,
        Tc_m = Σ z_i·Tc_i,   Pc_m = Σ z_i·Pc_i.
        Ligero: NBP<230 K = 414°R (tabla NBP arriba).

    Sin parámetros ajustables. Los umbrales 0.3, 0.75 y 230 K son
    constantes del manual, no calibraciones a casos particulares.

    Fundamento teórico complementario: el algoritmo es una simplificación
    del parámetro de identificación de fase (PIP) de Venkatarathnam &
    Oellrich, *Fluid Phase Equilibria* 301 (2011) 225-233 —mismo método
    implementado en NIST REFPROP, DWSIM y CoolProp— pero HYSYS lo
    reemplaza por umbrales sobre variables más simples (Z, β) más una
    regla auxiliar por composición para cubrir Z>1, restringidos por el
    régimen supercrítico.

    Validado contra 9 puntos verificados directamente en HYSYS por el
    usuario: C1/C2 90/10 a 350°R/1000 psi, a 2000 psi con
    T=400/433/434/450°R (frontera HYSYS entre 433 y 434 R), y a 1°R
    /6000 psi (LIQ); gas seco a 300°R/8000 psi (LIQ), y a 620°R con
    P=3000/8000/15000 psi (todos VAP).
    """
    # Punto pseudocrítico de Kay
    Tc_m = 0.0; Pc_m = 0.0
    for i in range(NC):
        Tc_m += z[i]*TC[i]
        Pc_m += z[i]*PC[i]

    # Régimen subcrítico en T: líquido comprimido
    if T < Tc_m:
        return "liquido"
    # T supercrítica pero P subcrítica: gas sobrecalentado
    if P < Pc_m:
        return "vapor"

    # Supercrítico genuino (T>Tc AND P>Pc): reglas del manual
    am_val = am(z,T,kij); bm_val = bm(z)
    b = bm_val
    Vm = Z*R_GAS*T/P

    # β = -(P/V)·(∂V/∂P)_T con derivada analítica exacta según EOS activa.
    # PR:  (∂P/∂V)_T = -RT/(V-b)² + 2a(V+b)/(V²+2bV-b²)²
    # SRK: (∂P/∂V)_T = -RT/(V-b)² + a(2V+b)/[V²(V+b)²]
    if es_srk(_EOS_ACTIVA):
        dPdV = -R_GAS*T/(Vm-b)**2 + am_val*(2*Vm+b)/(Vm*Vm*(Vm+b)**2)
    else:
        D_pr = Vm*Vm + 2*b*Vm - b*b
        dPdV = -R_GAS*T/(Vm-b)**2 + 2*am_val*(Vm+b)/D_pr**2
    if Vm != 0 and dPdV != 0:
        beta = -P/(Vm*dPdV)
    else:
        beta = 0.0

    # Composición ligeros / pesados (NBP<230 K = 414°R)
    z_lig = sum(z[i] for i in range(NC) if NBP[i] < 414.0)
    z_pes = sum(z[i] for i in range(NC) if NBP[i] >= 414.0)

    # Reglas del manual (en ese orden)
    regla_1 = (Z > 0.3)  and (beta > 0.75)
    regla_2 = (Z > 0.75) and (z_lig > z_pes)

    return "vapor" if (regla_1 or regla_2) else "liquido"

def _cardano_cubica(p2, p1, p0):
    """Raíces reales positivas (>0) de Z³ + p2·Z² + p1·Z + p0 = 0 por Cardano.
    Utilizado por PR y SRK con distintos coeficientes."""
    shift = p2/3.0
    p = p1 - p2*p2/3.0
    q = 2.0*p2**3/27.0 - p2*p1/3.0 + p0
    disc = (q*q)/4.0 + (p*p*p)/27.0
    if disc > 1e-14:
        sq = math.sqrt(disc)
        u = np.cbrt(-q/2.0 + sq)
        v = np.cbrt(-q/2.0 - sq)
        return [u + v - shift]
    if abs(p) < 1e-30:
        return [-shift]
    mfac = 2.0*math.sqrt(-p/3.0)
    arg = 3.0*q/(p*mfac)
    arg = max(-1.0, min(1.0, arg))
    theta = math.acos(arg)/3.0
    return [mfac*math.cos(theta - 2.0*math.pi*k/3.0) - shift for k in range(3)]

def solve_Z_pr(A,B):
    # PR: Z³ - (1-B)Z² + (A - 3B² - 2B)Z - (AB - B² - B³) = 0
    p2 = -(1.0 - B)
    p1 = A - 3.0*B*B - 2.0*B
    p0 = -(A*B - B*B - B*B*B)
    raices = _cardano_cubica(p2, p1, p0)
    real = [r for r in raices if r > B] or [max(raices)]
    real = sorted(real)
    return real[-1], real[0]

def solve_Z_srk(A,B):
    # SRK: Z³ - Z² + (A - B - B²)Z - AB = 0
    p2 = -1.0
    p1 = A - B - B*B
    p0 = -A*B
    raices = _cardano_cubica(p2, p1, p0)
    real = [r for r in raices if r > B] or [max(raices)]
    real = sorted(real)
    return real[-1], real[0]

def solve_Z(A,B):
    """Retorna (ZV, ZL) mediante Cardano según EOS activa."""
    return solve_Z_srk(A,B) if es_srk(_EOS_ACTIVA) else solve_Z_pr(A,B)

_SQRT2 = np.sqrt(2.0)

def ln_phi_i_pr(i,z,T,P,Z,am_val,bm_val,kij):
    """Coef. de fugacidad PR (fórmula clásica con factor 2√2)."""
    bi_=bi_eos(_EOS_ACTIVA)[i]; A,B=AB(am_val,bm_val,T,P)
    aa = ai_alpha_vec_eos(_EOS_ACTIVA, T)
    saa = np.sqrt(aa)
    w = np.asarray(z)*saa
    kij_arr = kij if isinstance(kij, np.ndarray) else np.asarray(kij)
    sum_aij = saa[i]*(w.sum() - (kij_arr[i] @ w))
    if Z<=B: Z=B+1e-12
    t1=(bi_/bm_val)*(Z-1)
    t2=-np.log(Z-B)
    denom=Z+(1-_SQRT2)*B
    numer=Z+(1+_SQRT2)*B
    if denom<=0: denom=1e-12
    if numer<=0: numer=1e-12
    t3=A/(2*_SQRT2*B)*np.log(numer/denom)
    t4=(2*sum_aij/am_val-bi_/bm_val)*t3
    return t1+t2-t4

def ln_phi_i_srk(i,z,T,P,Z,am_val,bm_val,kij):
    """Coef. de fugacidad SRK.
    ln φi = (bi/b)(Z-1) - ln(Z-B) - (A/B)[2 Σj xj·aij / am - bi/b] · ln[(Z+B)/Z]
    """
    bi_=bi_eos(_EOS_ACTIVA)[i]; A,B=AB(am_val,bm_val,T,P)
    aa = ai_alpha_vec_eos(_EOS_ACTIVA, T)
    saa = np.sqrt(aa)
    w = np.asarray(z)*saa
    kij_arr = kij if isinstance(kij, np.ndarray) else np.asarray(kij)
    sum_aij = saa[i]*(w.sum() - (kij_arr[i] @ w))
    if Z<=B: Z=B+1e-12
    t1 = (bi_/bm_val)*(Z-1)
    t2 = -np.log(Z-B)
    ratio = (Z+B)/Z
    if ratio<=0: ratio = 1e-12
    if B<=0: B = 1e-12
    t3 = (A/B)*np.log(ratio)
    t4 = (2.0*sum_aij/am_val - bi_/bm_val)*t3
    return t1 + t2 - t4

def ln_phi_i(i,z,T,P,Z,am_val,bm_val,kij):
    """Coef. de fugacidad según EOS activa."""
    if es_srk(_EOS_ACTIVA):
        return ln_phi_i_srk(i,z,T,P,Z,am_val,bm_val,kij)
    return ln_phi_i_pr(i,z,T,P,Z,am_val,bm_val,kij)

def phi_i(i,z,T,P,Z,am_val,bm_val,kij):
    return np.exp(min(700,max(-700,ln_phi_i(i,z,T,P,Z,am_val,bm_val,kij))))

def Ki_wilson(i,T,P):
    return (PC[i]/P)*np.exp(5.373*(1+OMEGA[i])*(1-TC[i]/T))

# ══ Rachford-Rice ════════════════════════════════════════════
def RR(V,z,K):
    return sum(z[i]*(K[i]-1)/(1+V*(K[i]-1)) for i in range(NC))

def RR_deriv(V,z,K):
    return -sum(z[i]*(K[i]-1)**2/(1+V*(K[i]-1))**2 for i in range(NC))

def solve_V(z,K):
    """Newton para Rachford-Rice — busca raíz en intervalo válido"""
    Ks=[k for k in K if abs(k-1)>1e-12]
    if not Ks: return 0.5
    Vmin=max([-1.0/(k-1) for k in K if k>1.0+1e-10]+[0.0])
    Vmax=min([ 1.0/(1-k) for k in K if k<1.0-1e-10]+[1.0])
    Vmin=max(Vmin+1e-10,1e-10); Vmax=min(Vmax-1e-10,1-1e-10)
    if Vmin>=Vmax: return 0.5
    V=0.5*(Vmin+Vmax)
    for _ in range(500):
        f=RR(V,z,K); df=RR_deriv(V,z,K)
        if abs(df)<1e-30: break
        dV=-f/df
        V_new=V+dV
        if V_new<Vmin: V_new=0.5*(V+Vmin)
        if V_new>Vmax: V_new=0.5*(V+Vmax)
        if abs(V_new-V)<1e-14: V=V_new; break
        V=V_new
    return max(0.0,min(1.0,V))

# ══ Análisis de Estabilidad de Michelsen ═════════════════════
def analisis_estabilidad(z,T,P,kij,tol=1e-12,triv_tol=1e-4,tol_S=1e-4,max_iter=1000):
    """Replica exacta de la macro AnalisisEstabilidad del Excel"""
    Kv=[Ki_wilson(i,T,P) for i in range(NC)]
    Kl=[Ki_wilson(i,T,P) for i in range(NC)]

    am_z=am(z,T,kij); bm_z=bm(z)
    ZV_z,ZL_z=solve_Z(*AB(am_z,bm_z,T,P))

    convV=convL=1.0
    for it in range(max_iter):
        Yv_raw=[z[i]*Kv[i] for i in range(NC)]
        sv=sum(Yv_raw); 
        if sv<=0: sv=1
        Yv=[y/sv for y in Yv_raw]

        Yl_raw=[z[i]/Kl[i] if Kl[i]>1e-30 else z[i]*1e30 for i in range(NC)]
        sl=sum(Yl_raw)
        if sl<=0 or not np.isfinite(sl): sl=1
        Yl=[y/sl for y in Yl_raw]

        am_v=am(Yv,T,kij); bm_v=bm(Yv)
        am_l=am(Yl,T,kij); bm_l=bm(Yl)
        ZV_v,_=solve_Z(*AB(am_v,bm_v,T,P))
        _,ZL_l=solve_Z(*AB(am_l,bm_l,T,P))

        fug_v=[phi_i(i,Yv,T,P,ZV_v,am_v,bm_v,kij)*Yv[i]*P for i in range(NC)]
        fug_l=[phi_i(i,Yl,T,P,ZL_l,am_l,bm_l,kij)*Yl[i]*P for i in range(NC)]
        fug_zV=[phi_i(i,z,T,P,ZV_z,am_z,bm_z,kij)*z[i]*P for i in range(NC)]
        fug_zL=[phi_i(i,z,T,P,ZL_z,am_z,bm_z,kij)*z[i]*P for i in range(NC)]

        Riv=[np.log(fug_v[i]/fug_zV[i]) if (fug_v[i]>0 and fug_zV[i]>0) else 0 for i in range(NC)]
        Ril=[np.log(fug_l[i]/fug_zL[i]) if (fug_l[i]>0 and fug_zL[i]>0) else 0 for i in range(NC)]

        convV=sum(r**2 for r in Riv); convL=sum(r**2 for r in Ril)
        if convV<=tol and convL<=tol: break

        # Actualización idéntica a la macro del Excel (K427/L427):
        #   Vapor:   Kv_new = Kv · f_z / (f_v · Sv)      [G427 = K241/(E427·L278)]
        #   Líquido: Kl_new = Kl · (f_l · SL) / f_z      [H427 = (F427·L279)/K241]
        # La normalización por Sv y SL (las sumas de las fases incipientes) es
        # lo que evita que la búsqueda de líquido diverja: en un sistema
        # monofásico la converge a la solución trivial (Ki→1) en lugar de
        # explotar al límite numérico.
        Sv_it=sum(z[i]*Kv[i] for i in range(NC))
        Sl_it=sum(z[i]/Kl[i] if Kl[i]>1e-30 else 0 for i in range(NC))
        if Sv_it<=0 or not np.isfinite(Sv_it): Sv_it=1.0
        if Sl_it<=0 or not np.isfinite(Sl_it): Sl_it=1.0

        Kv_new=[]; Kl_new=[]
        for i in range(NC):
            # Vapor: G = f_z/(f_v·Sv) ; Kv_new = Kv·G
            if fug_v[i]>0 and fug_zV[i]>0:
                G=fug_zV[i]/(fug_v[i]*Sv_it)
                Kv_new.append(max(1e-20,min(1e20, Kv[i]*G)))
            else:
                Kv_new.append(Kv[i])
            # Líquido: H = (f_l·SL)/f_z ; Kl_new = Kl·H
            if fug_l[i]>0 and fug_zL[i]>0:
                H=(fug_l[i]*Sl_it)/fug_zL[i]
                Kl_new.append(max(1e-20,min(1e20, Kl[i]*H)))
            else:
                Kl_new.append(Kl[i])
        Kv=Kv_new; Kl=Kl_new

    Sv=sum(z[i]*Kv[i] for i in range(NC))
    Sl=sum(z[i]/Kl[i] if Kl[i]>0 else 0 for i in range(NC))

    # Criterio de trivialidad — RÉPLICA del Excel (M427/N427):
    #   M427 = IF(G427=0, 0, (LN(Kv))^2)
    # Los componentes ausentes (z[i]=0) NO participan: su Ki deriva libremente
    # y contaminaría la suma. El Excel los excluye con el flag IF(...=0,0,...).
    # Por eso sólo acumulamos (LN Ki)^2 de los componentes presentes (z[i]>0).
    trivV=sum((np.log(Kv[i]))**2 for i in range(NC) if z[i]>0)
    trivL=sum((np.log(Kl[i]))**2 for i in range(NC) if z[i]>0)
    esTrivV=(trivV<triv_tol); esTrivL=(trivL<triv_tol)

    inestable=False
    if Sv>(1+tol_S) or Sl>(1+tol_S):
        resultado="INESTABLE - SE REQUIERE FLASH"
        inestable=True
        Ki_flash=[Kv[i]*Kl[i] for i in range(NC)]
    else:
        Ki_flash=[Ki_wilson(i,T,P) for i in range(NC)]
        if esTrivV and esTrivL:
            resultado="ESTABLE - LEJOS DE REGION BIFASICA"
        elif esTrivV:
            resultado="ESTABLE - TIENDE A VAPOR"
        elif esTrivL:
            resultado="ESTABLE - TIENDE A LIQUIDO"
        else:
            resultado="ESTABLE - FASE INDETERMINADA"

    return {"resultado":resultado,"inestable":inestable,"Ki_flash":Ki_flash,
            "Sv":Sv,"Sl":Sl,"Kv":Kv,"Kl":Kl,"iter":it+1}

# ══ Flash Muskat-McDowell ════════════════════════════════════
def flash_muskat(z,T,P,Ki_init,kij,tol=1e-16,max_iter=1000,metodo_densidad='EOS'):
    """
    Réplica EXACTA de la macro CalculoFlash:
    - Si ΣKi·zi ≤ 1 → fase única LÍQUIDA (x=z, y=0)
    - Si Σzi/Ki ≤ 1 → fase única VAPOR  (x=0, y=z)
    - Resto: flash bifásico
    Cuando una fase es evanescente (composición cero), su coeficiente de
    fugacidad es φ=1 para todos sus componentes (igual que el Excel con A=B=0),
    de modo que los Ki = φ_l/φ_v no colapsan a la solución trivial y la fase
    la determinan únicamente los sumatorios (fórmula D188), sin ningún supuesto.
    """
    K=list(Ki_init)

    x=list(z); y=list(z); V=1.0; L=0.0; modo="vapor_unico"
    for it in range(max_iter):
        # Criterio del Excel (fórmula D188 con K176=zi·Ki, L176=zi/Ki)
        sumKz=sum(z[i]*K[i] for i in range(NC))      # Σ(zi·Ki)
        sumZK=sum(z[i]/K[i] if K[i]>0 else 1e30 for i in range(NC))  # Σ(zi/Ki)

        if sumKz<=1.0:
            # Toda fase LÍQUIDA: xi=zi, yi=0  (I176/J176 con primera rama)
            x=list(z); y=[0.0]*NC
            V=0.0; L=1.0
            modo="liquido_unico"
        elif sumZK<=1.0:
            # Toda fase VAPOR: xi=0, yi=zi  (I176/J176 con segunda rama)
            x=[0.0]*NC; y=list(z)
            V=1.0; L=0.0
            modo="vapor_unico"
        else:
            # Bifásico
            V=solve_V(z,K)
            V=max(1e-10,min(1-1e-10,V))
            L=1-V
            x=[z[i]/(1+V*(K[i]-1)) for i in range(NC)]
            y=[K[i]*x[i]            for i in range(NC)]
            modo="bifasico"

        # Coeficientes de fugacidad de cada fase.
        # RÉPLICA EXACTA del Excel: cuando una fase es evanescente (composición
        # cero) su A=B=0, la raíz Z degenera y el coeficiente de fugacidad
        # resulta φ=1 para todos sus componentes (ln φ = 0). NO se evalúa con
        # la composición de la otra fase. Así Ki = φ_l/φ_v queda distinto de 1
        # (Ki = 1/φ_v si falta líquido, o Ki = φ_l si falta vapor) y sostiene
        # la clasificación sin colapsar a la solución trivial.
        sy=sum(y); sx=sum(x)
        y_n=[yi/sy for yi in y] if sy>1e-30 else [0.0]*NC
        x_n=[xi/sx for xi in x] if sx>1e-30 else [0.0]*NC

        if sy>1e-30:
            amv=am(y_n,T,kij); bmv=bm(y_n)
            ZVc,_=solve_Z(*AB(amv,bmv,T,P))
            phi_v=[phi_i(i,y_n,T,P,ZVc,amv,bmv,kij) for i in range(NC)]
        else:
            phi_v=[1.0]*NC      # vapor evanescente → φ_v = 1

        if sx>1e-30:
            aml=am(x_n,T,kij); bml=bm(x_n)
            _,ZLc=solve_Z(*AB(aml,bml,T,P))
            phi_l=[phi_i(i,x_n,T,P,ZLc,aml,bml,kij) for i in range(NC)]
        else:
            phi_l=[1.0]*NC      # líquido evanescente → φ_l = 1

        fug_v=[phi_v[i]*y[i]*P for i in range(NC)]
        fug_l=[phi_l[i]*x[i]*P for i in range(NC)]

        # Restricción de igualdad de fugacidades
        restr=[]
        for i in range(NC):
            if fug_v[i]>1e-30 and fug_l[i]>1e-30:
                restr.append(np.log(fug_l[i]/fug_v[i]))
            else:
                restr.append(0)

        errorMax=max(abs(r) for r in restr) if restr else 0
        if errorMax<=tol and it>5:
            break

        # Actualizar Ki = φ_liquido / φ_vapor (idéntico al Excel T113)
        K_new=[]
        for i in range(NC):
            if phi_v[i]>1e-30:
                K_new.append(phi_l[i]/phi_v[i])
            else:
                K_new.append(K[i])
        K_new=[max(1e-20,min(1e20,k)) for k in K_new]
        K=K_new

    # ── Determinación final del modo ────────────────────────────
    # El modo (vapor_unico / liquido_unico / bifasico) y las composiciones
    # x, y, V, L ya quedaron fijados DENTRO del bucle, exactamente con el
    # criterio del Excel (fórmula D188 / I176 / J176):
    #     Σ(zi·Ki) ≤ 1 → toda líquida   (xi=zi, yi=0,  Fv=0)
    #     Σ(zi/Ki) ≤ 1 → toda vapor      (xi=0,  yi=zi, Fv=1)
    #     en otro caso → bifásico (Rachford-Rice)
    sumKz=sum(z[i]*K[i] for i in range(NC))
    sumZK=sum(z[i]/K[i] if K[i]>0 else 1e30 for i in range(NC))

    # ── Ajuste para REGIÓN SUPERCRÍTICA (estilo HYSYS) ──────────
    # El criterio D188 del Excel es un test LOCAL de fugacidades: compara la
    # mezcla global contra una fase candidata evanescente. Es exacto en la
    # región de saturación normal, pero en la región supercrítica profunda
    # (presión muy por encima de Pc, sin curva de saturación de referencia)
    # ese test local puede etiquetar erróneamente como "líquido" un fluido
    # que en realidad es gas denso.
    #
    # ── Ajuste para REGIÓN SUPERCRÍTICA (calibrado con HYSYS real) ──
    # El criterio D188 del Excel es un test LOCAL de fugacidades: compara la
    # mezcla global contra una fase candidata evanescente. Es exacto en la
    # región de saturación normal, pero en la región supercrítica profunda
    # (presión muy por encima de Pc, sin curva de saturación de referencia)
    # ese test local puede etiquetar erróneamente como "líquido" un fluido
    # que en realidad es gas denso.
    #
    # Este ajuste sólo se activa cuando el FLASH YA CONVERGIÓ a una fase única
    # (modo vapor_unico o liquido_unico, decidido por D188) — nunca se aplica
    # en bifásico, así que no interfiere con la separación real de fases. La
    # condición de "supercrítico genuino" se verifica con la raíz de la fase
    # única resultante: si la EOS evaluada con esa composición (que es z, ya
    # que toda la mezcla quedó en una sola fase) tiene una sola raíz real, es
    # un fluido supercrítico sin curva de saturación de referencia.
    #
    # Criterio aplicado (ver docstring de fase_supercritica): reglas del
    # manual oficial de HYSYS (Z>0.3∧β>0.75 → vapor, o Z>0.75∧ligeros>
    # pesados → vapor, sino líquido), con β=P·κ y κ derivada analítica de
    # PR. Sin ajustes por composición ni por caso: los umbrales 0.3 y 0.75
    # son constantes del manual. Validado contra 5 puntos de HYSYS directos
    # (C1/C2 90/10 a 350°R,1000 psi y a 2000 psi con T=400,433,434,450°R)
    # más 3 puntos de gas seco a 620°R (3000, 8000, 15000 psi).
    if modo in ("vapor_unico","liquido_unico"):
        am_glob=am(z,T,kij); bm_glob=bm(z)
        ZVg,ZLg=solve_Z(*AB(am_glob,bm_glob,T,P))
        if abs(ZVg-ZLg)<1e-7:
            # Una sola raíz real → fluido supercrítico genuino (no hay
            # segunda fase candidata con la que el test D188 pueda comparar
            # de forma confiable).
            # Identificacion de fase de la raiz unica:
            #  - EOS PVTsim -> criterio de PVTsim (Tc/Pc de la mezcla)
            #  - EOS HYSYS  -> algoritmo de HYSYS (umbrales Z/beta), intacto
            if es_pvtsim(_EOS_ACTIVA):
                fase_sc = fase_pvtsim(z, T, P, ZVg, kij)
            else:
                fase_sc = fase_supercritica(z, T, P, ZVg, kij)
            if fase_sc=="vapor" and modo!="vapor_unico":
                x=[0.0]*NC; y=list(z); V=1.0; L=0.0; modo="vapor_unico"
            elif fase_sc=="liquido" and modo!="liquido_unico":
                x=list(z); y=[0.0]*NC; V=0.0; L=1.0; modo="liquido_unico"

    # ── Propiedades finales ─────────────────────────────────
    PM_v = sum(y[i]*PM[i] for i in range(NC)) if V>0 else 0.0
    PM_l = sum(x[i]*PM[i] for i in range(NC)) if L>0 else 0.0
    PM_z = sum(z[i]*PM[i] for i in range(NC))
    
    # Si el flash bifásico devolvió fases invertidas (vapor con PM mayor que líquido),
    # intercambiar etiquetas para mantener convención: vapor=fase liviana
    if modo=="bifasico" and V>0 and L>0 and PM_v>PM_l:
        x,y = y,x
        V,L = L,V
        PM_v,PM_l = PM_l,PM_v
        K = [1.0/k if k>1e-30 else 1e30 for k in K]
    # Calcular fracciones másicas con valores definitivos
    den_m = V*PM_v+L*PM_l if (V*PM_v+L*PM_l)>0 else 1
    Vm = V*PM_v/den_m if V>0 else 0.0
    Lm = L*PM_l/den_m if L>0 else 0.0

    ZV_fin = None; ZL_fin = None
    rho_v = None; rho_l = None
    sg_v = None; sg_l = None

    if V>0 and PM_v>0:
        am_v=am(y,T,kij); bm_v=bm(y)
        ZV_fin,_=solve_Z(*AB(am_v,bm_v,T,P))
        rho_v=P*PM_v/(ZV_fin*R_GAS*T)
        sg_v=PM_v/28.9625
    if L>0 and PM_l>0:
        am_l=am(x,T,kij); bm_l=bm(x)
        ZVL_l, ZLL_l = solve_Z(*AB(am_l,bm_l,T,P))
        ZL_fin = ZLL_l
        # ρ por EOS de Peng-Robinson (siempre calculable).  Es el default
        # cuando el usuario pide método='EOS' y también el fallback cuando
        # la correlación COSTALD no es aplicable en el estado (T,P) actual.
        rho_l_EOS = P*PM_l/(ZL_fin*R_GAS*T)

        # Algoritmo HYSYS "Smooth Liquid Density" (activado por default con
        # COSTALD).  El criterio de aplicabilidad de COSTALD+Chueh-Prausnitz
        # NO es el número de raíces de PR sino la temperatura reducida de
        # la mezcla (documentado literalmente en el manual, sec. A.4.1):
        #
        #   "It is used to predict the density for all systems whose
        #    pseudo-reduced temperature is below 1.0.  Above this
        #    temperature, the equation of state compressibility factor is
        #    used to calculate the liquid density."
        #
        # Con Smooth Liquid Density activo, HYSYS suaviza la transición
        # interpolando en la banda Tr ∈ [0.90, 1.00] con perfil CUADRÁTICO
        # w = t², donde t = (Tr−0.90)/0.10.  Los valores 0.90 y "cuadrático"
        # se identificaron por backward-fitting contra cuatro puntos HYSYS
        # verificados (C1/C2 90/10 a T=300°R,P=4000/6000; y T=350°R,
        # P=2000/5000), que quedan con error < 1% en densidad y factor Z
        # con esa combinación — la interpolación lineal en [0.95,1.00] que
        # documenta un manual antiguo de Aspen deja error residual de ~2%.
        # Las cotas Tr y la forma cuadrática son constantes universales
        # (identificadas del comportamiento observado de HYSYS), no
        # calibradas por composición ni por punto.
        #
        # Ramas:
        #   Tr < 0.90         → COSTALD saturado + Chueh-Prausnitz
        #   0.90 ≤ Tr ≤ 1.00  → interpolación cuadrática COSTALD_CP ↔ EOS
        #   Tr > 1.00         → EOS  (V_liq_costald_smooth retorna None)
        #
        # El caso "P < Ps" (presión subsaturada) está manejado dentro de
        # V_liq_costald_smooth: devuelve Vs sin corrección de presión.
        if metodo_densidad == 'COSTALD':
            mix = _costald_mix_params(x)
            V_liq = V_liq_costald_smooth(x, T, P, kij=kij) if mix is not None else None
            if V_liq is not None and V_liq > 0 and mix is not None:
                # ρ y Z de COSTALD+Chueh-Prausnitz
                rho_l_CP = PM_l/V_liq
                ZL_CP    = P*V_liq/(R_GAS*T)
                Tcm = mix[0]
                Tr  = T/Tcm
                if Tr < 0.90:
                    rho_l  = rho_l_CP
                    ZL_fin = ZL_CP
                else:
                    # Interpolación cuadrática entre CP (Tr=0.90) y EOS (Tr=1.00)
                    t = min(max((Tr - 0.90)/0.10, 0.0), 1.0)
                    w_EOS = t*t
                    w_CP  = 1.0 - w_EOS
                    rho_l  = w_CP*rho_l_CP + w_EOS*rho_l_EOS
                    ZL_fin = w_CP*ZL_CP    + w_EOS*ZLL_l
            else:
                # Tr ≥ 1 o mixing rule COSTALD falla → EOS
                rho_l = rho_l_EOS
        else:
            # Método EOS explícitamente pedido
            rho_l = rho_l_EOS
        sg_l=rho_l/62.4  # SG líquido respecto al agua

    den_m = V*PM_v+L*PM_l if (V*PM_v+L*PM_l)>0 else 1
    Vm = V*PM_v/den_m if V>0 else 0.0
    Lm = L*PM_l/den_m if L>0 else 0.0

    return {
        "V":V,"L":L,"Vm":Vm,"Lm":Lm,
        "x":x,"y":y,"z":list(z),"K":K,
        "ZV":ZV_fin,"ZL":ZL_fin,
        "PM_v":PM_v if V>0 else None,
        "PM_l":PM_l if L>0 else None,
        "PM_z":PM_z,
        "rho_v":rho_v,"rho_l":rho_l,
        "sg_v":sg_v,"sg_l":sg_l,
        "modo":modo,
        "iter":it+1,
        "sumKz":sumKz,"sumZK":sumZK
    }

# ══ Punto de entrada ═════════════════════════════════════════
def fase_pvtsim(z, T, P, Z, kij):
    """Identificacion de fase de una sola raiz real segun el criterio de
    PVTsim (Method Documentation, "Phase Identification"):

        Liquido si  (P < Pc y T < T_burbuja)  o  (P >= Pc y T < Tc)
        Gas     si  (P < Pc y T > T_rocio)    o  (P >= Pc y T > Tc)

    Usa el PUNTO CRITICO REAL de la mezcla (Pc, Tc) calculado con la EOS
    activa (no el pseudocritico de Kay, que erraba la frontera; p.ej. 90%
    C1/10% C2 a 3000 psia cambia a -82 °F, no a -96 °F). Si el punto critico
    no converge, cae al pseudocritico de Kay como respaldo."""
    Tcm = Pcm = None
    try:
        import critico
        c = critico.punto_critico(z, kij)
        if c is not None:
            Pcm, Tcm = c[0], c[1]
    except Exception:
        Tcm = Pcm = None
    if Tcm is None:                     # respaldo: pseudocritico de Kay
        TCa, PCa, _om, _pm = crit_props(_EOS_ACTIVA)
        Tcm = sum(z[i] * TCa[i] for i in range(NC))
        Pcm = sum(z[i] * PCa[i] for i in range(NC))
    return "liquido" if T < Tcm else "vapor"


def calcular(z,T,P,kij=None,metodo_densidad='EOS'):
    """
    Réplica de Sub AnalisisYFlash():
    1. Análisis de estabilidad de Michelsen
    2. SIEMPRE se corre el flash con los Ki del análisis
       (sea estable o inestable, como hace el usuario en el Excel)
    """
    if kij is None:
        kij = kij_base(_EOS_ACTIVA)
    estab=analisis_estabilidad(z,T,P,kij)

    # Réplica EXACTA de la macro AnalisisYFlash:
    #   • Si INESTABLE → el flash arranca con Ki = Kv·Kl (O427:O439)
    #   • Si ESTABLE   → el flash arranca con Ki de Wilson (D273:D285)
    # En ambos casos SIEMPRE se corre el flash a continuación.
    if estab["inestable"]:
        Ki_arranque=list(estab["Ki_flash"])          # Kv·Kl
    else:
        Ki_arranque=[Ki_wilson(i,T,P) for i in range(NC)]   # Wilson

    flash=flash_muskat(z,T,P,Ki_arranque,kij,metodo_densidad=metodo_densidad)
    flash["estabilidad"]=estab["resultado"]
    flash["iter_estab"]=estab["iter"]
    flash["inestable"]=estab["inestable"]
    return flash

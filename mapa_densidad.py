"""
mapa_densidad.py — Mapa de densidad + curva de transición monofásica
=====================================================================

Genera el "background" del diagrama P-T como un mapa continuo de
densidad estilo Whitson.  El coloreado se calcula en TODA la malla T×P
(sin enmascarar el interior de la envolvente), y es responsabilidad de
la capa de dibujo (pestana_envolvente.py) tapar el interior con un fill
continuo del polígono envolvente para evitar los escalones de píxeles.

Retorno principal (calcular_mapa_densidad):
  - rho_map     : densidad kg/m³ en cada nodo de la malla (todos los
                  puntos evaluados, sin NaN dentro)
  - poly_env_TP : polígono cerrado de la envolvente en formato (T°R, P psia),
                  utilizable como argumento de matplotlib.patches.Polygon
                  o ax.fill(...) para tapar el interior con un color de
                  fondo (por ejemplo gris tenue)
  - curva_T, curva_P : línea de transición monofásica LIQ↔VAP en el
                       régimen supercrítico (para dibujar como continua
                       fina)

Elección de raíz para la densidad:
  - Dos raíces reales (cerca de la envolvente): la de energía de Gibbs
    mínima, que corresponde al estado estable
  - Una raíz real (lejos de la envolvente): esa raíz
  - Raíz de líquido con Tr_COSTALD < 1: se aplica Smooth Liquid Density
    (COSTALD + Chueh-Prausnitz + banda smooth) del engine, consistente
    con HYSYS
"""
import numpy as np
import eos as e


# ── Densidad en un punto ────────────────────────────────────────
def _rho_kgm3_en_punto(z, T, P, kij, PM, metodo='COSTALD'):
    """Densidad kg/m³ de la fase estable en (T,P) para la composición z.

    El parámetro `metodo` selecciona la ruta de densidad de líquido:
    'COSTALD' (estados correspondientes con suavizado), 'Peneloux'
    (traslado de volumen sobre la EOS) o 'EOS' (ecuación de estado).

    En puntos con dos raíces reales de PR (dentro y cerca de la
    envolvente), elige la raíz de Gibbs mínimo, que corresponde al
    estado termodinámicamente estable.  El resultado numérico dentro de
    la envolvente NO se muestra al usuario (queda tapado por el fill
    gris del polígono envolvente), pero se calcula para que el imshow
    tenga valores continuos y no genere escalones cerca del borde.
    """
    R = e.R_GAS
    am_ = e.am(z, T, kij); bm_ = e.bm(z)
    A, B = e.AB(am_, bm_, T, P)
    ZV, ZL = e.solve_Z(A, B)
    dos_raices = abs(ZV - ZL) > 1e-7
    if dos_raices:
        try:
            phi_V = [e.phi_i(i, z, T, P, ZV, am_, bm_, kij) for i in range(e.NC)]
            phi_L = [e.phi_i(i, z, T, P, ZL, am_, bm_, kij) for i in range(e.NC)]
            G_V = sum(z[i]*np.log(max(phi_V[i]*z[i], 1e-300))
                      for i in range(e.NC) if z[i] > 0)
            G_L = sum(z[i]*np.log(max(phi_L[i]*z[i], 1e-300))
                      for i in range(e.NC) if z[i] > 0)
            liquido = (G_L < G_V)
        except Exception:
            liquido = (ZL < 0.35)
    else:
        liquido = (e.fase_supercritica(z, T, P, ZV, kij) == "liquido")

    if liquido:
        # EOS puro: densidad de la ecuación de estado
        if metodo == 'EOS':
            Z_use = ZL if dos_raices else ZV
            rho_lbft3 = P*PM/(Z_use*R*T)
        # Peneloux: traslado de volumen sobre el volumen de la EOS
        elif metodo == 'Peneloux':
            Z_use = ZL if dos_raices else ZV
            V_eos = Z_use*R*T/P
            V_pen = e.V_liq_peneloux(z, V_eos)
            rho_lbft3 = PM/V_pen if V_pen > 0 else P*PM/(Z_use*R*T)
        else:
            mix = e._costald_mix_params(z)
            if mix is not None:
                Tcm = mix[0]
                Tr = T/Tcm
                if Tr >= 1.0:
                    # Región supercrítica en T: densidad por la EOS
                    Z_use = ZL if dos_raices else ZV
                    rho_lbft3 = P*PM/(Z_use*R*T)
                elif Tr <= 0.95:
                    # COSTALD con corrección de líquido comprimido
                    V_liq = e.V_liq_costald_smooth(z, T, P, kij=kij)
                    if V_liq is not None and V_liq > 0:
                        rho_lbft3 = PM/V_liq
                    else:
                        Z_use = ZL if dos_raices else ZV
                        rho_lbft3 = P*PM/(Z_use*R*T)
                else:
                    # Banda de transición 0.95 < Tr < 1.0: interpolación con
                    # perfil cuadrático entre la densidad de líquido en Tr=0.95
                    # (COSTALD) y la densidad de la EOS en Tr=1.0.
                    T95 = 0.95*Tcm
                    V95 = e.V_liq_costald_smooth(z, T95, P, kij=kij)
                    if V95 is not None and V95 > 0:
                        rho95 = PM/V95
                    else:
                        am95 = e.am(z, T95, kij); bm95 = e.bm(z)
                        _, ZL95 = e.solve_Z(*e.AB(am95, bm95, T95, P))
                        rho95 = P*PM/(ZL95*R*T95)
                    T100 = Tcm
                    am100 = e.am(z, T100, kij); bm100 = e.bm(z)
                    _, ZL100 = e.solve_Z(*e.AB(am100, bm100, T100, P))
                    rho100 = P*PM/(ZL100*R*T100)
                    frac = (Tr - 0.95)/(1.0 - 0.95)
                    rho_lbft3 = rho95 + (rho100 - rho95)*frac*frac
            else:
                Z_use = ZL if dos_raices else ZV
                rho_lbft3 = P*PM/(Z_use*R*T)
    else:
        Z_use = ZV
        rho_lbft3 = P*PM/(Z_use*R*T)
        # Corrección de volumen de Peneloux en la fase vapor
        if metodo == 'Peneloux':
            V_eos = Z_use*R*T/P
            V_pen = e.V_liq_peneloux(z, V_eos)
            if V_pen > 0:
                rho_lbft3 = PM/V_pen

    return rho_lbft3   # unidades del programa (lb/ft³)


# ── Curva de transición monofásica ──────────────────────────────
def _fase_hysys_manual(z, T, P, kij):
    am_ = e.am(z, T, kij); bm_ = e.bm(z)
    ZV, _ = e.solve_Z(*e.AB(am_, bm_, T, P))
    return e.fase_supercritica(z, T, P, ZV, kij)


def calcular_curva_transicion(z, kij, P_min, P_max, n_pts=40,
                              T_lo=10.0, T_hi=2500.0):
    """Curva T(P) por bisección: separa LIQ↔VAP con el criterio HYSYS
    del manual, para trazar la línea negra fina."""
    Ts, Ps = [], []
    for P in np.linspace(P_min, P_max, n_pts):
        f_lo = _fase_hysys_manual(z, T_lo, P, kij)
        f_hi = _fase_hysys_manual(z, T_hi, P, kij)
        if f_lo == f_hi: continue
        lo, hi = T_lo, T_hi
        for _ in range(60):
            mid = 0.5*(lo + hi)
            if _fase_hysys_manual(z, mid, P, kij) == f_lo: lo = mid
            else: hi = mid
        Ts.append(0.5*(lo + hi)); Ps.append(P)
    return {'T': np.array(Ts), 'P': np.array(Ps)}


# ── Polígono envolvente para el fill gris ───────────────────────
def _envolvente_polygon_TP(resultado_env):
    """Polígono cerrado suave de la envolvente en (T°R, P psia).

    Usa el ORDEN NATURAL con el que el algoritmo (Ziervogel o Michelsen)
    recorre continuamente el envelope: primer extremo → línea de burbuja
    → punto crítico → línea de rocío → segundo extremo.  matplotlib
    cierra el polígono automáticamente uniendo el último punto con el
    primero, que ambos están en la base del envelope a baja P, así que
    el cierre es una línea recta corta que representa la "base".

    IMPORTANTE: no invertir la rocío.  Ambas listas ya vienen en orden
    de recorrido continuo: burbuja[-1] ≈ rocío[0] ≈ crítico.  Invertir
    la rocío hace que el polígono se auto-cruce (recorre A→crítico→Z→
    crítico→A formando una "X"), lo que confunde al motor de fill de
    matplotlib y termina rellenando todo el rectángulo del gráfico.

    Retorna None si no hay suficientes puntos.
    """
    burb = resultado_env.get('burbuja', []) or []
    roc  = resultado_env.get('rocio', []) or []
    if not burb and not roc: return None
    poly = []
    for pt in burb:
        poly.append((pt[1], pt[0]))     # (T°R, Ppsia)
    for pt in roc:
        poly.append((pt[1], pt[0]))
    if len(poly) < 3: return None
    return np.array(poly)


# ── Función principal ───────────────────────────────────────────
def calcular_mapa_densidad(z, kij, resultado_env, n_grid=100, n_curva=40,
                           progress_cb=None, metodo='COSTALD'):
    """Genera el mapa de densidad + polígono envolvente + curva de
    transición.  Todo en un solo paso para minimizar el ida-y-vuelta
    con el worker.

    Retorna dict con:
      'P_max'        : P máxima recomendada del gráfico (psia)
      'T_range'      : (T_min, T_max) del gráfico (°R)
      'rho_map'      : array 2D (n_grid, n_grid) densidad kg/m³ en TODA
                       la malla — sin NaN interior
      'Tg', 'Pg'     : ejes de la malla (°R y psia)
      'poly_env_TP'  : polígono cerrado envolvente (T°R, Ppsia) o None
      'curva_T'      : temperaturas de la curva de transición (°R)
      'curva_P'      : presiones de la curva de transición (psia)
      'Tc_Kay'       : Tc pseudocrítica de Kay (°R)
      'Pc_Kay'       : Pc pseudocrítica de Kay (psia)
      'cricondembar' : cricondembar detectado (psia)
    """
    burb = resultado_env.get('burbuja', []) or []
    roc  = resultado_env.get('rocio', []) or []
    Ps_env = [pt[0] for pt in burb] + [pt[0] for pt in roc]
    Ts_env = [pt[1] for pt in burb] + [pt[1] for pt in roc]
    Pmax_env = max(Ps_env) if Ps_env else 0.0
    Tmax_env = max(Ts_env) if Ts_env else 500.0
    Tmin_env = min(Ts_env) if Ts_env else 100.0
    Tc_Kay = sum(z[i]*e.TC[i] for i in range(e.NC))
    Pc_Kay = sum(z[i]*e.PC[i] for i in range(e.NC))
    P_max = 1.5 * max(Pmax_env, Pc_Kay)
    T_min = max(50.0, Tmin_env - 50.0)
    T_max = Tmax_env + 100.0
    PM = sum(z[i]*e.PM[i] for i in range(e.NC))

    if progress_cb: progress_cb(5, "Preparando malla…")

    Tg = np.linspace(T_min, T_max, n_grid)
    Pg = np.linspace(10.0, P_max, n_grid)

    # Densidad en TODOS los puntos (sin máscara).  Los puntos dentro de
    # la envolvente reciben un valor válido (raíz de Gibbs mínimo), pero
    # no se mostrarán al usuario: el fill gris del polígono los tapa.
    if progress_cb: progress_cb(15, "Calculando densidad en la malla…")
    rho_map = np.zeros((n_grid, n_grid), dtype=np.float32)
    N_total = n_grid*n_grid
    N_done = 0
    for j, P in enumerate(Pg):
        for i, T in enumerate(Tg):
            try:
                rho_map[j, i] = _rho_kgm3_en_punto(z, float(T), float(P), kij, PM, metodo)
            except Exception:
                rho_map[j, i] = np.nan
            N_done += 1
        if progress_cb and (j % 10 == 0):
            pct = 15 + int(70 * N_done / N_total)
            progress_cb(pct, "Calculando densidad…")

    if progress_cb: progress_cb(88, "Ensamblando envolvente y transición…")
    poly = _envolvente_polygon_TP(resultado_env)
    P_min_curva = max(Pmax_env * 1.01, 10.0)
    curva = calcular_curva_transicion(z, kij, P_min_curva, P_max, n_pts=n_curva)

    if progress_cb: progress_cb(100, "Listo")
    return {
        'P_max': P_max,
        'T_range': (T_min, T_max),
        'rho_map': rho_map,
        'Tg': Tg, 'Pg': Pg,
        'poly_env_TP': poly,
        'curva_T': curva['T'], 'curva_P': curva['P'],
        'Tc_Kay': Tc_Kay, 'Pc_Kay': Pc_Kay,
        'cricondembar': Pmax_env,
    }


ejecutar_completo = calcular_mapa_densidad

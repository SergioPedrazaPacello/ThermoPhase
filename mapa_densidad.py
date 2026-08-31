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
    """Polígono cerrado de la zona bifásica en (T°R, P psia).

    Usa el recorrido natural: burbuja (sin la cola de alta presión) →
    punto crítico → rocío.  La COLA VERTICAL (el tramo de la rama de
    burbuja por encima del codo, donde P > P_codo) no encierra zona
    bifásica real y se excluye para evitar que el polígono se desborde
    fuera de las curvas en esa región. El resto de la burbuja y toda la
    rocío se incluyen tal como estaban antes.

    Retorna None si no hay suficientes puntos.
    """
    burb = resultado_env.get('burbuja', []) or []
    roc  = resultado_env.get('rocio',   []) or []
    if not burb and not roc:
        return None

    lazo = burb   # por defecto: toda la burbuja (envolventes normales)
    if burb:
        Pmax_env = max([pt[0] for pt in burb] + ([pt[0] for pt in roc] if roc else []))
        Ptop = burb[0][0]
        if Ptop > 0.5 * Pmax_env:            # envolvente con cola de alta P
            i_codo = min(range(len(burb)), key=lambda i: burb[i][0])
            lazo = burb[i_codo:]             # solo del codo al crítico

    poly = [(pt[1], pt[0]) for pt in lazo]   # (T°R, P psia)
    poly += [(pt[1], pt[0]) for pt in roc]
    if len(poly) < 3:
        return None
    return np.array(poly)


# ── Contorno cerrado de la envolvente trazada (burbuja + rocío) ─────────────
def _contorno_env_TP(resultado_env):
    """Contorno cerrado de la envolvente TRAZADA en (T°R, P psia).

    A diferencia de `_envolvente_polygon_TP` (que RECORTA la cola de alta
    presión para el fill gris de las envolventes normales), aquí se usa el
    recorrido COMPLETO tal como lo dibujan las curvas de burbuja y rocío,
    INCLUYENDO la cola de alta presión. burbuja va (P baja → cola → crítico)
    y rocío va (crítico → P baja); concatenadas forman un lazo cerrado,
    ordenado y sin auto-intersección, que coincide exactamente con lo que
    ve el usuario. Sirve para confinar el sombreado gris (mask_bif) al
    interior real del trazado y evitar que se desborde por la cola.

    Retorna un array (N,2) en (T°R, P psia) o None si no hay puntos.
    """
    burb = resultado_env.get('burbuja', []) or []
    roc  = resultado_env.get('rocio',   []) or []
    if not burb and not roc:
        return None
    # burbuja: (P,T) en orden P baja → crítico; rocío: (P,T) crítico → P baja.
    # El primer punto de rocío suele coincidir con el crítico (último de
    # burbuja); se omite para no duplicar el vértice de la cúspide.
    loop = list(burb)
    if roc:
        loop += list(roc[1:]) if burb else list(roc)
    if len(loop) < 3:
        return None
    poly = np.array([(pt[1], pt[0]) for pt in loop], dtype=float)  # (T°R, P)
    return poly


def _mascara_dentro_contorno(poly_TP, Tg_R, Pg):
    """Máscara booleana (len(Pg), len(Tg_R)) True dentro del contorno.

    Test punto-en-polígono por ray casting vectorizado sobre toda la malla.
    poly_TP en (T°R, P psia); Tg_R en °R; Pg en psia. El resultado usa el
    mismo orden de índices que rho_map / mask_bif: [j (P), i (T)].
    """
    Tx = poly_TP[:, 0]
    Py = poly_TP[:, 1]
    n  = len(poly_TP)
    Tm, Pm = np.meshgrid(Tg_R, Pg)          # (nP, nT)
    dentro = np.zeros(Tm.shape, dtype=bool)
    j = n - 1
    for i in range(n):
        Ti, Pi = Tx[i], Py[i]
        Tj, Pj = Tx[j], Py[j]
        # ¿el segmento (i,j) cruza el rayo horizontal a P=Pm hacia -T?
        cond = ((Pi > Pm) != (Pj > Pm))
        denom = (Pj - Pi)
        denom = np.where(np.abs(denom) < 1e-30, 1e-30, denom)
        Tcross = Ti + (Tj - Ti) * (Pm - Pi) / denom
        dentro ^= (cond & (Tm < Tcross))
        j = i
    return dentro


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
    # Si la envolvente alcanzó el techo práctico (~10000 psia, rama de alta
    # presión), el mapa se capa justo por encima de ese techo (no tiene sentido
    # mostrar espacio vacío por arriba). En mezclas normales se deja el margen
    # habitual del 50 % sobre la P máxima.
    if Pmax_env >= 9500.0:
        P_max = Pmax_env * 1.02
        # Envolvente abierta (rama vertical de burbuja a baja T): el grid empieza
        # justo en la rama, sin margen a la izquierda, para que no quede una
        # franja coloreada (líquido) a la izquierda de la zona sombreada.
        T_min = Tmin_env
    else:
        P_max = 1.5 * max(Pmax_env, Pc_Kay)
        T_min = max(50.0, Tmin_env - 50.0)
    T_max = Tmax_env + 100.0
    PM = sum(z[i]*e.PM[i] for i in range(e.NC))

    if progress_cb: progress_cb(5, "Preparando malla…")

    Tg = np.linspace(T_min, T_max, n_grid)
    Pg = np.linspace(10.0, P_max, n_grid)

    # Densidad en TODOS los puntos (sin máscara). Simultáneamente se
    # construye mask_bif: True donde el sistema es bifásico (inestable),
    # que es exactamente el área que debe sombrearse en gris. Se usa
    # analisis_estabilidad con pocos iteraciones (solo necesitamos el
    # veredicto inestable/estable, no el flash completo).
    if progress_cb: progress_cb(15, "Calculando densidad en la malla…")
    rho_map  = np.zeros((n_grid, n_grid), dtype=np.float32)
    mask_bif = np.zeros((n_grid, n_grid), dtype=bool)
    N_total = n_grid * n_grid
    N_done  = 0
    for j, P in enumerate(Pg):
        for i, T in enumerate(Tg):
            try:
                rho_map[j, i] = _rho_kgm3_en_punto(z, float(T), float(P), kij, PM, metodo)
            except Exception:
                rho_map[j, i] = np.nan
            try:
                est = e.analisis_estabilidad(z, float(T), float(P), kij, max_iter=30)
                mask_bif[j, i] = bool(est.get('inestable', False))
            except Exception:
                mask_bif[j, i] = False
            N_done += 1
        if progress_cb and (j % 10 == 0):
            pct = 15 + int(70 * N_done / N_total)
            progress_cb(pct, "Calculando densidad…")

    # ── Confinar el sombreado gris al interior del trazado real ──────────────
    # El test de estabilidad (mask_bif) puede marcar como inestables celdas
    # que caen FUERA del contorno trazado por burbuja/rocío, en especial en la
    # "cola" de alta presión de las mezclas con metano + pesados (nonano,
    # octano, heptano): ahí el gris se desbordaba a la izquierda de la rama de
    # burbuja. Se intersecta mask_bif con el interior del contorno COMPLETO
    # (burbuja con cola + rocío) para que el sombreado coincida exactamente
    # con la envolvente dibujada. En envolventes normales el contorno contiene
    # toda la zona inestable, así que este recorte no cambia nada.
    contorno = _contorno_env_TP(resultado_env)
    if contorno is not None and mask_bif.any():
        try:
            dentro = _mascara_dentro_contorno(contorno, Tg, Pg)
            mask_bif &= dentro
        except Exception:
            pass

    # ── Envolvente abierta: blanquear a la izquierda de la burbuja ───────────
    if Pmax_env >= 9500.0 and burb and len(burb) >= 2:
        Pb = np.array([pt[0] for pt in burb])
        Tb = np.array([pt[1] for pt in burb])
        for j, P in enumerate(Pg):
            Tcru = []
            for k in range(len(burb) - 1):
                p0, p1 = Pb[k], Pb[k+1]
                if p0 != p1 and (p0 - P) * (p1 - P) <= 0.0:
                    f = (P - p0) / (p1 - p0)
                    Tcru.append(Tb[k] + f * (Tb[k+1] - Tb[k]))
            if Tcru:
                rho_map[j, Tg < min(Tcru)] = np.nan

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
        'mask_bif': mask_bif,
        'curva_T': curva['T'], 'curva_P': curva['P'],
        'Tc_Kay': Tc_Kay, 'Pc_Kay': Pc_Kay,
        'cricondembar': Pmax_env,
    }


ejecutar_completo = calcular_mapa_densidad

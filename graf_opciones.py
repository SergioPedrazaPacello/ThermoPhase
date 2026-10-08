"""
graf_opciones.py — Opciones globales de los gráficos (menú Gráficos).

  • MARCADORES: muestra u oculta los triángulos sobre las curvas de la
    envolvente y de la comparación de envolventes (las curvas quedan como
    línea continua).  No afecta al recorrido de P y T ni a los puntos
    especiales (punto crítico, punto marcado).
  • ETIQUETAS: en lugar de marcar todos los puntos, marca solo algunos
    (repartidos a lo largo de cada curva) y escribe junto a cada uno su valor
    «eje y:eje x», sin nombre ni unidad.  Se usa en la envolvente y en el
    análisis de sensibilidad.

Uso:
    graf_opciones.curva(ax, x, y, color, label=..., etiquetar=True)
    ...                                     # (resto del gráfico)
    graf_opciones.dibujar_etiquetas(ax, fmt_x, fmt_y)   # al final, con los
                                                         # límites ya fijados
"""
import math

MARCADORES = True
ETIQUETAS = False

SEP_ETIQ = 0.16      # separación entre etiquetas a lo largo de la curva
                     # (fracción del tamaño de los ejes)
DIST_MIN = 0.07      # distancia mínima entre dos etiquetas (cualquier curva)


def curva(ax, x, y, color, label=None, lw=0.7, ms=3, z_line=2, z_mark=3,
          alpha=1.0, mark_kw=None, con_marcadores=True, etiquetar=True):
    """Dibuja una curva con el estilo vigente.  `con_marcadores=False` para
    curvas que nunca llevan triángulos (p. ej. con el mapa de densidad)."""
    marcar = con_marcadores and MARCADORES and not ETIQUETAS
    if marcar:
        ax.plot(x, y, linestyle='-', linewidth=lw, color=color, zorder=z_line,
                alpha=alpha)
        ax.plot(x, y, linestyle='none', marker='^', markersize=ms, color=color,
                label=label, zorder=z_mark, alpha=alpha, **(mark_kw or {}))
    else:
        ax.plot(x, y, linestyle='-', linewidth=lw, color=color, zorder=z_line,
                alpha=alpha, label=label)
    if ETIQUETAS and etiquetar:
        pend = getattr(ax, '_tp_etiquetas', None)
        if pend is None:
            pend = []
            ax._tp_etiquetas = pend
        pend.append((list(x), list(y), color, max(z_mark, z_line) + 1))


def limpiar(ax):
    ax._tp_etiquetas = []


def fmt_auto(v):
    """Decimales según la magnitud (presión/temperatura sin decimales)."""
    a = abs(v)
    if a >= 100:
        return f"{v:.0f}"
    if a >= 10:
        return f"{v:.1f}"
    if a >= 1:
        return f"{v:.2f}"
    if a >= 0.01:
        return f"{v:.3f}"
    if a == 0:
        return "0"
    return f"{v:.2e}"


def fmt_entero(v):
    return f"{v:.0f}"


def dibujar_etiquetas(ax, fmt_x=fmt_entero, fmt_y=fmt_entero, fontsize=7):
    """Marca algunos puntos de cada curva pendiente con un triángulo y su
    valor «y:x».  Los puntos se reparten por longitud de arco en pantalla
    (válido también con ejes logarítmicos) y se evita amontonar etiquetas."""
    pend = getattr(ax, '_tp_etiquetas', None) or []
    ax._tp_etiquetas = []
    if not pend:
        return
    bb = ax.bbox
    W = max(bb.width, 1.0); H = max(bb.height, 1.0)
    tr = ax.transData
    dpi = float(getattr(ax.figure, 'dpi', 100.0) or 100.0)
    usados = []                               # posiciones normalizadas ya usadas
    # centroide de todas las curvas (para poner el texto hacia afuera)
    curvas = []
    sx = sy = 0.0; n_tot = 0
    for x, y, col, z in pend:
        pts = []
        for xi, yi in zip(x, y):
            try:
                xi = float(xi); yi = float(yi)
            except (TypeError, ValueError):
                continue
            if not (math.isfinite(xi) and math.isfinite(yi)):
                continue
            try:
                dx, dy = tr.transform((xi, yi))
            except Exception:
                continue
            u = (dx - bb.x0) / W; v = (dy - bb.y0) / H
            if not (math.isfinite(u) and math.isfinite(v)):
                continue
            pts.append((xi, yi, u, v))
            if -0.01 <= u <= 1.01 and -0.01 <= v <= 1.01:
                sx += u; sy += v; n_tot += 1
        curvas.append((pts, col, z))
    cx, cy = (sx / n_tot, sy / n_tot) if n_tot else (0.5, 0.5)

    for pts, col, z in curvas:
        if len(pts) < 2:
            continue
        # longitud de arco acumulada en coordenadas normalizadas
        s = [0.0]
        for i in range(1, len(pts)):
            s.append(s[-1] + math.hypot(pts[i][2] - pts[i-1][2], pts[i][3] - pts[i-1][3]))
        L = s[-1]
        if L <= 1e-9:
            continue
        n = max(2, int(L / SEP_ETIQ))
        objetivos = [L * (k + 0.5) / n for k in range(n)]
        elegidos = []
        j = 0
        for st in objetivos:
            while j < len(s) - 1 and s[j] < st:
                j += 1
            elegidos.append(j)
        for i in sorted(set(elegidos)):
            xi, yi, u, v = pts[i]
            if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0):
                continue
            if any(math.hypot(u - a, v - b) < DIST_MIN for a, b in usados):
                continue
            usados.append((u, v))
            # dirección normal a la curva, hacia afuera del conjunto
            a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]
            tx, ty = b[2] - a[2], b[3] - a[3]
            m = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / m, tx / m
            if (u - cx) * nx + (v - cy) * ny < 0:
                nx, ny = -nx, -ny
            ox, oy = 7 * nx, 7 * ny
            txt = f"{fmt_y(yi)}:{fmt_x(xi)}"
            # Si el texto se saldría del área del gráfico, va al otro lado.
            px = dpi / 72.0
            ancho = (abs(ox) + 0.55 * fontsize * len(txt)) * px / W
            alto = (abs(oy) + 1.3 * fontsize) * px / H
            if ox >= 0 and u + ancho > 1.0:
                ox = -max(abs(ox), 4.0)
            elif ox < 0 and u - ancho < 0.0:
                ox = max(abs(ox), 4.0)
            if oy >= 0 and v + alto > 1.0:
                oy = -max(abs(oy), 4.0)
            elif oy < 0 and v - alto < 0.0:
                oy = max(abs(oy), 4.0)
            ax.plot([xi], [yi], linestyle='none', marker='^', markersize=4,
                    color=col, zorder=z)
            ax.annotate(txt, (xi, yi), xytext=(ox, oy),
                        textcoords='offset points', fontsize=fontsize, color=col,
                        ha='left' if ox >= 0 else 'right',
                        va='bottom' if oy >= 0 else 'top', zorder=z + 1,
                        annotation_clip=True,
                        bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none',
                                  alpha=0.75))

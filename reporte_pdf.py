"""
Exportacion a PDF de resultados de ThermoPhase.
================================================

Genera un reporte con los resultados del calculo flash (Equilibrio de
fases) siguiendo exactamente el formato de referencia: tipografia Arial
Narrow, sin colores, sin bordes ni fondos. Solo texto negro sobre blanco.

Estructura del reporte:
    Reporte de Simulacion - ThermoPhase        (14pt, derecha)

    Condiones de calculo:                      (14pt)
      Presion (psi):              <valor>
      Temperatura (°F):           <valor>

    Modelo de calculo ocupado:                 (14pt)
      Ecuacion de estado ocupada:    <PR|SRK>
      Metodo de calculo de densidad: <COSTALD|EOS>

    Resumen de los calculos:                   (14pt)
      tabla 6 filas x 3 columnas

    Composicion de las fases:                  (14pt)
      tabla 13 componentes x 3 columnas

Uso:
    from reporte_pdf import generar_pdf
    ok, msg = generar_pdf(estado, path_destino)
"""
import os
import glob

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import idioma as _i18n


# ── Registro de la tipografia Arial Narrow ───────────────────────────────
_FONT = "Helvetica"     # se reemplaza si Arial Narrow esta disponible

def _registrar_fuente():
    """Registra la tipografia del reporte.

    Prioridad:
      1. Arial Narrow (C:\\Windows\\Fonts\\ARIALN.TTF) — es la que usa el
         resto del programa y la del reporte de referencia.
      2. DejaVu Sans — fallback en Linux. Importante porque las Type-1
         base de ReportLab (Helvetica) NO tienen los subindices Unicode
         de los nombres de componentes (N₂, CO₂) y los dibujan como
         cuadros negros.
      3. Helvetica — ultimo recurso.
    """
    global _FONT
    rutas = [os.path.join(os.environ.get('WINDIR', r'C:\Windows'),
                          'Fonts', 'ARIALN.TTF')]
    for base in ('/usr/share/fonts', '/usr/local/share/fonts'):
        rutas += glob.glob(os.path.join(base, '**', 'ArialN*.ttf'),
                           recursive=True)
    # Fallbacks con soporte Unicode completo (subindices N₂, CO₂)
    for base in ('/usr/share/fonts', '/usr/local/share/fonts'):
        rutas += glob.glob(os.path.join(base, '**', 'LiberationSans-Regular.ttf'),
                           recursive=True)
        rutas += glob.glob(os.path.join(base, '**', 'DejaVuSans.ttf'),
                           recursive=True)
    for r in rutas:
        try:
            if os.path.exists(r):
                pdfmetrics.registerFont(TTFont('ReporteFont', r))
                _FONT = 'ReporteFont'
                return
        except Exception:
            continue

_registrar_fuente()


# ── Paleta de color del reporte ──────────────────────────────────────────
# Azul acero sobrio, coherente con la identidad de ThermoPhase. Se usa con
# mesura: banda de título, acentos de sección, encabezados de tabla.
from reportlab.lib.colors import HexColor

_AZUL      = HexColor('#4a4a4a')   # gris medio principal (banda, acentos)
_AZUL_OSC  = HexColor('#2b2b2b')   # gris profundo (texto de título sobre banda)
_GRIS_HDR  = HexColor('#e6e6e6')   # fondo tenue de encabezados de tabla
_GRIS_ZEB  = HexColor('#f5f5f5')   # zebra muy sutil de filas
_GRIS_LIN  = HexColor('#c4c4c4')   # líneas divisorias finas
_TXT       = HexColor('#1a1a1a')   # texto principal
_TXT_TENUE = HexColor('#6a6a6a')   # texto secundario (fecha, pie)
_BLANCO    = HexColor('#ffffff')


# ── Estilos de parrafo ───────────────────────────────────────────────────
def _estilos():
    return {
        'titulo':   ParagraphStyle('titulo', fontName=_FONT, fontSize=17,
                                   leading=20, alignment=TA_RIGHT,
                                   textColor=_BLANCO),
        'subtitulo':ParagraphStyle('subtitulo', fontName=_FONT, fontSize=9,
                                   leading=11, alignment=TA_RIGHT,
                                   textColor=HexColor('#dcdcdc')),
        'seccion':  ParagraphStyle('seccion', fontName=_FONT, fontSize=13,
                                   leading=16, alignment=TA_LEFT,
                                   textColor=_AZUL_OSC),
        'lbl':      ParagraphStyle('lbl', fontName=_FONT, fontSize=9.3,
                                   leading=11.5, alignment=TA_RIGHT,
                                   textColor=_TXT),
        'val':      ParagraphStyle('val', fontName=_FONT, fontSize=9.3,
                                   leading=11.5, alignment=TA_CENTER,
                                   textColor=_TXT),
        'val_izq':  ParagraphStyle('val_izq', fontName=_FONT, fontSize=9.3,
                                   leading=11.5, alignment=TA_LEFT,
                                   textColor=_TXT),
        'hdr':      ParagraphStyle('hdr', fontName=_FONT, fontSize=9.3,
                                   leading=11.5, alignment=TA_CENTER,
                                   textColor=_AZUL_OSC),
        'pie':      ParagraphStyle('pie', fontName=_FONT, fontSize=8,
                                   leading=10, alignment=TA_CENTER,
                                   textColor=_TXT_TENUE),
    }


# Tabla de pares etiqueta/valor (condiciones, modelo): sin bordes, limpia.
_TBL = TableStyle([
    ('LEFTPADDING',   (0, 0), (-1, -1), 3),
    ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
    ('TOPPADDING',    (0, 0), (-1, -1), 2.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
])


def _estilo_tabla_datos(n_filas, n_hdr=1):
    """Estilo de tabla de resultados: encabezado con fondo tenue, filas
    zebra sutiles, líneas divisorias finas. n_hdr = nº de filas de encabezado."""
    cmds = [
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
        ('TOPPADDING',    (0, 0), (-1, -1), 2.3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.3),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        # Encabezado: fondo tenue y línea inferior azul
        ('BACKGROUND',    (0, 0), (-1, n_hdr-1), _GRIS_HDR),
        ('LINEBELOW',     (0, n_hdr-1), (-1, n_hdr-1), 0.8, _AZUL),
        ('LINEABOVE',     (0, 0), (-1, 0), 0.8, _AZUL),
    ]
    # Zebra: filas de datos alternas con fondo muy sutil
    for r in range(n_hdr, n_filas):
        if (r - n_hdr) % 2 == 1:
            cmds.append(('BACKGROUND', (0, r), (-1, r), _GRIS_ZEB))
    # Línea de cierre inferior
    cmds.append(('LINEBELOW', (0, n_filas-1), (-1, n_filas-1), 0.6, _GRIS_LIN))
    return TableStyle(cmds)


def _f(v, d=4):
    """Formatea un numero; cadena vacia si es None."""
    if v is None:
        return ""
    try:
        return f"{float(v):.{d}f}"
    except (TypeError, ValueError):
        return str(v)


# ── Logo vectorial y banda de encabezado / pie de pagina ─────────────────
def _dibujar_marco(canvas, doc):
    """Dibuja la banda de título superior (con logo) y el pie de página en
    cada hoja. Se invoca como onPage de ReportLab."""
    from reportlab.lib.pagesizes import letter as _LT
    W, H = _LT
    canvas.saveState()

    # ── Banda superior de título ──
    banda_h = 0.62 * inch
    y0 = H - 0.45*inch - banda_h
    canvas.setFillColor(_AZUL)
    canvas.rect(0, y0, W, banda_h, fill=1, stroke=0)
    # franja de acento más oscura en el borde inferior de la banda
    canvas.setFillColor(_AZUL_OSC)
    canvas.rect(0, y0, W, 0.035*inch, fill=1, stroke=0)

    cy = y0 + banda_h/2

    # ── Título dentro de la banda ──
    canvas.setFillColor(_BLANCO)
    canvas.setFont(_FONT, 17)
    canvas.drawRightString(W - 0.80*inch, cy - 1,
                           _i18n.t("Reporte de Simulacion - ThermoPhase"))

    canvas.restoreState()

    # ── Pie de página ──
    canvas.saveState()
    canvas.setStrokeColor(_GRIS_LIN)
    canvas.setLineWidth(0.6)
    yf = 0.55*inch
    canvas.line(0.80*inch, yf, W - 0.80*inch, yf)
    canvas.setFillColor(_TXT_TENUE)
    canvas.setFont(_FONT, 8)
    # izquierda: marca; derecha: página
    canvas.drawString(0.80*inch, yf - 12,
                      "ThermoPhase — " + _i18n.t("Simulador termodinámico"))
    canvas.drawRightString(W - 0.80*inch, yf - 12,
                           f"{_i18n.t('Página')} {canvas.getPageNumber()}")
    canvas.restoreState()


def _titulo_seccion(texto, W):
    """Devuelve una tabla de una celda que renderiza un título de sección con
    una barra de acento azul a la izquierda y una línea inferior fina."""
    E = _estilos()
    par = Paragraph("&nbsp;&nbsp;" + texto, E['seccion'])
    t = Table([[par]], colWidths=[W], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW',     (0, 0), (-1, -1), 0.8, _GRIS_LIN),
        # barra de acento azul a la izquierda del título
        ('LINEBEFORE',    (0, 0), (0, -1), 2.5, _AZUL),
    ]))
    return t


# ── API publica ──────────────────────────────────────────────────────────
# Convierte subindices Unicode (N₂, CO₂) a marcado <sub> de ReportLab, que
# funciona con CUALQUIER fuente (incluida Arial Narrow, que no trae el glifo
# del subindice y lo dibujaba como un recuadro negro).
_SUBS = {'\u2080':'0','\u2081':'1','\u2082':'2','\u2083':'3','\u2084':'4',
         '\u2085':'5','\u2086':'6','\u2087':'7','\u2088':'8','\u2089':'9'}
def _sub_markup(txt):
    out = txt
    for u, d in _SUBS.items():
        out = out.replace(u, f'<sub>{d}</sub>')
    return out


# ── Helpers de contenido reutilizables (composición y propiedades) ───────
# Saturación e hidratos comparten la misma estructura de tablas que
# Equilibrio: Nombre | Mezcla | Vapor | Líquido. Estos helpers arman esas
# tablas con el formato gris del reporte, replicando los cálculos de las
# pestañas (poder calorífico, peso molecular de mezcla, densidad de mezcla).

def _tabla_composicion(z, y, x, hay_vap, hay_liq, W):
    """Construye la tabla de composición de fases con formato del reporte."""
    from eos import NOMBRES, NC
    E = _estilos()
    def hdr(s): return Paragraph(s, E['hdr'])
    def lab(s): return Paragraph(s, E['lbl'])
    def val(v): return Paragraph(_f(v, 4), E['val'])
    def vac():  return Paragraph("", E['val'])
    sz = sum(z) if z else 0.0

    comp = [
        [lab(""), hdr(_i18n.t("Composicion General")), hdr(_i18n.t("Fase Vapor")),
         hdr(_i18n.t("Fase Liquida"))],
        [lab(""), hdr(_i18n.t("Fraccion Molar")), hdr(_i18n.t("Fraccion Molar")),
         hdr(_i18n.t("Fraccion Molar"))],
    ]
    for i in range(NC):
        zi = z[i] if i < len(z) else 0.0
        yi = y[i] if i < len(y) else 0.0
        xi = x[i] if i < len(x) else 0.0
        comp.append([
            lab(_sub_markup(_i18n.t(NOMBRES[i]))),
            val(zi) if sz > 0 else vac(),
            val(yi) if hay_vap else vac(),
            val(xi) if hay_liq else vac(),
        ])
    t = Table(comp, colWidths=[W*0.34, W*0.22, W*0.22, W*0.22], hAlign='CENTER')
    est = _estilo_tabla_datos(len(comp), n_hdr=2)
    est.add('LEFTPADDING', (0, 2), (0, -1), 8)
    t.setStyle(est)
    return t


def _tabla_propiedades_fase(props, z, y, x, hay_vap, hay_liq, W):
    """Construye la tabla de propiedades por fase (Mezcla|Vapor|Líquido),
    replicando los cálculos de las pestañas de saturación/hidratos."""
    import math as _math
    import unidades as _u
    import poder_calorifico as _pc
    import eos as _eng
    from pestana_saturacion import _PROP_SAT, _conv_prop
    E = _estilos()
    def hdr(s):   return Paragraph(s, E['hdr'])
    def lab(s):   return Paragraph(s, E['lbl'])
    def val(txt): return Paragraph(txt, E['val'])

    sz = sum(z) if z else 0.0
    p = props or {}
    _pc_v = _pc.poder_calorifico_fase(y, p.get('PM_v')) if hay_vap else {}
    _pc_l = _pc.poder_calorifico_fase(x, p.get('PM_l')) if hay_liq else {}
    _pc_z = _pc.poder_calorifico_fase(z, None) if sz > 0 else {}
    _gpm_v = _pc.gpm_c3(y) if hay_vap else None
    _gpm_z = _pc.gpm_c3(z) if sz > 0 else None
    _pm_z = sum(z[i]*_eng.PM[i] for i in range(len(z))) if sz > 0 else None
    _rho_z = None
    rho_v = p.get('rho_v'); rho_l = p.get('rho_l')
    Vm = p.get('Vm'); Lm = p.get('Lm')
    if hay_vap and hay_liq and rho_v and rho_l and Vm is not None and Lm is not None:
        inv = (Vm/rho_v if rho_v>0 else 0)+(Lm/rho_l if rho_l>0 else 0)
        if inv>0: _rho_z = 1.0/inv
    elif hay_liq and rho_l: _rho_z = rho_l
    elif hay_vap and rho_v: _rho_z = rho_v

    def _ok(v):
        return v is not None and not (isinstance(v, float) and
                                      (_math.isnan(v) or _math.isinf(v)))

    def _val_fase(kf, phase_pc, conv, gpm_val, existe):
        if not existe:
            return None
        if isinstance(kf, str) and kf.startswith('PCAL:'):
            v = phase_pc.get(kf.split(':', 1)[1])
        elif isinstance(kf, str) and kf.startswith('GPM:'):
            v = gpm_val if kf == 'GPM:v' else None
        else:
            v = _conv_prop(conv, p.get(kf))
        return v if _ok(v) else None

    def _val_mezcla(key, conv):
        if sz <= 0: return None
        if key == 'pm':       return _conv_prop(conv, _pm_z)
        if key == 'densidad': return _conv_prop(conv, _rho_z) if _rho_z else None
        if key in ('hhv_mas','lhv_mas','hhv_vol','lhv_vol'):
            v = _pc_z.get(key); return v if _ok(v) else None
        if key == 'gpm':      return _gpm_z if _ok(_gpm_z) else None
        return None

    filas = [[lab(""), hdr(_i18n.t("Composicion General")),
              hdr(_i18n.t("Fase Vapor")), hdr(_i18n.t("Fase Liquida"))]]
    for (key, base, mag, dec, kv, kl, conv) in _PROP_SAT:
        unidad = f" [{_u.u(mag)}]" if mag else ""
        vz = _val_mezcla(key, conv)
        vv = _val_fase(kv, _pc_v, conv, _gpm_v, hay_vap)
        vl = _val_fase(kl, _pc_l, conv, None, hay_liq)
        fmt = f"{{:.{dec}f}}"
        filas.append([
            lab(f"{_i18n.t(base)}{unidad}:"),
            val(fmt.format(vz)) if vz is not None else val(""),
            val(fmt.format(vv)) if vv is not None else val(""),
            val(fmt.format(vl)) if vl is not None else val(""),
        ])
    t = Table(filas, colWidths=[W*0.34, W*0.22, W*0.22, W*0.22], hAlign='CENTER')
    est = _estilo_tabla_datos(len(filas), n_hdr=1)
    est.add('LEFTPADDING', (0, 1), (0, -1), 8)
    t.setStyle(est)
    return t


def _grafica_envolvente(resultado):
    """Genera una imagen PNG (en escala de grises) de la envolvente de fases
    y devuelve su ruta temporal. Devuelve None si no hay datos.

    Reproduce la envolvente con la misma convención de unidades de la interfaz
    (°F/°C y psi/kPa según el sistema activo), pero SIN los colores rojo/azul:
    burbuja en gris oscuro y rocío en gris medio (línea discontinua para
    distinguirlas), con marcadores triangulares como en la app.
    """
    env = (resultado or {}).get('envolvente') or {}
    if not env:
        return None
    burb = env.get('burbuja', []) or []
    rocio = env.get('rocio', []) or []
    crit = env.get('critico')
    iso = (resultado or {}).get('isocalidad') or {}
    if not (burb or rocio):
        return None

    import unidades as _u
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import tempfile

    # Datos a unidades de presentación
    Tb = [_u.t_desde_R(t) for _, t in burb]; Pb = [_u.p_desde_psia(p) for p, _ in burb]
    Td = [_u.t_desde_R(t) for _, t in rocio]; Pd = [_u.p_desde_psia(p) for p, _ in rocio]

    fig, ax = plt.subplots(figsize=(6.6, 4.7), dpi=150)

    # Isocalidades primero (gris muy claro, al fondo)
    for _idx, pts in (iso or {}).items():
        if not pts:
            continue
        Ti = [_u.t_desde_R(t) for _, t in pts]
        Pi = [_u.p_desde_psia(p) for p, _ in pts]
        ax.plot(Ti, Pi, linestyle='-', linewidth=0.6, color='#b0b0b0',
                zorder=2)

    # Burbuja: gris oscuro, línea continua + triángulos
    if Tb and Pb:
        ax.plot(Tb, Pb, linestyle='-', linewidth=0.8, color='#3a3a3a', zorder=3)
        ax.plot(Tb, Pb, linestyle='none', marker='^', markersize=3.2,
                color='#3a3a3a', zorder=4, label=_i18n.t('Curva de Burbuja'))
    # Rocío: gris medio, línea discontinua + triángulos (para distinguir sin color)
    if Td and Pd:
        ax.plot(Td, Pd, linestyle='--', linewidth=0.8, color='#8a8a8a', zorder=3)
        ax.plot(Td, Pd, linestyle='none', marker='^', markersize=3.2,
                color='#8a8a8a', zorder=4, label=_i18n.t('Curva de Rocío'))
    # Punto crítico
    if crit is not None:
        try:
            Pc, Tc = crit
            ax.plot([_u.t_desde_R(Tc)], [_u.p_desde_psia(Pc)], linestyle='none',
                    marker='o', markersize=5, markerfacecolor='#5a5a5a',
                    markeredgecolor='#2b2b2b', markeredgewidth=0.6,
                    label=_i18n.t('Punto crítico'), zorder=5)
        except Exception:
            pass

    ax.set_xlabel(f"{_i18n.t('Temperatura')} ({_u.u('T')})", fontsize=9,
                  color='#2b2b2b')
    ax.set_ylabel(f"{_i18n.t('Presion')} ({_u.u('P')})", fontsize=9,
                  color='#2b2b2b')
    ax.tick_params(labelsize=8, colors='#2b2b2b')
    ax.grid(True, linestyle=':', linewidth=0.5, color='#d0d0d0')
    for spine in ax.spines.values():
        spine.set_edgecolor('#9a9a9a'); spine.set_linewidth(0.7)
    leg = ax.legend(fontsize=8, framealpha=0.9, edgecolor='#c0c0c0',
                    loc='best')
    if leg:
        leg.get_frame().set_facecolor('#f6f6f6')
    fig.tight_layout()

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    fig.savefig(tmp.name, dpi=150, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    return tmp.name


def generar_pdf(estado, path):
    """
    Genera el reporte PDF del calculo flash (Equilibrio de fases).

    Parametros
    ----------
    estado : dict   Dict de MainWindow._recopilar_estado()
    path   : str    Ruta destino del PDF

    Retorna
    -------
    (ok: bool, mensaje: str)
    """
    try:
        from eos import NOMBRES, NC

        tabs = estado.get('tabs', {})
        t_eq  = tabs.get('equilibrio', {}) or {}
        res   = t_eq.get('resultado') or {}
        ent   = t_eq.get('entrada', {}) or {}
        t_sat = tabs.get('saturacion', {}) or {}
        t_hid = tabs.get('hidratos', {}) or {}
        t_env = tabs.get('envolvente', {}) or {}
        res_sat = t_sat.get('resultado')
        res_hid = t_hid.get('resultado')
        res_env = (t_env.get('resultado') or {}).get('envolvente') \
                  if t_env.get('resultado') else None

        # Se exporta lo que esté calculado. Si NADA lo está, se avisa.
        if not (res or res_sat or res_hid or res_env):
            return False, (
                "No hay resultados para exportar.\n"
                "Ejecute al menos un cálculo (Equilibrio de fases, Saturación, "
                "Hidratos o Envolvente) antes de exportar.")

        E = _estilos()

        doc = SimpleDocTemplate(
            path, pagesize=letter,
            leftMargin=0.80*inch, rightMargin=0.80*inch,
            topMargin=1.22*inch, bottomMargin=0.75*inch,
            title="Reporte de Simulacion - ThermoPhase",
            author="ThermoPhase",
        )
        W = letter[0] - 1.60*inch     # ancho util

        story = []
        import unidades as _u
        import datetime as _dt
        fecha = _dt.datetime.now().strftime('%d/%m/%Y  %H:%M')

        def _fecha_par():
            return Paragraph(
                f"{_i18n.t('Generado')}: {fecha}",
                ParagraphStyle('fecha', fontName=_FONT, fontSize=9, leading=11,
                               alignment=TA_RIGHT, textColor=_TXT_TENUE))

        def hdr(s):        return Paragraph(s, E['hdr'])
        def lab(s):        return Paragraph(s, E['lbl'])
        def val(v, d=4):   return Paragraph(_f(v, d), E['val'])
        def vac():         return Paragraph("", E['val'])

        _primera = True   # controla el PageBreak entre hojas

        # ══════════════════════════════════════════════════════════
        # HOJA 1 — Equilibrio de fases (solo si está calculado)
        # ══════════════════════════════════════════════════════════
        if res:
            _primera = False
            story.append(_fecha_par())
            story.append(Spacer(1, 7))
            story.append(_titulo_seccion(_i18n.t("Equilibrio de fases"), W))
            story.append(Spacer(1, 8))

            # ═══ Condiones de calculo ════════════════════════════
            story.append(_titulo_seccion(_i18n.t("Condiones de calculo:"), W))
            story.append(Spacer(1, 6))

            import unidades as _u
            T_R = float(ent.get('T_R', 0) or 0)
            P   = float(ent.get('P_psi', 0) or 0)
            T_disp = _u.t_desde_R(T_R) if T_R > 0 else 0.0   # °F o °C
            P_disp = _u.p_desde_psia(P)                       # psi o kPa

            cond = [
                [Paragraph(f"{_i18n.t('Presion')} ({_u.u('P')}):", E['lbl']),
                 Paragraph(_f(P_disp, 2), E['val_izq'])],
                [Paragraph(f"{_i18n.t('Temperatura')} ({_u.u('T')}):", E['lbl']),
                 Paragraph(_f(T_disp, 2), E['val_izq'])],
            ]
            t = Table(cond, colWidths=[W*0.34, W*0.30], hAlign='LEFT')
            t.setStyle(_TBL)
            story.append(t)
            story.append(Spacer(1, 9))

            # ═══ Modelo de calculo ocupado ═══════════════════════════
            story.append(_titulo_seccion(_i18n.t("Modelo de calculo ocupado:"), W))
            story.append(Spacer(1, 6))

            modelo = [
                [Paragraph(_i18n.t("Ecuacion de estado ocupada:"), E['lbl']),
                 Paragraph(ent.get('eos', 'Peng-Robinson'), E['val_izq'])],
                [Paragraph(_i18n.t("Metodo de calculo de densidad:"), E['lbl']),
                 Paragraph(ent.get('densidad', 'COSTALD'), E['val_izq'])],
            ]
            t = Table(modelo, colWidths=[W*0.42, W*0.30], hAlign='LEFT')
            t.setStyle(_TBL)
            story.append(t)
            story.append(Spacer(1, 9))

            # ═══ Resumen de los calculos ═════════════════════════════
            story.append(_titulo_seccion(_i18n.t("Resumen de los calculos:"), W))
            story.append(Spacer(1, 6))

            V  = res.get('V')  or 0.0
            L  = res.get('L')  or 0.0
            Vm = res.get('Vm')
            Lm = res.get('Lm')
            ZV = res.get('ZV')
            ZL = res.get('ZL')
            PM_v  = res.get('PM_v');  PM_l  = res.get('PM_l');  PM_z = res.get('PM_z')
            rho_v = res.get('rho_v'); rho_l = res.get('rho_l')
            sg_v  = res.get('sg_v');  sg_l  = res.get('sg_l')

            # Densidad de la mezcla (volumenes aditivos), si no viene calculada
            rho_z = res.get('rho_z')
            if rho_z is None:
                if rho_v and rho_l:
                    inv = ((Vm or 0)/rho_v if rho_v > 0 else 0) + \
                          ((Lm or 0)/rho_l if rho_l > 0 else 0)
                    rho_z = 1.0/inv if inv > 0 else None
                elif rho_l:
                    rho_z = rho_l
                elif rho_v:
                    rho_z = rho_v

            # Densidad al sistema de unidades activo (MW y Z no cambian)
            rho_z = _u.dens_desde(rho_z) if rho_z is not None else None
            rho_v = _u.dens_desde(rho_v) if rho_v is not None else None
            rho_l = _u.dens_desde(rho_l) if rho_l is not None else None

            def hdr(s):        return Paragraph(s, E['hdr'])
            def lab(s):        return Paragraph(s, E['lbl'])
            def val(v, d=4):   return Paragraph(_f(v, d), E['val'])
            def vac():         return Paragraph("", E['val'])

            resumen = [
                [lab(""), hdr(_i18n.t("Composicion General")), hdr(_i18n.t("Fase Vapor")),
                 hdr(_i18n.t("Fase Liquida"))],
                [lab(_i18n.t("Fase fraccion [molar]:")),      vac(),
                 val(V),  val(L)],
                [lab(_i18n.t("Fase fraccion [masica]:")),     vac(),
                 val(Vm), val(Lm)],
                [lab(_i18n.t("Gravedad especifica:")),        vac(),
                 val(sg_v), val(sg_l)],
                [lab(f"{_i18n.t('Densidad masica')} [{_u.u('dens')}]:"),   val(rho_z),
                 val(rho_v), val(rho_l)],
                [lab(_i18n.t("Factor de compresibilidad:")),  vac(),
                 val(ZV), val(ZL)],
                [lab(_i18n.t("Peso molecular:")),             val(PM_z),
                 val(PM_v), val(PM_l)],
            ]
            t = Table(resumen, colWidths=[W*0.34, W*0.22, W*0.22, W*0.22],
                      hAlign='CENTER')
            t.setStyle(_estilo_tabla_datos(len(resumen), n_hdr=1))
            story.append(t)
            story.append(Spacer(1, 8))

            # ═══ Composicion de las fases ════════════════════════════
            story.append(_titulo_seccion(_i18n.t("Composicion de las fases:"), W))
            story.append(Spacer(1, 6))

            z = list(ent.get('composicion') or [0.0]*NC)
            x = list(res.get('x') or [0.0]*NC)
            y = list(res.get('y') or [0.0]*NC)

            comp = [
                [lab(""), hdr(_i18n.t("Composicion General")), hdr(_i18n.t("Fase Vapor")),
                 hdr(_i18n.t("Fase Liquida"))],
                [lab(""), hdr(_i18n.t("Fraccion Molar")), hdr(_i18n.t("Fraccion Molar")),
                 hdr(_i18n.t("Fraccion Molar"))],
            ]
            for i in range(NC):
                zi = z[i] if i < len(z) else 0.0
                yi = y[i] if i < len(y) else 0.0
                xi = x[i] if i < len(x) else 0.0
                comp.append([
                    lab(_sub_markup(_i18n.t(NOMBRES[i]))),  # <sub> para el subindice (N2, CO2)
                    val(zi),
                    val(yi) if V > 0 else vac(),
                    val(xi) if L > 0 else vac(),
                ])
            t = Table(comp, colWidths=[W*0.34, W*0.22, W*0.22, W*0.22],
                      hAlign='CENTER')
            est = _estilo_tabla_datos(len(comp), n_hdr=2)
            # Nombres de componentes alineados a la derecha (como el original),
            # con un poco más de aire a la izquierda.
            est.add('LEFTPADDING', (0, 2), (0, -1), 8)
            t.setStyle(est)
            story.append(t)

        # ══════════════════════════════════════════════════════════
        # Helpers de página adicional (salto + fecha en cada hoja)
        # ══════════════════════════════════════════════════════════
        def _abrir_hoja(titulo):
            """Inserta el salto de página (si procede), la fecha y el título
            de la hoja. Devuelve nada; opera sobre `story`."""
            nonlocal _primera
            if not _primera:
                story.append(PageBreak())
            _primera = False
            story.append(_fecha_par())
            story.append(Spacer(1, 5))
            story.append(_titulo_seccion(titulo, W))
            story.append(Spacer(1, 6))

        def _bloque_condiciones(pares):
            """Tabla de pares etiqueta/valor (condiciones/modelo)."""
            filas = [[Paragraph(k, E['lbl']), Paragraph(v, E['val_izq'])]
                     for k, v in pares]
            tt = Table(filas, colWidths=[W*0.40, W*0.34], hAlign='LEFT')
            tt.setStyle(_TBL)
            return tt

        # ══════════════════════════════════════════════════════════
        # HOJA — Puntos de saturación
        # ══════════════════════════════════════════════════════════
        if res_sat:
            _abrir_hoja(_i18n.t("Puntos de saturación"))
            e_sat = t_sat.get('entrada', {}) or {}
            T_s = res_sat.get('T'); P_s = res_sat.get('P')
            x_s = list(res_sat.get('x') or [0.0]*NC)
            y_s = list(res_sat.get('y') or [0.0]*NC)
            z_s = list(e_sat.get('z') or res_sat.get('z') or [0.0]*NC)
            # En un punto de saturación una fase es incipiente: mostramos ambas.
            props_s = res_sat.get('props', {}) or {}

            story.append(_titulo_seccion(_i18n.t("Condiones de calculo:"), W))
            story.append(Spacer(1, 6))
            tipo_s = e_sat.get('tipo', '')
            story.append(_bloque_condiciones([
                (f"{_i18n.t('Tipo de calculo')}:", _i18n.t(tipo_s) if tipo_s else ""),
                (f"{_i18n.t('Temperatura')} ({_u.u('T')}):",
                 _f(_u.t_desde_R(T_s), 2) if T_s else ""),
                (f"{_i18n.t('Presion')} ({_u.u('P')}):",
                 _f(_u.p_desde_psia(P_s), 2) if P_s else ""),
            ]))
            story.append(Spacer(1, 7))

            story.append(_titulo_seccion(_i18n.t("Composicion de las fases:"), W))
            story.append(Spacer(1, 6))
            story.append(_tabla_composicion(z_s, y_s, x_s, True, True, W))
            story.append(Spacer(1, 7))

            story.append(_titulo_seccion(_i18n.t("Propiedades del punto:"), W))
            story.append(Spacer(1, 6))
            story.append(_tabla_propiedades_fase(props_s, z_s, y_s, x_s,
                                                 True, True, W))

        # ══════════════════════════════════════════════════════════
        # HOJA — Formación de hidratos
        # ══════════════════════════════════════════════════════════
        if res_hid:
            _abrir_hoja(_i18n.t("Formación de hidratos"))
            flash_h = res_hid.get('flash', {}) or {}
            T_h = res_hid.get('T_R'); P_h = res_hid.get('P_psia')
            Vh = flash_h.get('V')
            hay_vap_h = (Vh is None) or (Vh > 1e-9)
            hay_liq_h = (Vh is None) or (Vh < 1.0 - 1e-9)
            x_h = list(flash_h.get('x') or [0.0]*NC)
            y_h = list(flash_h.get('y') or [0.0]*NC)
            z_h = list(flash_h.get('z') or res_hid.get('z') or [0.0]*NC)
            props_h = res_hid.get('props', {}) or {}

            story.append(_titulo_seccion(_i18n.t("Condiones de calculo:"), W))
            story.append(Spacer(1, 6))
            story.append(_bloque_condiciones([
                (f"{_i18n.t('Temperatura de Hidrato')} ({_u.u('T')}):",
                 _f(_u.t_desde_R(T_h), 2) if T_h else ""),
                (f"{_i18n.t('Presion')} ({_u.u('P')}):",
                 _f(_u.p_desde_psia(P_h), 2) if P_h else ""),
            ]))
            story.append(Spacer(1, 7))

            story.append(_titulo_seccion(_i18n.t("Composicion de las fases:"), W))
            story.append(Spacer(1, 6))
            story.append(_tabla_composicion(z_h, y_h, x_h, hay_vap_h, hay_liq_h, W))
            story.append(Spacer(1, 7))

            story.append(_titulo_seccion(_i18n.t("Propiedades del punto:"), W))
            story.append(Spacer(1, 6))
            story.append(_tabla_propiedades_fase(props_h, z_h, y_h, x_h,
                                                 hay_vap_h, hay_liq_h, W))

        # ══════════════════════════════════════════════════════════
        # HOJA — Envolvente de fases (gráfica en grises)
        # ══════════════════════════════════════════════════════════
        if res_env:
            _abrir_hoja(_i18n.t("Envolvente de fases"))
            img_path = _grafica_envolvente(t_env.get('resultado') or {})
            if img_path:
                story.append(Spacer(1, 4))
                # Ancho de imagen = ancho útil; alto proporcional
                img = Image(img_path, width=W, height=W*0.72)
                img.hAlign = 'CENTER'
                story.append(img)

        doc.build(story, onFirstPage=_dibujar_marco,
                  onLaterPages=_dibujar_marco)
        return True, _i18n.t("PDF exportado correctamente:") + f"\n{os.path.basename(path)}"

    except Exception as ex:
        import traceback
        return False, f"Error al generar el PDF:\n{ex}\n\n{traceback.format_exc()}"

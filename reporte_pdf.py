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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
        'lbl':      ParagraphStyle('lbl', fontName=_FONT, fontSize=10,
                                   leading=12.5, alignment=TA_RIGHT,
                                   textColor=_TXT),
        'val':      ParagraphStyle('val', fontName=_FONT, fontSize=10,
                                   leading=12.5, alignment=TA_CENTER,
                                   textColor=_TXT),
        'val_izq':  ParagraphStyle('val_izq', fontName=_FONT, fontSize=10,
                                   leading=12.5, alignment=TA_LEFT,
                                   textColor=_TXT),
        'hdr':      ParagraphStyle('hdr', fontName=_FONT, fontSize=10,
                                   leading=12.5, alignment=TA_CENTER,
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
        t_eq = tabs.get('equilibrio', {}) or {}
        res  = t_eq.get('resultado') or {}
        ent  = t_eq.get('entrada', {}) or {}

        if not res:
            return False, ("No hay resultados del calculo flash para exportar.\n"
                           "Ejecute el calculo en la pestaña de Equilibrio de "
                           "fases antes de exportar.")

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

        # ═══ Fecha de generación (bajo la banda) ═════════════════
        # El título va dibujado en la banda azul por _dibujar_marco. Aquí solo
        # se coloca la fecha de generación, alineada a la derecha.
        import datetime as _dt
        fecha = _dt.datetime.now().strftime('%d/%m/%Y  %H:%M')
        story.append(Paragraph(
            f"{_i18n.t('Generado')}: {fecha}",
            ParagraphStyle('fecha', fontName=_FONT, fontSize=9, leading=11,
                           alignment=TA_RIGHT, textColor=_TXT_TENUE)))
        story.append(Spacer(1, 7))

        # ═══ Condiones de calculo ════════════════════════════════
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
        story.append(Spacer(1, 11))

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

        doc.build(story, onFirstPage=_dibujar_marco,
                  onLaterPages=_dibujar_marco)
        return True, _i18n.t("PDF exportado correctamente:") + f"\n{os.path.basename(path)}"

    except Exception as ex:
        import traceback
        return False, f"Error al generar el PDF:\n{ex}\n\n{traceback.format_exc()}"

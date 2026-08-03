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


# ── Estilos de parrafo ───────────────────────────────────────────────────
def _estilos():
    return {
        'titulo':  ParagraphStyle('titulo',  fontName=_FONT, fontSize=14,
                                  leading=17, alignment=TA_RIGHT),
        'seccion': ParagraphStyle('seccion', fontName=_FONT, fontSize=14,
                                  leading=17, alignment=TA_LEFT),
        'lbl':     ParagraphStyle('lbl',     fontName=_FONT, fontSize=11,
                                  leading=14, alignment=TA_RIGHT),
        'val':     ParagraphStyle('val',     fontName=_FONT, fontSize=11,
                                  leading=14, alignment=TA_CENTER),
        'val_izq': ParagraphStyle('val_izq', fontName=_FONT, fontSize=11,
                                  leading=14, alignment=TA_LEFT),
        'hdr':     ParagraphStyle('hdr',     fontName=_FONT, fontSize=11,
                                  leading=14, alignment=TA_CENTER),
    }


# Tabla sin bordes, sin fondos, sin lineas — como el original
_TBL = TableStyle([
    ('LEFTPADDING',   (0, 0), (-1, -1), 2),
    ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
    ('TOPPADDING',    (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
])


def _f(v, d=4):
    """Formatea un numero; cadena vacia si es None."""
    if v is None:
        return ""
    try:
        return f"{float(v):.{d}f}"
    except (TypeError, ValueError):
        return str(v)


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
            topMargin=0.60*inch, bottomMargin=0.55*inch,
            title="Reporte de Simulacion - ThermoPhase",
            author="ThermoPhase",
        )
        W = letter[0] - 1.60*inch     # ancho util

        story = []

        # ═══ Titulo ══════════════════════════════════════════════
        story.append(Paragraph("Reporte de Simulacion - ThermoPhase",
                               E['titulo']))
        story.append(Spacer(1, 14))

        # ═══ Condiones de calculo ════════════════════════════════
        story.append(Paragraph("Condiones de calculo:", E['seccion']))
        story.append(Spacer(1, 7))

        T_R = float(ent.get('T_R', 0) or 0)
        P   = float(ent.get('P_psi', 0) or 0)
        T_F = T_R - 459.67 if T_R > 0 else 0.0

        cond = [
            [Paragraph("Presion (psi):", E['lbl']),
             Paragraph(_f(P, 2), E['val_izq'])],
            [Paragraph("Temperatura (°F):", E['lbl']),
             Paragraph(_f(T_F, 2), E['val_izq'])],
        ]
        t = Table(cond, colWidths=[W*0.34, W*0.30], hAlign='LEFT')
        t.setStyle(_TBL)
        story.append(t)
        story.append(Spacer(1, 12))

        # ═══ Modelo de calculo ocupado ═══════════════════════════
        story.append(Paragraph("Modelo de calculo ocupado:", E['seccion']))
        story.append(Spacer(1, 7))

        modelo = [
            [Paragraph("Ecuacion de estado ocupada:", E['lbl']),
             Paragraph(ent.get('eos', 'Peng-Robinson'), E['val_izq'])],
            [Paragraph("Metodo de calculo de densidad:", E['lbl']),
             Paragraph(ent.get('densidad', 'COSTALD'), E['val_izq'])],
        ]
        t = Table(modelo, colWidths=[W*0.42, W*0.30], hAlign='LEFT')
        t.setStyle(_TBL)
        story.append(t)
        story.append(Spacer(1, 12))

        # ═══ Resumen de los calculos ═════════════════════════════
        story.append(Paragraph("Resumen de los calculos:", E['seccion']))
        story.append(Spacer(1, 7))

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

        def hdr(s):        return Paragraph(s, E['hdr'])
        def lab(s):        return Paragraph(s, E['lbl'])
        def val(v, d=4):   return Paragraph(_f(v, d), E['val'])
        def vac():         return Paragraph("", E['val'])

        resumen = [
            [lab(""), hdr("Composicion General"), hdr("Fase Vapor"),
             hdr("Fase Liquida")],
            [lab("Fase fraccion [molar]:"),      vac(),
             val(V),  val(L)],
            [lab("Fase fraccion [masica]:"),     vac(),
             val(Vm), val(Lm)],
            [lab("Gravedad especifica:"),        vac(),
             val(sg_v), val(sg_l)],
            [lab("Densidad masica [lb/ft3]:"),   val(rho_z),
             val(rho_v), val(rho_l)],
            [lab("Factor de compresibilidad:"),  vac(),
             val(ZV), val(ZL)],
            [lab("Peso molecular:"),             val(PM_z),
             val(PM_v), val(PM_l)],
        ]
        t = Table(resumen, colWidths=[W*0.34, W*0.22, W*0.22, W*0.22],
                  hAlign='CENTER')
        t.setStyle(_TBL)
        story.append(t)
        story.append(Spacer(1, 14))

        # ═══ Composicion de las fases ════════════════════════════
        story.append(Paragraph("Composicion de las fases:", E['seccion']))
        story.append(Spacer(1, 7))

        z = list(ent.get('composicion') or [0.0]*NC)
        x = list(res.get('x') or [0.0]*NC)
        y = list(res.get('y') or [0.0]*NC)

        comp = [
            [lab(""), hdr("Composicion General"), hdr("Fase Vapor"),
             hdr("Fase Liquida")],
            [lab(""), hdr("Fraccion Molar"), hdr("Fraccion Molar"),
             hdr("Fraccion Molar")],
        ]
        for i in range(NC):
            zi = z[i] if i < len(z) else 0.0
            yi = y[i] if i < len(y) else 0.0
            xi = x[i] if i < len(x) else 0.0
            comp.append([
                lab(_sub_markup(NOMBRES[i])),  # <sub> para el subindice (N2, CO2)
                val(zi),
                val(yi) if V > 0 else vac(),
                val(xi) if L > 0 else vac(),
            ])
        t = Table(comp, colWidths=[W*0.34, W*0.22, W*0.22, W*0.22],
                  hAlign='CENTER')
        t.setStyle(_TBL)
        story.append(t)

        doc.build(story)
        import idioma as _i18n
        return True, _i18n.t("PDF exportado correctamente:") + f"\n{os.path.basename(path)}"

    except Exception as ex:
        import traceback
        return False, f"Error al generar el PDF:\n{ex}\n\n{traceback.format_exc()}"

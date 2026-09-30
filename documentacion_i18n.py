# -*- coding: utf-8 -*-
"""
Traducción del contenido HTML de la Documentación técnica.

El contenido de cada apartado está escrito en español en `documentacion.py`.
Este módulo traduce ese HTML al inglés cuando el idioma activo es EN,
sustituyendo cada bloque de texto (párrafo, encabezado o elemento de lista)
por su equivalente traducido. Las ecuaciones (marcadores @@EQ:...@@) son
universales y no se tocan.

El emparejamiento se hace por el TEXTO NORMALIZADO del bloque (colapsando
espacios), de modo que las etiquetas internas <sub>, <sup>, <em> se conservan
tal cual en la traducción. Un bloque sin entrada en el diccionario se deja en
español (degradación elegante), lo que permite ir traduciendo de forma
incremental sin romper nada.
"""
import re

# Diccionario ES -> EN a nivel de bloque de párrafo. La clave es el texto
# interior del bloque con los espacios colapsados a uno solo (sin las etiquetas
# <p>/<h2>/<h3>/<li> externas, pero conservando las etiquetas internas).
TRAD_DOC = {}


def _norm(s):
    """Normaliza el texto de un bloque: colapsa espacios en blanco."""
    return re.sub(r'\s+', ' ', s).strip()


_BLOQUE_RE = re.compile(r'<(h2|h3|p|li)>(.*?)</\1>', re.S)


def traducir_html(html, idioma):
    """Devuelve el HTML traducido al idioma dado ('ES' o 'EN').

    En ES devuelve el original. En EN sustituye el interior de cada bloque
    <h2>/<h3>/<p>/<li> por su traducción si existe en TRAD_DOC.
    """
    if idioma != 'EN':
        return html

    def repl(m):
        tag, inner = m.group(1), m.group(2)
        clave = _norm(inner)
        trad = TRAD_DOC.get(clave)
        if trad is None:
            return m.group(0)          # sin traducción: dejar en español
        return f'<{tag}>{trad}</{tag}>'

    return _BLOQUE_RE.sub(repl, html)


def registrar(pares):
    """Añade traducciones al diccionario. `pares` es una lista de (es, en)
    donde `es` es el texto del bloque en español (se normaliza) y `en` su
    traducción."""
    for es, en in pares:
        TRAD_DOC[_norm(es)] = en


# ══════════════════════════════════════════════════════════════════════
# Sección 9 — Poder calorífico y GPM
# ══════════════════════════════════════════════════════════════════════

def _registrar_contenido():
    """Registra las traducciones del contenido de documentacion_contenido:
    títulos numerados de capítulos y subsecciones, párrafos, subtítulos y
    elementos de lista."""
    import documentacion_contenido as _dc
    pares = []
    for ci, cap in enumerate(_dc.CAPITULOS, start=1):
        pares.append((f"{ci}. {cap['titulo'][0]}", f"{ci}. {cap['titulo'][1]}"))
        for si, sub in enumerate(cap['subsecciones'], start=1):
            pares.append((f"{ci}.{si} {sub['titulo'][0]}", f"{ci}.{si} {sub['titulo'][1]}"))
            for b in sub['bloques']:
                if b[0] in ('p', 'h3'):
                    pares.append((b[1], b[2]))
                elif b[0] == 'ul':
                    pares.extend(b[1])
    registrar(pares)


_registrar_contenido()


def traducir_titulo(titulo_es, idioma):
    """Traduce un título de sección/subsección del árbol.

    El árbol muestra los títulos SIN numeración (p.ej. 'Ecuación de estado'),
    mientras que TRAD_DOC los almacena CON numeración (p.ej.
    '1.1 Ecuación de estado'). Esta función normaliza y busca por el texto sin
    número, devolviendo el título en inglés también sin número.
    """
    if idioma != 'EN':
        return titulo_es
    clave_norm = _norm(titulo_es)
    # Buscar en TRAD_DOC una entrada cuyo texto sin número coincida.
    for es, en in TRAD_DOC.items():
        es_sin = re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', es).strip()
        if es_sin == clave_norm:
            return re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', en).strip()
    return titulo_es


# Índice invertido para acelerar traducir_titulo (se construye una vez).
_TITULO_INDEX = {}
for _es, _en in TRAD_DOC.items():
    _es_sin = re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', _es).strip()
    _en_sin = re.sub(r'^\s*\d+(\.\d+)*\.?\s+', '', _en).strip()
    _TITULO_INDEX[_es_sin] = _en_sin


def traducir_titulo_rapido(titulo_es, idioma):
    """Versión con índice del traductor de títulos."""
    if idioma != 'EN':
        return titulo_es
    return _TITULO_INDEX.get(_norm(titulo_es), titulo_es)


# Títulos de sección de nivel superior (encabezados del árbol sin contenido
# HTML propio). Se añaden al índice de títulos para que el árbol se traduzca.
_SECCIONES_TITULOS = {
    "Fundamentos de las EOS cúbicas": "Fundamentals of cubic EOS",
    "Parámetros de la ecuación de estado": "Equation of state parameters",
    "El cálculo flash (equilibrio L-V)": "The flash calculation (L-V equilibrium)",
    "Envolvente de fases": "Phase envelope",
    "Identificación de fase monofásica": "Single-phase identification",
    "Densidad de líquido y vapor": "Liquid and vapour density",
    "Entalpía y entropía": "Enthalpy and entropy",
    "Viscosidad": "Viscosity",
    "Poder calorífico y GPM": "Heating Value and GPM",
    "Formación de hidratos": "Hydrate Formation",
}
for _es, _en in _SECCIONES_TITULOS.items():
    _TITULO_INDEX[_norm(_es)] = _en


# Títulos del ÁRBOL que difieren de su encabezado <h2> (versiones abreviadas).
# Se registran con su traducción abreviada para que el árbol se traduzca.
_TITULOS_ARBOL = {
    "El coeficiente m y la función alfa": "The coefficient m and the alpha function",
    "Base de datos de los coeficientes": "Coefficient database",
    "Estimación inicial de las K": "Initial estimate of the K values",
    "Algoritmo completo del flash": "The complete flash algorithm",
    "Método de Ziervogel": "The Ziervogel method",
    "Método de Michelsen": "The Michelsen method",
    "Flujo de cálculo combinado": "Combined calculation flow",
    "El problema monofásico": "The single-phase problem",
    "Criterio de alta presión (A/B)": "High-pressure criterion (A/B)",
    "Variante PVTsim": "PVTsim variant",
    "Corrección por presión": "Pressure correction",
}
for _es, _en in _TITULOS_ARBOL.items():
    _TITULO_INDEX[_norm(_es)] = _en

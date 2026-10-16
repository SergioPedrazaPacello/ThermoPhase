"""
ThermoPhase — tipografía uniforme en cualquier PC.

Todo el programa usa «Arial Narrow», que NO viene con Windows (la instala
Microsoft Office).  En una PC sin ella, Windows la sustituye por Arial normal,
más ancha, y los textos ya no caben en los controles de ancho fijo.

Este módulo incluye Liberation Sans Narrow (libre, mismas medidas que Arial
Narrow) dentro del programa (fuentes_datos.py, sin archivos externos) y:
  · Qt: si Arial Narrow no está instalada, registra Liberation Sans Narrow y la
    declara sustituta de «Arial Narrow» → todas las hojas de estilo y QFont que
    piden "Arial Narrow" la usan sin cambiar nada más.
  · matplotlib y ReportLab (que necesitan archivos): la extrae una vez a
    %APPDATA%\\ThermoPhase\\fuentes y la registra.
Si Arial Narrow sí está instalada, se usa la original y esto no hace nada.

Prioridad cuando NO está instalada en el sistema:
  1. Arial Narrow incluida en fuente_arial_narrow.py (uso personal; borrar ese
     archivo antes de distribuir el programa).
  2. Liberation Sans Narrow incluida (libre).
"""
import os
import base64

FAMILIA = "Liberation Sans Narrow"
_ESTILOS = ('Regular', 'Bold', 'Italic', 'BoldItalic')
_qt_listo = False
_mpl_listo = False


def _bytes(estilo):
    from fuentes_datos import TTF_B64
    return base64.b64decode(TTF_B64[estilo])


def _bytes_arial():
    """Arial Narrow incluida (o None si se borró fuente_arial_narrow.py)."""
    try:
        from fuente_arial_narrow import TTF_B64
        return base64.b64decode(TTF_B64)
    except Exception:
        return None


def rutas_ttf():
    """Extrae (una sola vez) los TTF a una carpeta de caché y devuelve
    {estilo: ruta}.  Devuelve {} si no se pudo escribir."""
    base = os.getenv('APPDATA') or os.path.join(os.path.expanduser('~'), '.config')
    d = os.path.join(base, 'ThermoPhase', 'fuentes')
    rutas = {}
    try:
        os.makedirs(d, exist_ok=True)
        pares = [(e, f'LiberationSansNarrow-{e}.ttf', _bytes(e)) for e in _ESTILOS]
        an = _bytes_arial()
        if an:
            pares.insert(0, ('ArialNarrow', 'ARIALN.TTF', an))
        for clave, nombre, datos in pares:
            r = os.path.join(d, nombre)
            if not (os.path.exists(r) and os.path.getsize(r) == len(datos)):
                with open(r, 'wb') as fh:
                    fh.write(datos)
            rutas[clave] = r
    except Exception:
        return {}
    return rutas


def arial_narrow_instalada():
    """True si el sistema tiene la Arial Narrow original (requiere QApplication)."""
    from PyQt6.QtGui import QFontDatabase
    return any(f.lower() == 'arial narrow' for f in QFontDatabase.families())


def instalar_qt():
    """Llamar justo después de crear QApplication."""
    global _qt_listo
    if _qt_listo:
        return
    _qt_listo = True
    try:
        if arial_narrow_instalada():
            return
        from PyQt6.QtGui import QFontDatabase, QFont
        from PyQt6.QtCore import QByteArray
        an = _bytes_arial()
        if an and QFontDatabase.addApplicationFontFromData(QByteArray(an)) >= 0:
            return          # registrada con su propio nombre «Arial Narrow»
        ok = False
        for e in _ESTILOS:
            if QFontDatabase.addApplicationFontFromData(QByteArray(_bytes(e))) >= 0:
                ok = True
        if ok:
            QFont.insertSubstitution("Arial Narrow", FAMILIA)
    except Exception:
        pass


def instalar_matplotlib():
    """Registra la fuente en matplotlib si falta Arial Narrow."""
    global _mpl_listo
    if _mpl_listo:
        return
    _mpl_listo = True
    try:
        from matplotlib import font_manager as fm
        nombres = {f.name.lower() for f in fm.fontManager.ttflist}
        if 'arial narrow' in nombres:
            return
        for r in rutas_ttf().values():
            fm.fontManager.addfont(r)
    except Exception:
        pass


# Familias para matplotlib: la original primero; si falta, la equivalente.
FAMILIAS_MPL = ['Arial Narrow', FAMILIA, 'Arial', 'DejaVu Sans', 'sans-serif']

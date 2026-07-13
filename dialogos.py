"""
Ventanas emergentes unificadas para ThermoPhase.
=================================================

Todas las ventanas emergentes del programa deben usar estas funciones
en lugar de QMessageBox.* directamente para garantizar un aspecto
consistente en Windows (Fusion + tipografia Arial Narrow + boton
estilo retro).

Uso:
    from dialogos import info, advertencia, error
    info(self, "Operacion completada.", titulo="Guardado")
    advertencia(self, "La suma de fracciones debe ser 1.0")
    error(self, "No se pudo abrir el archivo:\n" + str(ex))
"""
from PyQt6.QtWidgets import (QMessageBox, QStyleFactory, QPushButton)
from PyQt6.QtCore import Qt

# Paleta y tipografia identicas al resto del programa
WHITE    = "#FFFFFF"
GRAY_BG  = "#E8E8E8"   # gris tenue (mismo tono que zonas de resultado)
BORDER   = "#888888"
TEXT     = "#000000"
FONT_F   = "Arial Narrow"
FS       = 10

# Titulos por defecto segun el tipo de mensaje
_TIT_INFO = "ThermoPhase"
_TIT_WARN = "ThermoPhase — Advertencia"
_TIT_ERR  = "ThermoPhase — Error"

# QSS unificado: solo colores, tipografia y botones. NO se fuerza el
# ancho de la ventana ni del label — Qt calcula el tamaño natural al
# texto, evitando ventanas grandes con texto pegado a la derecha o
# ventanas fijas con texto que se corta.
_STYLE = (
    f'QMessageBox {{ background:{GRAY_BG}; '
    f'  font-family:"{FONT_F}"; font-size:{FS}pt; color:{TEXT}; }} '
    f'QMessageBox QLabel {{ background:transparent; color:{TEXT}; '
    f'  font-family:"{FONT_F}"; font-size:{FS}pt; }} '
    f'QMessageBox QPushButton {{ background:{GRAY_BG}; color:{TEXT}; '
    f'  border:2px outset {BORDER}; padding:3px 18px; '
    f'  font-family:"{FONT_F}"; font-size:{FS}pt; min-width:70px; }} '
    f'QMessageBox QPushButton:hover {{ background:#F0F0F0; }} '
    f'QMessageBox QPushButton:pressed {{ border:2px inset {BORDER}; }} '
    f'QMessageBox QPushButton:default {{ border:2px outset {BORDER}; }}'
)


def _crear(parent, icon, titulo, texto):
    """Crea el QMessageBox con estilo unificado. El tamaño se calcula
    automaticamente segun el contenido."""
    mb = QMessageBox(parent)
    mb.setWindowTitle(titulo)
    mb.setText(texto)
    mb.setIcon(icon)
    mb.setStyle(QStyleFactory.create("Fusion"))
    mb.setStyleSheet(_STYLE)
    # Word wrap para textos largos (evita que se corten en el ancho fijo
    # que Qt calcula por defecto para textos de una sola linea).
    mb.setTextFormat(Qt.TextFormat.PlainText)
    # Un unico boton "Aceptar"
    mb.setStandardButtons(QMessageBox.StandardButton.Ok)
    btn_ok = mb.button(QMessageBox.StandardButton.Ok)
    if btn_ok:
        btn_ok.setText("Aceptar")
    return mb


def info(parent, texto, titulo=None):
    """Ventana informativa (icono 'i')."""
    _crear(parent, QMessageBox.Icon.Information,
           titulo or _TIT_INFO, texto).exec()


def advertencia(parent, texto, titulo=None):
    """Ventana de advertencia (icono triangulo amarillo)."""
    _crear(parent, QMessageBox.Icon.Warning,
           titulo or _TIT_WARN, texto).exec()


def error(parent, texto, titulo=None):
    """Ventana de error (icono X roja)."""
    _crear(parent, QMessageBox.Icon.Critical,
           titulo or _TIT_ERR, texto).exec()

"""
documentacion.py — Ventana de Documentación técnica de ThermoPhase.

Por ahora es un contenedor vacío (placeholder). El contenido —las ecuaciones
y toda la configuración técnica implementada— se irá construyendo despues,
seccion por seccion.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt


class DocTecnica(QWidget):
    """Contenedor de la documentación técnica. Vacío por el momento."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#FFFFFF;")
        cont = QVBoxLayout(self)
        cont.setContentsMargins(0, 0, 0, 0)

        # Area desplazable lista para recibir el contenido mas adelante.
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background:#FFFFFF;")

        self.cuerpo = QWidget()
        self.cuerpo.setStyleSheet("background:#FFFFFF;")
        self.lay_cuerpo = QVBoxLayout(self.cuerpo)
        self.lay_cuerpo.setContentsMargins(24, 24, 24, 24)
        self.lay_cuerpo.setSpacing(14)

        # Marca de posicion (se reemplazara por el contenido real).
        ph = QLabel("Documentación técnica")
        ph.setStyleSheet("color:#B0B0B0; font-family:'Arial'; font-size:12pt;")
        ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lay_cuerpo.addStretch()
        self.lay_cuerpo.addWidget(ph)
        self.lay_cuerpo.addStretch()

        self.scroll.setWidget(self.cuerpo)
        cont.addWidget(self.scroll)

"""
ThermoPhase — punto de entrada.

Ejecutar con:
    python main.py                    # abre la aplicacion vacia
    python main.py simulacion.tpsim   # abre una simulacion guardada

El splash se muestra ANTES de importar el resto del programa, y su barra de
progreso avanza a medida que se cargan las bibliotecas y la interfaz.
"""
import sys


def main():
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon
    app = QApplication(sys.argv)
    from rutas import ruta_recurso
    import os
    _ico = ruta_recurso('thermophase.ico')
    if os.path.exists(_ico):
        app.setWindowIcon(QIcon(_ico))
    from splash import SplashScreen
    sp = SplashScreen()
    sp.show()
    sp.progreso(0.05, "Iniciando ThermoPhase…")
    sp.progreso(0.15, "Cargando bibliotecas numéricas…")
    import numpy                                    # noqa: F401
    sp.progreso(0.30, "Cargando bibliotecas gráficas…")
    import matplotlib                               # noqa: F401
    matplotlib.use('QtAgg')
    from matplotlib.backends import backend_qtagg   # noqa: F401
    sp.progreso(0.45, "Cargando modelos termodinámicos…")
    import eos, flash_agua, huron_vidal             # noqa: F401
    sp.progreso(0.58, "Cargando interfaz…")
    import ventana_principal as vp
    vp.main(app=app, splash=sp)


if __name__ == "__main__":
    main()

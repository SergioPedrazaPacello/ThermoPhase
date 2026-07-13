"""
Resolucion de rutas a los archivos de recursos (splash.png, thermophase.ico).

Es necesario porque PyInstaller en modo --onefile descomprime los recursos
en un directorio temporal (sys._MEIPASS) distinto de la carpeta del codigo
fuente. Esta funcion devuelve la ruta correcta en ambos casos.
"""
import os
import sys


def ruta_recurso(nombre):
    """Devuelve la ruta absoluta a un archivo de recursos.

    Ejemplo:
        ruta_recurso('splash.png')
        ruta_recurso('thermophase.ico')
    """
    if getattr(sys, 'frozen', False):
        # Ejecutable PyInstaller: los recursos estan en _MEIPASS
        base = sys._MEIPASS
    else:
        # Ejecucion desde codigo fuente: misma carpeta que este archivo
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nombre)

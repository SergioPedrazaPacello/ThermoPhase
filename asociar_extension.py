r"""
Registro de la extension .tpsim con el ejecutable ThermoPhase en Windows.
=========================================================================

Escribe las claves en HKEY_CURRENT_USER\Software\Classes (no requiere
permisos de administrador). Solo funciona en Windows.

Solo tiene sentido cuando el programa esta empaquetado como .exe
(PyInstaller). En modo desarrollo (script .py) el registro no se hace
porque no habria un ejecutable estable al que apuntar.

Uso desde el menu Herramientas:
    from asociar_extension import registrar, desregistrar
    ok, msg = registrar()
"""
import os
import sys
import shutil


# ── Rutas persistentes ────────────────────────────────────────────
def _rutas():
    """Devuelve (path_exe, path_icono) - ambos rutas persistentes que
    pueden guardarse en el Registry. Retorna (None, None) si se corre
    desde Python (modo desarrollo)."""
    if not getattr(sys, 'frozen', False):
        return None, None
    exe = sys.executable
    # Copiar el icono a una ubicacion persistente. Cuando PyInstaller
    # esta en modo --onefile, el .ico esta dentro de _MEIPASS (un dir
    # temporal que Windows borra al cerrar); no sirve para el Registry.
    appdata = (os.environ.get('LOCALAPPDATA') or os.environ.get('APPDATA')
               or os.path.expanduser('~'))
    dest_dir = os.path.join(appdata, 'ThermoPhase')
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception:
        return exe, None
    dest_ico = os.path.join(dest_dir, 'thermophase.ico')
    from rutas import ruta_recurso
    src_ico = ruta_recurso('thermophase.ico')
    if os.path.exists(src_ico):
        try:
            shutil.copy(src_ico, dest_ico)
        except Exception:
            pass
    return exe, dest_ico if os.path.exists(dest_ico) else None


def _notificar_shell():
    """Le dice a Windows que refresque los iconos (SHCNE_ASSOCCHANGED)."""
    try:
        import ctypes
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
    except Exception:
        pass


def _borrar_key(subkey):
    """Elimina una llave del Registry si existe (silencioso)."""
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, subkey)
    except (FileNotFoundError, OSError, ImportError):
        pass


# ── API publica ───────────────────────────────────────────────────
def esta_disponible():
    """True si el programa esta en un entorno donde puede registrar."""
    return sys.platform.startswith('win') and getattr(sys, 'frozen', False)


def registrar():
    """Asocia la extension .tpsim con este ejecutable y su icono.
    Solo escribe en HKEY_CURRENT_USER (no requiere admin). Devuelve
    tupla (ok:bool, mensaje:str)."""
    if not sys.platform.startswith('win'):
        return False, "La asociacion de extensiones solo esta disponible en Windows."
    try:
        import winreg
    except ImportError:
        return False, "No se pudo importar winreg (Windows Registry)."

    exe, ico = _rutas()
    if not exe or not getattr(sys, 'frozen', False):
        return False, ("La asociacion solo funciona con la version empaquetada "
                       "(.exe). En modo desarrollo no hay un ejecutable estable.")
    if not ico:
        return False, "No se encontro el archivo de icono thermophase.ico."

    try:
        # HKCU\Software\Classes\.tpsim  -> ProgID
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Classes\.tpsim") as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, "ThermoPhase.Simulation")

        # HKCU\Software\Classes\ThermoPhase.Simulation
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Classes\ThermoPhase.Simulation") as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, "Simulacion ThermoPhase")

        # ...\DefaultIcon
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Classes\ThermoPhase.Simulation\DefaultIcon") as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, ico)

        # ...\shell\open\command
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Classes\ThermoPhase.Simulation\shell\open\command") as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, f'"{exe}" "%1"')

        _notificar_shell()
        return True, ("Asociacion registrada correctamente. Los archivos "
                      ".tpsim ahora muestran el icono de ThermoPhase y "
                      "se abren con doble clic.")
    except Exception as e:
        return False, f"Error al registrar: {e}"


def desregistrar():
    """Elimina la asociacion de HKEY_CURRENT_USER."""
    if not sys.platform.startswith('win'):
        return False, "Solo disponible en Windows."
    try:
        # Orden: primero las subclaves, despues las padre
        _borrar_key(r"Software\Classes\.tpsim")
        _borrar_key(r"Software\Classes\ThermoPhase.Simulation\shell\open\command")
        _borrar_key(r"Software\Classes\ThermoPhase.Simulation\shell\open")
        _borrar_key(r"Software\Classes\ThermoPhase.Simulation\shell")
        _borrar_key(r"Software\Classes\ThermoPhase.Simulation\DefaultIcon")
        _borrar_key(r"Software\Classes\ThermoPhase.Simulation")
        _notificar_shell()
        return True, "Asociacion eliminada."
    except Exception as e:
        return False, f"Error al desregistrar: {e}"

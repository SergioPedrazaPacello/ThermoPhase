"""
ThermoPhase — verificación de usuario y licencia en línea (Supabase).

Sin dependencias externas: solo la biblioteca estándar (urllib, json, ssl).

Flujo:
  1. iniciar_sesion(usuario, clave, recordar)
       usuario = correo   → POST /auth/v1/token?grant_type=password
       usuario = nombre   → POST /functions/v1/ingresar  (Edge Function)
                                                   → tokens de sesión
       POST /rest/v1/rpc/verificar_licencia      → ¿licencia activa, vigente y
                                                   este equipo permitido?
  2. reanudar_sesion()  (al arrancar, si se marcó «Recordarme»)
       POST /auth/v1/token?grant_type=refresh_token  → tokens nuevos
       POST /rest/v1/rpc/verificar_licencia
     Sin conexión: se permite entrar si la última verificación correcta en este
     equipo fue hace menos de DIAS_SIN_CONEXION días y la licencia no venció.

La sesión recordada se guarda en %APPDATA%\\ThermoPhase\\sesion.dat, cifrada
con DPAPI de Windows (solo la puede leer el mismo usuario de Windows en el
mismo equipo).  Nunca se guarda la contraseña.

Las dos claves de abajo son PÚBLICAS por diseño (Supabase las llama
«publishable»): la seguridad la ponen las políticas RLS y la función
verificar_licencia del servidor.  Nunca poner aquí la clave «secret/service_role».
"""
import os
import sys
import json
import uuid
import ssl
import base64
import hashlib
import platform
import datetime as _dt
import urllib.request
import urllib.error

SUPABASE_URL = "https://lskqnnhfedidgldvuxkw.supabase.co"
SUPABASE_KEY = "sb_publishable_r2ykjP-2qziqErpPnd5oAA_4SYQVz_M"

DIAS_SIN_CONEXION = 7
TIMEOUT = 10  # s


class Resultado:
    """Resultado de una verificación.  ok=True → puede entrar."""
    def __init__(self, ok, mensaje="", usuario="", vence=None, sin_conexion=False):
        self.ok = ok
        self.mensaje = mensaje
        self.usuario = usuario
        self.vence = vence
        self.sin_conexion = sin_conexion


class _SinConexion(Exception):
    pass


class _ErrorServidor(Exception):
    def __init__(self, status, datos):
        super().__init__(f"HTTP {status}")
        self.status = status
        self.datos = datos or {}


# ── identificación del equipo ────────────────────────────────────────────
def _machine_guid():
    if sys.platform != 'win32':
        return ''
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"SOFTWARE\Microsoft\Cryptography", 0,
                           winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        v, _ = winreg.QueryValueEx(k, "MachineGuid")
        return str(v)
    except Exception:
        return ''


def id_equipo():
    """Identificador estable y anónimo del equipo (hash, no datos personales).
    En Windows usa solo el MachineGuid (no cambia al renombrar el equipo ni al
    conectar adaptadores de red).  NO MODIFICAR en versiones futuras: si cambia,
    cada PC ya registrada contaría como un equipo nuevo."""
    g = _machine_guid()
    base = f"win|{g}" if g else f"{uuid.getnode()}|{platform.node()}"
    return hashlib.sha256(base.encode('utf-8')).hexdigest()[:32]


def nombre_equipo():
    return platform.node() or "equipo"


# ── almacenamiento local protegido ───────────────────────────────────────
def _ruta_sesion():
    base = os.getenv('APPDATA') or os.path.join(os.path.expanduser('~'), '.config')
    d = os.path.join(base, 'ThermoPhase')
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, 'sesion.dat')


def _dpapi(datos, cifrar):
    """Cifra/descifra con DPAPI (Windows).  En otros sistemas, sin cambios."""
    if sys.platform != 'win32':
        return datos
    import ctypes
    from ctypes import wintypes

    class BLOB(ctypes.Structure):
        _fields_ = [('cbData', wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_char))]

    buf = ctypes.create_string_buffer(datos, len(datos))
    entrada = BLOB(len(datos), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    salida = BLOB()
    entropia_b = b'ThermoPhase-licencia'
    eb = ctypes.create_string_buffer(entropia_b, len(entropia_b))
    entropia = BLOB(len(entropia_b), ctypes.cast(eb, ctypes.POINTER(ctypes.c_char)))
    f = (ctypes.windll.crypt32.CryptProtectData if cifrar
         else ctypes.windll.crypt32.CryptUnprotectData)
    if not f(ctypes.byref(entrada), None, ctypes.byref(entropia), None, None, 0,
             ctypes.byref(salida)):
        raise OSError("DPAPI falló")
    try:
        return ctypes.string_at(salida.pbData, salida.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(salida.pbData)


def _leer_sesion():
    try:
        with open(_ruta_sesion(), 'rb') as fh:
            raw = base64.b64decode(fh.read())
        d = json.loads(_dpapi(raw, cifrar=False).decode('utf-8'))
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _guardar_sesion(d):
    try:
        raw = _dpapi(json.dumps(d).encode('utf-8'), cifrar=True)
        with open(_ruta_sesion(), 'wb') as fh:
            fh.write(base64.b64encode(raw))
    except Exception:
        pass


def borrar_sesion():
    try:
        os.remove(_ruta_sesion())
    except Exception:
        pass


def usuario_recordado():
    d = _leer_sesion()
    return (d or {}).get('usuario', '')


# ── HTTP ──────────────────────────────────────────────────────────────────
def _post(ruta, cuerpo, token=None):
    cab = {'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'}
    if token:
        cab['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(SUPABASE_URL + ruta, data=json.dumps(cuerpo).encode('utf-8'),
                                 headers=cab, method='POST')
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return json.loads(r.read().decode('utf-8') or 'null')
    except urllib.error.HTTPError as e:
        try:
            datos = json.loads(e.read().decode('utf-8'))
        except Exception:
            datos = {}
        raise _ErrorServidor(e.code, datos)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise _SinConexion(str(e))


def _fecha(txt):
    try:
        return _dt.date.fromisoformat(str(txt)[:10]) if txt else None
    except Exception:
        return None


_MOTIVOS = {
    'sin_licencia': "Tu usuario no tiene una licencia asignada.",
    'inactiva': "Tu licencia está desactivada.",
    'sin_sesion': "No se pudo iniciar la sesión. Intenta de nuevo.",
}


def _mensaje_motivo(r):
    m = r.get('motivo', '')
    if m == 'vencida':
        f = _fecha(r.get('vence'))
        return f"Tu licencia venció el {f:%d/%m/%Y}." if f else "Tu licencia está vencida."
    if m == 'max_equipos':
        return (f"Tu licencia ya está en uso en el máximo de equipos "
                f"permitidos ({r.get('max', '?')}).")
    return _MOTIVOS.get(m, "Acceso no autorizado.")


def _verificar(tok, usuario, recordar, refresh):
    r = _post('/rest/v1/rpc/verificar_licencia',
              {'p_equipo': id_equipo(), 'p_nombre': nombre_equipo()}, token=tok)
    if not isinstance(r, dict) or not r.get('ok'):
        return Resultado(False, _mensaje_motivo(r or {}), usuario)
    vence = _fecha(r.get('vence'))
    if recordar:
        _guardar_sesion({'usuario': usuario, 'refresh': refresh, 'equipo': id_equipo(),
                         'ultima_ok': _dt.datetime.now(_dt.timezone.utc).isoformat(),
                         'vence': vence.isoformat() if vence else None})
    else:
        borrar_sesion()
    return Resultado(True, "", usuario, vence)


# ── API pública ──────────────────────────────────────────────────────────
def iniciar_sesion(usuario, clave, recordar=False):
    usuario = (usuario or '').strip()
    if not usuario or not clave:
        return Resultado(False, "Ingresa tu usuario y contraseña.", usuario)
    try:
        if '@' in usuario:
            t = _post('/auth/v1/token?grant_type=password',
                      {'email': usuario, 'password': clave})
        else:
            # Nombre de usuario: el servidor (Edge Function «ingresar») lo
            # traduce a correo sin revelarlo y devuelve los tokens.
            t = _post('/functions/v1/ingresar', {'usuario': usuario, 'clave': clave})
        return _verificar(t['access_token'], usuario, recordar, t.get('refresh_token'))
    except _SinConexion:
        return Resultado(False, "No hay conexión con el servidor de licencias. "
                                "Revisa tu conexión a internet.", usuario)
    except _ErrorServidor as e:
        if e.status in (400, 401):
            return Resultado(False, "Usuario o contraseña incorrectos.", usuario)
        if e.status == 429:
            return Resultado(False, "Demasiados intentos. Espera un momento.", usuario)
        return Resultado(False, f"Error del servidor de licencias ({e.status}).", usuario)
    except Exception as e:
        return Resultado(False, f"Error inesperado: {e}", usuario)


def reanudar_sesion():
    """Intenta entrar sin pedir datos con la sesión recordada.
    Devuelve None si no hay sesión recordada."""
    d = _leer_sesion()
    if not d or not d.get('refresh'):
        return None
    usuario = d.get('usuario', '')
    try:
        t = _post('/auth/v1/token?grant_type=refresh_token', {'refresh_token': d['refresh']})
        return _verificar(t['access_token'], usuario, True, t.get('refresh_token'))
    except _SinConexion:
        # Período de gracia sin conexión
        try:
            ult = _dt.datetime.fromisoformat(d['ultima_ok'])
            vence = _fecha(d.get('vence'))
            ahora = _dt.datetime.now(_dt.timezone.utc)
            dias = (ahora - ult).total_seconds() / 86400
            if (d.get('equipo') == id_equipo() and 0 <= dias < DIAS_SIN_CONEXION
                    and (vence is None or vence >= ahora.date())):
                return Resultado(True, "", usuario, vence, sin_conexion=True)
        except Exception:
            pass
        return Resultado(False, "Sin conexión y venció el plazo de uso sin conexión "
                                f"({DIAS_SIN_CONEXION} días). Conéctate a internet.", usuario)
    except _ErrorServidor:
        borrar_sesion()
        return Resultado(False, "Tu sesión expiró. Ingresa nuevamente.", usuario)
    except Exception:
        return None

"""
Módulo de entrada/salida para simulaciones ThermoPhase.
=========================================================

Guarda y carga simulaciones completas (inputs + resultados calculados) en
archivos JSON con extensión .tpsim. Permite reabrir una simulación con las
envolventes, isocalidades, mapas de densidad y propiedades ya renderizados
sin necesidad de recalcular.

Formato:
  {
    "formato": "ThermoPhase",
    "version": "1.0",
    "fecha_guardado": "...",
    "kij_user": [[...],...],     # matriz 13x13 editable por el usuario
    "eos_activa": "PR" | "SRK",
    "tabs": {
      "equilibrio":   { "entrada": {...}, "resultado": {...}|null },
      "envolvente":   { "entrada": {...}, "resultado": {...}|null },
      "saturacion":   { "entrada": {...}, "resultado": {...}|null },
      "propiedades":  { "entrada": {...}, "resultado": {...}|null }
    }
  }

Uso desde MainWindow:
  from simulacion import guardar, cargar
  guardar(path, estado_dict)
  estado_dict = cargar(path)
"""
import json
import datetime
import numpy as np


FORMATO   = "ThermoPhase"
VERSION   = "1.0"
EXTENSION = ".tpsim"


# ── Helpers de conversión ────────────────────────────────────────────
def _clean(o):
    """Convierte recursivamente numpy → tipos Python nativos serializables.
    Convierte np.ndarray a list, np.float64 a float, np.int64 a int, tuplas
    a listas. Los None y tipos nativos pasan sin cambios."""
    if o is None or isinstance(o, (str, bool)):
        return o
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        if np.isnan(o) or np.isinf(o):
            return None
        return float(o)
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, (list, tuple)):
        return [_clean(x) for x in o]
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    # fallback: str
    return str(o)


# ── API pública ──────────────────────────────────────────────────────
def guardar(path, estado):
    """Guarda la simulación completa en JSON. `estado` debe ser un dict
    con la estructura descrita en el docstring del módulo. Todos los
    numpy arrays / floats se serializan automáticamente."""
    doc = {
        "formato": FORMATO,
        "version": VERSION,
        "fecha_guardado": datetime.datetime.now().isoformat(timespec='seconds'),
    }
    doc.update(_clean(estado))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)


def cargar(path):
    """Carga la simulación desde un archivo .tpsim. Valida el formato y
    la versión mayor. Retorna el dict del archivo."""
    with open(path, 'r', encoding='utf-8') as f:
        doc = json.load(f)
    fmt = doc.get('formato', '?')
    if fmt != FORMATO:
        raise ValueError(f"El archivo no es un ThermoPhase valido (formato={fmt!r})")
    ver = doc.get('version', '?')
    ver_mayor = ver.split('.')[0] if '.' in ver else ver
    if ver_mayor != VERSION.split('.')[0]:
        raise ValueError(f"Version de archivo incompatible ({ver}). "
                         f"Este ThermoPhase espera version {VERSION}.")
    return doc

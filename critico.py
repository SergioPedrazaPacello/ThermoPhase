"""
critico.py — Punto critico REAL de la mezcla, para la identificacion de fase
al estilo PVTsim.

PVTsim distingue liquido/gas de un fluido monofasico comparando T y P con el
punto critico REAL de la mezcla (no el pseudocritico de Kay). Aqui se obtiene
el punto critico reutilizando el trazador de envolvente de Michelsen (que lo
localiza como el punto donde Ki->1), con CACHE por composicion+EOS para que el
costo se pague una sola vez por fluido. Incluye guarda de reentrancia para no
recursar si el propio trazado dispara un flash monofasico.
"""
import copy
import eos as E

_CACHE = {}            # (eos, comp_redondeada) -> (Pc, Tc) | None
_EN_CURSO = set()      # claves en calculo (guarda anti-recursion)


def _clave(z):
    return (E._EOS_ACTIVA, tuple(round(float(v), 5) for v in z))


def punto_critico(z, kij):
    """(Pc[psia], Tc[°R]) de la mezcla con la EOS activa, o None. Cacheado."""
    k = _clave(z)
    if k in _CACHE:
        return _CACHE[k]
    if k in _EN_CURSO:            # reentrancia: aun calculandose
        return None
    _EN_CURSO.add(k)
    crit = None
    try:
        import envolvente_michelsen as EM
        r = EM.construir_envolvente(list(z), kij, max_pts=400)
        crit = r.get('critico')
        if crit is not None:
            crit = (float(crit[0]), float(crit[1]))
    except Exception:
        crit = None
    finally:
        _EN_CURSO.discard(k)
    _CACHE[k] = crit
    return crit


def limpiar_cache():
    _CACHE.clear()
